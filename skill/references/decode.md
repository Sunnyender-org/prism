# 反推

`prism decode` 把参考图收成类型化 seed，再走同一套 compile。没有视觉模型或没有 `.env` 时，只编译已有 JSON，不假装看过原图。

```bash
python3 scripts/prism.py decode --image path.jpg
python3 scripts/prism.py decode --fixture evals/hard-set/H7-cloud-water.json --as-json
python3 scripts/prism.py decode --image path.jpg --type product --out /tmp/seed.json
```

默认打印编译后的散文。`--as-json` 才输出字段。

规则：

- 先判类型，再只填该类型字段。
- 看不清的字写成「不可辨小字」，不编品牌。
- 脸锁和风格锁分开。
- 媒介写绘画 / 摄影 / 三维 / 赛璐璐，不要写「电影静帧」。
- `image_type` 写明竖版或横版，以及 9:16 / 2:3 / 4:3 / 16:9。
- 不确定就 `generic`，在 notes 说明。
- 没有参考图输入时，decode 锁不住具体那张脸。
