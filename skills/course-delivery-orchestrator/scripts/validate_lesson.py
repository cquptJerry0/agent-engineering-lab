#!/usr/bin/env python3
"""Validate a dynamic CU's separated learning and interview tracks."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


LEARNING_HEADING_RE = re.compile(r"^#\s+.*推导式理解.*$", re.MULTILINE)
INTERVIEW_HEADING_RE = re.compile(r"^#\s+.*面试训练.*$", re.MULTILINE)
CU_ID_RE = re.compile(r"\bCU-\d{3}\b", re.IGNORECASE)
STATUS_RE = re.compile(
    r"CU\s*状态\s*[：:]\s*(未开始|推导中|面试训练中|待复核|已通过)"
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
STAGE_RE = re.compile(
    r"^##\s+(?:阶段|版本)\s*(?:[一二三四五六七八九十]+|\d+)",
    re.MULTILINE,
)
KNOWLEDGE_ROW_RE = re.compile(
    r"^\|\s*\d+\s*\|\s*([^|]+?)\s*\|",
    re.MULTILINE,
)

LEARNING_REQUIRED_SECTIONS = {
    "选课依据与覆盖知识点": (r"选课依据", r"覆盖知识点"),
    "核心推导链": (r"核心推导链",),
    "贯穿案例与初始状态": (r"贯穿案例", r"初始状态"),
    "正常链路": (r"正常链路",),
    "失败链路": (r"失败链路",),
    "最小实验": (r"最小实验",),
    "边界、代价与下一问题": (r"边界", r"下一问题"),
    "自测问题": (r"自测问题",),
    "知识图谱": (r"知识图谱",),
    "面试题索引": (r"面试题索引",),
}
FORBIDDEN_LEARNING_SECTIONS = {
    "30 秒回答": r"30\s*秒回答",
    "完整回答": r"完整回答",
    "原理追问": r"原理追问",
    "工程追问": r"工程追问",
    "项目追问": r"项目追问",
}
INTERVIEW_REQUIRED_FIELDS = (
    "题型",
    "一句话核心判断",
    "启发式思考",
    "30 秒回答",
    "完整回答",
    "追问",
    "证据",
    "对应推导章节",
)
HEURISTIC_REQUIRED_ROWS = (
    "没有它会怎样",
    "最小机制",
    "工程收益",
    "边界",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="校验动态 CU 的链路学习、双轨分离和知识主归属。"
    )
    parser.add_argument("learning", type=Path, help="推导式理解 Markdown 文件")
    parser.add_argument("--interview", type=Path, help="面试训练 Markdown 文件")
    parser.add_argument("--outline", type=Path, help="知识总纲 Markdown 文件")
    parser.add_argument("--progress", type=Path, help="学习进度 Markdown 文件")
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


def has_section_heading(text: str, patterns: tuple[str, ...]) -> bool:
    titles = [
        re.sub(r"^#{2,5}\s+", "", line).strip()
        for line in text.splitlines()
        if re.match(r"^#{2,5}\s+", line)
    ]
    return all(
        any(re.search(pattern, title, re.IGNORECASE) for title in titles)
        for pattern in patterns
    )


def section_text(text: str, title_pattern: str) -> str:
    match = re.search(
        rf"^##\s+[^\n]*(?:{title_pattern})[^\n]*\n(.*?)(?=^##\s+|\Z)",
        text,
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def normalize_question(question: str) -> str:
    return re.sub(r"[\s？?，,。.!！：:、“”\"'（）()]", "", question)


def knowledge_terms(point: str) -> list[str]:
    point = re.sub(r"\([^)]*\)", "", point)
    raw_terms = re.split(r"[、，,;/]|\s+与\s+|\s+和\s+|与|和", point)
    terms: list[str] = []
    for raw in raw_terms:
        term = re.sub(r"[\s。.!！：:、“”\"'（）()/_-]", "", raw).casefold()
        term = re.sub(r"(?:工作)?直觉$", "", term)
        if term == "请求结构":
            term = "请求"
        if term:
            terms.append(term)
    return terms


def normalize_source_text(text: str) -> str:
    text = re.sub(r"[()（）]", "", text)
    return re.sub(r"[\s、，,。.!！：:、“”\"'（）()/_-]", "", text).casefold()


def interview_question_sections(text: str) -> list[tuple[str, str]]:
    matches = list(INTERVIEW_QUESTION_RE.finditer(text))
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append((match.group(1).strip(), text[match.end():end]))
    return sections


def validate_knowledge_sources(
    points: list[str],
    source: Path | None,
    label: str,
) -> list[str]:
    if source is None:
        return []
    if not source.is_file():
        return [f"{label}不存在: {source}"]
    text = source.read_text(encoding="utf-8")
    normalized_source = normalize_source_text(text)
    missing: list[str] = []
    for point in points:
        if not all(term in normalized_source for term in knowledge_terms(point)):
            missing.append(f"{label}中未找到覆盖知识点: {point}")
    return missing


def validate_learning(
    path: Path,
    text: str,
    strict: bool,
) -> tuple[list[str], list[str], list[str], list[str], str | None]:
    errors: list[str] = []
    warnings: list[str] = []

    if LEARNING_HEADING_RE.search(text) is None:
        errors.append("一级标题必须明确标注“推导式理解”。")

    cu_match = CU_ID_RE.search(text)
    cu_id = cu_match.group(0).upper() if cu_match else None
    if cu_id is None:
        errors.append("推导式理解文档缺少 CU-XXX 编号。")

    if STATUS_RE.search(text) is None:
        (errors if strict else warnings).append("缺少合法的 CU 状态。")

    for section, patterns in LEARNING_REQUIRED_SECTIONS.items():
        if not has_section_heading(text, patterns):
            errors.append(f"推导式理解文档缺少章节: {section}")

    stage_count = len(STAGE_RE.findall(text))
    if stage_count < 3:
        errors.append(f"至少需要 3 个连续演进阶段，当前识别到 {stage_count} 个。")

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
        errors.append("推导式理解文档至少需要 1 张机制、覆盖或排障表。")

    coverage_section = section_text(text, r"选课依据|覆盖知识点")
    points = [point.strip() for point in KNOWLEDGE_ROW_RE.findall(coverage_section)]
    if not points:
        errors.append("覆盖知识点章节必须使用带序号表格列出知识点。")

    index_section = section_text(text, r"面试题索引")
    questions = [question.strip() for question in QUESTION_RE.findall(index_section)]
    if not questions:
        errors.append("面试题索引必须展示至少一道完整题目。")

    for name, pattern in FORBIDDEN_LEARNING_SECTIONS.items():
        if has_section_heading(text, (pattern,)):
            errors.append(f"推导式理解文档不应包含完整面试训练章节: {name}")

    if PLACEHOLDER_RE.search(text):
        (errors if strict else warnings).append("推导式理解文档仍包含占位符。")
    link_errors = local_link_errors(path, text)
    (errors if strict else warnings).extend(link_errors)
    return errors, warnings, questions, points, cu_id


def validate_interview(
    path: Path,
    text: str,
    learning_questions: list[str],
    learning_cu_id: str | None,
    strict: bool,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if INTERVIEW_HEADING_RE.search(text) is None:
        errors.append("面试文档一级标题必须明确标注“面试训练”。")
    if "对应推导式理解" not in text:
        errors.append("面试训练文档缺少“对应推导式理解”回链。")

    interview_cu = CU_ID_RE.search(text)
    if learning_cu_id and (
        interview_cu is None or interview_cu.group(0).upper() != learning_cu_id
    ):
        errors.append("两条轨道的 CU 编号不一致。")

    sections = interview_question_sections(text)
    if not sections:
        errors.append("面试训练文档没有识别到按编号拆分的完整题目。")

    normalized_interview = {
        normalize_question(question) for question, _ in sections
    }
    missing = [
        question
        for question in learning_questions
        if normalize_question(question) not in normalized_interview
    ]
    if missing:
        errors.append(f"面试训练尚未覆盖第一轨索引中的题目: {missing}")

    for question, body in sections:
        missing_fields = [
            field for field in INTERVIEW_REQUIRED_FIELDS if field not in body
        ]
        if missing_fields:
            errors.append(f"题目“{question}”缺少字段: {missing_fields}")

        missing_rows = [
            row for row in HEURISTIC_REQUIRED_ROWS if row not in body
        ]
        if missing_rows:
            errors.append(f"题目“{question}”的启发式思考不完整: {missing_rows}")

        short_match = re.search(
            r"30\s*秒回答\s*[：:]?(.*?)(?=\n完整回答\s*[：:]|\Z)",
            body,
            re.DOTALL,
        )
        if short_match is None or ">" not in short_match.group(1):
            errors.append(f"题目“{question}”缺少引用式 30 秒回答。")

        for follow_up in ("原理追问", "工程追问", "项目追问"):
            if follow_up not in body:
                errors.append(f"题目“{question}”缺少{follow_up}。")

    if PLACEHOLDER_RE.search(text):
        (errors if strict else warnings).append("面试训练文档仍包含占位符。")
    link_errors = local_link_errors(path, text)
    (errors if strict else warnings).extend(link_errors)
    return errors, warnings


def main() -> int:
    args = parse_args()
    if not args.learning.is_file():
        print(f"[ERROR] 推导式理解文档不存在: {args.learning}")
        return 2

    learning_text = args.learning.read_text(encoding="utf-8")
    errors, warnings, questions, points, cu_id = validate_learning(
        args.learning,
        learning_text,
        args.strict,
    )

    errors.extend(validate_knowledge_sources(points, args.outline, "知识总纲"))
    errors.extend(validate_knowledge_sources(points, args.progress, "学习进度"))

    if args.interview:
        if not args.interview.is_file():
            errors.append(f"面试训练文档不存在: {args.interview}")
        else:
            interview_errors, interview_warnings = validate_interview(
                args.interview,
                args.interview.read_text(encoding="utf-8"),
                questions,
                cu_id,
                args.strict,
            )
            errors.extend(interview_errors)
            warnings.extend(interview_warnings)

    for warning in warnings:
        print(f"[WARNING] {warning}")
    for error in errors:
        print(f"[ERROR] {error}")

    print(
        f"检查完成: {len(points)} 个知识点, {len(questions)} 道索引题, "
        f"{len(errors)} 个错误, {len(warnings)} 个提醒。"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
