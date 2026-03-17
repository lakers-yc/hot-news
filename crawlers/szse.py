"""
深交所爬虫 - 获取真实数据
"""
from typing import List, Dict, Any
from .base import BaseCrawler


class SzseCrawler(BaseCrawler):
    name = "深交所"
    source_type = "official"
    enabled = False  # 禁用: HTML结构变更，需JavaScript渲染

    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取深交所公告"""
        url = "http://www.szse.cn/disclosure/notice/index.html"

        response = self.fetch(url)
        if not response:
            return []

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'lxml')
            items = []

            for item in soup.select('.news-list li')[:15]:
                a = item.select_one('a')
                time_span = item.select_one('span')

                if a:
                    title = a.get_text(strip=True)
                    href = a.get('href', '')
                    time_str = time_span.get_text(strip=True) if time_span else ''

                    items.append({
                        'title': title,
                        'url': f'http://www.szse.cn{href}' if href and not href.startswith('http') else href or 'http://www.szse.cn',
                        'time': time_str,
                        'source': self.name
                    })

            return items

        except Exception as e:
            print(f"[{self.name}] 解析失败: {e}")
            return []