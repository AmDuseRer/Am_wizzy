"""
第 3 层 · 数据模型（Model）

这一层描述「一条待办在系统里长什么样」。
它不是数据库表，也不是 JSON，而是程序内部用的数据结构。

类比：员工档案里的「一条记录」—— id、标题、是否完成。
"""

from dataclasses import dataclass


@dataclass
class Todo:
    """待办事项（领域对象）"""

    id: int
    title: str
    done: bool = False
