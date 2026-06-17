# Accessibility_TestCase_Generation
This repository contains the dataset and code for the paper titled "基于大语言模型的移动应用GUI无障碍问题复现测试用例生成方法"

本仓库包含了论文《基于大语言模型的安卓移动应用GUI无障碍问题复现测试用例生成方法》相关的代码、50个测试用例样本以及实验评估脚本, 同时数据集中公开了实验所需的GUI。

## 📖 项目简介 (Introduction)

移动应用中的无障碍问题会严重影响全球数亿视障用户的使用体验。现有自动化测试方法多依赖规则引擎或静态分析，难以覆盖复杂的动态交互和辅助功能语义，导致无障碍问题复现测试用例极度匮乏。

本项目提出了一种结合大语言模型（LLMs，如 GPT-4o）与小样本学习（Few-shot Learning）的自动化测试生成框架。该方法通过整合多源界面信息（视觉、结构、语义）与 LLM 推理，能够自动生成高质量、可执行的 Android UIAutomator 无障碍复现测试用例，并配备了闭环验证与自动修复机制。实验表明，本方法在测试用例的生成执行成功率和问题复现率上显著优于基线方法（如 AXNav、GPTDroid 等）。

## ⚙️ 核心方法论 (Methodology Pipeline)

我们的自动化管线包含以下四个核心步骤：

1. **多源 GUI 表征构建与无障碍问题根控件识别**：结合界面截图（视觉层）、布局 XML（结构层）及 TalkBack 输出（辅助功能语义层），利用大语言模型精准定位导致无障碍问题的根控件。
2. **交互路径推理**：结合用户目标、无障碍问题描述及控件状态，推理出能够触发问题的多条交互路径（包含滑动、点击等），并对路径的可执行性进行打分以推荐最优路径。
3. **无障碍测试用例生成**：基于 50 个由无障碍专家编写的真实测试用例进行小样本学习，将自然语言推理的操作路径转化为可执行的 Android UIAutomator 脚本。
4. **闭环验证与自修复机制**：在模拟器中运行生成的脚本，若执行失败，则通过结构化提示让 LLM 分析错误日志与界面树，自适应地调整定位方式并迭代生成修复脚本（最高 5 次迭代）。

## 📁 仓库结构 (Repository Structure)

```text
├── pipeline/
│   ├── Ptrompt_Design.py         # 核心生成管线代码（包含 Step 1 - Step 4）
├── test_cases/
│   ├── Accesibility Issues.html  # 无障碍问题列表
│   └── TestCase_Example/         # 生成的50个可直接运行的 UIAutomator 测试用例
├── evaluation/
│   ├── Experiment(RQ1).py        # RQ1 & RQ4 性能评估与多模型对比脚本
│   ├── Experiment(RQ2).py           # RQ2 提示工程与小样本学习消融实验脚本
│   └── Experiment(RQ3).py        # RQ3 闭环修复自适应评估脚本
├── Accessibility_Test_Case_Data1-8  # Google Play与F-Droid的开源示例数据
├── Annotation_Guidelines.ipynb   # 用户标注规范
└── README.md                     # 本文档
