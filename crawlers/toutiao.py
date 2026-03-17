"""
今日头条爬虫 - 获取热点数据
使用 hot-board API 获取热榜数据
"""
from typing import List, Dict, Any
from .base import BaseCrawler


class ToutiaoCrawler(BaseCrawler):
    name = "今日头条"
    source_type = "hot"
    enabled = True

    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取今日头条热点 - 使用 hot-board API"""
        url = "https://www.toutiao.com/hot-event/hot-board/"
        params = {'origin': 'toutiao_pc'}

        response = self.fetch(url, params=params)
        if not response:
            return []

        try:
            data = response.json()
            items = []

            # 解析热搜数据
            hot_list = data.get('data', []) if isinstance(data.get('data'), list) else []

            for idx, item in enumerate(hot_list[:15], 1):
                title = item.get('Title', '') or item.get('title', '')
                url_link = item.get('Url', '') or item.get('url', '')
                hot_value = item.get('HotValue', '') or item.get('hotValue', '')

                if title:
                    items.append({
                        'title': title,
                        'url': url_link if url_link else 'https://www.toutiao.com',
                        'time': f'热度 {hot_value}' if hot_value else f'第{idx}名',
                        'source': self.name
                    })

            return items

        except Exception as e:
            print(f"[{self.name}] 解析失败: {e}")
            return []