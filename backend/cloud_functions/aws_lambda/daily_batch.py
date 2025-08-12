"""
AWS Lambda - 日次バッチ処理
EventBridgeで毎日午前2時に実行
"""

import json
import logging
import asyncio
import os
from datetime import datetime, timedelta
import sys

# Lambda Layerのパスを追加
sys.path.append('/opt/python')

# ローカルモジュールのインポート
from services.batch_processor import BatchProcessor

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    AWS Lambda エントリーポイント
    
    EventBridge設定:
    - スケジュール式: cron(0 17 * * ? *)  # UTC 17:00 = JST 2:00
    - または: rate(1 day)
    
    環境変数:
    - TENANT_ID: 処理対象テナント（複数の場合はカンマ区切り）
    - TARGET_DATE_OFFSET: 処理対象日のオフセット（デフォルト: -1 = 昨日）
    """
    
    logger.info(f"Lambda開始: {json.dumps(event)}")
    
    # 環境変数から設定を取得
    tenant_ids = os.environ.get('TENANT_ID', 'default_tenant').split(',')
    date_offset = int(os.environ.get('TARGET_DATE_OFFSET', '-1'))
    
    # 処理対象日を決定
    if event.get('target_date'):
        # イベントで日付が指定されている場合
        target_date = datetime.strptime(event['target_date'], '%Y-%m-%d')
    else:
        # デフォルトは昨日
        target_date = datetime.now() + timedelta(days=date_offset)
    
    logger.info(f"処理対象日: {target_date.strftime('%Y-%m-%d')}")
    logger.info(f"処理対象テナント: {tenant_ids}")
    
    # 非同期処理を実行
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    results = []
    try:
        for tenant_id in tenant_ids:
            logger.info(f"テナント {tenant_id} の処理開始")
            processor = BatchProcessor(tenant_id.strip())
            result = loop.run_until_complete(
                processor.process_daily_batch(target_date)
            )
            results.append({
                'tenant_id': tenant_id,
                'result': result
            })
            
            if result['success']:
                logger.info(
                    f"テナント {tenant_id} 処理成功: "
                    f"{result['message_count']}件のメッセージを処理"
                )
            else:
                logger.error(
                    f"テナント {tenant_id} 処理失敗: {result.get('error')}"
                )
    
    except Exception as e:
        logger.error(f"バッチ処理エラー: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'バッチ処理に失敗しました'
            }, ensure_ascii=False)
        }
    finally:
        loop.close()
    
    # 結果サマリーを作成
    success_count = sum(1 for r in results if r['result']['success'])
    error_count = len(results) - success_count
    
    response = {
        'statusCode': 200 if error_count == 0 else 207,
        'body': json.dumps({
            'message': f"バッチ処理完了: 成功={success_count}, エラー={error_count}",
            'target_date': target_date.strftime('%Y-%m-%d'),
            'results': results
        }, ensure_ascii=False, default=str)
    }
    
    logger.info(f"Lambda完了: {response}")
    return response


# ローカルテスト用
if __name__ == "__main__":
    test_event = {
        'target_date': '2025-08-11'  # テスト用の日付
    }
    test_context = {}
    
    result = lambda_handler(test_event, test_context)
    print(json.dumps(result, indent=2, ensure_ascii=False))