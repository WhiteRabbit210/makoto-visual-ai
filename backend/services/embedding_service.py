"""
エンベディング（ベクトル化）サービス
OpenAI text-embedding-3-largeを使用した文書のベクトル化と検索
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import asyncio
from datetime import datetime
import hashlib

# Azure OpenAI
from openai import AsyncAzureOpenAI

# ストレージサービス
from services.storage_service import storage_service
from services.kvm_service import kvm_service


@dataclass
class ChunkResult:
    """チャンク化の結果"""
    chunk_id: str
    text: str
    position: int
    metadata: Dict[str, Any]


@dataclass
class EmbeddingResult:
    """エンベディングの結果"""
    chunk_id: str
    embedding: List[float]
    text: str
    metadata: Dict[str, Any]


@dataclass
class SearchResult:
    """検索結果"""
    chunk_id: str
    text: str
    score: float
    filename: str
    metadata: Dict[str, Any]


class EmbeddingService:
    """
    エンベディングサービス
    - テキストのチャンク化
    - OpenAI APIでのベクトル化
    - コサイン類似度による検索
    """
    
    def __init__(self):
        # Azure OpenAI エンベディング専用設定
        self.client = AsyncAzureOpenAI(
            api_key=os.getenv('AZURE_OPENAI_EMBEDDING_API_KEY'),
            api_version=os.getenv('AZURE_OPENAI_EMBEDDING_API_VERSION', '2024-12-01-preview'),
            azure_endpoint=os.getenv('AZURE_OPENAI_EMBEDDING_ENDPOINT')
        )
        
        # エンベディングモデル設定
        self.embedding_model = os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'text-embedding-3-large-Trial')
        self.embedding_dimension = 3072  # text-embedding-3-largeの次元数
        
        # チャンク設定
        self.chunk_size = 1000  # 文字数
        self.chunk_overlap = 200  # 重複文字数
    
    def create_chunks(self, text: str, filename: str) -> List[ChunkResult]:
        """
        テキストをチャンクに分割
        
        Args:
            text: 分割するテキスト
            filename: ファイル名
            
        Returns:
            チャンクのリスト
        """
        chunks = []
        text_length = len(text)
        position = 0
        chunk_index = 0
        
        while position < text_length:
            # チャンクの終了位置を計算
            end_position = min(position + self.chunk_size, text_length)
            
            # 文の途中で切れないように調整（句読点で区切る）
            if end_position < text_length:
                # 句読点を探す
                for punct in ['。', '．', '！', '？', '\n\n', '\n']:
                    last_punct = text.rfind(punct, position, end_position)
                    if last_punct != -1:
                        end_position = last_punct + len(punct)
                        break
            
            # チャンクを作成
            chunk_text = text[position:end_position].strip()
            if chunk_text:  # 空のチャンクは無視
                chunk_id = hashlib.md5(f"{filename}_{chunk_index}_{chunk_text[:50]}".encode()).hexdigest()[:12]
                
                chunks.append(ChunkResult(
                    chunk_id=chunk_id,
                    text=chunk_text,
                    position=chunk_index,
                    metadata={
                        "filename": filename,
                        "start_position": position,
                        "end_position": end_position,
                        "chunk_index": chunk_index,
                        "total_chunks": 0  # 後で更新
                    }
                ))
                chunk_index += 1
            
            # 次の開始位置（オーバーラップを考慮）
            position = end_position - self.chunk_overlap
            if position <= 0:
                position = end_position
        
        # 総チャンク数を更新
        for chunk in chunks:
            chunk.metadata["total_chunks"] = len(chunks)
        
        return chunks
    
    async def create_embedding(self, text: str) -> List[float]:
        """
        テキストのエンベディングを作成
        
        Args:
            text: エンベディングするテキスト
            
        Returns:
            エンベディングベクトル
        """
        try:
            # Azure OpenAI エンベディングAPIを呼び出し
            response = await self.client.embeddings.create(
                model=self.embedding_model,  # デプロイメント名を使用
                input=text
            )
            
            # エンベディングを取得
            embedding = response.data[0].embedding
            return embedding
            
        except Exception as e:
            print(f"[ERROR] Failed to create embedding: {str(e)}")
            raise
    
    async def embed_chunks(self, chunks: List[ChunkResult]) -> List[EmbeddingResult]:
        """
        チャンクのリストをエンベディング
        
        Args:
            chunks: チャンクのリスト
            
        Returns:
            エンベディング結果のリスト
        """
        results = []
        
        # バッチ処理（並列化）
        batch_size = 5  # 同時に処理するチャンク数
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            
            # 並列でエンベディングを作成
            embedding_tasks = [
                self.create_embedding(chunk.text)
                for chunk in batch
            ]
            
            embeddings = await asyncio.gather(*embedding_tasks)
            
            # 結果を格納
            for chunk, embedding in zip(batch, embeddings):
                results.append(EmbeddingResult(
                    chunk_id=chunk.chunk_id,
                    embedding=embedding,
                    text=chunk.text,
                    metadata=chunk.metadata
                ))
        
        return results
    
    async def save_embeddings(
        self,
        library_id: str,
        filename: str,
        embeddings: List[EmbeddingResult],
        tenant_id: str = "default_tenant",
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """
        エンベディングをストレージに保存
        
        Args:
            library_id: ライブラリID
            filename: ファイル名
            embeddings: エンベディング結果のリスト
            tenant_id: テナントID
            user_id: ユーザーID
            
        Returns:
            保存結果
        """
        # エンベディングデータを準備
        embedding_data = {
            "filename": filename,
            "embedding_model": self.embedding_model,
            "embedding_dimension": self.embedding_dimension,
            "chunk_count": len(embeddings),
            "created_at": datetime.utcnow().isoformat(),
            "chunks": [
                {
                    "chunk_id": emb.chunk_id,
                    "text": emb.text,
                    "embedding": emb.embedding,
                    "metadata": emb.metadata
                }
                for emb in embeddings
            ]
        }
        
        # JSONとして保存
        storage_key = f"{tenant_id}/library/{library_id}/embeddings/{filename}.json"
        content = json.dumps(embedding_data, ensure_ascii=False, indent=2)
        
        await storage_service.put_object(
            key=storage_key,
            content=content,
            metadata={
                "library_id": library_id,
                "filename": filename,
                "chunk_count": str(len(embeddings))
            }
        )
        
        # KVMのファイル情報を更新
        pk = f"TENANT#{tenant_id}#USER#{user_id}"
        sk = f"LIBRARY#{library_id}#FILE#{filename}"
        
        await kvm_service.update_item(pk, sk, {
            "embedding_status": "completed",
            "chunk_count": len(embeddings),
            "embedded_at": datetime.utcnow().isoformat()
        })
        
        return {
            "success": True,
            "chunk_count": len(embeddings),
            "storage_key": storage_key
        }
    
    async def load_embeddings(
        self,
        library_id: str,
        tenant_id: str = "default_tenant"
    ) -> Dict[str, List[EmbeddingResult]]:
        """
        ライブラリの全エンベディングを読み込み
        
        Args:
            library_id: ライブラリID
            tenant_id: テナントID
            
        Returns:
            ファイル名をキーとしたエンベディングの辞書
        """
        embeddings_by_file = {}
        
        # エンベディングファイルのリストを取得
        prefix = f"{tenant_id}/library/{library_id}/embeddings/"
        result = await storage_service.list_objects(prefix=prefix)
        
        if result.get('success') and result.get('objects'):
            for obj in result['objects']:
                key = obj['key']
                if key.endswith('.json'):
                    # エンベディングデータを読み込み
                    content = await storage_service.get_object(key)
                    if content:
                        data = json.loads(content)
                        filename = data['filename']
                        
                        # EmbeddingResultオブジェクトに変換
                        embeddings = []
                        for chunk in data['chunks']:
                            embeddings.append(EmbeddingResult(
                                chunk_id=chunk['chunk_id'],
                                embedding=chunk['embedding'],
                                text=chunk['text'],
                                metadata=chunk['metadata']
                            ))
                        
                        embeddings_by_file[filename] = embeddings
        
        return embeddings_by_file
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        コサイン類似度を計算
        
        Args:
            vec1: ベクトル1
            vec2: ベクトル2
            
        Returns:
            コサイン類似度（-1～1）
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        # ゼロベクトルのチェック
        if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
            return 0.0
        
        # コサイン類似度を計算
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)
    
    async def search(
        self,
        library_id: str,
        query: str,
        top_k: int = 10,
        threshold: float = 0.7,
        tenant_id: str = "default_tenant"
    ) -> List[SearchResult]:
        """
        ライブラリ内をベクトル検索
        
        Args:
            library_id: ライブラリID
            query: 検索クエリ
            top_k: 返す結果の最大数
            threshold: 類似度の閾値
            tenant_id: テナントID
            
        Returns:
            検索結果のリスト
        """
        # クエリのエンベディングを作成
        query_embedding = await self.create_embedding(query)
        
        # ライブラリの全エンベディングを読み込み
        embeddings_by_file = await self.load_embeddings(library_id, tenant_id)
        
        # 全チャンクとの類似度を計算
        results = []
        for filename, embeddings in embeddings_by_file.items():
            for emb in embeddings:
                # コサイン類似度を計算
                similarity = self.cosine_similarity(query_embedding, emb.embedding)
                
                # 閾値以上の場合は結果に追加
                if similarity >= threshold:
                    results.append(SearchResult(
                        chunk_id=emb.chunk_id,
                        text=emb.text,
                        score=similarity,
                        filename=filename,
                        metadata=emb.metadata
                    ))
        
        # スコアでソート（降順）
        results.sort(key=lambda x: x.score, reverse=True)
        
        # top_k件を返す
        return results[:top_k]
    
    async def process_file(
        self,
        library_id: str,
        filename: str,
        text: str,
        tenant_id: str = "default_tenant",
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """
        ファイル全体のエンベディング処理
        
        Args:
            library_id: ライブラリID
            filename: ファイル名
            text: ファイルのテキスト
            tenant_id: テナントID
            user_id: ユーザーID
            
        Returns:
            処理結果
        """
        try:
            # チャンク化
            chunks = self.create_chunks(text, filename)
            print(f"[INFO] Created {len(chunks)} chunks for {filename}")
            
            # エンベディング作成
            embeddings = await self.embed_chunks(chunks)
            print(f"[INFO] Created embeddings for {len(embeddings)} chunks")
            
            # 保存
            result = await self.save_embeddings(
                library_id=library_id,
                filename=filename,
                embeddings=embeddings,
                tenant_id=tenant_id,
                user_id=user_id
            )
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Failed to process file {filename}: {str(e)}")
            
            # KVMのステータスを更新
            pk = f"TENANT#{tenant_id}#USER#{user_id}"
            sk = f"LIBRARY#{library_id}#FILE#{filename}"
            
            await kvm_service.update_item(pk, sk, {
                "embedding_status": "failed",
                "embedding_error": str(e),
                "updated_at": datetime.utcnow().isoformat()
            })
            
            raise


# シングルトンインスタンス
embedding_service = EmbeddingService()