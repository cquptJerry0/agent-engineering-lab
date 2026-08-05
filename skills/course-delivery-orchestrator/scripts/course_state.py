#!/usr/bin/env python3
"""Inspect a Markdown course catalog and lesson artifact states."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


CATALOG_LESSON_RE = re.compile(
    r"^#{2,4}\s+第\s*(\d{1,3})\s*课\s*[：:.\-]?\s*(.+?)\s*$"
)
ARTIFACT_HEADING_RE = re.compile(
    r"^#{1,4}\s+第\s*(\d{1,3})"
    r"(?:\s*[-—~至]\s*(\d{1,3}))?"
    r"\s*课\s*[：:.\-]?\s*(.+?)\s*$"
)
COVERAGE_RE = re.compile(
    r"覆盖课程\s*[：:]\s*(.+)"
)
NUMBER_RE = re.compile(r"第?\s*(\d{1,3})\s*课?")
STATUS_RE = re.compile(
    r"课程状态\s*[：:]\s*(进行中|待复核|已通过|未开始|已完成|已复核)"
)
COMPLETED = {"已通过", "已完成", "已复核"}


@dataclass
class Lesson:
    number: int
    title: str
    status: str
    artifact: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="读取课程目录和课件目录，输出课程状态与建议继续位置。"
    )
    parser.add_argument("catalog", type=Path, help="课程目录 Markdown 文件")
    parser.add_argument(
        "--lessons-dir",
        type=Path,
        help="正式课件目录；不存在时所有课程视为未开始",
    )
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    return parser.parse_args()


def parse_catalog(path: Path) -> list[tuple[int, str]]:
    lessons: list[tuple[int, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = CATALOG_LESSON_RE.match(line.strip())
        if match:
            lessons.append((int(match.group(1)), match.group(2).strip()))
    return lessons


def numbers_from_heading(match: re.Match[str]) -> list[int]:
    start = int(match.group(1))
    end = int(match.group(2) or start)
    if end < start:
        start, end = end, start
    return list(range(start, end + 1))


def numbers_from_coverage(text: str) -> list[int]:
    match = COVERAGE_RE.search(text)
    if match is None:
        return []
    return sorted({int(number) for number in NUMBER_RE.findall(match.group(1))})


def numbers_from_filename(path: Path) -> list[int]:
    match = re.search(
        r"第?\s*(\d{1,3})(?:\s*[-—~至]\s*(\d{1,3}))?\s*课",
        path.stem,
    )
    if match is None:
        return []
    start = int(match.group(1))
    end = int(match.group(2) or start)
    if end < start:
        start, end = end, start
    return list(range(start, end + 1))


def read_artifacts(path: Path | None) -> dict[int, tuple[str, str]]:
    if path is None or not path.exists():
        return {}

    artifacts: dict[int, tuple[str, str]] = {}
    for file in sorted(path.rglob("*.md")):
        text = file.read_text(encoding="utf-8")
        heading = next(
            (
                match
                for line in text.splitlines()
                if (match := ARTIFACT_HEADING_RE.match(line.strip()))
            ),
            None,
        )
        numbers = numbers_from_coverage(text)
        if not numbers and heading is not None:
            numbers = numbers_from_heading(heading)
        if not numbers:
            numbers = numbers_from_filename(file)
        if not numbers:
            continue

        status_match = STATUS_RE.search(text)
        status = status_match.group(1) if status_match else "进行中"
        for number in numbers:
            artifacts[number] = (status, str(file))
    return artifacts


def validate_numbers(lessons: list[tuple[int, str]]) -> list[str]:
    errors: list[str] = []
    numbers = [number for number, _ in lessons]
    if not numbers:
        return ["课程目录中没有识别到 `第 XX 课` 标题。"]
    if len(numbers) != len(set(numbers)):
        errors.append("课程编号存在重复。")
    expected = list(range(min(numbers), max(numbers) + 1))
    if numbers != expected:
        errors.append(f"课程编号不连续或顺序错误: {numbers}")
    return errors


def main() -> int:
    args = parse_args()
    if not args.catalog.is_file():
        print(f"[ERROR] 课程目录不存在: {args.catalog}", file=sys.stderr)
        return 2

    catalog_lessons = parse_catalog(args.catalog)
    errors = validate_numbers(catalog_lessons)
    if errors:
        for error in errors:
            print(f"[ERROR] {error}", file=sys.stderr)
        return 1

    artifacts = read_artifacts(args.lessons_dir)
    lessons = [
        Lesson(
            number=number,
            title=title,
            status=artifacts.get(number, ("未开始", None))[0],
            artifact=artifacts.get(number, ("未开始", None))[1],
        )
        for number, title in catalog_lessons
    ]

    next_lesson = next(
        (lesson for lesson in lessons if lesson.status not in COMPLETED),
        None,
    )
    summary = {
        "catalog": str(args.catalog),
        "total": len(lessons),
        "completed": sum(lesson.status in COMPLETED for lesson in lessons),
        "in_progress": sum(lesson.status == "进行中" for lesson in lessons),
        "pending_review": sum(lesson.status == "待复核" for lesson in lessons),
        "next_lesson": asdict(next_lesson) if next_lesson else None,
        "lessons": [asdict(lesson) for lesson in lessons],
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    print(f"课程总数: {summary['total']}")
    print(f"已通过: {summary['completed']}")
    print(f"进行中: {summary['in_progress']}")
    print(f"待复核: {summary['pending_review']}")
    if next_lesson:
        print(
            f"建议继续: 第 {next_lesson.number:02d} 课 "
            f"{next_lesson.title} [{next_lesson.status}]"
        )
        if next_lesson.artifact:
            print(f"课件: {next_lesson.artifact}")
    else:
        print("建议继续: 全部课程已通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
