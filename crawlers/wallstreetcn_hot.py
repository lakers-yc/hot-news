"""
华尔街见闻热榜爬虫 - 获取热门文章
"""
from typing import List, Dict, Any
from .base import BaseCrawler


class WallstreetcnHotCrawler(BaseCrawler):
    name = "华尔街见闻热榜"
    source_type = "hot"
    enabled = True

    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取华尔街见闻热门文章"""
        # 尝试获取热门文章API
        url = "https://api-one.wallstcn.com/apiv1/content/articles/hot"

        response = self.fetch(url)
        if not response:
            # 备用方案：获取最新文章作为热榜
            return self._fetch_latest_as_hot()

        try:
            data = response.json()
            items = []

            hot_list = data.get('data', {}).get('items', [])
            if not hot_list:
                hot_list = data.get('data', [])

            for idx, item in enumerate(hot_list[:15], 1):
                title = item.get('title', '')
                aid = item.get('id', '')
                pv = item.get('display_count', 0) or item.get('readCount', 0)

                if title:
                    items.append({
                        'title': title[:100] if len(title) > 100 else title,
                        'url': f'https://wallstreetcn.com/articles/{aid}' if aid else 'https://wallstreetcn.com',
                        'time': f'热度 {pv}' if pv else f'第{idx}名',
                        'source': self.name
                    })

            if items:
                return items

            # 如果无数据，使用备用方案
            return self._fetch_latest_as_hot()

        except Exception as e:
            print(f"[{self.name}] API解析失败: {e}")
            return self._fetch_latest_as_hot()

    def _fetch_latest_as_hot(self) -> List[Dict[str, Any]]:
        """获取最新文章作为热榜"""
        url = "https://api-one.wallstcn.com/apiv1/content/articles"
        params = {'channel': 'global-channel', 'action': 'latest', 'limit': 15}

        response = self.fetch(url, params=params)
        if not response:
            return []

        try:
            data = response.json()
            items = []

            for idx, item in enumerate(data.get('data', {}).get('items', []), 1):
                title = item.get('title', '')
                aid = item.get('id', '')

                if title:
                    items.append({
                        'title': title[:100] if len(title) > 100 else title,
                        'url': f'https://wallstreetcn.com/articles/{aid}' if aid else 'https://wallstreetcn.com',
                        'time': f'第{idx}名',
                        'source': self.name
                    })

            return items

        except Exception as e:
            print(f"[{self.name}] 获取最新文章失败: {e}")
            return []