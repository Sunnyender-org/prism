# 难图人审

8/8 已齐。前 5 张来自用户粘贴；后 3 张来自公开帖，只作内部评测。源图不进公开仓库，本目录只入库 JSON 种子。

| id | type | 图 | 来源 | 难度 | 人判 | 笔记 |
|---|---|---|---|---|---|---|
| H1 | portrait | `H1-duo-night.png` | 用户 | 双人交叉视线 | pass | |
| H2 | illustration | `H2-brand-cows.png` | 用户 | 双物种品牌 3D | pass-with-note | 对外勿用商标 |
| H3 | portrait | `H3-elevator-pose.png` | 用户 | 贴墙抬臂对视 | pass | |
| H4 | scene | `H4-spring-palace.png` | 用户 | 宽幅春苑点景 | pass | 逼出 `scene` 类型 |
| H5 | scene | `H5-mist-palace.png` | 用户 | 秋雾红廊，易抄成 H4 | pass | |
| H6 | poster | `H6-type-poster.jpg` | [古一 2080146746211262761](https://x.com/MANISH1027512/status/2080146746211262761) | 多层字 + 唯二彩色眼窗 | pass | |
| H7 | product | `H7-cloud-water.jpg` | [古一 2086741506296369545](https://x.com/MANISH1027512/status/2086741506296369545) 原图裁切 | 瓶即天空，标签必须可读 | pass | 从 Viko 对比屏裁的左栏原图 |
| H8 | illustration | `H8-cel-face.jpg` | [古一 2086439731823530268](https://x.com/MANISH1027512/status/2086439731823530268) 来源图裁切 | 细长红瞳，极易漂成萌脸 | pass | 正是他们自己说要单独锁脸的那类 |

人判只覆盖「编译稿能否直接丢给 GPT Image」。下面是真实生图。

## gpt-image-2 实生（2026-08-16）

- 路由：BeefAPI `https://beefapi.com/v1`，`model=gpt-image-2`，`quality=medium`，`n=1`
- 命令：`python3 scripts/prism.py doctor` 后逐条 `render --fixture evals/hard-set/H*.json`
- 产物：`evals/renders/`（已 gitignore，不入库）
- 密钥：仓库根 `.env`（`chmod 600`，gitignore）。聊天和 git 里都没有 key。
- 计分 v1：`pass` 3 / `pass-with-note` 4 / `fail` 1。可用 7/8。
- 计分 v2（打磨后，取每张更好的一版）：`pass` 5 / `pass-with-note` 3 / `fail` 0。可用 8/8。
- 计分 best-of（含 H5 v3）：`pass` 6 / `pass-with-note` 2 / `fail` 0。可用 8/8。验收仍不记全过。
- v2 只重跑了 H1/H2/H4/H5/H7/H8。H3、H6 沿用 v1。H5 另有 v3。旧文件未覆盖。

| id | size | v1 | v2 | 看哪张 | 笔记 |
|---|---|---|---|---|---|
| H1 | 1024x1536 | pass-with-note | pass | `H1-duo-night-v2.png` | v1 两人都看镜头。v2 交叉视线咬住了，粉包和短袖 T 也回来了。脸仍不是原图那两个人。 |
| H2 | 1536x1024 | pass-with-note | pass-with-note | `H2-brand-cows-v2.png` | 左眼更三角无奈，右眼仍偏萌。媒介还是电影毛绒，不是原图那种阴郁黏土。对外勿用商标。 |
| H3 | 1024x1536 | pass | — | `H3-elevator-pose.png` | 未重跑。姿态和电梯光已经够用。 |
| H4 | 1536x1024 | pass-with-note | pass | `H4-spring-palace-v2.png` | v1 是工笔手卷+假字。v2 有体积雾，题跋收成小印，更接近数字绘画。构图仍不是原图那套院落层次。 |
| H5 | 1536x1024 | pass | pass-with-note | `H5-mist-palace-v3.png` | v1 太手卷，v2 太实拍。v3 回到湿边数字绘画：红亭、敞廊、蓝袍背影、垂柳秋叶都在，没塌成 H4。构图仍比原图更「园中一角」，少原图左侧重檐和人流。 |
| H6 | 1024x1536 | pass | — | `H6-type-poster.png` | 未重跑。字报结构已经立住。 |
| H7 | 1024x1536 | fail | pass | `H7-cloud-water-v2.png` | v1 发明中文品牌，瓶是立在蓝天下。v2 瓶内云与背景云连续，标签是 `CLOUD WATER`。标签从融入式浅标变成一条白腰带，仍可接受。 |
| H8 | 1024x1536 | pass-with-note | pass-with-note | `H8-cel-face-v2.png` | 嘘手改到正向字段后姿态仍在。硬边赛璐璐还是偏厚涂，脸更中性。 |

v2 改了什么：

- 编译在负向前复述一句「必须守住」：风格、主体/脸、视线或姿态、海报文字。
- H7 删掉自相矛盾的「瓶内是水+气泡」，锁死 `CLOUD WATER` 和瓶内即天空。
- H1 把交叉视线写成硬锁，并禁止同时看镜头。
- H4/H5 把「工笔/浅绛手卷」从载体里拿掉。
- H8 把嘘手写进 `pose_expression`。

还没打磨完：

1. 没有参考图输入时，人脸身份锁不住（H1、H3）。
2. 赛璐璐硬边和黏土阴郁度，散文压不过 Image 2 默认甜感（H2、H8）。
3. 「数字绘画电影静帧」会矫枉过正成实景；H5 v3 改成「可见湿边和笔触」后回来了。同类词以后不要写「电影静帧」。
