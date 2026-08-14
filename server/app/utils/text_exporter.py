"""
备忘录 TXT 导出工具
使用 UTF-8 BOM 编码，确保 Windows 记事本正确显示中文
"""

from app.models.memo import Memo


def _category_label(category_id: int | None, category_map: dict[int, str]) -> str:
    if not category_id:
        return "未分类"
    return category_map.get(category_id, "未分类")


def _format_memo(memo: Memo, category_map: dict[int, str]) -> str:
    lines = [
        f"标题：{memo.title}",
        f"分类：{_category_label(memo.category_id, category_map)}",
        f"创建时间：{memo.created_at.strftime('%Y-%m-%d %H:%M')}",
        f"更新时间：{memo.updated_at.strftime('%Y-%m-%d %H:%M')}",
    ]
    if memo.is_pinned:
        lines.append("置顶：是")
    lines.extend(["", "内容：", memo.content or ""])
    return "\n".join(lines)


def generate_memo_txt(memo: Memo, category_map: dict[int, str]) -> bytes:
    """生成单条备忘录 TXT"""
    return _format_memo(memo, category_map).encode("utf-8-sig")


def generate_memos_txt(memos: list[Memo], category_map: dict[int, str]) -> bytes:
    """批量生成备忘录 TXT"""
    parts = []
    for index, memo in enumerate(memos, start=1):
        header = f"{'=' * 20} 备忘录 {index}/{len(memos)} {'=' * 20}"
        parts.append(f"{header}\n{_format_memo(memo, category_map)}")
    return "\n\n".join(parts).encode("utf-8-sig")
