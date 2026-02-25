"""
数据爬虫系统
用于自动抓取保险相关数据：条款、监管政策、行业新闻等
"""

import asyncio
import aiohttp
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import hashlib
import json

import logging
from bs4 import BeautifulSoup

# 配置日志
logger = logging.getLogger(__name__)


@dataclass
class CrawlResult:
    """爬取结果"""
    url: str
    title: str
    content: str
    source: str  # 来源网站
    category: str  # 数据类别：条款/政策/新闻/案例
    published_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    crawled_at: datetime = field(default_factory=datetime.now)
    hash_id: str = ""  # 内容哈希，用于去重

    def __post_init__(self):
        if not self.hash_id:
            content_hash = hashlib.md5(
                f"{self.title}:{self.content[:500]}".encode()
            ).hexdigest()
            self.hash_id = content_hash


@dataclass
class CrawlTask:
    """爬取任务"""
    url: str
    source: str
    category: str
    priority: int = 0  # 优先级，数字越小优先级越高
    retry_count: int = 0
    max_retries: int = 3


class BaseCrawler(ABC):
    """
    爬虫基类
    所有具体爬虫应继承此类
    """

    def __init__(
        self,
        source_name: str,
        base_url: str,
        delay: float = 1.0,  # 请求间隔（秒）
        timeout: int = 30,
        headers: Optional[Dict] = None
    ):
        self.source_name = source_name
        self.base_url = base_url
        self.delay = delay
        self.timeout = timeout
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch(self, url: str) -> Optional[str]:
        """获取页面内容"""
        if not self.session:
            raise RuntimeError("Crawler not initialized. Use async with context.")

        try:
            await asyncio.sleep(self.delay)  # 礼貌爬取间隔
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"Failed to fetch {url}: status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    @abstractmethod
    async def discover_urls(self) -> List[str]:
        """发现待爬取的URL列表"""
        pass

    @abstractmethod
    async def parse(self, url: str, html: str) -> Optional[CrawlResult]:
        """解析页面内容"""
        pass

    async def crawl(self) -> List[CrawlResult]:
        """执行爬取"""
        results = []
        urls = await self.discover_urls()
        logger.info(f"[{self.source_name}] Discovered {len(urls)} URLs")

        for url in urls:
            html = await self.fetch(url)
            if html:
                result = await self.parse(url, html)
                if result:
                    results.append(result)
                    logger.info(f"[{self.source_name}] Crawled: {result.title[:50]}...")

        return results


class CBIRCrawler(BaseCrawler):
    """
    银保监会（国家金融监督管理总局）政策爬虫
    爬取监管政策、通知公告等
    """

    def __init__(self):
        super().__init__(
            source_name="国家金融监督管理总局",
            base_url="https://www.nfra.gov.cn",
            delay=2.0
        )
        self.list_url = "https://www.nfra.gov.cn/cn/view/pages/governmentDetail.html?docId={}"

    async def discover_urls(self) -> List[str]:
        """
        发现政策文件URL
        实际实现需要调用API或解析列表页
        """
        # 这里使用示例URL，实际应从列表页/API获取
        # 银保监会的政策通常有规律ID，可以按日期范围构造
        urls = []

        # 示例：爬取最近的几条政策
        # 实际实现应该解析列表页获取真实ID
        sample_ids = [
            "10865422",  # 示例ID
            "10865421",
            "10865420",
        ]

        for doc_id in sample_ids:
            urls.append(self.list_url.format(doc_id))

        return urls

    async def parse(self, url: str, html: str) -> Optional[CrawlResult]:
        """解析政策详情页"""
        soup = BeautifulSoup(html, 'html.parser')

        # 提取标题
        title_tag = soup.find('h1') or soup.find('title')
        if not title_tag:
            return None
        title = title_tag.get_text(strip=True)

        # 提取正文
        content_div = soup.find('div', class_='content') or soup.find('article')
        if not content_div:
            return None

        # 清理内容
        for script in content_div.find_all(['script', 'style']):
            script.decompose()
        content = content_div.get_text(separator='\n', strip=True)

        # 提取发布日期
        published_at = None
        date_patterns = [
            soup.find('span', class_='date'),
            soup.find('meta', property='article:published_time'),
        ]
        for pattern in date_patterns:
            if pattern:
                try:
                    date_str = pattern.get('content') or pattern.get_text()
                    published_at = datetime.strptime(date_str[:10], "%Y-%m-%d")
                    break
                except:
                    continue

        return CrawlResult(
            url=url,
            title=title,
            content=content,
            source=self.source_name,
            category="监管政策",
            published_at=published_at,
            metadata={
                "doc_type": "监管文件",
                "issuer": "国家金融监督管理总局"
            }
        )


class InsuranceCompanyCrawler(BaseCrawler):
    """
    保险公司官网条款爬虫
    爬取公开的产品条款
    """

    def __init__(self, company_name: str, base_url: str, product_list_path: str):
        super().__init__(
            source_name=company_name,
            base_url=base_url,
            delay=1.5
        )
        self.product_list_path = product_list_path

    async def discover_urls(self) -> List[str]:
        """发现产品条款URL"""
        list_url = urljoin(self.base_url, self.product_list_path)
        html = await self.fetch(list_url)

        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        urls = []

        # 查找条款链接（根据实际网站结构调整选择器）
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if 'clause' in href.lower() or 'terms' in href.lower() or 'product' in href.lower():
                full_url = urljoin(self.base_url, href)
                urls.append(full_url)

        return urls[:20]  # 限制数量避免过度爬取

    async def parse(self, url: str, html: str) -> Optional[CrawlResult]:
        """解析条款详情页"""
        soup = BeautifulSoup(html, 'html.parser')

        # 提取产品名称
        title_tag = soup.find('h1') or soup.find('h2')
        title = title_tag.get_text(strip=True) if title_tag else "未知产品"

        # 提取条款内容
        content_div = (
            soup.find('div', class_='clause-content') or
            soup.find('div', class_='product-detail') or
            soup.find('article') or
            soup.find('main')
        )

        if not content_div:
            return None

        content = content_div.get_text(separator='\n', strip=True)

        # 提取产品类型
        product_type = "未知"
        if '重疾' in title or '疾病' in title:
            product_type = "重疾险"
        elif '意外' in title:
            product_type = "意外险"
        elif '医疗' in title:
            product_type = "医疗险"
        elif '寿险' in title or '人寿' in title:
            product_type = "寿险"
        elif '年金' in title:
            product_type = "年金险"

        return CrawlResult(
            url=url,
            title=title,
            content=content,
            source=self.source_name,
            category="产品条款",
            metadata={
                "product_type": product_type,
                "company": self.source_name
            }
        )


class CourtCaseCrawler(BaseCrawler):
    """
    保险纠纷案例爬虫
    从裁判文书网等爬取保险相关案例
    """

    def __init__(self):
        super().__init__(
            source_name="裁判文书网",
            base_url="https://wenshu.court.gov.cn",
            delay=3.0  # 裁判文书网需要更长的间隔
        )

    async def discover_urls(self) -> List[str]:
        """
        发现保险相关案例URL
        注意：裁判文书网有反爬机制，实际使用可能需要验证码处理
        """
        # 实际实现需要调用搜索API或解析搜索结果
        # 这里返回示例结构
        return []

    async def parse(self, url: str, html: str) -> Optional[CrawlResult]:
        """解析案例详情"""
        soup = BeautifulSoup(html, 'html.parser')

        # 提取案号
        case_number = ""
        case_tag = soup.find('div', class_='case-number')
        if case_tag:
            case_number = case_tag.get_text(strip=True)

        # 提取标题
        title = case_number or "保险纠纷案例"

        # 提取判决内容
        content_div = soup.find('div', class_='judgment-content')
        if not content_div:
            return None

        content = content_div.get_text(separator='\n', strip=True)

        return CrawlResult(
            url=url,
            title=title,
            content=content,
            source=self.source_name,
            category="法律案例",
            metadata={
                "case_number": case_number,
                "case_type": "保险纠纷"
            }
        )


class CrawlerScheduler:
    """
    爬虫调度器
    管理多个爬虫的执行调度
    """

    def __init__(self):
        self.crawlers: List[BaseCrawler] = []
        self.results: List[CrawlResult] = []
        self.crawl_history: List[Dict] = []

    def register_crawler(self, crawler: BaseCrawler):
        """注册爬虫"""
        self.crawlers.append(crawler)
        logger.info(f"Registered crawler: {crawler.source_name}")

    async def run_all(self) -> List[CrawlResult]:
        """运行所有爬虫"""
        all_results = []

        for crawler in self.crawlers:
            try:
                async with crawler:
                    results = await crawler.crawl()
                    all_results.extend(results)

                    self.crawl_history.append({
                        "source": crawler.source_name,
                        "crawled_at": datetime.now().isoformat(),
                        "count": len(results)
                    })

                    logger.info(
                        f"[{crawler.source_name}] Crawled {len(results)} items"
                    )
            except Exception as e:
                logger.error(f"Crawler {crawler.source_name} failed: {e}")

        self.results = all_results
        return all_results

    async def run_specific(self, source_name: str) -> List[CrawlResult]:
        """运行特定爬虫"""
        crawler = next(
            (c for c in self.crawlers if c.source_name == source_name),
            None
        )

        if not crawler:
            raise ValueError(f"Crawler not found: {source_name}")

        async with crawler:
            return await crawler.crawl()

    def get_stats(self) -> Dict:
        """获取爬取统计"""
        return {
            "total_crawlers": len(self.crawlers),
            "total_results": len(self.results),
            "by_source": {
                r.source for r in self.results
            },
            "by_category": {
                r.category for r in self.results
            },
            "history": self.crawl_history
        }


class DataStore:
    """
    数据存储
    将爬取的数据保存到数据库或文件
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or "backend/data/crawled_data.json"
        self.data: List[Dict] = []
        self._load_existing()

    def _load_existing(self):
        """加载已有数据"""
        import os
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except:
                self.data = []

    def save_result(self, result: CrawlResult) -> bool:
        """保存单个结果，自动去重"""
        # 检查是否已存在
        existing_hashes = {d.get('hash_id') for d in self.data}
        if result.hash_id in existing_hashes:
            logger.debug(f"Duplicate content skipped: {result.title[:30]}")
            return False

        # 保存新数据
        data_entry = {
            "hash_id": result.hash_id,
            "url": result.url,
            "title": result.title,
            "content": result.content,
            "source": result.source,
            "category": result.category,
            "published_at": result.published_at.isoformat() if result.published_at else None,
            "crawled_at": result.crawled_at.isoformat(),
            "metadata": result.metadata
        }

        self.data.append(data_entry)
        return True

    def save_results(self, results: List[CrawlResult]) -> int:
        """批量保存结果"""
        saved_count = 0
        for result in results:
            if self.save_result(result):
                saved_count += 1

        return saved_count

    def persist(self):
        """持久化到文件"""
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved {len(self.data)} records to {self.db_path}")

    def query(
        self,
        category: Optional[str] = None,
        source: Optional[str] = None,
        keyword: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """查询数据"""
        results = self.data

        if category:
            results = [r for r in results if r.get('category') == category]

        if source:
            results = [r for r in results if r.get('source') == source]

        if keyword:
            keyword_lower = keyword.lower()
            results = [
                r for r in results
                if keyword_lower in r.get('title', '').lower() or
                keyword_lower in r.get('content', '').lower()
            ]

        return results[:limit]

    def get_stats(self) -> Dict:
        """获取数据统计"""
        from collections import Counter

        return {
            "total_records": len(self.data),
            "by_category": dict(Counter(r.get('category') for r in self.data)),
            "by_source": dict(Counter(r.get('source') for r in self.data)),
            "latest_crawl": max(
                (r.get('crawled_at') for r in self.data),
                default=None
            )
        }


# 便捷函数
def create_default_scheduler() -> CrawlerScheduler:
    """创建默认的爬虫调度器（包含常用爬虫）"""
    scheduler = CrawlerScheduler()

    # 注册监管政策爬虫
    scheduler.register_crawler(CBIRCrawler())

    # 注册保险公司爬虫（示例）
    # scheduler.register_crawler(InsuranceCompanyCrawler(
    #     company_name="示例保险",
    #     base_url="https://www.example-ins.com",
    #     product_list_path="/products"
    # ))

    return scheduler


async def run_crawl_and_save(store_path: Optional[str] = None) -> Dict:
    """
    一键执行爬取并保存

    Returns:
        爬取统计信息
    """
    scheduler = create_default_scheduler()
    store = DataStore(db_path=store_path)

    # 执行爬取
    results = await scheduler.run_all()

    # 保存结果
    saved_count = store.save_results(results)
    store.persist()

    return {
        "crawled": len(results),
        "saved": saved_count,
        "duplicates": len(results) - saved_count,
        "stats": store.get_stats()
    }
