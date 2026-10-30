# 入门与基础路线

本路线对应 [`01_signals_systems/`](../01_signals_systems/) 与 [`02_digital_signal_processing/`](../02_digital_signal_processing/)，并接到采样、滤波与 DFT 的工程注意点。只使用本库已核验资料。本轮不运行代码。

## 先修

微积分、线性代数、复数。有 Python 读写数组更好，但不是硬门槛。

## 建议顺序

1. **连续/离散信号与 LTI**  
   教材：[`books/VetterliKovacevicGoyal_FoundationsSignalProcessing_2014_en.pdf`](../books/VetterliKovacevicGoyal_FoundationsSignalProcessing_2014_en.pdf)（B-01，Hilbert 空间统一视角）。  
   更短的本科入口：`books/PrandoniVetterli_SignalProcessingForCommunications_2008_en.pdf`（B-03）。  
   课程：[`courses/MIT_OCW_6_003_SignalsSystems_F2011_en.zip`](../courses/MIT_OCW_6_003_SignalsSystems_F2011_en.zip)（C-01）与 [`courses/MIT_OCW_RES_6_007_Oppenheim_SignalsSystems_en.zip`](../courses/MIT_OCW_RES_6_007_Oppenheim_SignalsSystems_en.zip)（C-02）。

2. **Fourier 从级数到变换**  
   [`books/Osgood_FourierTransformApplications_EE261_en.pdf`](../books/Osgood_FourierTransformApplications_EE261_en.pdf)（B-06，Stanford EE261 完整讲义卷）。  
   论文对照：[`01_signals_systems/papers/2023_Ji_FacesConvolutionFourierTheory_en.pdf`](../01_signals_systems/papers/2023_Ji_FacesConvolutionFourierTheory_en.pdf)。

3. **采样、混叠与重建**  
   经典：[`01_signals_systems/papers/2000_Unser_Sampling50YearsAfter_en.pdf`](../01_signals_systems/papers/2000_Unser_Sampling50YearsAfter_en.pdf)（Shannon 之后五十年，五年前经典补充）。  
   近五年：`2023_Zeng_GeneralizedNyquistShannonSampling_en.pdf`、`2025_Schwarzmann_EffectSamplingTimeJitter_en.pdf`、`2025_Shtendel_UnlimitedSamplingMultibandSignals_en.pdf`。  
   课程里的量化与波形：[`courses/MIT_OCW_6_450_DigitalCommunications_I_F2006_en.zip`](../courses/MIT_OCW_6_450_DigitalCommunications_I_F2006_en.zip)（C-14）。  
   代码入口：[`projects/ThinkDSP_code_en/`](../projects/ThinkDSP_code_en/)（commit `f9efe78b9e58`）。文档：[`software_docs/SciPy_1.16_signal_fft_docs_html_en/`](../software_docs/SciPy_1.16_signal_fft_docs_html_en/) 中 `scipy.signal.resample`。

4. **DFT/FFT、窗与频谱泄漏**  
   分章教材：`books/Smith_ScientistEngineersGuideDSP_1999_en/`（B-05，CH1–CH33）。  
   HTML 全书：[`books/Smith_MathematicsDFT_2e_html_en/`](../books/Smith_MathematicsDFT_2e_html_en/)（B-10，Julius O. Smith）。  
   实现对照：[`projects/scipy_signal_subset_en/scipy/fft/`](../projects/scipy_signal_subset_en/scipy/fft/) 与 [`software_docs/NumPy_fft_docs_html_en/`](../software_docs/NumPy_fft_docs_html_en/)。  
   近五年数值：[`02_digital_signal_processing/papers/2024_Pochimireddy_NumericalStabilityDFTComputation_en.pdf`](../02_digital_signal_processing/papers/2024_Pochimireddy_NumericalStabilityDFTComputation_en.pdf)。

5. **FIR/IIR、频率响应、相位与群延迟**  
   课程：[`courses/MIT_OCW_6_341_DiscreteTimeSP_F2005_en.zip`](../courses/MIT_OCW_6_341_DiscreteTimeSP_F2005_en.zip)（C-03）、[`courses/MIT_OCW_RES_6_008_DigitalSignalProcessing_en.zip`](../courses/MIT_OCW_RES_6_008_DigitalSignalProcessing_en.zip)（C-12）。  
   HTML：[`books/Smith_IntroductionDigitalFilters_html_en/`](../books/Smith_IntroductionDigitalFilters_html_en/)（B-11）。  
   文档：[`software_docs/SciPy_1.16_signal_fft_docs_html_en/`](../software_docs/SciPy_1.16_signal_fft_docs_html_en/) 的 `butter` / `lfilter` / `filtfilt`。  
   **硬区分**：`lfilter` 是因果；`filtfilt` 是双向离线零相位，不能叫在线滤波。

6. **多采样率、插值、抽取**  
   论文：[`02_digital_signal_processing/papers/2024_Carson_InterpolationFilterDesignSample_en.pdf`](../02_digital_signal_processing/papers/2024_Carson_InterpolationFilterDesignSample_en.pdf)、`2025_Carson_ResamplingFilterDesignMultirate_en.pdf`。  
   课程：[`courses/MIT_OCW_18_327_WaveletsFilterBanks_S2003_en.zip`](../courses/MIT_OCW_18_327_WaveletsFilterBanks_S2003_en.zip)（C-13，多相与完全重建）。

7. **量化、定点与实现结构**  
   B-05 后半与 C-12 讲义中的参数量化。  
   近五年：`2023_Hu_ResourceEfficientFIRFilter_en.pdf`、`2026_Portella_MultiplierlessDFTApproximationPrime_en.pdf`。  
   嵌入式对照：[`projects/CMSIS_DSP_src_en/`](../projects/CMSIS_DSP_src_en/)。

## 必做概念检查（读资料时勾选）

- 混叠：抗混叠滤波器在采样器之前；数字重采样仍要抗混叠。
- 时间戳：不均匀采样与抖动不是“加一点噪声”那么简单，见 Schwarzmann 2025。
- 窗、泄漏、幅值归一化：DFT 幅值是否除以窗能量/窗和，B-10 与 SciPy 文档必须对照。
- 边界效应：FIR 的 transient、IIR 的初始状态、短记录两端不可当稳态。
- 因果 vs 离线：任何 `filtfilt`、平滑、非因果分解都不能直接当作实时检测。

## 下一跳

统计估计与检测 → [`guides/statistical_signal_processing_path_cn.md`](statistical_signal_processing_path_cn.md)。  
时频与小波 → [`guides/time_frequency_path_cn.md`](time_frequency_path_cn.md)。  
软件入口 → [`guides/software_map_cn.md`](software_map_cn.md)。
