"""
股票推荐模块 - 根据概念匹配推荐龙头股和弹性股
"""
from typing import List, Dict, Any, Tuple, Optional
import os
import json


class StockRecommender:
    """股票推荐器"""

    # 概念龙头股配置（概念 -> 龙头股信息）
    CONCEPT_LEADERS = {
        "人工智能": [
            {"code": "002230", "name": "科大讯飞", "type": "龙头", "logic": "AI语音龙头，大模型核心标的"},
            {"code": "688327", "name": "云从科技", "type": "弹性", "logic": "AI算法龙头，计算机视觉"},
            {"code": "300474", "name": "景嘉微", "type": "弹性", "logic": "国产GPU芯片"}
        ],
        "算力": [
            {"code": "000977", "name": "浪潮信息", "type": "龙头", "logic": "AI服务器龙头"},
            {"code": "603881", "name": "数据港", "type": "弹性", "logic": "数据中心运营商"},
            {"code": "300382", "name": "斯达半导", "type": "弹性", "logic": "功率半导体"}
        ],
        "半导体": [
            {"code": "688981", "name": "中芯国际", "type": "龙头", "logic": "国内晶圆代工龙头"},
            {"code": "002371", "name": "北方华创", "type": "龙头", "logic": "半导体设备龙头"},
            {"code": "688256", "name": "寒武纪", "type": "弹性", "logic": "AI芯片设计"}
        ],
        "新能源": [
            {"code": "300274", "name": "阳光电源", "type": "龙头", "logic": "光伏逆变器龙头"},
            {"code": "002459", "name": "晶澳科技", "type": "龙头", "logic": "光伏组件龙头"},
            {"code": "300014", "name": "亿纬锂能", "type": "弹性", "logic": "动力电池"}
        ],
        "新能源汽车": [
            {"code": "002594", "name": "比亚迪", "type": "龙头", "logic": "新能源汽车龙头"},
            {"code": "300750", "name": "宁德时代", "type": "龙头", "logic": "动力电池龙头"},
            {"code": "002074", "name": "国轩高科", "type": "弹性", "logic": "动力电池"}
        ],
        "医药": [
            {"code": "300760", "name": "迈瑞医疗", "type": "龙头", "logic": "医疗器械龙头"},
            {"code": "603259", "name": "药明康德", "type": "龙头", "logic": "CRO龙头"},
            {"code": "300122", "name": "智飞生物", "type": "弹性", "logic": "疫苗龙头"}
        ],
        "军工": [
            {"code": "600893", "name": "航发动力", "type": "龙头", "logic": "航空发动机龙头"},
            {"code": "002179", "name": "中航光电", "type": "龙头", "logic": "军工电子连接器"},
            {"code": "300034", "name": "钢研高纳", "type": "弹性", "logic": "高温合金"}
        ],
        "机器人": [
            {"code": "002747", "name": "埃斯顿", "type": "龙头", "logic": "工业机器人龙头"},
            {"code": "688169", "name": "石头科技", "type": "弹性", "logic": "服务机器人"},
            {"code": "002611", "name": "东方精工", "type": "弹性", "logic": "智能包装设备"}
        ],
        "消费电子": [
            {"code": "002241", "name": "歌尔股份", "type": "龙头", "logic": "VR/AR设备龙头"},
            {"code": "002475", "name": "立讯精密", "type": "龙头", "logic": "苹果产业链龙头"},
            {"code": "603160", "name": "汇顶科技", "type": "弹性", "logic": "指纹识别芯片"}
        ],
        "数字经济": [
            {"code": "600588", "name": "用友网络", "type": "龙头", "logic": "企业管理软件龙头"},
            {"code": "002410", "name": "广联达", "type": "龙头", "logic": "建筑信息化龙头"},
            {"code": "300033", "name": "同花顺", "type": "弹性", "logic": "金融信息服务"}
        ],
        "通信": [
            {"code": "000063", "name": "中兴通讯", "type": "龙头", "logic": "5G设备龙头"},
            {"code": "300308", "name": "中际旭创", "type": "龙头", "logic": "光模块龙头"},
            {"code": "002281", "name": "光迅科技", "type": "弹性", "logic": "光器件"}
        ],
        "传媒": [
            {"code": "300059", "name": "东方财富", "type": "龙头", "logic": "互联网券商龙头"},
            {"code": "603444", "name": "吉比特", "type": "弹性", "logic": "游戏研发"},
            {"code": "300144", "name": "宋城演艺", "type": "弹性", "logic": "旅游演艺"}
        ],
        "脑机接口": [
            {"code": "300367", "name": "东方网力", "type": "弹性", "logic": "脑机接口概念"},
            {"code": "002421", "name": "达实智能", "type": "弹性", "logic": "智能医疗"}
        ]
    }

    def __init__(self, concept_crawler=None, market_crawler=None):
        """
        初始化推荐器

        Args:
            concept_crawler: 概念股爬虫实例
            market_crawler: 市场数据爬虫实例
        """
        self.concept_crawler = concept_crawler
        self.market_crawler = market_crawler

    def recommend(self, concepts: List[str], max_stocks: int = 3) -> List[Dict[str, Any]]:
        """
        根据概念推荐股票

        Args:
            concepts: 概念列表
            max_stocks: 每个概念最多推荐股票数

        Returns:
            推荐股票列表
        """
        recommendations = []
        seen_codes = set()

        for concept in concepts:
            stocks = self._get_concept_stocks(concept)
            for stock in stocks[:max_stocks]:
                if stock['code'] not in seen_codes:
                    seen_codes.add(stock['code'])
                    stock['concept'] = concept
                    recommendations.append(stock)

        return recommendations

    def _get_concept_stocks(self, concept: str) -> List[Dict[str, Any]]:
        """获取概念对应的股票"""
        # 从配置中获取
        if concept in self.CONCEPT_LEADERS:
            return self.CONCEPT_LEADERS[concept].copy()

        # 尝试从概念爬虫获取实时数据
        if self.concept_crawler:
            try:
                concept_data = self.concept_crawler.get_concept_by_name(concept)
                if concept_data:
                    lead_stock = concept_data.get('lead_stock', {})
                    if lead_stock.get('name'):
                        return [{
                            'code': lead_stock.get('code', ''),
                            'name': lead_stock.get('name', ''),
                            'type': '龙头',
                            'logic': f'{concept}概念领涨股'
                        }]
            except Exception as e:
                print(f"[StockRecommender] 获取概念数据失败: {e}")

        # 模糊匹配
        for key, stocks in self.CONCEPT_LEADERS.items():
            if concept in key or key in concept:
                return stocks.copy()

        return []

    def recommend_with_realtime(self, concepts: List[str], max_stocks: int = 3) -> List[Dict[str, Any]]:
        """
        结合实时数据推荐股票

        Args:
            concepts: 概念列表
            max_stocks: 最大推荐数

        Returns:
            推荐股票列表（含实时行情）
        """
        base_recommendations = self.recommend(concepts, max_stocks)

        # 如果有市场数据爬虫，补充实时行情
        if self.market_crawler:
            for stock in base_recommendations:
                # 这里可以补充实时价格、涨跌幅等信息
                pass

        return base_recommendations

    def get_stock_logic_strength(self, news: Dict[str, Any], stock: Dict[str, Any]) -> str:
        """
        评估股票与新闻的关联强度

        Args:
            news: 新闻数据
            stock: 股票数据

        Returns:
            关联强度评级：⭐⭐⭐ / ⭐⭐ / ⭐
        """
        title = news.get('title', '').lower()
        logic = stock.get('logic', '').lower()
        stock_name = stock.get('name', '').lower()

        # 强关联：股票名称直接出现在标题中
        if stock_name in title:
            return "⭐⭐⭐"

        # 中等关联：逻辑关键词出现在标题中
        logic_keywords = logic.split('，')[0] if '，' in logic else logic
        if logic_keywords and logic_keywords[:4] in title:
            return "⭐⭐⭐"

        # 弱关联：概念相关
        return "⭐⭐"

    def rank_by_relevance(self, stocks: List[Dict[str, Any]], news: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        按关联度排序股票

        Args:
            stocks: 股票列表
            news: 相关新闻

        Returns:
            排序后的股票列表
        """
        for stock in stocks:
            stock['logic_strength'] = self.get_stock_logic_strength(news, stock)

        # 按强度排序
        strength_order = {"⭐⭐⭐": 3, "⭐⭐": 2, "⭐": 1}
        stocks.sort(key=lambda x: strength_order.get(x.get('logic_strength', '⭐'), 0), reverse=True)

        return stocks

    def get_recommendation_summary(self, recommendations: List[Dict[str, Any]]) -> str:
        """
        生成推荐摘要

        Args:
            recommendations: 推荐列表

        Returns:
            摘要文本
        """
        if not recommendations:
            return "暂无推荐标的"

        leaders = [s for s in recommendations if s.get('type') == '龙头']
        flexibles = [s for s in recommendations if s.get('type') == '弹性']

        summary_parts = []

        if leaders:
            summary_parts.append(f"龙头股: {', '.join([s['name'] for s in leaders[:3]])}")

        if flexibles:
            summary_parts.append(f"弹性股: {', '.join([s['name'] for s in flexibles[:3]])}")

        return ' | '.join(summary_parts)


# 便捷函数
def recommend_stocks(concepts: List[str], max_stocks: int = 3) -> List[Dict[str, Any]]:
    """根据概念推荐股票"""
    recommender = StockRecommender()
    return recommender.recommend(concepts, max_stocks)