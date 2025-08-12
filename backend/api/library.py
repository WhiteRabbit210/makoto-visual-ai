"""
ライブラリ管理API
library_id/filename ベースの実装
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import io

from services.library_service import library_service

router = APIRouter()


# リクエスト/レスポンスモデル
class CreateLibraryRequest(BaseModel):
    """ライブラリ作成リクエスト"""
    name: str
    description: Optional[str] = ""
    metadata: Optional[Dict[str, Any]] = None


class UpdateLibraryRequest(BaseModel):
    """ライブラリ更新リクエスト"""
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    """ベクトル検索リクエスト"""
    query: str
    top_k: int = 10
    threshold: float = 0.7


class EmbeddingRequest(BaseModel):
    """エンベディング開始リクエスト"""
    force_update: bool = False


# ライブラリ管理エンドポイント
@router.get("/libraries")
async def get_libraries(
    tenant_id: str = "default_tenant",
    user_id: str = "default_user"
):
    """ライブラリ一覧を取得"""
    try:
        libraries = await library_service.get_libraries(tenant_id, user_id)
        return libraries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/libraries/{library_id}")
async def get_library(
    library_id: str,
    tenant_id: str = "default_tenant",
    user_id: str = "default_user"
):
    """ライブラリ詳細を取得（ファイル一覧含む）"""
    try:
        library = await library_service.get_library(library_id, tenant_id, user_id)
        if not library:
            raise HTTPException(status_code=404, detail="Library not found")
        return library
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/libraries")
async def create_library(
    request: CreateLibraryRequest,
    tenant_id: str = "default_tenant",
    user_id: str = "default_user"
):
    """新規ライブラリを作成"""
    try:
        library = await library_service.create_library(
            name=request.name,
            description=request.description,
            metadata=request.metadata,
            tenant_id=tenant_id,
            user_id=user_id
        )
        return library
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/libraries/{library_id}")
async def update_library(
    library_id: str,
    request: UpdateLibraryRequest,
    tenant_id: str = "default_tenant",
    user_id: str = "default_user"
):
    """ライブラリ情報を更新"""
    try:
        library = await library_service.update_library(
            library_id=library_id,
            name=request.name,
            description=request.description,
            metadata=request.metadata,
            tenant_id=tenant_id,
            user_id=user_id
        )
        if not library:
            raise HTTPException(status_code=404, detail="Library not found")
        return library
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/libraries/{library_id}")
async def delete_library(
    library_id: str,
    tenant_id: str = "default_tenant",
    user_id: str = "default_user"
):
    """ライブラリとその全ファイルを削除"""
    try:
        result = await library_service.delete_library(library_id, tenant_id, user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ファイル管理エンドポイント
@router.post("/libraries/{library_id}/files")
async def upload_file(
    library_id: str,
    file: UploadFile = File(...),
    tenant_id: str = "default_tenant",
    user_id: str = "default_user"
):
    """ファイルをアップロード（PDF, TXT, DOCX, XLSX, PPTX対応）"""
    # ファイル形式チェック
    allowed_extensions = {'.pdf', '.txt', '.docx', '.xlsx', '.pptx'}
    file_ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # ファイルサイズチェック（100MB上限）
    content = await file.read()
    if len(content) > 100 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds maximum allowed size of 100MB"
        )
    
    try:
        # ファイル名をデコード（URLエンコードされている場合）
        import urllib.parse
        decoded_filename = urllib.parse.unquote(file.filename)
        
        # デバッグ: コンテンツタイプとサイズを確認
        print(f"[DEBUG] Original filename: {file.filename}")
        print(f"[DEBUG] Decoded filename: {decoded_filename}")
        print(f"[DEBUG] Content type: {file.content_type}")
        print(f"[DEBUG] Content size: {len(content)} bytes")
        print(f"[DEBUG] Is bytes: {isinstance(content, bytes)}")
        
        result = await library_service.upload_file(
            library_id=library_id,
            filename=decoded_filename,  # デコード済みのファイル名を使用
            content=content,
            content_type=file.content_type or "application/octet-stream",
            tenant_id=tenant_id,
            user_id=user_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"[DEBUG] Upload error: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/libraries/{library_id}/files/{filename}")
async def download_file(
    library_id: str,
    filename: str,
    tenant_id: str = "default_tenant",
    user_id: str = "default_user"
):
    """ファイルをダウンロード"""
    try:
        print(f"[DEBUG download] Library ID: {library_id}")
        print(f"[DEBUG download] Filename (raw): {filename}")
        print(f"[DEBUG download] Filename (repr): {repr(filename)}")
        
        file_data = await library_service.get_file(
            library_id=library_id,
            filename=filename,
            tenant_id=tenant_id,
            user_id=user_id
        )
        
        print(f"[DEBUG download] File data result: {file_data is not None}")
        
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found")
        
        # コンテンツの型とサイズをデバッグ
        print(f"[DEBUG download] Content type: {file_data.get('content_type')}")
        print(f"[DEBUG download] Content is str: {isinstance(file_data.get('content'), str)}")
        print(f"[DEBUG download] Content is bytes: {isinstance(file_data.get('content'), bytes)}")
        
        # コンテンツの準備
        content = file_data['content']
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        # ファイル名をRFC 5987形式でエンコード（日本語対応）
        import urllib.parse
        encoded_filename = urllib.parse.quote(filename, safe='')
        
        # StreamingResponseで返す
        return StreamingResponse(
            io.BytesIO(content),
            media_type=file_data['content_type'],
            headers={
                "Content-Disposition": f"attachment; filename*=utf-8''{encoded_filename}"
            }
        )
    except ValueError as e:
        print(f"[DEBUG download] ValueError: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"[DEBUG download] Exception: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"[DEBUG download] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/libraries/{library_id}/files/{filename}")
async def delete_file(
    library_id: str,
    filename: str,
    tenant_id: str = "default_tenant",
    user_id: str = "default_user"
):
    """特定ファイルを削除"""
    try:
        result = await library_service.delete_file(
            library_id=library_id,
            filename=filename,
            tenant_id=tenant_id,
            user_id=user_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/libraries/{library_id}/files/{filename}/text")
async def extract_text(
    library_id: str,
    filename: str,
    tenant_id: str = "default_tenant",
    user_id: str = "default_user"
):
    """ファイルからテキスト抽出（全対応形式）"""
    try:
        file_data = await library_service.get_file(
            library_id=library_id,
            filename=filename,
            tenant_id=tenant_id,
            user_id=user_id
        )
        
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found")
        
        # ドキュメント抽出サービスを使用
        from services.document_extractor import document_extractor
        
        # ファイル内容を取得
        content = file_data.get('content')
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        # テキスト抽出
        result = await document_extractor.extract_text(content, filename)
        
        if result.success:
            return {
                "filename": filename,
                "text": result.text,
                "metadata": {
                    "format": result.metadata.format,
                    "page_count": result.metadata.page_count,
                    "paragraph_count": result.metadata.paragraph_count,
                    "table_count": result.metadata.table_count,
                    "sheet_count": result.metadata.sheet_count,
                    "sheet_names": result.metadata.sheet_names,
                    "slide_count": result.metadata.slide_count,
                    "size": result.metadata.size
                },
                "extracted_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=result.error)
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# エンベディング管理エンドポイント
@router.post("/libraries/{library_id}/embeddings")
async def start_embeddings(
    library_id: str,
    request: EmbeddingRequest = EmbeddingRequest(),
    tenant_id: str = "default_tenant",
    user_id: str = "default_user"
):
    """ライブラリ全体のエンベディングを開始"""
    # TODO: 実際のエンベディング処理を実装
    return {
        "job_id": f"job_{library_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "status": "pending",
        "message": "Embedding job started",
        "library_id": library_id
    }


@router.get("/libraries/{library_id}/embeddings/status")
async def get_embedding_status(
    library_id: str,
    tenant_id: str = "default_tenant",
    user_id: str = "default_user"
):
    """エンベディング処理状況を確認"""
    try:
        library = await library_service.get_library(library_id, tenant_id, user_id)
        if not library:
            raise HTTPException(status_code=404, detail="Library not found")
        
        return {
            "status": library.get('embedding_status', 'idle'),
            "total_chunks": 0,  # TODO: 実際のチャンク数を取得
            "embedded_chunks": 0,  # TODO: 実際の処理済みチャンク数を取得
            "last_updated": library.get('updated_at'),
            "vector_count": library.get('vector_count', 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/libraries/{library_id}/files/{filename}/embeddings")
async def update_file_embeddings(
    library_id: str,
    filename: str,
    tenant_id: str = "default_tenant",
    user_id: str = "default_user"
):
    """特定ファイルのエンベディングを更新"""
    # TODO: 実際のエンベディング更新処理を実装
    return {
        "message": "File embedding update started",
        "filename": filename,
        "library_id": library_id
    }


@router.delete("/libraries/{library_id}/files/{filename}/embeddings")
async def delete_file_embeddings(
    library_id: str,
    filename: str,
    tenant_id: str = "default_tenant",
    user_id: str = "default_user"
):
    """特定ファイルのエンベディングを削除"""
    # TODO: 実際のエンベディング削除処理を実装
    return {
        "message": "File embeddings deleted",
        "filename": filename,
        "library_id": library_id
    }


@router.post("/libraries/{library_id}/search")
async def search_library(
    library_id: str,
    request: SearchRequest,
    tenant_id: str = "default_tenant",
    user_id: str = "default_user"
):
    """ライブラリ内をベクトル検索（RAG用）"""
    # TODO: 実際のベクトル検索処理を実装
    return {
        "results": [
            {
                "filename": "sample.pdf",
                "chunk": "This is a sample text chunk that matches the query.",
                "score": 0.95,
                "metadata": {
                    "page": 1,
                    "position": 0
                }
            }
        ],
        "query": request.query,
        "library_id": library_id
    }