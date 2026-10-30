# 信号处理资源库

独立目录：`/root/signal_processing_literature/`。覆盖本科信号与系统到研究生专题、应用与工程部署。检索日 **2026-10-30**；论文五年窗口 **2021-10-30 至 2026-10-30**，必要经典单列。

本轮只收集整理：不安装依赖、不运行实验、不连接采集设备、不部署、不上传 GitHub、不删除资料。

## 子方向

| 目录 | 内容 |
|---|---|
| [`01_signals_systems/`](01_signals_systems/) | 连续/离散、LTI、卷积、变换、频率响应、采样重建 |
| [`02_digital_signal_processing/`](02_digital_signal_processing/) | DFT/FFT、FIR/IIR、多采样率、量化与定点 |
| [`03_statistical_signal_processing/`](03_statistical_signal_processing/) | 随机信号、谱估计、检测与估计 |
| [`04_time_frequency/`](04_time_frequency/) | STFT、小波、多分辨率、非平稳 |
| [`05_adaptive_filtering_estimation/`](05_adaptive_filtering_estimation/) | Wiener、LMS/RLS、Kalman 族、粒子滤波、平滑 |
| [`06_inverse_sparse_methods/`](06_inverse_sparse_methods/) | 逆问题、正则化、稀疏、压缩感知 |
| [`07_arrays_sensor_fusion/`](07_arrays_sensor_fusion/) | 阵列、波束、DOA、多传感器融合 |
| [`08_graph_spatiotemporal/`](08_graph_spatiotemporal/) | 图信号、图滤波/采样、时空 |
| [`09_audio_speech/`](09_audio_speech/) | 语音音频特征、增强、分离、事件 |
| [`10_industrial_biomedical/`](10_industrial_biomedical/) | 振动/电流/声发射与 ECG/EEG 等 |
| [`11_learning_based/`](11_learning_based/) | 可学习滤波、展开、物理+数据 |
| [`12_realtime_implementation/`](12_realtime_implementation/) | 流式、延迟、精度、嵌入式/GPU |

论文在各目录 `papers/`。教材、课程、软件文档、项目分别在 [`books/`](books/)、[`courses/`](courses/)、[`software_docs/`](software_docs/)、[`projects/`](projects/)。

## 登记文件

- [`catalog_cn.csv`](catalog_cn.csv) 已核验条目
- [`progress_cn.csv`](progress_cn.csv) 分方向进度
- [`download_failures_cn.csv`](download_failures_cn.csv) 失败与待核验
- [`project_readiness_cn.csv`](project_readiness_cn.csv) 代码 L0/L1（本轮不执行）
- [`search_log_cn.md`](search_log_cn.md) 检索与复用说明
- [`guides/`](guides/) 学习与工程路线（中文）

独立自建文件在扩展名前标 `_cn` 或 `_en`。上游源码内部文件名保持原样。

## 学习路线

- [`guides/foundations_path_cn.md`](guides/foundations_path_cn.md)
- [`guides/statistical_signal_processing_path_cn.md`](guides/statistical_signal_processing_path_cn.md)
- [`guides/time_frequency_path_cn.md`](guides/time_frequency_path_cn.md)
- [`guides/industrial_applications_path_cn.md`](guides/industrial_applications_path_cn.md)
- [`guides/software_map_cn.md`](guides/software_map_cn.md)
- [`guides/realtime_deployment_cn.md`](guides/realtime_deployment_cn.md)
- [`guides/practice_index_cn.md`](guides/practice_index_cn.md)
- [`guides/core_reading_list_cn.md`](guides/core_reading_list_cn.md)

## 完整性规则（摘要）

只计核验通过的完整资料。PDF 须可解析且正文完整。摘要/试读/残章不计。课程按完整资料包计。HTML 保存为离线页并记录范围。源码保留结构、许可证、SNAPSHOT（含 commit）。不下载大数据集、模型权重、安装包。不绕过付费墙。

## 断点续跑

```bash
cd /root/signal_processing_literature
python3 -I scripts/materials_en.py status
python3 -I scripts/papers_en.py status
python3 -I scripts/materials_en.py fetch books --retry-failed
python3 -I scripts/materials_en.py fetch courses --retry-failed
python3 -I scripts/materials_en.py fetch software --retry-failed
python3 -I scripts/materials_en.py fetch projects --retry-failed
python3 -I scripts/papers_en.py download NN --retry-failed   # NN = 01..12
python3 -I scripts/build_catalog_en.py
```

已核验条目不会覆盖。工作缓存：`/root/.cache/spl_lit/`。arXiv 与兄弟文献库共享 `arxiv.org` 锁。

## 代码等级

- **L0**：已下载快照。
- **L1**：静态见到 README/依赖清单/SNAPSHOT 等入口。
- 本轮不运行，不声称复现或实时性能。
