import os
import asyncio
import aiohttp
from typing import List, Dict, Optional
import json
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse
import re
from openai import AzureOpenAI
from dotenv import load_dotenv
from utils.logger import log_api_request, log_api_response, log_error
import time

load_dotenv()

# Azure OpenAIクライアントを初期化
azure_client = AzureOpenAI(
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

class WebCrawlerService:
    """Webクロールとコンテンツ要約サービス"""
    
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")
        self.max_search_results = 5
        self.max_content_length = 5000  # 1ページあたりの最大文字数
        self.use_mock = os.getenv("USE_WEB_SEARCH_MOCK", "false").lower() == "true"
        self.mock_data = None
        if self.use_mock:
            self._load_mock_data()
    
    def _load_mock_data(self):
        """モックデータを読み込む"""
        try:
            mock_file_path = os.path.join("data", "web_search_mock.json")
            with open(mock_file_path, "r", encoding="utf-8") as f:
                self.mock_data = json.load(f)
                log_api_response("WebCrawlerService", 200, {"mock_data_loaded": True})
        except Exception as e:
            log_error("Mock Data Load Error", str(e), "_load_mock_data")
            self.mock_data = None
    
    def _get_mock_response(self, keywords: List[str]) -> Dict[str, any]:
        """モックレスポンスを取得する"""
        if not self.mock_data:
            return None
        
        # キーワードが一致するモックレスポンスを探す
        for mock in self.mock_data.get("mock_responses", []):
            if set(mock["keywords"]) == set(keywords):
                return mock["response"]
        
        # デフォルトレスポンスを返す
        return self.mock_data.get("default_response")
        
    async def search_and_crawl(self, keywords: List[str], original_query: str, skip_summary: bool = False) -> Dict[str, any]:
        """
        Google検索を実行し、上位サイトをクロールして内容を要約
        
        Args:
            keywords: 検索キーワードのリスト
            original_query: 元のユーザー質問
            
        Returns:
            クロール結果と要約を含む辞書
        """
        try:
            # モックモードの場合はモックデータを返す
            if self.use_mock:
                mock_response = self._get_mock_response(keywords)
                if mock_response:
                    log_api_response("search_and_crawl", 200, {"mock_mode": True, "keywords": keywords})
                    return mock_response
            # 1. Google検索を実行
            search_results = await self._google_search(keywords)
            
            if not search_results:
                return {
                    "success": False,
                    "error": "検索結果が見つかりませんでした",
                    "crawled_contents": [],
                    "sources": []
                }
            
            # 2. 各URLの内容をクロール
            crawled_contents = []
            sources = []
            
            # コネクター設定（同時接続数を増やす）
            connector = aiohttp.TCPConnector(
                limit=30,  # 同時接続数の制限
                limit_per_host=5,  # ホストごとの同時接続数
                force_close=True
            )
            
            async with aiohttp.ClientSession(connector=connector) as session:
                tasks = []
                for result in search_results[:self.max_search_results]:
                    task = self._crawl_url(session, result['link'], result['title'])
                    tasks.append(task)
                
                crawled_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(crawled_results):
                    if isinstance(result, Exception):
                        log_error(f"クロールエラー: {search_results[i]['link']}", str(result), "web_crawler")
                        continue
                    
                    if result and result.get('content'):
                        crawled_contents.append(result)
                        sources.append({
                            "url": search_results[i]['link'],
                            "title": search_results[i]['title'],
                            "snippet": search_results[i].get('snippet', '')
                        })
            
            # 3. クロール内容を要約（スキップ可能）
            if crawled_contents and not skip_summary:
                summary = await self._summarize_contents(crawled_contents, original_query)
            elif crawled_contents:
                summary = "要約はスキップされました"
            else:
                summary = None
            
            return {
                "success": True,
                "search_keywords": keywords,
                "crawled_contents": crawled_contents,
                "sources": sources,
                "summary": summary
            }
            
        except Exception as e:
            log_error("Web Crawler Error", str(e), "search_and_crawl")
            return {
                "success": False,
                "error": str(e),
                "crawled_contents": [],
                "sources": []
            }
    
    async def _google_search(self, keywords: List[str]) -> List[Dict]:
        """Google Custom Search APIを使用して検索"""
        try:
            if not self.google_api_key or not self.google_cse_id:
                # APIキーがない場合はダミーデータを返す（開発用）
                log_error("Google API未設定", "Google APIキーまたはCSE IDが設定されていません", "_google_search")
                return self._get_dummy_search_results(keywords)
            
            search_query = " ".join(keywords)
            url = f"https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.google_api_key,
                "cx": self.google_cse_id,
                "q": search_query,
                "num": self.max_search_results,
                "hl": "ja"
            }
            
            # デバッグ情報をログ出力（詳細出力を削減）
            # print(f"Google Search Request: {url}")
            # print(f"Params: {params}")
            # print(f"API Key: {self.google_api_key[:10]}...")
            # print(f"CSE ID: {self.google_cse_id}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('items', [])
                    else:
                        error_text = await response.text()
                        log_error("Google Search API Error", f"Status: {response.status}, Error: {error_text}", "_google_search")
                        return []
                        
        except Exception as e:
            log_error("Google Search Exception", str(e), "_google_search")
            return []
    
    def _get_dummy_search_results(self, keywords: List[str]) -> List[Dict]:
        """開発用のダミー検索結果"""
        return [
            {
                "title": f"{' '.join(keywords)} - Wikipedia",
                "link": f"https://ja.wikipedia.org/wiki/{quote_plus(keywords[0])}",
                "snippet": f"{keywords[0]}に関する詳細な情報を提供しています。"
            },
            {
                "title": f"{keywords[0]}の最新情報 | ニュースサイト",
                "link": f"https://news.example.com/{quote_plus(keywords[0])}",
                "snippet": f"最新の{keywords[0]}に関するニュースと分析。"
            }
        ]
    
    async def _crawl_url(self, session: aiohttp.ClientSession, url: str, title: str) -> Dict:
        """指定されたURLの内容をクロール"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # タイムアウトを短縮（10秒→3秒）
            timeout = aiohttp.ClientTimeout(total=3)
            async with session.get(url, headers=headers, timeout=timeout) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # スクリプトとスタイルを除去
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # メインコンテンツを抽出
                content = self._extract_main_content(soup)
                
                # 内容を制限
                if len(content) > self.max_content_length:
                    content = content[:self.max_content_length] + "..."
                
                return {
                    "url": url,
                    "title": title,
                    "content": content
                }
                
        except Exception as e:
            log_error(f"URL Crawl Error: {url}", str(e), "_crawl_url")
            return None
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """ページから主要なコンテンツを抽出"""
        # 一般的なコンテンツコンテナを探す
        content_selectors = [
            'main', 'article', '[role="main"]',
            '.main-content', '#main-content',
            '.content', '#content',
            '.article-body', '.post-content'
        ]
        
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                text = content.get_text(separator='\n', strip=True)
                if len(text) > 100:  # 意味のあるコンテンツ
                    return text
        
        # 見つからない場合はbodyから抽出
        body = soup.find('body')
        if body:
            text = body.get_text(separator='\n', strip=True)
            # 冗長な空白を削除
            text = re.sub(r'\n+', '\n', text)
            text = re.sub(r' +', ' ', text)
            return text
        
        return ""
    
    async def _summarize_contents(self, contents: List[Dict], query: str) -> str:
        """クロールした内容を要約"""
        try:
            # コンテンツを結合
            combined_content = "\n\n---\n\n".join([
                f"【{c['title']}】\nURL: {c['url']}\n内容:\n{c['content'][:1000]}"
                for c in contents
            ])
            
            # 要約プロンプト
            messages = [
                {
                    "role": "system",
                    "content": "あなたは検索結果を要約する専門家です。提供された情報から、ユーザーの質問に関連する重要な情報を抽出し、簡潔にまとめてください。"
                },
                {
                    "role": "user",
                    "content": f"""以下の検索結果から、次の質問に答えるための重要な情報を抽出してください：

質問: {query}

検索結果:
{combined_content}

重要なポイントを箇条書きでまとめ、情報源も明記してください。"""
                }
            ]
            
            response = azure_client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "MAKOTO-gpt-5"),
                messages=messages,
                # temperature=0.3,  # GPT-5はデフォルト値(1)のみサポート
                max_completion_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            log_error("Content Summarization Error", str(e), "_summarize_contents")
            return "要約の生成に失敗しました。"

# シングルトンインスタンス
web_crawler_service = WebCrawlerService()