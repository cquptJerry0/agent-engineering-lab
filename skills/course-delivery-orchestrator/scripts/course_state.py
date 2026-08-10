#!/usr/bin/env python3
"""Inspect generated CU directories without assuming a fixed course catalog."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


CU_DIR_RE = re.compile(r"^CU-(\d{3})(?:-(.+))?$", re.IGNORECASE)
STATUS_RE = re.compile(
    r"CU\s*状态\s*[：:]\s*(未开始|推导中|面试训练中|待复核|已通过)"
)
KNOWLEDGE_ROW_RE = re.compile(r"^\|\s*\d+\s*\|\s*([^|]+?)\s*\|", re.MULTILINE)
COMPLETED = {"已通过"}


@dataclass
class CourseUnit:
    id: str
    title: str
    status: str
    knowledge_points: int
    learning: str
    interview: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="扫描实际生成的 CU，输出双轨状态和建议继续位置。"
    )
    parser.add_argument("course_root", type=Path, help="包含 CU-* 目录的课程根目录")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    return parser.parse_args()


def read_units(root: Path) -> list[CourseUnit]:
    units: list[CourseUnit] = []
    for directory in sorted(path for path in root.iterdir() if path.is_dir()):
        match = CU_DIR_RE.match(directory.name)
        if match is None:
            continue

        learning = directory / "推导式理解.md"
        if not learning.is_file():
            continue

        text = learning.read_text(encoding="utf-8")
        status_match = STATUS_RE.search(text)
        status = status_match.group(1) if status_match else "状态缺失"
        points = {
            point.strip()
            for point in KNOWLEDGE_ROW_RE.findall(text)
        }
        interview = directory / "面试训练.md"
        units.append(
            CourseUnit(
                id=f"CU-{match.group(1)}",
                title=(match.group(2) or "").replace("-", " "),
                status=status,
                knowledge_points=len(points),
                learning=str(learning),
                interview=str(interview) if interview.is_file() else None,
            )
        )
    return units


def main() -> int:
    args = parse_args()
    root = args.course_root.expanduser().resolve()
    if not root.is_dir():
        print(f"[ERROR] 课程目录不存在: {root}", file=sys.stderr)
        return 2

    units = read_units(root)
    current = next((unit for unit in units if unit.status not in COMPLETED), None)
    if current is None:
        next_action = "根据学习进度动态生成下一 CU"
    elif current.status == "未开始":
        next_action = f"开始 {current.id} 的推导式理解"
    elif current.status == "待复核":
        next_action = f"复核 {current.id} 并决定是否写回进度"
    else:
        next_action = f"继续 {current.id} 的{current.status}阶段"

    summary = {
        "course_root": str(root),
        "total": len(units),
        "completed": sum(unit.status in COMPLETED for unit in units),
        "current": asdict(current) if current else None,
        "next_action": next_action,
        "units": [asdict(unit) for unit in units],
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    print(f"已生成 CU: {summary['total']}")
    print(f"已通过 CU: {summary['completed']}")
    print(f"建议下一步: {summary['next_action']}")
    if current:
        print(f"覆盖知识点: {current.knowledge_points}")
        print(f"推导式理解: {current.learning}")
        print(f"面试训练: {current.interview or '尚未生成'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
