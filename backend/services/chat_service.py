from datetime import datetime
import uuid
from typing import List, Optional, Dict, Any
from services.message_processor import MessageProcessor
from services.kvm_service import kvm_service
from services.database import local_index_service

class ChatService:
    @staticmethod
    async def initialize_sample_data(tenant_id: str = "default_tenant", user_id: str = "default_user"):
        """サンプルデータの初期化"""
        # KVMから既存データを確認
        pk = f"TENANT#{tenant_id}#USER#{user_id}"
        existing = await kvm_service.query(pk=pk, sk_prefix="CHAT#", page_size=1)
        
        if not existing:
            # サンプルチャット1
            chat1 = await ChatService.create_chat(
                title='ミツイワ社長について',
                tenant_id=tenant_id,
                user_id=user_id
            )
            
            # サンプルメッセージ
            await ChatService.add_message(
                room_id=chat1['id'],
                role='user',
                content='ミツイワ株式会社の社長は誰ですか？',
                tenant_id=tenant_id,
                user_id=user_id
            )
            
            await ChatService.add_message(
                room_id=chat1['id'],
                role='assistant',
                content='''稲葉善典、ご質問をありがとうございます。
ミツイワ株式会社の現代表取締役社長は「高橋 洋章（たかはし ひろき）」氏です。''',
                tenant_id=tenant_id,
                user_id=user_id
            )
            
            # サンプルチャット2
            chat2 = await ChatService.create_chat(
                title='議事録まとめ',
                tenant_id=tenant_id,
                user_id=user_id
            )
            
            await ChatService.add_message(
                room_id=chat2['id'],
                role='user',
                content='本日の会議の議事録をまとめてください',
                tenant_id=tenant_id,
                user_id=user_id
            )
            
            await ChatService.add_message(
                room_id=chat2['id'],
                role='assistant',
                content='これは議事録のまとめです...',
                tenant_id=tenant_id,
                user_id=user_id
            )
            
            print("サンプルデータを初期化しました")

    @staticmethod
    async def get_all_chats(tenant_id: str = "default_tenant", user_id: str = "default_user", 
                           page_size: int = 50, last_evaluated_key: Optional[str] = None) -> Dict[str, Any]:
        """全てのチャットを取得（ページネーション対応）
        
        KVM（DynamoDB/CosmosDB）からチャットメタデータを高速取得
        カーソルベースページネーション対応
        
        Args:
            tenant_id: テナントID
            user_id: ユーザーID
            page_size: 1ページあたりの件数（デフォルト50、最大100）
            last_evaluated_key: 前回の最後のキー（カーソル）
        
        Returns:
            {
                'chats': チャットメタデータのリスト,
                'next_key': 次のページ用のキー（存在する場合）,
                'has_more': まだデータがあるかどうか
            }
        """
        # KVMからチャットルーム一覧を取得
        # PK: TENANT#{tenant_id}#USER#{user_id}
        # SK: CHAT#...
        pk = f"TENANT#{tenant_id}#USER#{user_id}"
        sk_prefix = "CHAT#"
        
        # KVMからクエリ（新しい順）
        chat_items = await kvm_service.query(
            pk=pk,
            sk_prefix=sk_prefix,
            limit=page_size,
            scan_forward=False  # 新しい順（SKの降順）
        )
        
        # チャット情報を整形
        chats = []
        for item in chat_items:
            # SKからroom_idを抽出
            room_id = item.get('SK', '').replace('CHAT#', '')
            
            chat_info = {
                'id': room_id,
                'title': item.get('title', f'Chat {room_id}'),
                'created_at': item.get('created_at', ''),
                'updated_at': item.get('updated_at', ''),
                'message_count': item.get('message_count', 0),
                'last_message': '',
                'status': item.get('status', 'active')
            }
            
            # 最終メッセージ情報があれば追加
            if 'last_message' in item and item['last_message']:
                last_msg = item['last_message']
                if isinstance(last_msg, dict):
                    # プレビューテキスト（50文字まで）
                    text = last_msg.get('text', '')
                    chat_info['last_message'] = text[:50] + '...' if len(text) > 50 else text
                    chat_info['last_message_time'] = last_msg.get('timestamp', '')
                    chat_info['last_message_role'] = last_msg.get('role', '')
                else:
                    chat_info['last_message'] = str(last_msg)
            
            # 未読数があれば追加
            if 'unread_count' in item:
                chat_info['unread_count'] = item['unread_count']
            
            chats.append(chat_info)
        
        # カーソルベースページネーションレスポンス
        return {
            'chats': chats,
            'has_more': len(chat_items) == page_size,
            'next_key': chat_items[-1].get('SK', '') if len(chat_items) == page_size and chat_items else None
        }
    
    @staticmethod
    def get_chat(room_id: str, tenant_id: str = "default_tenant", user_id: str = "default_user", page_size: int = 50):
        """特定のチャットを取得
        
        BlobStorage/S3から直接メッセージを読み込む
        
        Args:
            room_id: チャットルームID
            tenant_id: テナントID
            user_id: ユーザーID
            page_size: 1ページあたりのメッセージ数
        
        Returns:
            チャット情報とメッセージリスト
        """
        import asyncio
        import json
        from services.storage_service import storage_service
        
        # チャット基本情報（本来はDynamoDB/CosmosDBから取得）
        # TODO: メタデータストアから取得する実装に変更
        chat = {
            'id': room_id,
            'title': f'Chat {room_id}',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # BlobStorage/S3からメッセージを取得
        # プレフィックス: {tenant_id}/chat/{user_id}/{room_id}/messages/
        prefix = f"{tenant_id}/chat/{user_id}/{room_id}/messages/"
        
        # 非同期処理を同期的に実行
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # オブジェクトリストを取得
            result = loop.run_until_complete(
                storage_service.list_objects(prefix=prefix, limit=page_size*2)  # 余裕を持って取得
            )
            
            messages = []
            if result.get('success') and result.get('objects'):
                # オブジェクトを日付降順でソート（最新が先）
                sorted_objects = sorted(
                    result['objects'], 
                    key=lambda x: x['key'], 
                    reverse=True
                )[:page_size]  # 最新N件を取得
                
                # 各メッセージファイルを読み込む
                async def fetch_messages():
                    message_tasks = []
                    for obj in sorted_objects:
                        key = obj['key']
                        message_tasks.append(storage_service.get_object(key))
                    
                    # 並列で取得
                    contents = await asyncio.gather(*message_tasks, return_exceptions=True)
                    
                    parsed_messages = []
                    for i, content in enumerate(contents):
                        if isinstance(content, Exception):
                            print(f"メッセージ取得エラー: {sorted_objects[i]['key']}: {content}")
                            continue
                        if content:
                            try:
                                message = json.loads(content)
                                parsed_messages.append(message)
                            except json.JSONDecodeError as e:
                                print(f"メッセージのパースに失敗: {sorted_objects[i]['key']}: {e}")
                                continue
                    
                    return parsed_messages
                
                messages = loop.run_until_complete(fetch_messages())
                
                # タイムスタンプでソート（古い順）
                messages.sort(key=lambda x: x.get('timestamp', ''))
        
        except Exception as e:
            print(f"メッセージ取得エラー: {e}")
            messages = []
        
        finally:
            loop.close()
        
        chat['messages'] = messages
        return chat
    
    @staticmethod
    async def create_chat(title: str, tenant_id: str = "default_tenant", user_id: str = "default_user") -> Dict[str, Any]:
        """新しいチャットを作成
        
        KVMにチャットメタデータを登録
        
        Args:
            title: チャットタイトル
            tenant_id: テナントID
            user_id: ユーザーID
        
        Returns:
            作成されたチャット情報
        """
        room_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # KVMに保存するメタデータ
        chat_metadata = {
            'PK': f"TENANT#{tenant_id}#USER#{user_id}",
            'SK': f"CHAT#{room_id}",
            'title': title,
            'created_at': now,
            'updated_at': now,
            'message_count': 0,
            'status': 'active',
            'settings': {
                'system_prompt': '',
                'temperature': 0.7
            }
        }
        
        # KVMに保存
        result = await kvm_service.put_item(chat_metadata)
        
        if result['success']:
            return {
                'id': room_id,
                'title': title,
                'created_at': now,
                'updated_at': now,
                'message_count': 0,
                'status': 'active'
            }
        else:
            raise Exception(f"チャット作成失敗: {result.get('error')}")
    
    @staticmethod
    async def add_message(room_id: str, role: str, content: str, 
                         tenant_id: str = "default_tenant", user_id: str = "default_user",
                         images: Optional[List[dict]] = None, crawl_sources: Optional[List[dict]] = None):
        """メッセージを追加
        
        ⚠️ 重要: 全てのメッセージをBlobStorage/S3に保存します！
        サイズに関わらず、全てのメッセージを日付ベースディレクトリ構造で保存
        """
        import asyncio
        from services.storage_service import storage_service
        
        message_processor = MessageProcessor()
        
        # メッセージサイズを検証（上限チェックのみ）
        is_valid, content_size, error_msg = message_processor.validate_message_size(content)
        if not is_valid:
            raise ValueError(error_msg)
        
        message_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        message = {
            'id': message_id,
            'room_id': room_id,  # room_idに統一
            'role': role,
            'content': content,
            'timestamp': timestamp.isoformat()
        }
        
        # 画像がある場合は追加
        if images:
            message['images'] = images
        
        # Webクロール参照元がある場合は追加
        if crawl_sources:
            message['crawl_sources'] = crawl_sources
        
        # ⚠️ 全てのメッセージをBlobStorage/S3に保存（サイズに関わらず）
        # 日付ベースのキーを生成: user_id/room_id/yyyy/mm/dd/hh-mm-ss.sssZ-msg_id.json
        # TODO: user_idを取得する仕組みが必要
        user_id = "default_user"  # 実装時は実際のuser_idを使用
        
        # 日付ベースのパスを構築（仕様書準拠）
        # {tenant_id}/chat/{user_id}/{room_id}/messages/yyyy/mm/dd/
        date_path = timestamp.strftime("%Y/%m/%d")
        time_str = timestamp.strftime("%H-%M-%S.%f")[:-3] + "Z"
        storage_key = f"{tenant_id}/chat/{user_id}/{room_id}/messages/{date_path}/{time_str}-{message_id}.json"
        
        # 非同期処理を同期的に実行（全メッセージをBlobStorage/S3に保存）
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # メッセージの完全なデータをJSONとして保存
        import json
        message_json = json.dumps(message, ensure_ascii=False, indent=2)
        
        result = loop.run_until_complete(
            storage_service.put_object(storage_key, message_json)
        )
        loop.close()
        
        if result['success']:
            # BlobStorage/S3に正常に保存された
            print(f"メッセージを保存しました: {storage_key}")
            
            # KVMのメタデータを更新（アトミック更新）
            pk = f"TENANT#{tenant_id}#USER#{user_id}"
            sk = f"CHAT#{room_id}"
            
            # 最終メッセージプレビュー（50文字まで）
            preview_text = content[:50] + '...' if len(content) > 50 else content
            
            update_result = await kvm_service.update_item(
                pk=pk,
                sk=sk,
                updates={
                    'updated_at': timestamp.isoformat(),
                    'message_count': 1,  # インクリメント
                    'last_message': {
                        'text': preview_text,
                        'timestamp': timestamp.isoformat(),
                        'role': role
                    }
                }
            )
            
            if not update_result['success']:
                print(f"Warning: KVMメタデータ更新失敗: {update_result.get('error')}")
                # メッセージ自体は保存されているので、エラーにはしない
        else:
            # BlobStorage/S3保存失敗
            error_msg = f"BlobStorage/S3へのメッセージ保存に失敗しました: {result.get('error')}"
            print(f"Error: {error_msg}")
            raise Exception(error_msg)
        
        return message
    
    @staticmethod
    def update_message_images(message_id: str, images: List[dict]):
        """メッセージに画像を追加/更新"""
        from services.database import messages_table, MessageQuery
        
        # メッセージを検索
        messages = messages_table.search(MessageQuery.id == message_id)
        if not messages:
            return None
        
        # 画像情報を更新
        update_data = {'images': images}
        
        # 画像URLの総サイズを記録（参考情報）
        total_url_size = sum(len(img.get('url', '').encode('utf-8')) for img in images)
        update_data['images_url_size'] = total_url_size
        
        messages_table.update(
            update_data,
            MessageQuery.id == message_id
        )
        
        return True
    
    @staticmethod
    async def update_chat_title(room_id: str, title: str, tenant_id: str = "default_tenant", user_id: str = "default_user"):
        """チャットのタイトルを更新
        
        KVMのメタデータを更新
        """
        pk = f"TENANT#{tenant_id}#USER#{user_id}"
        sk = f"CHAT#{room_id}"
        
        result = await kvm_service.update_item(
            pk=pk,
            sk=sk,
            updates={
                'title': title,
                'updated_at': datetime.now().isoformat()
            }
        )
        
        return result['success']
    
    @staticmethod
    async def delete_chat(room_id: str, tenant_id: str = "default_tenant", user_id: str = "default_user"):
        """チャットを削除
        
        KVMからメタデータを削除（実データは残す場合もある）
        """
        pk = f"TENANT#{tenant_id}#USER#{user_id}"
        sk = f"CHAT#{room_id}"
        
        # KVMからメタデータを削除
        result = await kvm_service.delete_item(pk, sk)
        
        # 注意: BlobStorage/S3の実データは別途削除処理が必要
        # （アーカイブポリシーに従って処理）
        
        return result['success']