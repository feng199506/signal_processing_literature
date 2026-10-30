# 工业与生物医学应用路线

对应 [`10_industrial_biomedical/`](../10_industrial_biomedical/)，并交叉阵列/音频/估计。采集机制不同，不能共用同一套预处理。本轮不运行代码、不连接采集设备。

## 共同原则

- 写清通道、采样率、单位、传感器位置、同步方式。
- 先抗混叠与标定，再特征。
- 故障或事件检测是在线问题：双向滤波、EMD、未来窗的 STFT、整段分类准确率都不能直接当实时指标。
- 时间切分必须在任何统计标准化之前，避免把测试段信息泄漏进训练。

## A. 振动、电流、声发射、故障诊断

1. 背景：B-05 的频谱与滤波；时频用 B-02 / ssqueezepy / PyEMD（后者仅离线）。  
2. 近五年论文（均在 [`10_industrial_biomedical/papers/`](../10_industrial_biomedical/papers/)）：  
   - `2022_Aburakhia_HybridMethodConditionMonitoring_en.pdf` 状态监测。  
   - `2022_Liao_AttentionEmbeddedQuadraticNetwork_en.pdf` 二次网络。  
   - `2023_Lindley_ProbabilisticApproachAcousticEmission_en.pdf` 声发射，概率建模。  
   - `2025_Vieira_MoreRealisticEvaluationMachine_en.pdf` **评估泄漏**：离线切分与运行时检测不是同一任务。  
3. 代码：[`projects/PyEMD_src_en/`](../projects/PyEMD_src_en/)（离线分解）、[`projects/ssqueezepy_src_en/`](../projects/ssqueezepy_src_en/)、[`projects/scipy_signal_subset_en/scipy/signal/`](../projects/scipy_signal_subset_en/scipy/signal/)。  
4. 电流：注意电网频率、非整周期 DFT 泄漏、功率因数与采样时钟不同步（见 03 中同步论文 `2023_Roshandeh_MaximumLikelihoodTimeSynchronization_en.pdf`）。

## B. 音频增强、分离、声学事件（交叉 09、07）

- 论文：[`09_audio_speech/papers/`](../09_audio_speech/papers/) 中 Conv-TasNet、Demucs/Hybrid、PANNs、SkiM、低延迟去混响。  
- 项目：[`projects/asteroid_src_en/`](../projects/asteroid_src_en/)（commit `c15708a04d3d`，权重未下载）、[`projects/pyroomacoustics_src_en/`](../projects/pyroomacoustics_src_en/)（commit `ff7d61f219e4`）、[`projects/librosa_src_en/`](../projects/librosa_src_en/)。  
- 文档：[`software_docs/librosa_docs_html_en/`](../software_docs/librosa_docs_html_en/)、[`software_docs/torchaudio_docs_html_en/`](../software_docs/torchaudio_docs_html_en/)。  
- **指标**：离线 SDR/PESQ 不是实时 RTF 或端到端延迟。低延迟论文见 `2024_Venkatesh_RealTimeLowLatency_en.pdf`。

## C. 生物信号：ECG、EEG 等

- 课程：[`courses/MIT_OCW_HST_582J_BiomedicalSP_en.zip`](../courses/MIT_OCW_HST_582J_BiomedicalSP_en.zip)（C-09）。  
- 读写：[`projects/wfdb_python_src_en/`](../projects/wfdb_python_src_en/)（commit `b8914e1c9c77`，PhysioNet 大数据未下载）、[`software_docs/WFDB_python_docs_html_en/`](../software_docs/WFDB_python_docs_html_en/)。  
- 滤波相位：[`software_docs/MNE_filtering_docs_html_en/`](../software_docs/MNE_filtering_docs_html_en/)（明确 FIR 默认、零相位与因果差异）。这是本库关于生物信号 `filtfilt` 的主要工程依据。  
- 论文：`2016_Lawhern_EEGNet_en.pdf`（经典补充）、`2024_Han_CepstralAnalysisArtifactDetection_en.pdf`。  
- 采集差异：ECG 是准周期电活动，电极阻抗与工频干扰为主；EEG 幅度更小、伪迹类型不同。采样率、参考电极、硬件高通必须写进记录。  
- NeuroKit2 仓库快照因归档 362 MiB 超过上限未保存，不计入项目。

## D. 阵列、波束形成、多传感器（07）

- 综述：[`07_arrays_sensor_fusion/papers/2022_Pesavento_ThreeMoreDecadesArray_en.pdf`](../07_arrays_sensor_fusion/papers/2022_Pesavento_ThreeMoreDecadesArray_en.pdf)、`2025_Salama_DirectionArrivalEstimationTutorial_en.pdf`。  
- DOA/ESPRIT：`2022_Yang_NonasymptoticPerformanceAnalysisESPRIT_en.pdf`、`2025_Wang_LargeDimensionalAnalysisESPRIT_en.pdf`、`2025_Emenonye_ImpactModelMismatchDOA_en.pdf`。  
- 波束形成：`2023_Dietzen_ScalableComplexitySteeredResponse_en.pdf`、`2025_Herath_ScalableMVDRBeamformingAlgorithm_en.pdf`。  
- 融合估计：B-08、FilterPy、Stone Soup。平滑器仍不可当在线。  
- 标定与同步未单独成书；工程上先做时间戳对齐再做空间谱。

## E. 图与时空（08，环境监测站/传感器网）

- 经典：[`08_graph_spatiotemporal/papers/2012_Shuman_EmergingFieldSignalProcessing_en.pdf`](../08_graph_spatiotemporal/papers/2012_Shuman_EmergingFieldSignalProcessing_en.pdf)、`2017_Ortega_GraphSignalProcessing_en.pdf`。  
- 采样与重建：Hara 2022、Seifert 2022（有向图因果 Fourier）、Sripathmanathan 2023/2024、Sheng 2025。  
- 代码/文档：[`projects/PyGSP_src_en/`](../projects/PyGSP_src_en/)、[`software_docs/PyGSP_docs_html_en/`](../software_docs/PyGSP_docs_html_en/)。维护状态在种子中记为低活跃。  
- 站点网：图移位与传感器邻接是模型假设；掉站、不规则时间戳要先重采样或用不等间隔方法，不能直接套均匀图滤波。

## 任务对照（避免张冠李戴）

| 采集 | 典型采样率量级 | 常见任务 | 不能直接当在线的操作 |
|---|---|---|---|
| 振动加速度 | kHz–百 kHz | 谱、包络、阶次 | EMD、双向滤波、整段分类准确率 |
| 电机电流 | kHz | 边带、同步采样 | 未同步的 DFT 峰值 |
| 声发射 | 百 kHz–MHz | 瞬态检测 | 长窗中心 STFT |
| 语音/音频 | 16–48 kHz | 增强、分离、事件 | 离线 SDR 当实时指标 |
| ECG | 128–1000 Hz | QRS、节律 | 零相位滤波当监护实时 |
| EEG | 250–5000 Hz | 频带、事件 | 未来窗的伪迹剔除 |
| 阵列 | 与物理孔径有关 | DOA、波束 | 用整段协方差当因果快拍 |
| 监测站网络 | 分钟–小时 | 图滤波、插值 | 忽略时间戳的均匀图模型 |
