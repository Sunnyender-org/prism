# Prism / 棱镜

把参考图拆成可复用的视觉合同，再编译成 GPT Image 吃的自然语言。  
给 Codex、Grok、WorkBuddy 用的 **skill**（不是浏览器插件）。组织共享和审计走 BF Labs 企业版。

License: [Apache-2.0](LICENSE)

## 本地

```bash
python3 scripts/prism.py check
python3 scripts/prism.py compile --fixture evals/fixtures/poster.json
python3 scripts/prism.py decode --image path.jpg
python3 scripts/prism.py demo-vault
python3 scripts/prism.py draw --vault vault/demo-cards.jsonl --axes style,color --seed 1
python3 -m unittest tests.test_prism
```

## 文档

- 计划：`docs/prism-v0-plan.md`
- 验收：`docs/prism-acceptance.md`
- 免费 / 企业：`docs/tiers.md`
- Agent 合同：`skill/SKILL.md`

反推需要仓库根目录 `.env`（BeefAPI）。没有密钥时只编译 JSON。

## 现在没有

SkillHub 上架、WorkBuddy 企业席位实测、Chrome 插件、云端工作室。难图原图只作本机评测，不进本仓库。

## 许可

Copyright 2026 Sunnyender  
Licensed under the Apache License, Version 2.0.
