# 实时实现与部署路线

对应 [`12_realtime_implementation/`](../12_realtime_implementation/)。本轮只收集，不宣称已运行、已复现或达到实时性能。代码等级见 [`project_readiness_cn.csv`](../project_readiness_cn.csv)（L0 已下载，L1 为入口/依赖/配置的静态核对）。

## 从离线算法到流式

1. **块、缓冲、分帧**  
   离线脚本一次吃完整段 `x[0:N]`。流式必须固定 `frame_length`、`hop`、输入队列和输出队列。  
   依据：GNU Radio Doxygen `page_usage` / `group__filter__blk`（[`software_docs/GNU_Radio_docs_html_en/`](../software_docs/GNU_Radio_docs_html_en/)）；SciPy `lfilter` 的 `zi` 状态。  
   项目：[`projects/scipy_signal_subset_en/scipy/signal/_signaltools.py`](../projects/scipy_signal_subset_en/scipy/signal/_signaltools.py)（静态阅读，不执行）。

2. **延迟预算**  
   总延迟 ≥ 缓冲等待 + 算法前瞻 + 计算时间 + I/O。  
   中心窗 STFT 的算法前瞻 ≈ 窗长/2，这不是计算慢，是非因果。  
   论文：[`09_audio_speech/papers/2024_Venkatesh_RealTimeLowLatency_en.pdf`](../09_audio_speech/papers/2024_Venkatesh_RealTimeLowLatency_en.pdf)、[`12_realtime_implementation/papers/2022_Wang_STFTDomainNeuralSpeech_en.pdf`](../12_realtime_implementation/papers/2022_Wang_STFTDomainNeuralSpeech_en.pdf)。

3. **因果滤波 vs 离线零相位**  
   实时路径只用 `lfilter` / SOS 前向，或 FIR 线性相位但接受群延迟。  
   `filtfilt`、平滑器、EMD、未来帧 ISTFT 禁止标成可部署在线。MNE 滤波教程把这一点写得很清楚。

4. **数值精度与定点**  
   论文：`2024_Dai_TrainableFixedPointQuantization_en.pdf`、`2022_Sommer_DSPPacking_en.pdf`、`2023_Hu_ResourceEfficientFIRFilter_en.pdf`。  
   实现：[`projects/CMSIS_DSP_src_en/`](../projects/CMSIS_DSP_src_en/)（Q7/Q15/Q31，溢出饱和）、[`projects/FFTW_src_en/`](../projects/FFTW_src_en/)（浮点规划）。  
   级联 SOS、递归滤波的并行化：`2026_Zhai_ParallelCascadedRecursiveFiltering_en.pdf`。

5. **GPU / 可微流水**  
   [`software_docs/torchaudio_docs_html_en/`](../software_docs/torchaudio_docs_html_en/)；论文 `2025_Spanio_TorchFX_en.pdf`、`2026_Spanio_Fluxion_en.pdf`、`2025_Brady_PyDPF_en.pdf`。  
   本轮未测 RTF，也没有下载权重。

6. **调度**  
   实时线程不要做内存分配与阻塞 IO。GNU Radio 是流图调度的参考，不是本机已部署系统。

## 检查清单（部署前静态）

- 输入：交织/非交织、采样率、位深、单位、时间戳来源。
- 状态：滤波器 `zi`、STFT overlap 缓冲、检测器的确认窗。
- 溢出：定点最大幅度、中间累加位宽。
- 指标：延迟（毫秒）、是否丢帧、与离线参考的误差；**不要**用离线分类准确率代替。
- 硬件：本库 CMSIS 针对 Cortex-M/A，FFTW 针对 CPU；均未上板、未编译。

## 建议阅读顺序

C-10 [`courses/MIT_OCW_2_161_SignalProcessing_F2008_en.zip`](../courses/MIT_OCW_2_161_SignalProcessing_F2008_en.zip)（连续/离散与采集）→ B-05 实现章节 → SciPy `lfilter` 与 MNE 滤波教程 → CMSIS-DSP / FFTW 文档 → 12 组近五年论文。
