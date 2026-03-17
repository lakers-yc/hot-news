"""
热点追踪 Flask 后端服务
聚合多个财经/科技资讯源的实时热点新闻
"""
from flask import Flask, jsonify, request, send_file
from datetime import datetime
from typing import Dict, List, Any
import threading
import os

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
)

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
}

# 初始化爬虫实例 - 按指定顺序
CRAWLERS = {
    'cls': ClsCrawler(),           # 1. 财联社
    'jin10': Jin10Crawler(),       # 2. 金十数据
    'ths': ThsCrawler(),           # 3. 同花顺
    'eastmoney': EastmoneyCrawler(),  # 4. 东方财富
    'xueqiu': XueqiuCrawler(),     # 5. 雪球
    'stcn': StcnCrawler(),         # 6. 证券时报
    'wallstreetcn': WallstreetcnCrawler(),  # 7. 华尔街见闻
    'sse': SseCrawler(),           # 8. 上交所
    'szse': SzseCrawler(),         # 9. 深交所
    'gov': GovCrawler(),           # 10. 中国政府网
    'xinhua': XinhuaCrawler(),     # 11. 新华社
    'yicai': YicaiCrawler(),       # 12. 第一财经
    'weibo': WeiboCrawler(),       # 13. 微博热搜
    'toutiao': ToutiaoCrawler(),   # 14. 今日头条
    'kr36': Kr36Crawler(),         # 15. 36氪
    'baidu': BaiduCrawler(),       # 16. 百度热榜
}


def fetch_all_sources():
    """获取所有数据源的数据"""
    global HOT_NEWS_DATA, LAST_UPDATE_TIME

    results = {}

    for name, crawler in CRAWLERS.items():
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


if __name__ == '__main__':
    # 启动时先获取一次数据
    print("正在初始化数据...")
    fetch_all_sources()

    # 启动定时任务
    threading.Thread(target=schedule_refresh, daemon=True).start()
    print("定时刷新任务已启动 (每5分钟)")

    # 启动 Flask 服务
    print("热点追踪服务启动在 http://localhost:5003")
    app.run(host='0.0.0.0', port=5003, debug=False, threaded=True)