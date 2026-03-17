"""
概念匹配模块 - 根据新闻标题匹配相关概念
"""
from typing import List, Dict, Any, Tuple, Set
import json
import os
import re


class ConceptMatcher:
    """概念匹配器"""

    def __init__(self, keyword_mapping_path: str = None):
        """
        初始化匹配器

        Args:
            keyword_mapping_path: 关键词映射文件路径
        """
        self.keyword_mapping = {}
        self._load_keyword_mapping(keyword_mapping_path)

    def _load_keyword_mapping(self, path: str = None):
        """加载关键词映射"""
        if path is None:
            # 默认路径
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(base_dir, 'data', 'keyword_mapping.json')

        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    self.keyword_mapping = json.load(f)
                print(f"[ConceptMatcher] 加载关键词映射: {len(self.keyword_mapping)} 个概念")
            else:
                print(f"[ConceptMatcher] 关键词映射文件不存在: {path}")
                self._init_default_mapping()
        except Exception as e:
            print(f"[ConceptMatcher] 加载关键词映射失败: {e}")
            self._init_default_mapping()

    def _init_default_mapping(self):
        """初始化默认映射"""
        self.keyword_mapping = {
            "人工智能": ["AI", "GPT", "大模型", "人工智能", "机器学习"],
            "半导体": ["芯片", "半导体", "光刻机", "晶圆"],
            "新能源": ["光伏", "风电", "储能", "锂电池"],
            "医药": ["创新药", "疫苗", "CRO", "CXO"],
            "军工": ["军工", "国防", "装备"]
        }

    def match(self, text: str) -> List[Tuple[str, float, List[str]]]:
        """
        匹配文本中的概念

        Args:
            text: 新闻标题或内容

        Returns:
            [(概念名称, 匹配置信度, 匹配的关键词列表), ...]
        """
        if not text:
            return []

        text_lower = text.lower()
        matches = []

        for concept, keywords in self.keyword_mapping.items():
            matched_keywords = []
            match_count = 0

            for keyword in keywords:
                # 关键词匹配（不区分大小写）
                if keyword.lower() in text_lower:
                    matched_keywords.append(keyword)
                    match_count += 1

            if matched_keywords:
                # 计算置信度
                confidence = min(1.0, match_count * 0.5)  # 每匹配一个关键词增加0.5置信度

                # 多个关键词匹配时提高置信度
                if len(matched_keywords) > 1:
                    confidence = min(1.0, confidence + 0.2)

                matches.append((concept, confidence, matched_keywords))

        # 按置信度降序排序
        matches.sort(key=lambda x: x[1], reverse=True)

        return matches

    def match_with_priority(self, text: str, priority_concepts: List[str] = None) -> List[Tuple[str, float, List[str]]]:
        """
        带优先级的概念匹配

        Args:
            text: 文本
            priority_concepts: 优先概念列表（这些概念的匹配权重更高）

        Returns:
            匹配结果列表
        """
        matches = self.match(text)

        if priority_concepts:
            # 对优先概念提高置信度
            adjusted_matches = []
            for concept, confidence, keywords in matches:
                if concept in priority_concepts:
                    confidence = min(1.0, confidence + 0.3)
                adjusted_matches.append((concept, confidence, keywords))
            matches = adjusted_matches

        return matches

    def get_related_concepts(self, concept: str) -> List[str]:
        """
        获取相关概念

        Args:
            concept: 概念名称

        Returns:
            相关概念列表
        """
        # 定义概念关联关系
        concept_relations = {
            "人工智能": ["算力", "半导体", "通信"],
            "算力": ["半导体", "人工智能", "通信"],
            "半导体": ["消费电子", "新能源汽车", "人工智能"],
            "新能源汽车": ["锂电池", "半导体", "汽车"],
            "新能源": ["锂电池", "光伏", "储能"],
            "医药": ["医疗", "医美"],
            "军工": ["通信", "半导体"]
        }

        return concept_relations.get(concept, [])

    def batch_match(self, texts: List[str]) -> Dict[str, List[Tuple[str, float, List[str]]]]:
        """
        批量匹配

        Args:
            texts: 文本列表

        Returns:
            {文本: 匹配结果}
        """
        results = {}
        for text in texts:
            results[text] = self.match(text)
        return results

    def get_concept_keywords(self, concept: str) -> List[str]:
        """获取概念的关键词列表"""
        return self.keyword_mapping.get(concept, [])

    def get_all_concepts(self) -> List[str]:
        """获取所有概念列表"""
        return list(self.keyword_mapping.keys())

    def extract_stock_codes(self, text: str) -> List[str]:
        """
        从文本中提取股票代码

        Args:
            text: 文本

        Returns:
            股票代码列表
        """
        # 匹配6位数字股票代码
        codes = re.findall(r'\b(\d{6})\b', text)

        # 过滤有效的股票代码
        valid_codes = []
        for code in codes:
            # A股代码规则
            if code.startswith(('00', '30', '60', '68')):
                valid_codes.append(code)

        return valid_codes

    def calculate_relevance_score(self, text: str, concept: str) -> float:
        """
        计算文本与概念的关联分数

        Args:
            text: 文本
            concept: 概念名称

        Returns:
            关联分数 (0-1)
        """
        matches = self.match(text)
        for matched_concept, confidence, _ in matches:
            if matched_concept == concept:
                return confidence
        return 0.0


# 便捷函数
def match_concepts(text: str) -> List[Tuple[str, float, List[str]]]:
    """匹配文本中的概念"""
    matcher = ConceptMatcher()
    return matcher.match(text)


def get_concept_keywords(concept: str) -> List[str]:
    """获取概念关键词"""
    matcher = ConceptMatcher()
    return matcher.get_concept_keywords(concept)