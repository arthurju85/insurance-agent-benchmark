"""
数据爬虫相关API路由
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional

import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
try:
    from ...crawler.crawler import (
        CrawlerScheduler, DataStore, create_default_scheduler,
        CBIRCrawler, InsuranceCompanyCrawler, run_crawl_and_save
    )
    from ...crawler.parser import extract_structured_data
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from crawler.crawler import (
        CrawlerScheduler, DataStore, create_default_scheduler,
        CBIRCrawler, InsuranceCompanyCrawler, run_crawl_and_save
    )
    from crawler.parser import extract_structured_data

router = APIRouter()


class CrawlRequest(BaseModel):
    """爬取请求"""
    sources: List[str] = []  # 指定来源，空表示全部
    save: bool = True


class ParseRequest(BaseModel):
    """解析请求"""
    text: str
    product_name: Optional[str] = None
    company: Optional[str] = None


class AddCompanyCrawlerRequest(BaseModel):
    """添加保险公司爬虫请求"""
    company_name: str
    base_url: str
    product_list_path: str


@router.post("/run")
async def run_crawl(request: CrawlRequest):
    """
    执行数据爬取
    """
    scheduler = create_default_scheduler()

    if request.sources:
        # 只运行指定的爬虫
        results = []
        for source in request.sources:
            try:
                source_results = await scheduler.run_specific(source)
                results.extend(source_results)
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
    else:
        # 运行所有爬虫
        results = await scheduler.run_all()

    # 保存结果
    saved_count = 0
    if request.save:
        store = DataStore()
        saved_count = store.save_results(results)
        store.persist()

    return {
        "success": True,
        "crawled_count": len(results),
        "saved_count": saved_count,
        "sources": list(set(r.source for r in results)),
        "categories": list(set(r.category for r in results))
    }


@router.post("/run-async")
async def run_crawl_async(
    background_tasks: BackgroundTasks,
    request: CrawlRequest
):
    """
    异步执行数据爬取（后台任务）
    """
    async def crawl_task():
        result = await run_crawl_and_save()
        print(f"Crawl completed: {result}")

    background_tasks.add_task(crawl_task)

    return {
        "success": True,
        "message": "爬取任务已启动",
        "status": "running"
    }


@router.get("/sources")
async def list_sources():
    """
    列出可用的爬虫来源
    """
    scheduler = create_default_scheduler()

    return [
        {
            "name": c.source_name,
            "base_url": c.base_url,
            "type": c.__class__.__name__
        }
        for c in scheduler.crawlers
    ]


@router.post("/companies/add")
async def add_company_crawler(request: AddCompanyCrawlerRequest):
    """
    添加保险公司爬虫
    """
    crawler = InsuranceCompanyCrawler(
        company_name=request.company_name,
        base_url=request.base_url,
        product_list_path=request.product_list_path
    )

    # 测试连接
    try:
        async with crawler:
            test_html = await crawler.fetch(request.base_url)
            if test_html:
                return {
                    "success": True,
                    "message": f"已添加 {request.company_name} 爬虫",
                    "crawler": {
                        "name": crawler.source_name,
                        "base_url": crawler.base_url
                    }
                }
            else:
                raise HTTPException(
                    status_code=400,
                    detail="无法访问指定网站，请检查URL"
                )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"添加爬虫失败: {str(e)}"
        )


@router.get("/data")
async def query_crawled_data(
    category: Optional[str] = None,
    source: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = 50
):
    """
    查询已爬取的数据
    """
    store = DataStore()
    results = store.query(
        category=category,
        source=source,
        keyword=keyword,
        limit=limit
    )

    return {
        "total": len(results),
        "data": results
    }


@router.get("/data/{hash_id}")
async def get_crawled_item(hash_id: str):
    """
    获取单条爬取数据详情
    """
    store = DataStore()

    for item in store.data:
        if item.get('hash_id') == hash_id:
            return item

    raise HTTPException(status_code=404, detail="数据不存在")


@router.post("/parse")
async def parse_clause(request: ParseRequest):
    """
    解析保险条款文本
    """
    try:
        structured_data = extract_structured_data(request.text)

        return {
            "success": True,
            "product_name": request.product_name,
            "company": request.company,
            "structured_data": structured_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"解析失败: {str(e)}"
        )


@router.get("/stats")
async def get_crawl_stats():
    """
    获取爬取统计信息
    """
    store = DataStore()

    return {
        "storage": store.get_stats(),
        "available_sources": [
            {"name": "国家金融监督管理总局", "type": "监管政策"},
            {"name": "裁判文书网", "type": "法律案例"},
        ]
    }


@router.delete("/data/{hash_id}")
async def delete_crawled_item(hash_id: str):
    """
    删除单条爬取数据
    """
    store = DataStore()

    for i, item in enumerate(store.data):
        if item.get('hash_id') == hash_id:
            deleted = store.data.pop(i)
            store.persist()
            return {
                "success": True,
                "deleted": deleted.get('title', 'Unknown')
            }

    raise HTTPException(status_code=404, detail="数据不存在")
