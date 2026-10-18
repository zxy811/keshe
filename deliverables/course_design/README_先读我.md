# 交付说明

这是基于你提供的 v61.zip 修改的数字系统综合设计工程，专业部分采用 AM/DSB。原始压缩包保存在 original_v61.zip，便于核对和恢复。新版源代码位于 v61，完整操作步骤见 docs/操作手册.md，论文见 docs/课程设计报告.docx。

**先核对硬件：原代码明确使用 TMS320C5509、ICETEK-VC5509/CTR、CCS 3.3。提供的大型手册文件名为 DSP28335，但未能读取。若实物是 TMS320F28335，不要下载本工程的 C5509 程序；底层驱动、工程、链接脚本和 FFT 汇编均需另行移植。**

## 功能

| 按键 | 功能 |
|---|---|
| 1 | 低通 FIR；截止 1—10 kHz |
| 2 | 带通 FIR；1—2 到 9—10 kHz |
| 3 | 带阻 FIR；1—2 到 9—10 kHz |
| 4 | C DIT FFT；输入图片中间行，80 点补零到 256 点 |
| 5 | 独立 DIF FFT 的汇编构建路径，见下方说明 |
| 6 | AM；1 kHz 消息、8 kHz 载波，同时显示图片行调制效果 |
| 7 | DSB-SC；抑制载波的双边带调制 |
| 8 | 当前滤波截止/频带循环；其他模式只修改保留参数 |
| 9 | 图片来源循环：内置条纹、内置渐变、已导入图片 |

默认运行：低通 4 kHz、内置条纹。源图 dbImage，结果 dbTargetImage，用户图片 dbUserImage。物理按键由原驱动 GetKey() 读取，没有虚构串口通信协议。

## 验证状态与限制

便携 C 源码在 Linux GCC 中实际构建，61 项测试已通过；后续完整结果以 results/validation.json 为准。28 组定点滤波器、图像边界卷积、FFT、多按键状态切换、AM/DSB 频谱均有独立参考验证。

第 5 键采取“独立 DIF C 描述 → TI C55x 编译器生成完整 .asm → 再汇编链接”的方式，提供可执行构建步骤，不是手写汇编 FFT。当前环境没有 cl55；TI 下载域名被策略拒绝，因此没有伪造生成的 .asm、目标 .out、目标汇编验证或板卡实测结论。如果教师明确要求手写汇编，这一项仍需补充，不能把编译器生成汇编写成手写成果。

Matlab 脚本在 matlab/run_all.m，输出到 matlab/matlab_output。随包 results/figures 的图由 Python/便携 C 生成，不能标成 Matlab 实测。运行 MATLAB 后产生的图才能作为 MATLAB 仿真图提交。已使用 GNU Octave 9.4.0 完整执行脚本并输出 30 张图，位于 matlab/octave_output；它代表兼容性验证，不代表 MATLAB 商业软件实际运行。

本包不含已验证的新 DSP 可执行文件。实物板型、下载器和虚拟机系统尚未核实；需要按手册在本地完成目标编译与下载验证。FLASH 固化需要匹配板卡的官方烧写工具和启动配置，本包提供核对及验收流程，不提供猜测地址的烧写程序。

## 先在电脑上演示

现代 Ubuntu：安装 python3-venv、gcc、python3-tk 后，在包根目录执行 `bash tools/setup_host.sh`，再执行 `.venv/bin/python tools/viewer.py --image assets/demo_input.png`。

Windows 10/11：安装 Python 3.11 和 MinGW-w64 GCC，配置 GCC 的 PATH，在包根目录运行 `tools\setup_host.bat`，再运行 `.venv\Scripts\python tools\viewer.py --image assets\demo_input.png`。

这是调用相同 C 算法的电脑模拟器，界面会明确显示 PC SIMULATION ONLY。真实板卡结果需由 CCS 读取/导出，不能把模拟按钮理解成已控制物理按键。

## 文件位置

* v61：原工程改造后的 C5509 源码、旧版板级文件、CCS 工程、目标构建脚本。
* tools：环境安装、主机 C 构建、图片导入导出、电脑模拟器与板卡快照查看器。
* assets：示例图片及 6400 个 16 位字的 CCS 数据文件。
* matlab：全部滤波器、FFT、AM/DSB 的 Matlab 仿真脚本。
* results：全量滤波系数、测试记录、数值输出、图形、实际软件版本。
* docs：操作手册、报告、硬件验收表和要求对照。

论文中姓名、学号、组员、日期与硬件实验记录留待本人填写；学校专用封面模板未提供，当前采用通用课程设计格式。现场实践和个人体会应由实际实验后补充。
