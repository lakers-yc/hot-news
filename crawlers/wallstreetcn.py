"""
华尔街见闻爬虫 - 获取真实数据
"""
from typing import List, Dict, Any
from datetime import datetime
from .base import BaseCrawler


class WallstreetcnCrawler(BaseCrawler):
    name = "华尔街见闻"
    source_type = "fast"
    enabled = True

    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取华尔街见闻快讯"""
        url = "https://api-one.wallstcn.com/apiv1/content/articles"
        params = {'channel': 'global-channel', 'action': 'latest', 'limit': 20}

        response = self.fetch(url, params=params)
        if not response:
            return []

        try:
            data = response.json()
            items = []

            for item in data.get('data', {}).get('items', []):
                title = item.get('title', '')
                aid = item.get('id', '')
                ts = item.get('display_time', 0)

                time_str = datetime.fromtimestamp(ts).strftime('%H:%M') if ts else ''

                items.append({
                    'title': title,
                    'url': f'https://wallstreetcn.com/articles/{aid}' if aid else 'https://wallstreetcn.com',
                    'time': time_str,
                    'source': self.name
                })

            return items

        except Exception as e:
            print(f"[{self.name}] 解析失败: {e}")
            return []