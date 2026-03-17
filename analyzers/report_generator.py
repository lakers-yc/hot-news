"""
报告生成模块 - 生成专业的股票推荐报告
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import json


class ReportGenerator:
    """报告生成器"""

    def __init__(self, concept_crawler=None, market_crawler=None):
        """
        初始化报告生成器

        Args:
            concept_crawler: 概念股爬虫实例
            market_crawler: 市场数据爬虫实例
        """
        from .news_filter import NewsFilter
        from .concept_matcher import ConceptMatcher
        from .stock_recommender import StockRecommender

        self.news_filter = NewsFilter()
        self.concept_matcher = ConceptMatcher()
        self.stock_recommender = StockRecommender(concept_crawler, market_crawler)
        self.concept_crawler = concept_crawler
        self.market_crawler = market_crawler

    def generate(self, news_list: List[Dict[str, Any]], date: str = None) -> Dict[str, Any]:
        """
        生成报告

        Args:
            news_list: 新闻列表
            date: 日期字符串

        Returns:
            报告数据
        """
        # 获取当前时间
        now = datetime.now()
        date_str = date or now.strftime('%Y-%m-%d')
        update_time = now.strftime('%H:%M')

        # 筛选重要新闻
        important_news = self.news_filter.filter_news(news_list, min_score=1.0)

        # 去重
        important_news = self.news_filter.deduplicate_news(important_news)

        # 获取市场情绪
        market_sentiment = self._get_market_sentiment()

        # 分析每条重要新闻
        analysis_results = []
        for news in important_news[:15]:  # 最多分析15条
            analysis = self._analyze_news(news)
            if analysis:
                analysis_results.append(analysis)

        # 获取异动股票
        abnormal_stocks = self._get_abnormal_stocks()

        # 生成策略提示
        strategy = self._generate_strategy(analysis_results, market_sentiment)

        report = {
            'date': date_str,
            'updateTime': update_time,
            'marketSentiment': market_sentiment.get('summary', '市场情绪中性'),
            'analysis': analysis_results,
            'abnormalStocks': abnormal_stocks,
            'strategy': strategy,
            'raw_markdown': ''  # 将在后面生成
        }

        # 生成Markdown报告
        report['raw_markdown'] = self._generate_markdown(report)

        return report

    def _analyze_news(self, news: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """分析单条新闻"""
        title = news.get('title', '')
        source = news.get('source', '')
        time_str = news.get('time', '')

        # 匹配概念
        concept_matches = self.concept_matcher.match(title)

        if not concept_matches:
            return None

        # 取前2个最相关的概念
        top_concepts = [m[0] for m in concept_matches[:2]]

        # 推荐股票
        stocks = self.stock_recommender.recommend(top_concepts, max_stocks=3)

        # 排序股票
        stocks = self.stock_recommender.rank_by_relevance(stocks, news)

        # 计算逻辑强度
        logic_strength = self._calculate_logic_strength(news, concept_matches)

        return {
            'news': {
                'title': self._clean_title(title),
                'source': source,
                'time': time_str,
                'original_title': title
            },
            'concepts': top_concepts,
            'logicStrength': logic_strength,
            'stocks': stocks[:3]  # 最多3只股票
        }

    def _clean_title(self, title: str) -> str:
        """清理标题"""
        # 移除过长的时间信息
        import re
        title = re.sub(r'\d+小时前$', '', title)
        title = re.sub(r'\d+天前$', '', title)
        title = re.sub(r'\d+分钟前$', '', title)

        # 限制长度
        if len(title) > 60:
            title = title[:60] + '...'

        return title.strip()

    def _calculate_logic_strength(self, news: Dict[str, Any], concept_matches: List) -> str:
        """计算逻辑强度"""
        score = news.get('importance_score', 1)
        confidence = concept_matches[0][1] if concept_matches else 0

        # 综合评分
        combined = score * 0.5 + confidence * 0.5

        if combined >= 1.5:
            return "⭐⭐⭐"
        elif combined >= 1.0:
            return "⭐⭐"
        else:
            return "⭐"

    def _get_market_sentiment(self) -> Dict[str, Any]:
        """获取市场情绪"""
        if self.market_crawler:
            try:
                return self.market_crawler.get_market_sentiment()
            except:
                pass

        return {
            'score': 0,
            'summary': '市场情绪中性，建议观望为主',
            'factors': []
        }

    def _get_abnormal_stocks(self) -> List[Dict[str, Any]]:
        """获取异动股票"""
        if self.market_crawler:
            try:
                abnormals = self.market_crawler.get_abnormal_stocks()
                return abnormals[:10]  # 最多10条
            except:
                pass
        return []

    def _generate_strategy(self, analysis_results: List, market_sentiment: Dict) -> Dict[str, str]:
        """生成策略提示"""
        risk_hints = []
        suggestions = []

        # 根据市场情绪生成建议
        sentiment_score = market_sentiment.get('score', 0)
        if sentiment_score > 20:
            suggestions.append("市场情绪偏暖，可适度积极参与")
        elif sentiment_score < -20:
            risk_hints.append("市场情绪偏弱，注意控制仓位")

        # 根据分析结果生成提示
        strong_logic_count = sum(1 for a in analysis_results if a.get('logicStrength') == "⭐⭐⭐")
        if strong_logic_count > 3:
            risk_hints.append("热点较多，注意资金分流风险")
        elif strong_logic_count == 0:
            suggestions.append("今日无明显强逻辑热点，建议观望")

        # 检查是否有多条同概念新闻
        concept_count = {}
        for analysis in analysis_results:
            for concept in analysis.get('concepts', []):
                concept_count[concept] = concept_count.get(concept, 0) + 1

        hot_concepts = [c for c, count in concept_count.items() if count >= 2]
        if hot_concepts:
            suggestions.append(f"今日热点聚焦: {', '.join(hot_concepts[:3])}")

        return {
            'risk': risk_hints[0] if risk_hints else "高位股分歧风险，注意追高风险",
            'suggestion': suggestions[0] if suggestions else "关注低位补涨标的，控制仓位"
        }

    def _generate_markdown(self, report: Dict[str, Any]) -> str:
        """生成Markdown格式报告"""
        lines = []

        # 标题
        lines.append(f"**日期：** {report['date']} **数据更新时间：** {report['updateTime']} (北京时间)")
        lines.append(f"**市场情绪预判：** {report['marketSentiment']}")
        lines.append("")

        # 分析表格
        lines.append("| 消息/政策 (来源+时间) | 炒作方向/主题 | 逻辑强度 | 推荐关注个股 |")
        lines.append("|----------------------|--------------|----------|-------------|")

        for analysis in report['analysis']:
            news = analysis['news']
            concepts = '/'.join(analysis['concepts'][:2])
            strength = analysis['logicStrength']

            # 股票推荐
            stock_lines = []
            for i, stock in enumerate(analysis['stocks'][:3], 1):
                stock_lines.append(f"{i}. {stock['name']}({stock['code']}) - {stock['logic']}")

            stocks_text = '<br>'.join(stock_lines) if stock_lines else '暂无推荐'

            lines.append(f"| {news['title']}<br>({news['source']}) | {concepts} | {strength} | {stocks_text} |")

        lines.append("")

        # 异动股票
        if report['abnormalStocks']:
            lines.append("**近期异动股票（供参考）**")
            lines.append("| 异动股票 | 异动提示 |")
            lines.append("|----------|----------|")

            for stock in report['abnormalStocks'][:8]:
                hint = f"{stock.get('type', '')} {stock.get('change_pct', 0)}%"
                lines.append(f"| {stock['name']}({stock['code']}) | {hint} |")

            lines.append("")

        # 策略提示
        lines.append("**💡 策略师特别提示：**")
        lines.append(f"- **风险提示**：{report['strategy']['risk']}")
        lines.append(f"- **操作建议**：{report['strategy']['suggestion']}")
        lines.append("")
        lines.append("---")
        lines.append("*风险提示：以上内容仅供参考，不构成投资建议。股市有风险，入市需谨慎。*")

        return '\n'.join(lines)

    def save_report(self, report: Dict[str, Any], output_dir: str = None) -> str:
        """
        保存报告到文件

        Args:
            report: 报告数据
            output_dir: 输出目录

        Returns:
            文件路径
        """
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')

        os.makedirs(output_dir, exist_ok=True)

        # 生成文件名
        date_str = report['date']
        filename = f"report_{date_str.replace('-', '')}.md"
        filepath = os.path.join(output_dir, filename)

        # 保存Markdown文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report['raw_markdown'])

        # 同时保存JSON格式
        json_filepath = filepath.replace('.md', '.json')
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return filepath


# 便捷函数
def generate_report(news_list: List[Dict[str, Any]], date: str = None) -> Dict[str, Any]:
    """生成报告"""
    generator = ReportGenerator()
    return generator.generate(news_list, date)