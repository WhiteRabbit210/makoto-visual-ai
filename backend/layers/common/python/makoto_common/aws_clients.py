"""
AWSクライアント管理
AWS SDKクライアントの初期化と管理
"""

import os
from typing import Optional, Dict, Any
import boto3
from botocore.config import Config
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class AWSClientManager:
    """
    AWSクライアントマネージャー
    各種AWSサービスクライアントの作成と管理
    """
    
    def __init__(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        config: Optional[Config] = None
    ):
        """
        初期化
        
        Args:
            region: AWSリージョン
            profile: AWSプロファイル名
            endpoint_url: カスタムエンドポイントURL（ローカルテスト用）
            config: botocore設定
        """
        self.region = region or os.environ.get('AWS_DEFAULT_REGION', 'ap-northeast-1')
        self.profile = profile
        self.endpoint_url = endpoint_url
        self.config = config or Config(
            region_name=self.region,
            retries={'max_attempts': 3, 'mode': 'standard'},
            connect_timeout=5,
            read_timeout=20  # CLAUDE.mdの指定に従って20秒以内
        )
        
        # セッション作成
        self._session = self._create_session()
        
        # クライアントキャッシュ
        self._clients: Dict[str, Any] = {}
    
    def _create_session(self) -> boto3.Session:
        """
        Boto3セッションを作成
        
        Returns:
            Boto3セッション
        """
        if self.profile:
            return boto3.Session(
                profile_name=self.profile,
                region_name=self.region
            )
        else:
            return boto3.Session(region_name=self.region)
    
    def get_client(
        self,
        service_name: str,
        **kwargs
    ) -> Any:
        """
        AWSサービスクライアントを取得
        
        Args:
            service_name: サービス名（dynamodb, s3, lambda等）
            **kwargs: 追加のクライアント設定
            
        Returns:
            AWSサービスクライアント
        """
        # キャッシュキー生成
        cache_key = f"{service_name}_{hash(frozenset(kwargs.items()))}"
        
        # キャッシュ確認
        if cache_key in self._clients:
            return self._clients[cache_key]
        
        # クライアント作成パラメータ
        client_params = {
            'service_name': service_name,
            'config': self.config
        }
        
        # エンドポイントURL設定（ローカルテスト用）
        if self.endpoint_url:
            client_params['endpoint_url'] = self.endpoint_url
        
        # 追加パラメータマージ
        client_params.update(kwargs)
        
        # クライアント作成
        client = self._session.client(**client_params)
        
        # キャッシュ保存
        self._clients[cache_key] = client
        
        logger.debug(f"AWSクライアント作成: {service_name}")
        
        return client
    
    def get_resource(
        self,
        service_name: str,
        **kwargs
    ) -> Any:
        """
        AWSサービスリソースを取得
        
        Args:
            service_name: サービス名（dynamodb, s3等）
            **kwargs: 追加のリソース設定
            
        Returns:
            AWSサービスリソース
        """
        # リソース作成パラメータ
        resource_params = {
            'service_name': service_name,
            'config': self.config
        }
        
        # エンドポイントURL設定
        if self.endpoint_url:
            resource_params['endpoint_url'] = self.endpoint_url
        
        # 追加パラメータマージ
        resource_params.update(kwargs)
        
        # リソース作成
        resource = self._session.resource(**resource_params)
        
        logger.debug(f"AWSリソース作成: {service_name}")
        
        return resource
    
    # 便利メソッド群
    
    @property
    def dynamodb(self):
        """DynamoDBクライアント"""
        return self.get_client('dynamodb')
    
    @property
    def dynamodb_resource(self):
        """DynamoDBリソース"""
        return self.get_resource('dynamodb')
    
    @property
    def s3(self):
        """S3クライアント"""
        return self.get_client('s3')
    
    @property
    def s3_resource(self):
        """S3リソース"""
        return self.get_resource('s3')
    
    @property
    def lambda_client(self):
        """Lambdaクライアント"""
        return self.get_client('lambda')
    
    @property
    def sns(self):
        """SNSクライアント"""
        return self.get_client('sns')
    
    @property
    def sqs(self):
        """SQSクライアント"""
        return self.get_client('sqs')
    
    @property
    def cognito(self):
        """Cognitoクライアント"""
        return self.get_client('cognito-idp')
    
    @property
    def secrets_manager(self):
        """Secrets Managerクライアント"""
        return self.get_client('secretsmanager')
    
    @property
    def ssm(self):
        """Systems Managerクライアント"""
        return self.get_client('ssm')
    
    @property
    def cloudwatch(self):
        """CloudWatchクライアント"""
        return self.get_client('cloudwatch')
    
    @property
    def cloudwatch_logs(self):
        """CloudWatch Logsクライアント"""
        return self.get_client('logs')
    
    @property
    def eventbridge(self):
        """EventBridgeクライアント"""
        return self.get_client('events')
    
    @property
    def textract(self):
        """Textractクライアント"""
        return self.get_client('textract')
    
    @property
    def translate(self):
        """Translateクライアント"""
        return self.get_client('translate')
    
    @property
    def comprehend(self):
        """Comprehendクライアント"""
        return self.get_client('comprehend')
    
    @property
    def polly(self):
        """Pollyクライアント"""
        return self.get_client('polly')
    
    @property
    def transcribe(self):
        """Transcribeクライアント"""
        return self.get_client('transcribe')


# デフォルトマネージャー
_default_manager: Optional[AWSClientManager] = None


def get_aws_client_manager(
    region: Optional[str] = None,
    profile: Optional[str] = None,
    endpoint_url: Optional[str] = None,
    reset: bool = False
) -> AWSClientManager:
    """
    AWSクライアントマネージャーを取得
    
    Args:
        region: AWSリージョン
        profile: AWSプロファイル名
        endpoint_url: カスタムエンドポイントURL
        reset: 新しいインスタンスを強制作成
        
    Returns:
        AWSクライアントマネージャー
    """
    global _default_manager
    
    if reset or _default_manager is None:
        _default_manager = AWSClientManager(
            region=region,
            profile=profile,
            endpoint_url=endpoint_url
        )
    
    return _default_manager


# 便利関数

@lru_cache(maxsize=None)
def get_parameter(
    name: str,
    decrypt: bool = True,
    region: Optional[str] = None
) -> str:
    """
    SSMパラメータストアから値を取得
    
    Args:
        name: パラメータ名
        decrypt: 暗号化パラメータを復号化するか
        region: AWSリージョン
        
    Returns:
        パラメータ値
    """
    manager = get_aws_client_manager(region=region)
    
    response = manager.ssm.get_parameter(
        Name=name,
        WithDecryption=decrypt
    )
    
    return response['Parameter']['Value']


@lru_cache(maxsize=None)
def get_secret(
    secret_id: str,
    region: Optional[str] = None
) -> Dict[str, Any]:
    """
    Secrets Managerからシークレットを取得
    
    Args:
        secret_id: シークレットID
        region: AWSリージョン
        
    Returns:
        シークレット値
    """
    import json
    
    manager = get_aws_client_manager(region=region)
    
    response = manager.secrets_manager.get_secret_value(
        SecretId=secret_id
    )
    
    # 文字列の場合はJSONとしてパース
    if 'SecretString' in response:
        secret = response['SecretString']
        try:
            return json.loads(secret)
        except json.JSONDecodeError:
            return {'value': secret}
    else:
        # バイナリの場合
        return {'binary': response['SecretBinary']}


def put_metric(
    namespace: str,
    metric_name: str,
    value: float,
    unit: str = 'None',
    dimensions: Optional[Dict[str, str]] = None,
    region: Optional[str] = None
):
    """
    CloudWatchメトリクスを送信
    
    Args:
        namespace: メトリクス名前空間
        metric_name: メトリクス名
        value: メトリクス値
        unit: 単位
        dimensions: ディメンション
        region: AWSリージョン
    """
    manager = get_aws_client_manager(region=region)
    
    metric_data = {
        'MetricName': metric_name,
        'Value': value,
        'Unit': unit
    }
    
    if dimensions:
        metric_data['Dimensions'] = [
            {'Name': k, 'Value': v}
            for k, v in dimensions.items()
        ]
    
    manager.cloudwatch.put_metric_data(
        Namespace=namespace,
        MetricData=[metric_data]
    )
    
    logger.debug(f"メトリクス送信: {namespace}/{metric_name}={value}")


def send_notification(
    topic_arn: str,
    subject: str,
    message: str,
    attributes: Optional[Dict[str, Any]] = None,
    region: Optional[str] = None
):
    """
    SNS通知を送信
    
    Args:
        topic_arn: SNSトピックARN
        subject: 件名
        message: メッセージ
        attributes: メッセージ属性
        region: AWSリージョン
    """
    manager = get_aws_client_manager(region=region)
    
    params = {
        'TopicArn': topic_arn,
        'Subject': subject,
        'Message': message
    }
    
    if attributes:
        params['MessageAttributes'] = {
            k: {'DataType': 'String', 'StringValue': str(v)}
            for k, v in attributes.items()
        }
    
    response = manager.sns.publish(**params)
    
    logger.info(f"SNS通知送信: {topic_arn}, MessageId: {response['MessageId']}")


def invoke_lambda(
    function_name: str,
    payload: Dict[str, Any],
    invocation_type: str = 'RequestResponse',
    region: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Lambda関数を呼び出し
    
    Args:
        function_name: 関数名
        payload: ペイロード
        invocation_type: 呼び出しタイプ
        region: AWSリージョン
        
    Returns:
        レスポンス（同期呼び出しの場合）
    """
    import json
    
    manager = get_aws_client_manager(region=region)
    
    response = manager.lambda_client.invoke(
        FunctionName=function_name,
        InvocationType=invocation_type,
        Payload=json.dumps(payload)
    )
    
    if invocation_type == 'RequestResponse':
        result = json.loads(response['Payload'].read())
        logger.debug(f"Lambda呼び出し成功: {function_name}")
        return result
    
    logger.debug(f"Lambda非同期呼び出し: {function_name}")
    return None