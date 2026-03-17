"""
同花顺概念股爬虫 - 获取概念资金流向数据
"""
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import re
from .base import BaseCrawler


class ConceptCrawler(BaseCrawler):
    """同花顺概念股爬虫"""

    name = "概念股"
    source_type = "concept"
    enabled = True

    # 概念资金流向页面
    GN_URL = "https://q.10jqka.com.cn/gn/"

    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取概念股数据"""
        response = self.fetch(self.GN_URL)
        if not response:
            return []

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            concepts = self._parse_concept_table(soup)
            return concepts
        except Exception as e:
            print(f"[{self.name}] 解析失败: {e}")
            return []

    def _parse_concept_table(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """解析概念表格"""
        concepts = []

        # 查找表格
        table = soup.find('table', {'class': 'm-table'})
        if not table:
            # 尝试其他选择器
            table = soup.find('table')

        if not table:
            print(f"[{self.name}] 未找到表格")
            return concepts

        tbody = table.find('tbody')
        if not tbody:
            tbody = table

        rows = tbody.find_all('tr')

        for row in rows:
            try:
                cells = row.find_all('td')
                if len(cells) < 5:
                    continue

                # 解析概念名称和代码
                name_cell = cells[0]
                link = name_cell.find('a')
                if link:
                    concept_name = link.get_text(strip=True)
                    href = link.get('href', '')
                    # 从链接提取代码，如 /gn/detail/code/301558/
                    code_match = re.search(r'/code/(\d+)/', href)
                    concept_code = code_match.group(1) if code_match else ''
                else:
                    concept_name = name_cell.get_text(strip=True)
                    concept_code = ''

                # 解析涨跌幅
                change_cell = cells[1]
                change_text = change_cell.get_text(strip=True)
                change_pct = self._parse_change(change_text)

                # 解析领涨股
                lead_stock_cell = cells[2]
                lead_link = lead_stock_cell.find('a')
                if lead_link:
                    lead_stock_name = lead_link.get_text(strip=True)
                    lead_stock_code = self._extract_stock_code(lead_link.get('href', ''))
                else:
                    lead_stock_name = lead_stock_cell.get_text(strip=True)
                    lead_stock_code = ''

                # 解析领涨股涨幅
                lead_change_cell = cells[3]
                lead_change = self._parse_change(lead_change_cell.get_text(strip=True))

                # 解析资金净额
                amount_cell = cells[4] if len(cells) > 4 else None
                net_amount = 0
                if amount_cell:
                    amount_text = amount_cell.get_text(strip=True)
                    net_amount = self._parse_amount(amount_text)

                # 解析涨跌家数
                up_down_cell = cells[5] if len(cells) > 5 else None
                up_count, down_count = 0, 0
                if up_down_cell:
                    up_down_text = up_down_cell.get_text(strip=True)
                    up_count, down_count = self._parse_up_down(up_down_text)

                concept = {
                    'name': concept_name,
                    'code': concept_code,
                    'change_pct': change_pct,
                    'lead_stock': {
                        'name': lead_stock_name,
                        'code': lead_stock_code,
                        'change_pct': lead_change
                    },
                    'net_amount': net_amount,
                    'up_count': up_count,
                    'down_count': down_count,
                    'url': f"https://q.10jqka.com.cn/gn/detail/code/{concept_code}/" if concept_code else ''
                }

                concepts.append(concept)

                # 限制数量
                if len(concepts) >= 50:
                    break

            except Exception as e:
                print(f"[{self.name}] 解析行失败: {e}")
                continue

        return concepts

    def _parse_change(self, text: str) -> float:
        """解析涨跌幅"""
        try:
            # 去除百分号
            text = text.replace('%', '').replace('+', '').strip()
            return float(text)
        except:
            return 0.0

    def _extract_stock_code(self, href: str) -> str:
        """从链接提取股票代码"""
        match = re.search(r'/(\d{6})\.shtml', href)
        if match:
            return match.group(1)
        return ''

    def _parse_amount(self, text: str) -> float:
        """解析资金净额（亿元）"""
        try:
            text = text.replace('亿', '').strip()
            if '万' in text:
                text = text.replace('万', '')
                return float(text) / 10000  # 转换为亿
            return float(text)
        except:
            return 0.0

    def _parse_up_down(self, text: str) -> tuple:
        """解析涨跌家数"""
        try:
            # 格式通常为 "12/3" 或 "12家涨/3家跌"
            parts = text.replace('家', '').replace('涨', '').replace('跌', '').split('/')
            if len(parts) == 2:
                return int(parts[0]), int(parts[1])
        except:
            pass
        return 0, 0

    def get_concept_by_name(self, concept_name: str) -> Dict[str, Any]:
        """根据概念名称获取概念详情"""
        concepts = self.get_data()
        for concept in concepts:
            if concept_name in concept.get('name', ''):
                return concept
        return {}

    def get_hot_concepts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门概念（按资金流入排序）"""
        concepts = self.get_data()
        # 按资金净流入排序
        sorted_concepts = sorted(concepts, key=lambda x: x.get('net_amount', 0), reverse=True)
        return sorted_concepts[:limit]

    def get_rising_concepts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取上涨概念（按涨幅排序）"""
        concepts = self.get_data()
        # 按涨幅排序
        sorted_concepts = sorted(concepts, key=lambda x: x.get('change_pct', 0), reverse=True)
        return sorted_concepts[:limit]


# 便捷函数
def get_all_concepts() -> List[Dict[str, Any]]:
    """获取所有概念"""
    crawler = ConceptCrawler()
    return crawler.get_data()


def get_hot_concepts(limit: int = 10) -> List[Dict[str, Any]]:
    """获取热门概念"""
    crawler = ConceptCrawler()
    return crawler.get_hot_concepts(limit)