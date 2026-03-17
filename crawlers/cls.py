"""
财联社爬虫 - 获取真实数据
"""
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import json
import re
from .base import BaseCrawler


class ClsCrawler(BaseCrawler):
    name = "财联社"
    source_type = "fast"
    enabled = True

    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取财联社电报 - 从页面JSON数据中提取"""
        url = "https://www.cls.cn/telegraph"

        response = self.fetch(url)
        if not response:
            return []

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            items = []

            # 查找 __NEXT_DATA__ 中的数据
            for script in soup.find_all('script'):
                text = script.string or ''
                if 'telegraphList' in text:
                    match = re.search(r'({.*})', text, re.DOTALL)
                    if match:
                        data = json.loads(match.group(1))
                        telegraph_list = data.get('props', {}).get('initialState', {}).get('telegraph', {}).get('telegraphList', [])

                        for item in telegraph_list[:15]:
                            title = item.get('title') or item.get('content', '')
                            item_id = item.get('id', '')
                            ctime = item.get('ctime', '')

                            # 提取时间
                            time_str = ''
                            if ctime:
                                try:
                                    from datetime import datetime
                                    dt = datetime.fromtimestamp(int(ctime))
                                    time_str = dt.strftime('%H:%M')
                                except:
                                    pass

                            if title:
                                items.append({
                                    'title': title[:100] if len(title) > 100 else title,
                                    'url': f'https://www.cls.cn/telegraph/{item_id}' if item_id else 'https://www.cls.cn/telegraph',
                                    'time': time_str,
                                    'source': self.name
                                })

                        break

            return items

        except Exception as e:
            print(f"[{self.name}] 解析失败: {e}")
            return []