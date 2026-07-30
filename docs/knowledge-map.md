# Agent 开发知识地图

## 1. 地图目标

这份地图解决两个问题：

1. 学习范围不能由单个项目偶然遇到的问题决定。
2. 不同知识的学习深度不能平均分配。

因此，知识地图负责保证覆盖，掌握等级负责控制投入。

## 2. 掌握等级

| 等级 | 掌握要求 | 典型证据 |
|---|---|---|
| L1 识别 | 知道它解决什么问题，位于系统哪里 | 能画出位置并说出适用场景 |
| L2 解释 | 能解释机制、边界、取舍与常见失败 | 能完成对比和失败分析 |
| L3 实现 | 能不依赖高级封装完成最小实现 | 有可运行实验和测试 |
| L4 工程化 | 能处理规模、可靠性、安全与演进问题 | 有生产设计、压测和故障验证 |

第一轮不追求所有内容达到 L4。Agent 主干以 L3 为主，模型训练、视觉和具身智能等支线先达到 L1 或 L2。

## 3. 总体结构

```text
┌─────────────────────────────────────────────────────┐
│ Evaluation / Reliability / Security                 │
│                                                     │
│  ┌──────────────── Harness ──────────────────────┐  │
│  │ Instructions / Context / Tools / Environment  │  │
│  │ Permission / Sandbox / Trace / Verification   │  │
│  │                                               │  │
│  │  ┌──────── Graph and Durable Runtime ──────┐  │  │
│  │  │ State / Node / Edge / Checkpoint       │  │  │
│  │  │ Interrupt / Resume / Retry / Recovery   │  │  │
│  │  │                                         │  │  │
│  │  │  ┌────────── Agent Loop ─────────────┐  │  │  │
│  │  │  │ Observe → Decide → Act → Verify   │  │  │  │
│  │  │  │             ↖ Continue / Stop     │  │  │  │
│  │  │  └───────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

上图表达的是包含关系，不是学习顺序：

- `Loop` 解释 Agent 如何逐步行动。
- `Graph` 显式表达状态、分支、循环、暂停和恢复。
- `Harness` 决定模型能看到什么、能做什么、如何得到反馈。
- `Evaluation`、可靠性和安全约束整个系统，而不是最后附加的模块。

## 4. 主干知识模块

### M0 模型与表示基础

目标深度：L2。

需要理解模型能力从哪里来，以及它为什么会在 Agent 中失败，不追求完整训练算法推导。

- Token、Tokenizer 与上下文窗口。
- Transformer、Self-Attention 和位置编码的直觉。
- 预训练、指令微调、偏好对齐与推理的区别。
- Embedding 的表示意义与相似度。
- 自回归生成与下一 Token 预测。
- Temperature、Top-p、Stop 等解码参数。
- 幻觉、非确定性、知识截止与上下文依赖。
- 多模态模型的输入、输出和能力边界。
- 模型规模、延迟、成本、窗口和工具能力的选型维度。
- Fine-tuning、RAG、Prompt 和 Tool Use 分别改变什么。

完成标准：能从模型机制解释 Agent 的不稳定性、上下文限制和工具调用必要性。

### M1 模型交互原语

目标深度：L3。

- System、Developer、User、Assistant、Tool 消息语义。
- 请求与响应的真实数据结构。
- Structured Output 与 Schema 约束。
- Function Calling 和 Tool Calling 协议。
- 流式响应与事件模型。
- 多模态消息组织。
- Token Usage、Finish Reason 和错误响应。
- 超时、限流、重试、退避和请求取消。
- 幂等键、请求追踪和模型供应商差异。
- 原生 API 与框架封装的边界。

完成标准：能直接调用模型 API，实现流式输出、结构化结果和一次完整工具调用。

### M2 Agent Loop 与决策

目标深度：L3。

- Observe、Reason、Act、Result、Stop 的最小循环。
- ReAct 的工作方式与局限。
- 工具选择、参数生成和结果回填。
- 终止条件、最大步数和预算。
- Planning 与边执行边规划。
- 计划重写、失败重试和局部恢复。
- Reflection 与 Self-Correction。
- Evaluator-Optimizer 循环。
- 确定性代码与模型决策的边界。
- 死循环、重复调用、错误累积和奖励投机。

完成标准：能手写最小 Agent Loop，并通过日志解释每一轮为什么继续或停止。

### M3 Context、State 与 Memory

目标深度：L3。

- Prompt 与 Context 的区别。
- 静态上下文、动态上下文和运行时上下文。
- Context Selection、Compression、Isolation。
- 消息窗口裁剪、摘要和 Compaction。
- Working Memory 与任务草稿。
- Session State 与持久化状态。
- Episodic、Semantic、Procedural Memory。
- 长期记忆写入、检索、更新和遗忘。
- 文件系统和 Artifact 作为外部记忆。
- Context Pollution、Context Rot 和信息冲突。
- Subagent 上下文隔离。
- 多用户、多会话和多任务状态边界。

完成标准：能说明一条信息应该放入当前上下文、状态存储、长期记忆还是外部文件，并实现最小压缩和恢复。

### M4 Tools、Environment 与协议

目标深度：L3。

- Tool Schema、描述、粒度和返回契约。
- 参数校验、错误分类和失败语义。
- 只读工具、写工具和高风险工具。
- 工具幂等、超时、重试、取消和补偿。
- 串行、并行和批量工具调用。
- 工具结果压缩与大结果外置。
- Shell、Filesystem、Browser、Database、HTTP API 环境。
- Sandbox、资源限制和副作用隔离。
- MCP 的 Host、Client、Server、Transport 和 Capability。
- MCP 与普通函数调用、SDK、Skills 的边界。
- Tool Discovery、动态工具加载和权限过滤。
- 人工审批与可恢复执行。

完成标准：能设计一个模型易于正确调用、失败可诊断、权限可控制的工具，并能解释何时需要 MCP。

### M5 Knowledge、Search 与 RAG

目标深度：L2 至 L3。

- 文档解析、清洗、切分与元数据。
- Embedding 模型和向量索引。
- Dense、Sparse、Keyword、Hybrid Search。
- Query Rewrite、Expansion、Decomposition。
- Metadata Filter 和权限感知检索。
- Top-k、阈值、召回率和精确率。
- Rerank 与上下文排序。
- 引用、溯源和证据绑定。
- Retrieval Eval 与 Generation Eval。
- Agentic Search 与固定 RAG Pipeline。
- 长上下文、文件搜索、数据库查询和 RAG 的选择。
- 知识增量更新、版本和删除。

完成标准：能搭建最小检索链路，并分别定位“没召回”和“召回了但答错”的问题。

### M6 Orchestration Patterns

目标深度：L3。

- Prompt Chaining。
- Router。
- Parallelization。
- Map-Reduce。
- Planner-Executor。
- Orchestrator-Workers。
- Evaluator-Optimizer。
- Reflection。
- Handoff。
- Agent as Tool。
- Supervisor 与 Subagent。
- Multi-Agent Collaboration。
- 动态任务分解与静态工作流。
- 上下文共享、隔离与结果聚合。

每个模式都需要回答：

1. 控制权在代码还是模型。
2. 状态由谁维护。
3. 失败在哪里重试。
4. 上下文是否隔离。
5. 是否真的需要多个 Agent。

完成标准：能用同一问题比较至少三种编排方式，并解释复杂度增加是否值得。

### M7 Graph 与 Durable Runtime

目标深度：L3。

- State、Node、Edge。
- Conditional Edge、Loop 和 Reducer。
- Command、Event 与状态转换。
- Subgraph 和模块边界。
- Checkpoint、Thread 和持久化。
- Interrupt、Human-in-the-loop 和 Resume。
- Retry Policy、Timeout 和 Cancellation。
- Durable Execution 与进程崩溃恢复。
- 节点幂等和副作用管理。
- Time Travel、Replay 和 Debug。
- 流式事件和进度输出。
- 确定性节点与 Agent 节点混合。

完成标准：能把一个包含分支、循环、审批和恢复的流程建模为显式状态图，并验证中断后续跑。

### M8 Harness Engineering

目标深度：L3。

- Instructions、Rules 和约束组织。
- Context 构建与按需加载。
- Tool Interface 和 Toolset 设计。
- Skills、领域知识包和渐进披露。
- Filesystem、Shell、Browser 和代码执行环境。
- Sandbox、Workspace 和 Artifact 管理。
- Hook、Middleware 和生命周期扩展点。
- 权限模型、审批和最小权限。
- 环境反馈和 Verification。
- 长任务计划、进度记录与接力。
- Subagent 隔离、并行和汇总。
- Context Compression 与外部状态。
- 模型、工具和环境的可替换性。

完成标准：能解释同一个模型为什么会因 Harness 不同产生显著能力差异，并设计一个可验证、可恢复的工作环境。

### M9 Evaluation、可靠性与安全

目标深度：L3，贯穿所有模块。

- Trace、Span、Event 和完整执行轨迹。
- Golden Dataset 和任务样本设计。
- Offline Eval 与 Online Eval。
- Task Success、Tool Accuracy、Trajectory Quality。
- Retrieval、Generation 和端到端评测。
- Deterministic Check、Human Review、LLM as Judge。
- 回归测试和版本对比。
- 延迟、Token、成本和成功率预算。
- Prompt Injection、Tool Output Injection。
- 数据泄露、越权调用和供应链风险。
- Guardrail、Policy 和内容过滤。
- Least Privilege 和高风险动作审批。
- 故障注入、超时、降级和恢复。
- 人工反馈、线上监控和持续优化。

完成标准：每个实验和项目能力都有明确成功标准、失败样本和回归验证，而不是只看一次 Demo。

### M10 Agent 系统工程

目标深度：L2 至 L3，不单独背诵八股。

- API 服务、流式协议和异步任务。
- 并发、队列、背压和限流。
- 缓存、批处理和模型路由。
- 多租户、会话隔离和数据模型。
- 配置、密钥和环境管理。
- 日志、指标、Trace 和告警。
- 容器化、部署、扩缩容和灰度。
- 成本核算、预算和配额。
- 模型与 Prompt 版本管理。
- 数据保留、删除和合规。
- SLA、降级、灾备和恢复。

完成标准：能够把 Agent 从本地实验提升为有明确契约、可观测、可治理的服务。

## 5. 支线知识

这些内容需要进入知识地图，但第一轮不作为 Agent 主干的高投入项。

| 支线 | 第一轮目标 | 进入深入学习的触发条件 |
|---|---|---|
| 机器学习算法 | L1-L2 | 需要训练分类、排序或预测模型 |
| Transformer 数学推导 | L2 | 需要研究模型结构、推理优化或训练 |
| LoRA、QLoRA、SFT | L1-L2 | Prompt、RAG 和工具无法解决行为适配问题 |
| 推理部署与量化 | L1-L2 | 需要私有化模型或显著降低推理成本 |
| OpenCV、YOLO | L1 | 项目涉及传统视觉链路 |
| 多模态训练 | L1 | 需要定制视觉、语音或视频模型 |
| 具身智能 | L1 | 项目进入机器人或物理环境决策 |
| 分布式训练 | L1 | 目标转向模型训练工程 |

“低优先级”表示延后深入，不表示从知识地图中删除。

## 6. 概念定位

| 概念 | 在体系中的位置 |
|---|---|
| Prompt Engineering | Instructions 的设计方法 |
| Context Engineering | 每轮上下文的选择、组织、压缩与隔离 |
| Tool Calling | Loop 的行动接口 |
| MCP | 工具和资源的标准接入协议 |
| RAG | 获取外部知识和 Context 的一种机制 |
| Memory | 跨轮次或跨任务保存和恢复信息 |
| Skills | 可复用的指令、知识和工具使用说明 |
| Sandbox | Action 的隔离执行环境 |
| Human-in-the-loop | 执行过程的暂停、审批和恢复 |
| Graph | 显式状态与控制流 Runtime |
| Subagent | 隔离上下文并完成子任务的执行单元 |
| Multi-Agent | 多个 Agent Loop 的协作拓扑 |
| Harness | 环绕 Agent 的上下文、环境、工具和反馈系统 |
| Evals | 衡量能力、发现失败和驱动迭代的反馈系统 |

## 7. 依赖顺序

这不是具体学习排期，只表示认知依赖。

```text
模型基础
   ↓
模型交互原语
   ↓
Agent Loop
   ↓
Context / State / Tools
   ↓
Retrieval / Orchestration
   ↓
Graph / Durable Runtime
   ↓
Harness
   ↓
系统工程

Evaluation / Reliability / Security 贯穿全程
```

## 8. 地图维护原则

- 新概念必须先定位到现有模块，再判断是否需要新增模块。
- 框架名称不作为一级知识模块，框架只是机制实现样本。
- 热点名词不能因为流行就自动成为主干。
- 每个主干知识点都要进入覆盖台账。
- 每个模块后续都需要定义资料、机制实验和整合验证。
- 学习中发现知识缺口时，先更新地图和台账，再调整项目。
