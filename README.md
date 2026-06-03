# 墙体裂缝检测与审核报告系统

基于 **YOLO11 + QWEN-VL** 双模型协同的墙体裂缝智能检测与审核报告生成系统。

## 系统架构

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  图片上传    │────▶│  YOLO11      │────▶│  QWEN-VL     │────▶│  审核报告     │
│  Web 界面    │     │  裂缝检测     │     │  视觉分析     │     │  自动生成     │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                          │                     │
                    检测框+置信度          裂缝分类+严重程度
                    裂缝类型统计          原因分析+修复建议
```

**核心功能**：

| 模块 | 功能 | 说明 |
|------|------|------|
| 🔍 裂缝检测 | 图像/视频/批量检测 | YOLO11 实时检测 + 裂缝尺寸测量 |
| 🤖 AI 分析 | QWEN-VL 多模态诊断 | 严重程度/成因/风险/修复建议 |
| 🏷️ 数据标注 | 矩形+多边形标注 | 支持 LabelMe 格式导入导出 |
| 🎯 模型训练 | 自定义训练+断点恢复 | 27项可调参数，训练中断自动清理 |
| 📊 模型评估 | 多模型对比评估 | mAP/混淆矩阵/各类别指标 |
| 📥 数据集导入 | 本地文件夹导入 | 支持 YOLO 格式含子目录递归扫描 |

**工作流程**：

1. 用户通过 Web 界面上传墙体图片
2. YOLO11 目标检测模型识别裂缝位置、类型和置信度，**自动测量裂缝宽度和长度**
3. 将 YOLO 检测结果与原图一起发送给 QWEN-VL 视觉语言模型
4. QWEN-VL 进行专业级裂缝分析（分类、严重程度、原因、建议）
5. 系统自动整合双模型结果，生成结构化审核报告

## 环境要求

| 项目 | 最低要求 |
|------|---------|
| Python | 3.10+ |
| 内存 | 8GB+（推荐 16GB） |
| GPU | 可选（CPU 可运行，GPU 显著加速 YOLO 推理） |
| 磁盘 | 2GB+（含模型权重） |
| 操作系统 | Windows / Linux / macOS |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key（可选）

如需使用 QWEN-VL 真实分析功能，需配置阿里云 DashScope API Key：

**Windows:**
```bash
set DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx
```

**Linux/macOS:**
```bash
export DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx
```

> 未配置 API Key 时，系统将使用内置模拟分析，仍可正常运行。模拟分析基于 YOLO 检测结果生成合理推断，但不如 QWEN-VL 真实分析精确。

API Key 获取方式：
1. 访问 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/)
2. 注册/登录阿里云账号
3. 开通 DashScope 服务
4. 在 API-KEY 管理页面创建新的 API Key

### 3. 启动服务

**方式一：快捷脚本（推荐）**

双击项目根目录下的 `start.bat`，自动启动服务并打开浏览器。

| 脚本 | 功能 |
|------|------|
| `start.bat` | 🚀 启动服务 + 自动打开浏览器 |
| `stop.bat` | 🛑 一键停止服务 |
| `open.bat` | 🌐 仅打开浏览器（服务已运行时） |

**方式二：命令行**

```bash
python app.py
```

> 启动时系统会自动清理上次异常退出残留的训练/评估状态（`running`/`pending` → `interrupted`），避免服务重启后显示"训练中"但实际无进程的问题。

启动成功后，浏览器访问 **http://localhost:8000**

### 4. 使用自定义模型（可选）

将训练好的 YOLO11 裂缝检测权重文件放置到 `weights/best.pt`，系统启动时会自动加载。

## 项目结构

```
qiangtijiance/
├── app.py                    # FastAPI 主应用入口
├── config.py                 # 全局配置文件
├── requirements.txt          # Python 依赖清单
├── start.bat                 # 快捷启动脚本
├── stop.bat                  # 快捷停止脚本
├── open.bat                  # 快捷打开浏览器
├── models/
│   ├── __init__.py
│   ├── detector.py           # YOLO11 裂缝检测模块
│   ├── analyzer.py           # QWEN-VL 视觉分析模块
│   ├── annotator.py          # 数据标注管理模块
│   ├── trainer.py            # 模型训练管理模块
│   └── evaluator.py          # 模型评估管理模块
├── services/
│   ├── __init__.py
│   └── report.py             # 审核报告生成服务
├── templates/
│   ├── index.html            # 检测分析前端界面
│   ├── annotation.html       # 数据标注前端界面
│   ├── training.html         # 模型训练前端界面
│   └── evaluation.html       # 模型评估前端界面
├── static/
│   ├── uploads/              # 上传图片存储目录
│   ├── results/              # 检测结果标注图存储目录
│   ├── reports/              # 生成的 JSON 报告存储目录
│   ├── video_frames/         # 视频帧提取目录
│   └── exports/              # 数据导出目录
├── weights/                  # 自定义 YOLO 模型权重目录
│   └── (放置 best.pt)
├── datasets/                 # 数据集存储目录
├── training/                 # 训练输出目录
├── evaluation/               # 评估结果目录
└── docs/                     # 文档目录
    ├── configuration.md      # 配置说明
    ├── api.md                # API 接口文档
    ├── deployment.md         # 部署指南
    ├── custom_model.md       # 自定义模型训练指南
    ├── training_guide.md     # 模型训练使用指南
    ├── evaluation_guide.md   # 模型评估使用指南
    ├── annotation_guide.md   # 数据标注使用指南
    └── dataset_guide.md      # 数据集管理指南
```

## Web 界面使用说明

### 🏠 首页 — 裂缝检测

1. 在左侧面板点击上传区域或拖拽图片到上传区域
2. 支持格式：PNG、JPG、JPEG、BMP、TIFF、WEBP（最大 100MB）
3. 支持视频文件（MP4、AVI、MOV 等，最大 500MB）
4. 调整检测参数（置信度阈值、IOU 阈值、**标定参数**）

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 置信度阈值 | 0.25 | 低于此阈值的检测结果将被过滤 |
| IOU 阈值 | 0.45 | NMS 重叠框去除激进程度 |
| **像素毫米比** | 5.0 | 用于计算裂缝实际宽度和长度 |

5. 填写项目信息（项目名称、检测位置、检测人员）
6. 点击「开始检测与分析」，系统依次执行 YOLO 检测 → QWEN-VL 分析 → 报告生成

结果展示在三个标签页中：

| 标签页 | 内容 |
|--------|------|
| 🎯 检测结果 | 标注图（含 **宽度/长度标注**）、检测统计、裂缝详情 |
| 🤖 AI 分析 | 裂缝复核、严重程度、成因、风险、修复建议 |
| 📋 审核报告 | 结构化报告，含测量数据，支持打印和 JSON 下载 |

### 🏷️ 标注页面

| 功能 | 说明 |
|------|------|
| 矩形标注 | 拖拽绘制，快捷键 `R` |
| 多边形标注 | 点击添加顶点，双击闭合，快捷键 `P` |
| 编辑标注 | 拖拽顶点/整体移动/边线加点/删点，快捷键 `E` |
| LabelMe 导入 | `POST /api/datasets/{id}/import_labelme` |
| LabelMe 导出 | 导出格式选择 `labelme` |
| 数据集导入 | 📥 按钮 → 输入本地文件夹路径 |
| 自动标注 | YOLO11 模型自动预标注 |

### 🎯 训练页面

- 27 项可调超参数（学习率/损失权重/数据增强）
- 实时训练曲线（Loss/mAP/LR）
- **训练中断自动恢复**：服务重启后 `running`→`interrupted`，支持从 `last.pt` 断点恢复

### 📊 评估页面

- 多模型横向对比
- 混淆矩阵 + 各类别指标
- 系统自动生成优化建议

## 严重程度等级说明

| 等级 | 颜色 | 裂缝宽度 | 处理建议 |
|------|------|---------|---------|
| 轻微 | 🟢 绿色 | < 0.2mm | 无需处理，持续观察 |
| 一般 | 🟡 黄色 | 0.2 - 0.5mm | 需关注，计划处理 |
| 严重 | 🟠 橙色 | 0.5 - 2mm | 需维修，尽快处理 |
| 危险 | 🔴 红色 | > 2mm | 需紧急处理 |

## 常见问题

### Q: 启动时 YOLO 模型下载很慢怎么办？

首次运行时，Ultralytics 会自动下载 `yolo11n.pt` 预训练模型（约 5.4MB）。如果下载缓慢，可以手动下载后放到项目根目录：

```
下载地址: https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo11n.pt
放置位置: g:\bangong\qiangtijiance\yolo11n.pt
```

### Q: 如何使用 GPU 加速检测？

确保已安装 CUDA 版本的 PyTorch：

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

YOLO 会自动检测并使用 GPU。

### Q: 预训练模型检测效果不好怎么办？

`yolo11n.pt` 是通用目标检测模型，对裂缝的识别能力有限。建议使用自定义训练的裂缝检测模型，详见 [自定义模型训练指南](docs/custom_model.md)。

### Q: QWEN-VL 分析失败怎么办？

1. 检查 `DASHSCOPE_API_KEY` 是否正确设置
2. 确认 DashScope 账户余额充足
3. 检查网络连接是否正常
4. 系统会自动回退到模拟分析模式

### Q: 如何修改服务端口？

编辑 `_run_server.py` 或 `app.py` 最后一行：

```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # 修改 port 为所需端口
```

### Q: 训练中断后如何恢复？

系统启动时自动将残留的 `running`/`pending` 状态修正为 `interrupted`。在训练页面点击「恢复训练」即可从 `last.pt` 检查点继续。

### Q: 如何测量裂缝的实际宽度？

在首页检测时调整「像素毫米比」参数（默认 5.0 px/mm）。该值取决于拍摄距离和相机参数。系统会自动在每个检测框下方标注 `W:宽度mm L:长度mm`。

### Q: 支持哪些标注格式？

- **内部格式**：YOLO（.txt 归一化坐标）
- **导入**：LabelMe JSON → 自动转换为 YOLO
- **导出**：YOLO / COCO / VOC / LabelMe
- 多边形标注自动保存为 `_shapes.json` 侧载文件，重新打开时恢复顶点

## 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 后端框架 | FastAPI | 0.115+ |
| 目标检测 | Ultralytics YOLO11 | 8.3+ |
| 视觉分析 | 阿里云 QWEN-VL (DashScope) | 1.20+ |
| 图像处理 | OpenCV | 4.8+ |
| 前端 | HTML / CSS / JavaScript | - |
| 服务器 | Uvicorn | 0.30+ |
| 标注工具 | 内置（矩形/多边形/LabelMe） | - |

## 许可证

本项目仅供学习和研究使用。
