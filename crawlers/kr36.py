"""
36氪爬虫 - 获取真实数据
"""
from typing import List, Dict, Any
from datetime import datetime
from .base import BaseCrawler


class Kr36Crawler(BaseCrawler):
    name = "36氪"
    source_type = "fast"
    enabled = False  # 禁用: 触发反爬验证码

    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取36氪快讯"""
        url = "https://36kr.com/api/newsflash"

        response = self.fetch(url)
        if not response:
            return []

        try:
            data = response.json()
            items = []

            for item in data.get('data', {}).get('items', [])[:15]:
                title = item.get('title', '')
                news_id = item.get('id', '')
                created_at = item.get('created_at', '')

                time_str = ''
                if created_at:
                    try:
                        dt = datetime.fromtimestamp(int(created_at))
                        time_str = dt.strftime('%H:%M')
                    except:
                        pass

                items.append({
                    'title': title,
                    'url': f'https://36kr.com/newsflashes/{news_id}' if news_id else 'https://36kr.com',
                    'time': time_str,
                    'source': self.name
                })

            return items

        except Exception as e:
            print(f"[{self.name}] 解析失败: {e}")
            return []