"""
备忘录 API 路由
"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.exceptions import success
from app.models.user import User
from app.schemas.memo import MemoCreateRequest, MemoResponse, MemoUpdateRequest
from app.services import category_service, memo_service
from app.utils.text_exporter import generate_memo_txt, generate_memos_txt

router = APIRouter()

async def _memo_category_map(db: AsyncSession, user: User) -> dict[int, str]:
    categories = await category_service.list_categories(db, user, "memo")
    return {cat.id: cat.name for cat in categories}


@router.get("")
async def list_memos(
    keyword: str | None = None,
    category_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """分页查询备忘录"""
    memos, total = await memo_service.list_memos(
        db, current_user, keyword, category_id, page, page_size
    )
    return success({
        "items": [MemoResponse.model_validate(m).model_dump() for m in memos],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/export/all-txt")
async def export_all_memos_txt(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """导出全部备忘录 TXT"""
    memos, _ = await memo_service.list_memos(db, current_user, page=1, page_size=1000)
    category_map = await _memo_category_map(db, current_user)
    txt_bytes = generate_memos_txt(memos, category_map)
    return StreamingResponse(
        io.BytesIO(txt_bytes),
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="memos_export.txt"'},
    )


@router.get("/{memo_id}")
async def get_memo(
    memo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取单条备忘录"""
    memo = await memo_service.get_memo(db, current_user, memo_id)
    return success(MemoResponse.model_validate(memo).model_dump())


@router.post("")
async def create_memo(
    req: MemoCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建备忘录"""
    memo = await memo_service.create_memo(db, current_user, req)
    return success(MemoResponse.model_validate(memo).model_dump(), "创建成功")


@router.put("/{memo_id}")
async def update_memo(
    memo_id: int,
    req: MemoUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新备忘录"""
    memo = await memo_service.update_memo(db, current_user, memo_id, req)
    return success(MemoResponse.model_validate(memo).model_dump(), "更新成功")


@router.delete("/{memo_id}")
async def delete_memo(
    memo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除备忘录"""
    await memo_service.delete_memo(db, current_user, memo_id)
    return success(message="删除成功")


@router.get("/{memo_id}/export-txt")
async def export_memo_txt(
    memo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """导出单条备忘录 TXT"""
    memo = await memo_service.get_memo(db, current_user, memo_id)
    category_map = await _memo_category_map(db, current_user)
    txt_bytes = generate_memo_txt(memo, category_map)
    return StreamingResponse(
        io.BytesIO(txt_bytes),
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="memo_{memo_id}.txt"'},
    )
