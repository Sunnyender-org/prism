---
name: prism
description: >
  把参考图拆成类型化视觉合同，再编译成 GPT Image 可用的自然语言提示词，并沉淀可抽取的词卡。
  用于反推、拆风格、拆构图、抽色卡、锁脸、写失败风险、从词卡库抽一套再创作。
  不是通用 caption，不是 Midjourney 词汤，不提供企业共享库或审计。
---

# Prism

先读仓库 `docs/tiers.md`、`skill/references/compile.md` 和 `skill/references/decode.md`。字段以 `schema/types.json` 为准。

## 何时用

用户丢来一张图、一个截图，或说反推、拆图、拆风格、色卡、动作参考、词卡、竞品视觉简报时使用。

## 流程

1. 有参考图时先 `prism decode --image ...`；无图或无密钥时只编译已有 JSON，不假装看过原图。
2. 判断类型：`portrait` / `poster` / `product` / `illustration` / `scene`，不确定则 `generic` 并注明。
3. 只填该类型字段。必须包含 `core_style_contract`、`dynamic_negative_constraints`；人像/插画必须有 `face_archetype`。
4. 按 compile.md 收成一段中文散文。不要输出 JSON 给终端用户，除非对方明确要机器字段。
5. 把可独立迁移的短语标成词卡，轴只能是 style / subject / composition / color / motion。
6. 本地沉淀用 `python3 scripts/prism.py card-add`。

## 禁止

- 承诺 SkillHub 已上架、企业版已跑通、能 95% 复刻 Viko。
- 把共享词库、品牌锁、MCP、审计写进免费能力。
- 编造图上读不清的文字。

## 命令

```bash
python3 scripts/prism.py types
python3 scripts/prism.py fields poster
python3 scripts/prism.py decode --image path.jpg
python3 scripts/prism.py decode --fixture evals/hard-set/H7-cloud-water.json --as-json
python3 scripts/prism.py compile --fixture evals/fixtures/poster.json
python3 scripts/prism.py compile --fixture evals/fixtures/poster.json --as-json
python3 scripts/prism.py harvest --fixture evals/fixtures/poster.json --dry-run
python3 scripts/prism.py draw --vault vault/demo-cards.jsonl --axes style,color
python3 scripts/prism.py check
```
