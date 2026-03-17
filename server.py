"""
热点追踪 Flask 后端服务
聚合多个财经/科技资讯源的实时热点新闻
支持智能分析、概念匹配、股票推荐
"""
from flask import Flask, jsonify, request, send_file
from datetime import datetime
from typing import Dict, List, Any
import threading
import os
import json
from apscheduler.schedulers.background import BackgroundScheduler

# 导入爬虫 - 按指定顺序
from crawlers import (
    ClsCrawler,        # 1. 财联社
    Jin10Crawler,      # 2. 金十数据
    ThsCrawler,        # 3. 同花顺
    EastmoneyCrawler,  # 4. 东方财富
    XueqiuCrawler,     # 5. 雪球
    StcnCrawler,       # 6. 证券时报
    WallstreetcnCrawler,  # 7. 华尔街见闻
    SseCrawler,        # 8. 上交所
    SzseCrawler,       # 9. 深交所
    GovCrawler,        # 10. 中国政府网
    XinhuaCrawler,     # 11. 新华社
    YicaiCrawler,      # 12. 第一财经
    WeiboCrawler,      # 13. 微博热搜
    ToutiaoCrawler,    # 14. 今日头条
    Kr36Crawler,       # 15. 36氪
    BaiduCrawler,      # 16. 百度热榜
    # 热榜爬虫
    EastmoneyHotCrawler,
    ThsHotCrawler,
    ClsHotCrawler,
    YicaiHotCrawler,
    StcnHotCrawler,
    WallstreetcnHotCrawler,
)

# 导入新增模块
from crawlers.concept_crawler import ConceptCrawler
from crawlers.market_crawler import MarketCrawler
from analyzers import ReportGenerator

app = Flask(__name__)

# 获取当前目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 手动处理 CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# 全局数据存储
HOT_NEWS_DATA: Dict[str, Dict[str, Any]] = {}
LAST_UPDATE_TIME: datetime = None
DATA_LOCK = threading.Lock()

# 报告数据存储
REPORT_DATA: Dict[str, Any] = {}
REPORT_UPDATE_TIME: datetime = None
REPORT_LOCK = threading.Lock()

# 初始化新增爬虫
concept_crawler = ConceptCrawler()
market_crawler = MarketCrawler()

# 官网链接配置
SOURCE_URLS = {
    'cls': 'https://www.cls.cn',
    'jin10': 'https://www.jin10.com',
    'ths': 'http://www.10jqka.com.cn',
    'eastmoney': 'https://www.eastmoney.com',
    'xueqiu': 'https://xueqiu.com',
    'stcn': 'http://www.stcn.com',
    'wallstreetcn': 'http://wallstreetcn.com',
    'sse': 'http://www.sse.com.cn',
    'szse': 'http://www.szse.cn',
    'gov': 'http://www.gov.cn',
    'xinhua': 'http://www.xinhuanet.com',
    'yicai': 'https://www.yicai.com',
    'weibo': 'https://s.weibo.com/top/summary',
    'toutiao': 'https://www.toutiao.com',
    'kr36': 'https://36kr.com',
    'baidu': 'https://top.baidu.com/board?tab=realtime',
    # 热榜链接
    'eastmoney_hot': 'https://guba.eastmoney.com',
    'ths_hot': 'https://q.10jqka.com.cn/gn/',
    'cls_hot': 'https://www.cls.cn/hot',
    'yicai_hot': 'https://www.yicai.com/news/',
    'stcn_hot': 'https://news.stcn.com/',
    'wallstreetcn_hot': 'https://wallstreetcn.com/',
}

# 快讯爬虫 - 按指定顺序（仅快讯类型）
FAST_CRAWLERS = {
    'cls': ClsCrawler(),           # 1. 财联社
    'eastmoney': EastmoneyCrawler(),  # 2. 东方财富
    'ths': ThsCrawler(),           # 3. 同花顺
    'wallstreetcn': WallstreetcnCrawler(),  # 4. 华尔街见闻
    'stcn': StcnCrawler(),         # 5. 证券时报
    'yicai': YicaiCrawler(),       # 6. 第一财经
}

# 热榜爬虫 - 财经热榜优先
HOT_CRAWLERS = {
    'eastmoney_hot': EastmoneyHotCrawler(),   # 1. 东方财富热榜
    'ths_hot': ThsHotCrawler(),               # 2. 同花顺热榜
    'cls_hot': ClsHotCrawler(),               # 3. 财联社热榜
    'yicai_hot': YicaiHotCrawler(),           # 4. 第一财经热榜
    'stcn_hot': StcnHotCrawler(),             # 5. 证券时报热榜
    'wallstreetcn_hot': WallstreetcnHotCrawler(),  # 6. 华尔街见闻热榜
    'baidu': BaiduCrawler(),                  # 7. 百度热榜
    'toutiao': ToutiaoCrawler(),              # 8. 今日头条
}

# 兼容旧接口：所有爬虫合并
CRAWLERS = {**FAST_CRAWLERS, **HOT_CRAWLERS}


def fetch_all_sources():
    """获取所有数据源的数据"""
    global HOT_NEWS_DATA, LAST_UPDATE_TIME

    results = {}

    # 合并所有爬虫
    all_crawlers = {**FAST_CRAWLERS, **HOT_CRAWLERS}

    for name, crawler in all_crawlers.items():
        if not crawler.enabled:
            continue

        try:
            data = crawler.get_data(use_cache=False)
            # 每个来源最多15条
            items = data[:15] if data else []
            results[name] = {
                'info': {**crawler.get_source_info(), 'url': SOURCE_URLS.get(name, '#')},
                'items': items,
                'error': None if items else '暂无数据'
            }
        except Exception as e:
            print(f"[{crawler.name}] 获取失败: {e}")
            results[name] = {
                'info': {**crawler.get_source_info(), 'url': SOURCE_URLS.get(name, '#')},
                'items': [],
                'error': str(e)
            }

    with DATA_LOCK:
        HOT_NEWS_DATA = results
        LAST_UPDATE_TIME = datetime.now()

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 数据更新完成")


def generate_daily_report():
    """生成每日分析报告"""
    global REPORT_DATA, REPORT_UPDATE_TIME

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始生成每日报告...")

    try:
        # 收集所有新闻
        all_news = []
        with DATA_LOCK:
            for source_name, source_data in HOT_NEWS_DATA.items():
                for item in source_data.get('items', []):
                    item['source'] = source_data['info'].get('name', source_name)
                    all_news.append(item)

        # 生成报告
        generator = ReportGenerator(concept_crawler, market_crawler)
        report = generator.generate(all_news)

        # 保存报告
        report_path = generator.save_report(report)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 报告已保存: {report_path}")

        with REPORT_LOCK:
            REPORT_DATA = report
            REPORT_UPDATE_TIME = datetime.now()

        return report

    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 报告生成失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def schedule_refresh():
    """定时刷新任务"""
    fetch_all_sources()
    # 每5分钟刷新一次
    timer = threading.Timer(300, schedule_refresh)
    timer.daemon = True
    timer.start()


@app.route('/')
def index():
    """首页 - 返回 index.html"""
    index_path = os.path.join(BASE_DIR, 'index.html')
    print(f"[DEBUG] 查找 index.html: {index_path}, 存在: {os.path.exists(index_path)}")
    if os.path.exists(index_path):
        return send_file(index_path)
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>热点追踪 API</title>
    </head>
    <body>
        <h1>热点追踪 API 服务</h1>
        <p>请确保 index.html 文件存在</p>
        <ul>
            <li><a href="/api/hot-news/list">/api/hot-news/list</a> - 获取所有热点数据</li>
            <li><a href="/api/hot-news/refresh">/api/hot-news/refresh</a> - 强制刷新数据</li>
            <li><a href="/api/hot-news/sources">/api/hot-news/sources</a> - 获取数据源列表</li>
        </ul>
    </body>
    </html>
    '''


@app.route('/app.js')
def app_js():
    """返回 app.js"""
    js_path = os.path.join(BASE_DIR, 'app.js')
    if os.path.exists(js_path):
        return send_file(js_path, mimetype='application/javascript')
    return '// app.js not found', 404


@app.route('/api/hot-news/list')
def get_all_hot_news():
    """获取所有来源的热点数据"""
    with DATA_LOCK:
        data = HOT_NEWS_DATA.copy()
        update_time = LAST_UPDATE_TIME

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': data,
        'updateTime': update_time.strftime('%Y-%m-%d %H:%M:%S') if update_time else None
    })


@app.route('/api/hot-news/refresh')
def refresh_hot_news():
    """强制刷新所有数据"""
    try:
        fetch_all_sources()
        return jsonify({
            'code': 200,
            'message': '刷新成功',
            'updateTime': LAST_UPDATE_TIME.strftime('%Y-%m-%d %H:%M:%S') if LAST_UPDATE_TIME else None
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'刷新失败: {str(e)}'
        }), 500


@app.route('/api/hot-news/source/<source_name>')
def get_source_news(source_name):
    """获取单个来源的数据"""
    if source_name not in CRAWLERS:
        return jsonify({
            'code': 404,
            'message': f'未知的数据源: {source_name}'
        }), 404

    crawler = CRAWLERS[source_name]
    use_cache = request.args.get('cache', 'true').lower() == 'true'

    try:
        data = crawler.get_data(use_cache=use_cache)
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'info': {**crawler.get_source_info(), 'url': SOURCE_URLS.get(source_name, '#')},
                'items': data
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取数据失败: {str(e)}'
        }), 500


@app.route('/api/hot-news/sources')
def get_sources():
    """获取所有数据源信息"""
    sources = []
    for name, crawler in CRAWLERS.items():
        sources.append({
            'id': name,
            'name': crawler.name,
            'type': crawler.source_type,
            'enabled': crawler.enabled,
            'url': SOURCE_URLS.get(name, '#')
        })

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': sources
    })


@app.route('/api/hot-news/fast')
def get_fast_news():
    """获取快讯数据"""
    results = {}

    for name, crawler in FAST_CRAWLERS.items():
        if not crawler.enabled:
            continue

        try:
            data = crawler.get_data(use_cache=True)
            items = data[:15] if data else []
            results[name] = {
                'info': {**crawler.get_source_info(), 'url': SOURCE_URLS.get(name, '#')},
                'items': items,
                'error': None if items else '暂无数据'
            }
        except Exception as e:
            print(f"[{crawler.name}] 获取失败: {e}")
            results[name] = {
                'info': {**crawler.get_source_info(), 'url': SOURCE_URLS.get(name, '#')},
                'items': [],
                'error': str(e)
            }

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': results,
        'updateTime': LAST_UPDATE_TIME.strftime('%Y-%m-%d %H:%M:%S') if LAST_UPDATE_TIME else None
    })


@app.route('/api/hot-news/hot')
def get_hot_news():
    """获取热榜数据"""
    results = {}

    for name, crawler in HOT_CRAWLERS.items():
        if not crawler.enabled:
            continue

        try:
            data = crawler.get_data(use_cache=True)
            items = data[:15] if data else []
            results[name] = {
                'info': {**crawler.get_source_info(), 'url': SOURCE_URLS.get(name, '#')},
                'items': items,
                'error': None if items else '暂无数据'
            }
        except Exception as e:
            print(f"[{crawler.name}] 获取失败: {e}")
            results[name] = {
                'info': {**crawler.get_source_info(), 'url': SOURCE_URLS.get(name, '#')},
                'items': [],
                'error': str(e)
            }

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': results,
        'updateTime': LAST_UPDATE_TIME.strftime('%Y-%m-%d %H:%M:%S') if LAST_UPDATE_TIME else None
    })


@app.route('/api/hot-news/report')
def get_report():
    """获取分析报告"""
    with REPORT_LOCK:
        report = REPORT_DATA.copy() if REPORT_DATA else None
        update_time = REPORT_UPDATE_TIME

    if not report:
        # 如果没有报告，尝试生成
        report = generate_daily_report()
        if not report:
            return jsonify({
                'code': 404,
                'message': '报告暂未生成，请稍后再试'
            }), 404

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': report,
        'updateTime': update_time.strftime('%Y-%m-%d %H:%M:%S') if update_time else None
    })


@app.route('/api/hot-news/report/refresh')
def refresh_report():
    """强制刷新报告"""
    try:
        # 先刷新新闻数据
        fetch_all_sources()
        # 再生成报告
        report = generate_daily_report()

        if report:
            return jsonify({
                'code': 200,
                'message': '报告刷新成功',
                'data': report,
                'updateTime': REPORT_UPDATE_TIME.strftime('%Y-%m-%d %H:%M:%S') if REPORT_UPDATE_TIME else None
            })
        else:
            return jsonify({
                'code': 500,
                'message': '报告生成失败'
            }), 500
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'报告刷新失败: {str(e)}'
        }), 500


@app.route('/api/hot-news/concepts')
def get_concepts():
    """获取热门概念"""
    try:
        limit = request.args.get('limit', 20, type=int)
        concepts = concept_crawler.get_hot_concepts(limit)
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': concepts
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取概念数据失败: {str(e)}'
        }), 500


@app.route('/api/hot-news/market')
def get_market():
    """获取市场数据"""
    try:
        data = market_crawler.get_data()
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取市场数据失败: {str(e)}'
        }), 500


@app.route('/api/hot-news/sentiment')
def get_sentiment():
    """获取市场情绪"""
    try:
        sentiment = market_crawler.get_market_sentiment()
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': sentiment
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取情绪数据失败: {str(e)}'
        }), 500


@app.route('/api/hot-news/abnormal')
def get_abnormal():
    """获取异动股票"""
    try:
        limit = request.args.get('limit', 20, type=int)
        abnormals = market_crawler.get_abnormal_stocks()
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': abnormals[:limit]
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取异动数据失败: {str(e)}'
        }), 500


if __name__ == '__main__':
    # 启动时先获取一次数据
    print("正在初始化数据...")
    fetch_all_sources()

    # 生成初始报告
    print("正在生成初始报告...")
    generate_daily_report()

    # 启动定时任务 - 使用APScheduler
    scheduler = BackgroundScheduler()

    # 每5分钟刷新新闻数据
    scheduler.add_job(fetch_all_sources, 'interval', minutes=5, id='refresh_news')

    # 每天早上8点生成报告
    scheduler.add_job(generate_daily_report, 'cron', hour=8, minute=0, id='daily_report')

    scheduler.start()
    print("定时任务已启动:")
    print("  - 新闻数据: 每5分钟刷新")
    print("  - 分析报告: 每天8:00生成")

    # 启动 Flask 服务
    print("热点追踪服务启动在 http://localhost:5003")
    print("API接口:")
    print("  - /api/hot-news/list - 获取所有热点数据")
    print("  - /api/hot-news/report - 获取分析报告")
    print("  - /api/hot-news/concepts - 获取热门概念")
    print("  - /api/hot-news/market - 获取市场数据")
    print("  - /api/hot-news/sentiment - 获取市场情绪")
    print("  - /api/hot-news/abnormal - 获取异动股票")

    try:
        app.run(host='0.0.0.0', port=5003, debug=False, threaded=True)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("服务已停止")