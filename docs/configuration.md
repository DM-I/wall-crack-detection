# 配置说明

所有配置项集中在 `config.py` 文件中，通过修改该文件可以调整系统行为。

## 目录配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `UPLOAD_DIR` | `static/uploads/` | 上传图片的存储目录 |
| `RESULT_DIR` | `static/results/` | YOLO 检测标注图的输出目录 |
| `REPORT_DIR` | `static/reports/` | 生成的 JSON 报告存储目录 |
| `VIDEO_FRAMES_DIR` | `static/video_frames/` | 视频帧提取的输出目录 |
| `EXPORT_DIR` | `static/exports/` | 标注/报告导出目录 |
| `DATASET_DIR` | `datasets/` | 数据集存储目录 |
| `TRAINING_DIR` | `training/` | 训练输出目录 |
| `WEIGHTS_DIR` | `weights/` | 自定义模型权重目录 |
| `EVALUATION_DIR` | `evaluation/` | 评估结果目录 |

这些目录在系统启动时会自动创建（`os.makedirs(..., exist_ok=True)`）。

**自定义示例**：

```python
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "input")
RESULT_DIR = os.path.join(BASE_DIR, "data", "output")
REPORT_DIR = os.path.join(BASE_DIR, "data", "reports")
```

## YOLO 模型配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `YOLO_MODEL_PATH` | `weights/best.pt` | 自定义裂缝检测模型路径，存在时优先加载 |
| `YOLO_MODEL_DEFAULT` | `yolo11n.pt` | 默认预训练模型（通用目标检测） |
| `YOLO_CONF_THRESHOLD` | `0.25` | 默认置信度阈值，范围 0-1 |
| `YOLO_IOU_THRESHOLD` | `0.45` | 默认 NMS IOU 阈值，范围 0-1 |

### 模型加载逻辑

```
启动 → weights/best.pt 是否存在？
         ├─ 是 → 加载自定义模型
         └─ 否 → 加载 yolo11n.pt 预训练模型（首次自动下载）
```

### 置信度阈值调优建议

| 场景 | 推荐值 | 说明 |
|------|--------|------|
| 初步筛查 | 0.15 - 0.25 | 高召回率，不遗漏潜在裂缝 |
| 常规检测 | 0.25 - 0.40 | 平衡精确率与召回率 |
| 严格检测 | 0.40 - 0.60 | 高精确率，减少误检 |
| 精确验证 | 0.60 - 0.80 | 仅保留高置信度结果 |

### IOU 阈值调优建议

| 场景 | 推荐值 | 说明 |
|------|--------|------|
| 密集裂缝 | 0.30 - 0.40 | 更激进地去除重叠框 |
| 常规场景 | 0.40 - 0.50 | 默认值，适用于大多数情况 |
| 稀疏裂缝 | 0.50 - 0.70 | 保留更多独立检测框 |

## QWEN-VL 配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `DASHSCOPE_API_KEY` | 环境变量 `DASHSCOPE_API_KEY` | 阿里云 DashScope API Key |
| `QWEN_MODEL` | `qwen-vl-max-latest` | 使用的 QWEN 视觉语言模型版本 |

### 可用模型版本

| 模型名称 | 说明 | 适用场景 |
|----------|------|---------|
| `qwen-vl-max-latest` | 最新最强版本（默认） | 追求最佳分析质量 |
| `qwen-vl-max` | 稳定版最强模型 | 生产环境推荐 |
| `qwen-vl-plus` | 性价比版本 | 高频调用、成本敏感 |
| `qwen-vl-plus-latest` | 性价比最新版 | 平衡质量与成本 |

### API Key 配置方式

**方式一：环境变量（推荐）**

```bash
# Windows（临时）
set DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx

# Windows（永久，写入系统环境变量）
setx DASHSCOPE_API_KEY "sk-xxxxxxxxxxxxxxxx"

# Linux/macOS（临时）
export DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx

# Linux/macOS（永久，写入 ~/.bashrc 或 ~/.zshrc）
echo 'export DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx' >> ~/.bashrc
```

**方式二：直接修改 config.py**

```python
DASHSCOPE_API_KEY = "sk-xxxxxxxxxxxxxxxx"
```

> ⚠️ 不推荐将 API Key 硬编码在代码中，存在安全风险。

### 无 API Key 时的行为

当 `DASHSCOPE_API_KEY` 为空时，系统自动切换到**模拟分析模式**：

- 基于 YOLO 检测结果生成合理推断
- 不调用外部 API，无网络延迟
- 分析结果中会标记 `"mock": True`
- 前端界面会显示黄色提示条

## 裂缝类别配置

```python
CRACK_CLASSES = {
    0: "横向裂缝",
    1: "纵向裂缝",
    2: "斜向裂缝",
    3: "网状裂缝",
    4: "裂缝",
}
```

此映射定义了 YOLO 检测结果的类别 ID 到中文名称的对应关系。**使用自定义模型时，需根据模型训练数据集的类别定义修改此映射**。

例如，如果你的自定义模型类别为：

```
0: crack
1: spalling
2: efflorescence
```

则应修改为：

```python
CRACK_CLASSES = {
    0: "裂缝",
    1: "剥落",
    2: "风化",
}
```

## 严重程度等级配置

```python
SEVERITY_LEVELS = {
    "轻微": {"color": "#22c55e", "description": "裂缝宽度<0.2mm，无需处理"},
    "一般": {"color": "#eab308", "description": "裂缝宽度0.2-0.5mm，需关注"},
    "严重": {"color": "#f97316", "description": "裂缝宽度0.5-2mm，需维修"},
    "危险": {"color": "#ef4444", "description": "裂缝宽度>2mm，需紧急处理"},
}
```

此配置影响：
- 前端界面中严重程度的颜色显示
- 报告中严重程度的描述文字
- 建议的紧急处理程度

可根据实际工程标准调整裂缝宽度阈值和描述。

## 文件上传配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `ALLOWED_EXTENSIONS` | `png, jpg, jpeg, bmp, tiff, webp` | 允许上传的图片格式 |
| `ALLOWED_VIDEO_EXTENSIONS` | `mp4, avi, mov, mkv, wmv, flv, webm` | 允许上传的视频格式 |
| `MAX_FILE_SIZE` | `104857600`（100MB） | 上传图片最大字节数 |
| `MAX_VIDEO_FILE_SIZE` | `524288000`（500MB） | 上传视频最大字节数 |
| `VIDEO_FRAME_INTERVAL` | `30` | 视频帧提取间隔 |
| `VIDEO_MAX_FRAMES` | `200` | 视频最大提取帧数 |

**调整最大文件大小示例**：

```python
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_VIDEO_FILE_SIZE = 1024 * 1024 * 1024  # 1GB
```

**添加新格式支持**：

```python
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tiff", "webp", "tif", "dng"}
```

## 训练默认参数

`TRAINING_DEFAULTS` 字典定义了训练任务的默认超参数，用户可在 Web 界面或 API 调用时覆盖：

```python
TRAINING_DEFAULTS = {
    "epochs": 100,        # 训练轮数
    "batch_size": 16,     # 批次大小
    "imgsz": 640,         # 输入图片尺寸
    "patience": 50,       # 早停耐心值
    "lr0": 0.01,          # 初始学习率
    "lrf": 0.01,          # 最终学习率因子
    "momentum": 0.937,    # SGD 动量
    "weight_decay": 0.0005,  # 权重衰减
    "warmup_epochs": 3,   # 学习率预热轮数
    # ... 更多参数见 config.py
}
```

## 数据集分割默认参数

```python
DATASET_SPLIT_DEFAULTS = {
    "train_ratio": 0.7,   # 训练集比例
    "val_ratio": 0.2,     # 验证集比例
    "test_ratio": 0.1,    # 测试集比例
}
```

## 服务器配置

服务器参数在 `app.py` 末尾配置：

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `host` | `0.0.0.0` | 监听地址，`0.0.0.0` 表示所有网卡 |
| `port` | `8000` | 监听端口 |

**生产环境推荐启动方式**：

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 2
```

| Uvicorn 参数 | 说明 |
|-------------|------|
| `--workers N` | 工作进程数，建议设为 CPU 核心数 |
| `--log-level` | 日志级别：`debug`/`info`/`warning`/`error` |
| `--access-log` | 启用访问日志 |
| `--ssl-keyfile` | SSL 私钥文件路径 |
| `--ssl-certfile` | SSL 证书文件路径 |

## CORS 跨域配置

默认允许所有来源的跨域请求：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**生产环境建议限制来源**：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```
