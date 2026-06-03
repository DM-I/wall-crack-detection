# 数据集指南

## 公开数据集推荐

### Ultralytics Crack Segmentation Dataset

| 项目 | 说明 |
|------|------|
| 名称 | Crack Segmentation Dataset |
| 来源 | Ultralytics 官方 |
| 图片数量 | 4029 张 |
| 标注类型 | 语义分割（可转换为边界框） |
| 类别 | 1 类（crack） |
| 文件大小 | ~91.6 MB |
| 下载地址 | https://github.com/ultralytics/assets/releases/download/v0.0.0/crack-seg.zip |
| 许可证 | AGPL-3.0 |

该数据集已预分为训练集、验证集和测试集，包含 `data.yaml` 配置文件，可直接用于 YOLO11 训练。

**数据集结构**：

```
crack-seg/
├── images/
│   ├── train/    # 训练集图片
│   ├── val/      # 验证集图片
│   └── test/     # 测试集图片
├── labels/
│   ├── train/    # 训练集标注
│   ├── val/      # 验证集标注
│   └── test/     # 测试集标注
└── data.yaml     # 数据集配置
```

### USU Concrete Crack Dataset

| 项目 | 说明 |
|------|------|
| 名称 | USU Concrete Crack Dataset |
| 来源 | Utah State University |
| 图片数量 | ~2000 张 |
| 标注类型 | 边界框 |
| 类别 | 裂缝 |
| 特点 | 混凝土表面裂缝，多种光照条件 |
| 下载地址 | 学术申请获取 |

### 其他推荐数据集

| 数据集 | 图片数量 | 说明 | 来源 |
|--------|---------|------|------|
| CRACK500 | 500 | 路面裂缝图片，高分辨率 | [GitHub](https://github.com/fyangneil/pavement-crack-detection) |
| DeepCrack | 300 | 细裂缝图片，含像素级标注 | [GitHub](https://github.com/qinnzou/DeepCrack) |
| CFD | ~500 | 混凝土裂缝图片集 | [GitHub](https://github.com/cuilimeng/CRack-detection-dataset) |
| Rissbilder | ~400 | 墙体裂缝图片集，多种墙体材质 | 学术数据集 |
| SDNET2018 | 56000 | 混凝土桥梁裂缝，含无裂缝图片 | [Data.gov](https://digitalcommons.mtu.edu/data/2/) |
| Masonry Crack | ~1000 | 砌体结构裂缝 | 学术数据集 |

**数据集选择建议**

| 场景 | 推荐数据集 | 说明 |
|------|-----------|------|
| 快速开始 | Ultralytics Crack Segmentation | 一键下载，格式兼容 |
| 墙体裂缝 | Rissbilder / Masonry Crack | 贴近实际应用场景 |
| 大规模训练 | SDNET2018 | 数据量大，泛化能力强 |
| 精细检测 | DeepCrack | 细裂缝标注，适合小目标 |

---

## 使用 download_dataset.py 下载 Ultralytics 数据集

系统提供了 `download_dataset.py` 脚本，可一键下载并解压 Ultralytics Crack Segmentation 数据集。

### 下载步骤

**1. 运行下载脚本**

```powershell
cd G:\bangong\qiangtijiance
python download_dataset.py
```

**2. 下载过程**

脚本执行以下三个步骤：

```
[1/3] Downloading crack-seg dataset from Ultralytics...
      URL: https://github.com/ultralytics/assets/releases/download/v0.0.0/crack-seg.zip
      Size: ~91.6 MB
      Progress: 100.0% (91.6 / 91.6 MB)
      Download complete!

[2/3] Extracting dataset...
      Extraction complete!

[3/3] Verifying dataset structure...
      Train images: 2820
      Val images:   809
      Test images:  400
      Total:        4029
      Created data.yaml

[DONE] Dataset ready at: G:\bangong\qiangtijiance\datasets\crack-seg
       data.yaml: G:\bangong\qiangtijiance\datasets\crack-seg\data.yaml
```

**3. 断点续传**

如果 ZIP 文件已下载但未解压，脚本会跳过下载步骤直接解压：

```
[1/3] ZIP file already exists, skipping download.
[2/3] Extracting dataset...
```

如果 ZIP 文件损坏，脚本会自动重新下载：

```
[1/3] Existing ZIP file is corrupted, re-downloading...
```

如果数据集已解压完成，脚本会直接返回：

```
[OK] Dataset already extracted at: G:\bangong\qiangtijiance\datasets\crack-seg
```

### 下载后导入系统

下载的数据集位于 `datasets/crack-seg/` 目录，但尚未纳入系统的数据集管理。需要通过以下步骤导入：

**方式一：通过 API 创建数据集并上传**

```python
import requests
import os

base_url = "http://localhost:8000"

response = requests.post(f"{base_url}/api/datasets", data={
    "name": "Ultralytics Crack Segmentation",
    "description": "4029张裂缝图片，来自Ultralytics官方数据集",
})
dataset_id = response.json()["dataset"]["dataset_id"]

train_dir = "datasets/crack-seg/images/train"
files = []
for f in os.listdir(train_dir)[:50]:
    ext = f.rsplit(".", 1)[-1].lower()
    if ext in {"png", "jpg", "jpeg", "bmp", "tiff", "webp"}:
        files.append(("files", open(os.path.join(train_dir, f), "rb")))

response = requests.post(
    f"{base_url}/api/datasets/{dataset_id}/images",
    files=files,
)
for _, f in files:
    f.close()
print(f"上传完成: {response.json()}")
```

**方式二：手动创建数据集目录**

```powershell
# 在 datasets 目录下创建数据集结构
mkdir datasets\crack-seg-system
mkdir datasets\crack-seg-system\images
mkdir datasets\crack-seg-system\labels

# 复制图片和标注
xcopy datasets\crack-seg\images\train\* datasets\crack-seg-system\images\ /Y
xcopy datasets\crack-seg\labels\train\* datasets\crack-seg-system\labels\ /Y

# 创建 meta.json
# 需要通过 API 创建数据集或手动编写 meta.json
```

---

## 数据集格式要求

### YOLO 格式

YOLO 格式是本系统的原生标注格式，也是最常用的目标检测数据集格式。

**标注文件格式**

每张图片对应一个同名的 `.txt` 标注文件，每行一个目标：

```
class_id center_x center_y width height
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `class_id` | int | 类别 ID，从 0 开始 |
| `center_x` | float | 边界框中心点 X 坐标（归一化 0-1） |
| `center_y` | float | 边界框中心点 Y 坐标（归一化 0-1） |
| `width` | float | 边界框宽度（归一化 0-1） |
| `height` | float | 边界框高度（归一化 0-1） |

**归一化坐标计算**：

```
center_x = (x1 + x2) / 2 / image_width
center_y = (y1 + y2) / 2 / image_height
width = (x2 - x1) / image_width
height = (y2 - y1) / image_height
```

其中 `(x1, y1, x2, y2)` 为像素坐标。

**标注文件示例**：

```
0 0.452300 0.312500 0.234000 0.056700
2 0.678900 0.543200 0.089000 0.345600
3 0.234500 0.789100 0.156000 0.123400
```

**无目标的图片**：创建空的 `.txt` 文件即可。

### 目录结构

标准 YOLO 数据集目录结构：

```
dataset/
├── images/
│   ├── train/           # 训练集图片
│   │   ├── img_0001.jpg
│   │   ├── img_0002.jpg
│   │   └── ...
│   ├── val/             # 验证集图片
│   │   ├── img_1001.jpg
│   │   └── ...
│   └── test/            # 测试集图片（可选）
│       ├── img_2001.jpg
│       └── ...
├── labels/
│   ├── train/           # 训练集标注
│   │   ├── img_0001.txt
│   │   ├── img_0002.txt
│   │   └── ...
│   ├── val/             # 验证集标注
│   │   ├── img_1001.txt
│   │   └── ...
│   └── test/            # 测试集标注（可选）
│       ├── img_2001.txt
│       └── ...
└── data.yaml            # 数据集配置文件
```

**命名规则**：
- 图片文件和标注文件必须同名（扩展名不同）
- 文件名建议使用英文和数字，避免中文和特殊字符
- 支持的图片格式：`.png`、`.jpg`、`.jpeg`、`.bmp`、`.tiff`、`.webp`

### data.yaml 配置

```yaml
path: /absolute/path/to/dataset    # 数据集根目录（绝对路径）
train: images/train                 # 训练图片目录（相对于 path）
val: images/val                     # 验证图片目录（相对于 path）
test: images/test                   # 测试图片目录（相对于 path，可选）

nc: 5                               # 类别数量
names:                              # 类别名称映射
  0: 横向裂缝
  1: 纵向裂缝
  2: 斜向裂缝
  3: 网状裂缝
  4: 裂缝
```

**字段说明**：

| 字段 | 必填 | 说明 |
|------|------|------|
| `path` | 是 | 数据集根目录，建议使用绝对路径 |
| `train` | 是 | 训练集图片目录 |
| `val` | 是 | 验证集图片目录 |
| `test` | 否 | 测试集图片目录 |
| `nc` | 是 | 类别数量 |
| `names` | 是 | 类别 ID 到名称的映射 |

**系统自动生成的 data.yaml 示例**：

```yaml
path: G:\bangong\qiangtijiance\datasets\f00464ee
train: images/train
val: images/val
test: images/test

nc: 5
names: {"0": "横向裂缝", "1": "纵向裂缝", "2": "斜向裂缝", "3": "网状裂缝", "4": "裂缝"}
```

---

## 自定义数据集准备

### 图片采集建议

**1. 拍摄设备**

| 设备 | 推荐场景 | 注意事项 |
|------|---------|---------|
| 手机相机 | 日常巡检 | 注意稳定拍摄，避免模糊 |
| 数码相机 | 专业检测 | 使用三脚架保证稳定性 |
| 无人机 | 高空外墙 | 注意拍摄角度和距离 |
| 工业内窥镜 | 隐蔽部位 | 需要良好的照明 |

**2. 拍摄参数**

| 参数 | 建议 |
|------|------|
| 分辨率 | ≥ 1920×1080，推荐 4K |
| 格式 | JPEG 或 PNG |
| 光照 | 自然光或均匀人工光，避免强阴影 |
| 角度 | 正对墙面，避免大角度倾斜 |
| 距离 | 确保裂缝在画面中清晰可见 |

**3. 采集多样性**

确保数据集覆盖以下维度的多样性：

| 维度 | 变化范围 |
|------|---------|
| 光照条件 | 强光、弱光、逆光、阴影 |
| 墙体材质 | 混凝土、砖墙、抹灰、涂料 |
| 裂缝类型 | 横向、纵向、斜向、网状 |
| 裂缝宽度 | 细裂缝（<0.2mm）到宽裂缝（>2mm） |
| 拍摄距离 | 近景（<1m）到远景（>5m） |
| 天气条件 | 晴天、阴天、雨天（注意安全） |
| 背景干扰 | 无干扰、有纹理、有污渍 |

**4. 负样本采集**

负样本（无裂缝的墙体图片）对减少误检非常重要：

- 建议正负样本比例约 7:3
- 负样本应包含各种正常墙体表面
- 包含可能引起误检的纹理（如砖缝、接缝、水渍）

### 标注规范

**1. 边界框标注原则**

| 原则 | 说明 | 正确 | 错误 |
|------|------|------|------|
| 紧贴目标 | 框紧贴裂缝边缘，不留多余空间 | ✅ | ❌ 框过大 |
| 完整覆盖 | 框应覆盖裂缝的完整可见部分 | ✅ | ❌ 漏标部分 |
| 不截断 | 尽量不截断裂缝，如裂缝延伸出画面则截断 | ✅ | ❌ 在画面内截断 |
| 不重叠 | 同一裂缝不重复标注 | ✅ | ❌ 多个框重叠 |

**2. 类别选择规范**

| 类别 | 判定标准 |
|------|---------|
| 横向裂缝 | 裂缝走向与水平方向夹角 < 30° |
| 纵向裂缝 | 裂缝走向与垂直方向夹角 < 30° |
| 斜向裂缝 | 裂缝走向倾斜，不属于横向或纵向 |
| 网状裂缝 | 多条裂缝交叉形成网状或龟裂状 |
| 裂缝 | 无法明确分类的裂缝（兜底类别） |

**3. 标注质量检查清单**

- [ ] 每条裂缝都被标注（无漏标）
- [ ] 标注框紧贴裂缝边缘
- [ ] 类别选择正确
- [ ] 无重复标注
- [ ] 无裂缝区域无标注（无误标）
- [ ] 标注框无超出图片边界
- [ ] 归一化坐标值在 0-1 范围内

### 类别定义

**推荐类别定义**（与系统默认一致）：

| class_id | 类别名称 | 英文名 | 说明 |
|----------|---------|--------|------|
| 0 | 横向裂缝 | horizontal_crack | 走向近似水平 |
| 1 | 纵向裂缝 | vertical_crack | 走向近似垂直 |
| 2 | 斜向裂缝 | diagonal_crack | 走向倾斜 |
| 3 | 网状裂缝 | mesh_crack | 交叉形成网状 |
| 4 | 裂缝 | crack | 无法明确分类 |

**简化类别定义**（数据量少时推荐）：

| class_id | 类别名称 | 说明 |
|----------|---------|------|
| 0 | crack | 所有裂缝统一为一类 |

> **建议**：当每类别的训练样本少于 100 个时，使用简化类别定义，避免类别间混淆。

---

## 数据集导入系统的方法

### 方法一：通过 Web 界面

1. 打开标注模块 `http://localhost:8000/annotation`
2. 创建新数据集
3. 上传图片
4. 手动标注或使用自动标注
5. 分割数据集

### 方法二：通过 API

```python
import requests
import os

base_url = "http://localhost:8000"

# 1. 创建数据集
response = requests.post(f"{base_url}/api/datasets", data={
    "name": "自定义裂缝数据集",
    "description": "3号楼检测采集数据",
})
dataset_id = response.json()["dataset"]["dataset_id"]
print(f"数据集ID: {dataset_id}")

# 2. 上传图片
image_dir = "path/to/your/images"
files = []
for f in os.listdir(image_dir):
    ext = f.rsplit(".", 1)[-1].lower()
    if ext in {"png", "jpg", "jpeg", "bmp", "tiff", "webp"}:
        files.append(("files", open(os.path.join(image_dir, f), "rb")))

response = requests.post(
    f"{base_url}/api/datasets/{dataset_id}/images",
    files=files,
)
for _, f in files:
    f.close()
print(f"上传完成: {response.json()}")

# 3. 自动标注
response = requests.post(
    f"{base_url}/api/datasets/{dataset_id}/auto_annotate",
    data={"conf": 0.25, "iou": 0.45},
)
print(f"自动标注: {response.json()}")

# 4. 分割数据集
response = requests.post(
    f"{base_url}/api/datasets/{dataset_id}/split",
    data={"train_ratio": 0.7, "val_ratio": 0.2, "test_ratio": 0.1, "seed": 42},
)
print(f"分割结果: {response.json()}")
```

### 方法三：直接放置文件

将已标注好的数据集直接放置到 `datasets/` 目录下：

```
datasets/
└── my_dataset/           # 自定义数据集ID目录
    ├── images/
    │   ├── train/
    │   ├── val/
    │   └── test/
    ├── labels/
    │   ├── train/
    │   ├── val/
    │   └── test/
    ├── data.yaml
    └── meta.json         # 需手动创建
```

`meta.json` 模板：

```json
{
  "dataset_id": "my_dataset",
  "name": "自定义裂缝数据集",
  "description": "",
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

> **注意**：直接放置文件后，`image_count` 和 `annotated_count` 会在下次访问时自动更新。

---

## 数据增强建议

数据增强是提升模型泛化能力的重要手段。YOLO11 框架内置了丰富的数据增强功能，通过参数控制增强幅度。

### 推荐增强策略

**裂缝检测场景推荐配置**：

| 增强方法 | 推荐值 | 说明 |
|---------|--------|------|
| `hsv_h` | 0.015 | 色调微调，模拟不同色温 |
| `hsv_s` | 0.7 | 饱和度变化，模拟不同材质 |
| `hsv_v` | 0.4 | 明度变化，模拟不同光照 |
| `degrees` | 15.0 | 旋转 ±15°，裂缝方向多变 |
| `translate` | 0.1 | 平移 10%，模拟不同位置 |
| `scale` | 0.5 | 缩放 0.5-1.5x，模拟不同距离 |
| `flipud` | 0.5 | 50% 概率上下翻转 |
| `fliplr` | 0.5 | 50% 概率左右翻转 |
| `mosaic` | 1.0 | Mosaic 增强，4 图拼接 |
| `mixup` | 0.0 | MixUp 增强（数据少时可开启 0.1） |
| `copy_paste` | 0.0 | 复制粘贴增强（数据少时可开启 0.1） |

### 不同数据量的增强策略

| 数据量 | 增强策略 |
|--------|---------|
| < 100 张 | 最大增强：mosaic=1.0, mixup=0.2, copy_paste=0.1, degrees=30, scale=0.9 |
| 100-500 张 | 中等增强：mosaic=1.0, mixup=0.1, degrees=15, scale=0.5 |
| 500-2000 张 | 标准增强：mosaic=1.0, degrees=10, scale=0.5 |
| > 2000 张 | 轻度增强：mosaic=0.5, degrees=5, scale=0.3 |

### 离线数据增强

除了 YOLO11 训练时的在线增强，还可以使用离线增强扩充数据集：

```python
import cv2
import numpy as np
import os
import random

def augment_image(image, label_lines, output_img_dir, output_lbl_dir, base_name):
    h, w = image.shape[:2]
    augmented = []

    # 原图
    augmented.append((image.copy(), label_lines, base_name))

    # 水平翻转
    flipped_h = cv2.flip(image, 1)
    flipped_labels_h = []
    for line in label_lines:
        parts = line.strip().split()
        if len(parts) >= 5:
            cls_id, cx, cy, bw, bh = parts[0], 1-float(parts[1]), parts[2], parts[3], parts[4]
            flipped_labels_h.append(f"{cls_id} {cx:.6f} {cy} {bw} {bh}")
    augmented.append((flipped_h, flipped_labels_h, f"{base_name}_flip_h"))

    # 垂直翻转
    flipped_v = cv2.flip(image, 0)
    flipped_labels_v = []
    for line in label_lines:
        parts = line.strip().split()
        if len(parts) >= 5:
            cls_id, cx, cy, bw, bh = parts[0], parts[1], 1-float(parts[2]), parts[3], parts[4]
            flipped_labels_v.append(f"{cls_id} {cx} {cy:.6f} {bw} {bh}")
    augmented.append((flipped_v, flipped_labels_v, f"{base_name}_flip_v"))

    # 亮度调整
    for alpha in [0.7, 1.3]:
        bright = np.clip(image.astype(np.float32) * alpha, 0, 255).astype(np.uint8)
        augmented.append((bright, label_lines, f"{base_name}_bright_{alpha:.1f}"))

    # 旋转
    for angle in [-10, 10]:
        M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h))
        augmented.append((rotated, label_lines, f"{base_name}_rot_{angle}"))

    # 保存增强结果
    for img, labels, name in augmented:
        cv2.imwrite(os.path.join(output_img_dir, f"{name}.jpg"), img)
        with open(os.path.join(output_lbl_dir, f"{name}.txt"), "w") as f:
            f.write("\n".join(labels))


input_img_dir = "datasets/my_dataset/images/train"
input_lbl_dir = "datasets/my_dataset/labels/train"
output_img_dir = "datasets/my_dataset_augmented/images/train"
output_lbl_dir = "datasets/my_dataset_augmented/labels/train"

os.makedirs(output_img_dir, exist_ok=True)
os.makedirs(output_lbl_dir, exist_ok=True)

for img_file in os.listdir(input_img_dir):
    ext = img_file.rsplit(".", 1)[-1].lower()
    if ext not in {"png", "jpg", "jpeg", "bmp"}:
        continue

    base_name = os.path.splitext(img_file)[0]
    image = cv2.imread(os.path.join(input_img_dir, img_file))

    label_file = os.path.join(input_lbl_dir, f"{base_name}.txt")
    label_lines = []
    if os.path.exists(label_file):
        with open(label_file, "r") as f:
            label_lines = f.read().strip().split("\n")

    augment_image(image, label_lines, output_img_dir, output_lbl_dir, base_name)

print("离线增强完成")
```

> **注意**：旋转增强会改变标注框的位置，上述简化脚本未处理旋转后的标注框坐标变换。对于精确的旋转增强，建议使用 YOLO11 内置的在线增强功能。

---

## 数据集质量检查

### 自动检查脚本

```python
import os

def check_dataset(dataset_path):
    issues = []

    images_dir = os.path.join(dataset_path, "images")
    labels_dir = os.path.join(dataset_path, "labels")

    for split in ["train", "val", "test"]:
        img_split_dir = os.path.join(images_dir, split)
        lbl_split_dir = os.path.join(labels_dir, split)

        if not os.path.exists(img_split_dir):
            issues.append(f"[缺失] {split} 图片目录不存在")
            continue

        img_files = set()
        for f in os.listdir(img_split_dir):
            ext = f.rsplit(".", 1)[-1].lower() if "." in f else ""
            if ext in {"png", "jpg", "jpeg", "bmp", "tiff", "webp"}:
                img_files.add(os.path.splitext(f)[0])

        lbl_files = set()
        if os.path.exists(lbl_split_dir):
            for f in os.listdir(lbl_split_dir):
                if f.endswith(".txt"):
                    lbl_files.add(os.path.splitext(f)[0])

        missing_labels = img_files - lbl_files
        if missing_labels:
            issues.append(f"[警告] {split} 有 {len(missing_labels)} 张图片缺少标注文件")

        missing_images = lbl_files - img_files
        if missing_images:
            issues.append(f"[警告] {split} 有 {len(missing_labels)} 个标注文件缺少对应图片")

        empty_labels = 0
        total_objects = 0
        class_counts = {}
        for name in lbl_files:
            lbl_path = os.path.join(lbl_split_dir, f"{name}.txt")
            with open(lbl_path, "r") as f:
                content = f.read().strip()
                if not content:
                    empty_labels += 1
                else:
                    for line in content.split("\n"):
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            cls_id = parts[0]
                            class_counts[cls_id] = class_counts.get(cls_id, 0) + 1
                            total_objects += 1

                            cx, cy, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                            if not (0 <= cx <= 1 and 0 <= cy <= 1 and 0 < w <= 1 and 0 < h <= 1):
                                issues.append(f"[错误] {split}/{name}.txt 存在越界坐标: cx={cx}, cy={cy}, w={w}, h={h}")

        print(f"\n{split} 集:")
        print(f"  图片数量: {len(img_files)}")
        print(f"  标注文件数: {len(lbl_files)}")
        print(f"  空标注文件: {empty_labels}")
        print(f"  标注目标总数: {total_objects}")
        print(f"  类别分布: {class_counts}")

    yaml_path = os.path.join(dataset_path, "data.yaml")
    if not os.path.exists(yaml_path):
        issues.append("[缺失] data.yaml 配置文件不存在")

    if issues:
        print(f"\n发现 {len(issues)} 个问题:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n数据集检查通过！")

    return issues


check_dataset("datasets/f00464ee")
```

### 质量检查清单

**1. 完整性检查**

- [ ] 每张图片都有对应的标注文件
- [ ] 每个标注文件都有对应的图片
- [ ] `data.yaml` 配置文件存在且格式正确
- [ ] 训练集、验证集、测试集目录都存在

**2. 标注质量检查**

- [ ] 无越界坐标（所有归一化坐标在 0-1 范围内）
- [ ] 无异常大的标注框（宽或高接近 1.0 可能标注不精确）
- [ ] 无异常小的标注框（宽或高 < 0.01 可能是误标）
- [ ] 类别 ID 在定义范围内（0 到 nc-1）

**3. 数据分布检查**

- [ ] 各类别样本数量均衡（最大类不超过最小类的 5 倍）
- [ ] 训练集、验证集、测试集的类别分布相似
- [ ] 正负样本比例合理（约 7:3）
- [ ] 训练集图片数量 ≥ 100（推荐 ≥ 500）

**4. 图片质量检查**

- [ ] 无损坏的图片文件
- [ ] 图片分辨率 ≥ 640×640
- [ ] 无过暗或过曝的图片
- [ ] 无严重模糊的图片

### 常见数据集问题

| 问题 | 症状 | 解决方案 |
|------|------|---------|
| 类别不均衡 | 某类别 mAP 极低 | 对少数类过采样或使用类别权重 |
| 标注不一致 | 同类裂缝标注方式不同 | 统一标注规范，重新审核 |
| 漏标 | 召回率低 | 补充标注，检查所有可见裂缝 |
| 误标 | 精确率低 | 审核标注，移除非裂缝标注 |
| 数据泄露 | 验证集指标虚高 | 确保训练集和验证集无重复图片 |
| 分辨率不一致 | 小图检测效果差 | 统一分辨率或使用多尺度训练 |
