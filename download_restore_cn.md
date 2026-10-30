# 下载与恢复说明（信号处理资源库，2026-10-30）

## 发布内容

| 附件 | 说明 |
|---|---|
| `signal_processing_literature_20261030_batch001_cn_en.tar` | 资料库全文第 1 部分（1,517,289,472 字节，18,264 个文件） |
| `signal_processing_literature_20261030_batch002_cn_en.tar` | 资料库全文第 2 部分（208,666,624 字节，874 个文件） |
| `archive_index_cn.csv` | 包内每个文件的相对路径、所在 tar、大小和改动备注 |
| `windows_rename_map_cn.csv` | 为 Windows 改名的文件，以及为离线阅读改动或新增的文件明细 |
| `release_excluded_cn.csv` | 未随发布包提供的 6 种教材及官方获取地址 |
| `download_restore_cn.md` | 本说明 |
| `upload_report_cn.md` | 上传状态报告 |

两个 tar 都不压缩，合起来是一个完整目录：论文（12 个子方向的 `papers/`）、教材（`books/`，含 4 本 CCRMA 在线书的离线网页）、MIT OCW 课程包（`courses/`）、官方软件文档离线网页（`software_docs/`）、参考项目源码快照（`projects/`）、目录与登记 CSV、中文指南（`guides/`）和采集脚本（`scripts/`）。

## Windows 下恢复

1. 下载**两个** tar 包，放到同一个路径较短的目录，例如 `D:\sp\`。包内最长相对路径 157 个字符，解压目录本身建议不超过 80 个字符，以免超过资源管理器的 260 字符限制。
2. 在该目录解压两个包（任选一种），两个包的内容会合并到同一个目录树：
   - Windows 10/11 自带命令：在该目录打开命令提示符，依次运行
     `tar -xf signal_processing_literature_20261030_batch001_cn_en.tar` 和
     `tar -xf signal_processing_literature_20261030_batch002_cn_en.tar`
   - 7-Zip：分别右键 →“提取到当前位置”。
3. 用浏览器（Edge、Chrome、Firefox）打开解压目录下的 **`index_cn.html`**。它是离线首页：列出全部指南、登记文件和 148 条目录条目，每条都链接到本地文件。

不需要联网，也不需要安装任何软件。

## 离线阅读

- **首页与指南**：`index_cn.html`；`README_cn.md`、`search_log_cn.md` 和 `guides/*.md` 都另有同名 `.html` 版本，可在浏览器中直接打开，公式用包内 MathJax 渲染，文中的路径可点击跳转。`.md` 原文中的路径也已改为相对链接（VS Code、Typora 等可点击）。
- **CCRMA 在线书**（`books/Smith_*_html_en/`，Julius O. Smith III 的 4 本书：DFT 数学、数字滤波器导论、谱音频信号处理、物理音频信号处理）：
  - 从首页点进入口页即可阅读；书内页面、脚注页（`footnode.html`）和四本书之间的互相引用都已改为本地相对链接，可离线跳转。原镜像漏存的 34 个书内页面已补抓。
  - 插图（约 2,300 张）、样式表、图标和工具提示脚本已从原站下载到包内；公式用包内 MathJax 3 渲染。
  - 原站的“课程侧栏”需要联网服务，本地打开时不加载（不影响正文）。
- **软件文档网页**（`software_docs/*/`）：每个库只保存了与信号处理相关的几页（4–14 页）。页面所需的样式、脚本、图片和字体已下载到各目录下按域名分的子目录，页面可离线完整显示；已保存页面之间的链接是本地相对链接；指向**未保存页面**的链接改为原站在线网址（联网时点击可打开，离线时浏览器提示无法访问）。
- **只能联网使用的部分**（离线时不显示，不影响正文）：站内搜索、统计脚本、Read the Docs 版本菜单、Binder/Colab 按钮；少数原站自身已失效的图标（CMSIS-DSP 文档的搜索放大镜等，在线也不显示）。
- **目录链接**：首页和指南里指向项目目录（如 `projects/...`）或论文目录的链接，在浏览器中显示为文件列表，再点其中的文件即可。
- **PDF**：浏览器或任何 PDF 阅读器均可直接打开。
- **Jupyter 笔记本**（`books/Labbe_KalmanBayesianFiltersInPython_en/*.ipynb`）：用 VS Code（Jupyter 扩展）或 JupyterLab 打开；浏览器不能直接显示 `.ipynb`。

### MIT OCW 课程包

`courses/` 下的 10 个 MIT OCW 官方离线课程包（`.zip`）保持原样。zip 内没有顶层文件夹，请**各自解压到单独的空文件夹**（例如 `D:\ocw\6003\`），再打开其中的 `index.html` 离线浏览。RES.6-008 包内最长路径约 146 个字符，解压目录请尽量短。

## Windows 兼容改动

只改发布包，本地原资料库未改动。明细见 `windows_rename_map_cn.csv`。

- 19 个文件名改名：SciPy 文档镜像中含 `?` 的资源名（`xxx.css?v=…`）改为 `_`，引用它们的 11 个网页已同步改写。
- 没有仅大小写不同的文件名，没有符号链接；内层 zip 包中没有 Windows 不允许的文件名。

## 未随发布包提供的教材（6 种）

以下教材的 PDF 版权页或官网声明“仅供个人使用 / 未经许可不得复制或再分发”，因此不放进发布包：Boyd & Vandenberghe《Convex Optimization》、Gray & Davisson《An Introduction to Statistical Signal Processing》、Prandoni & Vetterli《Signal Processing for Communications》、Särkkä & Svensson《Bayesian Filtering and Smoothing》（第 2 版）、Särkkä & Solin《Applied Stochastic Differential Equations》、Smith《The Scientist and Engineer's Guide to Digital Signal Processing》（33 个章节 PDF）。它们都可以从作者或出版社官网免费下载，地址见 `release_excluded_cn.csv`，下载后放回 `books/` 目录即可。目录 `catalog_cn.csv` 中保留这些条目，离线首页中标为“未随发布包提供”。

## 校验

- `archive_index_cn.csv` 列出包内全部 19,138 个文件及字节数和所在 tar。
- 打包时校验过：tar 退出码为 0、包内列表与计划列表逐行一致；`tar -d` 与打包快照逐文件比对无差异。
- 打包内容是 2026-10-30（中欧时间）资料库的完整拷贝快照，之后资料库的改动不在本次发布中。

## 轻量 Git 分支

Release 对应的 Git 分支 `release-lite-20261030` 只含目录、登记 CSV、指南、脚本（不含缓存）、离线首页和以上说明文件（不含 PDF、网页镜像和源码快照），便于在 GitHub 网页上浏览。资料全文以 Release 附件为准。
