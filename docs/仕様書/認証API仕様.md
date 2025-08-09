# 認証API仕様

## 概要
MAKOTO Visual AIの認証・認可システムのAPI仕様書。AWS Cognitoを使用したマルチテナント対応の認証システムを提供する。

## 関連ドキュメント
- [型定義.md](./型定義.md) - すべてのAPIで使用される型定義の詳細

## 基本情報

### ベースURL
- 開発環境: `https://dev-api.makoto.com`
- 本番環境: `https://api.makoto.com`

### 認証方式
- Bearer Token (JWT)
- ヘッダー形式: `Authorization: Bearer {token}`

### テナント識別
- URLパス: `/tenants/{tenant_id}/...`
- ヘッダー: `X-Tenant-ID: {tenant_id}` (オプション)

### 認証モード
テナント毎に以下の認証モードを設定可能：
- `cognito`: Cognito User Pool認証（デフォルト）
- `entra_id`: Microsoft Entra ID（旧Azure AD）連携

## エンドポイント一覧

### 1. ユーザー登録

#### `POST /tenants/{tenant_id}/auth/register`

新規ユーザーを登録する。バックエンドでテナントの最大登録ユーザー数をチェックし、上限を超える場合は登録を拒否する。

**注意**: Entra ID連携テナントではこのエンドポイントは使用不可。

**型定義**: [RegisterUserRequest](./型定義.md#リクエスト) / [RegisterUserResponse](./型定義.md#レスポンス)

**リクエスト**
```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!",
  "name": "山田太郎",
  "organization_name": "株式会社サンプル"  // オプション
}
```

**パラメータ**
| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| tenant_id | string | ✓ | テナントID（URLパス） |
| email | string | ✓ | メールアドレス |
| password | string | ✓ | パスワード（8文字以上、大文字・小文字・数字・記号を含む） |
| name | string | ✓ | ユーザー名 |
| organization_name | string | - | 組織名 |

**処理フロー**
1. テナントの認証モード確認（Entra ID連携の場合は403エラー）
2. テナント設定から最大登録ユーザー数を取得
3. 現在の登録ユーザー数をカウント
4. 上限チェック
5. 上限内の場合のみユーザー登録を実行

**レスポンス**
```json
{
  "message": "登録が完了しました。メールをご確認ください。",
  "user_sub": "12345678-1234-1234-1234-123456789012"
}
```

**エラーレスポンス**
- `400 Bad Request`: メールアドレスが既に登録されている
- `400 Bad Request`: パスワードが要件を満たしていない
- `403 Forbidden`: テナントの最大ユーザー数に達しています
  ```json
  {
    "error": "USER_LIMIT_EXCEEDED",
    "message": "テナントの最大ユーザー数に達しています。管理者にお問い合わせください。",
    "details": {
      "current_users": 100,
      "max_users": 100
    }
  }
  ```
- `403 Forbidden`: Entra ID連携テナントでは使用不可
  ```json
  {
    "error": "OPERATION_NOT_ALLOWED",
    "message": "このテナントはEntra ID連携のため、ユーザー登録はできません。",
    "auth_mode": "entra_id"
  }
  ```
- `500 Internal Server Error`: サーバーエラー

### 2. ログイン

#### `POST /tenants/{tenant_id}/auth/login`

ユーザー認証を行い、JWTトークンを発行する。

**型定義**: [LoginRequest](./型定義.md#リクエスト-1) / [LoginResponse](./型定義.md#レスポンス-1)

**リクエスト**
```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!"
}
```

**パラメータ**
| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| tenant_id | string | ✓ | テナントID（URLパス） |
| email | string | ✓ | メールアドレス |
| password | string | ✓ | パスワード |

**レスポンス**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ...",
  "expires_in": 3600,
  "tenant_id": "tenant-abc-123"
}
```

**エラーレスポンス**
- `401 Unauthorized`: 認証に失敗しました
- `500 Internal Server Error`: サーバーエラー

### 3. メール確認

#### `POST /tenants/{tenant_id}/auth/confirm`

登録時に送信された確認コードを使用してメールアドレスを確認する。

**型定義**: [ConfirmEmailRequest](./型定義.md#リクエスト-2) / [ConfirmEmailResponse](./型定義.md#レスポンス-2)

**リクエスト**
```json
{
  "email": "user@example.com",
  "confirmation_code": "123456"
}
```

**パラメータ**
| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| tenant_id | string | ✓ | テナントID（URLパス） |
| email | string | ✓ | メールアドレス |
| confirmation_code | string | ✓ | 確認コード |

**レスポンス**
```json
{
  "message": "メールアドレスが確認されました。"
}
```

**エラーレスポンス**
- `400 Bad Request`: 無効な確認コード
- `404 Not Found`: ユーザーが見つからない
- `500 Internal Server Error`: サーバーエラー

### 4. 確認コード再送

#### `POST /tenants/{tenant_id}/auth/resend`

メール確認コードを再送信する。

**型定義**: [ResendConfirmationRequest](./型定義.md#リクエスト-3) / [ResendConfirmationResponse](./型定義.md#レスポンス-3)

**リクエスト**
```json
{
  "email": "user@example.com"
}
```

**パラメータ**
| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| tenant_id | string | ✓ | テナントID（URLパス） |
| email | string | ✓ | メールアドレス |

**レスポンス**
```json
{
  "message": "確認コードを再送信しました。"
}
```

**エラーレスポンス**
- `404 Not Found`: ユーザーが見つからない
- `400 Bad Request`: 既に確認済み
- `500 Internal Server Error`: サーバーエラー

### 5. トークンリフレッシュ

#### `POST /tenants/{tenant_id}/auth/refresh`

リフレッシュトークンを使用して新しいアクセストークンを取得する。

**型定義**: [RefreshTokenRequest](./型定義.md#リクエスト-4) / [RefreshTokenResponse](./型定義.md#レスポンス-4)

**リクエスト**
```json
{
  "refresh_token": "eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ..."
}
```

**パラメータ**
| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| tenant_id | string | ✓ | テナントID（URLパス） |
| refresh_token | string | ✓ | リフレッシュトークン |

**レスポンス**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ...",
  "expires_in": 3600,
  "tenant_id": "tenant-abc-123"
}
```

**エラーレスポンス**
- `401 Unauthorized`: トークンのリフレッシュに失敗しました
- `500 Internal Server Error`: サーバーエラー

### 6. ログアウト

#### `POST /tenants/{tenant_id}/auth/logout`

ユーザーをログアウトし、全てのトークンを無効化する。

**型定義**: [LogoutRequest](./型定義.md#リクエスト-5) / [LogoutResponse](./型定義.md#レスポンス-5)

**リクエスト**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**パラメータ**
| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| tenant_id | string | ✓ | テナントID（URLパス） |
| access_token | string | ✓ | アクセストークン |

**レスポンス**
```json
{
  "message": "ログアウトしました。"
}
```

**エラーレスポンス**
- `401 Unauthorized`: 無効なトークン
- `500 Internal Server Error`: サーバーエラー

### 7. ユーザー情報取得

#### `GET /tenants/{tenant_id}/auth/user`

現在ログイン中のユーザー情報を取得する。

**型定義**: [UserInfoResponse](./型定義.md#レスポンス-6)

**ヘッダー**
```
Authorization: Bearer {access_token}
```

**パラメータ**
| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| tenant_id | string | ✓ | テナントID（URLパス） |

**レスポンス**
```json
{
  "user_id": "12345678-1234-1234-1234-123456789012",
  "email": "user@example.com",
  "email_verified": true,
  "name": "山田太郎",
  "tenant_id": "tenant-abc-123",
  "role": "user",
  "organization_name": "株式会社サンプル",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

**エラーレスポンス**
- `401 Unauthorized`: 認証が必要です
- `403 Forbidden`: アクセス権限がありません
- `500 Internal Server Error`: サーバーエラー

## Entra ID連携専用エンドポイント

### 8. Entra ID同期

#### `POST /tenants/{tenant_id}/auth/entra/sync`

Entra IDからユーザー情報を同期する。このエンドポイントはEntra ID連携テナントのみ使用可能。

**注意**: このエンドポイントは管理者権限が必要。

**型定義**: [EntraSyncRequest](./型定義.md#リクエスト-7) / [EntraSyncResponse](./型定義.md#レスポンス-7)

**ヘッダー**
```
Authorization: Bearer {access_token}
X-Admin-Secret: {admin_secret}
```

**リクエスト**
```json
{
  "sync_type": "full",  // "full" | "incremental"
  "dry_run": false      // trueの場合は実行せずに同期対象を返す
}
```

**パラメータ**
| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| tenant_id | string | ✓ | テナントID（URLパス） |
| sync_type | string | ✓ | 同期タイプ（full: 全件同期、incremental: 差分同期） |
| dry_run | boolean | - | ドライラン実行（デフォルト: false） |

**レスポンス**
```json
{
  "message": "Entra ID同期が完了しました。",
  "sync_results": {
    "users_added": 5,
    "users_updated": 10,
    "users_disabled": 2,
    "total_users": 50,
    "sync_duration_ms": 3500
  }
}
```

**エラーレスポンス**
- `401 Unauthorized`: 管理者権限が必要です
- `403 Forbidden`: Cognito認証テナントでは使用不可
- `500 Internal Server Error`: サーバーエラー

### 9. Entra IDシングルサインオン（SSO）

#### `POST /tenants/{tenant_id}/auth/entra/sso`

Entra IDのSAMLトークンまたはOAuth2トークンを使用してMAKOTOのJWTトークンを取得する。

**型定義**: [EntraSSORequest](./型定義.md#リクエスト-8) / [EntraSSOResponse](./型定義.md#レスポンス-8)

**リクエスト**
```json
{
  "entra_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6...",
  "token_type": "oauth2"  // "saml" | "oauth2"
}
```

**パラメータ**
| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| tenant_id | string | ✓ | テナントID（URLパス） |
| entra_token | string | ✓ | Entra IDから取得したトークン |
| token_type | string | ✓ | トークンタイプ（saml/oauth2） |

**レスポンス**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ...",
  "expires_in": 3600,
  "tenant_id": "tenant-abc-123",
  "auth_mode": "entra_id"
}
```

**エラーレスポンス**
- `401 Unauthorized`: Entra IDトークンが無効です
- `403 Forbidden`: Cognito認証テナントでは使用不可
- `404 Not Found`: ユーザーが見つからない（同期が必要）
- `500 Internal Server Error`: サーバーエラー

### 10. Entra IDユーザー情報取得

#### `GET /tenants/{tenant_id}/auth/entra/users`

Entra IDから同期されたユーザー一覧を取得する。

**型定義**: [EntraUsersParams](./型定義.md#パラメータ-6) / [EntraUsersResponse](./型定義.md#レスポンス-9)

**ヘッダー**
```
Authorization: Bearer {access_token}
```

**パラメータ**
| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| tenant_id | string | ✓ | テナントID（URLパス） |
| limit | number | - | 取得件数（デフォルト: 20、最大: 100） |
| offset | number | - | オフセット（デフォルト: 0） |
| search | string | - | 検索キーワード（名前・メール） |

**レスポンス**
```json
{
  "users": [
    {
      "user_id": "12345678-1234-1234-1234-123456789012",
      "entra_id": "entra-user-id",
      "email": "user@company.com",
      "name": "山田太郎",
      "department": "営業部",
      "job_title": "営業課長",
      "enabled": true,
      "last_sync": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 50,
  "limit": 20,
  "offset": 0
}
```

**エラーレスポンス**
- `401 Unauthorized`: 認証が必要です
- `403 Forbidden`: Cognito認証テナントでは使用不可
- `500 Internal Server Error`: サーバーエラー

## JWTトークン構造

**型定義**: [IDToken](./型定義.md#idトークン) / [AccessToken](./型定義.md#アクセストークン)

### IDトークン
```json
{
  "sub": "12345678-1234-1234-1234-123456789012",
  "aud": "cognito-client-id",
  "iss": "https://cognito-idp.ap-northeast-1.amazonaws.com/user-pool-id",
  "exp": 1234567890,
  "iat": 1234567890,
  "auth_time": 1234567890,
  "token_use": "id",
  "email": "user@example.com",
  "email_verified": true,
  "name": "山田太郎",
  "custom:tenant_id": "tenant-abc-123",
  "custom:role": "user",
  "custom:organization_name": "株式会社サンプル",
  "cognito:groups": ["user", "tenant-abc-123"]
}
```

### アクセストークン
```json
{
  "sub": "12345678-1234-1234-1234-123456789012",
  "aud": "cognito-client-id",
  "iss": "https://cognito-idp.ap-northeast-1.amazonaws.com/user-pool-id",
  "exp": 1234567890,
  "iat": 1234567890,
  "token_use": "access",
  "scope": "openid profile email",
  "custom:tenant_id": "tenant-abc-123",
  "custom:role": "user",
  "cognito:groups": ["user", "tenant-abc-123"]
}
```

## エラーコード一覧

**型定義**: [ErrorResponse](./型定義.md#エラーレスポンス)

| コード | エラー名 | 説明 |
|--------|----------|------|
| 400 | BAD_REQUEST | リクエストが不正（パラメータエラー等） |
| 401 | UNAUTHORIZED | 認証エラー（ログインが必要） |
| 403 | FORBIDDEN | 権限エラー（アクセス権限なし） |
| 403 | USER_LIMIT_EXCEEDED | テナントの最大ユーザー数超過 |
| 403 | OPERATION_NOT_ALLOWED | Entra ID連携テナントでの操作不可 |
| 404 | NOT_FOUND | リソースが見つからない |
| 409 | CONFLICT | 競合（メールアドレス重複等） |
| 500 | INTERNAL_SERVER_ERROR | サーバーエラー |

## セキュリティ考慮事項

1. **HTTPS必須**
   - 全環境でHTTPS通信を使用
   - AWS環境ではAPI Gateway/CloudFrontで証明書管理

2. **トークン管理**
   - アクセストークン有効期限: 1時間
   - リフレッシュトークン有効期限: 30日
   - トークンはセキュアなストレージに保存

3. **パスワードポリシー**
   - 最小8文字
   - 大文字・小文字・数字・記号を含む
   - 定期的な変更を推奨

4. **レート制限**
   - ログイン試行: 5回/分
   - API呼び出し: 100回/分
   - API Gatewayでスロットリング設定

5. **AWS環境でのセキュリティ**
   - VPC内での通信
   - セキュリティグループによるアクセス制御
   - CloudTrailによる監査ログ

## 実装例

### ログイン実装例（JavaScript）
```javascript
async function login(tenantId, email, password) {
  try {
    const response = await fetch(`https://dev-api.makoto.com/tenants/${tenantId}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username: email, password })
    });

    if (!response.ok) {
      throw new Error('ログインに失敗しました');
    }

    const data = await response.json();
    
    // トークンを保存
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    localStorage.setItem('tenant_id', data.tenant_id);
    
    return data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}
```

### 認証付きAPIコール例（JavaScript）
```javascript
async function callAuthenticatedAPI(tenantId, endpoint) {
  const accessToken = localStorage.getItem('access_token');
  
  const response = await fetch(`https://dev-api.makoto.com/tenants/${tenantId}${endpoint}`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  });

  if (response.status === 401) {
    // トークンが無効な場合はリフレッシュを試みる
    await refreshToken();
    // リトライ
    return callAuthenticatedAPI(tenantId, endpoint);
  }

  return response.json();
}
```

### トークンリフレッシュ例（JavaScript）
```javascript
async function refreshToken() {
  const tenantId = localStorage.getItem('tenant_id');
  const refreshToken = localStorage.getItem('refresh_token');
  
  const response = await fetch(`https://dev-api.makoto.com/tenants/${tenantId}/auth/refresh`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ refresh_token: refreshToken })
  });

  if (!response.ok) {
    // リフレッシュ失敗時は再ログインが必要
    window.location.href = '/login';
    return;
  }

  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
}
```

## AWS環境での実装考慮事項

### API Gateway統合
- Lambda Authorizerによるトークン検証
- カスタムドメイン設定
- ステージ管理（dev/stg/prod）

### Lambda関数
- 各エンドポイントは独立したLambda関数として実装
- Lambda Layersで共通ライブラリを管理
- 環境変数でCognito設定を管理

### DynamoDB統合
- ユーザープロファイルの追加情報保存
- セッション管理
- 監査ログ保存
- テナント毎のユーザー数管理

### テナント設定管理
- AWS Secrets Managerでテナント毎の設定を管理
- **型定義**: [TenantConfig](./型定義.md#テナント設定)
- 設定例：
  ```json
  {
    "tenant_id": "tenant-abc-123",
    "auth_mode": "cognito",  // "cognito" | "entra_id"
    "max_users": 100,
    "plan": "enterprise",
    "features": {
      "max_storage_gb": 50,
      "api_rate_limit": 1000
    },
    "entra_config": {  // Entra ID連携時のみ
      "tenant_id": "microsoft-tenant-id",
      "client_id": "microsoft-app-client-id",
      "client_secret": "microsoft-app-client-secret",
      "redirect_uri": "https://dev-api.makoto.com/tenants/tenant-abc-123/auth/entra/callback"
    }
  }
  ```

## バックエンド実装例

### ユーザー登録時の上限チェック（Python/Lambda）
```python
import boto3
from fastapi import HTTPException

async def register_user(tenant_id: str, user_data: dict):
    # 1. テナント設定を取得
    secrets_client = boto3.client('secretsmanager')
    tenant_config = get_tenant_config(tenant_id)  # Secrets Managerから取得
    
    # 2. 認証モードチェック
    if tenant_config.get('auth_mode') == 'entra_id':
        raise HTTPException(
            status_code=403,
            detail={
                "error": "OPERATION_NOT_ALLOWED",
                "message": "このテナントはEntra ID連携のため、ユーザー登録はできません。",
                "auth_mode": "entra_id"
            }
        )
    
    # 3. 現在のユーザー数を取得
    cognito_client = boto3.client('cognito-idp')
    current_users = count_tenant_users(tenant_id, cognito_client)
    
    # 4. 最大ユーザー数チェック
    max_users = tenant_config.get('max_users', 10)  # デフォルト10
    if current_users >= max_users:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "USER_LIMIT_EXCEEDED",
                "message": "テナントの最大ユーザー数に達しています。管理者にお問い合わせください。",
                "details": {
                    "current_users": current_users,
                    "max_users": max_users
                }
            }
        )
    
    # 5. ユーザー登録処理
    response = cognito_client.sign_up(
        ClientId=get_client_id(tenant_id),
        Username=user_data['email'],
        Password=user_data['password'],
        UserAttributes=[
            {'Name': 'email', 'Value': user_data['email']},
            {'Name': 'name', 'Value': user_data['name']},
            {'Name': 'custom:tenant_id', 'Value': tenant_id},
            {'Name': 'custom:role', 'Value': 'user'}
        ]
    )
    
    return response

def count_tenant_users(tenant_id: str, cognito_client) -> int:
    """テナントの現在のユーザー数をカウント"""
    paginator = cognito_client.get_paginator('list_users')
    user_count = 0
    
    for page in paginator.paginate(
        UserPoolId=get_user_pool_id(tenant_id),
        Filter=f'custom:tenant_id = "{tenant_id}"'
    ):
        user_count += len(page['Users'])
    
    return user_count
```

### Entra ID同期処理例（Python/Lambda）
```python
from msgraph import GraphServiceClient
from azure.identity import ClientSecretCredential

async def sync_entra_users(tenant_id: str, sync_type: str = "full"):
    # 1. テナント設定を取得
    tenant_config = get_tenant_config(tenant_id)
    if tenant_config.get('auth_mode') != 'entra_id':
        raise HTTPException(
            status_code=403,
            detail="このテナントはEntra ID連携ではありません"
        )
    
    # 2. Entra ID設定取得
    entra_config = tenant_config.get('entra_config')
    credential = ClientSecretCredential(
        tenant_id=entra_config['tenant_id'],
        client_id=entra_config['client_id'],
        client_secret=entra_config['client_secret']
    )
    
    # 3. Microsoft Graph APIクライアント初期化
    graph_client = GraphServiceClient(
        credentials=credential,
        scopes=['https://graph.microsoft.com/.default']
    )
    
    # 4. ユーザー一覧取得
    users = await graph_client.users.get()
    
    # 5. DynamoDBに同期
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(f'makoto-{tenant_id}-users')
    
    sync_results = {
        "users_added": 0,
        "users_updated": 0,
        "users_disabled": 0
    }
    
    for user in users.value:
        # ユーザー情報をDynamoDBに保存
        item = {
            'user_id': user.id,
            'tenant_id': tenant_id,
            'email': user.mail or user.user_principal_name,
            'name': user.display_name,
            'department': user.department,
            'job_title': user.job_title,
            'enabled': user.account_enabled,
            'last_sync': datetime.utcnow().isoformat()
        }
        
        # 既存ユーザーチェック
        existing = table.get_item(Key={'user_id': user.id})
        if existing.get('Item'):
            sync_results['users_updated'] += 1
        else:
            sync_results['users_added'] += 1
            
        table.put_item(Item=item)
    
    return sync_results
```

## 更新履歴
- 2025-08-05: 初版作成（AWS開発環境を前提に作成）
- 2025-08-05: テナント毎の最大ユーザー数チェック機能を追加
- 2025-08-05: Entra ID連携機能を追加（同期、SSO、ユーザー取得）
- 2025-08-05: ユーザー登録でメールアドレスをオプションに変更、ログインでユーザー名またはメールアドレスでの認証に対応