#!/usr/bin/env python3
"""
チャットAPI詳細テスト

チャットルームの作成、メッセージ送信、履歴取得など
チャット機能の包括的なテストを実行します。
"""

from fastapi.testclient import TestClient
from main import app
import json
from datetime import datetime

def test_chat_api():
    """チャットAPIの詳細テスト"""
    
    client = TestClient(app)
    
    print("=" * 60)
    print("チャットAPI詳細テスト")
    print("=" * 60)
    print()
    
    # テスト結果を記録
    test_results = {
        "実行日時": datetime.now().isoformat(),
        "テスト項目": []
    }
    
    # 1. チャット一覧取得（初期状態）
    print("【1. チャット一覧取得テスト】")
    response = client.get("/api/chats")
    print(f"ステータスコード: {response.status_code}")
    
    if response.status_code == 200:
        chats_data = response.json()
        
        # レスポンス形式の確認
        if isinstance(chats_data, dict) and "chats" in chats_data:
            chats = chats_data["chats"]
            total_count = chats_data.get("total", len(chats))
        else:
            chats = chats_data if isinstance(chats_data, list) else []
            total_count = len(chats)
        
        print(f"取得したチャット数: {total_count}")
        
        # 既存チャットの詳細表示
        for i, chat in enumerate(chats[:3]):
            print(f"\n  チャット {i+1}:")
            print(f"    - ID: {chat.get('id', 'N/A')}")
            print(f"    - タイトル: {chat.get('title', 'N/A')}")
            print(f"    - 作成日時: {chat.get('created_at', 'N/A')}")
            print(f"    - 最終更新: {chat.get('updated_at', 'N/A')}")
            print(f"    - メッセージ数: {chat.get('message_count', 0)}")
        
        test_results["テスト項目"].append({
            "項目": "チャット一覧取得",
            "結果": "成功",
            "詳細": f"{total_count}件のチャットを取得"
        })
    else:
        print(f"エラー: {response.text}")
        test_results["テスト項目"].append({
            "項目": "チャット一覧取得",
            "結果": "失敗",
            "詳細": response.text
        })
    
    print("\n" + "-" * 40 + "\n")
    
    # 2. 新規チャット作成
    print("【2. 新規チャット作成テスト】")
    create_data = {
        "message": "AIの最新技術について教えてください。特にLLMの進化について詳しく知りたいです。"
    }
    
    response = client.post("/api/chats", json=create_data)
    print(f"ステータスコード: {response.status_code}")
    
    chat_id = None
    if response.status_code == 200:
        new_chat = response.json()
        chat_id = new_chat.get("chat_id") or new_chat.get("id")
        
        print(f"\n作成されたチャット:")
        print(f"  - ID: {chat_id}")
        print(f"  - 初回メッセージ: {create_data['message'][:50]}...")
        
        # AIレスポンスの確認
        if "response" in new_chat:
            ai_response = new_chat["response"]
            if isinstance(ai_response, dict):
                print(f"  - AIレスポンス: {ai_response.get('content', 'N/A')[:100]}...")
            else:
                print(f"  - AIレスポンス: {str(ai_response)[:100]}...")
        
        test_results["テスト項目"].append({
            "項目": "新規チャット作成",
            "結果": "成功",
            "詳細": f"チャットID: {chat_id}"
        })
    else:
        print(f"エラー: {response.text}")
        test_results["テスト項目"].append({
            "項目": "新規チャット作成",
            "結果": "失敗",
            "詳細": response.text
        })
    
    print("\n" + "-" * 40 + "\n")
    
    # 3. チャット詳細取得
    if chat_id:
        print("【3. チャット詳細取得テスト】")
        response = client.get(f"/api/chats/{chat_id}")
        print(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            chat_detail = response.json()
            print(f"\nチャット詳細:")
            print(f"  - ID: {chat_detail.get('id', 'N/A')}")
            print(f"  - タイトル: {chat_detail.get('title', 'N/A')}")
            print(f"  - 作成日時: {chat_detail.get('created_at', 'N/A')}")
            
            messages = chat_detail.get("messages", [])
            print(f"  - メッセージ数: {len(messages)}")
            
            # メッセージ履歴の表示
            print("\n  メッセージ履歴:")
            for i, msg in enumerate(messages[:5]):
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                timestamp = msg.get("timestamp", "")
                
                content_preview = content[:80] if len(content) > 80 else content
                print(f"    [{i+1}] {role}: {content_preview}...")
                if timestamp:
                    print(f"        時刻: {timestamp}")
            
            test_results["テスト項目"].append({
                "項目": "チャット詳細取得",
                "結果": "成功",
                "詳細": f"メッセージ数: {len(messages)}"
            })
        else:
            print(f"エラー: {response.text}")
            test_results["テスト項目"].append({
                "項目": "チャット詳細取得",
                "結果": "失敗",
                "詳細": response.text
            })
        
        print("\n" + "-" * 40 + "\n")
        
        # 4. メッセージ送信テスト
        print("【4. メッセージ送信テスト】")
        
        # 複数のメッセージを送信
        test_messages = [
            "GPT-4とGPT-5の違いは何ですか？",
            "Function Callingについて説明してください",
            "MAKOTOシステムの特徴を教えてください"
        ]
        
        for i, message in enumerate(test_messages):
            print(f"\nメッセージ {i+1}: {message}")
            
            message_data = {"message": message}
            response = client.post(f"/api/chats/{chat_id}/messages", json=message_data)
            
            if response.status_code == 200:
                msg_response = response.json()
                
                # レスポンスの内容を確認
                if "response" in msg_response:
                    ai_content = msg_response["response"]
                    if isinstance(ai_content, dict):
                        ai_text = ai_content.get("content", "N/A")
                    else:
                        ai_text = str(ai_content)
                    print(f"  AIレスポンス: {ai_text[:100]}...")
                
                test_results["テスト項目"].append({
                    "項目": f"メッセージ送信 {i+1}",
                    "結果": "成功",
                    "詳細": message[:30]
                })
            else:
                print(f"  エラー: {response.status_code}")
                test_results["テスト項目"].append({
                    "項目": f"メッセージ送信 {i+1}",
                    "結果": "失敗",
                    "詳細": f"ステータス: {response.status_code}"
                })
        
        print("\n" + "-" * 40 + "\n")
        
        # 5. メッセージ履歴の再取得
        print("【5. メッセージ履歴再取得テスト】")
        response = client.get(f"/api/chats/{chat_id}")
        
        if response.status_code == 200:
            updated_chat = response.json()
            messages = updated_chat.get("messages", [])
            print(f"更新後のメッセージ数: {len(messages)}")
            
            # 最新のメッセージを表示
            print("\n最新5件のメッセージ:")
            for msg in messages[-5:]:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")[:60]
                print(f"  [{role}]: {content}...")
            
            test_results["テスト項目"].append({
                "項目": "メッセージ履歴再取得",
                "結果": "成功",
                "詳細": f"総メッセージ数: {len(messages)}"
            })
        
        print("\n" + "-" * 40 + "\n")
        
        # 6. チャットタイトル更新テスト
        print("【6. チャットタイトル更新テスト】")
        update_data = {"title": "AI技術についての議論 - 更新済み"}
        response = client.put(f"/api/chats/{chat_id}", json=update_data)
        
        if response.status_code == 200:
            updated = response.json()
            print(f"更新後のタイトル: {updated.get('title', 'N/A')}")
            test_results["テスト項目"].append({
                "項目": "チャットタイトル更新",
                "結果": "成功",
                "詳細": update_data["title"]
            })
        else:
            print(f"更新失敗: ステータス {response.status_code}")
            test_results["テスト項目"].append({
                "項目": "チャットタイトル更新",
                "結果": "失敗または未実装",
                "詳細": f"ステータス: {response.status_code}"
            })
    
    # 7. 複数チャット作成テスト
    print("【7. 複数チャット作成テスト】")
    created_chats = []
    
    test_topics = [
        "Pythonプログラミングについて教えてください",
        "機械学習の基礎を説明してください",
        "Webアプリケーション開発のベストプラクティスは？"
    ]
    
    for i, topic in enumerate(test_topics):
        response = client.post("/api/chats", json={"message": topic})
        if response.status_code == 200:
            chat = response.json()
            chat_id = chat.get("chat_id") or chat.get("id")
            created_chats.append(chat_id)
            print(f"  作成 {i+1}: チャットID {chat_id[:8]}... - {topic[:30]}...")
    
    test_results["テスト項目"].append({
        "項目": "複数チャット作成",
        "結果": "成功",
        "詳細": f"{len(created_chats)}件のチャットを作成"
    })
    
    print("\n" + "-" * 40 + "\n")
    
    # 8. 最終的なチャット一覧確認
    print("【8. 最終チャット一覧確認】")
    response = client.get("/api/chats")
    
    if response.status_code == 200:
        final_data = response.json()
        
        if isinstance(final_data, dict) and "chats" in final_data:
            final_chats = final_data["chats"]
            final_count = final_data.get("total", len(final_chats))
        else:
            final_chats = final_data if isinstance(final_data, list) else []
            final_count = len(final_chats)
        
        print(f"総チャット数: {final_count}")
        print("\n最新5件のチャット:")
        for chat in final_chats[:5]:
            title = chat.get("title", "無題")[:40]
            chat_id = chat.get("id", "N/A")
            created = chat.get("created_at", "N/A")
            print(f"  - {title}... (ID: {chat_id[:8]}...)")
        
        test_results["テスト項目"].append({
            "項目": "最終チャット一覧",
            "結果": "成功",
            "詳細": f"総数: {final_count}件"
        })
    
    # テスト結果のサマリー
    print("\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)
    
    success_count = sum(1 for item in test_results["テスト項目"] if item["結果"] == "成功")
    total_count = len(test_results["テスト項目"])
    
    print(f"成功: {success_count}/{total_count}")
    print("\n詳細:")
    for item in test_results["テスト項目"]:
        status = "✅" if item["結果"] == "成功" else "❌"
        print(f"  {status} {item['項目']}: {item['詳細']}")
    
    # 結果をファイルに保存
    with open("test_chat_results.json", "w", encoding="utf-8") as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    
    print(f"\nテスト結果を test_chat_results.json に保存しました")
    
    return test_results

if __name__ == "__main__":
    test_chat_api()