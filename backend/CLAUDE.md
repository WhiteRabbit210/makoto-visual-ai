# MAKOTO Visual AI - 開発者向けガイドライン

## 📍 プロジェクト構造
```
makoto/
├── backend/          # バックエンドAPI
│   ├── api/         # APIエンドポイント
│   ├── services/    # ビジネスロジック
│   ├── tests/       # バックエンドテスト
│   └── CLAUDE.md    # このファイル
│
├── frontend/        # フロントエンドアプリ
│   ├── src/         # ソースコード
│   ├── public/      # 静的ファイル
│   └── tests/       # フロントエンドテスト
│
└── docs/           # ドキュメント・仕様書
```

## ⚠️ 重要な注意事項

### makoto_ui_referenceフォルダについて
**`makoto_ui_reference`フォルダは古いバージョンの参照用コードです。**
- 🚫 **直接使用禁止** - このフォルダのコードをそのまま使用しない
- ✅ **現在の開発** - `makoto`フォルダで実施
- 📖 **参照のみ** - 型定義やAPI設計の参考程度に留める
- 📝 **実装基準** - 必ず`makoto`側のドキュメントに準拠する
- ⚠️ **名前の由来** - 混乱を避けるため`_reference`を付けて明示的に参照用であることを示す

## テスト実行に関する重要事項

### 📁 バックエンドテスト

#### テスト実行時の必須事項
1. **必ずテストファイルを作成すること**
   - インラインコードでのテストは避ける
   - `test_*.py`の命名規則を使用
   - **必ず`tests/`フォルダに格納すること**
   - テストファイルはバージョン管理に含める

2. **テスト結果の文書化**
   - すべてのテスト結果を`tests/テスト実行結果.md`に記載
   - **テスト実行後は必ずドキュメントを更新すること**
   - 失敗したテストは問題点として冒頭に記載
   - テストファイル名を必ず明記
   - 実行日時を記録

3. **テストファイルの構成**
   ```python
   # 必須要素
   - テストの目的をdocstringで明記
   - 実行日時の記録
   - 結果のJSON形式での保存
   - サマリーの表示
   ```

4. **テストフォルダの管理ルール**
   - 場所: `/makoto/backend/tests/`
   - すべてのテスト関連ファイルをここに集約
   - テスト結果JSONファイルも同じフォルダに保存
   - `tests/README.md`にテスト一覧を維持

#### バックエンドテストファイル一覧
- `tests/test_api_functions.py` - 全API統合テスト
- `tests/test_chat_detailed.py` - チャットAPI詳細テスト
- `tests/test_agent.py` - エージェントAPIテスト
- `tests/test_crawl_performance.py` - Webクロール性能テスト
- `tests/テスト実行結果.md` - テスト結果の詳細ドキュメント

#### テスト実行コマンド
```bash
cd /home/whiterabbit/Projects/makoto_ui-1/makoto/backend
python tests/test_api_functions.py  # 全API統合テスト
```

### 📁 フロントエンドテスト

#### テスト実行時の必須事項
1. **テストファイルの配置**
   - `frontend/tests/`フォルダに格納
   - 統合テスト、コンポーネントテストを分離

2. **テスト結果の文書化**
   - `frontend/tests/フロントエンドテスト結果.md`に記載
   - ビルドエラーは必ず記録

#### フロントエンドテストファイル一覧
- `tests/test_frontend_integration.cjs` - 統合テスト
- `tests/フロントエンドテスト結果.md` - テスト結果

#### テスト実行コマンド
```bash
cd /home/whiterabbit/Projects/makoto_ui-1/makoto/frontend
node tests/test_frontend_integration.cjs  # 統合テスト
npm run lint  # Lintチェック
npm run build  # ビルドテスト
```

### 🔄 共通テストルール

1. **テスト実施後の確認**
   - バックエンド：`backend/tests/`に結果を保存
   - フロントエンド：`frontend/tests/`に結果を保存
   - 必ずドキュメントを更新

2. **テスト結果の管理**
   - JSON形式で結果を保存
   - 失敗したテストは問題点として記録
   - 実行日時を必ず記録

### テスト実行後の確認事項
1. **APIの動作確認**
   - ステータスコードの確認
   - レスポンス形式の検証
   - エラーハンドリングの確認

2. **パフォーマンス測定**
   - レスポンス時間の記録
   - 並列処理の効果測定
   - メモリ使用量の確認（必要に応じて）

## 既知の問題と対応状況

### 未解決の問題
1. **チャットメッセージ送信API** - `/api/chats/{chat_id}/messages`が404
2. **GPT-5のmax_tokensパラメータ** - `max_completion_tokens`への変更が必要
3. **チャットタイトル更新** - PUTメソッド未実装

### 解決済みの問題
1. **エージェントAPI Function Calling** - JSONモードで代替実装
2. **Webクロール高速化** - 76倍の性能改善達成
3. **型定義の統一** - backend_typesフォルダに統合

## Azure OpenAI設定

### 現在の設定（2025-08-12更新）
```env
# GPT-4.1設定（現在使用中）
AZURE_OPENAI_API_VERSION=2025-01-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1

# GPT-5設定（一時的にコメントアウト - 問題が解決次第復帰）
# AZURE_OPENAI_DEPLOYMENT_NAME=MAKOTO-gpt-5
# AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

### モデル切り替え時の注意点
- **GPT-4.1**: Function Calling対応、`max_tokens`使用
- **GPT-5**: Function Calling非対応、JSONモード使用、`max_completion_tokens`使用

### GPT-5使用時の注意点（現在無効化中）
1. Function Callingは非対応 - JSONモードを使用
2. temperatureパラメータは使用不可（デフォルト値のみ）
3. `max_tokens`ではなく`max_completion_tokens`を使用

## コード品質基準

### lintチェック
- 必ずlintチェックを通すこと（CLAUDE.mdのグローバル設定参照）
- Python: `ruff`または`flake8`を使用
- TypeScript: `eslint`を使用

### 型定義
- ドキュメント準拠の型定義を使用
- Pydantic v2を使用
- 型定義ファイルは`backend_types/`に配置

## デバッグとトラブルシューティング

### ログの確認
```bash
# APIログ
tail -f logs/API.log

# エラーログ
tail -f logs/error.log

# チャットログ
tail -f logs/chat.log
```

### よくあるエラーと対処法

1. **ModuleNotFoundError: 'types'**
   - 対処: `backend_types`を使用

2. **Azure OpenAI 400 Error**
   - 原因: パラメータの非互換
   - 対処: GPT-5用のパラメータに変更

3. **ConnectionRefused (port 8000)**
   - 原因: サーバー未起動
   - 対処: `python main.py`でサーバー起動

## パフォーマンス最適化

### Webクロール最適化設定
```python
connector = aiohttp.TCPConnector(
    limit=30,  # 同時接続数
    limit_per_host=5,  # ホストごとの接続数
    force_close=True
)
timeout = aiohttp.ClientTimeout(total=3)  # タイムアウト3秒
```

### 並列処理の活用
- `asyncio.gather()`で複数タスクを並列実行
- 要約処理のスキップオプション（`skip_summary=True`）

## セキュリティ考慮事項

### APIキーの管理
- `.env`ファイルに記載
- 絶対にコミットしない
- 環境変数から読み込む

### CORS設定
```python
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

## 今後の開発予定

### 優先度：高
1. チャットメッセージ送信APIの実装
2. GPT-5パラメータの修正

### 優先度：中
1. チャットタイトル更新機能
2. タスクテンプレートAPIの拡張

### 優先度：低
1. Pydantic警告の解消
2. WebSocket通信の最適化