"""
东方财富热榜爬虫 - 获取财经热点新闻
"""
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base import BaseCrawler


class EastmoneyHotCrawler(BaseCrawler):
    name = "东方财富热榜"
    source_type = "hot"
    enabled = True

    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取东方财富首页热点新闻"""
        url = "https://www.eastmoney.com/"

        response = self.fetch(url)
        if not response:
            return []

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            items = []
            seen = set()

            # 查找热点新闻列表
            selectors = [
                '.newsitem a',
                '.hotnews li a',
                '.mainNews li a',
                '.nlist li a',
                '.newsList li a',
                '.hot-list a',
            ]

            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    for idx, a in enumerate(elements[:20], 1):
                        title = a.get_text(strip=True)
                        href = a.get('href', '')

                        # 过滤有效新闻
                        if title and len(title) > 8 and title not in seen:
                            seen.add(title)

                            # 提取时间（如果有）
                            time_str = ''
                            time_span = a.find_next('span', class_='time')
                            if time_span:
                                time_str = time_span.get_text(strip=True)

                            items.append({
                                'title': title[:80] if len(title) > 80 else title,
                                'url': href if href.startswith('http') else f'https://www.eastmoney.com{href}',
                                'time': time_str or f'第{len(items)+1}名',
                                'source': self.name
                            })

                            if len(items) >= 15:
                                break

                if len(items) >= 15:
                    break

            # 如果上面没找到，尝试更通用的方式
            if len(items) < 5:
                for a in soup.find_all('a', href=True)[:50]:
                    title = a.get_text(strip=True)
                    href = a.get('href', '')

                    # 筛选新闻链接
                    if title and len(title) > 10 and len(title) < 100:
                        if title not in seen:
                            if '/a/' in href or 'news' in href or '.html' in href:
                                seen.add(title)
                                items.append({
                                    'title': title,
                                    'url': href if href.startswith('http') else f'https://www.eastmoney.com{href}',
                                    'time': '',
                                    'source': self.name
                                })
                                if len(items) >= 15:
                                    break

            return items

        except Exception as e:
            print(f"[{self.name}] 解析失败: {e}")
            return []