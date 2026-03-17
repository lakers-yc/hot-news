"""
市场数据爬虫 - 获取A50期货、汇率、异动股等市场情绪数据
"""
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import re
import json
from .base import BaseCrawler


class MarketCrawler(BaseCrawler):
    """市场数据爬虫"""

    name = "市场数据"
    source_type = "market"
    enabled = True

    # API URLs
    A50_URL = "https://quote.eastmoney.com/center/api/realtime_futures_data"
    USD_CNY_URL = "https://quote.eastmoney.com/api/quote/realtime?codes=USDCNY"
    ABNORMAL_URL = "https://eq.10jqka.com.cn/webpage/abnormal-alert/"

    def fetch_data(self) -> Dict[str, Any]:
        """获取市场数据"""
        return {
            'a50': self.get_a50_data(),
            'exchange_rate': self.get_exchange_rate(),
            'abnormal_stocks': self.get_abnormal_stocks(),
            'us_market': self.get_us_market_preview()
        }

    def get_a50_data(self) -> Dict[str, Any]:
        """获取A50期货数据"""
        try:
            # 东方财富A50期货行情接口
            url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
            params = {
                'fltt': 2,
                'invt': 2,
                'fields': 'f1,f2,f3,f4,f12,f13,f14',
                'secids': '142.IH,142.IC,142.IM,142.IF'  # 股指期货
            }

            response = self.fetch(url, params=params)
            if not response:
                return self._get_a50_fallback()

            data = response.json()
            if data and 'data' in data and 'diff' in data['data']:
                result = {}
                for item in data['data']['diff']:
                    code = item.get('f12', '')
                    name = item.get('f14', '')
                    price = item.get('f2', 0)
                    change = item.get('f3', 0)

                    # 判断涨跌
                    if code == 'IH':
                        result['if_ih'] = {'name': name, 'price': price, 'change': change}
                    elif code == 'IC':
                        result['if_ic'] = {'name': name, 'price': price, 'change': change}
                    elif code == 'IM':
                        result['if_im'] = {'name': name, 'price': price, 'change': change}
                    elif code == 'IF':
                        result['if_main'] = {'name': name, 'price': price, 'change': change}

                return result

            return self._get_a50_fallback()

        except Exception as e:
            print(f"[{self.name}] A50数据获取失败: {e}")
            return self._get_a50_fallback()

    def _get_a50_fallback(self) -> Dict[str, Any]:
        """A50数据回退方案"""
        try:
            # 尝试新浪接口
            url = "https://hq.sinajs.cn/list=nf_IF0"
            headers = {'Referer': 'https://finance.sina.com.cn'}
            response = self.fetch(url, headers=headers)

            if response:
                text = response.text
                # 解析格式: var hq_str_nf_IF0="名称,昨收,今开,最高,最低,最新,..."
                match = re.search(r'="([^"]+)"', text)
                if match:
                    parts = match.group(1).split(',')
                    if len(parts) > 6:
                        return {
                            'name': parts[0],
                            'last_close': float(parts[1]),
                            'open': float(parts[2]),
                            'high': float(parts[3]),
                            'low': float(parts[4]),
                            'price': float(parts[5]),
                            'change': round((float(parts[5]) - float(parts[1])) / float(parts[1]) * 100, 2)
                        }
        except Exception as e:
            print(f"[{self.name}] A50回退数据获取失败: {e}")

        return {'name': 'A50期货', 'price': 0, 'change': 0, 'error': '数据暂时不可用'}

    def get_exchange_rate(self) -> Dict[str, Any]:
        """获取美元人民币汇率"""
        try:
            # 东方财富汇率接口
            url = "https://push2.eastmoney.com/api/qt/stock/get"
            params = {
                'fltt': 2,
                'invt': 2,
                'fields': 'f43,f44,f45,f46,f47,f48,f50,f51,f52,f58',
                'secid': '100.USDCNY'
            }

            response = self.fetch(url, params=params)
            if not response:
                return self._get_exchange_rate_fallback()

            data = response.json()
            if data and 'data' in data:
                d = data['data']
                return {
                    'name': '美元人民币',
                    'price': d.get('f43', 0) / 100 if d.get('f43') else 0,
                    'change': d.get('f50', 0) / 100 if d.get('f50') else 0,
                    'change_pct': d.get('f51', 0) / 100 if d.get('f51') else 0,
                    'high': d.get('f44', 0) / 100 if d.get('f44') else 0,
                    'low': d.get('f45', 0) / 100 if d.get('f45') else 0
                }

            return self._get_exchange_rate_fallback()

        except Exception as e:
            print(f"[{self.name}] 汇率数据获取失败: {e}")
            return self._get_exchange_rate_fallback()

    def _get_exchange_rate_fallback(self) -> Dict[str, Any]:
        """汇率数据回退方案"""
        try:
            url = "https://api.exchangerate.host/latest"
            params = {'base': 'USD', 'symbols': 'CNY'}
            response = self.fetch(url, params=params)

            if response:
                data = response.json()
                if data and 'rates' in data and 'CNY' in data['rates']:
                    return {
                        'name': '美元人民币',
                        'price': data['rates']['CNY'],
                        'change': 0,
                        'change_pct': 0
                    }
        except Exception as e:
            print(f"[{self.name}] 汇率回退数据获取失败: {e}")

        return {'name': '美元人民币', 'price': 7.2, 'change': 0, 'change_pct': 0, 'error': '使用默认值'}

    def get_abnormal_stocks(self) -> List[Dict[str, Any]]:
        """获取异动股票数据"""
        try:
            response = self.fetch(self.ABNORMAL_URL)
            if not response:
                return []

            soup = BeautifulSoup(response.text, 'lxml')
            abnormals = []

            # 查找异动表格
            table = soup.find('table')
            if not table:
                return []

            rows = table.find_all('tr')[1:]  # 跳过表头

            for row in rows[:20]:  # 取前20条
                try:
                    cells = row.find_all('td')
                    if len(cells) < 4:
                        continue

                    # 股票名称和代码
                    name_cell = cells[0]
                    link = name_cell.find('a')
                    if link:
                        stock_name = link.get_text(strip=True)
                        stock_code = self._extract_stock_code(link.get('href', ''))
                    else:
                        stock_name = name_cell.get_text(strip=True)
                        stock_code = ''

                    # 异动时间
                    time_cell = cells[1] if len(cells) > 1 else None
                    abnormal_time = time_cell.get_text(strip=True) if time_cell else ''

                    # 异动类型
                    type_cell = cells[2] if len(cells) > 2 else None
                    abnormal_type = type_cell.get_text(strip=True) if type_cell else ''

                    # 涨跌幅
                    change_cell = cells[3] if len(cells) > 3 else None
                    change_pct = self._parse_change(change_cell.get_text(strip=True)) if change_cell else 0

                    # 异动原因
                    reason_cell = cells[4] if len(cells) > 4 else None
                    reason = reason_cell.get_text(strip=True) if reason_cell else ''

                    abnormals.append({
                        'name': stock_name,
                        'code': stock_code,
                        'time': abnormal_time,
                        'type': abnormal_type,
                        'change_pct': change_pct,
                        'reason': reason
                    })

                except Exception as e:
                    continue

            return abnormals

        except Exception as e:
            print(f"[{self.name}] 异动股数据获取失败: {e}")
            return []

    def get_us_market_preview(self) -> Dict[str, Any]:
        """获取美股行情预览"""
        try:
            # 获取美股三大指数
            url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
            params = {
                'fltt': 2,
                'invt': 2,
                'fields': 'f1,f2,f3,f12,f13,f14',
                'secids': '100.DJIA,100.SPX,100.NDX'  # 道琼斯、标普、纳斯达克
            }

            response = self.fetch(url, params=params)
            if not response:
                return {}

            data = response.json()
            if data and 'data' in data and 'diff' in data['data']:
                result = {}
                for item in data['data']['diff']:
                    code = item.get('f12', '')
                    name_map = {
                        'DJIA': '道琼斯',
                        'SPX': '标普500',
                        'NDX': '纳斯达克'
                    }
                    result[code.lower()] = {
                        'name': name_map.get(code, item.get('f14', '')),
                        'price': item.get('f2', 0),
                        'change': item.get('f3', 0)
                    }

                return result

        except Exception as e:
            print(f"[{self.name}] 美股数据获取失败: {e}")

        return {}

    def _extract_stock_code(self, href: str) -> str:
        """从链接提取股票代码"""
        match = re.search(r'/(\d{6})\.shtml', href)
        if match:
            return match.group(1)
        return ''

    def _parse_change(self, text: str) -> float:
        """解析涨跌幅"""
        try:
            text = text.replace('%', '').replace('+', '').strip()
            return float(text)
        except:
            return 0.0

    def get_market_sentiment(self) -> Dict[str, Any]:
        """获取市场情绪综合评估"""
        data = self.get_data()

        sentiment = {
            'score': 0,  # -100 到 100 的情绪分数
            'factors': [],
            'summary': ''
        }

        # A50影响
        a50 = data.get('a50', {})
        if isinstance(a50, dict) and 'change' in a50:
            a50_change = a50.get('change', 0)
            if a50_change > 0.5:
                sentiment['score'] += 20
                sentiment['factors'].append(f"A50期货上涨{a50_change}%，利好开盘")
            elif a50_change < -0.5:
                sentiment['score'] -= 20
                sentiment['factors'].append(f"A50期货下跌{abs(a50_change)}%，偏空信号")

        # 汇率影响
        exchange = data.get('exchange_rate', {})
        if isinstance(exchange, dict) and 'change' in exchange:
            rate_change = exchange.get('change_pct', 0)
            if rate_change > 0.1:  # 人民币贬值
                sentiment['score'] -= 10
                sentiment['factors'].append("人民币贬值，外资流出压力")
            elif rate_change < -0.1:  # 人民币升值
                sentiment['score'] += 10
                sentiment['factors'].append("人民币升值，利好外资流入")

        # 美股影响
        us_market = data.get('us_market', {})
        if us_market:
            spx = us_market.get('spx', {})
            if isinstance(spx, dict):
                spx_change = spx.get('change', 0)
                if spx_change > 1:
                    sentiment['score'] += 15
                    sentiment['factors'].append(f"美股大涨{round(spx_change, 2)}%，利好情绪")
                elif spx_change < -1:
                    sentiment['score'] -= 15
                    sentiment['factors'].append(f"美股大跌{abs(round(spx_change, 2))}%，偏空影响")

        # 生成摘要
        if sentiment['score'] > 30:
            sentiment['summary'] = "市场情绪偏暖，有利于做多"
        elif sentiment['score'] > 10:
            sentiment['summary'] = "市场情绪温和，可适度参与"
        elif sentiment['score'] > -10:
            sentiment['summary'] = "市场情绪中性，观望为主"
        elif sentiment['score'] > -30:
            sentiment['summary'] = "市场情绪偏弱，谨慎操作"
        else:
            sentiment['summary'] = "市场情绪悲观，建议防守"

        return sentiment


# 便捷函数
def get_market_data() -> Dict[str, Any]:
    """获取市场数据"""
    crawler = MarketCrawler()
    return crawler.get_data()


def get_market_sentiment() -> Dict[str, Any]:
    """获取市场情绪"""
    crawler = MarketCrawler()
    return crawler.get_market_sentiment()


def get_abnormal_stocks() -> List[Dict[str, Any]]:
    """获取异动股票"""
    crawler = MarketCrawler()
    return crawler.get_abnormal_stocks()