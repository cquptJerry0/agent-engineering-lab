# Agent 核心知识覆盖台账

## 使用说明

这份台账用于防止纯项目驱动造成遗漏。当前只定义首轮目标深度，所有知识点初始状态为“未开始”。

状态流转：

```text
未开始 → 已理解 → 已实验 → 已整合 → 已复核
```

同一个知识点可以不进入贯穿项目，但主干知识至少需要达到“已实验”。

## M0 模型与表示基础

| 编号 | 知识点 | 目标 | 状态 | 掌握证据 |
|---|---|---:|---|---|
| M0.1 | Token、Tokenizer、Context Window | L2 | 未开始 | 待补 |
| M0.2 | Transformer 与 Self-Attention 直觉 | L2 | 未开始 | 待补 |
| M0.3 | 自回归生成与下一 Token 预测 | L2 | 未开始 | 待补 |
| M0.4 | 预训练、指令微调、对齐与推理 | L2 | 未开始 | 待补 |
| M0.5 | Embedding 与相似度 | L2 | 未开始 | 待补 |
| M0.6 | 解码参数与非确定性 | L2 | 未开始 | 待补 |
| M0.7 | 幻觉与模型能力边界 | L2 | 未开始 | 待补 |
| M0.8 | 多模态模型基本机制 | L1-L2 | 未开始 | 待补 |
| M0.9 | Prompt、RAG、Tool、Fine-tuning 选型 | L2 | 未开始 | 待补 |

## M1 模型交互原语

| 编号 | 知识点 | 目标 | 状态 | 掌握证据 |
|---|---|---:|---|---|
| M1.1 | 消息角色与请求结构 | L3 | 未开始 | 待补 |
| M1.2 | Structured Output | L3 | 未开始 | 待补 |
| M1.3 | Function/Tool Calling 协议 | L3 | 未开始 | 待补 |
| M1.4 | 流式响应与事件模型 | L3 | 未开始 | 待补 |
| M1.5 | 多模态消息组织 | L2-L3 | 未开始 | 待补 |
| M1.6 | Usage、Finish Reason 与错误响应 | L3 | 未开始 | 待补 |
| M1.7 | 超时、限流、重试与取消 | L3 | 未开始 | 待补 |
| M1.8 | 供应商差异与适配边界 | L2 | 未开始 | 待补 |

## M2 Agent Loop 与决策

| 编号 | 知识点 | 目标 | 状态 | 掌握证据 |
|---|---|---:|---|---|
| M2.1 | Observe-Decide-Act-Verify Loop | L3 | 未开始 | 待补 |
| M2.2 | ReAct | L3 | 未开始 | 待补 |
| M2.3 | 工具选择与结果回填 | L3 | 未开始 | 待补 |
| M2.4 | 终止条件、步数与预算 | L3 | 未开始 | 待补 |
| M2.5 | Planning 与 Replanning | L3 | 未开始 | 待补 |
| M2.6 | Reflection 与 Self-Correction | L2-L3 | 未开始 | 待补 |
| M2.7 | Evaluator-Optimizer Loop | L3 | 未开始 | 待补 |
| M2.8 | 确定性代码与模型决策边界 | L3 | 未开始 | 待补 |
| M2.9 | 死循环、重复调用与错误累积 | L3 | 未开始 | 待补 |

## M3 Context、State 与 Memory

| 编号 | 知识点 | 目标 | 状态 | 掌握证据 |
|---|---|---:|---|---|
| M3.1 | Prompt 与 Context 的区别 | L3 | 未开始 | 待补 |
| M3.2 | 静态、动态和运行时上下文 | L3 | 未开始 | 待补 |
| M3.3 | Context Selection | L3 | 未开始 | 待补 |
| M3.4 | Window、Summary 与 Compaction | L3 | 未开始 | 待补 |
| M3.5 | Working Memory 与 Session State | L3 | 未开始 | 待补 |
| M3.6 | Episodic、Semantic、Procedural Memory | L2-L3 | 未开始 | 待补 |
| M3.7 | 长期记忆写入、检索和遗忘 | L3 | 未开始 | 待补 |
| M3.8 | Artifact 与文件系统外部记忆 | L3 | 未开始 | 待补 |
| M3.9 | Context Pollution 与 Context Rot | L3 | 未开始 | 待补 |
| M3.10 | 多会话与 Subagent 上下文隔离 | L3 | 未开始 | 待补 |

## M4 Tools、Environment 与协议

| 编号 | 知识点 | 目标 | 状态 | 掌握证据 |
|---|---|---:|---|---|
| M4.1 | Tool Schema、描述与粒度 | L3 | 未开始 | 待补 |
| M4.2 | 参数校验与错误契约 | L3 | 未开始 | 待补 |
| M4.3 | 工具幂等、超时、重试与补偿 | L3 | 未开始 | 待补 |
| M4.4 | 串行、并行与批量调用 | L3 | 未开始 | 待补 |
| M4.5 | 大结果压缩与外置 | L3 | 未开始 | 待补 |
| M4.6 | Shell、Filesystem、Browser、HTTP 环境 | L3 | 未开始 | 待补 |
| M4.7 | Sandbox 与副作用隔离 | L3 | 未开始 | 待补 |
| M4.8 | MCP 架构与 Transport | L3 | 未开始 | 待补 |
| M4.9 | MCP、Tool、SDK、Skill 的边界 | L3 | 未开始 | 待补 |
| M4.10 | 动态工具发现与权限过滤 | L2-L3 | 未开始 | 待补 |
| M4.11 | Human Approval 与可恢复执行 | L3 | 未开始 | 待补 |

## M5 Knowledge、Search 与 RAG

| 编号 | 知识点 | 目标 | 状态 | 掌握证据 |
|---|---|---:|---|---|
| M5.1 | 文档解析、清洗、切分与元数据 | L3 | 未开始 | 待补 |
| M5.2 | Embedding 模型与向量索引 | L3 | 未开始 | 待补 |
| M5.3 | Dense、Sparse 与 Hybrid Search | L3 | 未开始 | 待补 |
| M5.4 | Query Rewrite、Expansion、Decomposition | L2-L3 | 未开始 | 待补 |
| M5.5 | Metadata Filter 与权限感知检索 | L3 | 未开始 | 待补 |
| M5.6 | Top-k、阈值、召回率与精确率 | L3 | 未开始 | 待补 |
| M5.7 | Rerank | L3 | 未开始 | 待补 |
| M5.8 | 引用、溯源与证据绑定 | L3 | 未开始 | 待补 |
| M5.9 | Retrieval Eval 与 Generation Eval | L3 | 未开始 | 待补 |
| M5.10 | Agentic Search 与固定 RAG Pipeline | L2-L3 | 未开始 | 待补 |
| M5.11 | 知识增量更新与版本管理 | L2-L3 | 未开始 | 待补 |

## M6 Orchestration Patterns

| 编号 | 知识点 | 目标 | 状态 | 掌握证据 |
|---|---|---:|---|---|
| M6.1 | Prompt Chaining | L3 | 未开始 | 待补 |
| M6.2 | Router | L3 | 未开始 | 待补 |
| M6.3 | Parallelization | L3 | 未开始 | 待补 |
| M6.4 | Map-Reduce | L2-L3 | 未开始 | 待补 |
| M6.5 | Planner-Executor | L3 | 未开始 | 待补 |
| M6.6 | Orchestrator-Workers | L3 | 未开始 | 待补 |
| M6.7 | Evaluator-Optimizer | L3 | 未开始 | 待补 |
| M6.8 | Handoff 与 Agent as Tool | L3 | 未开始 | 待补 |
| M6.9 | Supervisor 与 Subagent | L3 | 未开始 | 待补 |
| M6.10 | Multi-Agent Collaboration | L2-L3 | 未开始 | 待补 |
| M6.11 | 上下文隔离、共享与结果聚合 | L3 | 未开始 | 待补 |

## M7 Graph 与 Durable Runtime

| 编号 | 知识点 | 目标 | 状态 | 掌握证据 |
|---|---|---:|---|---|
| M7.1 | State、Node、Edge | L3 | 未开始 | 待补 |
| M7.2 | Conditional Edge、Loop、Reducer | L3 | 未开始 | 待补 |
| M7.3 | Command、Event 与状态转换 | L3 | 未开始 | 待补 |
| M7.4 | Subgraph | L3 | 未开始 | 待补 |
| M7.5 | Checkpoint、Thread 与持久化 | L3 | 未开始 | 待补 |
| M7.6 | Interrupt、Approval 与 Resume | L3 | 未开始 | 待补 |
| M7.7 | Retry、Timeout 与 Cancellation | L3 | 未开始 | 待补 |
| M7.8 | Durable Execution 与崩溃恢复 | L3 | 未开始 | 待补 |
| M7.9 | 节点幂等与副作用管理 | L3 | 未开始 | 待补 |
| M7.10 | Replay、Time Travel 与 Debug | L2-L3 | 未开始 | 待补 |
| M7.11 | 流式事件与进度输出 | L3 | 未开始 | 待补 |

## M8 Harness Engineering

| 编号 | 知识点 | 目标 | 状态 | 掌握证据 |
|---|---|---:|---|---|
| M8.1 | Instructions、Rules 与约束组织 | L3 | 未开始 | 待补 |
| M8.2 | Context 构建与按需加载 | L3 | 未开始 | 待补 |
| M8.3 | Toolset 与能力边界 | L3 | 未开始 | 待补 |
| M8.4 | Skills 与渐进披露 | L3 | 未开始 | 待补 |
| M8.5 | Workspace、Sandbox 与 Artifact | L3 | 未开始 | 待补 |
| M8.6 | Hook、Middleware 与生命周期 | L3 | 未开始 | 待补 |
| M8.7 | 权限模型与最小权限 | L3 | 未开始 | 待补 |
| M8.8 | 环境反馈与 Verification | L3 | 未开始 | 待补 |
| M8.9 | 长任务计划与进度记录 | L3 | 未开始 | 待补 |
| M8.10 | Subagent 隔离、并行与汇总 | L3 | 未开始 | 待补 |
| M8.11 | 模型、工具和环境可替换性 | L2-L3 | 未开始 | 待补 |

## M9 Evaluation、可靠性与安全

| 编号 | 知识点 | 目标 | 状态 | 掌握证据 |
|---|---|---:|---|---|
| M9.1 | Trace、Span、Event 与执行轨迹 | L3 | 未开始 | 待补 |
| M9.2 | Golden Dataset | L3 | 未开始 | 待补 |
| M9.3 | Offline Eval 与 Online Eval | L3 | 未开始 | 待补 |
| M9.4 | Task、Tool、Trajectory 指标 | L3 | 未开始 | 待补 |
| M9.5 | Deterministic Check 与 Human Review | L3 | 未开始 | 待补 |
| M9.6 | LLM as Judge 与偏差 | L3 | 未开始 | 待补 |
| M9.7 | 回归测试与版本对比 | L3 | 未开始 | 待补 |
| M9.8 | 延迟、Token、成本与成功率预算 | L3 | 未开始 | 待补 |
| M9.9 | Prompt Injection | L3 | 未开始 | 待补 |
| M9.10 | Tool Output Injection 与数据泄露 | L3 | 未开始 | 待补 |
| M9.11 | Guardrail、Policy 与最小权限 | L3 | 未开始 | 待补 |
| M9.12 | 故障注入、降级与恢复 | L3 | 未开始 | 待补 |
| M9.13 | 人工反馈和持续优化 | L2-L3 | 未开始 | 待补 |

## M10 Agent 系统工程

| 编号 | 知识点 | 目标 | 状态 | 掌握证据 |
|---|---|---:|---|---|
| M10.1 | API、流式协议与异步任务 | L3 | 未开始 | 待补 |
| M10.2 | 并发、队列、背压和限流 | L2-L3 | 未开始 | 待补 |
| M10.3 | 缓存、批处理和模型路由 | L2-L3 | 未开始 | 待补 |
| M10.4 | 多租户、会话隔离和数据模型 | L3 | 未开始 | 待补 |
| M10.5 | 配置、密钥和环境管理 | L3 | 未开始 | 待补 |
| M10.6 | 日志、指标、Trace 和告警 | L3 | 未开始 | 待补 |
| M10.7 | 部署、扩缩容和灰度 | L2-L3 | 未开始 | 待补 |
| M10.8 | 成本、预算和配额 | L3 | 未开始 | 待补 |
| M10.9 | 模型与 Prompt 版本管理 | L3 | 未开始 | 待补 |
| M10.10 | 数据保留、删除和合规 | L2-L3 | 未开始 | 待补 |
| M10.11 | SLA、降级、灾备和恢复 | L2-L3 | 未开始 | 待补 |

## 支线

| 编号 | 知识点 | 目标 | 状态 | 深入触发条件 |
|---|---|---:|---|---|
| B1 | 机器学习核心算法 | L1-L2 | 未开始 | 需要训练传统模型 |
| B2 | Transformer 数学推导 | L2 | 未开始 | 研究模型或推理优化 |
| B3 | LoRA、QLoRA、SFT | L1-L2 | 未开始 | 需要调整模型行为 |
| B4 | 量化与私有化推理 | L1-L2 | 未开始 | 自部署或成本优化 |
| B5 | OpenCV、YOLO | L1 | 未开始 | 进入传统视觉链路 |
| B6 | 多模态训练 | L1 | 未开始 | 需要定制多模态模型 |
| B7 | 具身智能 | L1 | 未开始 | 进入物理环境决策 |
| B8 | 分布式训练 | L1 | 未开始 | 转向模型训练工程 |
