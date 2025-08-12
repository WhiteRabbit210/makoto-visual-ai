from datetime import datetime
import uuid
from typing import List, Optional
from services.database import tasks_table, categories_table, TaskQuery

class TaskService:
    @staticmethod
    def initialize_sample_data():
        """サンプルデータの初期化"""
        # カテゴリの初期化
        if len(categories_table.all()) == 0:
            categories = [
                {'id': 'minutes', 'name': '議事録まとめ', 'icon': '📋', 'color': '#4A90E2'},
                {'id': 'sales', 'name': '営業相談窓口', 'icon': '📊', 'color': '#52C41A'},
                {'id': 'engineering', 'name': 'SE協業ベンダー', 'icon': '🔧', 'color': '#F5A623'},
                {'id': 'other', 'name': 'その他', 'icon': '📌', 'color': '#999999'}
            ]
            for category in categories:
                categories_table.insert(category)
        
        # タスクの初期化
        if len(tasks_table.all()) == 0:
            sample_tasks = [
                {
                    'title': '週次ミーティング議事録作成',
                    'category': 'minutes',
                    'status': 'pending',
                    'priority': 'high',
                    'description': '月曜日の週次ミーティングの議事録を作成し、関係者に共有する'
                },
                {
                    'title': '営業資料の更新',
                    'category': 'sales',
                    'status': 'in_progress',
                    'priority': 'medium',
                    'description': 'Q2の実績を反映した営業資料を更新する'
                },
                {
                    'title': 'ベンダー連携会議の準備',
                    'category': 'engineering',
                    'status': 'pending',
                    'priority': 'high',
                    'description': '来週のベンダー連携会議のアジェンダと資料を準備する'
                },
                {
                    'title': '経費精算書類の提出',
                    'category': 'other',
                    'status': 'completed',
                    'priority': 'low',
                    'description': '今月分の経費精算書類を経理部に提出する'
                }
            ]
            
            for task_data in sample_tasks:
                task_id = str(uuid.uuid4())
                task = {
                    'id': task_id,
                    'title': task_data['title'],
                    'description': task_data.get('description'),
                    'category': task_data['category'],
                    'status': task_data['status'],
                    'priority': task_data['priority'],
                    'due_date': None,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                tasks_table.insert(task)

    @staticmethod
    def get_categories():
        """全カテゴリを取得"""
        return categories_table.all()
    
    @staticmethod
    def get_tasks(category: Optional[str] = None, status: Optional[str] = None):
        """タスクを取得（フィルタリング可能）"""
        if category and status:
            return tasks_table.search((TaskQuery.category == category) & (TaskQuery.status == status))
        elif category:
            return tasks_table.search(TaskQuery.category == category)
        elif status:
            return tasks_table.search(TaskQuery.status == status)
        return tasks_table.all()
    
    @staticmethod
    def get_task(task_id: str):
        """特定のタスクを取得"""
        tasks = tasks_table.search(TaskQuery.id == task_id)
        return tasks[0] if tasks else None
    
    @staticmethod
    def create_task(title: str, category: str, description: Optional[str] = None,
                   priority: str = 'medium', due_date: Optional[str] = None):
        """タスクを作成"""
        task_id = str(uuid.uuid4())
        task = {
            'id': task_id,
            'title': title,
            'description': description,
            'category': category,
            'status': 'pending',
            'priority': priority,
            'due_date': due_date,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        tasks_table.insert(task)
        return task
    
    @staticmethod
    def update_task(task_id: str, update_data: dict):
        """タスクを更新"""
        update_data['updated_at'] = datetime.now().isoformat()
        tasks_table.update(update_data, TaskQuery.id == task_id)
        return TaskService.get_task(task_id)
    
    @staticmethod
    def delete_task(task_id: str):
        """タスクを削除"""
        tasks_table.remove(TaskQuery.id == task_id)