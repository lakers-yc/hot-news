"""
东方财富爬虫 - 获取真实数据
"""
from typing import List, Dict, Any
from .base import BaseCrawler


class EastmoneyCrawler(BaseCrawler):
    name = "东方财富"
    source_type = "fast"
    enabled = True

    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取东方财富7x24快讯 - 实时数据"""
        url = "https://np-listapi.eastmoney.com/comm/web/getFastNewsList"
        params = {
            'client': 'web',
            'biz': 'web_724',
            'fastColumn': '102',
            'pageSize': 20,
            'sortEnd': '',
            'req_trace': '1'
        }

        response = self.fetch(url, params=params)
        if not response:
            return []

        try:
            data = response.json()
            items = []

            news_list = data.get('data', {}).get('fastNewsList', [])
            for item in news_list[:15]:
                title = item.get('title', '')
                code = item.get('code', '')
                show_time = item.get('showTime', '')

                # 提取时间部分 (HH:MM)
                time_str = ''
                if show_time:
                    try:
                        time_str = show_time.split(' ')[1][:5] if ' ' in show_time else show_time[:5]
                    except:
                        pass

                if title:
                    items.append({
                        'title': title,
                        'url': f'https://finance.eastmoney.com/a/{code}.html' if code else 'https://www.eastmoney.com',
                        'time': time_str,
                        'source': self.name
                    })

            return items

        except Exception as e:
            print(f"[{self.name}] 解析失败: {e}")
            return []