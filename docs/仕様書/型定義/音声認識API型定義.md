# 音声認識API型定義

## 目次

1. [概要](#概要)
2. [基本型定義](#基本型定義)
   - [AudioData](#audiodata)
   - [TranscriptionResult](#transcriptionresult)
   - [SpeechSynthesisResult](#speechsynthesisresult)
3. [Speech-to-Text型定義](#speech-to-text型定義)
   - [TranscriptionRequest](#transcriptionrequest)
   - [TranscriptionSegment](#transcriptionsegment)
   - [SpeakerDiarization](#speakerdiarization)
   - [WordTimestamp](#wordtimestamp)
4. [Text-to-Speech型定義](#text-to-speech型定義)
   - [SynthesisRequest](#synthesisrequest)
   - [VoiceProfile](#voiceprofile)
   - [AudioFormat](#audioformat)
   - [SSML](#ssml)
5. [リアルタイム音声処理型定義](#リアルタイム音声処理型定義)
   - [StreamingTranscription](#streamingtranscription)
   - [StreamingSynthesis](#streamingsynthesis)
6. [音声分析型定義](#音声分析型定義)
   - [AudioAnalysis](#audioanalysis)
   - [EmotionDetection](#emotiondetection)
   - [LanguageIdentification](#languageidentification)
7. [話者管理型定義](#話者管理型定義)
   - [Speaker](#speaker)
   - [VoiceCloning](#voicecloning)
8. [API リクエスト/レスポンス型定義](#api-リクエストレスポンス型定義)
   - [音声認識](#音声認識)
   - [音声合成](#音声合成)
   - [話者識別](#話者識別)
   - [音声分析](#音声分析-1)
9. [更新履歴](#更新履歴)

## 概要

MAKOTO Visual AIの音声認識機能で使用される型定義。Speech-to-Text（音声認識）、Text-to-Speech（音声合成）、話者識別、感情分析などの音声処理に関する構造を定義する。

## 基本型定義

### AudioData

音声データの基本構造：

```typescript
interface AudioData {
  // 識別情報
  audio_id: string;                        // 音声ID（UUID）
  tenant_id: string;                       // テナントID
  
  // ファイル情報
  file_info: {
    filename: string;                      // ファイル名
    format: AudioFileFormat;               // ファイル形式
    size_bytes: number;                    // ファイルサイズ（バイト）
    duration_seconds: number;              // 長さ（秒）
    sample_rate: number;                   // サンプリングレート（Hz）
    channels: number;                      // チャンネル数
    bit_depth?: number;                    // ビット深度
    codec?: string;                        // コーデック
  };
  
  // ストレージ情報
  storage: {
    provider: "s3" | "azure" | "gcp" | "local";
    bucket?: string;                       // バケット名
    key?: string;                          // オブジェクトキー
    url?: string;                          // アクセスURL
    signed_url?: string;                   // 署名付きURL
    expires_at?: string;                   // URL有効期限
  };
  
  // メタデータ
  metadata?: {
    title?: string;                        // タイトル
    description?: string;                  // 説明
    language?: string;                     // 言語コード
    source?: string;                       // ソース（録音、合成等）
    recorded_at?: string;                  // 録音日時
    location?: {                           // 録音場所
      latitude?: number;
      longitude?: number;
      address?: string;
    };
    tags?: string[];                       // タグ
    custom?: Record<string, any>;          // カスタムメタデータ
  };
  
  // タイムスタンプ
  created_at: string;                      // 作成日時
  updated_at: string;                      // 更新日時
  processed_at?: string;                   // 処理日時
}

// 音声ファイル形式
type AudioFileFormat = 
  | "wav"
  | "mp3"
  | "m4a"
  | "ogg"
  | "flac"
  | "aac"
  | "opus"
  | "webm"
  | "amr";
```

### TranscriptionResult

音声認識結果：

```typescript
interface TranscriptionResult {
  // 識別情報
  transcription_id: string;                // 認識結果ID
  audio_id: string;                        // 音声ID
  
  // 認識結果
  text: string;                           // 認識テキスト（全文）
  confidence: number;                      // 信頼度（0-1）
  language: string;                       // 検出言語
  
  // セグメント情報
  segments: TranscriptionSegment[];        // セグメント配列
  
  // 話者情報
  speakers?: Speaker[];                    // 話者リスト
  speaker_diarization?: SpeakerDiarization; // 話者分離結果
  
  // 単語タイムスタンプ
  words?: WordTimestamp[];                 // 単語タイムスタンプ
  
  // 処理情報
  processing_info: {
    model: string;                         // 使用モデル
    provider: "openai" | "google" | "aws" | "azure" | "custom";
    processing_time_ms: number;            // 処理時間（ミリ秒）
    cost?: number;                         // コスト
  };
  
  // 追加分析
  analysis?: {
    sentiment?: SentimentAnalysis;         // 感情分析
    entities?: NamedEntity[];              // 固有表現
    topics?: string[];                     // トピック
    summary?: string;                      // 要約
  };
  
  // ステータス
  status: TranscriptionStatus;             // ステータス
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  
  // タイムスタンプ
  created_at: string;                      // 作成日時
  completed_at?: string;                   // 完了日時
}

// 認識ステータス
type TranscriptionStatus = 
  | "pending"               // 待機中
  | "processing"            // 処理中
  | "completed"             // 完了
  | "failed"                // 失敗
  | "cancelled";            // キャンセル
```

### SpeechSynthesisResult

音声合成結果：

```typescript
interface SpeechSynthesisResult {
  // 識別情報
  synthesis_id: string;                    // 合成結果ID
  
  // 合成音声
  audio: AudioData;                        // 生成音声データ
  
  // 合成情報
  synthesis_info: {
    text: string;                         // 元テキスト
    voice_id: string;                     // 使用音声ID
    language: string;                     // 言語
    model: string;                        // 使用モデル
    provider: "openai" | "google" | "aws" | "azure" | "elevenlabs";
  };
  
  // 音声マーカー
  markers?: {
    sentences?: Array<{                    // 文境界
      text: string;
      start_time: number;
      end_time: number;
    }>;
    words?: WordTimestamp[];               // 単語タイムスタンプ
    phonemes?: Array<{                    // 音素
      phoneme: string;
      start_time: number;
      duration: number;
    }>;
  };
  
  // 処理情報
  processing_info: {
    processing_time_ms: number;           // 処理時間
    characters_count: number;              // 文字数
    cost?: number;                        // コスト
  };
  
  // ステータス
  status: "completed" | "failed";
  error?: {
    code: string;
    message: string;
  };
  
  // タイムスタンプ
  created_at: string;                     // 作成日時
  completed_at: string;                   // 完了日時
}
```

## Speech-to-Text型定義

### TranscriptionRequest

音声認識リクエスト：

```typescript
interface TranscriptionRequest {
  // 音声入力
  audio: {
    // ファイルアップロード
    file?: {
      content: string;                     // Base64エンコード
      format: AudioFileFormat;             // ファイル形式
      filename?: string;                   // ファイル名
    };
    
    // URLから取得
    url?: string;                         // 音声ファイルURL
    
    // 既存音声ID
    audio_id?: string;                    // 既存音声ID
  };
  
  // 認識設定
  config: {
    language?: string;                    // 言語コード（ja, en等）
    auto_detect_language?: boolean;       // 言語自動検出
    alternative_languages?: string[];     // 代替言語
    
    model?: TranscriptionModel;           // 使用モデル
    
    // 出力オプション
    enable_word_timestamps?: boolean;     // 単語タイムスタンプ
    enable_speaker_diarization?: boolean; // 話者分離
    max_speakers?: number;                // 最大話者数
    min_speakers?: number;                // 最小話者数
    
    // 処理オプション
    punctuation?: boolean;                // 句読点追加
    profanity_filter?: boolean;          // 不適切語フィルタ
    automatic_punctuation?: boolean;      // 自動句読点
    
    // 音声強調
    audio_enhancement?: {
      noise_reduction?: boolean;          // ノイズ除去
      volume_normalization?: boolean;     // 音量正規化
      echo_cancellation?: boolean;        // エコー除去
    };
    
    // 専門用語辞書
    vocabulary?: {
      phrases?: string[];                 // カスタムフレーズ
      boost_words?: Array<{               // ブースト単語
        word: string;
        weight: number;
      }>;
    };
  };
  
  // コールバック
  callback?: {
    url?: string;                         // コールバックURL
    headers?: Record<string, string>;     // ヘッダー
  };
  
  // メタデータ
  metadata?: Record<string, any>;         // カスタムメタデータ
}

// 認識モデル
type TranscriptionModel = 
  | "whisper-large"         // OpenAI Whisper Large
  | "whisper-medium"        // OpenAI Whisper Medium
  | "whisper-small"         // OpenAI Whisper Small
  | "google-enhanced"       // Google Enhanced
  | "google-standard"       // Google Standard
  | "aws-medical"          // AWS Medical
  | "aws-standard"         // AWS Standard
  | "azure-batch"          // Azure Batch
  | "azure-realtime";      // Azure Realtime
```

### TranscriptionSegment

認識セグメント：

```typescript
interface TranscriptionSegment {
  // セグメント情報
  segment_id: string;                     // セグメントID
  segment_index: number;                  // セグメント番号
  
  // タイミング
  start_time: number;                     // 開始時間（秒）
  end_time: number;                       // 終了時間（秒）
  duration: number;                       // 長さ（秒）
  
  // テキスト
  text: string;                          // 認識テキスト
  confidence: number;                    // 信頼度（0-1）
  
  // 話者情報
  speaker_id?: string;                   // 話者ID
  speaker_label?: string;                // 話者ラベル
  
  // 言語情報
  language?: string;                     // 言語コード
  language_confidence?: number;          // 言語信頼度
  
  // 代替候補
  alternatives?: Array<{
    text: string;
    confidence: number;
  }>;
  
  // 感情・トーン
  emotion?: {
    type: EmotionType;                   // 感情タイプ
    confidence: number;                   // 信頼度
  };
  
  // 単語情報
  words?: WordTimestamp[];               // 単語タイムスタンプ
}
```

### SpeakerDiarization

話者分離結果：

```typescript
interface SpeakerDiarization {
  // 話者リスト
  speakers: Array<{
    speaker_id: string;                   // 話者ID
    speaker_label: string;                // 話者ラベル（Speaker 1等）
    
    // 話者統計
    statistics: {
      total_speaking_time: number;        // 総発話時間（秒）
      speaking_percentage: number;        // 発話割合（%）
      segment_count: number;              // セグメント数
      average_segment_duration: number;   // 平均セグメント長（秒）
    };
    
    // 音声特徴
    voice_features?: {
      gender?: "male" | "female" | "unknown";
      age_range?: string;                 // 年齢範囲
      pitch_average?: number;             // 平均ピッチ
      speaking_rate?: number;             // 発話速度
    };
    
    // 話者埋め込みベクトル
    embedding?: number[];                 // 話者埋め込み
  }>;
  
  // タイムライン
  timeline: Array<{
    start_time: number;                   // 開始時間
    end_time: number;                     // 終了時間
    speaker_id: string;                   // 話者ID
    confidence: number;                   // 信頼度
  }>;
  
  // 話者変更点
  speaker_changes: Array<{
    timestamp: number;                    // 変更時刻
    from_speaker: string;                 // 変更前話者
    to_speaker: string;                   // 変更後話者
  }>;
  
  // 重複発話
  overlaps?: Array<{
    start_time: number;
    end_time: number;
    speakers: string[];                   // 重複話者ID
  }>;
}
```

### WordTimestamp

単語タイムスタンプ：

```typescript
interface WordTimestamp {
  word: string;                           // 単語
  start_time: number;                     // 開始時間（秒）
  end_time: number;                       // 終了時間（秒）
  confidence: number;                     // 信頼度
  
  // 音声情報
  phonetic?: string;                      // 発音記号
  is_punctuation?: boolean;              // 句読点フラグ
  
  // 品詞情報
  part_of_speech?: {
    tag: string;                         // 品詞タグ
    lemma?: string;                      // 原形
  };
  
  // 話者情報
  speaker_id?: string;                   // 話者ID
}
```

## Text-to-Speech型定義

### SynthesisRequest

音声合成リクエスト：

```typescript
interface SynthesisRequest {
  // テキスト入力
  input: {
    text?: string;                        // プレーンテキスト
    ssml?: string;                        // SSML形式
    segments?: Array<{                   // セグメント別合成
      text: string;
      voice_id?: string;
      style?: string;
    }>;
  };
  
  // 音声設定
  voice: {
    voice_id?: string;                    // 音声ID
    language?: string;                    // 言語コード
    gender?: "male" | "female" | "neutral"; // 性別
    age?: "child" | "young" | "middle" | "senior"; // 年齢
    
    // カスタム音声
    custom_voice?: {
      model_id: string;                   // カスタムモデルID
      speaker_id: string;                 // 話者ID
    };
  };
  
  // 音声パラメータ
  audio_config: {
    format?: AudioOutputFormat;           // 出力形式
    sample_rate?: number;                 // サンプリングレート
    bitrate?: number;                     // ビットレート
    
    // 音声調整
    speed?: number;                       // 速度（0.5-2.0）
    pitch?: number;                       // ピッチ（-20-20）
    volume?: number;                      // 音量（0-100）
    
    // スタイル
    speaking_style?: SpeakingStyle;       // 話し方スタイル
    emotion?: EmotionType;                // 感情
    emphasis_level?: number;              // 強調レベル（0-100）
  };
  
  // 高度な設定
  advanced?: {
    enable_word_timestamps?: boolean;     // 単語タイムスタンプ
    enable_viseme?: boolean;              // 口形素情報
    enable_neural_voice?: boolean;        // ニューラル音声
    
    // 音響効果
    effects?: {
      reverb?: number;                    // リバーブ
      echo?: number;                      // エコー
      chorus?: number;                    // コーラス
    };
    
    // 背景音
    background?: {
      music_url?: string;                 // BGM URL
      music_volume?: number;              // BGM音量
      ambient_sound?: string;             // 環境音
    };
  };
  
  // ストリーミング設定
  streaming?: {
    enabled: boolean;                     // ストリーミング有効
    chunk_size_ms?: number;               // チャンクサイズ（ミリ秒）
  };
}

// 音声出力形式
type AudioOutputFormat = 
  | "mp3"
  | "wav"
  | "ogg"
  | "pcm"
  | "opus"
  | "flac";

// 話し方スタイル
type SpeakingStyle = 
  | "neutral"           // 通常
  | "cheerful"          // 明るい
  | "sad"              // 悲しい
  | "angry"            // 怒っている
  | "calm"             // 落ち着いた
  | "excited"          // 興奮した
  | "friendly"         // フレンドリー
  | "professional"     // プロフェッショナル
  | "casual"           // カジュアル
  | "serious"          // 真剣
  | "assistant"        // アシスタント
  | "newscast";        // ニュースキャスター
```

### VoiceProfile

音声プロファイル：

```typescript
interface VoiceProfile {
  // 識別情報
  voice_id: string;                       // 音声ID
  name: string;                           // 音声名
  
  // 基本属性
  language: string;                       // 主要言語
  supported_languages: string[];          // 対応言語
  gender: "male" | "female" | "neutral";  // 性別
  age_range?: string;                     // 年齢範囲
  
  // 音声特性
  characteristics: {
    pitch_range: {                        // ピッチ範囲
      min: number;
      max: number;
      default: number;
    };
    speaking_rate: {                      // 発話速度
      min: number;
      max: number;
      default: number;
    };
    tone?: string;                        // トーン（warm, cool等）
    accent?: string;                      // アクセント
  };
  
  // スタイル対応
  supported_styles: SpeakingStyle[];      // 対応スタイル
  supported_emotions: EmotionType[];      // 対応感情
  
  // プロバイダー情報
  provider: {
    name: string;                         // プロバイダー名
    model: string;                        // モデル名
    tier?: "standard" | "premium" | "neural"; // ティア
  };
  
  // サンプル
  samples?: Array<{
    text: string;                         // サンプルテキスト
    audio_url: string;                    // サンプル音声URL
    style?: SpeakingStyle;                // スタイル
  }>;
  
  // 使用制限
  limitations?: {
    max_characters_per_request?: number;  // 最大文字数/リクエスト
    max_requests_per_minute?: number;     // 最大リクエスト/分
    requires_attribution?: boolean;       // 帰属表示必要
  };
  
  // メタデータ
  is_custom: boolean;                     // カスタム音声フラグ
  is_cloned: boolean;                     // クローン音声フラグ
  created_at: string;                     // 作成日時
  updated_at: string;                     // 更新日時
}
```

### AudioFormat

音声フォーマット詳細：

```typescript
interface AudioFormat {
  // コンテナ形式
  container: AudioFileFormat;             // コンテナ形式
  
  // オーディオストリーム
  audio_stream: {
    codec: string;                        // コーデック（opus, aac等）
    sample_rate: number;                  // サンプリングレート（Hz）
    bit_depth: number;                    // ビット深度
    bitrate: number;                      // ビットレート（kbps）
    channels: number;                     // チャンネル数
    channel_layout?: string;              // チャンネルレイアウト
  };
  
  // メタデータ
  metadata?: {
    title?: string;
    artist?: string;
    album?: string;
    date?: string;
    comment?: string;
    custom?: Record<string, string>;
  };
  
  // 圧縮設定
  compression?: {
    type: "lossy" | "lossless";
    quality?: number;                     // 品質（0-100）
    vbr?: boolean;                       // 可変ビットレート
  };
}
```

### SSML

SSML（Speech Synthesis Markup Language）型定義：

```typescript
interface SSMLDocument {
  version: "1.0" | "1.1";
  lang: string;                          // 言語コード
  
  // SSMLエレメント
  elements: SSMLElement[];
}

type SSMLElement = 
  | SSMLSpeak
  | SSMLParagraph
  | SSMLSentence
  | SSMLBreak
  | SSMLEmphasis
  | SSMLProsody
  | SSMLSayAs
  | SSMLPhoneme
  | SSMLAudio;

interface SSMLSpeak {
  type: "speak";
  content: SSMLElement[];
  attributes?: {
    version?: string;
    "xml:lang"?: string;
  };
}

interface SSMLProsody {
  type: "prosody";
  content: string | SSMLElement[];
  attributes?: {
    pitch?: string;                      // +10Hz, -5st, high, low
    rate?: string;                       // slow, medium, fast, 80%
    volume?: string;                     // soft, medium, loud, +10dB
  };
}

interface SSMLBreak {
  type: "break";
  attributes?: {
    time?: string;                       // 200ms, 3s
    strength?: "none" | "x-weak" | "weak" | "medium" | "strong" | "x-strong";
  };
}

interface SSMLEmphasis {
  type: "emphasis";
  content: string;
  level?: "strong" | "moderate" | "reduced";
}
```

## リアルタイム音声処理型定義

### StreamingTranscription

ストリーミング音声認識：

```typescript
interface StreamingTranscription {
  // セッション情報
  session: {
    session_id: string;                   // セッションID
    started_at: string;                   // 開始時刻
    language?: string;                    // 言語
    sample_rate: number;                  // サンプリングレート
  };
  
  // ストリーミング設定
  config: {
    interim_results?: boolean;            // 中間結果
    continuous?: boolean;                 // 連続認識
    single_utterance?: boolean;           // 単一発話
    max_alternatives?: number;            // 最大候補数
    
    // VAD（Voice Activity Detection）
    vad?: {
      enabled: boolean;
      sensitivity?: number;               // 感度（0-1）
      speech_timeout_ms?: number;        // 発話タイムアウト
      silence_timeout_ms?: number;       // 無音タイムアウト
    };
    
    // エンドポイント検出
    endpointing?: {
      enabled: boolean;
      silence_threshold_ms?: number;     // 無音閾値
      speech_complete_timeout_ms?: number; // 発話完了タイムアウト
    };
  };
  
  // ストリーミング結果
  results: Array<{
    result_id: string;                   // 結果ID
    is_final: boolean;                   // 最終結果フラグ
    stability: number;                   // 安定性（0-1）
    
    alternatives: Array<{
      transcript: string;                // 認識テキスト
      confidence: number;                // 信頼度
      words?: WordTimestamp[];           // 単語情報
    }>;
    
    result_end_time?: number;           // 結果終了時間
    language_code?: string;             // 検出言語
    channel_tag?: number;               // チャンネルタグ
  }>;
  
  // 統計情報
  statistics?: {
    total_billed_time: number;          // 課金時間（秒）
    total_speech_time: number;          // 発話時間（秒）
    total_silence_time: number;         // 無音時間（秒）
  };
}

// WebSocket メッセージ
interface StreamingMessage {
  type: "audio" | "config" | "result" | "error" | "end";
  
  // 音声データ
  audio?: {
    content: string;                     // Base64エンコード
    encoding: "LINEAR16" | "FLAC" | "MULAW" | "AMR" | "OPUS";
    sample_rate: number;
  };
  
  // 設定更新
  config?: Partial<StreamingTranscription["config"]>;
  
  // 認識結果
  result?: StreamingTranscription["results"][0];
  
  // エラー
  error?: {
    code: string;
    message: string;
  };
}
```

### StreamingSynthesis

ストリーミング音声合成：

```typescript
interface StreamingSynthesis {
  // セッション情報
  session: {
    session_id: string;                  // セッションID
    voice_id: string;                    // 音声ID
    started_at: string;                  // 開始時刻
  };
  
  // ストリーミング設定
  config: {
    chunk_size_bytes?: number;           // チャンクサイズ
    buffer_size_ms?: number;             // バッファサイズ
    
    // オーディオ設定
    audio_format: {
      encoding: "MP3" | "OGG_OPUS" | "PCM" | "MULAW";
      sample_rate: number;
      bit_depth?: number;
    };
    
    // レイテンシ設定
    latency_optimization?: "low" | "normal" | "high";
  };
  
  // ストリーミングチャンク
  chunks: Array<{
    chunk_id: string;                   // チャンクID
    sequence: number;                   // シーケンス番号
    audio_content: string;               // Base64音声データ
    
    // タイミング情報
    text_offset?: number;                // テキストオフセット
    duration_ms?: number;                // 長さ（ミリ秒）
    
    // マーカー
    markers?: {
      word_boundaries?: Array<{
        word: string;
        start_offset: number;
        end_offset: number;
      }>;
      visemes?: Array<{                 // 口形素
        viseme: string;
        timestamp: number;
      }>;
    };
    
    is_final?: boolean;                 // 最終チャンクフラグ
  }>;
  
  // 統計情報
  statistics?: {
    total_characters: number;            // 総文字数
    total_duration_ms: number;          // 総時間（ミリ秒）
    average_latency_ms: number;         // 平均レイテンシ
  };
}
```

## 音声分析型定義

### AudioAnalysis

音声分析結果：

```typescript
interface AudioAnalysis {
  // 識別情報
  analysis_id: string;                   // 分析ID
  audio_id: string;                      // 音声ID
  
  // 基本分析
  basic_analysis: {
    duration: number;                    // 長さ（秒）
    sample_rate: number;                 // サンプリングレート
    channels: number;                    // チャンネル数
    
    // 音響特徴
    audio_features: {
      average_amplitude: number;         // 平均振幅
      peak_amplitude: number;            // ピーク振幅
      rms: number;                      // RMS（実効値）
      silence_ratio: number;            // 無音率
      snr?: number;                     // S/N比
    };
    
    // スペクトル分析
    spectral_features?: {
      dominant_frequency?: number;       // 主要周波数
      spectral_centroid?: number;       // スペクトル重心
      spectral_rolloff?: number;        // スペクトルロールオフ
      mfcc?: number[][];                // MFCC係数
    };
  };
  
  // 音声品質
  quality_assessment?: {
    overall_quality: number;             // 全体品質（0-100）
    clarity: number;                    // 明瞭度（0-100）
    
    issues?: Array<{
      type: "noise" | "clipping" | "echo" | "distortion";
      severity: "low" | "medium" | "high";
      time_ranges?: Array<{
        start: number;
        end: number;
      }>;
    }>;
    
    recommendations?: string[];          // 改善推奨事項
  };
  
  // 音声アクティビティ
  voice_activity?: {
    speech_segments: Array<{
      start_time: number;
      end_time: number;
      confidence: number;
    }>;
    total_speech_time: number;          // 総発話時間
    speech_ratio: number;               // 発話率
  };
  
  // 音楽検出
  music_detection?: {
    has_music: boolean;                 // 音楽含有
    music_segments?: Array<{
      start_time: number;
      end_time: number;
      confidence: number;
      genre?: string;                   // ジャンル
    }>;
  };
  
  // 環境音分析
  environmental_sounds?: Array<{
    sound_type: string;                 // 音タイプ（applause, laughter等）
    start_time: number;
    end_time: number;
    confidence: number;
  }>;
}
```

### EmotionDetection

感情検出：

```typescript
interface EmotionDetection {
  // 全体感情
  overall_emotion: {
    primary: EmotionType;                // 主要感情
    confidence: number;                  // 信頼度
    
    secondary?: {                       // 副次感情
      emotion: EmotionType;
      confidence: number;
    };
  };
  
  // 時系列感情
  timeline: Array<{
    start_time: number;                 // 開始時間
    end_time: number;                   // 終了時間
    emotion: EmotionType;               // 感情
    confidence: number;                 // 信頼度
    
    // 感情強度
    intensity?: {
      arousal: number;                  // 覚醒度（-1 to 1）
      valence: number;                  // 感情価（-1 to 1）
      dominance?: number;               // 支配性（-1 to 1）
    };
  }>;
  
  // 感情分布
  emotion_distribution: {
    [key in EmotionType]?: number;      // 各感情の割合（%）
  };
  
  // 感情変化
  emotion_transitions?: Array<{
    timestamp: number;                  // 変化時刻
    from_emotion: EmotionType;         // 変化前感情
    to_emotion: EmotionType;           // 変化後感情
    transition_speed: number;           // 変化速度
  }>;
}

// 感情タイプ（MAKOTO仕様準拠）
type EmotionType = 
  | "通常"          // neutral
  | "笑い"          // happy/laugh
  | "泣き"          // sad/cry
  | "考え中"        // thinking
  | "混乱"          // confused
  | "落ち込み"      // depressed
  | "自慢"          // proud
  | "驚き"          // surprised
  | "怒り"          // angry
  | "疑念"          // suspicious
  | "安心"          // relieved
  | "照れる"        // shy
  | "興奮"          // excited
  | "暗黒";         // dark
```

### LanguageIdentification

言語識別：

```typescript
interface LanguageIdentification {
  // 主要言語
  primary_language: {
    code: string;                       // 言語コード（ISO 639-1）
    name: string;                       // 言語名
    confidence: number;                 // 信頼度
    script?: string;                    // 文字体系
  };
  
  // 代替候補
  alternatives?: Array<{
    code: string;
    name: string;
    confidence: number;
  }>;
  
  // 多言語検出
  multilingual?: {
    detected: boolean;                  // 多言語検出
    
    segments?: Array<{
      start_time: number;
      end_time: number;
      language_code: string;
      confidence: number;
    }>;
    
    language_distribution?: {           // 言語分布
      [language_code: string]: number;  // 割合（%）
    };
  };
  
  // 方言・アクセント
  dialect?: {
    region?: string;                    // 地域
    accent?: string;                    // アクセント
    confidence: number;
  };
}
```

## 話者管理型定義

### Speaker

話者情報：

```typescript
interface Speaker {
  // 識別情報
  speaker_id: string;                   // 話者ID（UUID）
  tenant_id: string;                    // テナントID
  
  // 基本情報
  profile: {
    name?: string;                      // 話者名
    display_name: string;               // 表示名
    description?: string;               // 説明
    avatar_url?: string;                // アバターURL
    
    // 属性
    gender?: "male" | "female" | "unknown";
    age_range?: string;                 // 年齢範囲
    language?: string;                  // 主要言語
  };
  
  // 音声特徴
  voice_characteristics: {
    // 音響特徴
    pitch_mean: number;                 // 平均ピッチ
    pitch_std: number;                  // ピッチ標準偏差
    speaking_rate: number;              // 発話速度
    
    // 声紋
    voiceprint?: {
      embedding: number[];              // 埋め込みベクトル
      model: string;                   // モデル名
      version: string;                  // バージョン
    };
    
    // 音質
    voice_quality?: {
      clarity: number;                  // 明瞭度
      naturalness: number;              // 自然さ
      uniqueness: number;               // 独自性
    };
  };
  
  // サンプル音声
  voice_samples?: Array<{
    sample_id: string;                  // サンプルID
    audio_id: string;                   // 音声ID
    text?: string;                      // テキスト
    duration: number;                   // 長さ（秒）
    quality_score?: number;             // 品質スコア
  }>;
  
  // 統計情報
  statistics?: {
    total_utterances: number;           // 総発話数
    total_duration: number;             // 総発話時間（秒）
    average_utterance_length: number;   // 平均発話長
    last_detected: string;              // 最終検出日時
  };
  
  // クローン音声
  voice_clone?: {
    model_id: string;                   // クローンモデルID
    status: "training" | "ready" | "failed";
    quality_score?: number;             // 品質スコア
    training_samples: number;           // 学習サンプル数
  };
  
  // メタデータ
  tags?: string[];                      // タグ
  is_registered: boolean;              // 登録済みフラグ
  is_synthetic: boolean;               // 合成音声フラグ
  created_at: string;                  // 作成日時
  updated_at: string;                  // 更新日時
}
```

### VoiceCloning

音声クローニング：

```typescript
interface VoiceCloning {
  // クローニングリクエスト
  clone_request: {
    request_id: string;                 // リクエストID
    speaker_id?: string;                // 話者ID
    name: string;                       // クローン名
    
    // トレーニングデータ
    training_data: {
      audio_samples: Array<{
        audio_id: string;               // 音声ID
        transcript?: string;            // 書き起こし
        quality: "low" | "medium" | "high";
      }>;
      total_duration: number;           // 総時間（秒）
      
      requirements?: {
        min_duration: number;           // 最小時間
        min_quality: string;            // 最小品質
        language: string;               // 言語
      };
    };
    
    // クローニング設定
    config: {
      model_type: "basic" | "advanced" | "professional";
      preserve_accent?: boolean;        // アクセント保持
      preserve_emotion?: boolean;       // 感情保持
      enhance_quality?: boolean;        // 品質向上
    };
  };
  
  // クローニング結果
  clone_result: {
    model_id: string;                   // モデルID
    status: CloneStatus;                // ステータス
    
    // 品質評価
    quality_metrics?: {
      similarity_score: number;         // 類似度スコア（0-100）
      naturalness_score: number;        // 自然さスコア（0-100）
      intelligibility_score: number;    // 明瞭度スコア（0-100）
      overall_score: number;            // 総合スコア（0-100）
    };
    
    // トレーニング情報
    training_info?: {
      started_at: string;               // 開始時刻
      completed_at?: string;            // 完了時刻
      training_hours?: number;          // トレーニング時間
      iterations?: number;              // イテレーション数
      loss?: number;                   // 損失値
    };
    
    // エラー情報
    error?: {
      code: string;
      message: string;
      details?: any;
    };
  };
}

// クローンステータス
type CloneStatus = 
  | "pending"               // 待機中
  | "validating"            // 検証中
  | "training"              // トレーニング中
  | "processing"            // 処理中
  | "ready"                 // 利用可能
  | "failed"                // 失敗
  | "expired";              // 期限切れ
```

## API リクエスト/レスポンス型定義

### 音声認識

```typescript
// 音声認識開始リクエスト
interface StartTranscriptionRequest {
  audio: {                              // 音声入力（必須）
    file?: string;                      // Base64エンコード
    url?: string;                       // 音声URL
    audio_id?: string;                  // 既存音声ID
  };
  
  config?: {                           // 認識設定
    language?: string;
    model?: TranscriptionModel;
    enable_speaker_diarization?: boolean;
    enable_word_timestamps?: boolean;
  };
  
  callback_url?: string;                // コールバックURL
  metadata?: Record<string, any>;       // メタデータ
}

// 音声認識開始レスポンス
interface StartTranscriptionResponse {
  transcription_id: string;             // 認識ID
  status: "queued" | "processing";      // ステータス
  estimated_time_seconds?: number;      // 推定処理時間
  
  polling_url?: string;                 // ポーリングURL
  sse_url?: string;                     // SSE URL
}

// 音声認識結果取得レスポンス
interface GetTranscriptionResponse {
  transcription: TranscriptionResult;   // 認識結果
  
  download_urls?: {
    text?: string;                      // テキストファイル
    srt?: string;                       // SRT字幕
    vtt?: string;                       // WebVTT字幕
    json?: string;                      // JSON形式
  };
}
```

### 音声合成

```typescript
// 音声合成リクエスト
interface SynthesizeSpeechRequest {
  text: string;                         // テキスト（必須）
  
  voice?: {                            // 音声設定
    voice_id?: string;
    language?: string;
    gender?: "male" | "female";
  };
  
  audio_config?: {                     // 音声設定
    format?: AudioOutputFormat;
    speed?: number;
    pitch?: number;
    volume?: number;
  };
  
  streaming?: boolean;                  // ストリーミング
}

// 音声合成レスポンス
interface SynthesizeSpeechResponse {
  synthesis_id: string;                 // 合成ID
  
  // 非ストリーミング
  audio?: {
    content?: string;                   // Base64音声データ
    url?: string;                       // ダウンロードURL
    duration_seconds: number;           // 長さ（秒）
  };
  
  // ストリーミング
  streaming?: {
    session_id: string;                 // セッションID
    websocket_url: string;              // WebSocket URL
  };
  
  cost?: {
    characters: number;                 // 文字数
    amount: number;                     // 金額
    currency: string;                   // 通貨
  };
}
```

### 話者識別

```typescript
// 話者識別リクエスト
interface IdentifySpeakerRequest {
  audio: {                             // 音声入力（必須）
    file?: string;
    url?: string;
    audio_id?: string;
  };
  
  reference_speakers?: string[];        // 参照話者ID
  
  config?: {
    min_confidence?: number;            // 最小信頼度
    max_speakers?: number;              // 最大話者数
    enable_unknown_detection?: boolean; // 不明話者検出
  };
}

// 話者識別レスポンス
interface IdentifySpeakerResponse {
  speakers: Array<{
    speaker_id: string;                 // 話者ID
    confidence: number;                 // 信頼度
    time_ranges: Array<{               // 発話時間範囲
      start: number;
      end: number;
    }>;
    is_registered: boolean;            // 登録済みフラグ
  }>;
  
  unknown_speakers?: number;            // 不明話者数
  
  timeline: Array<{                    // タイムライン
    start_time: number;
    end_time: number;
    speaker_id: string;
  }>;
}

// 話者登録リクエスト
interface RegisterSpeakerRequest {
  name: string;                         // 話者名（必須）
  
  voice_samples: Array<{               // 音声サンプル（必須）
    audio_id?: string;
    file?: string;
    url?: string;
  }>;
  
  profile?: {                          // プロファイル
    display_name?: string;
    description?: string;
    gender?: "male" | "female";
    language?: string;
  };
  
  enable_voice_clone?: boolean;         // 音声クローン有効
}

// 話者登録レスポンス
interface RegisterSpeakerResponse {
  speaker: Speaker;                     // 話者情報
  
  voice_clone?: {
    model_id?: string;                  // クローンモデルID
    status: CloneStatus;                // ステータス
    estimated_time?: number;            // 推定時間
  };
}
```

### 音声分析

```typescript
// 音声分析リクエスト
interface AnalyzeAudioRequest {
  audio: {                             // 音声入力（必須）
    file?: string;
    url?: string;
    audio_id?: string;
  };
  
  analyses?: string[];                  // 分析タイプ
  // "quality" | "emotion" | "language" | "music" | "environment"
  
  config?: {
    emotion_granularity?: "overall" | "segment" | "word";
    quality_metrics?: string[];
  };
}

// 音声分析レスポンス
interface AnalyzeAudioResponse {
  analysis_id: string;                  // 分析ID
  
  results: {
    audio_analysis?: AudioAnalysis;     // 音声分析
    emotion?: EmotionDetection;         // 感情検出
    language?: LanguageIdentification;  // 言語識別
  };
  
  recommendations?: string[];           // 推奨事項
  processing_time_ms: number;          // 処理時間
}
```

## 更新履歴

- 2025-08-07: 初版作成
  - Speech-to-Text型定義（音声認識、話者分離、リアルタイム認識）
  - Text-to-Speech型定義（音声合成、音声プロファイル、SSML）
  - リアルタイム音声処理型定義（ストリーミング）
  - 音声分析型定義（感情検出、言語識別、品質評価）
  - 話者管理型定義（話者情報、音声クローニング）
  - API リクエスト/レスポンス型定義