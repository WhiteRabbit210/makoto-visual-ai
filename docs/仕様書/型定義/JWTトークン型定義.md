# JWTトークン型定義

## 目次

1. [概要](#概要)
2. [IDトークン](#idトークン)
   - [IDTokenPayload](#idtokenpayload)
   - [CognitoIDToken](#cognitoidtoken)
   - [EntraIDToken](#entraidtoken)
3. [アクセストークン](#アクセストークン)
   - [AccessTokenPayload](#accesstokenpayload)
   - [CognitoAccessToken](#cognitoaccesstoken)
   - [EntraAccessToken](#entraaccesstoken)
4. [リフレッシュトークン](#リフレッシュトークン)
5. [カスタムクレーム](#カスタムクレーム)
6. [トークン検証](#トークン検証)
7. [更新履歴](#更新履歴)

## 概要

MAKOTO Visual AIの認証システムで使用されるJWT（JSON Web Token）の型定義。AWS CognitoとMicrosoft Entra ID（旧Azure AD）の両方に対応。

## IDトークン

IDトークンはユーザーの身元情報を含むトークン。

### IDTokenPayload

基本的なIDトークンのペイロード構造：

```typescript
interface IDTokenPayload {
  // 標準クレーム（OpenID Connect）
  sub: string;                      // Subject - ユーザー識別子
  aud: string | string[];           // Audience - トークンの対象者
  iss: string;                      // Issuer - トークン発行者
  exp: number;                      // Expiration Time - 有効期限（Unix時間）
  iat: number;                      // Issued At - 発行時刻（Unix時間）
  auth_time?: number;               // Authentication Time - 認証時刻（Unix時間）
  nonce?: string;                   // Nonce - リプレイ攻撃防止用
  
  // ユーザー情報クレーム
  email?: string;                   // メールアドレス
  email_verified?: boolean;         // メール確認済みフラグ
  name?: string;                    // 表示名
  given_name?: string;              // 名
  family_name?: string;             // 姓
  preferred_username?: string;      // 優先ユーザー名
  
  // トークン情報
  token_use: 'id';                  // トークン用途
}
```

### CognitoIDToken

AWS Cognito用のIDトークン：

```typescript
interface CognitoIDToken extends IDTokenPayload {
  // Cognito固有フィールド
  'cognito:username': string;       // Cognitoユーザー名
  'cognito:groups'?: string[];      // 所属グループ
  
  // カスタム属性
  'custom:tenant_id': string;       // テナントID
  'custom:role': UserRole;          // ユーザーロール
  'custom:organization_name'?: string; // 組織名
  'custom:plan'?: string;           // 利用プラン
  
  // その他のCognito属性
  phone_number?: string;            // 電話番号
  phone_number_verified?: boolean;  // 電話番号確認済み
  locale?: string;                  // ロケール
  zoneinfo?: string;                // タイムゾーン
}

// ユーザーロール
type UserRole = 'admin' | 'user' | 'viewer';
```

### EntraIDToken

Microsoft Entra ID用のIDトークン：

```typescript
interface EntraIDToken extends IDTokenPayload {
  // Entra ID固有フィールド
  oid: string;                      // Object ID - Entra ID内のユーザーID
  tid: string;                      // Tenant ID - Entra IDテナントID
  ver: '1.0' | '2.0';              // トークンバージョン
  
  // ユーザー情報
  upn?: string;                     // User Principal Name
  unique_name?: string;             // 一意の名前
  
  // 組織情報
  department?: string;              // 部署
  jobTitle?: string;                // 役職
  officeLocation?: string;          // オフィス所在地
  
  // グループ・ロール
  groups?: string[];                // グループID一覧
  roles?: string[];                 // アプリケーションロール
  
  // MAKOTO固有の拡張属性
  extension_TenantId?: string;      // MAKOTOテナントID
  extension_Role?: UserRole;        // MAKOTOユーザーロール
  extension_Plan?: string;          // MAKOTO利用プラン
}
```

## アクセストークン

アクセストークンはAPIアクセス権限を証明するトークン。

### AccessTokenPayload

基本的なアクセストークンのペイロード構造：

```typescript
interface AccessTokenPayload {
  // 標準クレーム
  sub: string;                      // Subject - ユーザー識別子
  aud: string | string[];           // Audience - トークンの対象者
  iss: string;                      // Issuer - トークン発行者
  exp: number;                      // Expiration Time - 有効期限
  iat: number;                      // Issued At - 発行時刻
  jti?: string;                     // JWT ID - トークン識別子
  
  // スコープ
  scope?: string;                   // スコープ（スペース区切り）
  
  // トークン情報
  token_use: 'access';              // トークン用途
}
```

### CognitoAccessToken

AWS Cognito用のアクセストークン：

```typescript
interface CognitoAccessToken extends AccessTokenPayload {
  // Cognito固有フィールド
  client_id: string;                // クライアントID
  'cognito:groups'?: string[];      // 所属グループ
  
  // カスタム属性
  'custom:tenant_id': string;       // テナントID
  'custom:role': UserRole;          // ユーザーロール
  
  // API権限
  'custom:api_permissions'?: string[]; // API権限リスト
  'custom:rate_limit'?: number;     // APIレート制限
}
```

### EntraAccessToken

Microsoft Entra ID用のアクセストークン：

```typescript
interface EntraAccessToken extends AccessTokenPayload {
  // Entra ID固有フィールド
  appid: string;                    // Application ID
  appidacr: '0' | '1' | '2';       // Application Authentication Context Class Reference
  oid: string;                      // Object ID
  tid: string;                      // Tenant ID
  ver: '1.0' | '2.0';              // トークンバージョン
  
  // 権限
  scp?: string;                     // スコープ（委任された権限）
  roles?: string[];                 // アプリケーションロール
  
  // MAKOTO固有の拡張
  extension_TenantId?: string;      // MAKOTOテナントID
  extension_ApiPermissions?: string[]; // MAKOTO API権限
}
```

## リフレッシュトークン

リフレッシュトークンは新しいアクセストークンを取得するためのトークン。

```typescript
interface RefreshToken {
  // リフレッシュトークンは通常JWTではなく、不透明なトークン
  // Cognitoの場合、暗号化されたJWT形式
  // Entra IDの場合、不透明な文字列
  
  token: string;                    // トークン文字列
  expires_in?: number;              // 有効期限（秒）
}
```

## カスタムクレーム

MAKOTO Visual AI固有のカスタムクレーム：

```typescript
interface MAKOTOCustomClaims {
  // テナント情報
  tenant_id: string;                // テナントID
  tenant_name?: string;             // テナント名
  
  // ユーザー情報
  user_role: UserRole;              // ユーザーロール
  organization_name?: string;       // 組織名
  department?: string;              // 部署
  
  // 利用制限
  plan: 'free' | 'basic' | 'professional' | 'enterprise'; // 利用プラン
  api_rate_limit: number;           // APIレート制限（リクエスト/分）
  max_storage_gb: number;           // 最大ストレージ容量（GB）
  max_users?: number;               // 最大ユーザー数（企業プランのみ）
  
  // 機能フラグ
  features: {
    image_generation: boolean;      // 画像生成機能
    audio_processing: boolean;      // 音声処理機能
    advanced_ai: boolean;           // 高度なAI機能
    custom_model: boolean;          // カスタムモデル使用
  };
  
  // メタデータ
  created_at: string;               // アカウント作成日時（ISO 8601）
  last_login?: string;              // 最終ログイン日時（ISO 8601）
}
```

## トークン検証

### トークン検証インターフェース

```typescript
interface TokenValidationResult {
  valid: boolean;                   // 検証結果
  payload?: IDTokenPayload | AccessTokenPayload; // ペイロード
  error?: string;                   // エラーメッセージ
  expired?: boolean;                // 有効期限切れフラグ
}

interface TokenValidator {
  // トークン検証
  validate(token: string): Promise<TokenValidationResult>;
  
  // 署名検証
  verifySignature(token: string): Promise<boolean>;
  
  // 有効期限検証
  checkExpiration(payload: any): boolean;
  
  // Audience検証
  verifyAudience(payload: any, expectedAudience: string): boolean;
  
  // Issuer検証
  verifyIssuer(payload: any, expectedIssuer: string): boolean;
}
```

### 検証時の考慮事項

```typescript
interface TokenValidationConfig {
  // Cognito設定
  cognito?: {
    region: string;                 // AWSリージョン
    userPoolId: string;             // User Pool ID
    clientId: string;               // クライアントID
    jwksUri?: string;               // JWKS URI（カスタム）
  };
  
  // Entra ID設定
  entra?: {
    tenantId: string;               // Entra IDテナントID
    clientId: string;               // アプリケーションID
    issuer?: string;                // Issuer URL
    jwksUri?: string;               // JWKS URI
  };
  
  // 共通設定
  clockTolerance?: number;          // 時刻のずれ許容値（秒）
  maxTokenAge?: number;             // トークンの最大有効期間（秒）
}
```

## 更新履歴

- 2025-08-06: 初版作成
  - CognitoとEntra ID両方のトークン形式に対応
  - カスタムクレームの定義を追加
  - トークン検証インターフェースを定義