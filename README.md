# 数字系统综合设计：代码、操作手册与论文

基于提供的 `v61.zip` 修改，专业部分选择 AM/DSB。原代码属于 **TI C5509 / ICETEK-VC5509 / CCS 3.3**。

## 下载文件

点击文件链接进入 GitHub 文件页后，使用 **Download raw file / 下载原始文件** 下载；也可以使用仓库的 **Code → Download ZIP** 下载全部内容。

- [完整交付压缩包](deliverables/数字系统综合设计_代码与文档.zip)
- [操作手册 Word](deliverables/course_design/docs/操作手册.docx)
- [操作手册在线阅读](deliverables/course_design/docs/操作手册.md)
- [论文报告 Word](deliverables/course_design/docs/课程设计报告.docx)
- [论文报告 PDF](deliverables/course_design/docs/课程设计报告.pdf)
- [FIR 全量系数 PDF](deliverables/course_design/docs/FIR滤波系数表.pdf)
- [新版 DSP 源代码](deliverables/course_design/v61)
- [完整说明与验证限制](deliverables/course_design/README_先读我.md)

## 按键功能

| 按键 | 功能 |
|---|---|
| 1 / 2 / 3 | 低通 / 带通 / 带阻 FIR |
| 4 | C DIT FFT |
| 5 | 独立 DIF FFT 的汇编构建路径 |
| 6 / 7 | AM / DSB 调制 |
| 8 | 切换滤波频率 |
| 9 | 切换图片来源 |

## 验证与尚待完成事项

便携 C 已通过 61 项检查；Matlab 脚本已在 GNU Octave 9.4.0 中完整运行，产生 30 张图。报告正文约 5880 个汉字，硬件实验记录留待实际操作后填写。

实际开发板型号尚未确认；另一份大型手册文件名指向 F28335。**不得将本 C5509 工程的程序直接下载到 F28335。** 第 5 键采用 TI 编译器生成汇编后再汇编链接，属于编译器生成汇编，不是手写汇编；目标编译、开发板下载与 FLASH 固化尚未验证，本仓库没有经过验证的新版 DSP 可执行文件。

Python 虚拟环境、编译缓存和本机动态库不上传。原始代码完整保留在 [original_v61.zip](deliverables/course_design/original_v61.zip)。
