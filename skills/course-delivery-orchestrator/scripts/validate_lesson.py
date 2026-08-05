#!/usr/bin/env python3
"""Validate decoupled learning and interview documents."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


LEARNING_HEADING_RE = re.compile(
    r"^#\s+(.+?推导式理解)\s*$",
    re.MULTILINE,
)
INTERVIEW_HEADING_RE = re.compile(
    r"^#\s+(.+?(?:面试最终答案|最终答案).*)$",
    re.MULTILINE,
)
CATALOG_RE = re.compile(
    r"^#{2,4}\s+第\s*(\d{1,3})\s*课\s*[：:.\-]?\s*(.+?)\s*$",
    re.MULTILINE,
)
COVERAGE_RE = re.compile(r"覆盖课程\s*[：:]\s*(.+)")
STATUS_RE = re.compile(
    r"课程状态\s*[：:]\s*(进行中|待复核|已通过|未开始|已完成|已复核)"
)
PLACEHOLDER_RE = re.compile(r"\b(?:TODO|TBD)\b|待补|稍后补充", re.IGNORECASE)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
QUESTION_RE = re.compile(
    r"^###\s+面试题\s*[：:]\s*(.+?[？?])\s*$",
    re.MULTILINE,
)
INTERVIEW_QUESTION_RE = re.compile(
    r"^##\s+\d+[.、]\s*(.+?[？?])\s*$",
    re.MULTILINE,
)
MECHANISM_HEADING_RE = re.compile(
    r"^##\s+(?:[一二三四五六七八九十]+、|\d+[.、])\s*.+",
    re.MULTILINE,
)

LEARNING_REQUIRED_SECTIONS = {
    "核心推导链": (r"核心推导链",),
    "正常实验": (r"正常实验", r"最小实验"),
    "失败实验": (r"失败实验", r"故障实验", r"反例实验"),
    "口语化输出模板": (r"口语化输出模板",),
    "自测问题": (r"自测问题",),
    "知识图谱": (r"知识图谱",),
    "面试题拆分清单": (r"面试题拆分清单", r"面试题索引"),
}
FORBIDDEN_LEARNING_SECTIONS = {
    "30 秒回答": r"30\s*秒回答",
    "3 分钟回答": r"3\s*分钟回答",
    "教科书定义": r"教科书定义",
    "完整追问点": r"追问点",
}
INTERVIEW_REQUIRED_FIELDS = (
    "题型",
    "教科书定义",
    "启发式思维",
    "口语化输出",
    "追问点",
    "实验或 Trace 证据",
    "对应学习章节",
)
HEURISTIC_REQUIRED_ROWS = (
    "没有它会怎样",
    "怎么解决",
    "好处",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="校验推导式理解文档与独立最终面试答案是否职责分离。"
    )
    parser.add_argument("learning", type=Path, help="推导式理解 Markdown 文件")
    parser.add_argument(
        "--interview",
        type=Path,
        help="独立最终面试答案 Markdown 文件",
    )
    parser.add_argument("--catalog", type=Path, help="课程目录 Markdown 文件")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="将状态、占位符、本地链接和双轨合同问题视为错误",
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


def coverage_numbers(text: str) -> list[int]:
    match = COVERAGE_RE.search(text)
    if match is None:
        return []

    coverage = match.group(1)
    numbers: set[int] = set()
    for start_text, end_text in re.findall(
        r"第?\s*(\d{1,3})\s*(?:[-—~至]\s*(\d{1,3}))?\s*课?",
        coverage,
    ):
        start = int(start_text)
        end = int(end_text or start_text)
        if end < start:
            start, end = end, start
        numbers.update(range(start, end + 1))
    return sorted(numbers)


def has_section_heading(text: str, patterns: tuple[str, ...]) -> bool:
    for line in text.splitlines():
        if not re.match(r"^#{2,5}\s+", line):
            continue
        title = re.sub(r"^#{2,5}\s+(?:\d+[.、]\s*)?", "", line).strip()
        if any(re.search(pattern, title, re.IGNORECASE) for pattern in patterns):
            return True
    return False


def section_text(text: str, title_pattern: str) -> str:
    match = re.search(
        rf"^##\s+[^\n]*(?:{title_pattern})[^\n]*\n(.*?)(?=^##\s+|\Z)",
        text,
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def normalize_question(question: str) -> str:
    return re.sub(r"[\s？?，,。.!！：:、“”\"'（）()]", "", question)


def interview_question_sections(text: str) -> list[tuple[str, str]]:
    matches = list(INTERVIEW_QUESTION_RE.finditer(text))
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append((match.group(1).strip(), text[match.end():end]))
    return sections


def validate_learning(
    path: Path,
    text: str,
    strict: bool,
) -> tuple[list[str], list[str], list[str], list[int]]:
    errors: list[str] = []
    warnings: list[str] = []

    if LEARNING_HEADING_RE.search(text) is None:
        errors.append("一级标题必须明确标注为“推导式理解”。")

    numbers = coverage_numbers(text)
    if not numbers:
        errors.append("缺少可识别的“覆盖课程”编号。")

    for section, patterns in LEARNING_REQUIRED_SECTIONS.items():
        if not has_section_heading(text, patterns):
            errors.append(f"推导式理解文档缺少章节: {section}")

    mechanism_count = len(MECHANISM_HEADING_RE.findall(text))
    if mechanism_count < 2:
        errors.append(
            f"至少需要 2 个按知识机制组织的主章节，当前识别到 {mechanism_count} 个。"
        )

    code_blocks = re.findall(
        r"```(?:text)?\s*\n(.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    ascii_blocks = [
        block
        for block in code_blocks
        if re.search(r"(?:→|←|↓|↑|┌|├|└|│|─|=|->)", block)
    ]
    if len(ascii_blocks) < 2:
        errors.append("推导式理解文档至少需要 2 张承担推导职责的 ASCII 图。")

    if not re.search(r"^\|.+\|\s*$\n^\|[-:| ]+\|\s*$", text, re.MULTILINE):
        errors.append("推导式理解文档至少需要 1 张机制、对比或排障表。")

    oral_section = section_text(text, r"口语化输出模板")
    questions = [question.strip() for question in QUESTION_RE.findall(oral_section)]
    if not questions:
        errors.append("口语化输出模板必须展示至少一道完整面试题原文。")

    split_section = section_text(text, r"面试题拆分清单|面试题索引")
    split_markers = ("面试题", "对应学习章节", "最终答案文档", "实验证据")
    if not all(marker in split_section for marker in split_markers):
        errors.append("面试题拆分清单缺少题目、学习章节、最终答案文档或实验证据。")

    for name, pattern in FORBIDDEN_LEARNING_SECTIONS.items():
        if has_section_heading(text, (pattern,)):
            errors.append(f"推导式理解文档不应包含完整面试答案章节: {name}")

    if STATUS_RE.search(text) is None:
        (errors if strict else warnings).append("缺少自然语言课程状态。")
    if PLACEHOLDER_RE.search(text):
        (errors if strict else warnings).append("学习文档仍包含占位符。")
    link_errors = local_link_errors(path, text)
    (errors if strict else warnings).extend(link_errors)
    return errors, warnings, questions, numbers


def validate_interview(
    path: Path,
    text: str,
    learning_questions: list[str],
    strict: bool,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if INTERVIEW_HEADING_RE.search(text) is None:
        errors.append("最终答案文档一级标题必须明确标注“面试最终答案”或“最终答案”。")
    if "对应学习文档" not in text:
        errors.append("最终答案文档缺少“对应学习文档”回链。")

    sections = interview_question_sections(text)
    if not sections:
        errors.append("最终答案文档没有识别到按编号拆分的完整面试题。")

    interview_questions = [question for question, _ in sections]
    normalized_interview = {
        normalize_question(question) for question in interview_questions
    }
    missing = [
        question
        for question in learning_questions
        if normalize_question(question) not in normalized_interview
    ]
    if missing:
        errors.append(f"最终答案文档尚未拆出学习文档中的题目: {missing}")

    for question, body in sections:
        missing_fields = [
            field for field in INTERVIEW_REQUIRED_FIELDS if field not in body
        ]
        if missing_fields:
            errors.append(f"题目“{question}”缺少字段: {missing_fields}")

        missing_rows = [
            row for row in HEURISTIC_REQUIRED_ROWS if row not in body
        ]
        if not ("坏处" in body or "边界" in body):
            missing_rows.append("坏处或边界")
        if missing_rows:
            errors.append(f"题目“{question}”的启发式思维不完整: {missing_rows}")

        oral_match = re.search(
            r"口语化输出\s*[：:]?(.*?)(?=\n(?:ASCII|追问点|实验或 Trace 证据|对应学习章节)\s*[：:]|\Z)",
            body,
            re.DOTALL,
        )
        if oral_match is None or ">" not in oral_match.group(1):
            errors.append(f"题目“{question}”缺少可直接上场的引用式口语回答。")

    if PLACEHOLDER_RE.search(text):
        (errors if strict else warnings).append("最终答案文档仍包含占位符。")
    link_errors = local_link_errors(path, text)
    (errors if strict else warnings).extend(link_errors)
    return errors, warnings


def main() -> int:
    args = parse_args()
    if not args.learning.is_file():
        print(f"[ERROR] 推导式理解文档不存在: {args.learning}")
        return 2

    learning_text = args.learning.read_text(encoding="utf-8")
    errors, warnings, questions, numbers = validate_learning(
        args.learning,
        learning_text,
        args.strict,
    )

    if args.catalog:
        if not args.catalog.is_file():
            errors.append(f"课程目录不存在: {args.catalog}")
        elif numbers:
            lessons = catalog_lessons(args.catalog)
            missing_numbers = [number for number in numbers if number not in lessons]
            if missing_numbers:
                errors.append(f"学习文档覆盖的课程不存在于目录: {missing_numbers}")

    if args.interview:
        if not args.interview.is_file():
            errors.append(f"最终面试答案文档不存在: {args.interview}")
        else:
            interview_errors, interview_warnings = validate_interview(
                args.interview,
                args.interview.read_text(encoding="utf-8"),
                questions,
                args.strict,
            )
            errors.extend(interview_errors)
            warnings.extend(interview_warnings)

    for warning in warnings:
        print(f"[WARNING] {warning}")
    for error in errors:
        print(f"[ERROR] {error}")

    print(f"检查完成: {len(errors)} 个错误, {len(warnings)} 个提醒。")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
