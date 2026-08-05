#!/usr/bin/env python3
"""Validate a problem-driven lesson artifact against the delivery contract."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


HEADING_RE = re.compile(
    r"^#\s+第\s*(\d{1,3})"
    r"(?:\s*[-—~至]\s*(\d{1,3}))?"
    r"\s*课\s*[：:.\-]?\s*(.+?)\s*$",
    re.MULTILINE,
)
CATALOG_RE = re.compile(
    r"^#{2,4}\s+第\s*(\d{1,3})\s*课\s*[：:.\-]?\s*(.+?)\s*$",
    re.MULTILINE,
)
STATUS_RE = re.compile(
    r"课程状态\s*[：:]\s*(进行中|待复核|已通过|未开始|已完成|已复核)"
)
PLACEHOLDER_RE = re.compile(r"\b(?:TODO|TBD)\b|待补|稍后补充", re.IGNORECASE)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
PROBLEM_HEADING_RE = re.compile(
    r"^#{3,5}\s+问题(?:[一二三四五六七八九十]|\d+)\s*[：:].+",
    re.MULTILINE,
)

REQUIRED_SECTIONS = {
    "开课总览": (r"开课总览", r"本单元要回答的问题"),
    "目标面试题": (r"目标面试题",),
    "题目关系图": (r"题目关系图", r"问题关系图"),
    "结构化答案骨架": (r"结构化答案骨架", r"答案骨架"),
    "推导学习": (r"推导学习", r"问题推导"),
    "正常实验": (r"正常实验", r"最小实验"),
    "失败实验": (r"失败实验", r"故障实验", r"反例实验"),
    "面试收束": (r"面试收束", r"结构化面试回答"),
    "30 秒回答": (r"30\s*秒回答",),
    "3 分钟回答": (r"3\s*分钟回答",),
    "覆盖检查": (r"覆盖检查", r"题目覆盖"),
    "单元验收": (r"单元验收", r"本课验收", r"课程验收"),
    "仍未解决的问题": (r"仍未解决的问题", r"遗留问题"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="校验总分总、问题驱动课件的结构、题目、实验和课程归属。"
    )
    parser.add_argument("lesson", type=Path, help="正式课件 Markdown 文件")
    parser.add_argument("--catalog", type=Path, help="课程目录 Markdown 文件")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="将缺失状态、占位符、链接和学习合同视为错误",
    )
    return parser.parse_args()


def local_link_errors(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    for target in LINK_RE.findall(text):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        local = target.split("#", 1)[0]
        if local and not (path.parent / local).exists():
            errors.append(f"本地链接不存在: {target}")
    return errors


def catalog_lessons(path: Path) -> dict[int, str]:
    return {
        int(match.group(1)): match.group(2).strip()
        for match in CATALOG_RE.finditer(path.read_text(encoding="utf-8"))
    }


def has_section_heading(text: str, patterns: tuple[str, ...]) -> bool:
    for line in text.splitlines():
        if not re.match(r"^#{2,5}\s+", line):
            continue
        title = re.sub(r"^#{2,5}\s+(?:\d+\.\s*)?", "", line).strip()
        if any(re.search(pattern, title, re.IGNORECASE) for pattern in patterns):
            return True
    return False


def section_text(text: str, title_pattern: str) -> str:
    match = re.search(
        rf"^##+\s+[^\n]*(?:{title_pattern})[^\n]*\n(.*?)(?=^##+\s+|\Z)",
        text,
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def covered_numbers(heading: re.Match[str]) -> list[int]:
    start = int(heading.group(1))
    end = int(heading.group(2) or start)
    if end < start:
        start, end = end, start
    return list(range(start, end + 1))


def main() -> int:
    args = parse_args()
    if not args.lesson.is_file():
        print(f"[ERROR] 课件不存在: {args.lesson}")
        return 2

    text = args.lesson.read_text(encoding="utf-8")
    errors: list[str] = []
    warnings: list[str] = []

    heading = HEADING_RE.search(text)
    if heading is None:
        errors.append("缺少 `# 第 XX 课：标题` 或 `# 第 XX-YY 课：标题`。")
        numbers: list[int] = []
        title = ""
    else:
        numbers = covered_numbers(heading)
        title = heading.group(3).strip()

    for section, patterns in REQUIRED_SECTIONS.items():
        if not has_section_heading(text, patterns):
            errors.append(f"缺少章节: {section}")

    problem_count = len(PROBLEM_HEADING_RE.findall(text))
    if not 2 <= problem_count <= 4:
        errors.append(f"问题章节应为 2 至 4 个，当前识别到 {problem_count} 个。")

    interview_section = section_text(text, r"目标面试题")
    if not re.search(r"[？?]", interview_section):
        errors.append("目标面试题章节没有识别到完整问题原文。")

    ascii_sections = re.findall(
        r"^##{3,5}\s+.*ASCII\s*图.*?(?=^##{2,5}\s+|\Z)",
        text,
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    if not ascii_sections:
        errors.append("缺少 ASCII 图章节。")
    elif not all("```" in section for section in ascii_sections):
        errors.append("存在没有代码块图的 ASCII 图章节。")
    if ascii_sections and not all(
        re.search(r"(问题|为什么|如何|怎样|什么|？|\?)", section.splitlines()[0])
        for section in ascii_sections
    ):
        errors.append("ASCII 图标题必须明确写出它回答的问题。")

    coverage_section = section_text(text, r"覆盖检查|题目覆盖")
    coverage_markers = ("面试题", "是否完整回答", "正文依据", "实验证据")
    if not all(marker in coverage_section for marker in coverage_markers):
        errors.append("覆盖检查缺少面试题、完整回答、正文依据或实验证据字段。")

    if STATUS_RE.search(text) is None:
        (errors if args.strict else warnings).append("缺少自然语言课程状态。")

    if PLACEHOLDER_RE.search(text):
        (errors if args.strict else warnings).append("课件仍包含 TODO、TBD 或待补占位符。")

    link_errors = local_link_errors(args.lesson, text)
    (errors if args.strict else warnings).extend(link_errors)

    if args.catalog:
        if not args.catalog.is_file():
            errors.append(f"课程目录不存在: {args.catalog}")
        elif numbers:
            lessons = catalog_lessons(args.catalog)
            missing = [number for number in numbers if number not in lessons]
            if missing:
                errors.append(f"课件覆盖的课程不存在于目录: {missing}")
            if len(numbers) == 1 and numbers[0] in lessons:
                catalog_title = lessons[numbers[0]]
                if catalog_title != title:
                    warnings.append(
                        f"课件标题与目录不同: 目录 `{catalog_title}`，课件 `{title}`。"
                    )

    for warning in warnings:
        print(f"[WARNING] {warning}")
    for error in errors:
        print(f"[ERROR] {error}")

    print(f"检查完成: {len(errors)} 个错误, {len(warnings)} 个提醒。")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
