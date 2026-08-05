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

VALID_LESSON = """# 第 01-03 课：从模型生成到真实调用协议

> 课程状态：待复核
> 覆盖课程：第 01、02、03 课

## 1. 开课总览

### 目标面试题

- 一次模型调用的输入、输出和停止条件分别是什么？
- 为什么合法 JSON 不等于工具调用成功？

### 题目关系图

```text
输入 → 生成 → 工具请求 → 程序执行 → 验证
```

### 结构化答案骨架

输入、协议、执行、验证。

## 2. 推导学习

### 问题一：一次模型调用如何运行

#### ASCII 图：一次调用为什么没有直接完成任务？

```text
请求 → 模型 → 工具请求 → 执行 → 回填
```

#### 正常实验

打印请求、响应和结束原因。

#### 失败实验

达到长度限制但误判为完成。

### 问题二：工具请求为什么不是业务成功

#### ASCII 图：工具调用如何变成可验证结果？

```text
Schema → 权限 → 执行 → 回读 → 验证
```

#### 正常实验

执行只读查询并回读。

#### 失败实验

返回合法但越权参数。

## 3. 面试收束

### 题目原文

一次模型调用如何运行？

#### 30 秒回答

先讲请求，再讲输出和停止边界。

#### 3 分钟回答

用协议、工具和验证展开。

## 4. 覆盖检查

| 面试题 | 是否完整回答 | 正文依据 | 实验证据 | 仍缺什么 |
|---|---|---|---|---|
| 模型调用 | 是 | 问题一 | Trace | 无 |

## 5. 单元验收

能够画图并解释失败。

## 6. 仍未解决的问题

后续验证真实供应商差异。
"""


class DeliveryScriptsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.catalog = self.root / "catalog.md"
        self.lessons = self.root / "lessons"
        self.lesson = self.lessons / "第01-03课.md"
        self.lessons.mkdir()
        self.catalog.write_text(CATALOG, encoding="utf-8")
        self.lesson.write_text(VALID_LESSON, encoding="utf-8")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_combined_lesson_validates_and_maps_all_courses(self) -> None:
        validate = subprocess.run(
            [
                "python3",
                str(VALIDATE),
                str(self.lesson),
                "--catalog",
                str(self.catalog),
                "--strict",
            ],
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)

        state = subprocess.run(
            [
                "python3",
                str(COURSE_STATE),
                str(self.catalog),
                "--lessons-dir",
                str(self.lessons),
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
            {str(self.lesson)},
        )

    def test_question_ids_without_full_text_are_rejected(self) -> None:
        invalid = VALID_LESSON.replace(
            "- 一次模型调用的输入、输出和停止条件分别是什么？\n"
            "- 为什么合法 JSON 不等于工具调用成功？",
            "- AGENT-MODEL-001\n- AGENT-MODEL-003",
        )
        self.lesson.write_text(invalid, encoding="utf-8")

        validate = subprocess.run(
            [
                "python3",
                str(VALIDATE),
                str(self.lesson),
                "--catalog",
                str(self.catalog),
                "--strict",
            ],
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual(validate.returncode, 1)
        self.assertIn("完整问题原文", validate.stdout)


if __name__ == "__main__":
    unittest.main()
