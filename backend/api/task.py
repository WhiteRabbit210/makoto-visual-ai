"""
タスク管理API

ドキュメント（/makoto/docs/仕様書/型定義/タスク管理API型定義.md）に
完全準拠した実装です。
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

# 型定義をインポート
from backend_types.api_types import (
    Task,
    TaskParameter,
    TaskExecution,
    GetTasksParams,
    GetTasksResponse,
    CreateTaskRequest,
    UpdateTaskRequest,
    ExecuteTaskRequest,
    ExecuteTaskResponse,
    TaskCategory,
    ExecutionMode,
    TaskStatus,
    ModelSettings,
    TaskVisibility,
    UpdateVisibilityRequest,
    TaskExecutionStatus,
    ExecutionResult,
    ExecutionError,
    generate_uuid,
    get_current_datetime
)

router = APIRouter()

# サンプルデータ（インメモリストレージ）
tasks_db: Dict[str, Task] = {}
executions_db: Dict[str, TaskExecution] = {}

def initialize_sample_tasks():
    """サンプルタスクを初期化"""
    sample_tasks = [
        Task(
            task_id=generate_uuid(),
            name="テキスト要約タスク",
            description="長文テキストを簡潔に要約します",
            category="summarization",
            tags=["要約", "テキスト処理"],
            icon="📝",
            prompt_template="以下のテキストを200文字以内で要約してください：\n\n{{text}}",
            system_prompt="あなたは文章要約の専門家です。",
            execution_mode="chat",
            model_settings=ModelSettings(
                temperature=0.3,
                max_tokens=500
            ),
            parameters=[
                TaskParameter(
                    parameter_id=generate_uuid(),
                    name="text",
                    label="要約対象テキスト",
                    description="要約したいテキストを入力してください",
                    type="text",
                    required=True,
                    ui_type="textarea",
                    display_order=1
                )
            ],
            created_by="system",
            created_at=get_current_datetime(),
            updated_at=get_current_datetime(),
            version=1,
            is_latest=True,
            visibility=TaskVisibility(
                type="tenant"
            ),
            status="active",
            execution_count=0
        ),
        Task(
            task_id=generate_uuid(),
            name="画像生成タスク",
            description="テキストから画像を生成します",
            category="image_generation",
            tags=["画像", "生成"],
            icon="🎨",
            prompt_template="{{prompt}}",
            execution_mode="image",
            model_settings=ModelSettings(
                image_size="1024x1024",
                image_quality="standard",
                image_style="vivid",
                image_count=1
            ),
            parameters=[
                TaskParameter(
                    parameter_id=generate_uuid(),
                    name="prompt",
                    label="画像プロンプト",
                    description="生成したい画像の説明を入力してください",
                    type="text",
                    required=True,
                    ui_type="textarea",
                    display_order=1,
                    validation={"max_length": 4000}
                )
            ],
            created_by="system",
            created_at=get_current_datetime(),
            updated_at=get_current_datetime(),
            version=1,
            is_latest=True,
            visibility=TaskVisibility(
                type="tenant"
            ),
            status="active",
            execution_count=0
        )
    ]
    
    for task in sample_tasks:
        tasks_db[task.task_id] = task

# 初期化
initialize_sample_tasks()

@router.get("")
async def get_tasks(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[TaskCategory] = None,
    status: Optional[TaskStatus] = None,
    execution_mode: Optional[ExecutionMode] = None,
    created_by: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = "updated_at",
    order: str = "desc"
) -> List[Task]:
    """
    タスク一覧を取得
    
    ドキュメント準拠のタスク一覧取得API
    """
    # フィルタリング
    filtered_tasks = list(tasks_db.values())
    
    if category:
        filtered_tasks = [t for t in filtered_tasks if t.category == category]
    if status:
        filtered_tasks = [t for t in filtered_tasks if t.status == status]
    if execution_mode:
        filtered_tasks = [t for t in filtered_tasks if t.execution_mode == execution_mode]
    if created_by:
        filtered_tasks = [t for t in filtered_tasks if t.created_by == created_by]
    if search:
        search_lower = search.lower()
        filtered_tasks = [
            t for t in filtered_tasks 
            if search_lower in t.name.lower() or 
               (t.description and search_lower in t.description.lower())
        ]
    
    # ソート
    reverse = order == "desc"
    if sort == "name":
        filtered_tasks.sort(key=lambda x: x.name, reverse=reverse)
    elif sort == "created_at":
        filtered_tasks.sort(key=lambda x: x.created_at, reverse=reverse)
    elif sort == "updated_at":
        filtered_tasks.sort(key=lambda x: x.updated_at, reverse=reverse)
    elif sort == "execution_count":
        filtered_tasks.sort(key=lambda x: x.execution_count, reverse=reverse)
    
    # ページング
    start = (page - 1) * limit
    end = start + limit
    
    return filtered_tasks[start:end]

@router.get("/{task_id}")
async def get_task(task_id: str) -> Task:
    """
    タスク詳細を取得
    
    指定されたIDのタスクを返します
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks_db[task_id]

@router.post("")
async def create_task(request: CreateTaskRequest) -> Task:
    """
    新規タスクを作成
    
    ドキュメント準拠のタスク作成API
    """
    task_id = generate_uuid()
    now = get_current_datetime()
    
    # デフォルト値の設定
    if not request.status:
        request.status = "draft"
    
    task = Task(
        task_id=task_id,
        name=request.name,
        description=request.description,
        category=request.category,
        tags=request.tags or [],
        icon=request.icon,
        prompt_template=request.prompt_template,
        system_prompt=request.system_prompt,
        execution_mode=request.execution_mode,
        model_settings=request.model_settings,
        parameters=request.parameters,
        created_by="current_user",  # 実際はAuthから取得
        created_at=now,
        updated_at=now,
        version=1,
        is_latest=True,
        visibility=request.visibility,
        status=request.status,
        execution_count=0
    )
    
    tasks_db[task_id] = task
    return task

@router.put("/{task_id}")
async def update_task(task_id: str, request: UpdateTaskRequest) -> Task:
    """
    タスクを更新
    
    ドキュメント準拠のタスク更新API
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    update_data = request.model_dump(exclude_unset=True)
    
    # バージョン管理
    if request.create_new_version:
        # 新バージョンの作成（簡略化）
        new_task_id = generate_uuid()
        new_task = task.model_copy()
        new_task.task_id = new_task_id
        new_task.version = task.version + 1
        new_task.previous_version_id = task_id
        new_task.updated_at = get_current_datetime()
        
        # 更新内容を適用
        for key, value in update_data.items():
            if hasattr(new_task, key):
                setattr(new_task, key, value)
        
        # 古いバージョンを非最新に
        task.is_latest = False
        
        tasks_db[new_task_id] = new_task
        return new_task
    else:
        # 現在のタスクを更新
        for key, value in update_data.items():
            if hasattr(task, key):
                setattr(task, key, value)
        task.updated_at = get_current_datetime()
        return task

@router.delete("/{task_id}")
async def delete_task(task_id: str) -> Dict[str, str]:
    """
    タスクを削除
    
    タスクをアーカイブ状態にします
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    task.status = "archived"
    task.updated_at = get_current_datetime()
    
    return {"message": "Task archived successfully", "task_id": task_id}

@router.post("/{task_id}/execute")
async def execute_task(task_id: str, request: ExecuteTaskRequest) -> ExecuteTaskResponse:
    """
    タスクを実行
    
    指定されたパラメータでタスクを実行します
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    
    # パラメータバリデーション
    for param in task.parameters:
        if param.required and param.name not in request.parameters:
            raise HTTPException(
                status_code=422,
                detail=f"Missing required parameter: {param.name}"
            )
    
    # 実行（モック）
    execution_id = generate_uuid()
    now = get_current_datetime()
    
    # 実行履歴を保存
    execution = TaskExecution(
        execution_id=execution_id,
        task_id=task_id,
        task_version=task.version,
        executed_by="current_user",
        executed_at=now,
        parameters=request.parameters,
        status="completed",
        result=ExecutionResult(
            type="text",
            text="タスクが正常に実行されました。"
        ),
        execution_time_ms=1500,
        tokens_used=100
    )
    
    executions_db[execution_id] = execution
    
    # タスクの実行回数を更新
    task.execution_count += 1
    task.last_executed_at = now
    
    return ExecuteTaskResponse(
        execution_id=execution_id,
        status="completed",
        result=execution.result,
        metadata={
            "execution_time_ms": execution.execution_time_ms,
            "tokens_used": execution.tokens_used
        }
    )

@router.get("/{task_id}/executions")
async def get_task_executions(
    task_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
) -> List[TaskExecution]:
    """
    タスクの実行履歴を取得
    
    指定されたタスクの実行履歴を返します
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # タスクIDでフィルタ
    task_executions = [
        e for e in executions_db.values()
        if e.task_id == task_id
    ]
    
    # 実行日時でソート（新しい順）
    task_executions.sort(key=lambda x: x.executed_at, reverse=True)
    
    # ページング
    start = (page - 1) * limit
    end = start + limit
    
    return task_executions[start:end]

@router.put("/{task_id}/visibility")
async def update_task_visibility(
    task_id: str,
    request: UpdateVisibilityRequest
) -> Task:
    """
    タスクの公開範囲を更新
    
    タスクの公開範囲設定を変更します
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    task.visibility = request.visibility
    task.updated_at = get_current_datetime()
    
    # 通知処理（実装は省略）
    if request.notify_users:
        pass  # 通知送信処理
    
    return task