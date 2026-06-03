# 数据标注模块使用指南

## 数据标注模块概述

数据标注模块是墙体裂缝检测系统的核心组件之一，支持**矩形标注**和**多边形标注**两种模式，提供完整的数据集创建、导入、图片上传、手动标注、自动标注、数据集分割和多格式导出功能。该模块基于 FastAPI 后端和 Canvas 前端交互，支持 YOLO 和 LabelMe 两种标注格式的导入导出。

### 核心功能

| 功能 | 说明 |
|------|------|
| 数据集管理 | 创建、导入、查看、删除数据集 |
| 矩形标注 | 拖拽绘制矩形框，快捷键 `R` |
| **多边形标注** | 单击添加顶点，双击/Enter闭合，快捷键 `P` |
| **编辑标注** | 拖拽顶点/边线加点/Shift+点击删点，快捷键 `E` |
| LabelMe 支持 | 导入/导出 LabelMe JSON 格式 |
| 自动标注 | YOLO11 预标注，一键生成标注 |
| 数据集分割 | 训练/验证/测试集自动分割 |
| 数据导出 | YOLO/COCO/VOC/LabelMe 多格式导出 |
| 类别管理 | 自定义类别，默认裂缝类别 |

### 访问地址

标注模块页面：`http://localhost:8009/annotation`

---

## 创建数据集

### 界面操作

1. 打开标注模块页面 `http://localhost:8000/annotation`
2. 在左侧数据集面板点击「新建数据集」按钮
3. 填写数据集名称和描述信息
4. 点击「确认」创建数据集

创建成功后，系统会在 `datasets/` 目录下自动生成以下结构：

```
datasets/{dataset_id}/
├── images/          # 图片目录
├── labels/          # 标注文件目录
└── meta.json        # 数据集元信息
```

`meta.json` 文件内容示例：

```json
{
  "dataset_id": "f00464ee",
  "name": "墙体裂缝数据集",
  "description": "3号楼裂缝检测采集数据",
  "classes": {
    "0": "横向裂缝",
    "1": "纵向裂缝",
    "2": "斜向裂缝",
    "3": "网状裂缝",
    "4": "裂缝"
  },
  "created_at": "2026-05-22 10:00:00",
  "updated_at": "2026-05-22 10:00:00",
  "image_count": 0,
  "annotated_count": 0
}
```

### API 调用

**创建数据集**

```
POST /api/datasets
Content-Type: multipart/form-data
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 数据集名称 |
| `description` | string | 否 | 数据集描述 |

请求示例：

```bash
curl -X POST http://localhost:8000/api/datasets \
  -F "name=墙体裂缝数据集" \
  -F "description=3号楼裂缝检测采集数据"
```

Python 示例：

```python
import requests

response = requests.post("http://localhost:8000/api/datasets", data={
    "name": "墙体裂缝数据集",
    "description": "3号楼裂缝检测采集数据",
})
dataset = response.json()
print(f"数据集ID: {dataset['dataset']['dataset_id']}")
```

响应示例：

```json
{
  "success": true,
  "dataset": {
    "dataset_id": "f00464ee",
    "name": "墙体裂缝数据集",
    "description": "3号楼裂缝检测采集数据",
    "classes": {"0": "横向裂缝", "1": "纵向裂缝", "2": "斜向裂缝", "3": "网状裂缝", "4": "裂缝"},
    "created_at": "2026-05-22 10:00:00",
    "updated_at": "2026-05-22 10:00:00",
    "image_count": 0,
    "annotated_count": 0
  }
}
```

**查看数据集列表**

```
GET /api/datasets
```

**查看单个数据集**

```
GET /api/datasets/{dataset_id}
```

**删除数据集**

```
DELETE /api/datasets/{dataset_id}
```

---

## 上传图片

### 批量上传

支持一次选择多张图片批量上传到指定数据集。系统会自动为每张图片创建对应的空标注文件。

**界面操作**

1. 在数据集详情页面，点击「上传图片」按钮
2. 在文件选择对话框中选择一张或多张图片
3. 系统自动上传并显示进度
4. 上传完成后，图片列表自动刷新

**支持的图片格式**

| 格式 | 扩展名 |
|------|--------|
| PNG | `.png` |
| JPEG | `.jpg`, `.jpeg` |
| BMP | `.bmp` |
| TIFF | `.tiff` |
| WebP | `.webp` |

**文件大小限制**：单张图片最大 100MB

### 拖拽上传

在标注页面中，可直接将图片文件拖拽到上传区域完成上传，操作步骤：

1. 从文件管理器中选择一张或多张图片
2. 拖拽到标注页面的上传区域
3. 松开鼠标，系统自动开始上传

### API 调用

**上传图片到数据集**

```
POST /api/datasets/{dataset_id}/images
Content-Type: multipart/form-data
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `files` | File[] | 是 | 图片文件列表（支持多文件） |

请求示例：

```bash
curl -X POST http://localhost:8000/api/datasets/f00464ee/images \
  -F "files=@wall_001.jpg" \
  -F "files=@wall_002.jpg" \
  -F "files=@wall_003.png"
```

Python 示例：

```python
import requests

files = [
    ("files", open("wall_001.jpg", "rb")),
    ("files", open("wall_002.jpg", "rb")),
    ("files", open("wall_003.png", "rb")),
]
response = requests.post(
    "http://localhost:8000/api/datasets/f00464ee/images",
    files=files,
)
result = response.json()
print(f"成功添加 {len(result['added'])} 张图片")
```

响应示例：

```json
{
  "success": true,
  "added": [
    {
      "filename": "a1b2c3d4_wall_001.jpg",
      "label_file": "a1b2c3d4_wall_001.txt",
      "has_annotation": false
    },
    {
      "filename": "e5f6g7h8_wall_002.jpg",
      "label_file": "e5f6g7h8_wall_002.txt",
      "has_annotation": false
    }
  ]
}
```

**查看数据集图片列表**

```
GET /api/datasets/{dataset_id}/images
```

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `annotated_only` | bool | 否 | false | 仅显示已标注图片 |
| `page` | int | 否 | 1 | 页码 |
| `page_size` | int | 否 | 50 | 每页数量 |

**删除数据集图片**

```
DELETE /api/datasets/{dataset_id}/images/{filename}
```

---

## 手动标注操作

### 工具栏

| 按钮 | 快捷键 | 功能 |
|------|--------|------|
| 矩形 | `R` | 拖拽绘制矩形标注框 |
| **多边形** | `P` | 点击添加顶点 → 双击/Enter闭合（≥3顶点） |
| **编辑** | `E` | 选中标注后：拖拽顶点 / 点击边线加点 / Shift+点击顶点删点 |
| 平移 | `H` | 拖拽平移画布，滚轮缩放 |

### 多边形标注操作

| 操作 | 方式 |
|------|------|
| 开始绘制 | 按 `P` → 在图上单击出第一个顶点 |
| 添加顶点 | 继续单击添加顶点（沿裂缝边缘） |
| **回退顶点** | 按 `Backspace` 逐点撤销 |
| 闭合完成 | **双击** / 按 `Enter` / 右键（≥3个顶点） |
| 取消绘制 | 按 `Esc` |

### 编辑模式操作

| 操作 | 方式 |
|------|------|
| 选中标注 | 按 `E` → 点击标注 |
| 拖拽顶点 | 拖拽标注的顶点圆点 |
| **边线加点** | 点击多边形边线（自动在最近边中点插入） |
| **删点** | `Shift` + 点击顶点（至少保留3个顶点） |
| 整体移动 | 拖拽标注主体 |
| 矩形↔多边形转换 | 右键 → 「转为多边形」/ 列表点击「转多边形」 |
| 右键菜单 | 右键标注 → 转换/添顶点/删顶点/删标注 |

### 多边形保存机制

- 保存时多边形**自动计算外接矩形**存入 YOLO `.txt`（用于训练）
- 完整顶点坐标存入 `_shapes.json` 侧载文件
- 重新打开图片时自动从侧载文件**还原多边形形状**

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| `R` | 矩形模式 |
| `P` | 多边形模式 |
| `E` | 编辑模式 |
| `H` | 平移模式 |
| `Delete` | 删除选中的标注 |
| `Ctrl + S` | 保存并跳转下一张 |
| `←` / `→` | 上一张/下一张 |
| `Backspace` | 多边形回退顶点 |
| `Enter` | 闭合多边形 |
| `Esc` | 取消绘制/取消选择 |

### 保存标注

标注数据通过以下 API 保存：

```
POST /api/datasets/{dataset_id}/images/{filename}/annotations
Content-Type: application/json
```

请求体：

```json
{
  "annotations": [
    {
      "class_id": 0,
      "cx": 0.452300,
      "cy": 0.312500,
      "w": 0.234000,
      "h": 0.056700
    },
    {
      "class_id": 2,
      "cx": 0.678900,
      "cy": 0.543200,
      "w": 0.089000,
      "h": 0.345600
    }
  ]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `class_id` | int | 类别 ID |
| `cx` | float | 中心点 X 坐标（归一化 0-1） |
| `cy` | float | 中心点 Y 坐标（归一化 0-1） |
| `w` | float | 框宽度（归一化 0-1） |
| `h` | float | 框高度（归一化 0-1） |

保存后，系统会在 `labels/` 目录下生成对应的 `.txt` 文件：

```
0 0.452300 0.312500 0.234000 0.056700
2 0.678900 0.543200 0.089000 0.345600
```

**获取图片标注**

```
GET /api/datasets/{dataset_id}/images/{filename}/annotations
```

响应示例：

```json
{
  "filename": "a1b2c3d4_wall_001.jpg",
  "annotations": [
    {
      "class_id": 0,
      "class_name": "横向裂缝",
      "cx": 0.4523,
      "cy": 0.3125,
      "w": 0.234,
      "h": 0.0567
    }
  ],
  "image_size": {
    "width": 1920,
    "height": 1080
  },
  "classes": {
    "0": "横向裂缝",
    "1": "纵向裂缝",
    "2": "斜向裂缝",
    "3": "网状裂缝",
    "4": "裂缝"
  }
}
```

---

## 自动标注

### YOLO11 预标注

自动标注功能利用 YOLO11 模型对数据集中的所有图片进行批量检测，自动生成标注结果。适用于以下场景：

- 大量图片的初步标注，减少手动工作量
- 已有模型的迭代训练数据准备
- 快速构建初始数据集

**界面操作**

1. 在数据集详情页面，点击「自动标注」按钮
2. 设置置信度阈值和 IOU 阈值
3. 点击「开始标注」
4. 系统自动对数据集中所有图片执行检测
5. 标注完成后，图片列表自动刷新，显示标注状态

### 参数设置

| 参数 | 默认值 | 范围 | 说明 |
|------|--------|------|------|
| `conf` | 0.25 | 0-1 | 置信度阈值，低于此值的检测结果将被过滤 |
| `iou` | 0.45 | 0-1 | NMS IOU 阈值，控制重叠框的去重程度 |

**参数调优建议**

| 场景 | conf | iou | 说明 |
|------|------|-----|------|
| 初步预标注 | 0.15 | 0.45 | 低阈值获取更多候选框，后续人工筛选 |
| 常规预标注 | 0.25 | 0.45 | 默认值，平衡精确率和召回率 |
| 精确预标注 | 0.40 | 0.50 | 高阈值减少误检，但可能漏检 |

> **注意**：自动标注会覆盖已有的标注文件。建议在自动标注后进行人工审核和修正。

### API 调用

```
POST /api/datasets/{dataset_id}/auto_annotate
Content-Type: multipart/form-data
```

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `conf` | float | 否 | 0.25 | 置信度阈值 |
| `iou` | float | 否 | 0.45 | NMS IOU 阈值 |

请求示例：

```bash
curl -X POST http://localhost:8000/api/datasets/f00464ee/auto_annotate \
  -F "conf=0.25" \
  -F "iou=0.45"
```

Python 示例：

```python
import requests

response = requests.post(
    "http://localhost:8000/api/datasets/f00464ee/auto_annotate",
    data={"conf": 0.25, "iou": 0.45},
)
result = response.json()
print(f"自动标注完成: {result['annotated']}/{result['total']} 张图片")
```

响应示例：

```json
{
  "success": true,
  "annotated": 45,
  "total": 50
}
```

---

## 数据集分割

### 训练/验证/测试集分割

在训练模型之前，需要将数据集分割为训练集、验证集和测试集。系统支持按指定比例随机分割数据集，并自动生成 `data.yaml` 配置文件。

**界面操作**

1. 在数据集详情页面，确保图片已完成标注
2. 点击「分割数据集」按钮
3. 设置训练集、验证集、测试集的比例
4. 设置随机种子（可选，用于可复现分割）
5. 点击「确认分割」

分割完成后，目录结构如下：

```
datasets/{dataset_id}/
├── images/
│   ├── train/       # 训练集图片
│   ├── val/         # 验证集图片
│   ├── test/        # 测试集图片
│   └── *.jpg        # 原始图片（保留）
├── labels/
│   ├── train/       # 训练集标注
│   ├── val/         # 验证集标注
│   ├── test/        # 测试集标注
│   └── *.txt        # 原始标注（保留）
├── data.yaml        # 数据集配置文件
└── meta.json        # 数据集元信息
```

### 比例设置

| 数据集 | 默认比例 | 说明 |
|--------|---------|------|
| 训练集 | 70% | 用于模型训练 |
| 验证集 | 20% | 用于训练过程中验证和早停 |
| 测试集 | 10% | 用于最终模型评估 |

常见分割比例参考：

| 场景 | 训练集 | 验证集 | 测试集 | 说明 |
|------|--------|--------|--------|------|
| 默认 | 70% | 20% | 10% | 适用于大多数情况 |
| 小数据集 | 80% | 15% | 5% | 数据量少时增大训练比例 |
| 大数据集 | 70% | 15% | 15% | 数据充足时增大测试比例 |
| 快速验证 | 80% | 20% | 0% | 不需要独立测试集时 |

### 随机种子

随机种子用于确保数据集分割的可复现性。使用相同的种子值，每次分割的结果一致。

- 默认种子值：`42`
- 如需不同的分割结果，可修改种子值
- 建议记录使用的种子值，以便后续复现

### data.yaml 配置文件

分割完成后，系统自动生成 `data.yaml` 文件：

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
| `nc` | 类别数量 |
| `names` | 类别 ID 到名称的映射 |

### API 调用

```
POST /api/datasets/{dataset_id}/split
Content-Type: multipart/form-data
```

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `train_ratio` | float | 否 | 0.7 | 训练集比例 |
| `val_ratio` | float | 否 | 0.2 | 验证集比例 |
| `test_ratio` | float | 否 | 0.1 | 测试集比例 |
| `seed` | int | 否 | 42 | 随机种子 |

请求示例：

```bash
curl -X POST http://localhost:8000/api/datasets/f00464ee/split \
  -F "train_ratio=0.7" \
  -F "val_ratio=0.2" \
  -F "test_ratio=0.1" \
  -F "seed=42"
```

Python 示例：

```python
import requests

response = requests.post(
    "http://localhost:8000/api/datasets/f00464ee/split",
    data={
        "train_ratio": 0.7,
        "val_ratio": 0.2,
        "test_ratio": 0.1,
        "seed": 42,
    },
)
result = response.json()
print(f"训练集: {result['train']}张, 验证集: {result['val']}张, 测试集: {result['test']}张")
```

响应示例：

```json
{
  "success": true,
  "dataset_id": "f00464ee",
  "total": 50,
  "train": 35,
  "val": 10,
  "test": 5,
  "ratios": {"train": 0.7, "val": 0.2, "test": 0.1},
  "yaml_path": "G:\\bangong\\qiangtijiance\\datasets\\f00464ee\\data.yaml"
}
```

---

## 数据导出

### YOLO 格式

YOLO 格式是系统原生格式，导出内容包含：

- `data.yaml`：数据集配置文件
- `images/{split}/`：按分割组织的图片
- `labels/{split}/`：按分割组织的标注文件

标注文件格式（每行一个目标）：

```
class_id center_x center_y width height
```

所有坐标为归一化值（0-1）。

导出文件：`dataset_{dataset_id}_yolo.zip`

### COCO 格式

COCO 格式导出为单个 JSON 文件，包含：

- `images`：图片信息列表（id、文件名、宽高）
- `annotations`：标注信息列表（id、image_id、category_id、bbox、area）
- `categories`：类别信息列表（id、name）

COCO 格式的 bbox 为 `[x, y, width, height]`，其中 `(x, y)` 为左上角坐标，值为像素绝对值。

导出文件：`coco_annotations.json`

COCO 格式示例：

```json
{
  "images": [
    {"id": 1, "file_name": "wall_001.jpg", "width": 1920, "height": 1080}
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 1,
      "category_id": 0,
      "bbox": [523.2, 265.5, 449.3, 61.2],
      "area": 27497.16,
      "iscrowd": 0
    }
  ],
  "categories": [
    {"id": 0, "name": "横向裂缝"},
    {"id": 1, "name": "纵向裂缝"}
  ]
}
```

### VOC 格式

VOC 格式导出为 XML 文件，每张图片对应一个 XML 标注文件。

VOC 格式示例：

```xml
<?xml version='1.0' encoding='utf-8'?>
<annotation>
  <folder>images</folder>
  <filename>wall_001.jpg</filename>
  <size>
    <width>1920</width>
    <height>1080</height>
    <depth>3</depth>
  </size>
  <object>
    <name>横向裂缝</name>
    <pose>Unspecified</pose>
    <truncated>0</truncated>
    <difficult>0</difficult>
    <bndbox>
      <xmin>523</xmin>
      <ymin>265</ymin>
      <xmax>972</xmax>
      <ymax>327</ymax>
    </bndbox>
  </object>
</annotation>
```

### LabelMe 格式

LabelMe 是 MIT 开发的开源标注工具格式，导出为单个 JSON 文件，包含多边形顶点坐标。系统支持 **LabelMe 格式的导入和导出**。

**导入 LabelMe**：`POST /api/datasets/{id}/import_labelme`（上传多个 .json 文件）

**导出 LabelMe**：导出格式选择 `labelme`，生成每个图片对应的 `.json` 文件。

LabelMe JSON 示例：
```json
{
  "version": "5.0.1",
  "shapes": [
    {"label": "横向裂缝", "points": [[50,50],[200,80]], "shape_type": "rectangle"},
    {"label": "纵向裂缝", "points": [[100,30],[180,90],[150,200]], "shape_type": "polygon"}
  ],
  "imagePath": "wall_001.jpg",
  "imageHeight": 640, "imageWidth": 480
}
```

### 格式对比

| 特性 | YOLO | COCO | VOC | LabelMe |
|------|------|------|-----|---------|
| 文件格式 | `.txt` | `.json` | `.xml` | `.json` |
| 坐标系统 | 归一化中心 | 像素左上角 | 像素左上角 | 像素绝对坐标 |
| 多边形支持 | 外接矩形 | 分割 | 边界框 | ✅ 原生多边形 |
| 存储效率 | 高 | 中 | 低 | 中 |
| 适用框架 | YOLO 系列 | mmdetection | Pascal VOC | LabelMe/LabelImg |

### API 调用

```
POST /api/datasets/{dataset_id}/export
Content-Type: multipart/form-data
```

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `format` | string | 否 | yolo | 导出格式：`yolo` / `coco` / `voc` |

请求示例：

```bash
curl -X POST http://localhost:8000/api/datasets/f00464ee/export \
  -F "format=yolo" \
  -o dataset_f00464ee_yolo.zip
```

Python 示例：

```python
import requests

response = requests.post(
    "http://localhost:8000/api/datasets/f00464ee/export",
    data={"format": "coco"},
)
with open("coco_export.zip", "wb") as f:
    f.write(response.content)
print("导出完成")
```

---

## 类别管理

### 自定义类别

系统支持自定义数据集的类别定义。创建数据集时默认使用系统预定义的裂缝类别，也可根据需要修改。

**界面操作**

1. 在数据集详情页面，点击「类别管理」按钮
2. 添加、修改或删除类别
3. 点击「保存」更新类别配置

### 默认裂缝类别

系统默认的裂缝类别定义（与 `config.py` 中 `CRACK_CLASSES` 一致）：

```python
CRACK_CLASSES = {
    0: "横向裂缝",
    1: "纵向裂缝",
    2: "斜向裂缝",
    3: "网状裂缝",
    4: "裂缝",
}
```

### 类别定义规范

- 类别 ID 从 0 开始连续编号
- 类别名称应简洁明确
- 类别数量建议不超过 10 个
- 类别之间不应有重叠或包含关系
- 类别定义需与标注数据和训练配置保持一致

### API 调用

**更新数据集类别**

```
PUT /api/datasets/{dataset_id}/classes
Content-Type: application/json
```

请求体：

```json
{
  "classes": {
    "0": "横向裂缝",
    "1": "纵向裂缝",
    "2": "斜向裂缝",
    "3": "网状裂缝",
    "4": "裂缝"
  }
}
```

请求示例：

```bash
curl -X PUT http://localhost:8000/api/datasets/f00464ee/classes \
  -H "Content-Type: application/json" \
  -d '{"classes": {"0": "crack", "1": "spalling", "2": "efflorescence"}}'
```

---

## API 参考

### 数据集管理

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/datasets` | 获取数据集列表 |
| `POST` | `/api/datasets` | 创建数据集 |
| **`POST`** | **`/api/datasets/import`** | **从本地文件夹导入数据集** |
| `GET` | `/api/datasets/{dataset_id}` | 获取数据集详情 |
| `DELETE` | `/api/datasets/{dataset_id}` | 删除数据集 |
| `PUT` | `/api/datasets/{dataset_id}/classes` | 更新数据集类别 |
| `POST` | `/api/datasets/{dataset_id}/import_labelme` | 导入 LabelMe JSON 文件 |

### 图片管理

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/datasets/{dataset_id}/images` | 获取图片列表 |
| `POST` | `/api/datasets/{dataset_id}/images` | 上传图片 |
| `DELETE` | `/api/datasets/{dataset_id}/images/{filename}` | 删除图片 |

### 标注操作

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/datasets/{dataset_id}/images/{filename}/annotations` | 获取图片标注 |
| `POST` | `/api/datasets/{dataset_id}/images/{filename}/annotations` | 保存图片标注 |
| `POST` | `/api/datasets/{dataset_id}/auto_annotate` | 自动标注 |

### 数据集操作

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/api/datasets/{dataset_id}/split` | 分割数据集 |
| `POST` | `/api/datasets/{dataset_id}/export` | 导出数据集 |

### 参数速查

**创建数据集参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `name` | string | 是 | - | 数据集名称 |
| `description` | string | 否 | "" | 数据集描述 |

**上传图片参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `files` | File[] | 是 | - | 图片文件列表 |

**获取图片列表参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `annotated_only` | bool | 否 | false | 仅显示已标注图片 |
| `page` | int | 否 | 1 | 页码 |
| `page_size` | int | 否 | 50 | 每页数量 |

**保存标注参数**

| 字段 | 类型 | 说明 |
|------|------|------|
| `annotations[].class_id` | int | 类别 ID |
| `annotations[].cx` | float | 中心点 X（归一化 0-1） |
| `annotations[].cy` | float | 中心点 Y（归一化 0-1） |
| `annotations[].w` | float | 框宽度（归一化 0-1） |
| `annotations[].h` | float | 框高度（归一化 0-1） |

**自动标注参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `conf` | float | 否 | 0.25 | 置信度阈值 |
| `iou` | float | 否 | 0.45 | NMS IOU 阈值 |

**分割数据集参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `train_ratio` | float | 否 | 0.7 | 训练集比例 |
| `val_ratio` | float | 否 | 0.2 | 验证集比例 |
| `test_ratio` | float | 否 | 0.1 | 测试集比例 |
| `seed` | int | 否 | 42 | 随机种子 |

**导入数据集参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 数据集名称 |
| `source_dir` | string | 是 | 源文件夹绝对路径 |
| `description` | string | 否 | 描述信息 |

**导出数据集参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `format` | string | 否 | yolo | 导出格式：yolo/coco/voc/labelme |
