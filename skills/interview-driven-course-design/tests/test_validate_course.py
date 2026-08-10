from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_course.py"

DYNAMIC = """# 动态课程

[学习总纲](总纲.md)定义知识真相源，[学习进度](进度.md)记录薄弱点。

## 动态选课

每次写明选课依据、覆盖知识点、中心问题和贯穿案例，再形成核心推导链。

当前 CU 包含推导式理解和面试训练。生成课程不更新进度，完成后再做状态写回，
然后根据进度重新计算下一 CU。
"""

SCHEDULED = """# 完整课程

### 第 01 课：基础
### 第 02 课：机制
### 第 03 课：实战
"""


class ValidateCourseTest(unittest.TestCase):
    def run_validator(
        self,
        content: str,
        *extra_args: str,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            course = root / "README.md"
            (root / "总纲.md").write_text("# 总纲\n", encoding="utf-8")
            (root / "进度.md").write_text("# 进度\n", encoding="utf-8")
            course.write_text(content, encoding="utf-8")
            return subprocess.run(
                ["python3", str(SCRIPT), str(course), "--strict", *extra_args],
                check=False,
                capture_output=True,
                text=True,
            )

    def test_accepts_dynamic_dual_track_design(self) -> None:
        result = self.run_validator(DYNAMIC)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_fixed_catalog_by_default(self) -> None:
        result = self.run_validator(SCHEDULED)
        self.assertEqual(result.returncode, 1)
        self.assertIn("默认应只设计当前 CU", result.stdout)

    def test_scheduled_catalog_requires_snapshot_contract(self) -> None:
        result = self.run_validator(SCHEDULED, "--allow-scheduled-catalog")
        self.assertEqual(result.returncode, 1)
        self.assertIn("快照声明", result.stdout)


if __name__ == "__main__":
    unittest.main()
