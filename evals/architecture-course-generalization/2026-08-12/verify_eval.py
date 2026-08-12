#!/usr/bin/env python3
"""Verify the architecture and dual-track course generalization evaluation."""

from __future__ import annotations

import random
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[2]
COURSE_SKILL = REPO_ROOT / "skills" / "course-delivery-orchestrator"
ARCHITECTURE_SKILL = REPO_ROOT / "skills" / "architecture-research"
SEED = 620082253

CANDIDATES_408 = [
    ("408-01", "复杂度、数组、链表与哈希表"),
    ("408-02", "栈、队列、递归与状态机"),
    ("408-03", "树、堆与索引型数据结构"),
    ("408-04", "图搜索、拓扑排序与依赖调度"),
    ("408-05", "排序、二分与外部排序"),
    ("408-06", "CPU 缓存、局部性与程序性能"),
    ("408-07", "进程、线程、调度与上下文切换"),
    ("408-08", "并发同步、死锁与内存可见性"),
    ("408-09", "虚拟内存、页表、缺页与文件映射"),
    ("408-10", "系统调用、文件 I/O 与 I/O 多路复用"),
    ("408-11", "TCP 可靠传输、流量控制与拥塞控制"),
    ("408-12", "DNS、TLS、HTTP 与代理缓存链路"),
]

CANDIDATES_STORAGE = [
    ("STO-01", "浏览器持久化、HTTP 缓存与离线一致性"),
    ("STO-02", "内存缓存、淘汰策略与缓存一致性"),
    ("STO-03", "页缓存、文件系统与 fsync 持久化语义"),
    ("STO-04", "B+Tree 页组织、索引与范围查询"),
    ("STO-05", "WAL、Redo、Undo 与崩溃恢复"),
    ("STO-06", "MVCC、锁与事务隔离"),
    ("STO-07", "LSM Tree、SSTable、Compaction 与 Bloom Filter"),
    ("STO-08", "Redis 持久化、复制与故障切换"),
    ("STO-09", "分片、热点、重平衡与路由"),
    ("STO-10", "复制、Quorum 与一致性模型"),
    ("STO-11", "共识日志、Leader 切换与线性一致性"),
    ("STO-12", "对象存储、数据放置与纠删码"),
    ("STO-13", "快照、备份、PITR 与容灾"),
    ("STO-14", "SSD、写放大与尾延迟"),
    ("STO-15", "数据校验、后台修复与静默损坏"),
    ("STO-16", "容量规划、可观测性与成本分层"),
]

EXPECTED_SELECTION = [
    ("408-12", "DNS、TLS、HTTP 与代理缓存链路"),
    ("408-03", "树、堆与索引型数据结构"),
    ("STO-03", "页缓存、文件系统与 fsync 持久化语义"),
    ("STO-08", "Redis 持久化、复制与故障切换"),
    ("408-08", "并发同步、死锁与内存可见性"),
]


def run(command: list[str]) -> None:
    result = subprocess.run(command, cwd=REPO_ROOT, text=True)
    if result.returncode:
        raise SystemExit(result.returncode)


def verify_random_selection() -> None:
    rng = random.Random(SEED)
    selected = rng.sample(CANDIDATES_408, 2)
    selected += rng.sample(CANDIDATES_STORAGE, 2)
    remaining = [
        item
        for item in CANDIDATES_408 + CANDIDATES_STORAGE
        if item not in selected
    ]
    selected += rng.sample(remaining, 1)
    rng.shuffle(selected)
    if selected != EXPECTED_SELECTION:
        raise SystemExit(f"随机抽样不一致: {selected}")
    print("随机抽样可复现。")


def verify_lessons() -> None:
    validator = COURSE_SKILL / "scripts" / "validate_lesson.py"
    course_count = 0
    for domain in ("408", "存储体系"):
        domain_root = ROOT / domain
        for cu_dir in sorted((domain_root / "课程").glob("CU-*")):
            run(
                [
                    sys.executable,
                    str(validator),
                    str(cu_dir / "推导式理解.md"),
                    "--interview",
                    str(cu_dir / "面试训练.md"),
                    "--outline",
                    str(domain_root / "知识总纲.md"),
                    "--progress",
                    str(domain_root / "学习进度.md"),
                    "--strict",
                ]
            )
            course_count += 1
    if course_count != 5:
        raise SystemExit(f"应有 5 个 CU，实际为 {course_count}")
    print("5 个双轨 CU 严格校验通过。")


def verify_course_entries() -> None:
    validator = COURSE_SKILL / "scripts" / "validate_course.py"
    for domain in ("408", "存储体系"):
        run(
            [
                sys.executable,
                str(validator),
                str(ROOT / domain / "课程" / "README.md"),
                "--strict",
            ]
        )
    print("2 个动态课程入口校验通过。")


def verify_document_system() -> None:
    run(
        [
            sys.executable,
            str(ARCHITECTURE_SKILL / "scripts" / "validate_doc_system.py"),
            str(ROOT),
            "--entry",
            "README.md",
            "--strict",
        ]
    )
    print("完整文档体系严格校验通过。")


def main() -> None:
    verify_random_selection()
    verify_lessons()
    verify_course_entries()
    verify_document_system()


if __name__ == "__main__":
    main()
