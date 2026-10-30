# 检索日志

检索日：2026-10-30。五年窗口：2021-10-30 至 2026-10-30。经典论文单列。

## 已有资料库核查

| 资料库 | 路径 | 结果 |
|---|---|---|
| 高斯过程文献库 | `/root/gaussian_process_literature` | 目录与脚本在，但 [`books/`](books/) 原件不在本机。Särkkä 两本改从作者站点新下载并核验，**不计已有复用**。 |
| 近期顶会研究 | `/root/recent_top_conference_research` | 存在。论文若命中则按核验复制，不移动原件。本轮论文以 arXiv 新下载为主。 |
| 时间序列 / 概率统计 / 控制 / 机器人 / 编程课程库 | `/root/time_series_literature` 等 | 本机无对应文献库目录；仅有 `/root/.cache/*_lit` 缓存，不把缓存当已核验复用。 |

规则：不移动原件、不重复计数；复用项须在本库重新核验。本轮教材/课程/软件/项目均记为新下载。

## 检索渠道

- 论文：arXiv API（`eess.SP` / `eess.AS` 及相关标题），五年窗口；经典从 arXiv 旧文或作者页。
- 教材：作者站点免费全书、CC/CUP 作者个人使用 PDF、CCRMA HTML 全书、GitHub 代码书。
- 课程：MIT OCW 官方 zip 课件包（含讲义 PDF，不含视频）。
- 软件：官方 HTML 子集。SciPy 早期条目含页面资源；其后条目保存页面本体。
- 项目：GitHub 指定 commit 的 zip 快照；丢弃权重、大型二进制与部分音频。

不绕过付费墙；不下载商业软件本体、破解工具或付费手册。

## 子方向论文

按 [`scripts/seeds/queries/`](scripts/seeds/queries/) 检索，种子在 [`scripts/seeds/papers/`](scripts/seeds/papers/)。核验：`%PDF-`、pypdf、页数/字数、题名与第一作者姓、参考文献节（含分散字母的 REFERENCES）。

失败摘录（详见 [`download_failures_cn.csv`](download_failures_cn.csv)）：

- 02：短文/404/页数不足（如 2407.06502、2505.23718、2210.15635）。
- 05：Kalman 1960 历史 PDF 链接 404。
- 11：一篇与 06 重复，未双计。

## 教材与课程

- HTML 全书用目录镜像（wget -r -np -l 1），音频安装包排除。
- MIT OCW 现行为课程 zip，而非旧版 `static_resources/` 散列 PDF。
- C-05 Stanford SEE、C-06 sp4comm 站点不计入大学课程名额（`exclude`）。
- 新增 C-13 MIT 18.327、C-14 MIT 6.450，使课程核验达到 10 套。

## 软件与项目

- librosa 文档改用 0.11.0 路径（`latest/core.html` 404）。
- GNU Radio wiki 对本 UA 403，改官方 Doxygen。
- MATLAB 公开文档 403/404，S-13 失败，不计入。
- NeuroKit2 归档 362 MiB 超限，P-12 失败；生物信号以 WFDB + MNE 文档为准。
- SciPy 全库过大，P-19 仅保留 `scipy/signal` 与 `scipy/fft`。

## 断点续跑

见 [`README_cn.md`](README_cn.md)。状态：[`scripts/state/papers/`](scripts/state/papers/)、[`scripts/state/materials/`](scripts/state/materials/)。缓存：`/root/.cache/spl_lit/`。
