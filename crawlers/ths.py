"""
同花顺爬虫 - 获取真实数据
"""
from typing import List, Dict, Any
import re
from bs4 import BeautifulSoup
from .base import BaseCrawler


class ThsCrawler(BaseCrawler):
    name = "同花顺"
    source_type = "fast"
    enabled = True

    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取同花顺热点新闻"""
        url = "https://www.10jqka.com.cn/"

        response = self.fetch(url)
        if not response:
            return []

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            items = []
            seen = set()

            # 查找所有新闻链接
            for a in soup.find_all('a', href=True):
                text = a.get_text(strip=True)
                href = a.get('href', '')

                # 筛选新闻链接
                if len(text) > 15 and len(text) < 150 and '.shtml' in href:
                    if text not in seen:
                        seen.add(text)

                        # 提取时间
                        time_str = ''
                        time_match = re.search(r'(\d+)小时前', text)
                        if time_match:
                            time_str = time_match.group(1) + 'h'

                        # 清理标题 - 在来源名称处截断
                        title = text
                        # 添加更多变体关键词
                        stop_words = [
                            '同花顺', '同花顺7x24快讯', '同顺号',
                            '中国证券报', '证券时报', '上海证券报',
                            '中国基金报', '基金报', '中证报'
                        ]
                        for stop_word in stop_words:
                            if stop_word in title:
                                title = title.split(stop_word)[0].strip()
                                break

                        # 额外清理末尾的时间信息
                        title = re.sub(r'\d+小时前$', '', title).strip()

                        if len(title) > 10:
                            items.append({
                                'title': title,
                                'url': href if href.startswith('http') else f'https://www.10jqka.com.cn{href}',
                                'time': time_str,
                                'source': self.name
                            })

                        if len(items) >= 15:
                            break

            return items

        except Exception as e:
            print(f"[{self.name}] 解析失败: {e}")
            return []