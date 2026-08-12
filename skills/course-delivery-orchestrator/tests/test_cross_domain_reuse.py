from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATE = SKILL_ROOT / "scripts" / "validate_lesson.py"


def learning_document(
    title: str,
    points: tuple[str, str, str],
    stages: tuple[str, str, str],
    case: str,
    question: str,
) -> str:
    coverage_rows = "\n".join(
        f"| {index} | {point} | 技术总纲 | 未开始 | 形成机制链 |"
        for index, point in enumerate(points, start=1)
    )
    stage_blocks = []
    for index, (point, stage) in enumerate(zip(points, stages), start=1):
        next_problem = (
            "怎样引入下一阶段机制？"
            if index < len(points)
            else "怎样把当前机制迁移到陌生案例？"
        )
        stage_blocks.append(
            f"""\
## 阶段{index}：{stage}

### 本阶段知识点群

| 知识点 | 本阶段解决的问题 | 与前后阶段的关系 |
|---|---|---|
| {point} | 解释当前技术阶段的核心机制 | 承接前置并引出后续 |

### 当前问题

现有能力无法同时满足正确性、可观察性和工程约束。

### 推导过程

从贯穿案例的失败现象定位缺失机制，再引入{point}。

### 机制全解

{point}包含明确输入、内部状态、运行步骤、输出、适用边界和失败条件。学习时需要解释各组成部分怎样协作，以及删除其中任一环节会破坏什么性质。

### 状态变化

| 维度 | 进入阶段前 | 引入机制后 |
|---|---|---|
| 输入 | 原始任务 | 带约束的任务 |
| 状态或不变量 | 不明确 | 可以被程序或实验观察 |
| 控制过程 | 单一路径 | 按机制分阶段推进 |
| 输出 | 结果不可解释 | 结果可回链状态 |
| 仍未解决 | 当前缺口 | {next_problem} |

### 阶段结论

{point}把案例从不可解释状态推进到可验证状态。

### 下一问题

{next_problem}
"""
        )

    return f"""\
# CU-001：{title} - 推导式理解

> CU 状态：未开始
> 生成依据：当前技术目标和未开始进度
> 覆盖知识点：3 个

## 选课依据与覆盖知识点

| 序号 | 知识点 | 总纲主归属 | 当前状态 | 本 CU 作用 |
|---|---|---|---|---|
{coverage_rows}

## 核心推导链

```text
已有能力 → 暴露约束 → 引入机制一 → 观察新状态 → 引入机制二 → 验证完整结果
```

## 贯穿案例与初始状态

{case}

{"".join(stage_blocks)}

## 正常链路与失败链路

```text
正常：输入 → 状态推进 → 约束满足 → 输出可验证
失败：输入 → 状态停滞 → 约束破坏 → 证据定位根因
```

## 实验任务卡

### 实验任务一：观察正常状态演进

实验目标：验证核心机制能产生预期状态变化。
覆盖知识点：{points[0]}、{points[1]}。
准备条件：最小可运行示例或纸面模拟器。
操作步骤：固定输入，逐步记录每个阶段的状态和输出。
预期现象：状态按机制顺序推进，最终满足不变量。
通过标准：每个输出都能回链到对应状态。
产出证据：状态表、运行日志或逐步推演记录。

### 实验任务二：注入失败边界

实验目标：验证机制失效时能定位边界。
覆盖知识点：{points[1]}、{points[2]}。
准备条件：实验一的输入和状态记录。
操作步骤：删除一个关键步骤或制造约束冲突，再比较状态。
预期现象：失败停留在明确阶段，结果不再满足不变量。
通过标准：能根据证据区分机制错误和输入错误。
产出证据：正常与失败对照表。

## 边界、代价与下一问题

当前 CU 只证明三个核心机制可以形成连续链路，后续 CU 根据进度动态选择性能、实现细节或生产边界。

## 自测题与答案

### 题目一

三个机制为什么应放在同一个 CU？

参考答案：它们共享同一贯穿案例，前一机制留下的状态问题会自然引出后一机制，并能共用正常与失败实验。

判分点：说出共享案例、连续状态和因果依赖。

常见误区：只因为它们在总纲中相邻就合并。

## 知识关系图

```text
[{points[0]}]
  └─ 产生中间状态 → [{points[1]}]
                         └─ 验证或推进 → [{points[2]}]
```

### 如何读图

从输入侧开始，沿带语义的箭头读取三个机制怎样形成完整闭环。

## 面试题索引

### 面试题：{question}

对应三个技术阶段和正常、失败实验。
"""


def interview_document(title: str, question: str) -> str:
    return f"""\
# CU-001：{title} - 面试训练

> 对应推导式理解：[推导式理解](推导式理解.md)

## 1. {question}

题型：原理与工程型

一句话核心判断：三个机制通过连续状态和明确边界组成一个可验证的技术闭环。

启发式思考：

| 思考 | 回答 |
|---|---|
| 没有它会怎样 | 只能背术语，无法解释运行过程 |
| 最小机制是什么 | 输入、状态推进、约束和输出 |
| 工程收益 | 结果可解释、可验证、可排障 |
| 边界和代价 | 需要额外状态记录和实验设计 |

30 秒回答：

> 我会从贯穿案例出发，依次说明三个机制解决的问题、状态怎样变化、正常与失败证据，以及它们的适用边界。

完整回答：

先定位原始问题，再说明三个机制如何依次接管状态推进和结果验证。每个结论都应回到可观察状态、运行步骤和失败证据，不能只列名词。

ASCII 图或关键表：

```text
输入 → 机制一 → 中间状态 → 机制二 → 验证 → 输出
```

追问：

- 原理追问：核心不变量是什么？
- 工程追问：怎样制造失败实验？
- 项目追问：在真实项目中怎样记录证据？

证据：

正常和失败状态对照、实验日志或可运行示例。

对应推导章节：

阶段一到阶段三。
"""


class CrossDomainReuseTest(unittest.TestCase):
    CASES = (
        (
            "React Fiber 调度与提交原理",
            ("Fiber 节点", "Render 阶段", "Commit 阶段"),
            ("Fiber 数据结构", "可中断 Render 阶段", "Commit 提交阶段"),
            "一个包含长列表和高优先级输入的 React 页面，观察渲染任务怎样拆分、暂停和提交。",
            "React Fiber 为什么要区分 Render 阶段和 Commit 阶段？",
        ),
        (
            "MySQL 事务可见性与崩溃恢复原理",
            ("Undo Log", "MVCC Read View", "Redo Log"),
            ("Undo Log 版本链", "MVCC 可见性判断", "Redo Log 崩溃恢复"),
            "一笔转账事务同时遇到并发读取和进程崩溃，追踪版本可见性与恢复结果。",
            "MySQL 怎样同时保证事务可见性和崩溃恢复？",
        ),
        (
            "Kubernetes 调度周期与资源绑定原理",
            ("Filter 插件", "Score 插件", "Bind 阶段"),
            ("Filter 节点过滤", "Score 节点评分", "Bind 资源绑定"),
            "一个 Pending Pod 在多个资源和亲和性不同的节点间完成过滤、评分和绑定。",
            "Kubernetes Scheduler 从 Pending Pod 到绑定节点经历哪些核心阶段？",
        ),
    )

    def test_three_distinct_technical_domains_validate(self) -> None:
        for title, points, stages, case, question in self.CASES:
            with self.subTest(title=title), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                cu = root / "课程" / f"CU-001-{title.replace(' ', '-')}"
                cu.mkdir(parents=True)
                learning = cu / "推导式理解.md"
                interview = cu / "面试训练.md"
                outline = root / "学习总纲.md"
                progress = root / "学习进度.md"
                learning.write_text(
                    learning_document(title, points, stages, case, question),
                    encoding="utf-8",
                )
                interview.write_text(
                    interview_document(title, question),
                    encoding="utf-8",
                )
                source = "\n".join(points)
                outline.write_text(source, encoding="utf-8")
                progress.write_text(source, encoding="utf-8")

                result = subprocess.run(
                    [
                        "python3",
                        str(VALIDATE),
                        str(learning),
                        "--interview",
                        str(interview),
                        "--outline",
                        str(outline),
                        "--progress",
                        str(progress),
                        "--strict",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    result.stdout + result.stderr,
                )


if __name__ == "__main__":
    unittest.main()
