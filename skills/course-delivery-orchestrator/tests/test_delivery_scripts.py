from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATE = SKILL_ROOT / "scripts" / "validate_lesson.py"
COURSE_STATE = SKILL_ROOT / "scripts" / "course_state.py"

CATALOG = """# 课程目录

### 第 01 课：模型基础
### 第 02 课：请求协议
### 第 03 课：工具调用
"""

LEARNING = """# 模型与真实 API - 推导式理解

> 课程状态：待复核
> 覆盖课程：第 01、02、03 课

## 核心推导链

```text
自然语言任务
  ↓
模型生成候选结果
  ↓
API 传输事件
  ↓
工具执行与验证
```

## 完整流程概览

| 层次 | 主要问题 | 解决机制 |
|---|---|---|
| 模型 | 怎样生成 | Token 概率 |
| API | 怎样传输 | 消息与事件 |
| 工具 | 怎样执行 | 校验与回填 |

## 一、模型怎样从上下文生成下一个 Token

### 为什么需要？

开放任务没有固定答案。

### ASCII 图：模型怎样逐步生成？

```text
输入 → Token → 概率分布 → 选择 → 继续生成
```

### 正常实验

重复调用并记录输出变化。

### 失败实验

强制唯一答案，观察模型补全缺失证据。

### 边界、代价与下一步

生成合理不等于事实正确，因此需要真实协议与工具。

## 二、真实 API 与工具协议怎样形成闭环

### 为什么需要？

模型输出必须经过程序执行和回填。

### ASCII 图：工具请求怎样变成验证结果？

```text
模型请求 → Schema → 权限 → 执行 → 回填 → 验证
```

### 正常实验

打印请求、工具结果和结束原因。

### 失败实验

让参数格式合法但业务越权。

### 边界、代价与下一步

工具成功仍不等于业务成功。

## 口语化输出模板

### 面试题：一次模型调用的输入、输出和停止条件分别是什么？

模型接收消息和参数，返回内容、工具请求和结束原因。

### 面试题：为什么工具参数通过 Schema 校验后仍需业务与权限校验？

Schema 只保证格式合法，不保证语义和权限合法。

## 自测问题

- 为什么模型停止不等于 Agent 完成？
- 合法 JSON 能证明什么？

## 知识图谱

```text
模型生成
  ├─ API 事件
  └─ 工具协议
       └─ 业务验证
```

## 面试题拆分清单

| 面试题 | 对应学习章节 | 最终答案文档 | 实验证据 |
|---|---|---|---|
| 一次模型调用的输入、输出和停止条件分别是什么？ | 第一、二章 | [最终答案](../面试答案/最终答案-Agent模型与API篇.md) | 请求 Trace |
| 为什么工具参数通过 Schema 校验后仍需业务与权限校验？ | 第二章 | [最终答案](../面试答案/最终答案-Agent模型与API篇.md) | 越权失败实验 |
"""

INTERVIEW = """# Agent 模型与 API 篇 - 面试最终答案（2 道题）

> 对应学习文档：[模型与真实 API](../学习文档/第01-03课-模型与真实API-推导式理解.md)

## 1. 一次模型调用的输入、输出和停止条件分别是什么？

题型：原理型

教科书定义：

模型调用接收消息和参数，返回内容、工具请求和结束原因。

启发式思维：

| 问题 | 回答 |
|---|---|
| 没有它会怎样 | 客户端无法区分输入、输出和结束状态 |
| 怎么解决 | 定义消息、响应和结束原因 |
| 好处 | 可以统一编排模型和工具 |
| 坏处或边界 | 模型结束不等于任务完成 |

口语化输出：

> 一次模型调用先接收消息和运行参数，再生成文本或工具请求，并用结束原因说明本轮为什么停止。

ASCII 图或关键表：

```text
消息 → 模型 → 内容或工具请求 → 结束原因
```

追问点：

Q: 为什么有文本不等于成功？

实验或 Trace 证据：

打印完整请求、响应和结束原因。

对应学习章节：

第一、二章。

## 2. 为什么工具参数通过 Schema 校验后仍需业务与权限校验？

题型：工程型

教科书定义：

Schema 只检查字段结构，业务和权限需要确定性程序判断。

启发式思维：

| 问题 | 回答 |
|---|---|
| 没有它会怎样 | 合法格式可能执行越权操作 |
| 怎么解决 | 分离格式、业务和权限校验 |
| 好处 | 阻止错误和越权副作用 |
| 坏处或边界 | 校验规则也需要维护 |

口语化输出：

> Schema 只能证明参数长得对，业务校验判断参数有没有意义，权限校验判断当前用户能不能执行。

ASCII 图或关键表：

```text
Schema → 业务语义 → 权限 → 执行 → 回读
```

追问点：

Q: 模型能否决定用户权限？

实验或 Trace 证据：

使用合法但越权的回滚参数执行失败实验。

对应学习章节：

第二章。
"""


class DeliveryScriptsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.catalog = self.root / "catalog.md"
        self.learning_dir = self.root / "学习文档"
        self.interview_dir = self.root / "面试答案"
        self.learning = self.learning_dir / "第01-03课-模型与真实API-推导式理解.md"
        self.interview = self.interview_dir / "最终答案-Agent模型与API篇.md"
        self.learning_dir.mkdir()
        self.interview_dir.mkdir()
        self.catalog.write_text(CATALOG, encoding="utf-8")
        self.learning.write_text(LEARNING, encoding="utf-8")
        self.interview.write_text(INTERVIEW, encoding="utf-8")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_validate(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(VALIDATE),
                str(self.learning),
                "--interview",
                str(self.interview),
                "--catalog",
                str(self.catalog),
                "--strict",
            ],
            check=False,
            text=True,
            capture_output=True,
        )

    def test_dual_track_documents_validate_and_map_all_courses(self) -> None:
        validate = self.run_validate()
        self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)

        state = subprocess.run(
            [
                "python3",
                str(COURSE_STATE),
                str(self.catalog),
                "--lessons-dir",
                str(self.learning_dir),
                "--json",
            ],
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual(state.returncode, 0, state.stdout + state.stderr)
        result = json.loads(state.stdout)
        self.assertEqual(result["pending_review"], 3)
        self.assertEqual(
            {lesson["artifact"] for lesson in result["lessons"]},
            {str(self.learning)},
        )

    def test_full_interview_answer_sections_are_rejected_in_learning_doc(self) -> None:
        invalid = LEARNING.replace(
            "## 自测问题",
            "## 30 秒回答\n\n不应出现在学习正文。\n\n## 自测问题",
        )
        self.learning.write_text(invalid, encoding="utf-8")

        validate = self.run_validate()
        self.assertEqual(validate.returncode, 1)
        self.assertIn("不应包含完整面试答案章节", validate.stdout)

    def test_missing_split_question_is_rejected(self) -> None:
        truncated = INTERVIEW.split(
            "## 2. 为什么工具参数通过 Schema 校验后仍需业务与权限校验？"
        )[0]
        self.interview.write_text(truncated, encoding="utf-8")

        validate = self.run_validate()
        self.assertEqual(validate.returncode, 1)
        self.assertIn("尚未拆出学习文档中的题目", validate.stdout)


if __name__ == "__main__":
    unittest.main()
