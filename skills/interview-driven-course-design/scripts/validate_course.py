#!/usr/bin/env python3
"""Validate an interview-oriented Markdown course catalog."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


LESSON_RE = re.compile(
    r"^#{2,4}\s+(?:第\s*)?(\d{1,3})\s*(?:课|讲|节|lesson)\s*[：:.\-]?\s*(.*)$",
    re.IGNORECASE,
)

REQUIRED_FIELDS = {
    "思考题": (r"核心思考", r"开场思考", r"思考题", r"核心问题"),
    "具体案例": (r"具体案例", r"真实案例", r"案例卡"),
    "ASCII 图": (r"ASCII\s*图",),
    "正常实验": (r"最小实验", r"正常实验", r"最小正常实验"),
    "失败实验": (r"失败实验", r"故障实验", r"反例实验"),
    "面试目标": (r"面试目标", r"面试攻防", r"30\s*秒回答"),
    "完成标准": (r"完成标准", r"课程验收", r"本课验收"),
}

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="校验面试导向 Markdown 课程目录的编号、必备字段和本地链接。"
    )
    parser.add_argument("course_file", type=Path, help="课程目录 Markdown 文件")
    parser.add_argument(
        "--expected-lessons",
        type=int,
        help="期望课程数量；未指定时只检查已发现课程",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="将缺少必备字段和本地链接错误视为失败",
    )
    return parser.parse_args()


def split_lessons(lines: list[str]) -> list[tuple[int, str, int, str]]:
    matches: list[tuple[int, str, int]] = []
    for index, line in enumerate(lines):
        match = LESSON_RE.match(line.strip())
        if match:
            matches.append((int(match.group(1)), match.group(2).strip(), index))

    lessons: list[tuple[int, str, int, str]] = []
    for offset, (number, title, start) in enumerate(matches):
        end = matches[offset + 1][2] if offset + 1 < len(matches) else len(lines)
        lessons.append((number, title, start + 1, "\n".join(lines[start:end])))
    return lessons


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
    lines = text.splitlines()
    lessons = split_lessons(lines)
    errors: list[str] = []
    warnings: list[str] = []

    if not lessons:
        errors.append("没有识别到课程标题，例如 `### 第 00 课：标题`。")
    else:
        numbers = [lesson[0] for lesson in lessons]
        duplicates = sorted({number for number in numbers if numbers.count(number) > 1})
        if duplicates:
            errors.append(f"课程编号重复: {duplicates}")

        expected_sequence = list(range(min(numbers), max(numbers) + 1))
        if numbers != expected_sequence:
            errors.append(
                f"课程编号不连续或顺序错误: 实际 {numbers}，期望 {expected_sequence}"
            )

        if args.expected_lessons is not None and len(lessons) != args.expected_lessons:
            errors.append(
                f"课程数量不符: 实际 {len(lessons)}，期望 {args.expected_lessons}"
            )

        for number, title, line_number, block in lessons:
            prefix = f"第 {number:02d} 课"
            if not title:
                errors.append(f"{prefix} 第 {line_number} 行缺少标题")
            for field, patterns in REQUIRED_FIELDS.items():
                if not any(re.search(pattern, block, re.IGNORECASE) for pattern in patterns):
                    message = f"{prefix} 缺少{field}"
                    (errors if args.strict else warnings).append(message)

    link_errors = validate_links(args.course_file, text)
    (errors if args.strict else warnings).extend(link_errors)

    if "覆盖" not in text:
        warnings.append("未发现覆盖矩阵或覆盖说明，建议证明知识单元都有课程去向。")
    if "防漂移" not in text and "漂移" not in text:
        warnings.append("未发现防漂移规则，长期授课可能偏离原知识边界。")

    for warning in warnings:
        print(f"[WARNING] {warning}")
    for error in errors:
        print(f"[ERROR] {error}")

    print(
        f"检查完成: {len(lessons)} 节课, "
        f"{len(errors)} 个错误, {len(warnings)} 个提醒。"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
