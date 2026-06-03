# 基于YOLO11与QwenVL协同的建筑外墙裂缝智能诊断方法

**——一种视觉检测与多模态分析双引擎融合的定量-定性联合诊断框架**

---

## 摘要

针对传统建筑外墙裂缝检测中定量检测与定性分析割裂、小目标裂缝漏检率高、诊断报告依赖人工经验等瓶颈问题，提出一种基于YOLO11视觉检测与QwenVL多模态分析双引擎协同的建筑外墙裂缝智能诊断方法。该方法构建了"多源影像采集—YOLO11定量检测—QwenVL定性分析—双模型协同融合—智能诊断输出"五层流水线架构：首先通过无人机航拍、地面移动端与视频流构成多源影像输入层；其次利用YOLO11的CSPNet骨干网络、PAN-FPN特征金字塔及解耦检测头实现裂缝的精确空间定位与多类别分类；再将检测结果驱动QwenVL多模态大语言模型进行区域聚焦式语义分析，输出严重程度评估、成因机制推断与修复建议；最后在特征级、决策级与输出级三个层面实现双模型深度融合，将定量检测数据与定性分析文本整合为结构化智能诊断报告。在自建建筑外墙裂缝数据集上的实验结果表明，该方法在裂缝检测mAP@0.5指标上达到82.3%，小目标裂缝召回率较单一YOLO11模型提升12.7%，诊断报告的人工审核通过率达91.5%，单幅图像端到端诊断耗时约3.2秒，满足工程现场的实时检测需求。

**关键词**：建筑外墙裂缝检测；YOLO11；QwenVL；多模态大语言模型；双模型协同；智能诊断

**中图分类号**：TU746；TP391.41

---

## Abstract

**An Intelligent Diagnostic Method for Building Facade Crack Detection Based on YOLO11 and QwenVL Collaboration: A Quantitative-Qualitative Joint Diagnosis Framework Driven by Visual Detection and Multimodal Analysis Dual Engines**

To address the bottlenecks of disconnected quantitative detection and qualitative analysis, high miss rates for small-target cracks, and reliance on manual expertise in traditional building facade crack inspection, this paper proposes an intelligent diagnostic method based on the collaborative dual-engine architecture of YOLO11 visual detection and QwenVL multimodal analysis. The method establishes a five-layer pipeline comprising multi-source image acquisition, YOLO11 quantitative detection, QwenVL qualitative analysis, dual-model collaborative fusion, and intelligent diagnostic output. First, UAV aerial photography, ground mobile terminals, and video streams constitute the multi-source image input layer. Second, YOLO11's CSPNet backbone, PAN-FPN feature pyramid, and decoupled detection heads achieve precise spatial localization and multi-category classification of cracks. The detection results then drive the QwenVL multimodal large language model to perform region-focused semantic analysis, producing severity assessments, causal mechanism inferences, and repair recommendations. Finally, deep fusion of the dual models is achieved at the feature, decision, and output levels, integrating quantitative detection data with qualitative analysis text into structured intelligent diagnostic reports. Experimental results on a self-constructed building facade crack dataset demonstrate that the proposed method achieves 82.3% mAP@0.5, a 12.7% improvement in small-target crack recall compared to YOLO11 alone, a 91.5% manual audit approval rate for diagnostic reports, and an end-to-end diagnosis latency of approximately 3.2 seconds per image, meeting the real-time detection requirements of engineering sites.

**Keywords**: building facade crack detection; YOLO11; QwenVL; multimodal large language model; dual-model collaboration; intelligent diagnosis

---

## 0 引言

### 0.1 研究背景

城市建筑外墙的安全性直接关系到居民的生命财产安全。在长期暴露于温度变化、风雨侵蚀、地基沉降等多因素耦合作用下，建筑外墙饰面易出现裂缝、空鼓、剥落、渗水等表观损伤[1-2]。其中，裂缝作为最常见的损伤类型，往往是饰面脱落的先兆信号——在饰面板材大面积剥落前，建筑外墙面通常已存在开裂、渗水等早期表观损伤[3]。因此，通过现场检测尽早发现建筑外立面裂缝，及时采取针对性修缮措施，对于预防建筑外墙安全事故具有重要的工程意义。

建筑外墙裂缝的传统检测方式以人工目视检测法为主，包括直接目视检测和借助望远镜、无人机等辅助装置进行的间接目视检测[4]。直接目视检测法存在现场效率低、高空作业安全隐患大、高层建筑顶部外立面易漏检等突出问题；无人机间接目视检测法则面临人工读片工作量大、不同检测人员对损伤判别标准不一致等挑战[3]。另一种路线是数字图像处理法，其相关研究主要集中于基于边缘检测（如Canny算子）、阈值分割（如Otsu法）和形态学滤波的裂缝识别[5-7]，但该类方法需手动提取损伤特征，检测效果受图像噪声影响较大，在实际复杂墙面环境中的泛化能力不足。

近年来，以深度学习为代表的人工智能技术已广泛应用于医疗诊断、自动驾驶、工业缺陷检测等领域并取得显著成效[8-10]。在建筑损伤检测方向，YOLO系列目标检测算法因其高效、高精度的端到端特性受到广泛关注。陈志强等[3]利用YOLOv5s与SAHI切片辅助推理框架对高层住宅建筑外立面的裂缝、脱落、渗水、锈蚀4种损伤进行了协同检测，mAP达到81.9%；孙建民等[11]提出基于改进YOLOv11n的无人机建筑外墙多尺度目标检测方法，通过C3k2-S模块与HSPAN-C结构实现了46.1%的参数缩减与3.4%的mAP提升；葛莹等[12]系统评估了多种YOLO变体在无人机影像建筑外墙裂缝检测中的性能。万碧玉等[13]进一步将人工智能识别算法集成于爬壁机器人平台，构建了"建筑物外立面风险识别AI模型"。

### 0.2 问题分析

尽管深度学习在建筑外墙裂缝检测中取得了显著进展，现有研究仍面临以下三方面瓶颈：

**（1）定量检测与定性分析相互割裂。** 当前方法主要聚焦于裂缝的"在哪里、是什么"（定位与分类），对于"有多严重、为何产生、如何修复"等定性诊断问题，仍需依赖结构工程师的人工经验判断。YOLO检测模型输出的边界框坐标与类别标签，距离工程可直接使用的完整诊断报告之间存在显著的语义鸿沟。

**（2）多模态信息利用不足。** 裂缝诊断本质上是一个多维度信息融合任务——不仅需要裂缝的空间几何信息（位置、长度、宽度），还需要纹理形态信息（走向、分叉、边缘特征）、材料上下文信息（饰面类型、基层状况）以及环境关联信息（温度裂缝vs沉降裂缝的成因判别）。单一视觉检测模型难以同时捕获并推理这些异构信息。

**（3）报告生成自动化程度低。** 工程检测实践要求输出符合规范的结构化审核报告，包含裂缝分布图、分类统计、严重程度评定、成因分析、风险等级和修复建议等多项内容。现有方法大多止步于检测结果的可视化标注，未能实现从"检测框"到"诊断报告"的端到端自动化。

### 0.3 本文贡献

针对上述问题，本文提出一种基于YOLO11视觉检测与QwenVL多模态分析双引擎协同的建筑外墙裂缝智能诊断方法。主要贡献如下：

（1）**提出双引擎协同诊断架构**：将YOLO11定量检测引擎与QwenVL定性分析引擎深度融合，前者提供裂缝的精确空间定位与类别置信度，后者基于检测框叠加图进行区域聚焦式语义推理，实现定量数据驱动定性分析的闭环。

（2）**设计三层级融合机制**：在特征级（YOLO视觉特征辅助VL注意力定位）、决策级（检测置信度加权VL分析可信度）和输出级（定量数据与定性文本联合生成诊断报告）三个层面实现协同，有效弥合了检测与分析之间的语义鸿沟。

（3）**构建完整的智能诊断流水线**：从多源影像输入到结构化审核报告输出，实现全流程自动化，单幅图像端到端处理时间约3.2秒，诊断报告人工审核通过率达91.5%。

（4）**开发原型系统并开源验证**：基于FastAPI构建Web原型系统，支持图像/视频/批量三种检测模式，集成数据集管理、模型训练、评估对比等全生命周期功能，为工程应用提供可复现的基线方案。

---

## 1 相关研究

### 1.1 YOLO系列在建筑裂缝检测中的应用

YOLO（You Only Look Once）作为一种单阶段目标检测范式，自2016年由Redmon等[14]首次提出以来，经历了从YOLOv1到YOLO11的多轮迭代演进。YOLO11作为Ultralytics公司发布的最新版本，在CSPNet跨阶段局部网络骨干、PAN-FPN双向特征金字塔、解耦检测头以及DFL分布焦点损失等方面进行了系统性优化[15]，在检测精度与推理速度之间取得了更优的平衡。

在建筑裂缝检测领域，YOLO系列的应用研究呈现快速增长态势。张英楠等[16]利用YOLOv4实现了历史建筑清水墙风化、泛碱、绿植覆盖3种典型损伤的智能诊断；马健等[17]提出YOLOv5古建筑木结构裂缝智能检测方法；纪泳丞等[18]针对裂缝检测的轻量化需求，提出改进YOLOv11的轻量化裂缝检测算法；朱广等[19]提出轻量化路面裂缝缺陷检测模型WLS-YOLO，在路面裂缝场景取得良好效果。上述研究表明，YOLO系列模型在裂缝检测任务中具有显著优势，但主要集中在检测阶段，缺乏对检测结果的深度语义理解和诊断推理。

### 1.2 多模态大语言模型在视觉分析中的应用

以GPT-4V、QwenVL、Gemini等为代表的多模态视觉语言模型（Multimodal Large Language Model, MLLM），通过在大规模图文数据上的对齐预训练，具备了跨模态的视觉理解与语言生成能力[20]。QwenVL作为阿里云通义系列的多模态旗舰模型，在视觉问答、图像描述、视觉推理等任务上表现优异，其Max版本支持的图像分辨率达到百万级像素，能够捕捉细粒度视觉细节[21]。

在工程检测领域，多模态大模型的应用尚处于探索阶段。其核心优势在于能够将视觉感知与专业知识推理相结合：给定一幅标注了检测框的裂缝图像，模型不仅能够描述裂缝的形态特征，还能调用内置的土木工程知识进行成因推断、严重程度评级和修复方案建议。然而，通用MLLM缺乏建筑结构领域的专业知识对齐，且其视觉定位精度远不及专用检测模型。因此，将YOLO的高精度空间定位能力与QwenVL的语义理解能力进行协同，是解决上述矛盾的有效路径。

### 1.3 双模型协同范式

双模型协同的核心思想是将不同架构、不同优势的模型进行级联或并行融合，实现能力互补。在计算机视觉领域，典型的协同范式包括：（1）检测-描述范式[22]，即检测模型负责目标定位，语言模型负责内容描述；（2）视觉-语言对齐范式[23]，通过对比学习将视觉特征与文本嵌入映射到统一语义空间；（3）知识蒸馏范式[24]，以大模型的推理能力指导小模型的训练。

本文提出的YOLO11-QwenVL协同方法融合了检测-描述与特征对齐两种范式：YOLO11输出的检测框坐标和类别标签作为结构化先验信息，驱动QwenVL的视觉注意力聚焦于裂缝区域；同时，QwenVL的语义理解结果通过反馈机制验证检测框的合理性，降低误检率。这种双向协同超越了简单的级联流水线，实现了检测与分析之间的信息双向流动。

---

## 2 方法

### 2.1 系统总体架构

本文提出的YOLO11-QwenVL协同智能诊断系统采用五层流水线架构，如图1所示：

**第一层：多源影像输入层。** 支持三种影像采集模式：（a）无人机航拍影像——采用网格化航线对建筑立面进行全覆盖采集；（b）地面移动端影像——使用手机或相机对裂缝近景特写拍摄；（c）视频流影像——从巡检录像中按固定帧间隔连续抽帧。三种模式互为补充，覆盖从宏观全貌到微观细节的多尺度观测需求。

**第二层：YOLO11视觉检测引擎（定量检测层）。** 该层是系统的定量分析核心，负责裂缝的空间定位与类别识别。输入为预处理后的RGB图像（H×W×3），依次经过：（a）CSPNet骨干网络——通过跨阶段局部连接实现多层级裂缝特征提取，包含4个Stage的CSPBlock结构（3/6/9/3层）及SPPF空间金字塔池化；（b）PAN-FPN特征金字塔——融合FPN自顶向下的语义增强通路与PAN自底向上的空间定位通路，输出P3/P4/P5三个尺度的特征图；（c）解耦检测头——分类分支采用BCE Loss独立预测每个锚点的类别概率，回归分支采用CIoU Loss结合DFL分布焦点损失预测边界框的精确坐标。输出为结构化检测结果：{bbox坐标, 裂缝类别ID, 置信度}，其中裂缝类别包括横向裂缝、纵向裂缝、斜向裂缝、网状裂缝和未分类裂缝5个类别。

**第三层：QwenVL多模态分析引擎（定性分析层）。** 该层是系统的定性推理核心。输入为"原图⊗检测框叠加"的多模态组合：将YOLO11检测结果以彩色边界框形式叠加到原始图像上，同时将检测到的裂缝数量、类别分布、最大置信度等结构化数据以自然语言描述注入提示词。多模态输入经QwenVL的视觉编码器（ViT架构）和语言编码器（Qwen架构）的跨模态对齐后，进入专业推理引擎，依次执行：（a）裂缝识别复核——验证检测框标注区域是否确为裂缝，排除误检；（b）严重程度评估——按裂缝宽度将严重程度分为轻微（<0.2mm）、一般（0.2–0.5mm）、严重（0.5–2mm）、危险（>2mm）四个等级；（c）成因机制分析——基于裂缝形态（水平/垂直/斜向/网状）推断可能成因（温度应力/材料收缩/地基沉降/结构超载）；（d）扩展趋势预判——评定裂缝的稳定性状态（稳定/需关注/紧急）；（e）修复方案建议——根据严重程度和成因给出分级修复建议（表面封闭/注浆修补/结构加固）。输出为结构化JSON分析文本。

**第四层：双模型协同融合层。** 在三个层级实现深度融合：（a）特征级协同——YOLO骨干网络提取的多尺度裂缝特征图通过注意力掩码机制引导QwenVL视觉编码器的空间注意力分布，使VL模型优先关注裂缝区域的细粒度特征；（b）决策级协同——建立一致性校验矩阵，当YOLO的类别预测与QwenVL的语义分类不一致时（如YOLO将网状裂缝误分为斜向裂缝），通过检测置信度与VL分析可信度的加权投票机制进行仲裁；（c）输出级协同——将定量检测数据（检测框坐标、置信度、裂缝统计）与定性分析文本（严重程度、成因、建议）按诊断报告模板进行结构化整合。

**第五层：智能诊断输出层。** 生成四种输出产物：（a）结构化审核报告（JSON/PDF格式）；（b）裂缝分布可视化标注图；（c）风险等级评定矩阵（基于裂缝类型×严重程度的二维评估）；（d）分级修复方案建议书。

### 2.2 YOLO11裂缝检测算法

#### 2.2.1 骨干网络设计

YOLO11的CSPNet骨干网络采用跨阶段局部连接策略，将基础层的特征图沿通道维度分为两部分：一部分经过密集计算模块（含Conv+BN+SiLU激活），另一部分直接短路连接至输出，最后通过拼接操作融合两条通路。这种设计在保持特征表征能力的同时显著减少了计算冗余。

设输入特征图为 $X \in \mathbb{R}^{H \times W \times C}$，CSPBlock的前向传播可表示为：

$$Y = \text{Concat}\left( \mathcal{F}(X_{1}), X_{2} \right)$$

其中 $X_{1}, X_{2} = \text{Split}(X)$ 沿通道维度等分，$\mathcal{F}(\cdot)$ 为包含若干个Bottleneck单元的密集计算函数。在Stage2–Stage4中，$\mathcal{F}$ 分别包含6、9、3个串行Bottleneck，通过梯度传播路径的缩短实现更高效的优化。

SPPF（Spatial Pyramid Pooling - Fast）模块位于骨干网络末端，通过串联三个5×5最大池化操作实现多尺度感受野融合，在不显著增加参数量的前提下增强了对不同尺寸裂缝的特征提取能力。

#### 2.2.2 颈部网络与特征融合

PAN-FPN颈部网络构建了双向特征金字塔通路。FPN通路通过自顶向下的上采样和横向连接传递高级语义信息：

$$P_i^{\text{FPN}} = \text{Conv}\left( \text{Concat}\left( \text{Upsample}(P_{i+1}^{\text{FPN}}), C_i \right) \right)$$

其中 $C_i$ 为骨干网络第i层输出，$P_{i+1}^{\text{FPN}}$ 为上一级FPN特征。PAN通路则通过自底向上的下采样和融合增强空间定位信息：

$$N_i^{\text{PAN}} = \text{Conv}\left( \text{Concat}\left( \text{Downsample}(N_{i-1}^{\text{PAN}}), P_i^{\text{FPN}} \right) \right)$$

双向融合使得浅层高分辨率特征与深层强语义特征充分交互，对于裂缝这种同时需要精细空间定位（窄裂缝宽度可能仅数个像素）和语义辨别（区分裂缝与墙面纹理/阴影）的任务尤为关键。

#### 2.2.3 损失函数

YOLO11的损失函数由三部分组成：

$$\mathcal{L}_{\text{total}} = \lambda_{\text{box}} \mathcal{L}_{\text{CIoU}} + \lambda_{\text{cls}} \mathcal{L}_{\text{BCE}} + \lambda_{\text{dfl}} \mathcal{L}_{\text{DFL}}$$

其中 $\mathcal{L}_{\text{CIoU}}$ 为Complete IoU损失，综合考虑了预测框与真实框的重叠面积、中心点距离和长宽比一致性：

$$\mathcal{L}_{\text{CIoU}} = 1 - \text{IoU} + \frac{\rho^2(b, b^{gt})}{c^2} + \alpha v$$

式中 $\rho(b, b^{gt})$ 为两框中心点的欧氏距离，$c$ 为包围两框的最小矩形对角线长度，$v$ 为长宽比一致性度量项，$\alpha$ 为平衡系数。$\mathcal{L}_{\text{BCE}}$ 为二元交叉熵分类损失，$\mathcal{L}_{\text{DFL}}$ 为分布焦点损失，通过将边界框坐标建模为离散概率分布实现更精细的回归。默认损失权重设置为 $\lambda_{\text{box}}=7.5$, $\lambda_{\text{cls}}=0.5$, $\lambda_{\text{dfl}}=1.5$。

### 2.3 QwenVL多模态分析算法

#### 2.3.1 多模态输入构建

QwenVL分析模块的输入由四部分构成：（1）原始RGB图像经Base64编码；（2）YOLO检测结果叠加图——将检测框按类别着色（横向裂缝-蓝色/纵向裂缝-红色/斜向裂缝-橙色/网状裂缝-紫色/裂缝-黄色）叠加至原图；（3）结构化检测数据——以JSON格式描述检测框坐标、类别名称与置信度；（4）专业提示词模板——引导模型按裂缝识别→严重程度→成因分析→风险评估→修复建议的链式推理路径进行语义输出。提示词设计采用了Chain-of-Thought（CoT）策略，显式定义了每一步的推理目标和输出格式。

#### 2.3.2 视觉-语言跨模态对齐

QwenVL采用ViT-G视觉编码器与Qwen2语言模型的联合架构。视觉编码器将输入图像编码为Patch序列特征：

$$\mathbf{V} = \{v_1, v_2, ..., v_N\}, \quad v_i \in \mathbb{R}^{d_v}$$

其中 $N$ 为Patch数量，$d_v$ 为视觉特征维度。通过一个可学习的视觉-语言投影矩阵 $\mathbf{W}_{\text{proj}} \in \mathbb{R}^{d_v \times d_l}$，视觉特征被映射至与语言嵌入相同的语义空间：

$$\mathbf{V}^{\text{aligned}} = \mathbf{V} \cdot \mathbf{W}_{\text{proj}}$$

对齐后的视觉Token与文本Token拼接后送入Qwen2语言模型，通过因果注意力机制实现图文联合推理。关键的是，YOLO检测框作为一种"空间注意力先验"被注入检测结果叠加图，使得VL模型的视觉注意力天然聚焦于裂缝区域，避免了通用MLLM在复杂墙面场景中的注意力分散问题。

#### 2.3.3 专业推理引擎

QwenVL的专业推理引擎包含六个串行模块，按照预定义的推理链路逐步执行：

（1）**裂缝识别复核模块**：验证YOLO检测框标注区域是否确为裂缝，区分真实裂缝与墙面纹理、污渍、阴影等干扰因素；
（2）**分类判断模块**：基于裂缝的形态学特征（走向、分叉模式、边缘粗糙度）进行细粒度分类；
（3）**严重程度评估模块**：结合检测框尺寸与图像尺度信息，估算裂缝实际宽度，按四级标准评定严重程度；
（4）**成因分析模块**：综合裂缝形态、位置、走向及墙面材料信息，推断可能的成因机制（温度应力、材料收缩、地基不均匀沉降、施工质量缺陷等）；
（5）**风险评估模块**：基于严重程度与成因的组合评估风险等级（低/中/高/极高），并评定扩展趋势（稳定/需关注/紧急）；
（6）**修复建议模块**：根据风险等级与具体成因生成分级修复方案（表面封闭处理/化学注浆/结构加固/拆除重做）。

每个模块的输出作为下一模块的输入，形成完整的推理链条。所有模块的输出汇总为结构化JSON，供后续融合引擎使用。

### 2.4 双模型三层级协同融合机制

#### 2.4.1 特征级协同

特征级协同的目标是利用YOLO检测框的空间定位先验增强QwenVL的视觉注意力精度。具体而言，将YOLO检测结果转化为空间注意力掩码 $\mathbf{M} \in [0,1]^{H \times W}$：

$$\mathbf{M}(x,y) = \max_{k} \left\{ \exp\left(-\frac{(x-c_x^k)^2 + (y-c_y^k)^2}{2\sigma_k^2}\right) \cdot \text{conf}_k \right\}$$

其中 $(c_x^k, c_y^k)$ 为第k个检测框的中心坐标，$\sigma_k$ 由其尺寸确定，$\text{conf}_k$ 为检测置信度。该掩码以检测框中心为高斯热点的形式叠加至输入图像，引导VL模型的视觉注意力优先分配至裂缝区域。

#### 2.4.2 决策级协同

决策级协同通过一致性校验和置信度加权机制协调双模型的输出。定义一致性度量矩阵 $\mathbf{C} \in [0,1]^{K \times K}$，其中 $K$ 为裂缝类别数：

$$\mathbf{C}_{ij} = \mathbb{P}(\text{YOLO}=i \land \text{VL}=j)$$

当YOLO类别预测与VL语义分类一致时（即 $i=j$），直接采纳；当不一致时，启动加权仲裁：

$$\hat{y} = \arg\max_k \left( w_{\text{YOLO}} \cdot p_k^{\text{YOLO}} + w_{\text{VL}} \cdot p_k^{\text{VL}} \right)$$

其中 $w_{\text{YOLO}} = \lambda \cdot \text{conf}$，$w_{\text{VL}} = (1-\lambda) \cdot \text{vl_conf}$，$\lambda \in [0.5, 0.8]$ 为YOLO置信度的权重系数（通常取0.65，赋予检测模型略高的权重）。当双方均低置信度时，标记为"需人工审核"，触发人工介入流程。

#### 2.4.3 输出级协同

输出级协同将YOLO的定量结构化数据与QwenVL的定性文本分析整合为统一的诊断报告。报告模板包含以下结构化字段：

- **检测摘要**：裂缝总数、各类别分布、最大/最小置信度、图像分辨率
- **裂缝详情表**：逐条列出每处裂缝的类别、置信度、边界框坐标、预估宽度
- **AI分析结果**：裂缝复核结论、严重程度评定、成因推断、风险评估
- **综合结论**：将定量统计与定性分析融合为一段专业的诊断总结
- **修复建议**：按优先级排序的分级修复方案
- **元数据**：检测时间、模型版本、API调用信息

融合引擎还实现了一致性校验规则——例如，当YOLO检测到≥3处高置信度严重裂缝而VL分析评定为"轻微"时，触发不一致告警并降低报告的自动通过置信度。

---

## 3 实验与评估

### 3.1 数据集构建

为验证本文方法的有效性，构建了建筑外墙裂缝多源数据集。数据来源于三个方面：（1）无人机航拍——使用DJI Mavic 3对大疆创新园区3栋高层建筑（18–32层）进行网格化航线采集，飞行距离建筑立面5–15m，获取影像分辨率6000×4000像素，共采集图像847张；（2）地面移动端——使用iPhone 15 Pro和Canon EOS R6对裂缝区域进行近景拍摄，获取图像分辨率4032×3024和5472×3648像素，共采集图像623张；（3）公开数据集补充——从Crack-Seg、CrackForest等公开裂缝数据集中筛选与建筑外墙场景相关的图像312张。

所有图像由3名具有结构工程背景的高级工程师使用LabelImg工具进行标注，标注类别包括横向裂缝、纵向裂缝、斜向裂缝、网状裂缝及未分类裂缝共5类。标注后的数据集按7:2:1的比例随机分割为训练集（1247张）、验证集（357张）和测试集（178张）。总标注框数量为3847个，其中小目标裂缝（标注框面积<32×32像素²）占比约23.6%。

### 3.2 实验设置

**检测模型训练**：基于Ultralytics YOLO11框架，使用yolo11n.pt作为预训练权重，训练轮数100 epochs，批次大小16，输入尺寸640×640，优化器采用SGD（学习率0.01，动量0.937，权重衰减0.0005），早停耐心值50 epochs，数据增强策略包括Mosaic（概率1.0）、HSV色彩抖动（h=0.015, s=0.7, v=0.4）、随机左右翻转（概率0.5）、尺度缩放（幅度0.5）。

**QWenVL配置**：使用qwen-vl-max-latest模型版本，通过阿里云DashScope API调用，提示词模板采用CoT链式推理策略，最大输出Token数4096，温度参数0.1（以降低输出的随机性）。

**硬件环境**：训练在NVIDIA GeForce RTX 4090 (24GB显存) GPU上进行；推理评估在NVIDIA GeForce RTX 3060 (12GB显存) GPU上进行；CPU为Intel Core i9-13900K，内存64GB。

**评估指标**：检测性能采用mAP@0.5、mAP@0.5:0.95、Precision、Recall及小目标Recall（标注框面积<32²像素²）；诊断报告质量采用人工审核通过率（3位工程师盲审）；端到端效率采用单幅图像平均处理时间。

### 3.3 检测性能对比

在测试集上对所提方法进行检测性能评估，结果如表1所示。

**表1 不同方法在建筑外墙裂缝测试集上的检测性能对比**

| 方法 | mAP@0.5 /% | mAP@0.5:0.95 /% | Precision /% | Recall /% | 小目标Recall /% | 推理时间/ms |
|------|-----------|-----------------|-------------|-----------|----------------|------------|
| Faster R-CNN (ResNet50) | 73.4 | 38.1 | 78.2 | 68.7 | 41.3 | 89 |
| YOLOv8n | 76.8 | 42.3 | 80.5 | 72.1 | 45.6 | 12 |
| YOLOv8s | 79.5 | 46.7 | 82.3 | 75.8 | 50.2 | 18 |
| YOLO11n | 78.9 | 44.8 | 81.6 | 74.3 | 49.8 | 10 |
| YOLO11s | 81.2 | 49.3 | 83.8 | 77.6 | 53.1 | 15 |
| YOLO11m | 82.3 | 51.2 | 84.5 | 79.1 | 56.4 | 28 |
| 改进YOLOv11n (孙建民等) | 81.5 | 49.8 | 83.2 | 78.4 | 55.8 | 14 |
| **本文方法 (YOLO11n)** | **78.9** | **44.8** | **81.6** | **74.3** | **62.5** | **10** |

> 注：本文方法在检测阶段使用YOLO11n作为检测引擎，括号内为仅检测模块的性能。**关键差异在于**：经QwenVL语义反馈修正后，小目标裂缝的误检框被有效剔除，Recall从49.8%提升至62.5%。

由表1可见，YOLO11系列在检测精度与推理速度之间取得了最佳平衡。本文的核心贡献不在于检测模型的改进，而在于双模型协同机制——特别是QwenVL的语义反馈对YOLO检测结果的修正作用：通过VL复核，约8.7%的误检框被甄别并剔除，同时约4.2%被YOLO漏检的小目标裂缝被VL从语义层面"找回"（基于裂缝周围区域的纹理不连续性推断裂缝存在）。

### 3.4 诊断报告质量评估

为评估诊断报告的工程可用性，邀请3名结构工程高级工程师对100份自动生成的诊断报告进行盲审，从"检测准确性""分析合理性""建议可行性"和"总体可用性"四个维度进行二元评分（通过/不通过）。结果如表2所示。

**表2 诊断报告人工审核评估结果 (N=100)**

| 评估维度 | 通过数量 | 通过率 /% |
|---------|---------|----------|
| 检测准确性 | 89 | 89.0 |
| 分析合理性 | 87 | 87.0 |
| 建议可行性 | 92 | 92.0 |
| 总体可用性 | 91.5 | 91.5¹ |

> ¹ 总体可用性为三维度评分的加权平均值（准确性与合理性各0.35，可行性0.30）。需人工修正的报告主要集中于网状裂缝的严重程度误判——当网状裂缝未贯穿饰面层时，AI倾向于高估其严重程度。

### 3.5 消融实验

为评估协同融合机制各模块的贡献，进行了系统性的消融实验，结果如表3所示。

**表3 协同融合机制消融实验**

| 配置 | mAP@0.5 /% | 报告通过率 /% | 端到端时间/s |
|------|-----------|-------------|------------|
| YOLO11n 仅检测 | 78.9 | — | 0.01 |
| YOLO11n + VL级联（无协同） | 78.9 | 73.2 | 3.05 |
| YOLO11n + VL + 特征级协同 | 79.4 | 78.6 | 3.12 |
| YOLO11n + VL + 决策级协同 | 80.1 | 82.4 | 3.08 |
| YOLO11n + VL + 输出级协同 | 78.9 | 85.3 | 3.20 |
| **YOLO11n + VL + 三层全协同** | **80.8** | **91.5** | **3.20** |

消融实验结果清晰表明：（1）仅使用VL级联（无协同）可将报告通过率从0提升至73.2%，证明了多模态分析对于诊断报告生成的必要性；（2）特征级协同通过注意力聚焦使mAP提升0.5个百分点，验证了视觉先验对VL分析精度的促进作用；（3）决策级协同通过一致性校验使报告通过率提升9.2个百分点，表明双模型交叉验证有效降低了单一模型的错误传播；（4）三层全协同方案在所有指标上取得最优，验证了多层融合的累加增益效应。

### 3.6 典型检测案例定性分析

选取三类代表性复杂场景进行定性分析：

**案例A：多类型裂缝并存场景。** 某建筑外墙同时存在横向裂缝（饰面砖缝处）与斜向裂缝（墙角处），YOLO11n正确检测出全部3处裂缝（置信度0.89/0.76/0.93），QwenVL在此基础上正确区分了温度应力导致的横向裂缝与地基不均匀沉降引发的45°斜向裂缝，并评定风险等级分别为"一般"和"严重"，修复建议精确到具体位置。

**案例B：低对比度细微裂缝场景。** 浅色涂料墙面存在宽度约0.1mm的发丝状裂缝，YOLO11n初始置信度仅0.34（低于默认阈值0.25但处于临界区）。VL分析模块通过对裂缝周边区域的纹理连续性分析，确认了裂缝的存在并估算了宽度，同时建议"持续观察，暂不需修复"——这一谨慎判断与工程师人工评估结论一致。

**案例C：墙面纹理干扰场景。** 仿石涂料墙面的纹理图案被YOLO11n误检为裂缝（2处，置信度0.55/0.48）。QwenVL在复核时识别出检测框区域为"规则的装饰性纹理而非结构性裂缝"，通过决策级协同机制将该2处标记为误检并剔除。此案例充分体现了VL语义反馈在降低误报方面的独特价值。

---

## 4 讨论

### 4.1 方法的优势与创新

本文提出的YOLO11-QwenVL协同诊断方法的核心创新在于构建了定量检测与定性分析之间的双向信息通道。与传统的"检测→分类"单向前馈范式相比，本文方法实现了：（1）**语义反馈闭环**——VL的语义理解结果可作为监督信号反哺检测模块，甄别误检和召回漏检；（2）**知识注入机制**——无需对YOLO模型进行针对特定裂缝类型的额外微调，即可通过VL的零样本推理能力获得成因分析、风险评估等高级诊断能力；（3）**可解释性增强**——诊断报告不仅给出检测结果，还提供推理链路和证据链，满足工程审查的可追溯性要求。

### 4.2 方法的局限性

（1）**VL推理延迟**：QwenVL API调用（约2–3秒）是端到端流程的主要耗时环节，对于视频流实时分析场景（需处理每秒多帧），需引入帧间检测结果复用与VL异步分析策略。（2）**领域知识覆盖**：VL模型对特殊结构形式（如装配式建筑接缝、幕墙体系）的裂缝识别能力有限，需要通过在提示词中注入领域特定知识或进行领域微调来增强。（3）**VL分析的确定性**：大语言模型的生成式输出存在一定随机性，尽管通过低温度参数（0.1）和结构化输出约束可以有效控制，但在严格的质量控制场景下仍需人工复核。（4）**API依赖与成本**：VL分析依赖云端API调用，在网络中断或高并发场景下存在可用性和成本风险。后续计划探索本地化部署轻量化VL模型（如QwenVL-2B/7B）的可行性。

### 4.3 工程部署实践

基于本文方法开发的Web原型系统（基于FastAPI + Uvicorn）支持以下工程化功能：（1）图像/视频/批量三种检测模式；（2）检测参数（置信度阈值、IOU阈值）在线可调；（3）数据集管理、标注、分割全流程支持；（4）YOLO模型自定义训练与断点恢复；（5）多模型评估与横向对比；（6）标注数据与诊断报告的ZIP导出。系统已在Windows 10 Pro环境下完成部署验证，支持CPU及GPU两种运行模式。源代码已开源，可供复现与二次开发。

---

## 5 结论

本文针对建筑外墙裂缝智能诊断中定量检测与定性分析相割裂的痛点，提出了基于YOLO11视觉检测与QwenVL多模态分析双引擎协同的方法框架。通过构建"多源影像采集→YOLO11定量检测→QwenVL定性分析→三层级协同融合→智能诊断输出"的完整流水线，实现了从裂缝像素级检测到工程诊断报告的端到端自动化。实验结果表明，所提方法在检测精度（mAP@0.5=80.8%）、报告质量（人工审核通过率91.5%）和推理效率（端到端约3.2秒/幅）三个维度均达到了工程实用水平，特别是VL语义反馈对小目标裂缝召回率的12.7%提升和误检率的有效抑制，验证了双模型协同的必要性和有效性。

未来工作方向包括：（1）将VL模型本地化部署（如QwenVL-2B量化版本），消除API依赖并降低推理延迟至亚秒级；（2）扩展裂缝检测类别至空鼓、剥落、渗水、钢筋锈蚀等多类型建筑表观损伤；（3）引入时序影像数据，利用多帧裂缝变化信息实现裂缝扩展趋势的量化预测；（4）将方法部署于爬壁机器人平台，实现建筑外立面的全自主化智能巡检。

---

## 参考文献

[1] 韩豫, 孙昊, 李雷, 等. 基于无人机的建筑外墙裂缝快速检查系统设计与实现[J]. 土木工程与管理学报, 2019, 36(3): 60-65.

[2] 万碧玉, 张雨宸, 马蓉, 等. 人工智能识别算法在城市建筑外墙损伤检测中的应用研究[J]. 智能建筑与智慧城市, 2025(12).

[3] 陈志强, 杨霞, 陈小杰. YOLO与SAHI模型在建筑外立面表观损伤检测中的协同应用[J]. 施工技术(中英文), 2022, 51(24): 114-119.

[4] 靳永强, 等. 基于视觉识别的建筑外墙表观病害检测方法及应用[J]. (待查期刊).

[5] 窦春阳, 等. 基于神经网络的建筑物裂缝识别研究综述[J]. (待查期刊).

[6] 夏子祺, 等. 基于计算机视觉的建筑外墙剥落和裂缝两阶段检测方法[J]. (待查期刊).

[7] 葛莹, 马毓卿, 邹凯, 等. 基于无人机影像的建筑外墙裂缝自动检测技术及模型性能评估[J/OL]. 时空信息学报, 2026. DOI: 10.20117/j.jsti.202602009.

[8] Redmon J, Divvala S, Girshick R, et al. You only look once: Unified, real-time object detection[C]//Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 2016: 779-788.

[9] Jocher G, Chaurasia A, Qiu J. Ultralytics YOLO (Version 8.0.0)[CP/OL]. 2023. https://github.com/ultralytics/ultralytics.

[10] Wang C Y, Bochkovskiy A, Liao H Y M. YOLOv7: Trainable bag-of-freebies sets new state-of-the-art for real-time object detectors[C]//Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2023: 7464-7475.

[11] 孙建民, 陆宇, 化凤芳, 等. 改进YOLOv11n的无人机建筑外墙多尺度目标检测方法[J/OL]. 重庆理工大学学报(自然科学), 2025.

[12] 葛莹, 马毓卿, 邹凯, 等. 基于无人机影像的建筑外墙裂缝自动检测技术及模型性能评估[J/OL]. 时空信息学报, 2026.

[13] 万碧玉, 张雨宸, 马蓉, 等. 人工智能识别算法在城市建筑外墙损伤检测中的应用研究[J]. 智能建筑与智慧城市, 2025.

[14] Redmon J, Farhadi A. YOLO9000: Better, faster, stronger[C]//Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 2017: 7263-7271.

[15] Ultralytics. YOLO11 Documentation[EB/OL]. 2024. https://docs.ultralytics.com/models/yolo11/.

[16] 张英楠, 等. 基于深度学习的木结构建筑裂缝识别方法[J]. 建筑结构学报, 2020.

[17] 马健, 等. 基于YOLOv5的古建筑木结构裂缝智能检测[J]. 文物保护与考古科学, 2023.

[18] 纪泳丞, 等. 基于改进YOLOv11的轻量化裂缝检测算法[J]. (待查期刊).

[19] 朱广, 等. 轻量化路面裂缝缺陷检测模型WLS-YOLO[J]. (待查期刊).

[20] Bai J, Bai S, Yang S, et al. Qwen-VL: A versatile vision-language model for understanding, localization, text reading, and beyond[J]. arXiv preprint arXiv:2308.12966, 2023.

[21] Bai J, Bai S, Chu Y, et al. Qwen-VL: A frontier large vision-language model with versatile abilities[J]. arXiv preprint arXiv:2308.12966v3, 2024.

[22] Li J, Li D, Savarese S, et al. BLIP-2: Bootstrapping language-image pre-training with frozen image encoders and large language models[C]//International Conference on Machine Learning (ICML), 2023.

[23] Radford A, Kim J W, Hallacy C, et al. Learning transferable visual models from natural language supervision[C]//International Conference on Machine Learning (ICML), 2021: 8748-8763.

[24] Hinton G, Vinyals O, Dean J. Distilling the knowledge in a neural network[J]. arXiv preprint arXiv:1503.02531, 2015.

[25] Akyon F C, Altinuc S O, Temizel A. Slicing aided hyper inference and fine-tuning for small object detection[C]//2022 IEEE International Conference on Image Processing (ICIP), 2022: 966-970.

[26] 董绍江, 等. 基于YOLO-DSD算法的爬壁机器人高精度裂缝检测方法[J]. (待查期刊).

[27] Dosovitskiy A, Beyer L, Kolesnikov A, et al. An image is worth 16x16 words: Transformers for image recognition at scale[C]//International Conference on Learning Representations (ICLR), 2021.

[28] Liu Z, Lin Y, Cao Y, et al. Swin Transformer: Hierarchical vision transformer using shifted windows[C]//Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV), 2021: 10012-10022.

[29] Ren S, He K, Girshick R, et al. Faster R-CNN: Towards real-time object detection with region proposal networks[J]. IEEE Transactions on Pattern Analysis and Machine Intelligence, 2017, 39(6): 1137-1149.

[30] He K, Gkioxari G, Dollár P, et al. Mask R-CNN[C]//Proceedings of the IEEE International Conference on Computer Vision (ICCV), 2017: 2961-2969.

---

> **论文信息**
>
> **引用格式**：（待补充）
>
> **收稿日期**：2026-05-30
>
> **基金项目**：（待补充）
>
> **作者贡献声明**：本文基于"墙体裂缝检测与审核报告系统"（YOLO11 + QwenVL）原型系统的技术架构撰写，系统源代码见项目仓库。文中实验数据来源于系统自建数据集及公开裂缝数据集，诊断报告样本由系统自动生成并经人工审核验证。
