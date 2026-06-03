# 模型训练模块使用指南

## 模型训练模块概述

模型训练模块基于 Ultralytics YOLO11 框架，提供从数据集准备到模型训练的完整流程。系统支持在 Web 界面或通过 API 启动训练任务，实时监控训练进度，并自动保存训练结果和权重文件。训练过程在后台线程中异步执行，不影响系统的其他功能。

### 核心功能

| 功能 | 说明 |
|------|------|
| 训练启动 | Web 界面或 API 启动训练任务 |
| 参数配置 | 丰富的训练参数设置 |
| 实时监控 | 训练进度、Loss 曲线、mAP 曲线 |
| 训练管理 | 查看训练列表、停止训练、删除训练 |
| 权重管理 | 自动保存 best.pt 和 last.pt |
| 模型选择 | 预训练模型和自定义模型 |

### 访问地址

训练模块页面：`http://localhost:8000/training`

---

## 训练前准备

### 数据集要求

在启动训练之前，需确保数据集满足以下条件：

| 项目 | 要求 |
|------|------|
| 数据集已创建 | 通过标注模块创建数据集 |
| 图片已上传 | 至少上传 50 张以上标注图片 |
| 标注已完成 | 每张图片至少有 1 个标注框 |
| 数据集已分割 | 已执行训练/验证/测试集分割 |
| data.yaml 已生成 | 分割后自动生成 |

### data.yaml 配置

数据集分割后自动生成 `data.yaml` 配置文件，这是训练的必要文件。示例：

```yaml
path: G:\bangong\qiangtijiance\datasets\f00464ee
train: images/train
val: images/val
test: images/test

nc: 5
names: {"0": "横向裂缝", "1": "纵向裂缝", "2": "斜向裂缝", "3": "网状裂缝", "4": "裂缝"}
```

| 字段 | 说明 |
|------|------|
| `path` | 数据集根目录的绝对路径 |
| `train` | 训练集图片目录（相对于 path） |
| `val` | 验证集图片目录（相对于 path） |
| `test` | 测试集图片目录（相对于 path） |
| `nc` | 类别数量（number of classes） |
| `names` | 类别 ID 到名称的映射 |

> **注意**：如果未执行数据集分割，训练将无法启动，系统会提示"数据集未分割，请先执行数据集分割操作"。

### 数据集质量检查清单

- [ ] 训练集图片数量 ≥ 100 张（推荐 ≥ 500 张）
- [ ] 验证集图片数量 ≥ 20 张（推荐 ≥ 100 张）
- [ ] 每个类别至少有 30 个标注实例
- [ ] 标注框紧贴目标，无过大或过小的框
- [ ] 图片场景具有多样性（不同光照、角度、材质）
- [ ] 无损坏或无法读取的图片文件

---

## 训练参数详解

### 基础参数

| 参数 | 默认值 | 范围 | 说明 |
|------|--------|------|------|
| `model` | yolo11n.pt | - | 预训练模型路径或名称 |
| `epochs` | 100 | 10-500 | 训练轮数，整个数据集训练一遍为一个 epoch |
| `batch_size` | 16 | 1-128 | 批次大小，每次训练处理的图片数量 |
| `imgsz` | 640 | 320-1280 | 输入图片尺寸，训练时统一缩放到此尺寸 |
| `patience` | 50 | 10-100 | 早停耐心值，验证集指标连续 N 轮无提升则停止 |
| `save_period` | -1 | -1/正整数 | 每 N 个 epoch 保存一次检查点，-1 表示仅保存 best 和 last |

**参数选择建议**

| 场景 | epochs | batch_size | imgsz | patience |
|------|--------|------------|-------|----------|
| 快速试验 | 30 | 16 | 640 | 20 |
| 常规训练 | 100 | 16 | 640 | 50 |
| 精细训练 | 200 | 8 | 1280 | 80 |
| 大数据集 | 50 | 32 | 640 | 30 |

**batch_size 调整指南**

| GPU 显存 | 推荐 batch_size |
|----------|----------------|
| 4GB | 4-8 |
| 6GB | 8-16 |
| 8GB | 16 |
| 12GB | 16-32 |
| 24GB | 32-64 |

如果训练时出现 CUDA Out of Memory 错误，请减小 batch_size。

### 模型规模选择

| 模型 | 参数量 | 推理速度 | 精度 | 适用场景 |
|------|--------|---------|------|---------|
| `yolo11n.pt` | 2.6M | 最快 | 一般 | 实时检测、边缘设备 |
| `yolo11s.pt` | 9.4M | 快 | 较好 | 平衡速度与精度 |
| `yolo11m.pt` | 20.1M | 中等 | 好 | 服务器部署 |
| `yolo11l.pt` | 25.3M | 较慢 | 很好 | 高精度需求 |
| `yolo11x.pt` | 56.9M | 最慢 | 最好 | 追求极致精度 |

### 学习率参数

| 参数 | 默认值 | 范围 | 说明 |
|------|--------|------|------|
| `lr0` | 0.01 | 0.0001-0.1 | 初始学习率，控制参数更新的步长 |
| `lrf` | 0.01 | 0.01-1.0 | 最终学习率因子，最终学习率 = lr0 × lrf |
| `warmup_epochs` | 3 | 0-10 | 学习率预热轮数，从低学习率逐渐增大到 lr0 |
| `warmup_momentum` | 0.8 | 0-1 | 预热阶段的动量值 |
| `warmup_bias_lr` | 0.1 | 0-1 | 预热阶段的偏置学习率 |
| `momentum` | 0.937 | 0.5-0.999 | SGD 动量，加速收敛并减少震荡 |
| `weight_decay` | 0.0005 | 0-0.01 | 权重衰减（L2 正则化），防止过拟合 |

**学习率调优建议**

| 场景 | lr0 | lrf | 说明 |
|------|-----|-----|------|
| 从零训练 | 0.01 | 0.01 | 默认值，适用于大多数情况 |
| 微调训练 | 0.001 | 0.1 | 小学习率避免遗忘已学特征 |
| 大数据集 | 0.01 | 0.01 | 数据充足，可用较大学习率 |
| 小数据集 | 0.005 | 0.05 | 小学习率防止过拟合 |

**学习率调度说明**

训练过程中学习率的变化：

```
lr0 ──→ warmup ──→ lr0 ──→ cosine decay ──→ lr0 × lrf
         (3 epochs)     (训练主体)           (训练结束)
```

- **Warmup 阶段**：前 `warmup_epochs` 轮，学习率从 0 线性增长到 `lr0`，避免训练初期不稳定
- **Cosine Decay 阶段**：学习率按余弦曲线从 `lr0` 衰减到 `lr0 × lrf`，平滑降低学习率

### 损失权重参数

| 参数 | 默认值 | 范围 | 说明 |
|------|--------|------|------|
| `box` | 7.5 | 1-20 | 边界框损失权重，控制定位精度的重要性 |
| `cls` | 0.5 | 0.1-5 | 分类损失权重，控制类别分类的重要性 |
| `dfl` | 1.5 | 0.5-5 | 分布焦点损失权重，控制边界框分布回归的精度 |
| `label_smoothing` | 0.0 | 0-0.1 | 标签平滑系数，防止模型对训练标签过度自信 |
| `nbs` | 64 | 16-128 | 名义批次大小，用于损失归一化 |

**损失权重调优建议**

| 问题 | 调整方案 |
|------|---------|
| 检测框不够精准 | 增大 `box`（如 10.0） |
| 类别分类错误多 | 增大 `cls`（如 1.0） |
| 小目标检测差 | 增大 `box` 和 `dfl` |
| 模型过拟合 | 增大 `label_smoothing`（如 0.05） |

### 数据增强参数

| 参数 | 默认值 | 范围 | 说明 |
|------|--------|------|------|
| `hsv_h` | 0.015 | 0-1 | 色调增强幅度，模拟不同光照色温 |
| `hsv_s` | 0.7 | 0-1 | 饱和度增强幅度，模拟不同材质表面 |
| `hsv_v` | 0.4 | 0-1 | 明度增强幅度，模拟不同光照强度 |
| `degrees` | 0.0 | 0-45 | 随机旋转角度范围（度） |
| `translate` | 0.1 | 0-0.5 | 随机平移幅度（相对于图片尺寸） |
| `scale` | 0.5 | 0-1 | 随机缩放幅度，模拟不同拍摄距离 |
| `shear` | 0.0 | 0-20 | 随机剪切角度（度） |
| `perspective` | 0.0 | 0-0.001 | 随机透视变换幅度 |
| `flipud` | 0.0 | 0-1 | 上下翻转概率 |
| `fliplr` | 0.5 | 0-1 | 左右翻转概率 |
| `mosaic` | 1.0 | 0-1 | Mosaic 增强概率，将 4 张图拼接为 1 张 |
| `mixup` | 0.0 | 0-1 | MixUp 增强概率，将两张图混合 |
| `copy_paste` | 0.0 | 0-1 | 复制粘贴增强概率，将目标复制到其他位置 |

**裂缝检测推荐增强策略**

```python
{
    "hsv_h": 0.015,
    "hsv_s": 0.7,
    "hsv_v": 0.4,
    "degrees": 15.0,
    "translate": 0.1,
    "scale": 0.5,
    "shear": 0.0,
    "perspective": 0.0,
    "flipud": 0.5,
    "fliplr": 0.5,
    "mosaic": 1.0,
    "mixup": 0.0,
    "copy_paste": 0.0
}
```

**增强参数调优建议**

| 场景 | 推荐调整 |
|------|---------|
| 光照变化大 | 增大 `hsv_v`（0.5-0.6） |
| 裂缝方向多变 | 增大 `degrees`（10-30） |
| 拍摄距离不固定 | 增大 `scale`（0.5-0.9） |
| 数据量少 | 开启 `mosaic`（1.0）和 `mixup`（0.1） |
| 小目标多 | 增大 `mosaic`，减小 `scale` |
| 过拟合严重 | 增大所有增强幅度 |

---

## 启动训练

### 界面操作

1. 打开训练模块页面 `http://localhost:8000/training`
2. 在训练配置面板中：
   - 选择数据集（需已完成分割）
   - 选择预训练模型（如 `yolo11n.pt`）
   - 配置训练参数
3. 点击「开始训练」按钮
4. 系统在后台启动训练线程
5. 页面自动跳转到训练监控界面

### API 调用

```
POST /api/train/start
Content-Type: multipart/form-data
```

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `dataset_id` | string | 是 | - | 数据集 ID |
| `model` | string | 否 | yolo11n.pt | 预训练模型名称或路径 |
| `epochs` | int | 否 | 100 | 训练轮数 |
| `batch_size` | int | 否 | 16 | 批次大小 |
| `imgsz` | int | 否 | 640 | 输入图片尺寸 |
| `patience` | int | 否 | 50 | 早停耐心值 |
| `lr0` | float | 否 | 0.01 | 初始学习率 |
| `lrf` | float | 否 | 0.01 | 最终学习率因子 |
| `momentum` | float | 否 | 0.937 | 动量 |
| `weight_decay` | float | 否 | 0.0005 | 权重衰减 |
| `warmup_epochs` | int | 否 | 3 | 预热轮数 |
| `warmup_momentum` | float | 否 | 0.8 | 预热动量 |
| `warmup_bias_lr` | float | 否 | 0.1 | 预热偏置学习率 |
| `box` | float | 否 | 7.5 | 边界框损失权重 |
| `cls` | float | 否 | 0.5 | 分类损失权重 |
| `dfl` | float | 否 | 1.5 | 分布焦点损失权重 |
| `label_smoothing` | float | 否 | 0.0 | 标签平滑 |
| `nbs` | int | 否 | 64 | 名义批次大小 |
| `hsv_h` | float | 否 | 0.015 | 色调增强 |
| `hsv_s` | float | 否 | 0.7 | 饱和度增强 |
| `hsv_v` | float | 否 | 0.4 | 明度增强 |
| `degrees` | float | 否 | 0.0 | 旋转角度 |
| `translate` | float | 否 | 0.1 | 平移幅度 |
| `scale` | float | 否 | 0.5 | 缩放幅度 |
| `shear` | float | 否 | 0.0 | 剪切角度 |
| `perspective` | float | 否 | 0.0 | 透视变换 |
| `flipud` | float | 否 | 0.0 | 上下翻转概率 |
| `fliplr` | float | 否 | 0.5 | 左右翻转概率 |
| `mosaic` | float | 否 | 1.0 | Mosaic 增强 |
| `mixup` | float | 否 | 0.0 | MixUp 增强 |
| `copy_paste` | float | 否 | 0.0 | 复制粘贴增强 |
| `save_period` | int | 否 | -1 | 检查点保存周期 |

请求示例：

```bash
curl -X POST http://localhost:8000/api/train/start \
  -F "dataset_id=f00464ee" \
  -F "model=yolo11s.pt" \
  -F "epochs=100" \
  -F "batch_size=16" \
  -F "imgsz=640" \
  -F "lr0=0.01" \
  -F "patience=50"
```

Python 示例：

```python
import requests

response = requests.post(
    "http://localhost:8000/api/train/start",
    data={
        "dataset_id": "f00464ee",
        "model": "yolo11s.pt",
        "epochs": 100,
        "batch_size": 16,
        "imgsz": 640,
        "lr0": 0.01,
        "patience": 50,
        "degrees": 15.0,
        "flipud": 0.5,
        "fliplr": 0.5,
        "mosaic": 1.0,
    },
)
result = response.json()
print(f"训练ID: {result['training']['training_id']}")
print(f"状态: {result['training']['status']}")
```

响应示例：

```json
{
  "success": true,
  "training": {
    "training_id": "a1b2c3d4",
    "dataset_id": "f00464ee",
    "run_name": "train_a1b2c3d4",
    "config": {
      "epochs": 100,
      "batch_size": 16,
      "imgsz": 640,
      "lr0": 0.01,
      "model": "yolo11s.pt"
    },
    "status": "pending",
    "started_at": "2026-05-22 10:00:00",
    "completed_at": null,
    "project_dir": "G:\\bangong\\qiangtijiance\\training\\train_a1b2c3d4",
    "yaml_path": "G:\\bangong\\qiangtijiance\\datasets\\f00464ee\\data.yaml",
    "results": null,
    "error": null
  }
}
```

---

## 训练监控

### 实时进度

训练启动后，可通过以下 API 获取实时进度：

```
GET /api/train/progress/{training_id}
```

响应示例：

```json
{
  "epochs_completed": 45,
  "total_epochs": 100,
  "metrics": [
    {
      "epoch": 45,
      "train/box_loss": "0.04523",
      "train/cls_loss": "0.8912",
      "train/dfl_loss": "1.0234",
      "val/box_loss": "0.05123",
      "val/cls_loss": "0.9234",
      "val/dfl_loss": "1.1234",
      "metrics/precision(B)": "0.8456",
      "metrics/recall(B)": "0.7823",
      "metrics/mAP50(B)": "0.8234",
      "metrics/mAP50-95(B)": "0.5678",
      "lr/pg0": "0.00543"
    }
  ]
}
```

### 训练曲线说明

系统通过以下 API 获取训练曲线数据：

```
GET /api/train/curves/{training_id}
```

返回的数据可用于绘制以下训练曲线：

### Loss 曲线

训练过程中有 3 组 Loss 曲线，分别对应 YOLO11 的 3 个损失函数：

**1. Box Loss（边界框损失）**

- `train_box_loss`：训练集边界框损失
- `val_box_loss`：验证集边界框损失
- 含义：衡量预测边界框与真实框的偏差
- 期望趋势：持续下降并趋于稳定
- 异常信号：验证集 loss 上升 → 过拟合

**2. Class Loss（分类损失）**

- `train_cls_loss`：训练集分类损失
- `val_cls_loss`：验证集分类损失
- 含义：衡量类别预测的准确性
- 期望趋势：持续下降并趋于稳定
- 异常信号：验证集 loss 上升 → 过拟合

**3. DFL Loss（分布焦点损失）**

- `train_dfl_loss`：训练集 DFL 损失
- `val_dfl_loss`：验证集 DFL 损失
- 含义：衡量边界框分布回归的精度
- 期望趋势：持续下降并趋于稳定

### mAP 曲线

**1. Precision（精确率）曲线**

- 含义：预测为正样本中实际为正样本的比例
- 期望趋势：逐步上升并趋于稳定
- 典型值：0.7-0.95

**2. Recall（召回率）曲线**

- 含义：实际为正样本中被正确预测的比例
- 期望趋势：逐步上升并趋于稳定
- 典型值：0.6-0.9

**3. mAP50 曲线**

- 含义：IOU=0.5 时的平均精度均值
- 期望趋势：逐步上升
- 良好值：> 0.7
- 优秀值：> 0.85

**4. mAP50-95 曲线**

- 含义：IOU 从 0.5 到 0.95（步长 0.05）的平均精度均值
- 期望趋势：逐步上升
- 良好值：> 0.4
- 优秀值：> 0.6

### 学习率曲线

- `lr`：当前学习率
- 期望趋势：Warmup 阶段线性上升，之后余弦衰减

### 训练状态查询

```
GET /api/train/status/{training_id}
```

训练状态值：

| 状态 | 说明 |
|------|------|
| `pending` | 训练任务已创建，等待启动 |
| `running` | 训练进行中 |
| `completed` | 训练已完成 |
| `failed` | 训练失败 |
| `stopped` | 训练被手动停止 |
| `interrupted` | 服务重启导致训练中断（可通过恢复训练继续） |

> **关于 `interrupted` 状态**：训练在后台线程中执行。当服务重启时，线程随进程终止，但磁盘上的 `training_info.json` 可能残留 `running` 状态。系统在每次启动时会自动扫描所有训练记录，将 `running`/`pending` 状态修正为 `interrupted`，避免前端误显示"训练中"。已中断的训练可通过 **恢复训练** 功能从 `last.pt` 检查点继续。

---

## 训练结果

### 权重文件说明

训练完成后，系统在 `training/train_{training_id}/` 目录下保存以下权重文件：

| 文件 | 说明 |
|------|------|
| `best.pt` | 验证集 mAP50-95 最高的模型权重 |
| `last.pt` | 最后一个 epoch 的模型权重 |

此外，YOLO11 框架在 `training/train_{training_id}/weights/weights/` 目录下也保存了原始权重文件，系统会自动复制到上层目录。

### best.pt vs last.pt

| 对比项 | best.pt | last.pt |
|--------|---------|---------|
| 选择标准 | 验证集 mAP50-95 最高 | 最后一个 epoch |
| 推荐用途 | 生产部署 | 继续训练（断点续训） |
| 精度 | 通常更高 | 可能不如 best |
| 使用场景 | 模型评估、部署 | 训练中断后恢复 |

> **建议**：部署时始终使用 `best.pt`，而非 `last.pt`。

### 训练输出目录结构

```
training/train_{training_id}/
├── best.pt                          # 最优权重（复制）
├── last.pt                          # 末轮权重（复制）
├── training_info.json               # 训练信息
└── weights/                         # YOLO11 原始输出
    ├── weights/
    │   ├── best.pt                  # 最优权重（原始）
    │   └── last.pt                  # 末轮权重（原始）
    ├── results.csv                  # 训练指标数据
    ├── results.png                  # 训练曲线图
    ├── confusion_matrix.png         # 混淆矩阵
    ├── labels.jpg                   # 标签分布图
    ├── labels_correlogram.jpg       # 标签相关图
    ├── P_curve.png                  # Precision 曲线
    ├── R_curve.png                  # Recall 曲线
    ├── PR_curve.png                 # PR 曲线
    └── F1_curve.png                 # F1 曲线
```

### training_info.json

训练信息文件记录了完整的训练配置和结果：

```json
{
  "training_id": "a1b2c3d4",
  "dataset_id": "f00464ee",
  "run_name": "train_a1b2c3d4",
  "config": {
    "epochs": 100,
    "batch_size": 16,
    "imgsz": 640,
    "lr0": 0.01,
    "model": "yolo11s.pt"
  },
  "status": "completed",
  "started_at": "2026-05-22 10:00:00",
  "completed_at": "2026-05-22 12:30:00",
  "project_dir": "G:\\bangong\\qiangtijiance\\training\\train_a1b2c3d4",
  "results": {
    "best_weight": "G:\\bangong\\qiangtijiance\\training\\train_a1b2c3d4\\best.pt",
    "last_weight": "G:\\bangong\\qiangtijiance\\training\\train_a1b2c3d4\\last.pt",
    "metrics": {
      "best_epoch": {"epoch": "85", "metrics/mAP50-95(B)": "0.5678"},
      "last_epoch": {"epoch": "100", "metrics/mAP50-95(B)": "0.5432"}
    }
  }
}
```

---

## 训练技巧

### 超参数调优建议

**1. 学习率调优**

学习率是最重要的超参数。推荐使用学习率查找方法：

- 从 `lr0=0.01` 开始（默认值）
- 如果训练初期 loss 震荡剧烈，降低到 `0.001`
- 如果 loss 下降过慢，增大到 `0.02`
- 微调已有模型时，使用 `lr0=0.001`

**2. 早停策略**

- 默认 `patience=50`，即验证集指标 50 轮无提升则停止
- 小数据集建议 `patience=30`，避免过拟合
- 大数据集可设 `patience=80`，给模型更多收敛机会

**3. 数据增强调优**

- 数据量少（< 200 张）：增大增强幅度，开启 mosaic 和 mixup
- 数据量中等（200-1000 张）：使用默认增强参数
- 数据量大（> 1000 张）：可适当减小增强幅度
- 裂缝方向多变：增大 `degrees`（10-30）和翻转概率

**4. 模型选择**

- 数据量少（< 200 张）：使用 `yolo11n.pt`，避免大模型过拟合
- 数据量中等（200-1000 张）：使用 `yolo11s.pt`
- 数据量大（> 1000 张）：使用 `yolo11m.pt` 或 `yolo11l.pt`
- 追求推理速度：使用 `yolo11n.pt`
- 追求精度：使用 `yolo11l.pt` 或 `yolo11x.pt`

### 常见问题解决

**1. CUDA Out of Memory**

```
RuntimeError: CUDA out of memory
```

解决方案：
- 减小 `batch_size`（如 16 → 8 → 4）
- 减小 `imgsz`（如 640 → 480）
- 使用更小的模型（如 yolo11m → yolo11s）

**2. 训练 loss 不下降**

可能原因及解决方案：
- 学习率过大：降低 `lr0`（如 0.01 → 0.001）
- 数据标注质量差：检查并修正标注
- 数据集太小：增加训练数据
- 模型太大导致过拟合：使用更小的模型

**3. 验证集 loss 上升（过拟合）**

解决方案：
- 增大数据增强幅度
- 减小模型规模
- 增大 `weight_decay`（如 0.0005 → 0.001）
- 开启 `label_smoothing`（如 0.05）
- 增加训练数据量
- 减小训练轮数

**4. mAP 值很低**

可能原因及解决方案：
- 标注质量差：检查标注框是否紧贴目标
- 类别定义不合理：合并相似类别或拆分模糊类别
- 数据集太小：增加训练数据
- 数据分布不均：确保各类别样本均衡
- 图片分辨率太低：使用更高分辨率的图片

**5. 训练速度慢**

解决方案：
- 确认使用了 GPU（检查 CUDA 是否可用）
- 增大 `batch_size`（在显存允许范围内）
- 减小 `imgsz`
- 使用更小的模型

**6. 数据集未分割错误**

```
{"error": "数据集未分割，请先执行数据集分割操作"}
```

解决方案：
- 在标注模块中执行数据集分割操作
- 确认 `data.yaml` 文件已生成

---

## API 参考

### 训练管理

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/api/train/start` | 启动训练 |
| `GET` | `/api/train/status/{training_id}` | 获取训练状态 |
| `GET` | `/api/train/progress/{training_id}` | 获取训练进度 |
| `GET` | `/api/train/curves/{training_id}` | 获取训练曲线数据 |
| `POST` | `/api/train/stop/{training_id}` | 停止训练 |
| `POST` | `/api/train/resume/{training_id}` | 恢复已中断的训练 |
| `GET` | `/api/train/list` | 获取训练列表 |
| `DELETE` | `/api/train/{training_id}` | 删除训练 |
| `GET` | `/api/train/models` | 获取可用模型列表 |

### 启动训练参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `dataset_id` | string | 是 | - | 数据集 ID |
| `model` | string | 否 | yolo11n.pt | 模型名称或路径 |
| `epochs` | int | 否 | 100 | 训练轮数 |
| `batch_size` | int | 否 | 16 | 批次大小 |
| `imgsz` | int | 否 | 640 | 输入图片尺寸 |
| `patience` | int | 否 | 50 | 早停耐心值 |
| `lr0` | float | 否 | 0.01 | 初始学习率 |
| `lrf` | float | 否 | 0.01 | 最终学习率因子 |
| `momentum` | float | 否 | 0.937 | 动量 |
| `weight_decay` | float | 否 | 0.0005 | 权重衰减 |
| `warmup_epochs` | int | 否 | 3 | 预热轮数 |
| `warmup_momentum` | float | 否 | 0.8 | 预热动量 |
| `warmup_bias_lr` | float | 否 | 0.1 | 预热偏置学习率 |
| `box` | float | 否 | 7.5 | 边界框损失权重 |
| `cls` | float | 否 | 0.5 | 分类损失权重 |
| `dfl` | float | 否 | 1.5 | 分布焦点损失权重 |
| `label_smoothing` | float | 否 | 0.0 | 标签平滑 |
| `nbs` | int | 否 | 64 | 名义批次大小 |
| `hsv_h` | float | 否 | 0.015 | 色调增强 |
| `hsv_s` | float | 否 | 0.7 | 饱和度增强 |
| `hsv_v` | float | 否 | 0.4 | 明度增强 |
| `degrees` | float | 否 | 0.0 | 旋转角度 |
| `translate` | float | 否 | 0.1 | 平移幅度 |
| `scale` | float | 否 | 0.5 | 缩放幅度 |
| `shear` | float | 否 | 0.0 | 剪切角度 |
| `perspective` | float | 否 | 0.0 | 透视变换 |
| `flipud` | float | 否 | 0.0 | 上下翻转概率 |
| `fliplr` | float | 否 | 0.5 | 左右翻转概率 |
| `mosaic` | float | 否 | 1.0 | Mosaic 增强 |
| `mixup` | float | 否 | 0.0 | MixUp 增强 |
| `copy_paste` | float | 否 | 0.0 | 复制粘贴增强 |
| `save_period` | int | 否 | -1 | 检查点保存周期 |

### 停止训练

```
POST /api/train/stop/{training_id}
```

响应示例：

```json
{
  "success": true,
  "training_id": "a1b2c3d4"
}
```

### 获取可用模型

```
GET /api/train/models
```

响应示例：

```json
{
  "models": [
    {
      "name": "best.pt",
      "path": "G:\\bangong\\qiangtijiance\\weights\\best.pt",
      "type": "custom"
    },
    {
      "name": "yolo11n.pt",
      "path": "yolo11n.pt",
      "type": "pretrained"
    },
    {
      "name": "train_a1b2c3d4/best.pt",
      "path": "G:\\bangong\\qiangtijiance\\training\\train_a1b2c3d4\\best.pt",
      "type": "trained"
    }
  ]
}
```

| 模型类型 | 说明 |
|---------|------|
| `custom` | 用户放置在 `weights/` 目录的自定义模型 |
| `pretrained` | YOLO11 预训练模型（首次使用自动下载） |
| `trained` | 通过本系统训练得到的模型 |
