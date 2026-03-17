"""
第一财经爬虫 - 获取真实数据
"""
from typing import List, Dict, Any
from .base import BaseCrawler


class YicaiCrawler(BaseCrawler):
    name = "第一财经"
    source_type = "fast"
    enabled = True

    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取第一财经快讯"""
        url = "https://www.yicai.com/api/ajax/getlatest"

        response = self.fetch(url)
        if not response:
            return []

        try:
            data = response.json()
            items = []

            for item in data[:15]:
                title = item.get('NewsTitle', '') or item.get('Title', '') or item.get('title', '')
                url_link = item.get('NewsUrl', '') or item.get('Url', '') or item.get('url', '')
                time_str = item.get('CreateDate', '') or item.get('createtime', '')

                if title:
                    items.append({
                        'title': title,
                        'url': url_link if url_link and url_link.startswith('http') else 'https://www.yicai.com',
                        'time': time_str[:16] if time_str else '',
                        'source': self.name
                    })

            return items

        except Exception as e:
            print(f"[{self.name}] 解析失败: {e}")
            return []