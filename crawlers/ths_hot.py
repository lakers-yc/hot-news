"""
同花顺热榜爬虫 - 获取概念热榜和热门股票
"""
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import re
from .base import BaseCrawler


class ThsHotCrawler(BaseCrawler):
    name = "同花顺热榜"
    source_type = "hot"
    enabled = True

    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取同花顺概念热榜"""
        url = "https://q.10jqka.com.cn/gn/"

        response = self.fetch(url)
        if not response:
            return []

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            items = []

            # 解析概念热榜表格
            for tr in soup.select('tbody tr')[:15]:
                tds = tr.select('td')
                if len(tds) >= 3:
                    # 概念名称
                    name_a = tds[1].select_one('a')
                    name = name_a.get_text(strip=True) if name_a else ''
                    href = name_a.get('href', '') if name_a else ''

                    # 领涨股
                    stock_a = tds[2].select_one('a')
                    stock = stock_a.get_text(strip=True) if stock_a else ''

                    # 涨跌幅
                    change = tds[3].get_text(strip=True) if len(tds) > 3 else ''

                    if name:
                        title = f"{name}"
                        if stock:
                            title += f" - 领涨: {stock}"
                        if change:
                            title += f" ({change})"

                        items.append({
                            'title': title,
                            'url': href if href.startswith('http') else f'https://q.10jqka.com.cn{href}',
                            'time': change if change else '',
                            'source': self.name
                        })

            # 如果概念热榜数据不足，尝试获取热门股票
            if len(items) < 5:
                items.extend(self._fetch_hot_stocks())

            return items[:15]

        except Exception as e:
            print(f"[{self.name}] 解析失败: {e}")
            return []

    def _fetch_hot_stocks(self) -> List[Dict[str, Any]]:
        """获取热门股票"""
        url = "https://q.10jqka.com.cn/index/"
        response = self.fetch(url)
        if not response:
            return []

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            items = []

            for li in soup.select('.board-hq-list li')[:10]:
                a = li.select_one('a')
                if a:
                    name = a.get_text(strip=True)
                    href = a.get('href', '')

                    if name:
                        items.append({
                            'title': name,
                            'url': href if href.startswith('http') else f'https://q.10jqka.com.cn{href}',
                            'time': '',
                            'source': self.name
                        })

            return items

        except Exception as e:
            print(f"[{self.name}] 获取热门股票失败: {e}")
            return []