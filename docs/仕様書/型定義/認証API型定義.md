# 認証API型定義

## 目次

1. [概要](#概要)
2. [基本認証API](#基本認証api)
   - [ユーザー登録](#ユーザー登録)
     - [RegisterUserRequest](#registeruserrequest)
     - [RegisterUserResponse](#registeruserresponse)
   - [ログイン](#ログイン)
     - [LoginRequest](#loginrequest)
     - [LoginResponse](#loginresponse)
   - [メール確認](#メール確認)
     - [ConfirmEmailRequest](#confirmemailrequest)
     - [ConfirmEmailResponse](#confirmemailresponse)
   - [確認コード再送](#確認コード再送)
     - [ResendConfirmationRequest](#resendconfirmationrequest)
     - [ResendConfirmationResponse](#resendconfirmationresponse)
   - [トークンリフレッシュ](#トークンリフレッシュ)
     - [RefreshTokenRequest](#refreshtokenrequest)
     - [RefreshTokenResponse](#refreshtokenresponse)
   - [ログアウト](#ログアウト)
     - [LogoutRequest](#logoutrequest)
     - [LogoutResponse](#logoutresponse)
   - [ユーザー情報取得](#ユーザー情報取得)
     - [UserInfoResponse](#userinforesponse)
3. [Entra ID連携API](#entra-id連携api)
   - [Entra ID同期](#entra-id同期)
     - [EntraSyncRequest](#entrasyncrequest)
     - [EntraSyncResponse](#entrasyncresponse)
   - [Entra IDシングルサインオン](#entra-idシングルサインオン)
     - [EntraSSORequest](#entrassorequest)
     - [EntraSSOResponse](#entrassoresponse)
   - [Entra IDユーザー一覧](#entra-idユーザー一覧)
     - [EntraUsersParams](#entrausersparams)
     - [EntraUsersResponse](#entrausersresponse)
     - [EntraUser](#entrauser)
4. [JWTトークン型定義](#jwtトークン型定義)
   - [IDトークン](#idトークン)
   - [アクセストークン](#アクセストークン)
5. [テナント設定型定義](#テナント設定型定義)
   - [TenantConfig](#tenantconfig)
   - [EntraConfig](#entraconfig)
   - [AuthHeaders](#authheaders)
   - [AdminHeaders](#adminheaders)
6. [更新履歴](#更新履歴)

## 概要

MAKOTO Visual AIの認証・認可システムで使用される型定義。AWS Cognitoおよび Microsoft Entra ID（旧Azure AD）連携に関する型を定義する。

## 基本認証API

### ユーザー登録

#### RegisterUserRequest
```typescript
interface RegisterUserRequest {
  email?: Email;                   // メールアドレス（オプション）
  password: string;                // パスワード（8文字以上、大文字・小文字・数字・記号を含む）
  name: string;                    // ユーザー名（必須）
  organization_name?: string;      // 組織名（オプション）
}
```

**注意事項**:
- `name`は必須項目
- `email`はオプション項目
- `email`が提供されない場合、`name`をユーザー識別子として使用
- `name`が空の場合、`email`が提供されていればそれを`name`として設定

#### RegisterUserResponse
```typescript
interface RegisterUserResponse {
  message: string;                 // 成功メッセージ
  user_sub: UUID;                  // CognitoユーザーSub（UUID形式）
}
```

### ログイン

#### LoginRequest
```typescript
interface LoginRequest {
  username: string;                // ユーザー名またはメールアドレス
  password: string;                // パスワード
}
```

**注意事項**:
- `username`にはユーザー名またはメールアドレスのいずれかを指定可能
- Entra ID連携テナントの場合は、このエンドポイントではなくSSO（`/auth/entra/sso`）を使用

#### LoginResponse
```typescript
interface LoginResponse {
  access_token: string;            // JWTアクセストークン
  id_token: string;                // JWT IDトークン
  refresh_token: string;           // リフレッシュトークン
  expires_in: number;              // 有効期限（秒単位）
  tenant_id: TenantId;             // テナントID
}
```

### メール確認

#### ConfirmEmailRequest
```typescript
interface ConfirmEmailRequest {
  email: Email;                    // メールアドレス
  confirmation_code: string;       // 確認コード（6桁の数字）
}
```

#### ConfirmEmailResponse
```typescript
interface ConfirmEmailResponse {
  message: string;                 // 成功メッセージ
}
```

### 確認コード再送

#### ResendConfirmationRequest
```typescript
interface ResendConfirmationRequest {
  email: Email;                    // メールアドレス
}
```

#### ResendConfirmationResponse
```typescript
interface ResendConfirmationResponse {
  message: string;                 // 成功メッセージ
}
```

### トークンリフレッシュ

#### RefreshTokenRequest
```typescript
interface RefreshTokenRequest {
  refresh_token: string;           // リフレッシュトークン
}
```

#### RefreshTokenResponse
```typescript
interface RefreshTokenResponse {
  access_token: string;            // 新しいJWTアクセストークン
  id_token: string;                // 新しいJWT IDトークン
  refresh_token: string;           // 新しいリフレッシュトークン
  expires_in: number;              // 有効期限（秒単位）
  tenant_id: TenantId;             // テナントID
}
```

### ログアウト

#### LogoutRequest
```typescript
interface LogoutRequest {
  access_token: string;            // アクセストークン
}
```

#### LogoutResponse
```typescript
interface LogoutResponse {
  message: string;                 // 成功メッセージ
}
```

### ユーザー情報取得

#### UserInfoResponse
```typescript
interface UserInfoResponse {
  user_id: UUID;                   // ユーザーID
  email: Email;                    // メールアドレス
  email_verified: boolean;         // メール確認済みフラグ
  name: string;                    // ユーザー名
  tenant_id: TenantId;             // テナントID
  role: UserRole;                  // ユーザーロール
  organization_name?: string;      // 組織名（オプション）
  created_at: DateTime;            // 作成日時
  updated_at: DateTime;            // 更新日時
}
```

## Entra ID連携API

### Entra ID同期

#### EntraSyncRequest
```typescript
interface EntraSyncRequest {
  sync_type: "full" | "incremental";  // 同期タイプ
  dry_run?: boolean;                  // ドライラン実行（デフォルト: false）
}
```

#### EntraSyncResponse
```typescript
interface EntraSyncResponse {
  message: string;                 // 成功メッセージ
  sync_results: {
    users_added: number;           // 追加されたユーザー数
    users_updated: number;         // 更新されたユーザー数
    users_disabled: number;        // 無効化されたユーザー数
    total_users: number;           // 総ユーザー数
    sync_duration_ms: number;      // 同期処理時間（ミリ秒）
  };
}
```

### Entra IDシングルサインオン

#### EntraSSORequest
```typescript
interface EntraSSORequest {
  entra_token: string;             // Entra IDトークン
  token_type: "saml" | "oauth2";   // トークンタイプ
}
```

#### EntraSSOResponse
```typescript
interface EntraSSOResponse {
  access_token: string;            // JWTアクセストークン
  id_token: string;                // JWT IDトークン
  refresh_token: string;           // リフレッシュトークン
  expires_in: number;              // 有効期限（秒単位）
  tenant_id: TenantId;             // テナントID
  auth_mode: "entra_id";           // 認証モード（固定値）
}
```

### Entra IDユーザー一覧

#### EntraUsersParams
```typescript
interface EntraUsersParams {
  limit?: number;                  // 取得件数（デフォルト: 20、最大: 100）
  offset?: number;                 // オフセット（デフォルト: 0）
  search?: string;                 // 検索キーワード（名前・メール）
}
```

#### EntraUsersResponse
```typescript
interface EntraUsersResponse {
  users: EntraUser[];              // ユーザー一覧
  total: number;                   // 総件数
  limit: number;                   // 取得件数
  offset: number;                  // オフセット
}
```

#### EntraUser
```typescript
interface EntraUser {
  user_id: UUID;                   // ユーザーID（内部ID）
  entra_id: string;                // Entra ID（Microsoft側のID）
  email: Email;                    // メールアドレス
  name: string;                    // ユーザー名
  department?: string;             // 部署（オプション）
  job_title?: string;              // 役職（オプション）
  enabled: boolean;                // 有効フラグ
  last_sync: DateTime;             // 最終同期日時
}
```

## JWTトークン型定義

### IDトークン

```typescript
interface IDToken {
  // 標準クレーム
  sub: UUID;                       // ユーザーID（Subject）
  aud: string;                     // オーディエンス（クライアントID）
  iss: string;                     // 発行者URL
  exp: number;                     // 有効期限（UNIXタイムスタンプ）
  iat: number;                     // 発行時刻（UNIXタイムスタンプ）
  auth_time: number;               // 認証時刻（UNIXタイムスタンプ）
  token_use: "id";                 // トークン用途（固定値）
  
  // ユーザー情報
  email: Email;                    // メールアドレス
  email_verified: boolean;         // メール確認済みフラグ
  name: string;                    // ユーザー名
  
  // カスタムクレーム
  "custom:tenant_id": TenantId;    // テナントID
  "custom:role": UserRole;         // ユーザーロール
  "custom:organization_name"?: string;  // 組織名（オプション）
  
  // グループ情報
  "cognito:groups": string[];      // Cognitoグループ
}
```

### アクセストークン

```typescript
interface AccessToken {
  // 標準クレーム
  sub: UUID;                       // ユーザーID（Subject）
  aud: string;                     // オーディエンス（クライアントID）
  iss: string;                     // 発行者URL
  exp: number;                     // 有効期限（UNIXタイムスタンプ）
  iat: number;                     // 発行時刻（UNIXタイムスタンプ）
  token_use: "access";             // トークン用途（固定値）
  scope: string;                   // スコープ（スペース区切り）
  
  // カスタムクレーム
  "custom:tenant_id": TenantId;    // テナントID
  "custom:role": UserRole;         // ユーザーロール
  
  // グループ情報
  "cognito:groups": string[];      // Cognitoグループ
}
```

## テナント設定型定義

### TenantConfig

```typescript
interface TenantConfig {
  tenant_id: TenantId;             // テナントID
  auth_mode: "cognito" | "entra_id";  // 認証モード
  max_users: number;               // 最大ユーザー数
  plan: "free" | "standard" | "enterprise";  // プラン
  features: {
    max_storage_gb: number;        // 最大ストレージ容量（GB）
    api_rate_limit: number;        // APIレート制限（リクエスト/分）
    image_generation?: boolean;    // 画像生成機能（オプション）
    audio_processing?: boolean;    // 音声処理機能（オプション）
  };
  entra_config?: EntraConfig;      // Entra ID設定（Entra ID連携時のみ）
  created_at: DateTime;            // 作成日時
  updated_at: DateTime;            // 更新日時
}
```

### EntraConfig

```typescript
interface EntraConfig {
  tenant_id: string;               // Microsoft テナントID
  client_id: string;               // アプリケーションID
  client_secret: string;           // クライアントシークレット（暗号化保存）
  redirect_uri: string;            // リダイレクトURI
  scope?: string[];                // 要求するスコープ（オプション）
}
```

### AuthHeaders

```typescript
interface AuthHeaders {
  Authorization: `Bearer ${string}`;  // Bearerトークン
  "X-Tenant-ID"?: TenantId;          // テナントID（オプション）
}
```

### AdminHeaders

```typescript
interface AdminHeaders extends AuthHeaders {
  "X-Admin-Secret": string;        // 管理者シークレット
}
```

## 更新履歴

- 2025-08-05: 初版作成（基本認証API、Entra ID連携API、JWTトークン、テナント設定の型定義）
- 2025-08-05: ユーザー登録でメールアドレスをオプションに変更、目次に型定義へのリンクを追加
- 2025-08-05: ログインでユーザー名またはメールアドレスでの認証に対応