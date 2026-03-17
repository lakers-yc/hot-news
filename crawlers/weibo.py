"""
微博热搜爬虫 - 获取真实数据
"""
from typing import List, Dict, Any
from .base import BaseCrawler


class WeiboCrawler(BaseCrawler):
    name = "微博热搜"
    source_type = "hot"
    enabled = False  # 禁用: 连接超时，网络无法访问

    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取微博热搜 - 使用微博API"""
        url = "https://m.weibo.cn/api/container/getIndex"
        params = {'containerid': '106003type=25&t=3&disable_hot=1&filter_type=realtimehot'}

        try:
            response = self.fetch(url, params=params)
            if not response:
                return []

            # 处理编码问题
            try:
                data = response.json()
            except Exception:
                # 尝试手动解码
                content = response.content
                try:
                    text = content.decode('utf-8')
                except UnicodeDecodeError:
                    text = content.decode('gbk', errors='ignore')
                import json
                data = json.loads(text)

            items = []

            cards = data.get('data', {}).get('cards', [])
            if cards:
                for card in cards:
                    card_group = card.get('card_group', [])
                    for item in card_group[:15]:
                        desc = item.get('desc', '') or item.get('title_sub', '')

                        if desc:
                            items.append({
                                'title': desc,
                                'url': f'https://s.weibo.com/weibo?q={desc}',
                                'time': f'热搜第{len(items)+1}名' if len(items) < 15 else '热搜',
                                'source': self.name
                            })

            return items

        except Exception as e:
            print(f"[{self.name}] 解析失败: {e}")
            return []