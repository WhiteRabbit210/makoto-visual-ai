"""
Azure Functions - 日次バッチ処理
Timer Triggerで毎日午前2時に実行
"""

import logging
import json
import asyncio
import os
from datetime import datetime, timedelta
import azure.functions as func
import sys

# Azure Functionsのパスを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.batch_processor import BatchProcessor


def main(mytimer: func.TimerRequest) -> str:
    """
    Azure Functions エントリーポイント
    
    function.json設定:
    {
      "schedule": "0 0 2 * * *"  // 毎日午前2時（現地時間）
    }
    
    環境変数（Application Settings）:
    - TENANT_ID: 処理対象テナント（複数の場合はカンマ区切り）
    - TARGET_DATE_OFFSET: 処理対象日のオフセット（デフォルト: -1 = 昨日）
    """
    
    utc_timestamp = datetime.utcnow().isoformat()
    
    if mytimer.past_due:
        logging.warning('タイマーが遅延実行されています')
    
    logging.info(f'日次バッチ処理開始: {utc_timestamp}')
    
    # 環境変数から設定を取得
    tenant_ids = os.environ.get('TENANT_ID', 'default_tenant').split(',')
    date_offset = int(os.environ.get('TARGET_DATE_OFFSET', '-1'))
    
    # 処理対象日（デフォルトは昨日）
    target_date = datetime.now() + timedelta(days=date_offset)
    
    logging.info(f"処理対象日: {target_date.strftime('%Y-%m-%d')}")
    logging.info(f"処理対象テナント: {tenant_ids}")
    
    # 非同期処理を実行
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    results = []
    try:
        for tenant_id in tenant_ids:
            logging.info(f"テナント {tenant_id} の処理開始")
            processor = BatchProcessor(tenant_id.strip())
            result = loop.run_until_complete(
                processor.process_daily_batch(target_date)
            )
            results.append({
                'tenant_id': tenant_id,
                'result': result
            })
            
            if result['success']:
                logging.info(
                    f"テナント {tenant_id} 処理成功: "
                    f"{result['message_count']}件のメッセージを処理, "
                    f"出力: {result['output_path']}"
                )
            else:
                logging.error(
                    f"テナント {tenant_id} 処理失敗: {result.get('error')}"
                )
    
    except Exception as e:
        logging.error(f"バッチ処理エラー: {str(e)}")
        return json.dumps({
            'status': 'error',
            'message': str(e),
            'timestamp': utc_timestamp
        }, ensure_ascii=False)
    
    finally:
        loop.close()
    
    # 結果サマリー
    success_count = sum(1 for r in results if r['result']['success'])
    error_count = len(results) - success_count
    
    response = {
        'status': 'success' if error_count == 0 else 'partial',
        'message': f"バッチ処理完了: 成功={success_count}, エラー={error_count}",
        'target_date': target_date.strftime('%Y-%m-%d'),
        'timestamp': utc_timestamp,
        'results': results
    }
    
    logging.info(f"処理完了: {response['message']}")
    
    return json.dumps(response, ensure_ascii=False, default=str)