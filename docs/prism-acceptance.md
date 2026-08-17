---
half_life: 7d
archive_at: 2026-08-23
artifact_mode: delivery-doc
scope_type: version
scope_name: prism-v0
coverage: Prism v0 底座与阶段 1 的验收条目
not_complete_for: SkillHub 实际上架、WorkBuddy 企业席位、真实生图盲测、Chrome 插件
verification_level: local
real_smoke_status: not_required
review_status: not_reviewed
reviewer: none
review_command: python3 /Users/sunny/.agents/skills/delivery-planner/scripts/check_delivery_doc.py docs/prism-acceptance.md
review_notes: 与计划同时起草，尚未独立 review
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

# Prism v0 验收矩阵

| Criterion | Evidence level | Test or manual evidence | Status | Notes |
|---|---|---|---|---|
| 四类图像字段表可列出 | local | `python3 scripts/prism.py types` 与 `fields poster` | pass | 2026-08-16 本地检查 |
| fixture 能编译出含失败风险的散文 | fixture | `python3 scripts/prism.py check` | pass | 现有 4 条 fixture；20 条仍属阶段 1 |
| 免费/企业切分不含生图次数墙 | docs-only | `docs/tiers.md` 对照本表 | pass | |
| Skill 正文不承诺企业独占能力 | local | 阅读 `skill/SKILL.md` 与 `skill/skill.yml` | pass | forbidden_claims 已写 |
| 20 条 eval 夹具齐备 | fixture | `evals/cases.json` 计数与 4 类覆盖 | pass | 2026-08-16：每类 5 条，check 计数通过 |
| 8 张难图人审至少 6 张可投 GPT Image | local | `evals/hard-set.md` 签字 | pass | 8/8 编译可投 |
| 8 张 hard-set 真实 gpt-image-2 出图 | local | `evals/renders/` + `evals/hard-set.md` 实生表 | partial | 2026-08-16 best-of：可用 8/8，pass 6；H5 v3 已回绘画。H2/H8 仍漂。不记全过 |
| 参考图 decode 出可编译 seed | local | `evals/decode-smoke.md` + `prism decode` | pass | 2026-08-16：8/8 类型一致，validate+compile 通过 |
| decode→render 闭环 | local | `evals/renders/*-decode.png` + smoke 表 | partial | 2026-08-16：可用 7/8；H7 瓶即天空失败。不记全过 |
| SkillHub 上架 | real-smoke | 平台回执 | blocked | 需 Ender 批准外部写入 |
| WorkBuddy 企业共享库 | real-smoke | 席位录屏与权限对照 | blocked | 需企业席位 |

规则：fixture 与 docs-only 只证明底座和文案；SkillHub、企业席位、对外宣发必须 real-smoke。
