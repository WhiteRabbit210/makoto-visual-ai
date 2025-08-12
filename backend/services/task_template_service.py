from datetime import datetime
import uuid
from typing import List, Optional
from services.database import task_templates_table, TaskQuery


class TaskTemplateService:
    @staticmethod
    def initialize_default_templates():
        """デフォルトのタスクテンプレートを初期化"""
        if len(task_templates_table.all()) == 0:
            templates = [
                {
                    'id': 'meeting-minutes',
                    'name': '議事録の作成',
                    'description': '会議の内容を整理し、議事録として文書化します',
                    'prompt': '''以下の会議内容から議事録を作成してください。

【議事録に含める内容】
1. 会議の基本情報（日時、場所、参加者）
2. 議題と協議内容
3. 決定事項
4. アクションアイテム（担当者と期限を含む）
5. 次回の予定

【形式】
- 簡潔で読みやすい箇条書き形式
- 重要な決定事項は強調表示
- アクションアイテムは表形式で整理''',
                    'category': '作成'
                },
                {
                    'id': 'summary',
                    'name': '要約・サマリー作成',
                    'description': '長文や複雑な内容を簡潔にまとめます',
                    'prompt': '''以下の内容を要約してください。

【要約の要件】
1. 元の内容の10-20%程度の長さにまとめる
2. 重要なポイントを漏らさない
3. 論理的な構成で整理する
4. 専門用語は必要に応じて説明を追加

【含めるべき内容】
- 主要なトピック
- 重要な結論や発見
- 今後のアクションや推奨事項''',
                    'category': '作成'
                },
                {
                    'id': 'report',
                    'name': 'レポート作成',
                    'description': '調査結果や分析内容をレポート形式でまとめます',
                    'prompt': '''以下の情報を基にレポートを作成してください。

【レポートの構成】
1. エグゼクティブサマリー
2. 背景と目的
3. 調査・分析方法
4. 結果と発見事項
5. 考察と洞察
6. 結論と推奨事項
7. 参考資料（必要に応じて）

【作成時の注意点】
- データに基づいた客観的な記述
- 図表を用いた視覚的な説明の提案
- 読み手を意識した構成''',
                    'category': '作成'
                },
                {
                    'id': 'translation',
                    'name': '翻訳',
                    'description': 'テキストを他の言語に翻訳します',
                    'prompt': '''以下のテキストを指定された言語に翻訳してください。

【翻訳の要件】
1. 正確性：原文の意味を正確に伝える
2. 自然さ：ターゲット言語として自然な表現を使用
3. 文脈考慮：文脈に応じた適切な訳語選択
4. 専門用語：分野に応じた適切な専門用語の使用

【翻訳時の注意点】
- 文化的な違いを考慮
- 必要に応じて注釈を追加
- フォーマルレベルを原文に合わせる''',
                    'category': '作成'
                },
                {
                    'id': 'analysis',
                    'name': '分析・調査',
                    'description': 'データや情報を分析し、洞察を導き出します',
                    'prompt': '''以下のデータ・情報を分析してください。

【分析の観点】
1. データの概要と特徴
2. パターンやトレンドの発見
3. 異常値や特異点の特定
4. 相関関係の分析
5. 因果関係の推測（可能な範囲で）

【分析結果の提示】
- 主要な発見事項を箇条書きで整理
- 数値データは可能な限り具体的に提示
- 視覚化の提案（グラフやチャートの種類）
- 制限事項や注意点の明記''',
                    'category': '分析'
                },
                {
                    'id': 'qa',
                    'name': '質問応答',
                    'description': '質問に対して適切な回答を提供します',
                    'prompt': '''以下の質問に回答してください。

【回答の指針】
1. 正確性：事実に基づいた正確な情報提供
2. 完全性：質問の全ての側面に対応
3. 明確性：分かりやすい説明
4. 構造化：論理的な順序で情報を整理

【回答形式】
- 直接的な回答を最初に提示
- 必要に応じて背景情報を追加
- 複雑な内容は段階的に説明
- 参考情報やソースがあれば明記''',
                    'category': '分析'
                },
                {
                    'id': 'creative-writing',
                    'name': 'クリエイティブライティング',
                    'description': '創造的な文章やコンテンツを作成します',
                    'prompt': '''以下の要件に基づいてクリエイティブな文章を作成してください。

【作成の指針】
1. 独創性：オリジナルで魅力的な内容
2. 読者意識：ターゲット読者に合わせた表現
3. 感情喚起：読者の感情に訴える要素
4. 構成：起承転結など効果的な構成

【考慮事項】
- トーンとスタイルの一貫性
- 比喩や修辞技法の効果的な使用
- リズムと読みやすさのバランス
- メッセージの明確な伝達''',
                    'category': 'その他'
                },
                {
                    'id': 'code-review',
                    'name': 'コード生成・レビュー',
                    'description': 'プログラムコードの生成や既存コードのレビューを行います',
                    'prompt': '''以下の要件に基づいてコードを生成/レビューしてください。

【コード生成の場合】
1. 要件の明確化と確認
2. 適切な言語/フレームワークの選択理由
3. クリーンで保守性の高いコード
4. エラーハンドリングの実装
5. コメントとドキュメンテーション

【コードレビューの場合】
1. コードの品質評価
2. パフォーマンスの観点
3. セキュリティの懸念事項
4. 保守性と可読性
5. ベストプラクティスへの準拠
6. 改善提案とその理由''',
                    'category': 'その他'
                }
            ]
            
            for template in templates:
                template['created_at'] = datetime.now().isoformat()
                template['updated_at'] = datetime.now().isoformat()
                task_templates_table.insert(template)
    
    @staticmethod
    def get_all_templates() -> List[dict]:
        """全てのタスクテンプレートを取得"""
        return sorted(task_templates_table.all(), key=lambda x: x.get('category', ''))
    
    @staticmethod
    def get_template_by_id(template_id: str) -> Optional[dict]:
        """特定のタスクテンプレートを取得"""
        templates = task_templates_table.search(TaskQuery.id == template_id)
        return templates[0] if templates else None
    
    @staticmethod
    def get_templates_by_category(category: str) -> List[dict]:
        """カテゴリー別にタスクテンプレートを取得"""
        return task_templates_table.search(TaskQuery.category == category)