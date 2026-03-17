"""
新华社爬虫 - 获取真实数据
"""
from typing import List, Dict, Any
from .base import BaseCrawler


class XinhuaCrawler(BaseCrawler):
    name = "新华社"
    source_type = "official"
    enabled = False  # 禁用: HTML结构变更，数据为空

    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取新华社新闻"""
        url = "http://www.xinhuanet.com/"

        response = self.fetch(url)
        if not response:
            return []

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'lxml')
            items = []

            # 尝试多个选择器
            selectors = ['.dataList li', '.news-item li', '.main-list li', 'li.news']
            news_list = []

            for selector in selectors:
                news_list = soup.select(selector)
                if news_list:
                    break

            for item in news_list[:15]:
                a = item.select_one('a')
                time_elem = item.select_one('.time, .date')

                if a:
                    title = a.get_text(strip=True)
                    href = a.get('href', '')
                    time_str = time_elem.get_text(strip=True) if time_elem else ''

                    if title:
                        items.append({
                            'title': title,
                            'url': href if href.startswith('http') else f'http://www.xinhuanet.com{href}',
                            'time': time_str,
                            'source': self.name
                        })

            return items

        except Exception as e:
            print(f"[{self.name}] 解析失败: {e}")
            return []