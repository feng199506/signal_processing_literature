# 实战案例索引

下列案例把已下载代码/文档对到任务。本轮**未执行**任何命令；“建议命令”只供续跑隔离环境使用。不得把平滑、双向滤波或整段分解称为可在线。

通用限制：项目自带大型数据/权重已丢弃或未下载；缺子模块/LFS 见各 SNAPSHOT 与 [`project_readiness_cn.csv`](../project_readiness_cn.csv)。

## 1. 采样、混叠与抗混叠

- 资料：B-04 [`books/Downey_ThinkDSP_1.1.5_en.pdf`](../books/Downey_ThinkDSP_1.1.5_en.pdf)；[`projects/ThinkDSP_code_en/`](../projects/ThinkDSP_code_en/)（`thinkdsp/`，commit `f9efe78b9e58`）；Unser 2000；C-01/C-14。  
- 输入：教学波形或 notebook 中的小型数组；示例 wav 已丢弃。采样率见各 notebook，单位通常为无量纲或 Hz。  
- 预处理：无，或先低通再降采样。  
- 参数：原 `fs`、目标 `fs`、抗混叠截止。  
- 输出：时域与 DFT 幅值。  
- 指标：混叠分量是否进入基带。  
- 建议命令（未运行）：在隔离 venv 中阅读 [`projects/ThinkDSP_code_en/README.md`](../projects/ThinkDSP_code_en/README.md) 后按其中 notebook 入口执行。  
- 因果性：离线教学。  
- 限制：无硬件 ADC；时间抖动见 Schwarzmann 2025 论文，不在 ThinkDSP 里。

## 2. 滤波设计与频率响应

- 资料：S-01 butter/lfilter/filtfilt；[`projects/scipy_signal_subset_en/`](../projects/scipy_signal_subset_en/)；C-03/C-12；B-05。  
- 输入：`float64` 一维序列，需自备或用随机噪声；`fs` 自定。  
- 预处理：去均值（只用训练集统计）。  
- 参数：阶数、截止（归一化或 Hz）、SOS vs TF。  
- 输出：`sos`、`w,h`、滤波后序列。  
- 指标：通带纹波、阻带衰减、群延迟。  
- 建议：对照 SciPy 教程页 `tutorial/signal.html`（在 S-01 离线树）。  
- **因果**：`lfilter` 在线可用（有 `zi`）；`filtfilt` 仅离线。边界：短记录两端不要当稳态。

## 3. 频谱和时频分析

- 资料：S-01 `stft`/`welch`；librosa 0.11 文档与 [`projects/librosa_src_en/`](../projects/librosa_src_en/)；B-10；ssqueezepy。  
- 输入：单通道，已知 `fs`。  
- 预处理：可选去趋势。  
- 参数：`n_fft`、hop、窗、是否中心对齐、幅值归一化。  
- 输出：STFT 复谱或功率谱。  
- 指标：COLA 误差、泄漏。  
- 因果：默认中心窗非因果。在线须右对齐窗并接受延迟。

## 4. 去噪、检测及参数估计

- 资料：B-07、B-16；PyLops；03 组检测/CRLB 论文。  
- 输入：带噪序列；噪声方差若未知需估计。  
- 预处理：不要用含测试段的全局 z-score。  
- 输出：点估计、区间或检测标签。  
- 指标：MSE vs CRLB、虚警约束下的检测概率。  
- 因果：批估计默认离线；滑动窗口检测才可能在线，延迟 = 窗长 + 确认逻辑。

## 5. 在线自适应滤波

- 资料：[`projects/padasip_src_en/`](../projects/padasip_src_en/)；Zhao 2025 LMS 瞬态；Colburn 2022 Wiener。  
- 输入：期望信号 `d[n]` 与输入 `u[n]`，样本级。  
- 参数：滤波器长度、步长 μ、遗忘因子。  
- 输出：误差 `e[n]`、权重轨迹。  
- 指标：稳态 MSE、发散与否。  
- 因果：**样本级在线（因果）**。不要用整段相关矩阵的 Wiener 解冒充 LMS。

## 6. 多传感器状态估计

- 资料：B-08、B-09；[`projects/filterpy_src_en/`](../projects/filterpy_src_en/)；[`projects/StoneSoup_src_en/`](../projects/StoneSoup_src_en/)；KalmanNet 官方代码（无权重）。  
- 输入：带时间戳的测量；单位与状态量纲必须一致。  
- 预处理：时间对齐、异常值门控。  
- 输出：滤波均值/协方差。  
- 指标：NEES/NIS、位置 RMSE（需声明滤波还是平滑）。  
- 因果：`filter` 因果；`rts_smoother` 等**离线**。KalmanNet 训练离线，推理是否逐步见脚本，本轮未验证。

## 7. 工业振动或电流故障分析

- 资料：10 组论文；[`projects/PyEMD_src_en/`](../projects/PyEMD_src_en/)；ssqueezepy。  
- 输入：加速度或电流，kHz 量级，单位 m/s² 或 A。  
- 预处理：去趋势、抗混叠、可能的阶次重采样（需转速）。  
- 输出：谱、包络、IMF（若用 EMD）。  
- 指标：检测延迟、虚警；**不要**用整段准确率。  
- 因果：谱滑动窗可近在线；EMD 不可。Vieira 2025 专门讨论评估是否现实。

## 8. 音频增强或分离

- 资料：Asteroid、pyroomacoustics、09 组论文。  
- 输入：wav/float，16–48 kHz；示例音频多已丢弃，需自备小型文件。  
- 预处理：重采样到模型 `fs`。  
- 输出：估计源或增强单通道。  
- 指标：SDR 等为**离线**；实时看延迟与 RTF（未测）。  
- 因果：默认整句离线。低延迟见 Venkatesh 2024/2025。权重未下载，不能复现论文数值。

## 9. 生物信号分析

- 资料：C-09；WFDB 源码与文档；MNE 滤波教程；EEGNet 2016。  
- 输入：WFDB 记录头给出 `fs` 与单位（通常 mV）；本库不附带 PhysioNet 数据库。  
- 预处理：工频陷波、带通；必须选因果或零相位并写进记录。  
- 输出：滤波波形、QRS 位置等。  
- 指标：灵敏度/正预测（检测），不是离线分类准确率。  
- 因果：监护场景用因果滤波；科研离线可用 `filtfilt`，但要标明。

## 10. 离线算法转为流式处理

- 资料：S-12 GNU Radio Doxygen；SciPy `lfilter(..., zi=)`；12 组 STFT 域语音论文。  
- 步骤（概念，未实施）：切帧 → 保存 overlap 与滤波器状态 → 每块输出 hop 个新样本。  
- 限制：任何需要整段的算法（EMD、filtfilt、非因果平滑）没有流式对应，除非改造成因果近似。

## 11. CPU、GPU 或嵌入式性能比较

- 资料：FFTW 手册与源码；CMSIS-DSP；torchaudio 文档；Sommer DSP packing；Dai 定点量化。  
- 本轮**没有**基准数字。续跑应在隔离环境分别编译/安装后用同一输入长度比较延迟，记录编译器、频率、是否 SIMD。  
- 不得引用上游 README 的性能数字当作本机结果。
