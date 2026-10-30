# 软件与工具地图

本轮只保存官方文档子集与源码快照，不安装依赖、不运行、不下载商业软件本体。HTML 为离线可读页面本体；SciPy 的 S-01 另含 wget 页面资源。版本以抓取时页面或 SNAPSHOT 为准。

## Python 科学计算

| 工具 | 文档（离线） | 源码快照 | 用途与注意 |
|---|---|---|---|
| NumPy FFT | [`software_docs/NumPy_fft_docs_html_en/`](../software_docs/NumPy_fft_docs_html_en/)（S-02） | 未另存全库 | `fft` / `rfft` / `fftfreq` / `fftshift`；频率轴不要和采样率搞反 |
| SciPy signal/fft | [`software_docs/SciPy_1.16_signal_fft_docs_html_en/`](../software_docs/SciPy_1.16_signal_fft_docs_html_en/)（S-01，含教程与 butter/lfilter/filtfilt/resample/stft/welch） | [`projects/scipy_signal_subset_en/`](../projects/scipy_signal_subset_en/)（仅 `scipy/signal` 与 `scipy/fft`，commit `7490ad2d980f`） | **`lfilter` 因果；`filtfilt` 双向离线**。SOS 比高阶 TF 更稳 |
| PyWavelets | [`software_docs/PyWavelets_docs_html_en/`](../software_docs/PyWavelets_docs_html_en/)（S-03） | [`projects/PyWavelets_src_en/`](../projects/PyWavelets_src_en/) `c9b542b2d2c3` | DWT/CWT；边界延拓见 API |
| librosa 0.11.0 | [`software_docs/librosa_docs_html_en/`](../software_docs/librosa_docs_html_en/)（S-04） | [`projects/librosa_src_en/`](../projects/librosa_src_en/) `4ffed287f904` | STFT 默认可中心窗；示例音频已按规则丢弃 |
| torchaudio | [`software_docs/torchaudio_docs_html_en/`](../software_docs/torchaudio_docs_html_en/)（S-09） | 未另存全库 | GPU 重采样与变换；不含模型权重 |
| PyGSP | [`software_docs/PyGSP_docs_html_en/`](../software_docs/PyGSP_docs_html_en/)（S-10） | [`projects/PyGSP_src_en/`](../projects/PyGSP_src_en/) `4716b12c470c` | 图滤波；维护偏低 |
| padasip | 以源码 README 为准 | [`projects/padasip_src_en/`](../projects/padasip_src_en/) `4c13692b8f7c` | LMS/NLMS/RLS 在线更新 |
| ssqueezepy | README | [`projects/ssqueezepy_src_en/`](../projects/ssqueezepy_src_en/) `adf76ac19303` | CWT/同步压缩，离线 |
| PyLops | README | [`projects/PyLops_src_en/`](../projects/PyLops_src_en/) `9575012effa1` | 去卷积与正则化算子，离线 |
| deepinv | README | [`projects/deepinv_src_en/`](../projects/deepinv_src_en/) `ea2c1313f4c7` | 算法展开；权重未下载 |
| FilterPy | README/LICENSE | [`projects/filterpy_src_en/`](../projects/filterpy_src_en/) `5df4e095fac0` | Kalman/EKF/UKF/PF；含 smoother |
| Stone Soup | LICENSE | [`projects/StoneSoup_src_en/`](../projects/StoneSoup_src_en/) `b27fa86597cc` | 多传感器跟踪 |
| Asteroid | LICENSE | [`projects/asteroid_src_en/`](../projects/asteroid_src_en/) `c15708a04d3d` | 分离配方；权重未下载 |
| DDSP | LICENSE | [`projects/DDSP_src_en/`](../projects/DDSP_src_en/) `676aa9d8016e` | 可学习 DSP；权重/音频丢弃 |
| ThinkDSP | 与 B-04 配套 | [`projects/ThinkDSP_code_en/`](../projects/ThinkDSP_code_en/) `f9efe78b9e58` | 教学；大型 wav 已丢弃 |
| PyEMD | LICENSE | [`projects/PyEMD_src_en/`](../projects/PyEMD_src_en/) `e8ea44f6d577` | EMD 离线非因果 |
| pyroomacoustics | LICENSE | [`projects/pyroomacoustics_src_en/`](../projects/pyroomacoustics_src_en/) `ff7d61f219e4` | 室内声学与波束；示例音频丢弃 |

## 生物信号

| 工具 | 文档 | 源码 | 注意 |
|---|---|---|---|
| MNE-Python | [`software_docs/MNE_filtering_docs_html_en/`](../software_docs/MNE_filtering_docs_html_en/)（S-05，滤波/重采样教程） | 未存全库 | 默认 FIR 与零相位说明，是相位问题的主要依据 |
| WFDB-Python | [`software_docs/WFDB_python_docs_html_en/`](../software_docs/WFDB_python_docs_html_en/)（S-06） | [`projects/wfdb_python_src_en/`](../projects/wfdb_python_src_en/) `b8914e1c9c77` | 不下载 PhysioNet 大数据集 |

## 底层、嵌入式、流式

| 工具 | 文档 | 源码 | 注意 |
|---|---|---|---|
| FFTW3 | [`software_docs/FFTW_docs_html_en/`](../software_docs/FFTW_docs_html_en/)（S-07） | [`projects/FFTW_src_en/`](../projects/FFTW_src_en/) `a7b679c52833` | 规划、精度；本轮不编译 |
| CMSIS-DSP | [`software_docs/CMSIS_DSP_docs_html_en/`](../software_docs/CMSIS_DSP_docs_html_en/)（S-08） | [`projects/CMSIS_DSP_src_en/`](../projects/CMSIS_DSP_src_en/) `dce4b4f1db66` | 定点 FFT/FIR；注意溢出与 Q 格式 |
| GNU Octave Forge signal | [`software_docs/GNU_Octave_signal_docs_html_en/`](../software_docs/GNU_Octave_signal_docs_html_en/)（S-11） | 未存 | MATLAB 工具箱的自由软件对应；`filtfilt` 同样是离线零相位 |
| GNU Radio | [`software_docs/GNU_Radio_docs_html_en/`](../software_docs/GNU_Radio_docs_html_en/)（S-12，Doxygen：index/pages/filter/usage） | 未存全树 | 流式图、块处理。wiki 教程页对本 UA 返回 403，改用官方 Doxygen |

## MATLAB

MathWorks 公开 HTML（Signal/DSP/Wavelet Toolbox 索引）对本抓取 UA 返回 403 或子页 404，**未计入**。失败见 [`download_failures_cn.csv`](../download_failures_cn.csv) 中 S-13。不下载工具箱安装包或付费手册。对应概念用 SciPy/Octave 文档对照。

## 许可证（摘要）

SciPy/NumPy/MNE：BSD。PyWavelets：MIT。librosa：ISC。torchaudio：BSD-2。FFTW：GPL-2.0-or-later。CMSIS-DSP：Apache-2.0。PyLops：LGPL-3.0。其余见各 SNAPSHOT 旁 LICENSE。KalmanNet 根目录未见许可证文件。
