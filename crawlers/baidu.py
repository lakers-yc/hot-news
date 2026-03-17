"""
百度热榜爬虫 - 获取实时热搜数据
"""
import re
from typing import List, Dict, Any
from .base import BaseCrawler


class BaiduCrawler(BaseCrawler):
    name = "百度热榜"
    source_type = "hot"
    enabled = True

    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取百度热榜 - 从页面提取JSON数据"""
        url = "https://top.baidu.com/board?tab=realtime"

        response = self.fetch(url)
        if not response:
            return []

        try:
            # 确保正确解码
            text = response.text
            if not text:
                text = response.content.decode('utf-8', errors='ignore')

            items = []

            # 使用正则提取热榜数据
            # 格式: "word":"标题"
            word_pattern = r'"word":"([^"]+)"'
            words = re.findall(word_pattern, text)

            # 提取热度: "hotScore":"12345"
            score_pattern = r'"hotScore":"?(\d+)"?'
            scores = re.findall(score_pattern, text)

            # 提取链接: "url":"..."
            url_pattern = r'"rawUrl":"([^"]+)"'
            urls = re.findall(url_pattern, text)

            # 组合数据
            for i, word in enumerate(words[:15]):
                if word:
                    score = scores[i] if i < len(scores) else ''
                    link = urls[i] if i < len(urls) else 'https://www.baidu.com'

                    items.append({
                        'title': word,
                        'url': link if link.startswith('http') else f'https://www.baidu.com/s?wd={word}',
                        'time': f'热度 {score}' if score else f'第{i+1}名',
                        'source': self.name
                    })

            return items

        except Exception as e:
            print(f"[{self.name}] 解析失败: {e}")
            return []