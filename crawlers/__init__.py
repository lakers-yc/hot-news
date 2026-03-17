"""
热点追踪爬虫模块
"""
from .base import BaseCrawler
from .jin10 import Jin10Crawler
from .cls import ClsCrawler
from .eastmoney import EastmoneyCrawler
from .xueqiu import XueqiuCrawler
from .stcn import StcnCrawler
from .wallstreetcn import WallstreetcnCrawler
from .sse import SseCrawler
from .szse import SzseCrawler
from .gov import GovCrawler
from .xinhua import XinhuaCrawler
from .yicai import YicaiCrawler
from .weibo import WeiboCrawler
from .toutiao import ToutiaoCrawler
from .ths import ThsCrawler
from .kr36 import Kr36Crawler
from .baidu import BaiduCrawler
from .concept_crawler import ConceptCrawler
from .market_crawler import MarketCrawler

# 热榜爬虫
from .eastmoney_hot import EastmoneyHotCrawler
from .ths_hot import ThsHotCrawler
from .cls_hot import ClsHotCrawler
from .yicai_hot import YicaiHotCrawler
from .stcn_hot import StcnHotCrawler
from .wallstreetcn_hot import WallstreetcnHotCrawler

__all__ = [
    'BaseCrawler',
    'Jin10Crawler',
    'ClsCrawler',
    'EastmoneyCrawler',
    'XueqiuCrawler',
    'StcnCrawler',
    'WallstreetcnCrawler',
    'SseCrawler',
    'SzseCrawler',
    'GovCrawler',
    'XinhuaCrawler',
    'YicaiCrawler',
    'WeiboCrawler',
    'ToutiaoCrawler',
    'ThsCrawler',
    'Kr36Crawler',
    'BaiduCrawler',
    'ConceptCrawler',
    'MarketCrawler',
    # 热榜爬虫
    'EastmoneyHotCrawler',
    'ThsHotCrawler',
    'ClsHotCrawler',
    'YicaiHotCrawler',
    'StcnHotCrawler',
    'WallstreetcnHotCrawler',
]