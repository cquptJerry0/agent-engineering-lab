# Agent Engineering Lab

这个仓库用于建立一套完整、现代、可迁移的 Agent 开发知识体系。

当前阶段只固化学习地图、覆盖范围和学习方法，不提前确定周计划、主框架或最终项目形态。

## 学习目标

1. 快速掌握 Agent 开发的核心原理，而不是先堆框架 API。
2. 工程类面试题暂不作为独立背诵任务，通过原理、实验和项目自然吸收。
3. 建立能串联主流 Agent 体系的统一心智模型，并最终通过一个贯穿项目完成整合。
4. 保证核心知识覆盖完整，避免纯项目驱动造成知识盲区。

## 核心方法

```text
完整知识地图
    +
最小机制实验
    +
贯穿项目
    +
覆盖台账与评测
```

项目负责串联和验证，不负责决定学习范围。

## 总体心智

```text
Agent System
│
├── Model Foundations
├── Model Interaction Primitives
├── Agent Loop
├── Context and State
├── Tools and Environment
├── Knowledge and Retrieval
├── Orchestration Patterns
├── Graph and Durable Runtime
├── Harness
└── Evaluation, Reliability and Security
```

`Loop` 是执行内核，`Graph` 是复杂控制流与持久化执行的表达方式，`Harness` 是围绕模型和执行循环建立的环境、工具、权限、反馈与验证系统。三者不是线性替代关系。

## 文档导航

| 文档 | 用途 |
|---|---|
| [知识地图](docs/knowledge-map.md) | 定义完整学习边界、模块依赖和目标深度 |
| [学习机制](docs/learning-system.md) | 定义如何兼顾系统覆盖、原理理解和项目串联 |
| [覆盖台账](docs/coverage-ledger.md) | 跟踪每个核心知识点的学习状态与掌握证据 |
| [ADR-0001](docs/adr/0001-learning-architecture.md) | 记录当前学习架构的选择与取舍 |

## 当前已确定

- 不采用纯项目驱动。
- 不采用数百节课程从头到尾线性学习。
- 每个核心知识点都需要学习，但目标深度不同。
- 核心机制至少需要做到能解释、能做最小实现、能识别失败边界。
- 贯穿项目后续单独讨论，目前不反向限制知识地图。

## 后续待讨论

- 每个模块的具体资料与学习顺序。
- 第一轮学习的时间预算。
- Python、TypeScript、Java 中的主实验语言。
- 贯穿项目的业务目标与验收标准。
- 主框架以及框架切换和对照策略。
- 如何设计阶段测验、复习机制和最终评测集。

## 原始参考材料

- [入行 AI，看这篇分享就够了](https://docs.qq.com/doc/DUFFheFJiQ0VWbmVO)
- [双元 AI 之 JavaAI](https://docs.qq.com/mind/DUHJrb0FsY2tTWkpK)
- [AI4.0 双元 AI 之 PythonAI 体系](https://docs.qq.com/mind/DUHRIZ2J1UkVXTHNC)
- [RAG 智能问答系统架构图](https://docs.qq.com/slide/DUHJEeEZwUm5ndWxI)
- [大模型驱动的多模态智能客服系统](https://docs.qq.com/slide/DUE52REtpTEpoZ1po)
- [基于 Agent 的企业智能办公助手](https://docs.qq.com/slide/DUGNQanpIZm1HeWJ6)
- [白泽 AI 大模型面试题库](https://docs.qq.com/mind/DUFVrUFpscW5QTGta)

这些材料作为知识索引、专题补充、架构检查表和问题库使用，不直接作为线性学习顺序。
