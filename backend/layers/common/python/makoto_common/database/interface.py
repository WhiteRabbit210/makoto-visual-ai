"""
データベースインターフェース
マルチクラウド対応のデータベース抽象化
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, AsyncIterator

from ..types.primitives import TenantId
from ..tenant.context import require_tenant_context


class ConsistencyLevel(Enum):
    """一貫性レベル"""
    EVENTUAL = "eventual"  # 結果的一貫性
    STRONG = "strong"  # 強一貫性
    SESSION = "session"  # セッション一貫性


class OperationType(Enum):
    """操作タイプ"""
    PUT = "put"  # 挿入/更新
    UPDATE = "update"  # 更新
    DELETE = "delete"  # 削除
    CONDITION_CHECK = "condition_check"  # 条件チェック


@dataclass
class QueryResult:
    """
    クエリ結果
    ページネーション情報を含む
    """
    items: List[Dict[str, Any]]  # 結果アイテム
    last_evaluated_key: Optional[Dict[str, Any]] = None  # 次ページのキー
    count: int = 0  # 取得件数
    scanned_count: int = 0  # スキャン件数
    consumed_capacity: Optional[Dict[str, Any]] = None  # 消費キャパシティ
    
    def __post_init__(self):
        """カウントの自動設定"""
        if self.count == 0:
            self.count = len(self.items)
        if self.scanned_count == 0:
            self.scanned_count = self.count
    
    @property
    def has_more(self) -> bool:
        """次ページがあるか"""
        return self.last_evaluated_key is not None


@dataclass
class TransactionItem:
    """
    トランザクションアイテム
    トランザクション内の単一操作
    """
    operation: OperationType  # 操作タイプ
    table_name: str  # テーブル名
    key: Dict[str, Any]  # キー
    item: Optional[Dict[str, Any]] = None  # アイテム（PUT時）
    update_expression: Optional[str] = None  # 更新式（UPDATE時）
    expression_values: Optional[Dict[str, Any]] = None  # 式の値
    condition_expression: Optional[str] = None  # 条件式
    return_values: str = "NONE"  # 戻り値設定


@dataclass
class BatchWriteRequest:
    """
    バッチ書き込みリクエスト
    複数アイテムの一括操作
    """
    table_name: str  # テーブル名
    put_requests: List[Dict[str, Any]] = field(default_factory=list)  # PUTリクエスト
    delete_requests: List[Dict[str, Any]] = field(default_factory=list)  # DELETEリクエスト
    
    @property
    def total_requests(self) -> int:
        """総リクエスト数"""
        return len(self.put_requests) + len(self.delete_requests)


class DatabaseInterface(ABC):
    """
    データベース操作の基本インターフェース
    テナント完全分離を保証
    """
    
    def __init__(self, tenant_id: Optional[TenantId] = None):
        """
        初期化
        
        Args:
            tenant_id: テナントID（オプション、コンテキストから取得も可）
        """
        self.tenant_id = tenant_id
    
    def _get_tenant_id(self) -> TenantId:
        """
        テナントIDを取得
        コンテキストまたは初期化時の値から取得
        
        Returns:
            テナントID
            
        Raises:
            RuntimeError: テナントIDが設定されていない場合
        """
        if self.tenant_id:
            return self.tenant_id
        
        # コンテキストから取得
        context = require_tenant_context()
        return context.tenant_id
    
    def _get_table_name(self, base_name: str) -> str:
        """
        テナント別テーブル名を取得
        
        Args:
            base_name: 基本テーブル名
            
        Returns:
            テナント固有のテーブル名
        """
        tenant_id = self._get_tenant_id()
        return f"{tenant_id}-{base_name}"
    
    @abstractmethod
    async def get_item(
        self,
        table_name: str,
        key: Dict[str, Any],
        consistent_read: bool = False,
        projection_expression: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        単一アイテムの取得
        
        Args:
            table_name: テーブル名（ベース名）
            key: プライマリキー
            consistent_read: 強一貫性読み取り
            projection_expression: 取得属性の指定
            
        Returns:
            アイテム（存在しない場合None）
        """
        pass
    
    @abstractmethod
    async def put_item(
        self,
        table_name: str,
        item: Dict[str, Any],
        condition_expression: Optional[str] = None,
        expression_values: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        アイテムの保存
        
        Args:
            table_name: テーブル名（ベース名）
            item: 保存するアイテム
            condition_expression: 条件式
            expression_values: 式の値
        """
        pass
    
    @abstractmethod
    async def update_item(
        self,
        table_name: str,
        key: Dict[str, Any],
        update_expression: str,
        expression_values: Dict[str, Any],
        condition_expression: Optional[str] = None,
        return_values: str = "UPDATED_NEW"
    ) -> Dict[str, Any]:
        """
        アイテムの更新
        
        Args:
            table_name: テーブル名（ベース名）
            key: プライマリキー
            update_expression: 更新式
            expression_values: 式の値
            condition_expression: 条件式
            return_values: 戻り値設定
            
        Returns:
            更新後の属性
        """
        pass
    
    @abstractmethod
    async def delete_item(
        self,
        table_name: str,
        key: Dict[str, Any],
        condition_expression: Optional[str] = None,
        expression_values: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        アイテムの削除
        
        Args:
            table_name: テーブル名（ベース名）
            key: プライマリキー
            condition_expression: 条件式
            expression_values: 式の値
        """
        pass
    
    @abstractmethod
    async def query(
        self,
        table_name: str,
        key_condition: str,
        expression_values: Dict[str, Any],
        index_name: Optional[str] = None,
        limit: Optional[int] = None,
        scan_forward: bool = True,
        projection_expression: Optional[str] = None,
        filter_expression: Optional[str] = None,
        exclusive_start_key: Optional[Dict[str, Any]] = None,
        consistent_read: bool = False
    ) -> QueryResult:
        """
        条件に基づくクエリ
        
        Args:
            table_name: テーブル名（ベース名）
            key_condition: キー条件式
            expression_values: 式の値
            index_name: インデックス名
            limit: 取得件数制限
            scan_forward: ソート順（True: 昇順）
            projection_expression: 取得属性の指定
            filter_expression: フィルタ式
            exclusive_start_key: 開始キー
            consistent_read: 強一貫性読み取り
            
        Returns:
            クエリ結果
        """
        pass
    
    @abstractmethod
    async def scan(
        self,
        table_name: str,
        filter_expression: Optional[str] = None,
        expression_values: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        projection_expression: Optional[str] = None,
        exclusive_start_key: Optional[Dict[str, Any]] = None,
        consistent_read: bool = False,
        index_name: Optional[str] = None
    ) -> QueryResult:
        """
        テーブルスキャン
        
        Args:
            table_name: テーブル名（ベース名）
            filter_expression: フィルタ式
            expression_values: 式の値
            limit: 取得件数制限
            projection_expression: 取得属性の指定
            exclusive_start_key: 開始キー
            consistent_read: 強一貫性読み取り
            index_name: インデックス名
            
        Returns:
            スキャン結果
        """
        pass
    
    @abstractmethod
    async def batch_write(
        self,
        requests: List[BatchWriteRequest]
    ) -> Dict[str, Any]:
        """
        バッチ書き込み
        
        Args:
            requests: バッチリクエストリスト
            
        Returns:
            未処理アイテム情報
        """
        pass
    
    @abstractmethod
    async def batch_get(
        self,
        table_name: str,
        keys: List[Dict[str, Any]],
        projection_expression: Optional[str] = None,
        consistent_read: bool = False
    ) -> List[Dict[str, Any]]:
        """
        バッチ読み込み
        
        Args:
            table_name: テーブル名（ベース名）
            keys: キーリスト
            projection_expression: 取得属性の指定
            consistent_read: 強一貫性読み取り
            
        Returns:
            アイテムリスト
        """
        pass
    
    @abstractmethod
    async def transaction_write(
        self,
        transactions: List[TransactionItem]
    ) -> None:
        """
        トランザクション書き込み
        
        Args:
            transactions: トランザクションアイテムリスト
        """
        pass
    
    @abstractmethod
    async def create_table(
        self,
        table_name: str,
        key_schema: List[Dict[str, str]],
        attribute_definitions: List[Dict[str, str]],
        billing_mode: str = "PAY_PER_REQUEST",
        global_secondary_indexes: Optional[List[Dict[str, Any]]] = None,
        stream_specification: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        テーブルの作成
        
        Args:
            table_name: テーブル名（ベース名）
            key_schema: キースキーマ
            attribute_definitions: 属性定義
            billing_mode: 課金モード
            global_secondary_indexes: グローバルセカンダリインデックス
            stream_specification: ストリーム設定
        """
        pass
    
    @abstractmethod
    async def delete_table(
        self,
        table_name: str
    ) -> None:
        """
        テーブルの削除
        
        Args:
            table_name: テーブル名（ベース名）
        """
        pass
    
    @abstractmethod
    async def describe_table(
        self,
        table_name: str
    ) -> Dict[str, Any]:
        """
        テーブル情報の取得
        
        Args:
            table_name: テーブル名（ベース名）
            
        Returns:
            テーブル情報
        """
        pass