---
half_life: 7d
archive_at: 2026-08-23
artifact_mode: delivery-doc
scope_type: version
scope_name: prism-v0
coverage: Prism 内核、免费/企业切分、SkillHub 分发准备、Lucas 素材管道的 v0 阶段计划与并行轨道
not_complete_for: Chrome 悬停插件、公网工作室、SkillHub 实际上架、WorkBuddy 企业席位实测、付费结算、Viko 式创作者社区
verification_level: local
real_smoke_status: not_required
review_status: not_reviewed
reviewer: none
review_command: python3 /Users/sunny/.agents/skills/delivery-planner/scripts/check_delivery_doc.py docs/prism-v0-plan.md
review_notes: 计划由当前会话起草，尚未独立 review
review_owner: human:ender
review_due: 2026-08-20
execution_backend: direct
lead_agent: current
peer_agents: none
builder_agent: none
verifier_agent: none
verification_independence: self_checked
cwf_decision: not_needed
cwf_trigger_boundary: none
goal_handoff: none
acceptance_contract_status: proposed
memory_required: false
memory_space: none
acceptance_memory_id: none
memory_asserted_by: none
memory_confirmed_by: none
memory_intended_for: none
memory_validity: proposed
memory_valid_from: 2026-08-16
memory_review_due: event:owner-confirm
---

# Prism v0 阶段计划

产品名 Prism（棱镜）。仓库目录暂用 `VIKO`，对外文档和 skill id 只用 `prism`。

本版把个人拆图能力做成可被 Codex、Grok、WorkBuddy 共用的 skill 内核；免费包走腾讯 SkillHub 获客；组织级共享、品牌锁、MCP、审计留给 BF Labs 定制的 WorkBuddy 企业版。不复制 Viko 网站、积分和创作者俱乐部。

## Alignment

- 做：类型化拆图合同、自然语言编译、本地词卡库、免费/企业对照、可上架的 skill 包形、一条可录的拆图演示。
- 不做：账号积分、开卡包云工作室、悬停插件一期、自建 GitHub、没席位就宣称企业版已跑通。
- 真相源：本仓库 `schema/`、`skill/SKILL.md`、`docs/tiers.md`、WorkBuddy 企业测试方案 V1、腾讯 SkillHub 公开说明。
- 验证：本地 CLI 与 fixture 编译；SkillHub / 企业席位属于后续外部动作，本版不验收。

## 四条可并行轨道

四条轨道共享同一份 schema 和 `docs/tiers.md`，互不堵开工。合并点只在「skill 包能被 Codex 读到，并且 `prism compile` 对 fixture 稳定出散文」。

```
        schema + tiers（已作为底座）
           /        |         \         \
     A 内核评测   B 包装分发   C 企业对照   D 素材管道
           \        |         /         /
              v0 合并：可安装 skill + 一条演示稿
```

| 轨道 | 产出 | 可并行 | 停条 |
|---|---|---|---|
| A 内核 | schema、编译器、CLI、20 条 eval 夹具 | 是 | `prism compile` 对 4 类 fixture 都吐出含「避免」段的散文 |
| B 包装 | `SKILL.md`、`skill.yml`、SkillHub 清单、工蜂/GitHub 镜像说明 | 是 | 包内无密钥、路径可相对解析、安装说明只指向 SkillHub 而未实际上架 |
| C 企业对照 | `docs/tiers.md` 冻结免费/企业切分 | 是 | 付费点只含共享库、品牌锁、MCP、审计、定时数字员工；不含生图次数 |
| D 素材 | Lucas 用的 60–90 秒脚本 + 输入样本清单 | 是 | 脚本含输入、操作、结果、人工修正；不写未验证企业能力 |

Chrome 悬停采集、公网站、SkillHub 提交、企业席位实测标为 v0.1+，本版不开工。

## 阶段

### 阶段 0 — 底座（本回合）

- 冻结产品名、切分和四轨道。
- 落地 4 类 schema、编译顺序、CLI、skill 骨架、eval 目录。
- 证据：`python3 scripts/prism.py check` 退出 0。

### 阶段 1 — 可演示内核（本机，不接外部账号）

- 补 20 条夹具：人像、海报、产品、插画各 5；每条含结构化字段和期望散文锚点。
- 人看 8 张难图：复杂姿势海报 2、强配色产品 2、脸易漂二次元 2、文字海报 2。只评编译质量，不评真实生图。
- 停：8 张中至少 6 张人判「可直接丢给 GPT Image」，且都带失败风险句。

### 阶段 2 — 包装（仍不上架）

- 按腾讯 SkillHub / WorkBuddy skill 市场字段填 `skill.yml`。
- README 用中文写清免费边界和国内安装路径。
- 停：dry-run 打包无绝对路径、无 token、无客户数据。

### 阶段 3 — 外部动作（需 Ender 单独批准）

每项单独批准，不打包进 v0：

1. 上传腾讯 SkillHub。
2. 镜像到工蜂或 CODING。
3. 上传小红书 SkillHub。
4. 用真实 WorkBuddy 企业席位跑共享库/权限。
5. Lucas 对外发布视频。

## 模块

| 模块 | 路径 | 职责 |
|---|---|---|
| 类型合同 | `schema/*.json` | 人像/海报/产品/插画字段与轴 |
| 编译器 | `scripts/prism.py` + `skill/references/compile.md` | JSON seed 收成禁止词汤的中文散文 |
| 词卡库 | `vault/cards.jsonl` | 本地原子词，五轴抽卡 |
| Agent 入口 | `skill/SKILL.md` | Codex / Grok / WorkBuddy 同一合同 |
| 切分 | `docs/tiers.md` | 免费与企业版锁什么 |
| 评测 | `evals/` | fixture 与难图清单 |

## 失败路径

- 没有视觉模型：CLI 只编译已有 JSON，不假装反推了原图。
- 图像类型不明：默认 `generic`，并在 notes 标明估计。
- 企业功能被写进免费 skill：`tiers.md` 为否决源，skill 正文不得承诺共享库或审计。
- SkillHub 上架失败：源码仍可通过 git 克隆；安装文档改写失败原因，不改内核。

## 优先级

- P0：schema、compile、CLI check、tiers、SKILL.md
- P1：20 fixture、8 张难图人审、skill.yml
- P2：目录页文案、演示脚本
- P3：SkillHub / 工蜂 / 企业席位

## 已知未决（不阻塞 v0 底座）

- 最终对外中文名用「棱镜」还是同时保留英文 Prism：默认双写。
- 企业席位到位时间：阶段 3 保持 blocked。
- 是否做悬停插件：等阶段 1 人审后再议。
