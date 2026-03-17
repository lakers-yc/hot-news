"""
爬虫基类模块
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from curl_cffi import requests as curl_requests
    USE_CURL = True
except ImportError:
    import requests as curl_requests
    USE_CURL = False


class BaseCrawler(ABC):
    """爬虫基类"""

    name: str = "base"
    source_type: str = "general"
    enabled: bool = True

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self._last_fetch_time: Optional[datetime] = None
        self._cached_data: List[Dict[str, Any]] = []
        self._cache_time: Optional[datetime] = None
        self._cache_ttl: int = 300

    def _get_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }

    def fetch(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Optional[Any]:
        """发起HTTP请求"""
        try:
            req_headers = self._get_headers()
            if headers:
                req_headers.update(headers)

            if USE_CURL:
                response = curl_requests.get(
                    url, params=params, headers=req_headers,
                    timeout=self.timeout, impersonate='chrome120'
                )
            else:
                response = curl_requests.get(
                    url, params=params, headers=req_headers,
                    timeout=self.timeout, verify=False
                )

            response.raise_for_status()
            self._last_fetch_time = datetime.now()
            return response
        except Exception as e:
            print(f"[{self.name}] 请求失败: {e}")
            return None

    def post(self, url: str, data: Optional[Dict] = None, json: Optional[Dict] = None, headers: Optional[Dict] = None) -> Optional[Any]:
        """发起POST请求"""
        try:
            req_headers = self._get_headers()
            if headers:
                req_headers.update(headers)

            if USE_CURL:
                response = curl_requests.post(
                    url, data=data, json=json, headers=req_headers,
                    timeout=self.timeout, impersonate='chrome120'
                )
            else:
                response = curl_requests.post(
                    url, data=data, json=json, headers=req_headers,
                    timeout=self.timeout, verify=False
                )

            response.raise_for_status()
            self._last_fetch_time = datetime.now()
            return response
        except Exception as e:
            print(f"[{self.name}] POST请求失败: {e}")
            return None

    @abstractmethod
    def fetch_data(self) -> List[Dict[str, Any]]:
        """获取数据（子类实现）"""
        pass

    def _deduplicate(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重：根据标题去重"""
        seen = set()
        result = []
        for item in items:
            title = item.get('title', '')
            if title and title not in seen:
                seen.add(title)
                result.append(item)
        return result

    def get_data(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """获取数据（带缓存和去重）"""
        now = datetime.now()

        if use_cache and self._cache_time:
            elapsed = (now - self._cache_time).total_seconds()
            if elapsed < self._cache_ttl and self._cached_data:
                return self._cached_data

        try:
            data = self.fetch_data()
            if data:
                # 去重
                data = self._deduplicate(data)
                self._cached_data = data
                self._cache_time = now
            return data if data else []
        except Exception as e:
            print(f"[{self.name}] 获取数据失败: {e}")
            return []

    def get_source_info(self) -> Dict[str, str]:
        return {
            'name': self.name,
            'type': self.source_type,
            'enabled': self.enabled,
            'last_fetch': self._last_fetch_time.isoformat() if self._last_fetch_time else None
        }