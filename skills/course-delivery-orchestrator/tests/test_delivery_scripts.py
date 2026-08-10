from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATE = SKILL_ROOT / "scripts" / "validate_lesson.py"
COURSE_STATE = SKILL_ROOT / "scripts" / "course_state.py"

POINTS = ("模型生成", "请求结构", "工具校验")

LEARNING = """# CU-001：模型到行动 - 推导式理解

> CU 状态：未开始
> 生成依据：当前进度全部未开始
> 覆盖知识点：3 个

## 选课依据与覆盖知识点

| 序号 | 知识点 | 总纲主归属 | 当前状态 | 本 CU 作用 |
|---|---|---|---|---|
| 1 | 模型生成 | 第一部分 | 未开始 | 理解候选输出 |
| 2 | 请求结构 | 第一部分 | 未开始 | 承载输入输出 |
| 3 | 工具校验 | 第二部分 | 未开始 | 控制真实执行 |

## 核心推导链

```text
文本任务 → 候选输出 → 请求结构 → 工具校验 → 真实行动
```

## 贯穿案例与初始状态

研发 Agent 调查一次发布失败。

## 阶段一：模型生成只能给候选

已有能力是生成文本，问题是没有真实状态。引入请求结构，留下怎样执行的问题。

## 阶段二：请求结构承载行动意图

请求把输入输出分开，问题是结构合法不代表允许执行。引入工具校验。

## 阶段三：工具校验形成受控行动

程序检查参数和权限，执行后回填结果，留下下一 CU 的循环验证问题。

## 正常链路与失败链路

```text
正常：请求 → 校验 → 执行 → 回填
失败：请求 → 越权 → 拒绝 → 错误回填
```

## 最小实验

发送合法请求和合法但越权的请求，比较结果。

## 边界、代价与下一问题

单次工具调用没有形成循环，下一问题是 Agent 怎样决定继续或停止。

## 自测问题

- 为什么模型输出不等于执行成功？

## 知识图谱

```text
模型生成
  └─ 请求结构
       └─ 工具校验
```

## 面试题索引

### 面试题：为什么模型输出不能直接当成真实行动？

对应阶段一到阶段三。

### 面试题：为什么 Schema 校验后仍需要权限校验？

对应阶段三。
"""

INTERVIEW = """# CU-001：模型到行动 - 面试训练

> 对应推导式理解：[推导式理解](推导式理解.md)

## 1. 为什么模型输出不能直接当成真实行动？

题型：原理型

一句话核心判断：模型产生候选，程序拥有执行控制权。

启发式思考：

| 思考 | 回答 |
|---|---|
| 没有它会怎样 | 模型描述会被误当成结果 |
| 最小机制是什么 | 分离意图、执行和回填 |
| 工程收益 | 可以验证和审计 |
| 边界和代价 | 执行器需要维护 |

30 秒回答：

> 模型只生成候选内容或行动意图，程序还要校验参数、权限和真实结果。

完整回答：

模型没有直接控制外部系统，工具执行器才拥有副作用控制权。

ASCII 图或关键表：

```text
模型意图 → 程序校验 → 工具执行 → 结果回填
```

追问：

- 原理追问：自回归生成意味着什么？
- 工程追问：怎样防止重复副作用？
- 项目追问：你如何保存调用证据？

证据：

合法请求与越权请求的对照 Trace。

对应推导章节：

阶段一到阶段三。

## 2. 为什么 Schema 校验后仍需要权限校验？

题型：工程型

一句话核心判断：结构合法不代表业务允许。

启发式思考：

| 思考 | 回答 |
|---|---|
| 没有它会怎样 | 合法参数可能越权 |
| 最小机制是什么 | 分离结构、业务和权限校验 |
| 工程收益 | 限制错误副作用 |
| 边界和代价 | 权限规则需要维护 |

30 秒回答：

> Schema 只保证字段形状，业务规则和用户权限必须由确定性程序单独判断。

完整回答：

工具参数来自不可信模型输出，执行前需要逐层校验。

ASCII 图或关键表：

```text
Schema → 业务语义 → 权限 → 执行
```

追问：

- 原理追问：Schema 能证明什么？
- 工程追问：审批放在哪一层？
- 项目追问：如何验证越权被拒绝？

证据：

合法但越权参数的失败实验。

对应推导章节：

阶段三。
"""


class DeliveryScriptsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.course_root = self.root / "课程"
        self.cu = self.course_root / "CU-001-模型到行动"
        self.cu.mkdir(parents=True)
        self.learning = self.cu / "推导式理解.md"
        self.interview = self.cu / "面试训练.md"
        self.outline = self.root / "学习总纲.md"
        self.progress = self.root / "学习进度.md"
        self.learning.write_text(LEARNING, encoding="utf-8")
        self.interview.write_text(INTERVIEW, encoding="utf-8")
        source = "\n".join(POINTS)
        self.outline.write_text(source, encoding="utf-8")
        self.progress.write_text(source, encoding="utf-8")

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
                "--outline",
                str(self.outline),
                "--progress",
                str(self.progress),
                "--strict",
            ],
            check=False,
            text=True,
            capture_output=True,
        )

    def test_dual_track_cu_validates_and_state_scans_directory(self) -> None:
        validate = self.run_validate()
        self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)

        state = subprocess.run(
            [
                "python3",
                str(COURSE_STATE),
                str(self.course_root),
                "--json",
            ],
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual(state.returncode, 0, state.stdout + state.stderr)
        result = json.loads(state.stdout)
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["current"]["id"], "CU-001")
        self.assertEqual(result["current"]["knowledge_points"], 3)
        self.assertEqual(result["current"]["status"], "未开始")

    def test_full_interview_sections_are_rejected_in_learning_track(self) -> None:
        invalid = LEARNING.replace(
            "## 自测问题",
            "## 30 秒回答\n\n不应出现在第一轨。\n\n## 自测问题",
        )
        self.learning.write_text(invalid, encoding="utf-8")
        validate = self.run_validate()
        self.assertEqual(validate.returncode, 1)
        self.assertIn("不应包含完整面试训练章节", validate.stdout)

    def test_missing_interview_question_is_rejected(self) -> None:
        truncated = INTERVIEW.split(
            "## 2. 为什么 Schema 校验后仍需要权限校验？"
        )[0]
        self.interview.write_text(truncated, encoding="utf-8")
        validate = self.run_validate()
        self.assertEqual(validate.returncode, 1)
        self.assertIn("尚未覆盖第一轨索引中的题目", validate.stdout)

    def test_unknown_knowledge_point_is_rejected(self) -> None:
        self.progress.write_text("模型生成\n请求结构\n", encoding="utf-8")
        validate = self.run_validate()
        self.assertEqual(validate.returncode, 1)
        self.assertIn("学习进度中未找到覆盖知识点: 工具校验", validate.stdout)


if __name__ == "__main__":
    unittest.main()
