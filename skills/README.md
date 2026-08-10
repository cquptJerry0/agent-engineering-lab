# 个人 Skills

## 1. 定位

这个目录保存与本仓库长期目标直接相关的个人 Skill 快照，便于版本管理、复用和后续迭代。

当前只归档三类：

- 调研与知识体系建设。
- 学习与课程设计。
- 简历、项目故事和工作总结。

业务专用、设备自动化、公司平台操作和通用第三方 Skill 不放入这里，避免把个人方法仓变成完整运行环境的镜像。

## 2. 当前清单

| 中文名称 | 内部标识 | 中文用途 | 分类 |
|---|---|---|---|
| [知识体系调研与总纲设计](architecture-research/SKILL.md) | `architecture-research` | 多来源调研、知识合订和文档体系重构 | 调研 |
| [自适应课程设计](interview-driven-course-design/SKILL.md) | `interview-driven-course-design` | 根据稳定知识图、动态进度和目标设计当前课程单元 | 学习 |
| [链路课程授课与面试训练](course-delivery-orchestrator/SKILL.md) | `course-delivery-orchestrator` | 先用贯穿案例形成推导链，再独立编译面试训练 | 学习 |
| [extract-resume-stories](extract-resume-stories/SKILL.md) | `extract-resume-stories` | 从业务与架构中提炼简历钩子和答辩故事 | 简历 |
| [resume-polish](resume-polish/SKILL.md) | `resume-polish` | 逐条优化简历项目经历和配套话术 | 简历 |
| [distill-work-summary](distill-work-summary/SKILL.md) | `distill-work-summary` | 提炼工作总结、成长、晋升和复盘材料 | 简历与沉淀 |

## 3. 目录规则

每个 Skill 保留完整目录，包括：

```text
skill-name/
├── SKILL.md
├── agents/
├── references/
├── scripts/
└── tests/
```

并非每个 Skill 都需要所有子目录，但已有资源必须整体保留，不能只复制`SKILL.md`导致脚本或参考资料失效。

## 4. 版本边界

- 本目录是仓库内的可审查版本，不假设具体 Agent 平台和用户目录。
- Skill 正文不得硬编码个人主目录下的绝对路径。
- 安装时将目标 Skill 目录同步到所用 Agent 平台的技能目录。
- 后续修改优先在仓库版本完成评审和校验，再同步到实际运行目录。

一句话收束：这个目录保存的是可复用方法，不是本机所有 Skill 的无差别备份。
