# テストディレクトリ

## 📁 フォルダ構成

```
tests/
├── README.md                    # このファイル
├── __init__.py                  # Pythonパッケージ初期化
├── テスト実行結果.md            # 全テスト結果の詳細ドキュメント
├── test_chat_results.json      # チャットAPIテスト結果（自動生成）
│
├── test_api_functions.py       # 全API統合テスト
├── test_chat_detailed.py       # チャットAPI詳細テスト
├── test_agent.py               # エージェントAPIテスト
├── test_crawl_performance.py   # Webクロール性能テスト
├── test_simple_gpt5.py         # GPT-5基本動作テスト
└── test_gpt5_debug.py          # GPT-5デバッグテスト
```

## 🚀 テスト実行方法

### 全テストを実行
```bash
cd /home/whiterabbit/Projects/makoto_ui-1/makoto/backend
python tests/test_api_functions.py
```

### 個別テストを実行
```bash
# チャットAPI詳細テスト
python tests/test_chat_detailed.py

# エージェントAPIテスト
python tests/test_agent.py

# Webクロール性能テスト
python tests/test_crawl_performance.py
```

## 📊 テスト結果

最新のテスト結果は `テスト実行結果.md` を参照してください。

### 現在のテスト状況（2025-08-12）

| テスト項目 | ステータス | 備考 |
|----------|----------|------|
| ヘルスチェック | ✅ | 正常動作 |
| チャットAPI | ⚠️ | 6/10項目成功（メッセージ送信API未実装） |
| ライブラリAPI | ✅ | 全機能正常動作 |
| タスクAPI | ✅ | 全機能正常動作 |
| WebクロールAPI | ✅ | 76倍高速化達成 |
| エージェントAPI | ✅ | GPT-4.1で正常動作 |
| 設定API | ✅ | 正常動作 |

## ⚠️ 既知の問題

### 優先度：高
1. **チャットメッセージ送信API** (`/api/chats/{chat_id}/messages`)
   - 404 Not Found
   - エンドポイント未実装

### 優先度：中
1. **チャットタイトル更新** (`PUT /api/chats/{chat_id}`)
   - 405 Method Not Allowed
   - PUTメソッド未実装

### 優先度：低
1. **Pydantic警告**
   - `model_settings`の名前空間競合
   - 動作に影響なし

## 🔧 テスト環境設定

### Azure OpenAI（現在GPT-4.1使用中）
```env
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1
AZURE_OPENAI_API_VERSION=2025-01-01-preview
```

### テスト実行前の確認事項
1. `.env`ファイルの設定確認
2. 仮想環境の有効化
3. 依存パッケージのインストール

```bash
# 仮想環境有効化
source /home/whiterabbit/makoto-venv/bin/activate

# 依存パッケージ確認
pip list | grep -E "fastapi|openai|pytest"
```

## 📝 新しいテストの追加

新しいテストファイルを作成する場合：

1. `test_`プレフィックスを使用
2. docstringでテストの目的を明記
3. 結果をJSONファイルに保存
4. テスト結果を`テスト実行結果.md`に追記

例：
```python
#!/usr/bin/env python3
"""
新機能のテスト

テストの目的と対象を記載
"""

def test_new_feature():
    # テスト実装
    pass

if __name__ == "__main__":
    test_new_feature()
```