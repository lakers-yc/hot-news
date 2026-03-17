"""
第一财经热榜爬虫 - 获取热门新闻
"""
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base import BaseCrawler


class YicaiHotCrawler(BaseCrawler):
    name = "第一财经热榜"
    source_type = "hot"
    enabled = True

    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取第一财经热门新闻"""
        url = "https://www.yicai.com/news/"

        response = self.fetch(url)
        if not response:
            return []

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            items = []
            seen = set()  # 去重

            # 尝试多种选择器
            selectors = [
                '.news-list li',
                '.hot-news li',
                '.news-item',
                '.list-item',
                'article'
            ]

            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    for idx, item in enumerate(elements[:15], 1):
                        title_a = item.select_one('a')
                        if title_a:
                            title = title_a.get('title', '') or title_a.get_text(strip=True)
                            href = title_a.get('href', '')

                            if title and len(title) > 5 and title not in seen:
                                seen.add(title)
                                items.append({
                                    'title': title[:100] if len(title) > 100 else title,
                                    'url': href if href.startswith('http') else f'https://www.yicai.com{href}',
                                    'time': f'第{len(items)+1}名',
                                    'source': self.name
                                })

                    if items:
                        break

            # 如果选择器都没找到，尝试从标题标签解析
            if not items:
                for a in soup.find_all('a', href=True)[:30]:
                    title = a.get('title', '') or a.get_text(strip=True)
                    href = a.get('href', '')

                    # 筛选新闻链接
                    if title and len(title) > 10 and '/news/' in href and title not in seen:
                        seen.add(title)
                        items.append({
                            'title': title[:100] if len(title) > 100 else title,
                            'url': href if href.startswith('http') else f'https://www.yicai.com{href}',
                            'time': '',
                            'source': self.name
                        })

                    if len(items) >= 15:
                        break

            return items

        except Exception as e:
            print(f"[{self.name}] 解析失败: {e}")
            return []