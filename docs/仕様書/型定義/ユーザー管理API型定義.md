# ユーザー管理API型定義

## 目次
- [概要](#概要)
- [基本型定義](#基本型定義)
  - [User](#user)
  - [UserProfile](#userprofile)
  - [UserCredentials](#usercredentials)
  - [UserStatus](#userstatus)
- [認証・認可](#認証・認可)
  - [CognitoAuthentication](#cognitoauthentication)
  - [CognitoAuthenticationRequest](#cognitoauthenticationrequest)
  - [CognitoAuthenticationResponse](#cognitoauthenticationresponse)
  - [CognitoTokens](#cognitotokens)
  - [CognitoUserPoolOperations](#cognitouserpooloperations)
  - [CognitoAdminOperations](#cognitoadminoperations)
  - [CognitoGroup](#cognitogroup)
  - [CognitoUserImport](#cognitouserimport)
  - [EntraIDConfiguration](#entraidconfiguration)
  - [EntraIDToken](#entraidtoken)
  - [EntraIDUser](#entraiduser)
  - [EntraIDGroup](#entraidgroup)
  - [EntraIDAuthenticationRequest](#entraidauthenticationrequest)
  - [EntraIDAuthenticationResponse](#entraidauthenticationresponse)
  - [EntraIDSyncConfiguration](#entraidsyncconfiguration)
  - [CognitoEntraIDIntegration](#cognitoentriadintegration)
  - [AuthenticationRequest](#authenticationrequest)
  - [AuthenticationResponse](#authenticationresponse)
  - [AuthorizationCheck](#authorizationcheck)
  - [OAuth2Integration](#oauth2integration)
  - [SAMLAssertion](#samlassertion)
  - [MultiFactorAuth](#multifactorauth)
- [権限管理](#権限管理)
  - [Role](#role)
  - [Permission](#permission)
  - [PolicyDocument](#policydocument)
  - [AccessControl](#accesscontrol)
  - [ResourcePermission](#resourcepermission)
- [組織・グループ管理](#組織・グループ管理)
  - [Organization](#organization)
  - [Department](#department)
  - [Team](#team)
  - [UserGroup](#usergroup)
  - [MembershipRule](#membershiprule)
- [セッション管理](#セッション管理)
  - [UserSession](#usersession)
  - [SessionToken](#sessiontoken)
  - [DeviceInfo](#deviceinfo)
  - [SessionActivity](#sessionactivity)
- [ユーザー操作](#ユーザー操作)
  - [CreateUserRequest](#createuserrequest)
  - [UpdateUserRequest](#updateuserrequest)
  - [DeleteUserRequest](#deleteuserrequest)
  - [BulkUserOperation](#bulkuseroperation)
  - [UserImport](#userimport)
- [プロファイル管理](#プロファイル管理)
  - [ProfileUpdate](#profileupdate)
  - [AvatarUpload](#avatarupload)
  - [PreferenceSettings](#preferencesettings)
  - [NotificationPreferences](#notificationpreferences)
- [パスワード管理](#パスワード管理)
  - [PasswordPolicy](#passwordpolicy)
  - [PasswordReset](#passwordreset)
  - [PasswordHistory](#passwordhistory)
  - [PasswordStrength](#passwordstrength)
- [アカウント管理](#アカウント管理)
  - [AccountLock](#accountlock)
  - [AccountRecovery](#accountrecovery)
  - [AccountDeletion](#accountdeletion)
  - [DataExport](#dataexport)
- [監査・コンプライアンス](#監査・コンプライアンス)
  - [UserAuditLog](#userauditlog)
  - [ConsentRecord](#consentrecord)
  - [GDPRCompliance](#gdprcompliance)
  - [DataRetention](#dataretention)
- [統合・連携](#統合・連携)
  - [LDAPConfig](#ldapconfig)
  - [ActiveDirectorySync](#activedirectorysync)
  - [SCIMProvision](#scimprovision)
  - [SSOConfiguration](#ssoconfiguration)
- [API定義](#api定義)
  - [レスポンス型](#レスポンス型)
  - [エラー型](#エラー型)

## 概要
MAKOTO Visual AIのユーザー管理システムに関する型定義です。エンタープライズグレードの認証・認可、権限管理、組織管理、コンプライアンス対応を含みます。

## 基本型定義

### User
```typescript
// ユーザー基本情報
interface User {
  // ユーザー識別子（内部システム用）
  user_id: string;
  
  // Cognitoユーザーサブ（必須）
  cognito_sub?: string;
  
  // ユーザー名（ログインID）
  // Cognitoのpreferred_usernameまたはemailから取得
  username: string;
  
  // メールアドレス（オプション、ユーザーIDがメールアドレスの場合は必須）
  email?: string;
  
  // メール確認状態
  email_verified?: boolean;
  
  // プロファイル情報
  profile: UserProfile;
  
  // ステータス情報
  status: UserStatus;
  
  // 所属組織
  organization_id?: string;
  
  // 所属部門
  department_ids?: string[];
  
  // 所属チーム
  team_ids?: string[];
  
  // 割り当てロール
  roles: string[];
  
  // 直接権限
  direct_permissions?: Permission[];
  
  // アカウントタイプ
  account_type: 'standard' | 'admin' | 'service' | 'guest';
  
  // 作成日時
  created_at: string;
  
  // 更新日時
  updated_at: string;
  
  // 最終ログイン日時
  last_login_at?: string;
  
  // ログイン回数
  login_count: number;
  
  // タグ
  tags?: Record<string, string>;
  
  // カスタム属性
  custom_attributes?: Record<string, any>;
}
```

### UserProfile
```typescript
// ユーザープロファイル
interface UserProfile {
  // 表示名
  display_name: string;
  
  // 名
  first_name?: string;
  
  // 姓
  last_name?: string;
  
  // ミドルネーム
  middle_name?: string;
  
  // ニックネーム
  nickname?: string;
  
  // プロフィール画像URL
  avatar_url?: string;
  
  // 役職
  job_title?: string;
  
  // 部署名（表示用）
  department?: string;
  
  // 電話番号
  phone_number?: string;
  
  // 携帯電話番号
  mobile_number?: string;
  
  // 勤務地
  location?: string;
  
  // タイムゾーン
  timezone?: string;
  
  // 言語設定
  language?: string;
  
  // 自己紹介
  bio?: string;
  
  // ソーシャルリンク
  social_links?: {
    linkedin?: string;
    twitter?: string;
    github?: string;
    [key: string]: string | undefined;
  };
  
  // スキル
  skills?: string[];
  
  // 誕生日
  birth_date?: string;
  
  // 入社日
  hire_date?: string;
  
  // 従業員番号
  employee_id?: string;
}
```

### UserCredentials
```typescript
// ユーザー認証情報
interface UserCredentials {
  // ユーザーID
  user_id: string;
  
  // パスワードハッシュ
  password_hash?: string;
  
  // パスワード設定日時
  password_set_at?: string;
  
  // パスワード有効期限
  password_expires_at?: string;
  
  // MFA設定
  mfa_enabled: boolean;
  
  // MFAシークレット
  mfa_secret?: string;
  
  // バックアップコード
  backup_codes?: string[];
  
  // 公開鍵認証
  public_keys?: PublicKeyCredential[];
  
  // OAuth2トークン
  oauth_tokens?: OAuthToken[];
  
  // APIキー
  api_keys?: APIKey[];
  
  // セキュリティ質問
  security_questions?: SecurityQuestion[];
  
  // 生体認証登録
  biometric_credentials?: BiometricCredential[];
}

// 公開鍵認証情報
interface PublicKeyCredential {
  credential_id: string;
  public_key: string;
  algorithm: string;
  created_at: string;
  last_used_at?: string;
  device_name?: string;
}

// OAuthトークン
interface OAuthToken {
  provider: string;
  access_token: string;
  refresh_token?: string;
  expires_at?: string;
  scope?: string[];
}

// APIキー
interface APIKey {
  key_id: string;
  key_hash: string;
  name: string;
  permissions: string[];
  expires_at?: string;
  created_at: string;
  last_used_at?: string;
}

// セキュリティ質問
interface SecurityQuestion {
  question_id: string;
  question: string;
  answer_hash: string;
}

// 生体認証情報
interface BiometricCredential {
  credential_id: string;
  type: 'fingerprint' | 'face' | 'voice';
  device_id: string;
  enrolled_at: string;
}
```

### UserStatus
```typescript
// ユーザーステータス
interface UserStatus {
  // アカウント状態
  account_status: 'active' | 'inactive' | 'suspended' | 'locked' | 'deleted';
  
  // 有効化状態
  is_enabled: boolean;
  
  // ロック状態
  is_locked: boolean;
  
  // ロック理由
  lock_reason?: string;
  
  // ロック日時
  locked_at?: string;
  
  // ロック解除予定日時
  unlock_at?: string;
  
  // 停止状態
  is_suspended: boolean;
  
  // 停止理由
  suspension_reason?: string;
  
  // 停止開始日時
  suspended_at?: string;
  
  // 停止終了予定日時
  suspension_ends_at?: string;
  
  // パスワードリセット要求
  password_reset_required: boolean;
  
  // 利用規約同意状態
  terms_accepted: boolean;
  
  // 利用規約同意日時
  terms_accepted_at?: string;
  
  // プライバシーポリシー同意状態
  privacy_accepted: boolean;
  
  // プライバシーポリシー同意日時
  privacy_accepted_at?: string;
}
```

## 認証・認可

### CognitoAuthentication
```typescript
// AWS Cognito認証情報
interface CognitoAuthentication {
  // ユーザープールID
  user_pool_id: string;
  
  // クライアントID
  client_id: string;
  
  // アイデンティティプールID
  identity_pool_id?: string;
  
  // リージョン
  region: string;
  
  // Cognitoユーザー属性
  cognito_attributes: {
    sub: string; // CognitoユーザーID（必須）
    // ユーザーIDまたはメールアドレス（どちらか必須）
    // preferred_usernameが無い場合は自動的にemailがユーザーIDになる
    preferred_username?: string; // ユーザーID
    email?: string; // メールアドレス
    email_verified?: boolean;
    phone_number?: string;
    phone_number_verified?: boolean;
    name?: string;
    given_name?: string;
    family_name?: string;
    picture?: string;
    locale?: string;
    zoneinfo?: string;
    updated_at?: number;
    // カスタム属性
    [key: `custom:${string}`]: string | number | boolean;
  } & (
    // preferred_usernameまたはemailのどちらか必須
    | { preferred_username: string; email?: string }
    | { preferred_username?: never; email: string }
  );
  
  // Cognitoグループ
  cognito_groups?: string[];
  
  // 認証フロー
  auth_flow: 'USER_SRP_AUTH' | 'USER_PASSWORD_AUTH' | 'CUSTOM_AUTH' | 'ADMIN_NO_SRP_AUTH';
  
  // MFA設定
  mfa_configuration?: 'OFF' | 'ON' | 'OPTIONAL';
  
  // MFAメソッド
  mfa_methods?: ('SMS_MFA' | 'SOFTWARE_TOKEN_MFA')[];
}
```

### CognitoAuthenticationRequest
```typescript
// Cognito認証リクエスト
interface CognitoAuthenticationRequest {
  // 認証フロータイプ
  auth_flow: 'USER_SRP_AUTH' | 'USER_PASSWORD_AUTH' | 'REFRESH_TOKEN_AUTH' | 'CUSTOM_AUTH';
  
  // ユーザー識別子（ユーザーIDまたはメールアドレス）
  username?: string;
  
  // パスワード（USER_PASSWORD_AUTHの場合）
  password?: string;
  
  // リフレッシュトークン（REFRESH_TOKEN_AUTHの場合）
  refresh_token?: string;
  
  // SRPパラメータ（USER_SRP_AUTHの場合）
  srp_a?: string;
  
  // チャレンジレスポンス
  challenge_responses?: {
    USERNAME?: string;
    PASSWORD?: string;
    NEW_PASSWORD?: string;
    SMS_MFA_CODE?: string;
    SOFTWARE_TOKEN_MFA_CODE?: string;
    DEVICE_KEY?: string;
    [key: string]: string | undefined;
  };
  
  // クライアントメタデータ
  client_metadata?: Record<string, string>;
  
  // アナリティクスメタデータ
  analytics_metadata?: {
    analytics_endpoint_id?: string;
  };
  
  // デバイス記憶
  remember_device?: boolean;
}
```

### CognitoAuthenticationResponse
```typescript
// Cognito認証レスポンス
interface CognitoAuthenticationResponse {
  // 認証結果
  authentication_result?: {
    // アクセストークン（JWT）
    access_token: string;
    
    // IDトークン（JWT）
    id_token: string;
    
    // リフレッシュトークン
    refresh_token: string;
    
    // トークン有効期限（秒）
    expires_in: number;
    
    // トークンタイプ
    token_type: 'Bearer';
    
    // デバイスキー
    new_device_metadata?: {
      device_key: string;
      device_group_key: string;
    };
  };
  
  // チャレンジ情報（追加認証が必要な場合）
  challenge_name?: 
    | 'SMS_MFA'
    | 'SOFTWARE_TOKEN_MFA'
    | 'SELECT_MFA_TYPE'
    | 'MFA_SETUP'
    | 'PASSWORD_VERIFIER'
    | 'CUSTOM_CHALLENGE'
    | 'DEVICE_SRP_AUTH'
    | 'DEVICE_PASSWORD_VERIFIER'
    | 'NEW_PASSWORD_REQUIRED';
  
  // チャレンジパラメータ
  challenge_parameters?: Record<string, string>;
  
  // セッション（チャレンジ用）
  session?: string;
  
  // レスポンスメタデータ
  response_metadata?: {
    request_id: string;
    http_status_code: number;
  };
}
```

### CognitoTokens
```typescript
// Cognitoトークン情報
interface CognitoTokens {
  // IDトークン（ユーザー属性を含む）
  id_token: {
    raw: string;
    payload: {
      sub: string;
      aud: string;
      cognito_groups?: string[];
      email_verified?: boolean;
      iss: string;
      cognito_username?: string;
      cognito_roles?: string[];
      aud: string;
      event_id: string;
      token_use: 'id';
      auth_time: number;
      exp: number;
      iat: number;
      // カスタム属性
      [key: string]: any;
    };
  };
  
  // アクセストークン（API認可用）
  access_token: {
    raw: string;
    payload: {
      sub: string;
      device_key?: string;
      cognito_groups?: string[];
      token_use: 'access';
      scope: string;
      auth_time: number;
      iss: string;
      exp: number;
      iat: number;
      jti: string;
      client_id: string;
      username: string;
    };
  };
  
  // リフレッシュトークン
  refresh_token?: string;
  
  // 有効期限
  expires_at: Date;
  
  // トークン更新タイムスタンプ
  refreshed_at?: Date;
}
```

### CognitoUserPoolOperations
```typescript
// Cognitoユーザープール操作
interface CognitoUserPoolOperations {
  // ユーザー登録
  signUp: {
    // ユーザー識別子（ユーザーIDまたはメールアドレス）
    // メールアドレスのみの場合は自動的にそれがユーザーIDになる
    username: string;
    password: string;
    user_attributes?: Array<{
      name: string;
      value: string;
    }>;
    validation_data?: Array<{
      name: string;
      value: string;
    }>;
    client_metadata?: Record<string, string>;
  };
  
  // ユーザー確認
  confirmSignUp: {
    username: string;
    confirmation_code: string;
    client_metadata?: Record<string, string>;
    force_alias_creation?: boolean;
  };
  
  // パスワード忘れ（メール無しユーザーの場合はエラーまたは代替手段を提案）
  forgotPassword: {
    username: string;
    client_metadata?: Record<string, string>;
    // メールが無い場合の処理フラグ
    fallback_to_admin?: boolean;
  };
  
  // パスワードリセット確認
  confirmForgotPassword: {
    username: string;
    confirmation_code: string;
    password: string;
    client_metadata?: Record<string, string>;
  };
  
  // パスワード変更
  changePassword: {
    access_token: string;
    previous_password: string;
    proposed_password: string;
  };
  
  // ユーザー属性更新
  updateUserAttributes: {
    access_token: string;
    user_attributes: Array<{
      name: string;
      value: string;
    }>;
    client_metadata?: Record<string, string>;
  };
  
  // ユーザー削除
  deleteUser: {
    access_token: string;
  };
  
  // MFA設定
  setUserMFAPreference: {
    access_token: string;
    sms_mfa_settings?: {
      enabled: boolean;
      preferred_mfa: boolean;
    };
    software_token_mfa_settings?: {
      enabled: boolean;
      preferred_mfa: boolean;
    };
  };
}
```

### CognitoAdminOperations
```typescript
// Cognito管理者操作（IAM権限必要）
interface CognitoAdminOperations {
  // 管理者によるユーザー作成
  adminCreateUser: {
    username: string;
    user_pool_id: string;
    user_attributes?: Array<{
      name: string;
      value: string;
    }>;
    temporary_password?: string;
    force_alias_creation?: boolean;
    message_action?: 'RESEND' | 'SUPPRESS';
    desired_delivery_mediums?: ('SMS' | 'EMAIL')[];
    client_metadata?: Record<string, string>;
  };
  
  // 管理者によるユーザー削除
  adminDeleteUser: {
    username: string;
    user_pool_id: string;
  };
  
  // 管理者によるユーザー有効化
  adminEnableUser: {
    username: string;
    user_pool_id: string;
  };
  
  // 管理者によるユーザー無効化
  adminDisableUser: {
    username: string;
    user_pool_id: string;
  };
  
  // 管理者によるパスワードリセット
  adminResetUserPassword: {
    username: string;
    user_pool_id: string;
    client_metadata?: Record<string, string>;
  };
  
  // グループへのユーザー追加
  adminAddUserToGroup: {
    username: string;
    group_name: string;
    user_pool_id: string;
  };
  
  // グループからのユーザー削除
  adminRemoveUserFromGroup: {
    username: string;
    group_name: string;
    user_pool_id: string;
  };
  
  // ユーザー属性の検証
  adminUpdateUserAttributes: {
    username: string;
    user_pool_id: string;
    user_attributes: Array<{
      name: string;
      value: string;
    }>;
    client_metadata?: Record<string, string>;
  };
}
```

### CognitoGroup
```typescript
// Cognitoグループ
interface CognitoGroup {
  // グループ名
  group_name: string;
  
  // ユーザープールID
  user_pool_id: string;
  
  // 説明
  description?: string;
  
  // IAMロールARN
  role_arn?: string;
  
  // 優先順位
  precedence?: number;
  
  // 作成日時
  creation_date?: Date;
  
  // 最終更新日時
  last_modified_date?: Date;
}
```

### CognitoUserImport
```typescript
// Cognitoユーザーインポート
interface CognitoUserImport {
  // ジョブID
  job_id: string;
  
  // ユーザープールID
  user_pool_id: string;
  
  // CSVファイル
  csv_file: {
    url: string;
    headers: string[];
    delimiter?: string;
  };
  
  // マッピング
  attribute_mapping?: Record<string, string>;
  
  // ジョブ状態
  status: 'Created' | 'Pending' | 'InProgress' | 'Stopping' | 'Expired' | 'Stopped' | 'Failed' | 'Succeeded';
  
  // 統計
  statistics?: {
    users_imported: number;
    users_failed: number;
    users_skipped: number;
  };
  
  // エラー
  errors?: Array<{
    row_number: number;
    error_code: string;
    error_message: string;
  }>;
}
```

### EntraIDConfiguration
```typescript
// Entra ID（旧Azure AD）設定
interface EntraIDConfiguration {
  // テナントID
  tenant_id: string;
  
  // クライアントID
  client_id: string;
  
  // クライアントシークレット
  client_secret?: string;
  
  // 証明書（クライアント証明書認証用）
  certificate?: {
    thumbprint: string;
    private_key: string;
    certificate: string;
  };
  
  // アプリケーションタイプ
  app_type: 'web' | 'spa' | 'mobile' | 'daemon';
  
  // 権限スコープ
  scopes: string[];
  
  // リダイレクトURI
  redirect_uris: string[];
  
  // ログアウトURL
  logout_url?: string;
  
  // グラフAPIエンドポイント
  graph_endpoint: string;
  
  // 認証エンドポイント
  authority: string;
  
  // リソースID
  resource?: string;
  
  // B2Cポリシー（B2Cテナントの場合）
  b2c_policy?: {
    sign_up_sign_in: string;
    password_reset?: string;
    profile_edit?: string;
  };
  
  // 条件付きアクセス
  conditional_access?: {
    enabled: boolean;
    policies?: string[];
  };
}
```

### EntraIDToken
```typescript
// Entra ID トークン
interface EntraIDToken {
  // アクセストークン
  access_token: {
    raw: string;
    payload: {
      aud: string; // Audience
      iss: string; // Issuer
      iat: number; // Issued At
      exp: number; // Expiration
      sub: string; // Subject (User ID)
      tid: string; // Tenant ID
      oid: string; // Object ID
      upn?: string; // User Principal Name
      email?: string;
      name?: string;
      given_name?: string;
      family_name?: string;
      roles?: string[];
      groups?: string[];
      scp?: string; // Scopes
      app_displayname?: string;
      appid?: string;
      ver: string; // Version
    };
  };
  
  // IDトークン（OpenID Connect）
  id_token?: {
    raw: string;
    payload: {
      aud: string;
      iss: string;
      iat: number;
      exp: number;
      sub: string;
      tid: string;
      oid: string;
      upn?: string;
      email?: string;
      email_verified?: boolean;
      name?: string;
      given_name?: string;
      family_name?: string;
      preferred_username?: string;
      nonce?: string;
      at_hash?: string;
    };
  };
  
  // リフレッシュトークン
  refresh_token?: string;
  
  // 有効期限
  expires_at: Date;
  
  // スコープ
  scope: string[];
  
  // トークンタイプ
  token_type: 'Bearer';
}
```

### EntraIDUser
```typescript
// Entra ID ユーザー情報
interface EntraIDUser {
  // オブジェクトID
  id: string;
  
  // ユーザープリンシパル名
  userPrincipalName: string;
  
  // 表示名
  displayName?: string;
  
  // 名
  givenName?: string;
  
  // 姓
  surname?: string;
  
  // メールアドレス
  mail?: string;
  
  // その他のメール
  otherMails?: string[];
  
  // 電話番号
  businessPhones?: string[];
  
  // 携帯電話
  mobilePhone?: string;
  
  // 役職
  jobTitle?: string;
  
  // 部署
  department?: string;
  
  // 会社名
  companyName?: string;
  
  // オフィス所在地
  officeLocation?: string;
  
  // 上司
  manager?: {
    id: string;
    displayName?: string;
  };
  
  // 直属の部下
  directReports?: Array<{
    id: string;
    displayName?: string;
  }>;
  
  // グループメンバーシップ
  memberOf?: Array<{
    id: string;
    displayName?: string;
    type: string;
  }>;
  
  // アプリケーションロール
  appRoleAssignments?: Array<{
    id: string;
    appRoleId: string;
    resourceId: string;
    principalType: string;
  }>;
  
  // 作成日時
  createdDateTime?: Date;
  
  // アカウント有効状態
  accountEnabled?: boolean;
  
  // 使用場所
  usageLocation?: string;
  
  // ライセンス
  assignedLicenses?: Array<{
    skuId: string;
    disabledPlans?: string[];
  }>;
  
  // 拡張属性
  extensionAttributes?: Record<string, any>;
}
```

### EntraIDGroup
```typescript
// Entra ID グループ
interface EntraIDGroup {
  // グループID
  id: string;
  
  // グループ名
  displayName: string;
  
  // 説明
  description?: string;
  
  // グループタイプ
  groupTypes: string[];
  
  // メール有効
  mailEnabled: boolean;
  
  // セキュリティ有効
  securityEnabled: boolean;
  
  // メールニックネーム
  mailNickname?: string;
  
  // メールアドレス
  mail?: string;
  
  // メンバー
  members?: Array<{
    id: string;
    displayName?: string;
    userPrincipalName?: string;
  }>;
  
  // オーナー
  owners?: Array<{
    id: string;
    displayName?: string;
    userPrincipalName?: string;
  }>;
  
  // 動的メンバーシップルール
  membershipRule?: string;
  
  // ルール処理状態
  membershipRuleProcessingState?: 'On' | 'Paused';
  
  // 可視性
  visibility?: 'Public' | 'Private' | 'HiddenMembership';
  
  // 作成日時
  createdDateTime?: Date;
}
```

### EntraIDAuthenticationRequest
```typescript
// Entra ID 認証リクエスト
interface EntraIDAuthenticationRequest {
  // 認証フロー
  flow_type: 'authorization_code' | 'client_credentials' | 'device_code' | 'refresh_token' | 'on_behalf_of';
  
  // テナントID
  tenant_id: string;
  
  // クライアントID
  client_id: string;
  
  // 認証コード（authorization_codeフロー）
  code?: string;
  
  // リダイレクトURI
  redirect_uri?: string;
  
  // スコープ
  scope?: string[];
  
  // リソース
  resource?: string;
  
  // クライアント認証
  client_authentication?: {
    method: 'client_secret' | 'certificate' | 'client_assertion';
    client_secret?: string;
    client_assertion?: string;
    client_assertion_type?: string;
  };
  
  // リフレッシュトークン
  refresh_token?: string;
  
  // デバイスコード
  device_code?: string;
  
  // ユーザーコード
  user_code?: string;
  
  // PKCEパラメータ
  code_verifier?: string;
  
  // カスタムパラメータ
  custom_parameters?: Record<string, string>;
}
```

### EntraIDAuthenticationResponse
```typescript
// Entra ID 認証レスポンス
interface EntraIDAuthenticationResponse {
  // 成功フラグ
  success: boolean;
  
  // トークン
  tokens?: EntraIDToken;
  
  // デバイスコード情報（device_codeフロー）
  device_code_info?: {
    device_code: string;
    user_code: string;
    verification_uri: string;
    verification_uri_complete?: string;
    expires_in: number;
    interval: number;
    message?: string;
  };
  
  // ユーザー情報
  user_info?: EntraIDUser;
  
  // エラー情報
  error?: {
    error: string;
    error_description?: string;
    error_codes?: number[];
    correlation_id?: string;
    trace_id?: string;
    timestamp?: string;
  };
  
  // レスポンスメタデータ
  metadata?: {
    request_id: string;
    duration_ms: number;
  };
}
```

### EntraIDSyncConfiguration
```typescript
// Entra ID 同期設定
interface EntraIDSyncConfiguration {
  // 設定ID
  config_id: string;
  
  // テナント設定
  tenant: EntraIDConfiguration;
  
  // 同期対象
  sync_targets: {
    users: boolean;
    groups: boolean;
    applications?: boolean;
    devices?: boolean;
  };
  
  // フィルター
  filters: {
    // ユーザーフィルター（ODataクエリ）
    user_filter?: string;
    
    // グループフィルター
    group_filter?: string;
    
    // 部門フィルター
    department_filter?: string[];
    
    // ライセンスフィルター
    license_filter?: string[];
    
    // 無効ユーザー除外
    exclude_disabled_users?: boolean;
  };
  
  // 属性マッピング
  attribute_mapping: {
    user_attributes: Record<string, string>;
    group_attributes?: Record<string, string>;
  };
  
  // 同期オプション
  sync_options: {
    // 増分同期
    delta_sync: boolean;
    
    // 削除されたオブジェクトの処理
    handle_deletions: 'disable' | 'delete' | 'ignore';
    
    // 競合解決
    conflict_resolution: 'entra_wins' | 'local_wins' | 'manual';
    
    // バッチサイズ
    batch_size: number;
    
    // 同期間隔（分）
    sync_interval_minutes: number;
  };
  
  // Graph API設定
  graph_settings: {
    // APIバージョン
    api_version: 'v1.0' | 'beta';
    
    // リクエスト制限
    rate_limit: {
      requests_per_second: number;
      burst_limit: number;
    };
    
    // リトライ設定
    retry_policy: {
      max_retries: number;
      backoff_strategy: 'exponential' | 'linear';
      initial_delay_ms: number;
    };
  };
  
  // 監査設定
  audit_config: {
    log_all_operations: boolean;
    log_errors_only?: boolean;
    retention_days: number;
  };
}
```

### CognitoEntraIDIntegration
```typescript
// Cognito と Entra ID の統合設定
interface CognitoEntraIDIntegration {
  // 統合ID
  integration_id: string;
  
  // Cognito設定
  cognito: {
    user_pool_id: string;
    identity_provider: {
      provider_name: string;
      provider_type: 'SAML' | 'OIDC';
      provider_details: {
        // SAML設定
        MetadataURL?: string;
        IDPSignout?: boolean;
        
        // OIDC設定
        client_id?: string;
        client_secret?: string;
        attributes_request_method?: 'GET' | 'POST';
        oidc_issuer?: string;
        authorize_scopes?: string;
        
        // Entra ID固有設定
        tenant_id: string;
        policy_name?: string; // B2Cの場合
      };
      
      // 属性マッピング
      attribute_mapping: {
        'email': string;
        'given_name'?: string;
        'family_name'?: string;
        'name'?: string;
        [key: string]: string | undefined;
      };
    };
  };
  
  // Entra ID設定
  entra_id: EntraIDConfiguration;
  
  // グループマッピング
  group_mapping?: Array<{
    entra_group_id: string;
    entra_group_name: string;
    cognito_group_name: string;
    auto_create_cognito_group: boolean;
  }>;
  
  // ユーザープロビジョニング
  user_provisioning: {
    // JITプロビジョニング
    just_in_time: boolean;
    
    // デフォルトグループ
    default_groups?: string[];
    
    // カスタム属性同期
    custom_attribute_sync?: Record<string, string>;
    
    // プロファイル更新
    update_on_login: boolean;
  };
  
  // 同期状態
  sync_status: {
    last_sync?: Date;
    next_sync?: Date;
    sync_in_progress: boolean;
    users_synced: number;
    groups_synced: number;
    errors: Array<{
      timestamp: Date;
      error_type: string;
      message: string;
      user_id?: string;
    }>;
  };
  
  // SSO設定
  sso_configuration: {
    enabled: boolean;
    default_redirect_url?: string;
    logout_behavior: 'cognito_only' | 'entra_id_only' | 'both';
    session_duration?: number;
  };
}
```

### AuthenticationRequest
```typescript
// 統合認証リクエスト（Cognito + 内部システム）
interface AuthenticationRequest {
  // 認証方式
  auth_method: 'cognito' | 'federated' | 'api_key' | 'service_account';
  
  // Cognito認証
  cognito?: CognitoAuthenticationRequest;
  
  // フェデレーション認証
  federated?: {
    provider: 'google' | 'facebook' | 'amazon' | 'apple' | 'saml' | 'oidc';
    token?: string;
    code?: string;
  };
  
  // APIキー認証
  api_key?: string;
  
  // サービスアカウント認証
  service_account?: {
    client_id: string;
    client_secret?: string;
    jwt_assertion?: string;
  };
  
  // デバイス情報
  device_info?: DeviceInfo;
  
  // IPアドレス
  ip_address?: string;
  
  // ユーザーエージェント
  user_agent?: string;
}
```

### AuthenticationResponse
```typescript
// 統合認証レスポンス
interface AuthenticationResponse {
  // 認証成功
  success: boolean;
  
  // Cognito認証結果
  cognito_result?: CognitoAuthenticationResponse;
  
  // 統合ユーザー情報
  user?: User & {
    cognito_sub?: string;
    cognito_groups?: string[];
    federated_identities?: Array<{
      provider: string;
      provider_id: string;
    }>;
  };
  
  // トークン
  tokens?: CognitoTokens;
  
  // 一時的な認証情報（STSクレデンシャル）
  temporary_credentials?: {
    access_key_id: string;
    secret_access_key: string;
    session_token: string;
    expiration: Date;
  };
  
  // セッションID
  session_id?: string;
  
  // MFA要求
  mfa_required?: boolean;
  
  // パスワード変更要求
  password_change_required?: boolean;
  
  // エラー情報
  error?: {
    code: string;
    message: string;
    cognito_error_code?: string;
    details?: any;
  };
}
```

### AuthorizationCheck
```typescript
// 認可チェック
interface AuthorizationCheck {
  // ユーザーID
  user_id: string;
  
  // リソース
  resource: string;
  
  // アクション
  action: string;
  
  // コンテキスト
  context?: {
    // IPアドレス
    ip_address?: string;
    
    // デバイスID
    device_id?: string;
    
    // セッションID
    session_id?: string;
    
    // 時間条件
    time_constraints?: TimeConstraints;
    
    // 地理的制約
    geo_constraints?: GeoConstraints;
    
    // カスタム属性
    attributes?: Record<string, any>;
  };
  
  // チェック結果
  result?: {
    allowed: boolean;
    reason?: string;
    applied_policies?: string[];
    required_permissions?: string[];
    missing_permissions?: string[];
  };
}

// 時間制約
interface TimeConstraints {
  start_time?: string;
  end_time?: string;
  days_of_week?: number[];
  timezone?: string;
}

// 地理的制約
interface GeoConstraints {
  allowed_countries?: string[];
  blocked_countries?: string[];
  allowed_regions?: string[];
  blocked_regions?: string[];
  allowed_ip_ranges?: string[];
  blocked_ip_ranges?: string[];
}
```

### OAuth2Integration
```typescript
// OAuth2統合設定
interface OAuth2Integration {
  // プロバイダーID
  provider_id: string;
  
  // プロバイダー名
  provider_name: string;
  
  // プロバイダータイプ
  provider_type: 'google' | 'microsoft' | 'github' | 'okta' | 'auth0' | 'custom';
  
  // クライアントID
  client_id: string;
  
  // クライアントシークレット
  client_secret?: string;
  
  // 認可エンドポイント
  authorization_endpoint: string;
  
  // トークンエンドポイント
  token_endpoint: string;
  
  // ユーザー情報エンドポイント
  userinfo_endpoint: string;
  
  // JWKSエンドポイント
  jwks_uri?: string;
  
  // リダイレクトURI
  redirect_uris: string[];
  
  // スコープ
  scopes: string[];
  
  // レスポンスタイプ
  response_type: string;
  
  // グラントタイプ
  grant_types: string[];
  
  // PKCE要求
  pkce_required: boolean;
  
  // ユーザー属性マッピング
  attribute_mapping: {
    user_id?: string;
    username?: string;
    email?: string;
    display_name?: string;
    [key: string]: string | undefined;
  };
  
  // 自動プロビジョニング
  auto_provision: boolean;
  
  // デフォルトロール
  default_roles?: string[];
}
```

### SAMLAssertion
```typescript
// SAML認証情報
interface SAMLAssertion {
  // アサーションID
  assertion_id: string;
  
  // 発行者
  issuer: string;
  
  // サブジェクト
  subject: string;
  
  // 名前ID
  name_id: string;
  
  // 名前IDフォーマット
  name_id_format: string;
  
  // 認証コンテキスト
  auth_context: string;
  
  // セッションインデックス
  session_index?: string;
  
  // 属性
  attributes: Record<string, string | string[]>;
  
  // 条件
  conditions: {
    not_before?: string;
    not_on_or_after?: string;
    audience_restriction?: string[];
  };
  
  // 認証ステートメント
  auth_statement: {
    auth_instant: string;
    session_not_on_or_after?: string;
    auth_context_class_ref?: string;
  };
  
  // 署名検証結果
  signature_valid: boolean;
  
  // 検証エラー
  validation_errors?: string[];
}
```

### MultiFactorAuth
```typescript
// 多要素認証
interface MultiFactorAuth {
  // ユーザーID
  user_id: string;
  
  // MFA方式
  methods: MFAMethod[];
  
  // プライマリ方式
  primary_method: string;
  
  // 設定日時
  configured_at: string;
  
  // 最終使用日時
  last_used_at?: string;
  
  // 信頼済みデバイス
  trusted_devices?: TrustedDevice[];
  
  // リカバリーオプション
  recovery_options: RecoveryOption[];
}

// MFA方式
interface MFAMethod {
  method_id: string;
  type: 'totp' | 'sms' | 'email' | 'push' | 'u2f' | 'webauthn' | 'biometric';
  name: string;
  configured: boolean;
  verified: boolean;
  configuration?: any;
}

// 信頼済みデバイス
interface TrustedDevice {
  device_id: string;
  device_name: string;
  device_type: string;
  trusted_at: string;
  expires_at?: string;
  last_used_at: string;
}

// リカバリーオプション
interface RecoveryOption {
  type: 'backup_codes' | 'recovery_email' | 'recovery_phone' | 'admin_reset';
  configured: boolean;
  details?: any;
}
```

## 権限管理

### Role
```typescript
// ロール定義
interface Role {
  // ロールID
  role_id: string;
  
  // ロール名
  name: string;
  
  // 表示名
  display_name: string;
  
  // 説明
  description?: string;
  
  // ロールタイプ
  type: 'system' | 'custom' | 'dynamic';
  
  // 権限
  permissions: Permission[];
  
  // 継承ロール
  inherited_roles?: string[];
  
  // スコープ
  scope?: {
    organization_id?: string;
    department_id?: string;
    team_id?: string;
    resource_type?: string;
  };
  
  // 条件
  conditions?: RoleCondition[];
  
  // 優先度
  priority?: number;
  
  // 有効状態
  is_enabled: boolean;
  
  // システムロール（編集不可）
  is_system: boolean;
  
  // 作成日時
  created_at: string;
  
  // 更新日時
  updated_at: string;
  
  // メタデータ
  metadata?: Record<string, any>;
}

// ロール条件
interface RoleCondition {
  type: 'time' | 'location' | 'attribute' | 'resource';
  operator: 'eq' | 'ne' | 'in' | 'not_in' | 'contains' | 'regex';
  field: string;
  value: any;
}
```

### Permission
```typescript
// 権限定義
interface Permission {
  // 権限ID
  permission_id: string;
  
  // 権限名
  name: string;
  
  // リソースタイプ
  resource_type: string;
  
  // アクション
  action: string;
  
  // スコープ
  scope?: 'global' | 'organization' | 'department' | 'team' | 'self';
  
  // リソース条件
  resource_conditions?: ResourceCondition[];
  
  // 効果
  effect: 'allow' | 'deny';
  
  // 説明
  description?: string;
  
  // カテゴリ
  category?: string;
  
  // リスクレベル
  risk_level?: 'low' | 'medium' | 'high' | 'critical';
  
  // 依存権限
  dependencies?: string[];
  
  // 除外権限
  exclusions?: string[];
}

// リソース条件
interface ResourceCondition {
  field: string;
  operator: 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'not_in' | 'contains' | 'regex';
  value: any;
}
```

### PolicyDocument
```typescript
// ポリシードキュメント（AWS IAM形式）
interface PolicyDocument {
  // バージョン
  version: string;
  
  // ステートメント
  statements: PolicyStatement[];
  
  // 変数定義
  variables?: Record<string, any>;
}

// ポリシーステートメント
interface PolicyStatement {
  // ステートメントID
  sid?: string;
  
  // 効果
  effect: 'Allow' | 'Deny';
  
  // プリンシパル
  principal?: {
    type: 'User' | 'Role' | 'Group' | 'Service';
    identifiers: string[];
  };
  
  // アクション
  action: string | string[];
  
  // リソース
  resource: string | string[];
  
  // 条件
  condition?: PolicyCondition;
}

// ポリシー条件
interface PolicyCondition {
  [operator: string]: {
    [key: string]: string | string[] | number | boolean;
  };
}
```

### AccessControl
```typescript
// アクセス制御
interface AccessControl {
  // ACL ID
  acl_id: string;
  
  // リソースID
  resource_id: string;
  
  // リソースタイプ
  resource_type: string;
  
  // オーナー
  owner_id: string;
  
  // アクセスエントリ
  entries: AccessControlEntry[];
  
  // 継承設定
  inheritance: {
    enabled: boolean;
    from_parent?: string;
    propagate_to_children?: boolean;
  };
  
  // デフォルト権限
  default_permissions?: Permission[];
  
  // 作成日時
  created_at: string;
  
  // 更新日時
  updated_at: string;
}

// アクセス制御エントリ
interface AccessControlEntry {
  // エントリID
  entry_id: string;
  
  // プリンシパルタイプ
  principal_type: 'user' | 'role' | 'group' | 'service';
  
  // プリンシパルID
  principal_id: string;
  
  // 権限
  permissions: string[];
  
  // 効果
  effect: 'allow' | 'deny';
  
  // 優先度
  priority?: number;
  
  // 有効期限
  expires_at?: string;
  
  // 条件
  conditions?: AccessCondition[];
}

// アクセス条件
interface AccessCondition {
  type: string;
  parameters: Record<string, any>;
}
```

### ResourcePermission
```typescript
// リソース権限
interface ResourcePermission {
  // リソース識別子
  resource_id: string;
  
  // リソースタイプ
  resource_type: string;
  
  // リソース名
  resource_name?: string;
  
  // パス
  path?: string;
  
  // 所有者
  owner: {
    type: 'user' | 'group' | 'service';
    id: string;
  };
  
  // 権限マトリックス
  permissions: {
    read?: PermissionGrant[];
    write?: PermissionGrant[];
    delete?: PermissionGrant[];
    share?: PermissionGrant[];
    execute?: PermissionGrant[];
    manage?: PermissionGrant[];
    [action: string]: PermissionGrant[] | undefined;
  };
  
  // 共有設定
  sharing: {
    is_shared: boolean;
    share_type?: 'public' | 'organization' | 'specific';
    shared_with?: string[];
    share_link?: string;
    share_expires_at?: string;
  };
  
  // 監査設定
  audit: {
    track_access: boolean;
    track_modifications: boolean;
    retention_days?: number;
  };
}

// 権限付与
interface PermissionGrant {
  grantee_type: 'user' | 'role' | 'group' | 'everyone';
  grantee_id: string;
  granted_at: string;
  granted_by: string;
  expires_at?: string;
  conditions?: Record<string, any>;
}
```

## 組織・グループ管理

### Organization
```typescript
// 組織
interface Organization {
  // 組織ID
  organization_id: string;
  
  // 組織名
  name: string;
  
  // 表示名
  display_name: string;
  
  // ドメイン
  domains: string[];
  
  // 業種
  industry?: string;
  
  // 規模
  size?: 'small' | 'medium' | 'large' | 'enterprise';
  
  // 国
  country?: string;
  
  // タイムゾーン
  timezone?: string;
  
  // 言語
  default_language?: string;
  
  // 親組織
  parent_org_id?: string;
  
  // 子組織
  child_org_ids?: string[];
  
  // 設定
  settings: OrganizationSettings;
  
  // 契約情報
  subscription?: {
    plan: string;
    status: string;
    expires_at?: string;
    user_limit?: number;
    features: string[];
  };
  
  // 管理者
  admins: string[];
  
  // 作成日時
  created_at: string;
  
  // 更新日時
  updated_at: string;
  
  // ステータス
  status: 'active' | 'suspended' | 'deleted';
}

// 組織設定
interface OrganizationSettings {
  // セキュリティ設定
  security: {
    password_policy?: PasswordPolicy;
    mfa_required?: boolean;
    session_timeout?: number;
    ip_whitelist?: string[];
    allowed_domains?: string[];
  };
  
  // 認証設定
  authentication: {
    methods: string[];
    sso_enabled?: boolean;
    sso_provider?: string;
    ldap_enabled?: boolean;
  };
  
  // 通知設定
  notifications: {
    admin_emails: string[];
    security_alerts: boolean;
    usage_reports: boolean;
  };
  
  // カスタマイズ
  customization: {
    logo_url?: string;
    color_scheme?: string;
    custom_domain?: string;
  };
}
```

### Department
```typescript
// 部門
interface Department {
  // 部門ID
  department_id: string;
  
  // 部門名
  name: string;
  
  // 部門コード
  code?: string;
  
  // 組織ID
  organization_id: string;
  
  // 親部門
  parent_department_id?: string;
  
  // 子部門
  child_department_ids?: string[];
  
  // 部門長
  manager_id?: string;
  
  // 副部門長
  deputy_manager_ids?: string[];
  
  // メンバー数
  member_count: number;
  
  // コストセンター
  cost_center?: string;
  
  // 場所
  location?: string;
  
  // 説明
  description?: string;
  
  // メタデータ
  metadata?: Record<string, any>;
  
  // 作成日時
  created_at: string;
  
  // 更新日時
  updated_at: string;
  
  // ステータス
  status: 'active' | 'inactive' | 'reorganizing';
}
```

### Team
```typescript
// チーム
interface Team {
  // チームID
  team_id: string;
  
  // チーム名
  name: string;
  
  // 表示名
  display_name: string;
  
  // 説明
  description?: string;
  
  // 部門ID
  department_id?: string;
  
  // チームタイプ
  type: 'permanent' | 'project' | 'virtual' | 'cross_functional';
  
  // チームリーダー
  leader_id: string;
  
  // メンバー
  members: TeamMember[];
  
  // チャンネル（コミュニケーション）
  channels?: {
    slack?: string;
    teams?: string;
    email?: string;
  };
  
  // プロジェクト
  projects?: string[];
  
  // 目標
  objectives?: string[];
  
  // 作成日時
  created_at: string;
  
  // 更新日時
  updated_at: string;
  
  // 有効期限（プロジェクトチームの場合）
  expires_at?: string;
  
  // ステータス
  status: 'active' | 'inactive' | 'archived';
}

// チームメンバー
interface TeamMember {
  user_id: string;
  role: 'leader' | 'member' | 'viewer';
  joined_at: string;
  responsibilities?: string[];
}
```

### UserGroup
```typescript
// ユーザーグループ
interface UserGroup {
  // グループID
  group_id: string;
  
  // グループ名
  name: string;
  
  // 表示名
  display_name: string;
  
  // 説明
  description?: string;
  
  // グループタイプ
  type: 'static' | 'dynamic' | 'nested';
  
  // メンバーシップルール（動的グループ）
  membership_rules?: MembershipRule[];
  
  // 静的メンバー
  static_members?: string[];
  
  // ネストグループ
  nested_groups?: string[];
  
  // 除外メンバー
  excluded_members?: string[];
  
  // ロール割り当て
  assigned_roles?: string[];
  
  // 権限
  permissions?: Permission[];
  
  // オーナー
  owner_id: string;
  
  // 管理者
  admins?: string[];
  
  // 同期設定
  sync_config?: {
    source: 'ldap' | 'azure_ad' | 'okta' | 'manual';
    sync_interval?: number;
    last_sync?: string;
    mapping?: Record<string, string>;
  };
  
  // メタデータ
  metadata?: Record<string, any>;
  
  // 作成日時
  created_at: string;
  
  // 更新日時
  updated_at: string;
}
```

### MembershipRule
```typescript
// メンバーシップルール（動的グループ用）
interface MembershipRule {
  // ルールID
  rule_id: string;
  
  // ルールタイプ
  type: 'attribute' | 'department' | 'location' | 'role' | 'custom';
  
  // 属性
  attribute?: string;
  
  // 演算子
  operator: 'eq' | 'ne' | 'contains' | 'starts_with' | 'ends_with' | 'regex' | 'in' | 'not_in';
  
  // 値
  value: any;
  
  // 論理演算子（複数ルールの場合）
  logical_operator?: 'AND' | 'OR' | 'NOT';
  
  // 子ルール
  child_rules?: MembershipRule[];
  
  // 有効状態
  is_enabled: boolean;
  
  // 優先度
  priority?: number;
}
```

## セッション管理

### UserSession
```typescript
// ユーザーセッション
interface UserSession {
  // セッションID
  session_id: string;
  
  // ユーザーID
  user_id: string;
  
  // セッショントークン
  token: SessionToken;
  
  // デバイス情報
  device: DeviceInfo;
  
  // IPアドレス
  ip_address: string;
  
  // 地理情報
  geo_location?: {
    country?: string;
    region?: string;
    city?: string;
    latitude?: number;
    longitude?: number;
  };
  
  // 作成日時
  created_at: string;
  
  // 最終アクティビティ
  last_activity_at: string;
  
  // 有効期限
  expires_at: string;
  
  // セッション状態
  status: 'active' | 'idle' | 'expired' | 'revoked';
  
  // アイドルタイムアウト（秒）
  idle_timeout?: number;
  
  // 絶対タイムアウト（秒）
  absolute_timeout?: number;
  
  // リフレッシュ可能
  refreshable: boolean;
  
  // セッション属性
  attributes?: Record<string, any>;
  
  // アクティビティログ
  activities?: SessionActivity[];
}
```

### SessionToken
```typescript
// セッショントークン
interface SessionToken {
  // トークン値
  value: string;
  
  // トークンタイプ
  type: 'bearer' | 'mac' | 'jwt';
  
  // 発行日時
  issued_at: string;
  
  // 有効期限
  expires_at: string;
  
  // リフレッシュトークン
  refresh_token?: string;
  
  // スコープ
  scope?: string[];
  
  // クレーム（JWT）
  claims?: Record<string, any>;
  
  // 署名
  signature?: string;
  
  // 暗号化
  encrypted?: boolean;
}
```

### DeviceInfo
```typescript
// デバイス情報
interface DeviceInfo {
  // デバイスID
  device_id: string;
  
  // デバイス名
  device_name?: string;
  
  // デバイスタイプ
  device_type: 'desktop' | 'mobile' | 'tablet' | 'iot' | 'unknown';
  
  // OS
  os: {
    name: string;
    version: string;
    platform: string;
  };
  
  // ブラウザ
  browser?: {
    name: string;
    version: string;
    engine: string;
  };
  
  // ユーザーエージェント
  user_agent: string;
  
  // 画面解像度
  screen_resolution?: string;
  
  // 信頼済みデバイス
  is_trusted?: boolean;
  
  // 初回使用日時
  first_seen_at: string;
  
  // 最終使用日時
  last_seen_at: string;
  
  // フィンガープリント
  fingerprint?: string;
}
```

### SessionActivity
```typescript
// セッションアクティビティ
interface SessionActivity {
  // アクティビティID
  activity_id: string;
  
  // タイムスタンプ
  timestamp: string;
  
  // アクション
  action: string;
  
  // リソース
  resource?: string;
  
  // 結果
  result: 'success' | 'failure' | 'error';
  
  // IPアドレス
  ip_address?: string;
  
  // 詳細
  details?: Record<string, any>;
}
```

## ユーザー操作

### CreateUserRequest
```typescript
// ユーザー作成リクエスト
interface CreateUserRequest {
  // ユーザー名（必須、メールアドレスでも可）
  username: string;
  
  // メールアドレス（オプション、usernameがメールでない場合に指定）
  email?: string;
  
  // パスワード
  password?: string;
  
  // プロファイル
  profile: Partial<UserProfile>;
  
  // 組織ID
  organization_id?: string;
  
  // 部門ID
  department_ids?: string[];
  
  // チームID
  team_ids?: string[];
  
  // ロール
  roles?: string[];
  
  // グループ
  groups?: string[];
  
  // アカウントタイプ
  account_type?: 'standard' | 'admin' | 'service' | 'guest';
  
  // 招待送信
  send_invitation?: boolean;
  
  // パスワードリセット要求
  require_password_reset?: boolean;
  
  // MFA要求
  require_mfa?: boolean;
  
  // カスタム属性
  custom_attributes?: Record<string, any>;
  
  // メタデータ
  metadata?: Record<string, any>;
}
```

### UpdateUserRequest
```typescript
// ユーザー更新リクエスト
interface UpdateUserRequest {
  // ユーザーID
  user_id: string;
  
  // ユーザー名
  username?: string;
  
  // メールアドレス
  email?: string;
  
  // プロファイル更新
  profile?: Partial<UserProfile>;
  
  // ステータス更新
  status?: Partial<UserStatus>;
  
  // 組織変更
  organization_id?: string;
  
  // 部門変更
  department_ids?: string[];
  
  // チーム変更
  team_ids?: string[];
  
  // ロール変更
  roles?: {
    add?: string[];
    remove?: string[];
    set?: string[];
  };
  
  // グループ変更
  groups?: {
    add?: string[];
    remove?: string[];
    set?: string[];
  };
  
  // カスタム属性更新
  custom_attributes?: Record<string, any>;
  
  // 更新理由
  reason?: string;
  
  // 通知送信
  notify_user?: boolean;
}
```

### DeleteUserRequest
```typescript
// ユーザー削除リクエスト
interface DeleteUserRequest {
  // ユーザーID
  user_id: string;
  
  // 削除タイプ
  deletion_type: 'soft' | 'hard' | 'anonymize';
  
  // データ保持
  data_retention?: {
    // 保持期間（日）
    retention_days?: number;
    
    // 保持するデータタイプ
    retain_types?: string[];
    
    // 削除するデータタイプ
    delete_types?: string[];
  };
  
  // 後継者
  successor?: {
    // 後継者ユーザーID
    user_id: string;
    
    // 移管するリソース
    transfer_resources?: boolean;
    
    // 移管する権限
    transfer_permissions?: boolean;
    
    // 移管するグループメンバーシップ
    transfer_groups?: boolean;
  };
  
  // 削除理由
  reason: string;
  
  // 削除確認
  confirmation_code?: string;
  
  // 通知
  notifications?: {
    notify_user?: boolean;
    notify_admins?: boolean;
    notify_team?: boolean;
  };
}
```

### BulkUserOperation
```typescript
// 一括ユーザー操作
interface BulkUserOperation {
  // 操作ID
  operation_id: string;
  
  // 操作タイプ
  operation_type: 'create' | 'update' | 'delete' | 'activate' | 'deactivate' | 'assign_role' | 'remove_role';
  
  // 対象ユーザー
  user_ids?: string[];
  
  // フィルター条件
  filter?: {
    organization_id?: string;
    department_ids?: string[];
    roles?: string[];
    groups?: string[];
    status?: string;
    custom_query?: string;
  };
  
  // 操作データ
  data?: any;
  
  // 実行オプション
  options?: {
    // バッチサイズ
    batch_size?: number;
    
    // 並列実行
    parallel?: boolean;
    
    // エラー時の動作
    on_error?: 'stop' | 'continue' | 'rollback';
    
    // ドライラン
    dry_run?: boolean;
    
    // 通知
    notify?: boolean;
  };
  
  // 実行状態
  status?: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  
  // 進捗
  progress?: {
    total: number;
    processed: number;
    succeeded: number;
    failed: number;
    errors?: Array<{
      user_id: string;
      error: string;
    }>;
  };
  
  // 開始日時
  started_at?: string;
  
  // 完了日時
  completed_at?: string;
}
```

### UserImport
```typescript
// ユーザーインポート
interface UserImport {
  // インポートID
  import_id: string;
  
  // インポートソース
  source: 'csv' | 'ldap' | 'azure_ad' | 'okta' | 'api';
  
  // ファイル情報（CSV）
  file?: {
    name: string;
    size: number;
    mime_type: string;
    url?: string;
  };
  
  // マッピング設定
  mapping: {
    // フィールドマッピング
    fields: Record<string, string>;
    
    // デフォルト値
    defaults?: Record<string, any>;
    
    // 変換ルール
    transformations?: Array<{
      field: string;
      type: string;
      params?: any;
    }>;
  };
  
  // インポートオプション
  options: {
    // 更新モード
    update_mode: 'create_only' | 'update_only' | 'upsert';
    
    // 重複処理
    duplicate_handling: 'skip' | 'update' | 'error';
    
    // 検証
    validate_before_import?: boolean;
    
    // 通知送信
    send_invitations?: boolean;
    
    // ロール自動割り当て
    auto_assign_roles?: string[];
    
    // グループ自動割り当て
    auto_assign_groups?: string[];
  };
  
  // インポート状態
  status: 'pending' | 'validating' | 'importing' | 'completed' | 'failed';
  
  // 結果
  result?: {
    total_records: number;
    imported: number;
    updated: number;
    skipped: number;
    failed: number;
    errors?: ImportError[];
  };
  
  // 開始日時
  started_at?: string;
  
  // 完了日時
  completed_at?: string;
}

// インポートエラー
interface ImportError {
  row: number;
  field?: string;
  value?: any;
  error: string;
}
```

## プロファイル管理

### ProfileUpdate
```typescript
// プロファイル更新
interface ProfileUpdate {
  // ユーザーID
  user_id: string;
  
  // 更新フィールド
  fields: Partial<UserProfile>;
  
  // 検証ルール
  validation?: {
    // 必須フィールド
    required_fields?: string[];
    
    // フォーマット検証
    format_rules?: Record<string, string>;
    
    // カスタム検証
    custom_validators?: Array<{
      field: string;
      validator: string;
      params?: any;
    }>;
  };
  
  // 承認要求
  requires_approval?: boolean;
  
  // 承認者
  approver_id?: string;
  
  // 変更理由
  reason?: string;
  
  // 監査ログ
  audit?: {
    // 変更前の値
    old_values?: Partial<UserProfile>;
    
    // 変更者
    changed_by: string;
    
    // 変更日時
    changed_at: string;
  };
}
```

### AvatarUpload
```typescript
// アバターアップロード
interface AvatarUpload {
  // ユーザーID
  user_id: string;
  
  // ファイル情報
  file: {
    name: string;
    size: number;
    mime_type: string;
    data?: string; // Base64
    url?: string;
  };
  
  // 画像処理
  processing?: {
    // リサイズ
    resize?: {
      width: number;
      height: number;
      maintain_aspect_ratio?: boolean;
    };
    
    // クロップ
    crop?: {
      x: number;
      y: number;
      width: number;
      height: number;
    };
    
    // フォーマット変換
    format?: 'jpeg' | 'png' | 'webp';
    
    // 品質
    quality?: number;
  };
  
  // サムネイル生成
  thumbnails?: Array<{
    size: 'small' | 'medium' | 'large';
    width: number;
    height: number;
  }>;
  
  // アップロード結果
  result?: {
    url: string;
    thumbnails?: Record<string, string>;
    uploaded_at: string;
  };
}
```

### PreferenceSettings
```typescript
// ユーザー設定
interface PreferenceSettings {
  // ユーザーID
  user_id: string;
  
  // UI設定
  ui: {
    theme?: 'light' | 'dark' | 'auto';
    language?: string;
    timezone?: string;
    date_format?: string;
    time_format?: '12h' | '24h';
    first_day_of_week?: number;
  };
  
  // 通知設定
  notifications: NotificationPreferences;
  
  // プライバシー設定
  privacy: {
    profile_visibility?: 'public' | 'organization' | 'private';
    show_email?: boolean;
    show_phone?: boolean;
    show_location?: boolean;
    activity_status?: boolean;
  };
  
  // セキュリティ設定
  security: {
    two_factor_auth?: boolean;
    session_timeout?: number;
    login_notifications?: boolean;
    suspicious_activity_alerts?: boolean;
  };
  
  // アクセシビリティ
  accessibility: {
    high_contrast?: boolean;
    large_text?: boolean;
    screen_reader?: boolean;
    keyboard_navigation?: boolean;
    reduce_motion?: boolean;
  };
  
  // カスタム設定
  custom?: Record<string, any>;
}
```

### NotificationPreferences
```typescript
// 通知設定
interface NotificationPreferences {
  // メール通知
  email: {
    enabled: boolean;
    frequency?: 'immediate' | 'hourly' | 'daily' | 'weekly';
    categories?: {
      security?: boolean;
      updates?: boolean;
      mentions?: boolean;
      tasks?: boolean;
      reports?: boolean;
    };
  };
  
  // プッシュ通知
  push: {
    enabled: boolean;
    devices?: string[];
    categories?: {
      security?: boolean;
      mentions?: boolean;
      urgent?: boolean;
    };
  };
  
  // アプリ内通知
  in_app: {
    enabled: boolean;
    show_desktop?: boolean;
    sound?: boolean;
    categories?: Record<string, boolean>;
  };
  
  // SMS通知
  sms?: {
    enabled: boolean;
    phone_number?: string;
    categories?: {
      security?: boolean;
      urgent?: boolean;
    };
  };
  
  // 通知時間設定
  quiet_hours?: {
    enabled: boolean;
    start_time?: string;
    end_time?: string;
    timezone?: string;
    days?: number[];
  };
}
```

## パスワード管理

### PasswordPolicy
```typescript
// パスワードポリシー
interface PasswordPolicy {
  // 最小長
  min_length: number;
  
  // 最大長
  max_length?: number;
  
  // 大文字要求
  require_uppercase: boolean;
  
  // 小文字要求
  require_lowercase: boolean;
  
  // 数字要求
  require_numbers: boolean;
  
  // 特殊文字要求
  require_special_chars: boolean;
  
  // 特殊文字リスト
  special_chars?: string;
  
  // 禁止パスワード
  blacklist?: string[];
  
  // 辞書チェック
  dictionary_check?: boolean;
  
  // 個人情報チェック
  personal_info_check?: boolean;
  
  // 過去のパスワード禁止数
  history_count?: number;
  
  // 有効期限（日）
  expiry_days?: number;
  
  // 期限前警告（日）
  expiry_warning_days?: number;
  
  // 最小変更文字数
  min_change_chars?: number;
  
  // パスワード強度要求
  min_strength?: 'weak' | 'fair' | 'good' | 'strong' | 'very_strong';
  
  // カスタムルール
  custom_rules?: Array<{
    name: string;
    regex: string;
    message: string;
  }>;
}
```

### PasswordReset
```typescript
// パスワードリセット
interface PasswordReset {
  // リセットID
  reset_id: string;
  
  // ユーザーID
  user_id: string;
  
  // リセット方法（メールが無い場合は管理者リセットまたはSMS、セキュリティ質問を使用）
  method: 'email' | 'sms' | 'security_questions' | 'admin' | 'phone_verification';
  
  // 利用可能なリセット方法（メール無しユーザー用）
  available_methods?: ('sms' | 'security_questions' | 'admin' | 'phone_verification')[];
  
  // メール送信可否
  email_available?: boolean;
  
  // 電話番号（SMS用）
  phone_number?: string;
  
  // トークン
  token?: string;
  
  // トークン有効期限
  token_expires_at?: string;
  
  // セキュリティ質問
  security_questions?: Array<{
    question_id: string;
    question: string;
    answer?: string;
  }>;
  
  // 電話認証コード（SMS用）
  verification_code?: string;
  
  // 新パスワード
  new_password?: string;
  
  // 確認パスワード
  confirm_password?: string;
  
  // リクエスト日時
  requested_at: string;
  
  // リクエスト元IP
  request_ip?: string;
  
  // リセット完了日時
  completed_at?: string;
  
  // ステータス
  status: 'pending' | 'verified' | 'completed' | 'expired' | 'cancelled' | 'awaiting_admin';
  
  // 試行回数
  attempts?: number;
  
  // 最大試行回数
  max_attempts?: number;
  
  // 管理者承認要求（メール・電話が無い場合）
  admin_approval_required?: boolean;
  
  // 管理者通知送信済み
  admin_notified?: boolean;
}
```

### PasswordHistory
```typescript
// パスワード履歴
interface PasswordHistory {
  // ユーザーID
  user_id: string;
  
  // 履歴エントリ
  entries: PasswordHistoryEntry[];
  
  // 保持エントリ数
  retention_count: number;
  
  // 保持期間（日）
  retention_days?: number;
}

// パスワード履歴エントリ
interface PasswordHistoryEntry {
  // パスワードハッシュ
  password_hash: string;
  
  // 設定日時
  set_at: string;
  
  // 変更理由
  change_reason?: string;
  
  // 変更者
  changed_by?: string;
  
  // 強度スコア
  strength_score?: number;
}
```

### PasswordStrength
```typescript
// パスワード強度
interface PasswordStrength {
  // 強度スコア（0-100）
  score: number;
  
  // 強度レベル
  level: 'very_weak' | 'weak' | 'fair' | 'good' | 'strong' | 'very_strong';
  
  // 推定クラック時間
  crack_time?: {
    online_throttling: string;
    online_no_throttling: string;
    offline_slow: string;
    offline_fast: string;
  };
  
  // フィードバック
  feedback?: {
    warning?: string;
    suggestions?: string[];
  };
  
  // チェック結果
  checks: {
    length?: boolean;
    uppercase?: boolean;
    lowercase?: boolean;
    numbers?: boolean;
    special_chars?: boolean;
    dictionary?: boolean;
    personal_info?: boolean;
    common_patterns?: boolean;
  };
  
  // エントロピー
  entropy?: number;
}
```

## アカウント管理

### AccountLock
```typescript
// アカウントロック
interface AccountLock {
  // ユーザーID
  user_id: string;
  
  // ロックタイプ
  lock_type: 'security' | 'admin' | 'payment' | 'compliance' | 'temporary';
  
  // ロック理由
  reason: string;
  
  // ロック詳細
  details?: string;
  
  // ロック日時
  locked_at: string;
  
  // ロック実行者
  locked_by: string;
  
  // 自動解除設定
  auto_unlock?: {
    enabled: boolean;
    unlock_at?: string;
    conditions?: string[];
  };
  
  // 解除要件
  unlock_requirements?: {
    password_reset?: boolean;
    mfa_setup?: boolean;
    admin_approval?: boolean;
    payment_update?: boolean;
    training_completion?: boolean;
  };
  
  // 解除試行
  unlock_attempts?: Array<{
    attempted_at: string;
    method: string;
    success: boolean;
    reason?: string;
  }>;
  
  // 解除情報
  unlock_info?: {
    unlocked_at: string;
    unlocked_by: string;
    unlock_reason: string;
  };
}
```

### AccountRecovery
```typescript
// アカウント回復
interface AccountRecovery {
  // 回復ID
  recovery_id: string;
  
  // ユーザー識別情報
  identifier: {
    email?: string;
    username?: string;
    phone?: string;
    employee_id?: string;
  };
  
  // 回復方法
  recovery_methods: RecoveryMethod[];
  
  // 選択された方法
  selected_method?: string;
  
  // 検証ステップ
  verification_steps: VerificationStep[];
  
  // 現在のステップ
  current_step?: number;
  
  // リクエスト日時
  requested_at: string;
  
  // 有効期限
  expires_at: string;
  
  // ステータス
  status: 'pending' | 'verifying' | 'verified' | 'completed' | 'failed' | 'expired';
  
  // 結果
  result?: {
    user_id?: string;
    access_restored?: boolean;
    new_credentials?: boolean;
    completed_at?: string;
  };
}

// 回復方法
interface RecoveryMethod {
  method_id: string;
  type: 'email' | 'sms' | 'security_questions' | 'backup_codes' | 'admin_verification' | 'id_verification' | 'phone_verification';
  available: boolean;
  priority: number;
  // メール無しユーザーのための詳細情報
  details?: {
    phone_number_masked?: string; // SMS用のマスクされた電話番号
    security_questions_count?: number; // 設定済みセキュリティ質問数
    admin_contact?: string; // 管理者連絡先
  };
}

// 検証ステップ
interface VerificationStep {
  step_id: string;
  type: string;
  required: boolean;
  completed: boolean;
  attempts: number;
  max_attempts?: number;
}
```

### AccountDeletion
```typescript
// アカウント削除
interface AccountDeletion {
  // 削除リクエストID
  deletion_id: string;
  
  // ユーザーID
  user_id: string;
  
  // 削除タイプ
  deletion_type: 'user_requested' | 'admin_requested' | 'compliance' | 'inactive';
  
  // 削除スケジュール
  schedule: {
    requested_at: string;
    scheduled_for: string;
    grace_period_days: number;
    can_cancel_until: string;
  };
  
  // データ処理
  data_handling: {
    // エクスポート
    export_data?: boolean;
    export_format?: string;
    export_url?: string;
    
    // 匿名化
    anonymize?: boolean;
    anonymization_fields?: string[];
    
    // 保持
    retain_for_compliance?: boolean;
    retention_period_days?: number;
    
    // 削除
    delete_immediately?: string[];
    delete_after_export?: string[];
  };
  
  // 影響分析
  impact_analysis?: {
    owned_resources?: number;
    shared_resources?: number;
    dependencies?: string[];
    transfer_required?: boolean;
  };
  
  // 確認
  confirmation?: {
    method: 'email' | 'sms' | 'in_app';
    confirmed: boolean;
    confirmed_at?: string;
  };
  
  // ステータス
  status: 'pending' | 'confirmed' | 'processing' | 'completed' | 'cancelled';
  
  // 完了情報
  completion?: {
    completed_at: string;
    deleted_data_types: string[];
    retained_data_types?: string[];
    anonymized_data_types?: string[];
  };
}
```

### DataExport
```typescript
// データエクスポート（GDPR対応）
interface DataExport {
  // エクスポートID
  export_id: string;
  
  // ユーザーID
  user_id: string;
  
  // リクエスト理由
  reason: 'gdpr' | 'ccpa' | 'deletion' | 'audit' | 'migration';
  
  // エクスポート範囲
  scope: {
    // データカテゴリ
    categories?: string[];
    
    // 期間
    date_range?: {
      start: string;
      end: string;
    };
    
    // 特定のサービス
    services?: string[];
    
    // 含める/除外する
    include_archived?: boolean;
    include_deleted?: boolean;
    exclude_sensitive?: boolean;
  };
  
  // フォーマット
  format: 'json' | 'csv' | 'xml' | 'pdf';
  
  // 暗号化
  encryption?: {
    enabled: boolean;
    method?: string;
    password_protected?: boolean;
  };
  
  // 配送方法
  delivery: {
    method: 'download' | 'email' | 'secure_transfer';
    destination?: string;
    expires_at?: string;
  };
  
  // ステータス
  status: 'requested' | 'processing' | 'ready' | 'delivered' | 'expired';
  
  // 結果
  result?: {
    file_size: number;
    record_count: number;
    download_url?: string;
    checksum?: string;
    generated_at: string;
  };
  
  // リクエスト日時
  requested_at: string;
  
  // 完了日時
  completed_at?: string;
}
```

## 監査・コンプライアンス

### UserAuditLog
```typescript
// ユーザー監査ログ
interface UserAuditLog {
  // ログID
  log_id: string;
  
  // タイムスタンプ
  timestamp: string;
  
  // ユーザーID
  user_id: string;
  
  // アクション
  action: string;
  
  // アクションカテゴリ
  category: 'authentication' | 'authorization' | 'profile' | 'security' | 'data_access' | 'admin';
  
  // リソース
  resource?: {
    type: string;
    id: string;
    name?: string;
  };
  
  // 変更内容
  changes?: {
    before?: any;
    after?: any;
    fields?: string[];
  };
  
  // 結果
  result: 'success' | 'failure' | 'partial';
  
  // エラー
  error?: {
    code: string;
    message: string;
  };
  
  // コンテキスト
  context: {
    ip_address?: string;
    user_agent?: string;
    session_id?: string;
    device_id?: string;
    location?: any;
  };
  
  // リスクスコア
  risk_score?: number;
  
  // 異常検知
  anomaly_detected?: boolean;
  
  // コンプライアンスタグ
  compliance_tags?: string[];
}
```

### ConsentRecord
```typescript
// 同意記録（GDPR/CCPA対応）
interface ConsentRecord {
  // 記録ID
  record_id: string;
  
  // ユーザーID
  user_id: string;
  
  // 同意タイプ
  consent_type: 'privacy_policy' | 'terms_of_service' | 'marketing' | 'cookies' | 'data_processing' | 'third_party_sharing';
  
  // バージョン
  version: string;
  
  // 同意状態
  granted: boolean;
  
  // 同意日時
  granted_at?: string;
  
  // 撤回日時
  revoked_at?: string;
  
  // 同意方法
  method: 'explicit' | 'implicit' | 'opt_out';
  
  // 同意の詳細
  details?: {
    purpose?: string[];
    data_categories?: string[];
    retention_period?: string;
    third_parties?: string[];
  };
  
  // 法的根拠
  legal_basis?: 'consent' | 'contract' | 'legal_obligation' | 'vital_interests' | 'public_task' | 'legitimate_interests';
  
  // 証跡
  evidence?: {
    ip_address?: string;
    user_agent?: string;
    screenshot_url?: string;
    form_data?: any;
  };
  
  // 有効期限
  expires_at?: string;
  
  // 更新要求
  renewal_required?: boolean;
}
```

### GDPRCompliance
```typescript
// GDPR コンプライアンス
interface GDPRCompliance {
  // ユーザーID
  user_id: string;
  
  // データ主体の権利
  rights: {
    // アクセス権
    access: {
      enabled: boolean;
      last_exercised?: string;
    };
    
    // 訂正権
    rectification: {
      enabled: boolean;
      last_exercised?: string;
    };
    
    // 削除権（忘れられる権利）
    erasure: {
      enabled: boolean;
      last_exercised?: string;
    };
    
    // 処理制限権
    restriction: {
      enabled: boolean;
      active?: boolean;
      reason?: string;
    };
    
    // データポータビリティ権
    portability: {
      enabled: boolean;
      last_exercised?: string;
    };
    
    // 異議申立権
    objection: {
      enabled: boolean;
      objections?: Array<{
        date: string;
        reason: string;
        status: string;
      }>;
    };
  };
  
  // 処理活動
  processing_activities: ProcessingActivity[];
  
  // データ侵害通知
  breach_notifications?: BreachNotification[];
  
  // DPO連絡先
  dpo_contact?: {
    name: string;
    email: string;
    phone?: string;
  };
  
  // 監査ログ
  audit_required: boolean;
  
  // 最終レビュー日
  last_review_date?: string;
  
  // 次回レビュー日
  next_review_date?: string;
}

// 処理活動
interface ProcessingActivity {
  activity_id: string;
  purpose: string;
  legal_basis: string;
  data_categories: string[];
  recipients?: string[];
  retention_period: string;
  security_measures: string[];
}

// データ侵害通知
interface BreachNotification {
  breach_id: string;
  occurred_at: string;
  discovered_at: string;
  notified_at?: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  affected_data: string[];
  actions_taken: string[];
}
```

### DataRetention
```typescript
// データ保持ポリシー
interface DataRetention {
  // ポリシーID
  policy_id: string;
  
  // ポリシー名
  name: string;
  
  // 適用範囲
  scope: {
    user_types?: string[];
    data_categories?: string[];
    regions?: string[];
  };
  
  // 保持ルール
  retention_rules: RetentionRule[];
  
  // デフォルト保持期間（日）
  default_retention_days: number;
  
  // 法的要件
  legal_requirements?: {
    jurisdiction: string;
    regulation: string;
    minimum_retention?: number;
    maximum_retention?: number;
  };
  
  // 削除スケジュール
  deletion_schedule: {
    frequency: 'daily' | 'weekly' | 'monthly';
    time?: string;
    timezone?: string;
  };
  
  // 例外
  exceptions?: Array<{
    condition: string;
    retention_days: number;
    reason: string;
  }>;
  
  // 有効状態
  is_active: boolean;
  
  // 作成日時
  created_at: string;
  
  // 更新日時
  updated_at: string;
}

// 保持ルール
interface RetentionRule {
  rule_id: string;
  data_type: string;
  retention_days: number;
  action_after_retention: 'delete' | 'archive' | 'anonymize';
  conditions?: Record<string, any>;
}
```

## 統合・連携

### LDAPConfig
```typescript
// LDAP設定
interface LDAPConfig {
  // 設定ID
  config_id: string;
  
  // 接続設定
  connection: {
    host: string;
    port: number;
    use_ssl: boolean;
    use_tls: boolean;
    bind_dn: string;
    bind_password?: string;
    timeout?: number;
  };
  
  // ベースDN
  base_dn: string;
  
  // ユーザー検索
  user_search: {
    base_dn?: string;
    filter: string;
    scope: 'base' | 'one' | 'sub';
    attributes: string[];
  };
  
  // グループ検索
  group_search?: {
    base_dn?: string;
    filter: string;
    scope: 'base' | 'one' | 'sub';
    attributes: string[];
  };
  
  // 属性マッピング
  attribute_mapping: {
    username: string;
    email: string;
    display_name?: string;
    first_name?: string;
    last_name?: string;
    department?: string;
    [key: string]: string | undefined;
  };
  
  // 同期設定
  sync: {
    enabled: boolean;
    schedule?: string; // Cron形式
    last_sync?: string;
    sync_groups?: boolean;
    create_users?: boolean;
    update_users?: boolean;
    deactivate_users?: boolean;
  };
  
  // テスト結果
  test_result?: {
    success: boolean;
    message?: string;
    user_count?: number;
    group_count?: number;
    tested_at: string;
  };
}
```

### ActiveDirectorySync
```typescript
// Active Directory同期
interface ActiveDirectorySync {
  // 同期ID
  sync_id: string;
  
  // ドメイン設定
  domain: {
    name: string;
    controllers: string[];
    default_ou?: string;
  };
  
  // 認証
  authentication: {
    method: 'simple' | 'kerberos' | 'ntlm';
    username: string;
    password?: string;
    use_ssl: boolean;
  };
  
  // フィルター
  filters: {
    user_filter?: string;
    group_filter?: string;
    ou_filter?: string[];
    exclude_disabled?: boolean;
  };
  
  // マッピング
  field_mapping: Record<string, string>;
  
  // 同期オプション
  options: {
    sync_passwords?: boolean;
    sync_photos?: boolean;
    sync_manager_hierarchy?: boolean;
    sync_group_membership?: boolean;
    nested_groups?: boolean;
  };
  
  // 同期状態
  status: {
    last_sync?: string;
    next_sync?: string;
    in_progress: boolean;
    users_synced?: number;
    groups_synced?: number;
    errors?: Array<{
      timestamp: string;
      entity: string;
      error: string;
    }>;
  };
}
```

### SCIMProvision
```typescript
// SCIM プロビジョニング
interface SCIMProvision {
  // エンドポイント設定
  endpoint: {
    base_url: string;
    version: '1.1' | '2.0';
    authentication: {
      type: 'bearer' | 'basic' | 'oauth2';
      credentials: any;
    };
  };
  
  // リソースタイプ
  resource_types: {
    users: boolean;
    groups: boolean;
    enterprise_users?: boolean;
  };
  
  // スキーママッピング
  schema_mapping: {
    user_schema: Record<string, string>;
    group_schema?: Record<string, string>;
    custom_schemas?: Record<string, any>;
  };
  
  // プロビジョニング設定
  provisioning: {
    create_users: boolean;
    update_users: boolean;
    delete_users: boolean;
    create_groups?: boolean;
    update_groups?: boolean;
    delete_groups?: boolean;
  };
  
  // フィルター
  filters?: {
    user_filter?: string;
    group_filter?: string;
  };
  
  // 同期状態
  sync_status: {
    enabled: boolean;
    last_sync?: string;
    total_users?: number;
    total_groups?: number;
    failed_operations?: Array<{
      operation: string;
      resource: string;
      error: string;
      timestamp: string;
    }>;
  };
}
```

### SSOConfiguration
```typescript
// SSO設定
interface SSOConfiguration {
  // SSO ID
  sso_id: string;
  
  // プロトコル
  protocol: 'saml' | 'oauth2' | 'oidc' | 'ws-fed';
  
  // IdPメタデータ
  idp_metadata: {
    entity_id: string;
    sso_url: string;
    slo_url?: string;
    certificate: string;
    metadata_url?: string;
  };
  
  // SPメタデータ
  sp_metadata: {
    entity_id: string;
    acs_url: string;
    slo_url?: string;
    certificate?: string;
  };
  
  // 属性マッピング
  attribute_mapping: Record<string, string>;
  
  // セッション設定
  session: {
    duration: number;
    idle_timeout?: number;
    force_authn?: boolean;
  };
  
  // JIT（Just-In-Time）プロビジョニング
  jit_provisioning?: {
    enabled: boolean;
    default_roles?: string[];
    default_groups?: string[];
    update_on_login?: boolean;
  };
  
  // アクセス制御
  access_control?: {
    allowed_domains?: string[];
    allowed_groups?: string[];
    blocked_users?: string[];
  };
  
  // ステータス
  status: 'active' | 'inactive' | 'testing';
  
  // テスト設定
  test_mode?: {
    enabled: boolean;
    test_users?: string[];
    debug_logging?: boolean;
  };
}
```

## API定義

### レスポンス型

```typescript
// 成功レスポンス
interface UserManagementSuccessResponse<T = any> {
  success: true;
  data: T;
  metadata?: {
    timestamp: string;
    request_id: string;
    pagination?: {
      page: number;
      size: number;
      total: number;
      has_next: boolean;
    };
  };
}

// ページネーション付きレスポンス
interface PaginatedUsersResponse {
  users: User[];
  pagination: {
    page: number;
    size: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
  };
  filters_applied?: Record<string, any>;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}
```

### エラー型

```typescript
// エラーレスポンス
interface UserManagementErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: any;
    field_errors?: Array<{
      field: string;
      message: string;
      code: string;
    }>;
    timestamp: string;
    request_id: string;
  };
}

// エラーコード
type UserManagementErrorCode = 
  | 'USER_NOT_FOUND'
  | 'USER_ALREADY_EXISTS'
  | 'INVALID_CREDENTIALS'
  | 'ACCOUNT_LOCKED'
  | 'ACCOUNT_SUSPENDED'
  | 'PASSWORD_EXPIRED'
  | 'MFA_REQUIRED'
  | 'INSUFFICIENT_PERMISSIONS'
  | 'INVALID_TOKEN'
  | 'SESSION_EXPIRED'
  | 'RATE_LIMIT_EXCEEDED'
  | 'VALIDATION_ERROR'
  | 'AUTHENTICATION_FAILED'
  | 'AUTHORIZATION_FAILED'
  | 'PASSWORD_POLICY_VIOLATION'
  | 'CONSENT_REQUIRED'
  | 'GDPR_VIOLATION'
  | 'LDAP_CONNECTION_ERROR'
  | 'SSO_ERROR'
  // Cognito関連エラー
  | 'COGNITO_USER_NOT_FOUND'
  | 'COGNITO_USER_NOT_CONFIRMED'
  | 'COGNITO_INVALID_PASSWORD'
  | 'COGNITO_TEMPORARY_PASSWORD_EXPIRED'
  | 'COGNITO_MFA_CHALLENGE_EXCEPTION'
  | 'COGNITO_CODE_MISMATCH'
  | 'COGNITO_EXPIRED_CODE'
  | 'COGNITO_LIMIT_EXCEEDED'
  | 'COGNITO_INTERNAL_ERROR'
  // EntraID関連エラー
  | 'ENTRAID_INVALID_CLIENT'
  | 'ENTRAID_INVALID_GRANT'
  | 'ENTRAID_UNAUTHORIZED_CLIENT'
  | 'ENTRAID_UNSUPPORTED_GRANT_TYPE'
  | 'ENTRAID_INVALID_SCOPE'
  | 'ENTRAID_TENANT_NOT_FOUND'
  | 'ENTRAID_USER_NOT_FOUND'
  | 'ENTRAID_CONDITIONAL_ACCESS_BLOCKED'
  | 'ENTRAID_DEVICE_NOT_COMPLIANT'
  | 'ENTRAID_MFA_REQUIRED'
  | 'ENTRAID_CONSENT_REQUIRED'
  | 'ENTRAID_INTERACTION_REQUIRED';
```