#!/usr/bin/env python3
"""Validate a dynamic, dual-track course design."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
SCHEDULED_LESSON_RE = re.compile(
    r"^#{2,4}\s+(?:第\s*)?\d{1,3}\s*(?:课|讲|节|lesson)\b",
    re.IGNORECASE | re.MULTILINE,
)
CU_RE = re.compile(r"\bCU-\d{3}\b", re.IGNORECASE)

REQUIRED_CONCEPTS = {
    "知识真相源": (r"学习总纲", r"知识总纲"),
    "动态学习状态": (r"学习进度", r"薄弱点"),
    "动态选课": (r"动态选课", r"选课依据", r"选择过程"),
    "知识覆盖": (r"覆盖知识点", r"知识覆盖", r"共覆盖"),
    "中心问题": (r"中心问题", r"完整问题"),
    "贯穿案例": (r"贯穿案例",),
    "因果推导": (r"推导链", r"已有能力.*暴露问题"),
    "理解轨": (r"推导式理解",),
    "面试轨": (r"面试训练",),
    "状态写回": (r"状态更新", r"状态写回", r"不更新进度"),
    "动态续课": (r"下一\s*CU", r"重新计算", r"动态决定"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="校验动态选课、链路学习、双轨产物和状态写回合同。"
    )
    parser.add_argument("course_file", type=Path, help="课程入口或设计 Markdown 文件")
    parser.add_argument(
        "--allow-scheduled-catalog",
        action="store_true",
        help="允许用户明确要求的完整暂定排期",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="将缺少核心合同、本地链接和固定排期问题视为错误",
    )
    return parser.parse_args()


def validate_links(course_file: Path, text: str) -> list[str]:
    errors: list[str] = []
    for target in LINK_RE.findall(text):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        local_path = target.split("#", 1)[0]
        if local_path and not (course_file.parent / local_path).exists():
            errors.append(f"本地链接不存在: {target}")
    return errors


def main() -> int:
    args = parse_args()
    if not args.course_file.is_file():
        print(f"[ERROR] 课程文件不存在: {args.course_file}")
        return 2

    text = args.course_file.read_text(encoding="utf-8")
    errors: list[str] = []
    warnings: list[str] = []

    for concept, patterns in REQUIRED_CONCEPTS.items():
        if not any(re.search(pattern, text, re.IGNORECASE | re.DOTALL) for pattern in patterns):
            message = f"缺少动态课程合同: {concept}"
            (errors if args.strict else warnings).append(message)

    scheduled_lessons = len(SCHEDULED_LESSON_RE.findall(text))
    if scheduled_lessons >= 3 and not args.allow_scheduled_catalog:
        errors.append(
            "识别到完整固定课表；默认应只设计当前 CU。"
            "若用户明确要求公开课排期，请使用 --allow-scheduled-catalog。"
        )

    if args.allow_scheduled_catalog and scheduled_lessons:
        snapshot_markers = ("暂定", "重排条件", "生成时间")
        missing = [marker for marker in snapshot_markers if marker not in text]
        if missing:
            errors.append(f"完整排期缺少快照声明: {missing}")

    cu_ids = CU_RE.findall(text)

    link_errors = validate_links(args.course_file, text)
    (errors if args.strict else warnings).extend(link_errors)

    for warning in warnings:
        print(f"[WARNING] {warning}")
    for error in errors:
        print(f"[ERROR] {error}")

    print(
        f"检查完成: {scheduled_lessons} 个固定课标题, "
        f"{len(set(cu_id.upper() for cu_id in cu_ids))} 个 CU 引用, "
        f"{len(errors)} 个错误, {len(warnings)} 个提醒。"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
