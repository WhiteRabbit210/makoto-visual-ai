"""
WebクロールAPI

ドキュメント（/makoto/docs/仕様書/型定義/WebクロールAPI型定義.md）に
完全準拠した実装で、既存のweb_crawler_serviceを利用します。
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Optional, List
import uuid
from datetime import datetime

# 型定義をインポート
from backend_types.api_types import (
    WebCrawlRequest,
    WebCrawlResponse,
    CrawlResult,
    CrawlJobStatus,
    generate_uuid,
    get_current_datetime
)
from services.web_crawler_service import web_crawler_service
from utils.logger import log_api_request, log_api_response, log_error

router = APIRouter()

# ジョブストレージ（インメモリ）
crawl_jobs: Dict[str, Dict] = {}

@router.post("/crawl")
async def crawl_web(request: WebCrawlRequest) -> WebCrawlResponse:
    """
    Webクロールを開始
    
    指定されたURLをクロールして情報を収集します
    """
    log_api_request("/api/webcrawl/crawl", "POST", {
        "url": request.url,
        "max_depth": request.max_depth,
        "max_pages": request.max_pages
    })
    
    try:
        # ジョブIDを生成
        job_id = generate_uuid()
        
        # URLからキーワードを抽出（簡易実装）
        keywords = [request.url.split('//')[-1].split('/')[0]]  # ドメイン名をキーワードとして使用
        
        # Web crawlerサービスを呼び出し（要約をスキップして高速化）
        result = await web_crawler_service.search_and_crawl(
            keywords=keywords,
            original_query=f"URL: {request.url} の内容を取得",
            skip_summary=True  # 要約処理をスキップして高速化
        )
        
        # 結果を変換
        if result.get('success'):
            crawl_results = []
            
            # クロール結果を変換
            for content in result.get('crawled_contents', []):
                crawl_result = CrawlResult(
                    url=content.get('url', request.url),
                    title=content.get('title', 'No title'),
                    content=content.get('content', ''),
                    images=[] if not request.extract_images else None,
                    links=[] if not request.extract_links else None
                )
                crawl_results.append(crawl_result)
            
            # ソース情報からも結果を追加
            for source in result.get('sources', []):
                if not any(cr.url == source['url'] for cr in crawl_results):
                    crawl_result = CrawlResult(
                        url=source['url'],
                        title=source.get('title', 'No title'),
                        content=source.get('snippet', ''),
                        images=[] if request.extract_images else None,
                        links=[] if request.extract_links else None
                    )
                    crawl_results.append(crawl_result)
            
            # ジョブを保存
            crawl_jobs[job_id] = {
                "job_id": job_id,
                "status": "completed",
                "started_at": get_current_datetime(),
                "completed_at": get_current_datetime(),
                "request": request.model_dump(),
                "results": crawl_results,
                "summary": result.get('summary')
            }
            
            response = WebCrawlResponse(
                job_id=job_id,
                status="completed",
                results=crawl_results[:request.max_pages] if crawl_results else []
            )
            
            log_api_response("/api/webcrawl/crawl", 200, {
                "job_id": job_id,
                "status": "completed",
                "results_count": len(crawl_results)
            })
            
        else:
            # エラーの場合
            error_msg = result.get('error', 'Unknown error')
            
            crawl_jobs[job_id] = {
                "job_id": job_id,
                "status": "failed",
                "started_at": get_current_datetime(),
                "completed_at": get_current_datetime(),
                "request": request.model_dump(),
                "error": error_msg
            }
            
            response = WebCrawlResponse(
                job_id=job_id,
                status="failed",
                error=error_msg
            )
            
            log_error("Web Crawl Failed", error_msg, "/api/webcrawl/crawl")
        
        return response
        
    except Exception as e:
        log_error("Web Crawl Exception", str(e), "/api/webcrawl/crawl")
        
        # エラー時もジョブを保存
        job_id = generate_uuid()
        crawl_jobs[job_id] = {
            "job_id": job_id,
            "status": "failed",
            "started_at": get_current_datetime(),
            "completed_at": get_current_datetime(),
            "request": request.model_dump(),
            "error": str(e)
        }
        
        return WebCrawlResponse(
            job_id=job_id,
            status="failed",
            error=f"Webクロールエラー: {str(e)}"
        )

@router.get("/status/{job_id}")
async def get_crawl_status(job_id: str) -> WebCrawlResponse:
    """
    クロールジョブのステータスを取得
    
    指定されたジョブIDのクロール状態を返します
    """
    if job_id not in crawl_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = crawl_jobs[job_id]
    
    return WebCrawlResponse(
        job_id=job_id,
        status=job["status"],
        results=job.get("results"),
        error=job.get("error")
    )

@router.post("/cancel/{job_id}")
async def cancel_crawl(job_id: str) -> Dict[str, str]:
    """
    クロールジョブをキャンセル
    
    実行中のクロールジョブを停止します
    """
    if job_id not in crawl_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = crawl_jobs[job_id]
    
    if job["status"] not in ["running", "paused"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status: {job['status']}"
        )
    
    # ジョブをキャンセル
    job["status"] = "cancelled"
    job["cancelled_at"] = get_current_datetime()
    
    return {
        "message": "Job cancelled successfully",
        "job_id": job_id,
        "status": "cancelled"
    }

@router.get("/jobs")
async def list_crawl_jobs(
    status: Optional[CrawlJobStatus] = None,
    limit: int = 20
) -> Dict:
    """
    クロールジョブ一覧を取得
    
    実行中または完了したクロールジョブの一覧を返します
    """
    jobs = list(crawl_jobs.values())
    
    # ステータスでフィルタ
    if status:
        jobs = [j for j in jobs if j["status"] == status]
    
    # 新しい順にソート
    jobs.sort(key=lambda x: x.get("started_at", ""), reverse=True)
    
    # 制限
    jobs = jobs[:limit]
    
    return {
        "jobs": jobs,
        "total": len(jobs)
    }

# 既存のサービスとの互換性のためのエンドポイント（キーワード検索）
from pydantic import BaseModel

class KeywordSearchRequest(BaseModel):
    """キーワード検索リクエスト"""
    keywords: List[str]
    original_query: str

@router.post("/search")
async def search_and_crawl(request: KeywordSearchRequest) -> Dict:
    """
    キーワード検索してWebクロール（既存サービスのラッパー）
    
    Google検索を実行し、結果をクロールします
    """
    log_api_request("/api/webcrawl/search", "POST", {
        "keywords": request.keywords,
        "query": request.original_query
    })
    
    try:
        # 既存のサービスを呼び出し
        result = await web_crawler_service.search_and_crawl(
            keywords=request.keywords,
            original_query=request.original_query
        )
        
        if result.get('success'):
            log_api_response("/api/webcrawl/search", 200, {
                "sources_count": len(result.get('sources', [])),
                "has_summary": bool(result.get('summary'))
            })
        else:
            log_error("Search Failed", result.get('error', 'Unknown error'), "/api/webcrawl/search")
        
        return result
        
    except Exception as e:
        log_error("Search Exception", str(e), "/api/webcrawl/search")
        return {
            "success": False,
            "error": str(e),
            "crawled_contents": [],
            "sources": []
        }