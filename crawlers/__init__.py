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
]