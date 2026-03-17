"""
证券时报爬虫 - 获取真实数据
"""
from typing import List, Dict, Any
from .base import BaseCrawler


class StcnCrawler(BaseCrawler):
    name = "证券时报"
    source_type = "fast"
    enabled = True

    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取证券时报快讯"""
        url = "https://news.stcn.com/sd/index.html"

        response = self.fetch(url)
        if not response:
            return []

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'lxml')
            items = []

            for item in soup.select('.news_list li')[:15]:
                a = item.select_one('a')
                time_span = item.select_one('.time')

                if a:
                    title = a.get_text(strip=True)
                    href = a.get('href', '')
                    time_str = time_span.get_text(strip=True) if time_span else ''

                    items.append({
                        'title': title,
                        'url': href if href.startswith('http') else f'https://news.stcn.com{href}',
                        'time': time_str,
                        'source': self.name
                    })

            return items

        except Exception as e:
            print(f"[{self.name}] 解析失败: {e}")
            return []