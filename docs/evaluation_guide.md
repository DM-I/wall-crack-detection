# 模型评估模块使用指南

## 模型评估模块概述

模型评估模块用于对训练完成的 YOLO11 模型进行全面评估，提供多种评估指标、混淆矩阵、各类别分析以及多模型横向对比功能。系统还能根据评估结果自动生成优化建议，帮助用户迭代改进模型性能。

### 核心功能

| 功能 | 说明 |
|------|------|
| 模型评估 | 对指定模型在验证集/测试集上进行评估 |
| 评估指标 | mAP50、mAP50-95、Precision、Recall、F1 等 |
| 混淆矩阵 | 展示各类别的分类情况 |
| 各类别分析 | 每个类别的独立评估指标 |
| 模型对比 | 多个模型横向对比 |
| 优化建议 | 系统自动生成改进建议 |
| 评估管理 | 查看评估列表、删除评估记录 |

### 访问地址

评估模块页面：`http://localhost:8000/evaluation`

---

## 评估指标详解

### mAP50

**全称**：Mean Average Precision at IOU=0.5

**含义**：在 IOU 阈值为 0.5 时，所有类别平均精度的均值。即预测框与真实框的重叠度超过 50% 时视为正确检测。

**计算方式**：
1. 对每个类别，计算不同召回率下的精确率，得到 PR 曲线
2. 计算 PR 曲线下面积，得到该类别的 AP（Average Precision）
3. 对所有类别的 AP 取平均，得到 mAP50

**解读参考**：

| mAP50 范围 | 评价 | 说明 |
|------------|------|------|
| 0.9 - 1.0 | 优秀 | 模型检测能力极强 |
| 0.7 - 0.9 | 良好 | 模型可用于生产部署 |
| 0.5 - 0.7 | 一般 | 模型需要进一步优化 |
| 0.3 - 0.5 | 较差 | 建议增加数据或调整参数 |
| < 0.3 | 差 | 需要重新审视数据集和训练策略 |

### mAP50-95

**全称**：Mean Average Precision at IOU=0.5:0.95

**含义**：在 IOU 阈值从 0.5 到 0.95（步长 0.05）的 10 个阈值下，mAP 的平均值。该指标对检测框的定位精度要求更高。

**与 mAP50 的区别**：
- mAP50 只要求 50% 的重叠度，侧重"是否检测到"
- mAP50-95 要求更高的重叠度，侧重"检测框是否精准"
- mAP50-95 通常显著低于 mAP50

**解读参考**：

| mAP50-95 范围 | 评价 |
|---------------|------|
| > 0.6 | 优秀 |
| 0.4 - 0.6 | 良好 |
| 0.2 - 0.4 | 一般 |
| < 0.2 | 需要改进 |

### Precision（精确率）

**含义**：在所有预测为正样本的结果中，实际为正样本的比例。即"预测的裂缝中有多少是真正的裂缝"。

**公式**：Precision = TP / (TP + FP)

- TP（True Positive）：正确检测的裂缝数
- FP（False Positive）：误检数（将非裂缝检测为裂缝）

**解读**：
- 高精确率：误检少，检测结果可信度高
- 低精确率：误检多，存在大量假阳性

### Recall（召回率）

**含义**：在所有实际为正样本中，被正确预测为正样本的比例。即"实际的裂缝中有多少被检测到"。

**公式**：Recall = TP / (TP + FN)

- FN（False Negative）：漏检数（实际有裂缝但未检测到）

**解读**：
- 高召回率：漏检少，裂缝不易遗漏
- 低召回率：漏检多，存在安全隐患

### F1 分数

**含义**：精确率和召回率的调和平均值，综合衡量模型的检测能力。

**公式**：F1 = 2 × Precision × Recall / (Precision + Recall)

**解读**：

| F1 范围 | 评价 |
|---------|------|
| > 0.8 | 优秀 |
| 0.6 - 0.8 | 良好 |
| 0.4 - 0.6 | 一般 |
| < 0.4 | 需要改进 |

### 混淆矩阵

混淆矩阵展示了模型对每个类别的分类情况，是一个 N×N 的矩阵（N 为类别数）。

**矩阵结构**：

```
                 预测类别
                 横向  纵向  斜向  网状  裂缝  背景
实 横向裂缝  [  45    2    1    0    3    5  ]
际 纵向裂缝  [   1   38    0    0    2    4  ]
类 斜向裂缝  [   2    1   35    1    2    6  ]
别 网状裂缝  [   0    0    1   28    3    3  ]
   裂缝      [   3    2    2    1   30    7  ]
   背景      [   4    3    2    1    5   200 ]
```

**解读方法**：
- **对角线元素**：正确分类的数量，越大越好
- **非对角线元素**：错误分类的数量，越小越好
- **行方向**：该类别被错误分为其他类别的情况（漏检/误分类）
- **列方向**：其他类别被错误分为该类别的情况（误检）

**常见问题分析**：

| 现象 | 可能原因 | 解决方案 |
|------|---------|---------|
| 某类别行值分散 | 该类别特征不明显 | 增加该类别训练数据 |
| 某类别列值高 | 其他类别易被误分为该类 | 增加负样本、调整类别定义 |
| 背景列值高 | 误检严重 | 提高置信度阈值、增加负样本 |
| 背景行值高 | 漏检严重 | 降低置信度阈值、增加正样本 |

---

## 启动评估

### 界面操作

1. 打开评估模块页面 `http://localhost:8000/evaluation`
2. 在评估配置面板中：
   - 选择模型（预训练模型或训练完成的模型）
   - 选择数据集（需已完成分割）
   - 设置评估参数
3. 点击「开始评估」按钮
4. 系统执行模型评估
5. 评估完成后显示结果

### 参数设置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `model_path` | - | 模型文件路径（必填） |
| `dataset_id` | - | 数据集 ID（需已完成分割） |
| `conf` | 0.25 | 置信度阈值 |
| `iou` | 0.45 | NMS IOU 阈值 |
| `imgsz` | 640 | 评估时输入图片尺寸 |
| `batch_size` | 16 | 评估批次大小 |
| `split` | val | 评估使用的数据集分割（val/test） |

**split 参数说明**：

| 值 | 说明 | 适用场景 |
|----|------|---------|
| `val` | 使用验证集评估 | 训练过程中的常规评估 |
| `test` | 使用测试集评估 | 最终模型评估，结果更客观 |

> **建议**：训练过程中使用验证集评估，最终部署前使用测试集评估。

---

## 评估结果解读

### 指标含义

评估完成后，系统返回以下指标：

```json
{
  "metrics": {
    "mAP50": 0.8234,
    "mAP50-95": 0.5678,
    "precision": 0.8456,
    "recall": 0.7823,
    "f1": 0.8127,
    "fitness": 0.6132,
    "speed": {
      "preprocess": 0.52,
      "inference": 3.21,
      "postprocess": 0.38
    }
  }
}
```

| 字段 | 说明 |
|------|------|
| `mAP50` | IOU=0.5 时的平均精度均值 |
| `mAP50-95` | IOU=0.5:0.95 的平均精度均值 |
| `precision` | 精确率 |
| `recall` | 召回率 |
| `f1` | F1 分数 |
| `fitness` | 综合适应度指标（YOLO11 内部使用） |
| `speed.preprocess` | 预处理耗时（ms/image） |
| `speed.inference` | 推理耗时（ms/image） |
| `speed.postprocess` | 后处理耗时（ms/image） |

### 各类别分析

系统提供每个类别的独立评估指标：

```json
{
  "per_class_metrics": [
    {
      "class_id": 0,
      "mAP50": 0.8912,
      "mAP50-95": 0.6234,
      "precision": 0.9123,
      "recall": 0.8456
    },
    {
      "class_id": 1,
      "mAP50": 0.7856,
      "mAP50-95": 0.5123,
      "precision": 0.8234,
      "recall": 0.7123
    }
  ]
}
```

**各类别分析要点**：

1. **找出薄弱类别**：mAP50 最低的类别是最需要改进的
2. **分析原因**：
   - 精确率低 → 该类别误检多，可能是类别定义模糊
   - 召回率低 → 该类别漏检多，可能是训练样本不足
3. **针对性优化**：
   - 增加薄弱类别的训练数据
   - 检查该类别的标注质量
   - 考虑合并相似类别

### 评估输出目录

```
evaluation/eval_{eval_id}/
├── eval_info.json               # 评估信息
└── results/                     # YOLO11 评估输出
    ├── confusion_matrix.png     # 混淆矩阵图
    ├── confusion_matrix_normalized.png  # 归一化混淆矩阵
    ├── P_curve.png              # Precision 曲线
    ├── R_curve.png              # Recall 曲线
    ├── PR_curve.png             # PR 曲线
    ├── F1_curve.png             # F1 曲线
    └── ...
```

---

## 模型对比

### 多模型横向对比方法

系统支持对多个已完成的评估结果进行横向对比，帮助选择最优模型。

**界面操作**

1. 在评估列表中，勾选需要对比的评估记录（至少 2 个）
2. 点击「对比分析」按钮
3. 系统生成对比报告，包含：
   - 各模型指标对比表
   - 各类别指标对比
   - 最优模型推荐
   - 优化建议

### API 调用

```
POST /api/eval/compare
Content-Type: application/json
```

请求体：

```json
{
  "eval_ids": ["a1b2c3d4", "e5f6g7h8", "i9j0k1l2"]
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `eval_ids` | string[] | 是 | 评估 ID 列表，至少 2 个 |

请求示例：

```bash
curl -X POST http://localhost:8000/api/eval/compare \
  -H "Content-Type: application/json" \
  -d '{"eval_ids": ["a1b2c3d4", "e5f6g7h8"]}'
```

Python 示例：

```python
import requests

response = requests.post(
    "http://localhost:8000/api/eval/compare",
    json={"eval_ids": ["a1b2c3d4", "e5f6g7h8"]},
)
result = response.json()
print(f"最佳模型: {result['best_model']['model_path']}")
print(f"mAP50-95: {result['best_model']['metrics']['mAP50-95']}")
```

响应示例：

```json
{
  "comparisons": [
    {
      "eval_id": "a1b2c3d4",
      "model_path": "training/train_a1b2c3d4/best.pt",
      "metrics": {
        "mAP50": 0.8234,
        "mAP50-95": 0.5678,
        "precision": 0.8456,
        "recall": 0.7823,
        "f1": 0.8127
      },
      "per_class_metrics": [...]
    },
    {
      "eval_id": "e5f6g7h8",
      "model_path": "training/train_e5f6g7h8/best.pt",
      "metrics": {
        "mAP50": 0.7512,
        "mAP50-95": 0.4823,
        "precision": 0.8012,
        "recall": 0.7234,
        "f1": 0.7604
      },
      "per_class_metrics": [...]
    }
  ],
  "best_model": {
    "eval_id": "a1b2c3d4",
    "model_path": "training/train_a1b2c3d4/best.pt",
    "metrics": {
      "mAP50": 0.8234,
      "mAP50-95": 0.5678,
      "precision": 0.8456,
      "recall": 0.7823,
      "f1": 0.8127
    }
  },
  "recommendation": "最佳模型: best.pt，mAP50-95=0.5678；模型精度良好，可尝试微调以进一步提升"
}
```

---

## 优化建议

### 系统自动生成的建议说明

系统根据评估结果自动生成优化建议，逻辑如下：

**1. 基于 mAP50-95 的整体评价**

| mAP50-95 范围 | 系统建议 |
|---------------|---------|
| < 0.3 | 模型精度较低，建议增加训练数据量或调整超参数 |
| 0.3 - 0.5 | 模型精度一般，建议增加数据增强或调整学习率 |
| 0.5 - 0.7 | 模型精度良好，可尝试微调以进一步提升 |
| > 0.7 | 模型精度优秀，可用于生产部署 |

**2. 基于精确率的建议**

| Precision 范围 | 系统建议 |
|---------------|---------|
| < 0.5 | 精确率偏低，误检较多，建议提高置信度阈值或增加负样本 |

**3. 基于召回率的建议**

| Recall 范围 | 系统建议 |
|------------|---------|
| < 0.5 | 召回率偏低，漏检较多，建议降低置信度阈值或增加正样本 |

**4. 基于 F1 分数的建议**

| F1 范围 | 系统建议 |
|--------|---------|
| < 0.5 | F1分数偏低，精确率和召回率不均衡，建议调整检测阈值 |

---

## 评估与迭代优化流程

### 完整迭代流程

```
数据准备 → 模型训练 → 模型评估 → 分析结果 → 优化调整 → 重新训练
   ↑                                                    |
   └──────────── 评估结果不满足要求 ←────────────────────┘
```

### 详细步骤

**第一步：基线评估**

1. 使用默认参数训练初始模型
2. 在验证集上评估模型
3. 记录基线指标（mAP50、mAP50-95、Precision、Recall）

**第二步：分析评估结果**

1. 检查整体指标是否达标
2. 查看各类别指标，找出薄弱类别
3. 分析混淆矩阵，了解误分类模式
4. 查看系统优化建议

**第三步：针对性优化**

| 问题 | 优化方案 |
|------|---------|
| 整体精度低 | 增加训练数据、使用更大模型 |
| 某类别精度低 | 增加该类别数据、检查标注质量 |
| 精确率低 | 提高置信度阈值、增加负样本 |
| 召回率低 | 降低置信度阈值、增加正样本 |
| 过拟合 | 增大数据增强、减小模型、增大 weight_decay |
| 欠拟合 | 增大模型、增加训练轮数、减小正则化 |

**第四步：重新训练**

1. 根据优化方案调整训练参数或数据
2. 重新启动训练
3. 训练完成后再次评估

**第五步：模型对比**

1. 对比新旧模型的评估结果
2. 确认优化是否有效
3. 如果指标提升，继续迭代；如果下降，回退并尝试其他方案

**第六步：最终评估**

1. 在测试集上进行最终评估
2. 确认模型满足生产要求
3. 将 best.pt 复制到 `weights/` 目录部署

### 优化迭代记录模板

建议记录每次迭代的关键信息：

| 项目 | 内容 |
|------|------|
| 迭代版本 | v1 / v2 / v3 |
| 训练参数变更 | 如 lr0: 0.01→0.005 |
| 数据变更 | 如 新增200张标注图片 |
| mAP50 | 0.75 → 0.82 |
| mAP50-95 | 0.42 → 0.51 |
| Precision | 0.78 → 0.85 |
| Recall | 0.72 → 0.80 |
| 备注 | 如 "增加斜向裂缝样本后，该类别mAP提升显著" |

---

## API 参考

### 评估状态说明

| 状态值 | 说明 |
|--------|------|
| `pending` | 评估任务已创建，等待启动 |
| `running` | 评估进行中 |
| `completed` | 评估已完成 |
| `failed` | 评估失败 |
| `interrupted` | 服务重启导致评估中断 |

> **关于 `interrupted` 状态**：评估在请求线程中同步执行。当服务在评估过程中重启时，`eval_info.json` 可能残留 `running`/`pending` 状态。系统在每次启动时会自动扫描所有评估记录，将残留状态修正为 `interrupted`。

### 评估管理

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/api/eval/start` | 启动评估 |
| `GET` | `/api/eval/list` | 获取评估列表 |
| `GET` | `/api/eval/{eval_id}` | 获取评估详情 |
| `DELETE` | `/api/eval/{eval_id}` | 删除评估 |
| `POST` | `/api/eval/compare` | 模型对比 |

### 启动评估

```
POST /api/eval/start
Content-Type: multipart/form-data
```

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `model_path` | string | 是 | - | 模型文件路径 |
| `dataset_id` | string | 否 | - | 数据集 ID |
| `conf` | float | 否 | 0.25 | 置信度阈值 |
| `iou` | float | 否 | 0.45 | NMS IOU 阈值 |
| `imgsz` | int | 否 | 640 | 输入图片尺寸 |
| `batch_size` | int | 否 | 16 | 评估批次大小 |
| `split` | string | 否 | val | 评估数据集分割（val/test） |

请求示例：

```bash
curl -X POST http://localhost:8000/api/eval/start \
  -F "model_path=training/train_a1b2c3d4/best.pt" \
  -F "dataset_id=f00464ee" \
  -F "conf=0.25" \
  -F "iou=0.45" \
  -F "split=test"
```

Python 示例：

```python
import requests

response = requests.post(
    "http://localhost:8000/api/eval/start",
    data={
        "model_path": "training/train_a1b2c3d4/best.pt",
        "dataset_id": "f00464ee",
        "conf": 0.25,
        "iou": 0.45,
        "imgsz": 640,
        "batch_size": 16,
        "split": "test",
    },
)
result = response.json()
eval_info = result["evaluation"]
print(f"评估ID: {eval_info['eval_id']}")
print(f"状态: {eval_info['status']}")
```

响应示例：

```json
{
  "success": true,
  "evaluation": {
    "eval_id": "i9j0k1l2",
    "model_path": "training/train_a1b2c3d4/best.pt",
    "dataset_id": "f00464ee",
    "yaml_path": "G:\\bangong\\qiangtijiance\\datasets\\f00464ee\\data.yaml",
    "conf": 0.25,
    "iou": 0.45,
    "imgsz": 640,
    "batch_size": 16,
    "split": "test",
    "status": "completed",
    "started_at": "2026-05-22 14:00:00",
    "completed_at": "2026-05-22 14:05:00",
    "results": {
      "metrics": {
        "mAP50": 0.8234,
        "mAP50-95": 0.5678,
        "precision": 0.8456,
        "recall": 0.7823,
        "f1": 0.8127,
        "fitness": 0.6132,
        "speed": {
          "preprocess": 0.52,
          "inference": 3.21,
          "postprocess": 0.38
        }
      },
      "confusion_matrix": [[45, 2, 1, 0, 3, 5], [1, 38, 0, 0, 2, 4], ...],
      "per_class_metrics": [
        {"class_id": 0, "mAP50": 0.8912, "mAP50-95": 0.6234, "precision": 0.9123, "recall": 0.8456},
        {"class_id": 1, "mAP50": 0.7856, "mAP50-95": 0.5123, "precision": 0.8234, "recall": 0.7123}
      ]
    }
  }
}
```

### 获取评估列表

```
GET /api/eval/list
```

响应示例：

```json
{
  "evaluations": [
    {
      "eval_id": "i9j0k1l2",
      "model_path": "training/train_a1b2c3d4/best.pt",
      "dataset_id": "f00464ee",
      "status": "completed",
      "started_at": "2026-05-22 14:00:00",
      "completed_at": "2026-05-22 14:05:00"
    }
  ]
}
```

### 获取评估详情

```
GET /api/eval/{eval_id}
```

### 删除评估

```
DELETE /api/eval/{eval_id}
```

### 模型对比

```
POST /api/eval/compare
Content-Type: application/json
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `eval_ids` | string[] | 是 | 评估 ID 列表，至少 2 个 |
