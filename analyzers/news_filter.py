"""
重要新闻筛选模块 - 筛选政策类、突破性事件等重要新闻
"""
from typing import List, Dict, Any, Tuple
import re
import json
import os


class NewsFilter:
    """重要新闻筛选器"""

    # 重要新闻关键词
    IMPORTANT_KEYWORDS = [
        # 政策类
        "印发", "发布", "批准", "批复", "通知", "方案", "规划",
        "国务院", "发改委", "工信部", "财政部", "央行", "证监会",
        "政策", "法规", "条例", "意见", "办法", "规定",
        # 突破性事件
        "首次", "突破", "全球首个", "国内首创", "正式上线",
        "世界第一", "亚洲首个", "国内首个", "业内首",
        # 重大事件
        "并购", "重组", "上市", "首发", "签约", "合作",
        "落地", "投产", "开工", "交付", "验收",
        # 市场影响
        "涨价", "缺货", "断供", "制裁", "禁令",
        "放量", "爆发", "激增", "暴跌", "暴涨",
        # 技术突破
        "研发成功", "技术突破", "量产", "专利", "认证",
        # 业绩相关
        "业绩预增", "扭亏", "盈利", "翻倍", "超预期"
    ]

    # 高权重关键词（涉及重大政策或事件）
    HIGH_WEIGHT_KEYWORDS = [
        "国务院", "发改委", "工信部", "央行", "证监会",
        "首次", "突破", "全球首个", "国内首创",
        "并购", "重组", "暴涨", "暴跌"
    ]

    # 过滤关键词（排除噪音）
    FILTER_KEYWORDS = [
        "热恋", "出轨", "离婚", "结婚", "生子", "怀孕",
        "综艺", "娱乐", "明星", "网红", "八卦",
        "直播带货", "主播", "粉丝"
    ]

    # 行业权重配置
    INDUSTRY_WEIGHTS = {
        "科技": 1.5,
        "芯片": 1.5,
        "半导体": 1.5,
        "人工智能": 1.5,
        "AI": 1.5,
        "新能源": 1.3,
        "光伏": 1.3,
        "锂电": 1.3,
        "医药": 1.2,
        "军工": 1.2,
        "金融": 1.0,
        "消费": 1.0
    }

    def __init__(self, keyword_mapping_path: str = None):
        """初始化筛选器"""
        self.keyword_mapping = {}
        if keyword_mapping_path:
            self._load_keyword_mapping(keyword_mapping_path)

    def _load_keyword_mapping(self, path: str):
        """加载关键词映射"""
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    self.keyword_mapping = json.load(f)
        except Exception as e:
            print(f"[NewsFilter] 加载关键词映射失败: {e}")

    def is_important(self, title: str, content: str = "") -> Tuple[bool, float, List[str]]:
        """
        判断新闻是否重要

        Args:
            title: 新闻标题
            content: 新闻内容（可选）

        Returns:
            (是否重要, 重要性分数, 匹配的关键词列表)
        """
        text = f"{title} {content}".lower()
        matched_keywords = []
        score = 0.0

        # 检查过滤关键词
        for filter_word in self.FILTER_KEYWORDS:
            if filter_word in text:
                return False, 0, []

        # 检查重要关键词
        for keyword in self.IMPORTANT_KEYWORDS:
            if keyword in text:
                matched_keywords.append(keyword)
                # 高权重关键词加分
                if keyword in self.HIGH_WEIGHT_KEYWORDS:
                    score += 2.0
                else:
                    score += 1.0

        # 行业权重加成
        for industry, weight in self.INDUSTRY_WEIGHTS.items():
            if industry in text:
                score *= weight
                break

        # 标题长度惩罚（太长可能是营销号）
        if len(title) > 80:
            score *= 0.7

        # 来源权威性加成（通过关键词判断）
        authoritative_sources = ["新华社", "人民日报", "央视", "中国证券报", "上海证券报"]
        for source in authoritative_sources:
            if source in text:
                score *= 1.2
                break

        is_important = score >= 1.0

        return is_important, round(score, 2), matched_keywords

    def filter_news(self, news_list: List[Dict[str, Any]], min_score: float = 1.0) -> List[Dict[str, Any]]:
        """
        筛选重要新闻列表

        Args:
            news_list: 新闻列表
            min_score: 最低分数阈值

        Returns:
            筛选后的新闻列表（按分数降序）
        """
        filtered = []

        for news in news_list:
            title = news.get('title', '')
            source = news.get('source', '')
            time_str = news.get('time', '')

            is_important, score, keywords = self.is_important(title)

            if is_important and score >= min_score:
                filtered.append({
                    **news,
                    'importance_score': score,
                    'matched_keywords': keywords
                })

        # 按分数降序排序
        filtered.sort(key=lambda x: x.get('importance_score', 0), reverse=True)

        return filtered

    def get_news_category(self, title: str, content: str = "") -> str:
        """
        获取新闻类别

        Returns:
            新闻类别：policy(政策), breakthrough(突破), event(事件), market(市场), other(其他)
        """
        text = f"{title} {content}"

        # 政策类
        policy_keywords = ["印发", "发布", "批准", "批复", "通知", "方案", "规划",
                         "国务院", "发改委", "工信部", "政策", "法规"]
        for kw in policy_keywords:
            if kw in text:
                return "policy"

        # 突破类
        breakthrough_keywords = ["首次", "突破", "全球首个", "国内首创", "研发成功", "技术突破"]
        for kw in breakthrough_keywords:
            if kw in text:
                return "breakthrough"

        # 事件类
        event_keywords = ["并购", "重组", "上市", "签约", "落地", "投产"]
        for kw in event_keywords:
            if kw in text:
                return "event"

        # 市场类
        market_keywords = ["涨价", "缺货", "暴涨", "暴跌", "放量", "爆发"]
        for kw in market_keywords:
            if kw in text:
                return "market"

        return "other"

    def deduplicate_news(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """新闻去重（基于标题相似度）"""
        seen_titles = []
        result = []

        for news in news_list:
            title = news.get('title', '')

            # 简单去重：检查是否与已有标题高度相似
            is_duplicate = False
            for seen in seen_titles:
                if self._similarity(title, seen) > 0.8:
                    is_duplicate = True
                    break

            if not is_duplicate:
                seen_titles.append(title)
                result.append(news)

        return result

    def _similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（简单实现）"""
        if not text1 or not text2:
            return 0

        # 取较短文本长度
        min_len = min(len(text1), len(text2))
        if min_len == 0:
            return 0

        # 计算公共字符数
        common = 0
        for i, char in enumerate(text1):
            if i < len(text2) and char == text2[i]:
                common += 1

        return common / min_len


# 便捷函数
def is_important_news(title: str, content: str = "") -> Tuple[bool, float, List[str]]:
    """判断新闻是否重要"""
    filter_obj = NewsFilter()
    return filter_obj.is_important(title, content)


def filter_important_news(news_list: List[Dict[str, Any]], min_score: float = 1.0) -> List[Dict[str, Any]]:
    """筛选重要新闻"""
    filter_obj = NewsFilter()
    return filter_obj.filter_news(news_list, min_score)