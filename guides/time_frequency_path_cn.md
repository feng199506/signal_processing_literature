# 时频与小波路线

对应 [`04_time_frequency/`](../04_time_frequency/)，并交叉 `02` 的分帧/窗与 `09` 的音频 STFT。重点记录每种分解的假设和限制。本轮不运行代码。

## 先修

DFT、窗函数、线性滤波。B-01 后半与 B-02。

## 读法

1. **STFT 与分帧**  
   教材：Julius Smith《Spectral Audio Signal Processing》[`books/Smith_SpectralAudioSignalProcessing_html_en/`](../books/Smith_SpectralAudioSignalProcessing_html_en/)（B-12）。  
   文档：SciPy `stft` 页、[`software_docs/librosa_docs_html_en/`](../software_docs/librosa_docs_html_en/)（0.11.0：`core.html`、`librosa.stft` / `istft`）。  
   源码：[`projects/librosa_src_en/`](../projects/librosa_src_en/)（commit `4ffed287f904`）。  
   近五年：[`04_time_frequency/papers/2022_Pascal_CovariantDiscreteTimeFrequency_en.pdf`](../04_time_frequency/papers/2022_Pascal_CovariantDiscreteTimeFrequency_en.pdf)、`2023_Leiber_DifferentiableAdaptiveShortTime_en.pdf`。  
   限制：窗长决定时间/频率折中；中心窗 STFT 默认非因果；hop 与 COLA 不满足则 ISTFT 不能完美重建。

2. **小波、多分辨率、滤波器组**  
   教材：[`books/VetterliKovacevicGoyal_FourierWaveletSignalProcessing_2013_en.pdf`](../books/VetterliKovacevicGoyal_FourierWaveletSignalProcessing_2013_en.pdf)（B-02）。  
   课程：[`courses/MIT_OCW_18_327_WaveletsFilterBanks_S2003_en.zip`](../courses/MIT_OCW_18_327_WaveletsFilterBanks_S2003_en.zip)（C-13）。  
   文档/源码：[`software_docs/PyWavelets_docs_html_en/`](../software_docs/PyWavelets_docs_html_en/)、[`projects/PyWavelets_src_en/`](../projects/PyWavelets_src_en/)（commit `c9b542b2d2c3`）。  
   限制：离散小波通常假设有限长度信号加边界延拓；延拓方式改变端点系数。实时间小波可用因果滤波器组，但与离线对称延拓的系数不同。

3. **同步压缩与瞬态**  
   经典：[`04_time_frequency/papers/2009_Daubechies_SynchrosqueezedWaveletTransforms_en.pdf`](../04_time_frequency/papers/2009_Daubechies_SynchrosqueezedWaveletTransforms_en.pdf)。  
   实现：[`projects/ssqueezepy_src_en/`](../projects/ssqueezepy_src_en/)（commit `adf76ac19303`）。  
   限制：同步压缩假设分量在时频面上可分离；交叉与强噪声下再分配会伪影。整段 CWT 是离线的。

4. **散射与稳定时频表示**  
   经典：`2011_Mallat_GroupInvariantScattering_en.pdf`、`2013_Anden_DeepScatteringSpectrum_en.pdf`。  
   限制：散射对小形变稳定，但丢失一部分可逆相位；不宜当作通用去噪器。

5. **经验模态等自适应分解**  
   实现：[`projects/PyEMD_src_en/`](../projects/PyEMD_src_en/)（commit `e8ea44f6d577`）。  
   **硬限制**：EMD/EEMD 是离线、非因果分解，依赖整段包络插值。工业振动里常见，但不得把 IMF 当作在线故障检测输出。见 Vieira 2025 对评估泄漏的讨论（[`10_industrial_biomedical/papers/`](../10_industrial_biomedical/papers/)）。

6. **计算**  
   [`04_time_frequency/papers/2026_Franchino_ExactFactorisationFastComputation_en.pdf`](../04_time_frequency/papers/2026_Franchino_ExactFactorisationFastComputation_en.pdf)。实时分帧见 [`guides/realtime_deployment_cn.md`](realtime_deployment_cn.md)。

## 分帧清单（写进案例记录）

- 采样率、窗长、hop、窗型、是否中心对齐。
- 频谱泄漏与幅值归一化（窗和 / 窗能量 / PSD 标定）。
- 边界帧：是否填充、填充是否用到未来样本。
- COLA 与 ISTFT 误差。
- 若任务是在线检测：只能使用已到达样本的因果窗；延迟 ≥ 窗长的一半（中心窗）或整窗（右对齐因果窗）。
