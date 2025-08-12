from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.task_template_service import TaskTemplateService

router = APIRouter()

# Models
class TaskTemplate(BaseModel):
    id: str
    name: str
    description: str
    prompt: str
    category: str
    created_at: str
    updated_at: str

class TaskTemplateResponse(BaseModel):
    templates: List[TaskTemplate]

# Initialize default templates
TaskTemplateService.initialize_default_templates()

@router.get("/task-templates", response_model=TaskTemplateResponse)
async def get_all_task_templates():
    """全てのタスクテンプレートを取得"""
    templates = TaskTemplateService.get_all_templates()
    return TaskTemplateResponse(templates=templates)

@router.get("/task-templates/{template_id}", response_model=TaskTemplate)
async def get_task_template(template_id: str):
    """特定のタスクテンプレートを取得"""
    template = TaskTemplateService.get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="タスクテンプレートが見つかりません")
    return template

@router.get("/task-templates/category/{category}", response_model=TaskTemplateResponse)
async def get_task_templates_by_category(category: str):
    """カテゴリー別にタスクテンプレートを取得"""
    templates = TaskTemplateService.get_templates_by_category(category)
    return TaskTemplateResponse(templates=templates)