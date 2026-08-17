# 60 秒拆海报演示（本机，不涉及企业版）

输入：`evals/fixtures/poster.json`（标本册 3D 头海报 seed）

1. `python3 scripts/prism.py fields poster` — 说明海报用哪些字段。
2. `python3 scripts/prism.py compile --fixture evals/fixtures/poster.json` — 读出散文，停在「避免写成写实肖像」。
3. `python3 scripts/prism.py harvest --fixture evals/fixtures/poster.json --dry-run` — 指出风格/构图/色彩被切成词卡。
4. `python3 scripts/prism.py draw --vault vault/demo-cards.jsonl --axes style,color --seed 1` — 从库里抽两张。

必须同时说：这是本地 fixture，不是 SkillHub 已上架，也不是企业共享库。
若编译读起来不能直接丢给 GPT Image，记入 `evals/hard-set.md`，不要在视频里改口。
