# decode 烟雾（2026-08-16）

视觉模型：BeefAPI `gpt-5.5`。生图：`gpt-image-2` medium。  
反推 JSON 在 `evals/decodes/`（gitignore）。闭环图在 `evals/renders/*-decode.png`。

## 判型（对照手写种子）

8/8 类型一致。H8 第一轮曾误判 portrait，分类提示改过后再跑为 illustration。

| 图 | 手写 | decode | 字标/难点 |
|---|---|---|---|
| H1 | portrait | portrait | 搭肩在；交叉视线只写成「侧望」，没锁左右对视 |
| H2 | illustration | illustration | McD 制服和交汉堡在；两张脸区分弱 |
| H3 | portrait | portrait | 贴墙抬臂、对视、金属厢都写到了 |
| H4 | scene | scene | 春苑、雾、塔、点景在；载体写成画卷 |
| H5 | scene | scene | 秋雾宫苑在；载体写成宣纸工笔，会把假字题跋带回来 |
| H6 | poster | poster | `VIBESHOTCLUB`、口号、眼窗、樱桃都抄到 |
| H7 | product | product | `CLOUD WATER` 抄到；瓶即天空偏弱 |
| H8 | illustration | illustration | 红瞳十字高光、嘘手、校服在 |

## decode → render

| 图 | 看这张 | 闭环 | 对照手写成品 |
|---|---|---|---|
| H1 | `H1-duo-night-decode.png` | pass-with-note | 弱于手写 v2。两边都变成粉开衫，视线没交叉死 |
| H2 | `H2-brand-cows-decode.png` | pass-with-note | 和手写 v2 接近。横幅已补；多了 WANTED 海报 |
| H3 | `H3-elevator-pose-decode.png` | pass | 和手写 v1 接近 |
| H4 | `H4-spring-palace-decode.png` | pass-with-note | 弱于手写 v2，偏金夕阳仙侠 |
| H5 | `H5-mist-palace-decode.png` | pass-with-note | 弱于手写 v3。回到工笔手卷+假字 |
| H6 | `H6-type-poster-decode.png` | pass | 和手写 v1 一样能立住字报结构 |
| H7 | `H7-cloud-water-decode.png` | fail | 弱于手写 v2。标签对，瓶仍立在蓝天下 |
| H8 | `H8-cel-face-decode.png` | pass-with-note | 和手写 v2 一样，硬边赛璐璐偏厚涂 |

闭环可用 7/8。H7 的硬锁手写能补上，decode 第一次过还补不上。

过程里修了两处：生图遇 Cloudflare 524 会重试；`infer_size` 认「横向 / 宽幅」，否则 H2/H5 会被收成竖图。
