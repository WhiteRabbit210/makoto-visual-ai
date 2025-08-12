"""
日次バッチ処理サービス（Parquet変換）

BlobStorage/S3のメッセージデータを日次でParquet形式に変換し、
Athena/Synapseでの分析を可能にします。

仕様書: /makoto/docs/仕様書/データ保存仕様書.md#分析用データ（日次バッチ）
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from services.storage_service import storage_service
from services.kvm_service import kvm_service
import logging

logger = logging.getLogger(__name__)


class BatchProcessor:
    """日次バッチ処理クラス"""
    
    def __init__(self, tenant_id: str = "default_tenant"):
        self.tenant_id = tenant_id
        self.batch_size = 1000  # 一度に処理するメッセージ数
        
    async def process_daily_batch(self, target_date: Optional[datetime] = None):
        """
        日次バッチ処理のメイン関数
        
        Args:
            target_date: 処理対象日（指定なしの場合は前日）
        """
        if target_date is None:
            # デフォルトは前日
            target_date = datetime.now() - timedelta(days=1)
        
        date_str = target_date.strftime("%Y-%m-%d")
        logger.info(f"日次バッチ処理開始: {date_str}")
        
        try:
            # 1. 対象メッセージを収集
            messages = await self._collect_messages(target_date)
            logger.info(f"収集したメッセージ数: {len(messages)}")
            
            if not messages:
                logger.info("処理対象のメッセージがありません")
                return
            
            # 2. DataFrameに変換
            df = self._create_dataframe(messages)
            
            # 3. Parquet形式で保存
            output_path = await self._save_as_parquet(df, target_date)
            logger.info(f"Parquetファイル保存完了: {output_path}")
            
            # 4. 処理完了をKVMに記録
            await self._record_batch_completion(target_date, len(messages), output_path)
            
            logger.info(f"日次バッチ処理完了: {date_str}")
            return {
                'success': True,
                'date': date_str,
                'message_count': len(messages),
                'output_path': output_path
            }
            
        except Exception as e:
            logger.error(f"バッチ処理エラー: {e}")
            return {
                'success': False,
                'date': date_str,
                'error': str(e)
            }
    
    async def _collect_messages(self, target_date: datetime) -> List[Dict[str, Any]]:
        """
        対象日のメッセージを収集
        
        Args:
            target_date: 処理対象日
        
        Returns:
            メッセージのリスト
        """
        messages = []
        
        # 日付パスを構築
        year = target_date.strftime("%Y")
        month = target_date.strftime("%m")
        day = target_date.strftime("%d")
        
        # テナント内の全ユーザーのメッセージを収集
        # 実際の実装ではKVMから対象ユーザーリストを取得
        pk = f"TENANT#{self.tenant_id}"
        users = await kvm_service.query(pk=pk, sk_prefix="USER#")
        
        for user_item in users:
            user_id = user_item.get('SK', '').replace('USER#', '')
            if not user_id:
                continue
            
            # ユーザーの全チャットルームを取得
            user_pk = f"TENANT#{self.tenant_id}#USER#{user_id}"
            rooms = await kvm_service.query(pk=user_pk, sk_prefix="CHAT#")
            
            for room_item in rooms:
                room_id = room_item.get('SK', '').replace('CHAT#', '')
                if not room_id:
                    continue
                
                # メッセージのパスパターン
                prefix = f"{self.tenant_id}/chat/{user_id}/{room_id}/messages/{year}/{month}/{day}/"
                
                # ストレージからメッセージファイルリストを取得
                result = await storage_service.list_objects(prefix=prefix)
                
                if result['success'] and result.get('objects'):
                    for obj in result['objects']:
                        # メッセージファイルを読み込み
                        msg_result = await storage_service.get_json(obj['key'])
                        if msg_result['success'] and msg_result.get('data'):
                            message_data = msg_result['data']
                            # メタデータを追加
                            message_data['tenant_id'] = self.tenant_id
                            message_data['user_id'] = user_id
                            message_data['room_id'] = room_id
                            message_data['storage_key'] = obj['key']
                            messages.append(message_data)
        
        return messages
    
    def _create_dataframe(self, messages: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        メッセージリストからDataFrameを作成
        
        Args:
            messages: メッセージのリスト
        
        Returns:
            pandas DataFrame
        """
        # DataFrameに変換
        df = pd.DataFrame(messages)
        
        # データ型の最適化
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # カテゴリ型に変換（メモリ効率化）
        categorical_columns = ['tenant_id', 'user_id', 'room_id', 'role']
        for col in categorical_columns:
            if col in df.columns:
                df[col] = df[col].astype('category')
        
        # 必要なカラムを追加
        df['processed_at'] = datetime.now()
        
        # ソート
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp')
        
        return df
    
    async def _save_as_parquet(self, df: pd.DataFrame, target_date: datetime) -> str:
        """
        DataFrameをParquet形式で保存
        
        Args:
            df: 保存するDataFrame
            target_date: 処理対象日
        
        Returns:
            保存先パス
        """
        # Hive形式のパーティションパス
        year = target_date.strftime("%Y")
        month = target_date.strftime("%m")
        day = target_date.strftime("%d")
        
        # 出力パス
        output_key = (
            f"{self.tenant_id}/analytics/messages/"
            f"year={year}/month={month}/day={day}/"
            f"messages_{target_date.strftime('%Y%m%d')}.parquet"
        )
        
        # Parquetバイナリに変換
        table = pa.Table.from_pandas(df)
        
        # メモリバッファに書き込み
        import io
        buffer = io.BytesIO()
        pq.write_table(
            table, 
            buffer,
            compression='snappy',  # 圧縮アルゴリズム
            use_dictionary=True,    # 辞書エンコーディング
            compression_level=9     # 圧縮レベル（最大）
        )
        
        # ストレージに保存
        buffer.seek(0)
        result = await storage_service.upload_file(
            file_content=buffer.getvalue(),
            key=output_key,
            content_type='application/octet-stream'
        )
        
        if result['success']:
            return output_key
        else:
            raise Exception(f"Parquetファイルの保存に失敗: {result.get('error')}")
    
    async def _record_batch_completion(self, target_date: datetime, message_count: int, output_path: str):
        """
        バッチ処理完了をKVMに記録
        
        Args:
            target_date: 処理対象日
            message_count: 処理したメッセージ数
            output_path: 出力ファイルパス
        """
        # バッチ処理メタデータ
        batch_metadata = {
            'PK': f"TENANT#{self.tenant_id}#BATCH",
            'SK': f"DAILY#{target_date.strftime('%Y-%m-%d')}",
            'processed_at': datetime.now().isoformat(),
            'message_count': message_count,
            'output_path': output_path,
            'status': 'completed',
            'batch_type': 'daily_message_parquet'
        }
        
        # KVMに保存
        await kvm_service.put_item(batch_metadata)


class BatchScheduler:
    """バッチ処理スケジューラー"""
    
    def __init__(self):
        self.processors = {}
        self.running = False
    
    async def start(self):
        """スケジューラー開始"""
        self.running = True
        logger.info("バッチスケジューラー開始")
        
        while self.running:
            try:
                # 現在時刻をチェック
                now = datetime.now()
                
                # 毎日午前2時に実行
                if now.hour == 2 and now.minute == 0:
                    await self._run_daily_batch()
                    
                    # 重複実行を防ぐため1分待機
                    await asyncio.sleep(60)
                
                # 1分ごとにチェック
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"スケジューラーエラー: {e}")
                await asyncio.sleep(60)
    
    async def stop(self):
        """スケジューラー停止"""
        self.running = False
        logger.info("バッチスケジューラー停止")
    
    async def _run_daily_batch(self):
        """日次バッチを実行"""
        logger.info("日次バッチ開始")
        
        # 全テナントのバッチ処理を実行
        # 実際の実装ではテナントリストをKVMから取得
        tenants = await self._get_tenant_list()
        
        tasks = []
        for tenant_id in tenants:
            processor = BatchProcessor(tenant_id)
            task = processor.process_daily_batch()
            tasks.append(task)
        
        # 並列実行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 結果を集計
        success_count = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
        error_count = sum(1 for r in results if isinstance(r, Exception) or (isinstance(r, dict) and not r.get('success')))
        
        logger.info(f"日次バッチ完了: 成功={success_count}, エラー={error_count}")
    
    async def _get_tenant_list(self) -> List[str]:
        """テナントリストを取得"""
        # 実装例：KVMからテナントリストを取得
        tenants = await kvm_service.query(pk="SYSTEM#TENANTS", sk_prefix="TENANT#")
        return [t.get('tenant_id') for t in tenants if t.get('tenant_id')]


# バッチ処理のCLI実行用
async def run_batch_for_date(date_str: str, tenant_id: str = "default_tenant"):
    """
    特定日のバッチ処理を手動実行
    
    Args:
        date_str: 処理対象日（YYYY-MM-DD形式）
        tenant_id: テナントID
    """
    target_date = datetime.strptime(date_str, "%Y-%m-%d")
    processor = BatchProcessor(tenant_id)
    result = await processor.process_daily_batch(target_date)
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # コマンドライン引数から日付を取得
        date_str = sys.argv[1]
        tenant_id = sys.argv[2] if len(sys.argv) > 2 else "default_tenant"
        
        # バッチ処理を実行
        result = asyncio.run(run_batch_for_date(date_str, tenant_id))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("使用方法: python batch_processor.py YYYY-MM-DD [tenant_id]")
        print("例: python batch_processor.py 2025-08-11 default_tenant")