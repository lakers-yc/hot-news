"""
金十数据爬虫 - 获取真实数据
"""
from typing import List, Dict, Any
from datetime import datetime
from .base import BaseCrawler


class Jin10Crawler(BaseCrawler):
    name = "金十数据"
    source_type = "fast"
    enabled = False  # 禁用: API返回502错误，服务器端问题

    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取金十数据快讯 - 使用备用接口"""
        url = "https://rmdex.jin10.com/data.json"

        response = self.fetch(url)
        if not response:
            return []

        try:
            data = response.json()
            items = []

            for item in data.get('data', [])[:15]:
                title = item.get('content', '') or item.get('title', '')
                item_id = item.get('id', '')
                ts = item.get('time', '')

                time_str = ''
                if ts:
                    try:
                        dt = datetime.fromtimestamp(int(ts))
                        time_str = dt.strftime('%H:%M')
                    except:
                        pass

                if title:
                    items.append({
                        'title': title[:100] if len(title) > 100 else title,
                        'url': f'https://www.jin10.com/flash/{item_id}.html' if item_id else 'https://www.jin10.com',
                        'time': time_str,
                        'source': self.name
                    })

            return items

        except Exception as e:
            print(f"[{self.name}] 解析失败: {e}")
            return []