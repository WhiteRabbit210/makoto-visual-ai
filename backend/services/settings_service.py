from typing import Dict, Any, Optional
from services.database import settings_table, SettingsQuery

class SettingsService:
    # デフォルト設定
    DEFAULT_SETTINGS = {
        'general': {
            'language': 'ja',
            'timezone': 'Asia/Tokyo',
            'auto_save': True,
            'auto_save_interval': 5
        },
        'appearance': {
            'theme': 'light',
            'font_size': 'medium',
            'sidebar_collapsed': False,
            'animations': True
        },
        'ai': {
            'model': 'gpt-4.1',
            'temperature': 0.7,
            'max_tokens': 2000,
            'stream_response': True
        },
        'notifications': {
            'desktop': True,
            'sound': True,
            'email': False,
            'task_reminders': True
        }
    }

    @staticmethod
    def initialize_settings():
        """設定の初期化"""
        # 各カテゴリごとに設定を保存
        for category, settings in SettingsService.DEFAULT_SETTINGS.items():
            if not settings_table.search(SettingsQuery.category == category):
                settings_table.insert({
                    'category': category,
                    'settings': settings
                })

    @staticmethod
    def get_all_settings():
        """全設定を取得"""
        settings_records = settings_table.all()
        result = {}
        
        # カテゴリごとの設定を結合
        for record in settings_records:
            result[record['category']] = record['settings']
        
        # デフォルト設定で不足分を補完
        for category, default_settings in SettingsService.DEFAULT_SETTINGS.items():
            if category not in result:
                result[category] = default_settings
        
        return result

    @staticmethod
    def get_category_settings(category: str):
        """カテゴリ別の設定を取得"""
        records = settings_table.search(SettingsQuery.category == category)
        
        if records:
            return records[0]['settings']
        elif category in SettingsService.DEFAULT_SETTINGS:
            return SettingsService.DEFAULT_SETTINGS[category]
        else:
            return None

    @staticmethod
    def update_category_settings(category: str, settings: Dict[str, Any]):
        """カテゴリ別の設定を更新"""
        if category not in SettingsService.DEFAULT_SETTINGS:
            return False
        
        # 既存のレコードを更新または新規作成
        if settings_table.search(SettingsQuery.category == category):
            settings_table.update(
                {'settings': settings},
                SettingsQuery.category == category
            )
        else:
            settings_table.insert({
                'category': category,
                'settings': settings
            })
        
        return True

    @staticmethod
    def reset_settings():
        """設定をデフォルトにリセット"""
        # 全設定を削除
        settings_table.truncate()
        
        # デフォルト設定で初期化
        SettingsService.initialize_settings()
        
        return SettingsService.get_all_settings()