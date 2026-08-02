# 个人 Skills

## 1. 定位

这个目录保存与本仓库长期目标直接相关的个人 Skill 快照，便于版本管理、复用和后续迭代。

当前只归档三类：

- 调研与知识体系建设。
- 学习与课程设计。
- 简历、项目故事和工作总结。

业务专用、设备自动化、公司平台操作和通用第三方 Skill 不放入这里，避免把个人方法仓变成完整运行环境的镜像。

## 2. 当前清单

| Skill | 中文用途 | 分类 |
|---|---|---|
| [architecture-research](architecture-research/SKILL.md) | 多来源调研、知识合订和文档体系重构 | 调研 |
| [interview-driven-course-design](interview-driven-course-design/SKILL.md) | 将知识总纲编译成面试导向的高 ROI 课程 | 学习 |
| [extract-resume-stories](extract-resume-stories/SKILL.md) | 从业务与架构中提炼简历钩子和答辩故事 | 简历 |
| [resume-polish](resume-polish/SKILL.md) | 逐条优化简历项目经历和配套话术 | 简历 |
| [distill-work-summary](distill-work-summary/SKILL.md) | 提炼工作总结、成长、晋升和复盘材料 | 简历与沉淀 |

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
