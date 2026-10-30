# 统计信号处理路线

对应 [`03_statistical_signal_processing/`](../03_statistical_signal_processing/) 与 [`05_adaptive_filtering_estimation/`](../05_adaptive_filtering_estimation/)。强调相关、功率谱、检测估计、滤波与平滑的因果性。本轮不运行代码。

## 先修

[`guides/foundations_path_cn.md`](foundations_path_cn.md) 中的 LTI、DFT 与采样。本科概率（期望、协方差、条件分布）。

## 理论主线

1. **随机信号与二阶矩**  
   教材：`books/GrayDavisson_IntroductionStatisticalSignalProcessing_2011_en.pdf`（B-07）。  
   卷积与功率谱的代数：[`books/Gray_ToeplitzCirculantMatrices_en.pdf`](../books/Gray_ToeplitzCirculantMatrices_en.pdf)（B-16）。  
   课程：[`courses/MIT_OCW_6_011_SignalsSystemsInference_S2018_en.zip`](../courses/MIT_OCW_6_011_SignalsSystemsInference_S2018_en.zip)（C-04，信号、系统与推断）。

2. **功率谱估计**  
   文档：[`software_docs/SciPy_1.16_signal_fft_docs_html_en/`](../software_docs/SciPy_1.16_signal_fft_docs_html_en/) 中 Welch。  
   近五年：[`03_statistical_signal_processing/papers/2022_Hong_EstimationEvolutionaryPowerSpectral_en.pdf`](../03_statistical_signal_processing/papers/2022_Hong_EstimationEvolutionaryPowerSpectral_en.pdf)、`2026_Magsino_CrossCorrelationPeriodogramsDecaying_en.pdf`。  
   进化谱、短时方法都假设局部平稳；违反时改走时频路线。

3. **检测与估计、假设检验**  
   近五年：`2022_Luong_FamilyNeymanPearsonDetectors_en.pdf`、`2023_Wang_CramerRaoLowerBound_en.pdf`、`2023_Lamperski_NonAsymptoticPointwiseWorst_en.pdf`。  
   课程中的检测与信号空间：[`courses/MIT_OCW_6_450_DigitalCommunications_I_F2006_en.zip`](../courses/MIT_OCW_6_450_DigitalCommunications_I_F2006_en.zip)。  
   记录量：虚警/漏检随阈值与样本数变化，不要只用一次准确率。

4. **Wiener / LMS / RLS**  
   近五年：[`05_adaptive_filtering_estimation/papers/2022_Colburn_FunctionalWienerFilter_en.pdf`](../05_adaptive_filtering_estimation/papers/2022_Colburn_FunctionalWienerFilter_en.pdf)、`2025_Zhao_TransientErrorAnalysisLMS_en.pdf`。  
   在线实现：[`projects/padasip_src_en/`](../projects/padasip_src_en/)（commit `4c13692b8f7c`，样本级更新，因果）。

5. **Kalman、EKF/UKF、粒子滤波与平滑**  
   教材：`books/Sarkka_BayesianFilteringSmoothing_2e_en.pdf`（B-08，作者站点个人使用 PDF）。  
   连续—离散：`books/SarkkaSolin_AppliedSDEs_2019_en.pdf`（B-09）。  
   代码书：[`books/Labbe_KalmanBayesianFiltersInPython_en/`](../books/Labbe_KalmanBayesianFiltersInPython_en/)（B-15）与 [`projects/filterpy_src_en/`](../projects/filterpy_src_en/)（commit `5df4e095fac0`）。  
   多传感器跟踪框架：[`projects/StoneSoup_src_en/`](../projects/StoneSoup_src_en/)（commit `b27fa86597cc`）。  
   **硬区分**：滤波器用到当前及过去观测；平滑用未来观测。B-08 与 FilterPy 同时提供 smoother，平滑结果不得称为可在线使用。

6. **可学习滤波（接到 11）**  
   经典补充：[`05_adaptive_filtering_estimation/papers/2021_Revach_KalmanNet_en.pdf`](../05_adaptive_filtering_estimation/papers/2021_Revach_KalmanNet_en.pdf)（v1 略早于窗口，已单列）。  
   官方代码：[`projects/KalmanNet_official_en/`](../projects/KalmanNet_official_en/)（commit `828a2cf529bc`，未见根目录许可证文件，权重未下载）。  
   另见 `2023_Buchnik_LatentKalmanNet_en.pdf`、`2023_Chen_OverviewDifferentiableParticleFilters_en.pdf`。

## 不确定性怎么写进实验记录

- 估计器：给出偏差、方差或 CRLB 对照，而不是单点误差。
- 检测器：ROC 或虚警约束下的检测概率；阈值随噪声与样本数变。
- 自适应滤波：稳态 MSE 与瞬态；步长过大则发散。
- 时间切分：先切分再做任何依赖标签的预处理，避免用未来统计量标准化训练集。

## 下一跳

工业振动/电流/生物信号 → [`guides/industrial_applications_path_cn.md`](industrial_applications_path_cn.md)。  
实时部署中的延迟与定点 → [`guides/realtime_deployment_cn.md`](realtime_deployment_cn.md)。
