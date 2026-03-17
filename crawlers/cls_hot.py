"""
财联社热榜爬虫 - 获取热门电报
"""
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import json
import re
from .base import BaseCrawler


class ClsHotCrawler(BaseCrawler):
    name = "财联社热榜"
    source_type = "hot"
    enabled = True

    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取财联社热门电报"""
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
                    # 提取JSON数据
                    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', text, re.DOTALL)
                    if not match:
                        # 尝试另一种格式
                        match = re.search(r'({.*})', text, re.DOTALL)

                    if match:
                        try:
                            data = json.loads(match.group(1))
                        except json.JSONDecodeError:
                            continue

                        telegraph_list = data.get('props', {}).get('initialState', {}).get('telegraph', {}).get('telegraphList', [])

                        # 按阅读量/热度排序
                        sorted_list = sorted(
                            telegraph_list,
                            key=lambda x: x.get('readCount', 0) or x.get('pv', 0) or 0,
                            reverse=True
                        )

                        for idx, item in enumerate(sorted_list[:15], 1):
                            title = item.get('title', '') or item.get('content', '')
                            item_id = item.get('id', '')
                            ctime = item.get('ctime', '')
                            read_count = item.get('readCount', 0) or item.get('pv', 0)

                            # 提取时间
                            time_str = ''
                            if ctime:
                                try:
                                    from datetime import datetime
                                    dt = datetime.fromtimestamp(int(ctime))
                                    time_str = dt.strftime('%H:%M')
                                except (ValueError, TypeError):
                                    pass

                            if title:
                                # 截断标题
                                if len(title) > 80:
                                    title = title[:80] + '...'

                                items.append({
                                    'title': title,
                                    'url': f'https://www.cls.cn/telegraph/{item_id}' if item_id else 'https://www.cls.cn/telegraph',
                                    'time': f'热度{read_count}' if read_count else time_str,
                                    'source': self.name
                                })

                        break

            return items

        except Exception as e:
            print(f"[{self.name}] 解析失败: {e}")
            return []