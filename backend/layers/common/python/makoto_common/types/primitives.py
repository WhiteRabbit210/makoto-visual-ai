"""
基本型定義
プリミティブな型定義を提供
"""

from datetime import datetime
from decimal import Decimal
from typing import NewType, TypeAlias
from uuid import UUID

# 識別子型
TenantId = NewType('TenantId', str)  # テナントID (例: tenant-abc12345)
UserId = NewType('UserId', str)  # ユーザーID (UUID形式)
SessionId = NewType('SessionId', str)  # セッションID
ResourceId = NewType('ResourceId', str)  # リソースID (UUID形式)

# チャット関連
ChatId = NewType('ChatId', str)  # チャットID
MessageId = NewType('MessageId', str)  # メッセージID
AgentId = NewType('AgentId', str)  # エージェントID

# ファイル関連
FileId = NewType('FileId', str)  # ファイルID
LibraryId = NewType('LibraryId', str)  # ライブラリID

# 時刻型
Timestamp: TypeAlias = datetime  # タイムスタンプ (datetime型)
UnixTimestamp = NewType('UnixTimestamp', int)  # UNIXタイムスタンプ (秒)

# 数値型
Amount = NewType('Amount', Decimal)  # 金額 (高精度)
Percentage = NewType('Percentage', float)  # パーセンテージ (0.0-100.0)
Count = NewType('Count', int)  # カウント (非負整数)
Score = NewType('Score', float)  # スコア (0.0-1.0)

# テキスト型
Email = NewType('Email', str)  # メールアドレス
PhoneNumber = NewType('PhoneNumber', str)  # 電話番号
URL = NewType('URL', str)  # URL
JapanesePostalCode = NewType('JapanesePostalCode', str)  # 郵便番号

# サイズ・容量型
FileSize = NewType('FileSize', int)  # ファイルサイズ (バイト)
Duration = NewType('Duration', int)  # 継続時間 (秒)

# ステータス型
Status: TypeAlias = str  # ステータス文字列
ErrorCode: TypeAlias = str  # エラーコード

# メタデータ型
Metadata: TypeAlias = dict  # メタデータ辞書
Tags: TypeAlias = list  # タグリスト