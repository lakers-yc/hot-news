# 热点追踪 - 多源财经资讯聚合系统

聚合多个财经/科技资讯源的实时热点新闻，以卡片式布局呈现，支持自动刷新。

---

## 目录结构

```
hot-news/
├── server.py              # Flask 后端服务
├── index.html             # 主页面
├── app.js                 # 前端逻辑
├── requirements.txt       # Python 依赖
├── 启动.bat               # Windows 启动脚本
└── crawlers/              # 爬虫模块
    ├── __init__.py        # 模块导出
    ├── base.py            # 爬虫基类
    ├── cls.py             # 财联社
    ├── eastmoney.py       # 东方财富
    ├── ths.py             # 同花顺
    ├── stcn.py            # 证券时报
    ├── wallstreetcn.py    # 华尔街见闻
    ├── yicai.py           # 第一财经
    ├── toutiao.py         # 今日头条
    ├── baidu.py           # 百度热榜
    ├── jin10.py           # 金十数据 (已禁用)
    ├── xueqiu.py          # 雪球 (已禁用)
    ├── weibo.py           # 微博热搜 (已禁用)
    ├── kr36.py            # 36氪 (已禁用)
    ├── sse.py             # 上交所 (已禁用)
    ├── szse.py            # 深交所 (已禁用)
    ├── gov.py             # 中国政府网 (已禁用)
    └── xinhua.py          # 新华社 (已禁用)
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
- API 接口：http://localhost:5003/api/hot-news/list

---

## 数据源状态

### 启用的数据源 (8个)

| 数据源 | 类型 | 获取方式 | 每次条数 |
|--------|------|----------|----------|
| 财联社 | 快讯 | 页面 JSON 提取 | 15 |
| 东方财富 | 快讯 | API 接口 | 15 |
| 同花顺 | 财经 | HTML 解析 | 15 |
| 证券时报 | 快讯 | HTML 解析 | 10 |
| 华尔街见闻 | 快讯 | API 接口 | 5 |
| 第一财经 | 快讯 | API 接口 | 10 |
| 今日头条 | 热榜 | API 接口 | 15 |
| 百度热榜 | 热榜 | 页面正则提取 | 15 |

### 禁用的数据源 (8个)

| 数据源 | 禁用原因 |
|--------|----------|
| 金十数据 | API 返回 502 错误，服务器故障 |
| 雪球 | WAF 保护，无法绕过 |
| 微博热搜 | 连接超时 |
| 36氪 | 触发反爬验证码 |
| 上交所 | HTML 结构变更，需 JS 渲染 |
| 深交所 | HTML 结构变更，需 JS 渲染 |
| 中国政府网 | HTML 结构变更 |
| 新华社 | HTML 结构变更 |

---

## API 接口文档

### 1. 获取所有热点数据

```
GET /api/hot-news/list
```

**响应示例：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "cls": {
      "info": {
        "name": "财联社",
        "type": "fast",
        "enabled": true,
        "last_fetch": "2026-03-17T21:30:00"
      },
      "items": [
        {
          "title": "新闻标题",
          "url": "https://...",
          "time": "21:30",
          "source": "财联社"
        }
      ],
      "error": null
    }
  },
  "updateTime": "2026-03-17 21:30:00"
}
```

### 2. 强制刷新所有数据

```
GET /api/hot-news/refresh
```

### 3. 获取单个数据源

```
GET /api/hot-news/source/<source_name>?cache=true
```

**参数：**
- `source_name`: 数据源 ID（如 cls, eastmoney, baidu）
- `cache`: 是否使用缓存（默认 true）

### 4. 获取数据源列表

```
GET /api/hot-news/sources
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
│                 │   Crawler Hub  │              │
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
    source_type: str    # 类型: fast/hot/official/tech
    enabled: bool       # 是否启用

    def fetch(self, url, params) -> Response:
        """发起 HTTP 请求（支持 curl_cffi 模拟浏览器）"""

    def fetch_data(self) -> List[Dict]:
        """获取数据（子类实现）"""

    def get_data(self, use_cache=True) -> List[Dict]:
        """获取数据（带缓存和去重）"""

    def get_source_info(self) -> Dict:
        """获取数据源信息"""
```

### 前端架构

```
┌─────────────────────────────────────────────────┐
│                   index.html                     │
├─────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────┐  │
│  │              Header (sticky)               │  │
│  │  [Logo] 热点追踪    [状态] [刷新按钮]      │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │              News Grid (CSS Grid)          │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐      │  │
│  │  │ Card 1  │ │ Card 2  │ │ Card 3  │      │  │
│  │  │ 财联社  │ │ 同花顺  │ │ 东方财富 │      │  │
│  │  └─────────┘ └─────────┘ └─────────┘      │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐      │  │
│  │  │ Card 4  │ │ Card 5  │ │ Card 6  │      │  │
│  │  │ 证券时报│ │华尔街见闻│ │ 第一财经 │      │  │
│  │  └─────────┘ └─────────┘ └─────────┘      │  │
│  │  ┌─────────┐ ┌─────────┐                  │  │
│  │  │ Card 7  │ │ Card 8  │                  │  │
│  │  │今日头条 │ │ 百度热榜 │                  │  │
│  │  └─────────┘ └─────────┘                  │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │              Loading Overlay               │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## 响应式布局

```css
/* Mobile First */
.news-grid { grid-template-columns: 1fr; }

/* 平板 (≥768px) */
@media (min-width: 768px) {
  .news-grid { grid-template-columns: repeat(2, 1fr); }
}

/* 桌面 (≥1200px) */
@media (min-width: 1200px) {
  .news-grid { grid-template-columns: repeat(3, 1fr); }
}

/* 大屏 (≥1600px) */
@media (min-width: 1600px) {
  .news-grid { grid-template-columns: repeat(4, 1fr); }
}
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
    source_type = "fast"  # fast/hot/official/tech
    enabled = True

    def fetch_data(self):
        url = "https://api.example.com/news"
        response = self.fetch(url)

        if not response:
            return []

        data = response.json()
        items = []

        for item in data.get('list', [])[:15]:
            items.append({
                'title': item.get('title'),
                'url': item.get('url'),
                'time': item.get('time'),
                'source': self.name
            })

        return items
```

2. 在 `crawlers/__init__.py` 中导出：

```python
from .new_source import NewSourceCrawler

__all__ = [..., 'NewSourceCrawler']
```

3. 在 `server.py` 中注册：

```python
from crawlers import NewSourceCrawler

CRAWLERS = {
    ...
    'new_source': NewSourceCrawler(),
}

SOURCE_URLS = {
    ...
    'new_source': 'https://example.com',
}
```

4. 在 `app.js` 中添加前端配置：

```javascript
const SOURCES = {
    ...
    new_source: {
        name: '新数据源',
        type: 'fast',
        icon: 'zap',
        color: '#fa0d00',
        url: 'https://example.com'
    }
};
```

---

## 注意事项

1. **请求频率**：部分数据源有反爬机制，请勿过于频繁请求
2. **网络环境**：部分数据源可能需要特定网络环境
3. **数据时效**：缓存时间为 5 分钟，可根据需要调整
4. **用户代理**：已配置 Chrome UA 模拟浏览器请求

---

## 更新日志

### v1.0.0 (2026-03-17)

- 初始版本发布
- 支持 8 个数据源实时获取
- 卡片式响应式布局
- 自动刷新机制
- 单独刷新功能

---

## License

MIT License