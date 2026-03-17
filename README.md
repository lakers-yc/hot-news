# 热点追踪 - 多源财经资讯聚合系统

聚合多个财经/科技资讯源的实时热点新闻，以卡片式布局呈现，支持快讯/热榜Tab切换，自动刷新。

---

## 目录结构

```
hot-news/
├── server.py              # Flask 后端服务
├── index.html             # 主页面
├── app.js                 # 前端逻辑
├── requirements.txt       # Python 依赖
├── 启动.bat               # Windows 启动脚本
├── crawlers/              # 爬虫模块
│   ├── __init__.py        # 模块导出
│   ├── base.py            # 爬虫基类
│   # 快讯爬虫
│   ├── cls.py             # 财联社快讯
│   ├── eastmoney.py       # 东方财富快讯
│   ├── ths.py             # 同花顺快讯
│   ├── stcn.py            # 证券时报快讯
│   ├── wallstreetcn.py    # 华尔街见闻快讯
│   ├── yicai.py           # 第一财经快讯
│   # 热榜爬虫
│   ├── cls_hot.py         # 财联社热榜
│   ├── eastmoney_hot.py   # 东方财富热榜
│   ├── ths_hot.py         # 同花顺热榜
│   ├── stcn_hot.py        # 证券时报热榜
│   ├── wallstreetcn_hot.py# 华尔街见闻热榜
│   ├── yicai_hot.py       # 第一财经热榜
│   # 综合热榜
│   ├── baidu.py           # 百度热榜
│   ├── toutiao.py         # 今日头条
│   └── ...                # 其他数据源
├── analyzers/             # 分析模块
│   ├── news_filter.py     # 新闻过滤
│   ├── concept_matcher.py # 概念匹配
│   ├── stock_recommender.py# 股票推荐
│   └── report_generator.py# 报告生成
└── reports/               # 生成的报告
```

---

## 快速开始

### 方式一：使用启动脚本（Windows）

双击 `启动.bat` 即可自动检查依赖并启动服务。

### 方式二：命令行启动

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python server.py
```

### 访问地址

- 主页面：http://localhost:5003
- 快讯接口：http://localhost:5003/api/hot-news/fast
- 热榜接口：http://localhost:5003/api/hot-news/hot

---

## 功能特性

### Tab切换

前端支持**快讯/热榜**Tab切换，分开显示不同类型的数据：

```
┌─────────────────────────────────────────────────┐
│  [📊 智能分析报告]                    [刷新报告] │
├─────────────────────────────────────────────────┤
│  [快讯]  [热榜]     ← Tab切换                   │
├─────────────────────────────────────────────────┤
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐              │
│  │财联社│ │东财 │ │同花顺│ │...  │  卡片网格    │
│  └─────┘ └─────┘ └─────┘ └─────┘              │
└─────────────────────────────────────────────────┘
```

---

## 数据源配置

### 快讯Tab（6个）

| 优先级 | 数据源 | 类型 | 获取方式 |
|--------|--------|------|----------|
| 1 | 财联社 | fast | 页面JSON提取 |
| 2 | 东方财富 | fast | API接口 |
| 3 | 同花顺 | fast | HTML解析 |
| 4 | 华尔街见闻 | fast | API接口 |
| 5 | 证券时报 | fast | HTML解析 |
| 6 | 第一财经 | fast | API接口 |

### 热榜Tab（8个）- 财经热榜优先

| 优先级 | 数据源 | 类型 | 获取方式 |
|--------|--------|------|----------|
| 1 | 东方财富热榜 | hot | HTML解析 |
| 2 | 同花顺热榜 | hot | HTML解析 |
| 3 | 财联社热榜 | hot | JSON提取 |
| 4 | 第一财经热榜 | hot | HTML解析 |
| 5 | 证券时报热榜 | hot | HTML解析 |
| 6 | 华尔街见闻热榜 | hot | API接口 |
| 7 | 百度热榜 | hot | 页面正则 |
| 8 | 今日头条 | hot | API接口 |

---

## API 接口文档

### 1. 获取快讯数据

```
GET /api/hot-news/fast
```

**响应示例：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "cls": {
      "info": { "name": "财联社", "type": "fast" },
      "items": [{ "title": "...", "url": "...", "time": "12:30" }],
      "error": null
    }
  },
  "updateTime": "2026-03-18 00:30:00"
}
```

### 2. 获取热榜数据

```
GET /api/hot-news/hot
```

### 3. 强制刷新所有数据

```
GET /api/hot-news/refresh
```

### 4. 获取单个数据源

```
GET /api/hot-news/source/<source_name>?cache=false
```

**参数：**
- `source_name`: 数据源 ID（如 cls, eastmoney_hot, baidu）
- `cache`: 是否使用缓存（默认 true）

### 5. 获取分析报告

```
GET /api/hot-news/report
```

### 6. 刷新分析报告

```
GET /api/hot-news/report/refresh
```

---

## 架构设计

### 后端架构

```
┌─────────────────────────────────────────────────┐
│                   Flask Server                   │
│                     (5003)                       │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │  API Route  │  │ Data Cache  │  │ Scheduler│ │
│  │  Handler    │  │  (Memory)   │  │ (5 min)  │ │
│  └──────┬──────┘  └──────┬──────┘  └────┬────┘ │
│         │                │              │      │
│         └────────────────┼──────────────┘      │
│                          ▼                      │
│                 ┌────────────────┐              │
│                 │  Crawler Hub   │              │
│                 │ ┌─────┬─────┐  │              │
│                 │ │FAST │ HOT │  │              │
│                 │ └─────┴─────┘  │              │
│                 └───────┬────────┘              │
│                         │                       │
└─────────────────────────┼───────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
   ┌─────────┐      ┌─────────┐      ┌─────────┐
   │ API型   │      │ HTML型  │      │ JSON型  │
   │ Crawler │      │ Crawler │      │ Crawler │
   └─────────┘      └─────────┘      └─────────┘
```

### 爬虫基类设计

```python
class BaseCrawler(ABC):
    name: str           # 数据源名称
    source_type: str    # 类型: fast/hot
    enabled: bool       # 是否启用

    def fetch(self, url, params) -> Response:
        """发起 HTTP 请求（支持 curl_cffi 模拟浏览器）"""

    def fetch_data(self) -> List[Dict]:
        """获取数据（子类实现）"""

    def get_data(self, use_cache=True) -> List[Dict]:
        """获取数据（带缓存和去重）"""
```

---

## 配置项

### 后端配置 (server.py)

```python
# 服务端口
PORT = 5003

# 定时刷新间隔
REFRESH_INTERVAL = 300  # 5分钟

# 每个数据源最大条数
MAX_ITEMS_PER_SOURCE = 15
```

### 前端配置 (app.js)

```javascript
const CONFIG = {
    API_BASE: '',              // API 基础路径
    POLLING_INTERVAL: 60000,   // 轮询间隔（1分钟）
    AUTO_REFRESH: true,        // 是否自动刷新
};
```

---

## 依赖清单

```
flask>=2.0.0
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
curl_cffi>=0.5.0  # 可选，用于绕过反爬
apscheduler>=3.9.0  # 定时任务
```

---

## 扩展开发

### 添加新的数据源

1. 在 `crawlers/` 目录创建新的爬虫文件：

```python
# crawlers/new_source.py
from .base import BaseCrawler

class NewSourceCrawler(BaseCrawler):
    name = "新数据源"
    source_type = "hot"  # fast 或 hot
    enabled = True

    def fetch_data(self):
        url = "https://api.example.com/news"
        response = self.fetch(url)

        if not response:
            return []

        data = response.json()
        items = []
        seen = set()  # 去重

        for item in data.get('list', [])[:15]:
            title = item.get('title', '')
            if title and title not in seen:
                seen.add(title)
                items.append({
                    'title': title,
                    'url': item.get('url', ''),
                    'time': item.get('time', ''),
                    'source': self.name
                })

        return items
```

2. 在 `crawlers/__init__.py` 中导出

3. 在 `server.py` 中注册到 `FAST_CRAWLERS` 或 `HOT_CRAWLERS`

4. 在 `app.js` 中添加前端配置到 `FAST_SOURCES` 或 `HOT_SOURCES`

---

## 注意事项

1. **请求频率**：部分数据源有反爬机制，请勿过于频繁请求
2. **网络环境**：部分数据源可能需要特定网络环境
3. **数据时效**：缓存时间为 5 分钟，可根据需要调整
4. **XSS防护**：前端已添加HTML转义防止XSS攻击

---

## 更新日志

### v1.1.0 (2026-03-18)

- **新增功能**：快讯/热榜Tab切换
- **新增爬虫**：6个财经平台热榜爬虫
- **新增API**：`/api/hot-news/fast` 和 `/api/hot-news/hot`
- **安全修复**：前端XSS防护
- **代码优化**：爬虫去重逻辑、热度排序

### v1.0.0 (2026-03-17)

- 初始版本发布
- 支持 8 个数据源实时获取
- 卡片式响应式布局
- 自动刷新机制
- 单独刷新功能

---

## License

MIT License