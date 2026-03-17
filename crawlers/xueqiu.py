"""
雪球爬虫 - 获取真实数据
通过先访问首页获取Cookie来绕过WAF
"""
from typing import List, Dict, Any
from .base import BaseCrawler


class XueqiuCrawler(BaseCrawler):
    name = "雪球"
    source_type = "hot"
    enabled = False  # 禁用: WAF保护，无法绕过

    def __init__(self, timeout: int = 15):
        super().__init__(timeout)
        self._cookies = None

    def _init_cookies(self) -> bool:
        """访问首页获取Cookie"""
        if self._cookies:
            return True

        try:
            # 使用curl_cffi访问首页获取cookies
            from curl_cffi import requests as curl_requests

            headers = self._get_headers()
            response = curl_requests.get(
                'https://xueqiu.com',
                headers=headers,
                timeout=self.timeout,
                impersonate='chrome120'
            )

            # 提取cookies
            self._cookies = dict(response.cookies)
            return True
        except Exception as e:
            print(f"[{self.name}] 获取Cookie失败: {e}")
            return False

    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取雪球热门股票"""
        # 先尝试获取Cookie
        self._init_cookies()

        url = "https://stock.xueqiu.com/v5/stock/hot_stock/list.json"
        params = {'type': '10', 'size': 20}

        try:
            from curl_cffi import requests as curl_requests

            headers = self._get_headers()
            headers['Referer'] = 'https://xueqiu.com/'

            response = curl_requests.get(
                url,
                params=params,
                headers=headers,
                cookies=self._cookies,
                timeout=self.timeout,
                impersonate='chrome120'
            )

            if response.status_code != 200:
                print(f"[{self.name}] HTTP状态码: {response.status_code}")
                # 重置cookies，下次重新获取
                self._cookies = None
                return []

            data = response.json()
            items = []

            for item in data.get('data', {}).get('items', []):
                stock = item.get('stock', {})
                name = stock.get('name', '')
                symbol = stock.get('symbol', '')
                reason = item.get('reason', '')

                items.append({
                    'title': f"{name} - {reason}" if reason else name,
                    'url': f'https://xueqiu.com/S/{symbol}' if symbol else 'https://xueqiu.com',
                    'time': f"热度{item.get('rank', '')}名",
                    'source': self.name
                })

            return items

        except Exception as e:
            print(f"[{self.name}] 解析失败: {e}")
            # 重置cookies
            self._cookies = None
            return []