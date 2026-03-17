"""
中国政府网爬虫 - 获取真实数据
"""
from typing import List, Dict, Any
from .base import BaseCrawler


class GovCrawler(BaseCrawler):
    name = "中国政府网"
    source_type = "official"
    enabled = False  # 禁用: HTML结构变更，数据为空

    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取中国政府网政策"""
        url = "http://www.gov.cn/zhengce/"

        response = self.fetch(url)
        if not response:
            return []

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'lxml')
            items = []

            for item in soup.select('.list li')[:15]:
                a = item.select_one('a')
                date_span = item.select_one('.date')

                if a:
                    title = a.get_text(strip=True)
                    href = a.get('href', '')
                    time_str = date_span.get_text(strip=True) if date_span else ''

                    items.append({
                        'title': title,
                        'url': f'http://www.gov.cn{href}' if href and not href.startswith('http') else href or 'http://www.gov.cn',
                        'time': time_str,
                        'source': self.name
                    })

            return items

        except Exception as e:
            print(f"[{self.name}] 解析失败: {e}")
            return []