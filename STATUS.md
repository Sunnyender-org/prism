# STATUS

- 本线程只做 Prism 内核。网站归 BF Labs 另一线程。
- 阶段 1 夹具：20/20，`python3 scripts/prism.py check` PASS，`python3 -m unittest tests.test_prism` PASS
- 演示：`evals/demo-script.md` + `vault/demo-cards.jsonl`
- 难图：8/8 已齐，见 `evals/hard-set.md`
- 生图：BeefAPI `gpt-image-2` v1/v2/H5-v3 都在 `evals/renders/`。best-of 可用 8/8，pass 6。
- decode：8/8 hard-set 已反推，类型全对。闭环图在 `evals/renders/*-decode.png`，可用 7/8，H7 瓶即天空仍失败。见 `evals/decode-smoke.md`。
- 未做：SkillHub、企业席位
- 下次：decode 提示补媒介硬锁（瓶即天空、赛璐璐、绘画笔触）；不要把验收改成 Image 2 全过
