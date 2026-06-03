# 自定义模型训练指南

系统默认使用 `yolo11n.pt` 通用目标检测模型，该模型并非针对裂缝检测训练，检测效果有限。为获得更好的裂缝检测效果，建议使用自定义训练的 YOLO11 裂缝检测模型。

## 1. 数据集准备

### 1.1 数据集结构

推荐使用 YOLO 格式组织数据集：

```
crack_dataset/
├── images/
│   ├── train/
│   │   ├── img_0001.jpg
│   │   ├── img_0002.jpg
│   │   └── ...
│   ├── val/
│   │   ├── img_1001.jpg
│   │   ├── img_1002.jpg
│   │   └── ...
│   └── test/
│       ├── img_2001.jpg
│       └── ...
└── labels/
    ├── train/
    │   ├── img_0001.txt
    │   ├── img_0002.txt
    │   └── ...
    ├── val/
    │   ├── img_1001.txt
    │   └── ...
    └── test/
        ├── img_2001.txt
        └── ...
```

### 1.2 标注格式（YOLO 格式）

每张图片对应一个同名的 `.txt` 标注文件，每行一个目标：

```
class_id center_x center_y width height
```

所有坐标均为归一化值（0-1），相对于图片尺寸。

**示例**：

```
0 0.4523 0.3125 0.2340 0.0567
1 0.6789 0.5432 0.0890 0.3456
```

### 1.3 推荐的裂缝类别定义

| class_id | 类别名称 | 说明 |
|----------|---------|------|
| 0 | 横向裂缝 | 裂缝走向近似水平 |
| 1 | 纵向裂缝 | 裂缝走向近似垂直 |
| 2 | 斜向裂缝 | 裂缝走向倾斜 |
| 3 | 网状裂缝 | 多条裂缝交叉形成网状 |
| 4 | 裂缝 | 无法明确分类的裂缝 |

> 类别定义需与 `config.py` 中的 `CRACK_CLASSES` 保持一致。

### 1.4 数据集要求

| 项目 | 建议 |
|------|------|
| 图片数量 | 训练集 ≥ 500 张，验证集 ≥ 100 张 |
| 图片分辨率 | 640×640 以上 |
| 标注质量 | 边界框紧贴裂缝，避免过大或过小 |
| 场景多样性 | 包含不同光照、角度、墙体材质 |
| 正负样本比 | 建议含裂缝图片占 70%，无裂缝图片占 30% |

### 1.5 公开裂缝数据集

可使用以下公开数据集进行训练或预训练：

| 数据集 | 说明 | 链接 |
|--------|------|------|
| CRACK500 | 500 张路面裂缝图片 | [GitHub](https://github.com/fyangneil pavement-crack-detection) |
| DeepCrack | 300 张细裂缝图片 | [GitHub](https://github.com/qinnzou/DeepCrack) |
| CFD | 混凝土裂缝图片集 | [GitHub](https://github.com/cuilimeng/CRack-detection-dataset) |
| Rissbilder | 墙体裂缝图片集 | 学术数据集 |

## 2. 数据集配置文件

创建 `crack.yaml` 数据集配置文件：

```yaml
path: D:/datasets/crack_dataset    # 数据集根目录（绝对路径）
train: images/train                 # 训练图片目录（相对于 path）
val: images/val                     # 验证图片目录
test: images/test                   # 测试图片目录（可选）

# 类别定义
names:
    0: 横向裂缝
    1: 纵向裂缝
    2: 斜向裂缝
    3: 网状裂缝
    4: 裂缝
```

## 3. 模型训练

### 3.1 基础训练命令

```bash
yolo detect train \
    model=yolo11n.pt \
    data=crack.yaml \
    epochs=100 \
    imgsz=640 \
    batch=16 \
    project=crack_detection \
    name=train_v1
```

### 3.2 训练参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `model` | - | 预训练模型路径，`yolo11n.pt` 为 nano 版本 |
| `data` | - | 数据集配置文件路径 |
| `epochs` | 100 | 训练轮数 |
| `imgsz` | 640 | 输入图片尺寸 |
| `batch` | 16 | 批次大小（根据 GPU 显存调整） |
| `lr0` | 0.01 | 初始学习率 |
| `patience` | 50 | 早停耐心值（验证集指标无提升的轮数） |
| `augment` | True | 是否使用数据增强 |
| `device` | auto | 训练设备（`cpu`/`0`/`0,1`） |

### 3.3 模型规模选择

| 模型 | 参数量 | 推理速度 | 精度 | 适用场景 |
|------|--------|---------|------|---------|
| `yolo11n.pt` | 2.6M | 最快 | 一般 | 实时检测、边缘设备 |
| `yolo11s.pt` | 9.4M | 快 | 较好 | 平衡速度与精度 |
| `yolo11m.pt` | 20.1M | 中等 | 好 | 服务器部署 |
| `yolo11l.pt` | 25.3M | 较慢 | 很好 | 高精度需求 |
| `yolo11x.pt` | 56.9M | 最慢 | 最好 | 追求极致精度 |

### 3.4 Python 脚本训练

```python
from ultralytics import YOLO

model = YOLO("yolo11s.pt")

results = model.train(
    data="crack.yaml",
    epochs=150,
    imgsz=640,
    batch=16,
    lr0=0.01,
    patience=30,
    augment=True,
    project="crack_detection",
    name="train_v2",
    hsv_h=0.015,
    hsv_s=0.7,
    hsv_v=0.4,
    degrees=10.0,
    translate=0.1,
    scale=0.5,
    flipud=0.5,
    fliplr=0.5,
    mosaic=1.0,
)
```

### 3.5 训练增强建议

裂缝检测场景推荐的数据增强策略：

```python
results = model.train(
    data="crack.yaml",
    epochs=150,
    imgsz=640,
    batch=16,
    hsv_h=0.015,       # 色调增强（模拟不同光照）
    hsv_s=0.7,         # 饱和度增强
    hsv_v=0.4,         # 明度增强
    degrees=15.0,       # 旋转角度（裂缝方向多变）
    translate=0.1,      # 平移
    scale=0.5,          # 缩放（模拟不同拍摄距离）
    flipud=0.5,         # 上下翻转
    fliplr=0.5,         # 左右翻转
    mosaic=1.0,         # Mosaic 增强
    erasing=0.4,        # 随机擦除（模拟遮挡）
)
```

## 4. 模型评估

### 4.1 验证集评估

```bash
yolo detect val \
    model=crack_detection/train_v1/weights/best.pt \
    data=crack.yaml \
    imgsz=640
```

### 4.2 关键指标

| 指标 | 说明 | 期望值 |
|------|------|--------|
| mAP50 | IOU=0.5 时的平均精度 | > 0.7 |
| mAP50-95 | IOU=0.5:0.95 的平均精度 | > 0.4 |
| Precision | 精确率 | > 0.8 |
| Recall | 召回率 | > 0.7 |

### 4.3 测试集推理

```bash
yolo detect predict \
    model=crack_detection/train_v1/weights/best.pt \
    source=test_images/ \
    conf=0.25 \
    save=True
```

## 5. 模型部署

### 5.1 部署到本系统

训练完成后，将最优权重文件复制到项目的 `weights` 目录：

```bash
copy crack_detection\train_v1\weights\best.pt g:\bangong\qiangtijiance\weights\best.pt
```

重启服务即可自动加载自定义模型。

### 5.2 更新类别映射

如果自定义模型的类别定义与默认不同，需修改 `config.py` 中的 `CRACK_CLASSES`：

```python
CRACK_CLASSES = {
    0: "横向裂缝",
    1: "纵向裂缝",
    2: "斜向裂缝",
    3: "网状裂缝",
    4: "裂缝",
}
```

确保类别 ID 和名称与训练数据集的 `crack.yaml` 中 `names` 定义一致。

### 5.3 验证部署

```bash
curl -X POST http://localhost:8000/api/detect \
  -F "file=@test_wall.jpg" \
  -F "conf=0.25"
```

检查返回结果中 `class_name` 是否正确显示自定义类别名称。

## 6. 持续优化

### 6.1 迭代训练流程

```
收集新数据 → 标注 → 合并数据集 → 重新训练 → 评估 → 部署
     ↑                                                    |
     └──────────── 线上误检/漏检反馈 ←──────────────────────┘
```

### 6.2 模型微调

基于已有权重继续训练：

```bash
yolo detect train \
    model=crack_detection/train_v1/weights/best.pt \
    data=crack_v2.yaml \
    epochs=50 \
    lr0=0.001
```

注意使用更小的学习率（`lr0=0.001`），避免遗忘已学到的特征。

### 6.3 困难样本挖掘

1. 收集线上检测中的误检和漏检图片
2. 人工标注后加入训练集
3. 增大困难样本的采样权重
4. 重新训练模型

### 6.4 多尺度训练

对于不同分辨率的输入图片，可使用多尺度训练提升鲁棒性：

```python
results = model.train(
    data="crack.yaml",
    epochs=150,
    imgsz=640,
    scale=0.5,          # 缩放增强范围
)
```
