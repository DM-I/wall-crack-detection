# 部署指南

## 系统要求

### 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|---------|---------|
| CPU | 4 核 | 8 核及以上 |
| 内存 | 8 GB | 16 GB 及以上 |
| 硬盘 | 20 GB 可用空间 | 100 GB SSD |
| GPU | 无（可 CPU 推理） | NVIDIA GPU，显存 ≥ 6 GB |

### 软件要求

| 软件 | 版本要求 | 说明 |
|------|---------|------|
| Python | 3.8 - 3.12 | 推荐 3.10 |
| pip | 最新版 | Python 包管理器 |
| Git | 最新版 | 可选，用于克隆代码 |
| CUDA | 11.8 或 12.x | GPU 加速所需（仅 NVIDIA GPU） |
| cuDNN | 8.x | GPU 加速所需（仅 NVIDIA GPU） |

### GPU 支持说明

GPU 加速可显著提升 YOLO11 的推理和训练速度。不同场景的 GPU 需求：

| 场景 | 推荐显存 | 说明 |
|------|---------|------|
| 仅推理（检测） | 2-4 GB | 可使用小模型实时推理 |
| 训练（小模型） | 6-8 GB | yolo11n/yolo11s 训练 |
| 训练（中等模型） | 12-16 GB | yolo11m/yolo11l 训练 |
| 训练（大模型） | 24 GB+ | yolo11x 训练 |

> **无 GPU 时**：系统可在 CPU 模式下运行，推理速度较慢但功能完整。训练在 CPU 上也可进行，但速度极慢，不推荐。

---

## 安装步骤

### 1. Python 环境准备

**Windows**

```powershell
# 下载并安装 Python 3.10
# https://www.python.org/downloads/release/python-31011/

# 安装时勾选 "Add Python to PATH"

# 验证安装
python --version
pip --version
```

**推荐使用虚拟环境**

```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 升级 pip
python -m pip install --upgrade pip
```

**Linux/macOS**

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip
```

### 2. 依赖安装

```powershell
# 进入项目目录
cd G:\bangong\qiangtijiance

# 安装依赖
pip install -r requirements.txt
```

`requirements.txt` 内容：

```
fastapi>=0.115.0
uvicorn>=0.30.0
python-multipart>=0.0.9
ultralytics>=8.3.0
opencv-python>=4.8.0
Pillow>=10.0.0
numpy>=1.23.0,<=2.1.1
dashscope>=1.20.0
jinja2>=3.1.0
python-dateutil>=2.8.0
```

**依赖说明**

| 包名 | 用途 |
|------|------|
| `fastapi` | Web 框架，提供 API 服务 |
| `uvicorn` | ASGI 服务器，运行 FastAPI 应用 |
| `python-multipart` | 处理文件上传 |
| `ultralytics` | YOLO11 框架，提供检测和训练功能 |
| `opencv-python` | 图像处理 |
| `Pillow` | 图像读写 |
| `numpy` | 数值计算 |
| `dashscope` | 阿里云 DashScope SDK，调用 QWEN-VL |
| `jinja2` | HTML 模板引擎 |
| `python-dateutil` | 日期处理 |

### 3. 模型下载

首次运行时，YOLO11 会自动下载预训练模型 `yolo11n.pt`。如需提前下载：

```python
from ultralytics import YOLO

model = YOLO("yolo11n.pt")
```

模型文件将下载到用户目录下的缓存文件夹中。

如需使用自定义训练的模型，将 `best.pt` 放置到 `weights/` 目录：

```powershell
# 创建 weights 目录（如不存在）
mkdir weights

# 复制模型文件
copy path\to\your\best.pt weights\best.pt
```

---

## 配置说明

所有配置项集中在 `config.py` 文件中。以下是各项配置的详细说明。

### 目录配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `UPLOAD_DIR` | `static/uploads/` | 上传图片存储目录 |
| `RESULT_DIR` | `static/results/` | 检测标注图输出目录 |
| `REPORT_DIR` | `static/reports/` | JSON 报告存储目录 |
| `VIDEO_FRAMES_DIR` | `static/video_frames/` | 视频帧提取目录 |
| `EXPORT_DIR` | `static/exports/` | 数据导出目录 |
| `DATASET_DIR` | `datasets/` | 数据集存储目录 |
| `TRAINING_DIR` | `training/` | 训练输出目录 |
| `WEIGHTS_DIR` | `weights/` | 模型权重目录 |
| `EVALUATION_DIR` | `evaluation/` | 评估结果目录 |

所有目录在系统启动时自动创建。

### YOLO 模型配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `YOLO_MODEL_PATH` | `weights/best.pt` | 自定义模型路径，优先加载 |
| `YOLO_MODEL_DEFAULT` | `yolo11n.pt` | 默认预训练模型 |
| `YOLO_CONF_THRESHOLD` | `0.25` | 默认置信度阈值 |
| `YOLO_IOU_THRESHOLD` | `0.45` | 默认 NMS IOU 阈值 |

**模型加载逻辑**：

```
启动 → weights/best.pt 是否存在？
         ├─ 是 → 加载自定义模型
         └─ 否 → 加载 yolo11n.pt 预训练模型（首次自动下载）
```

### QWEN-VL 配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `DASHSCOPE_API_KEY` | 环境变量 `DASHSCOPE_API_KEY` | 阿里云 DashScope API Key |
| `QWEN_MODEL` | `qwen-vl-max-latest` | QWEN 视觉语言模型版本 |

### 裂缝类别配置

```python
CRACK_CLASSES = {
    0: "横向裂缝",
    1: "纵向裂缝",
    2: "斜向裂缝",
    3: "网状裂缝",
    4: "裂缝",
}
```

使用自定义模型时，需根据模型训练数据集的类别定义修改此映射。

### 严重程度等级配置

```python
SEVERITY_LEVELS = {
    "轻微": {"color": "#22c55e", "description": "裂缝宽度<0.2mm，无需处理"},
    "一般": {"color": "#eab308", "description": "裂缝宽度0.2-0.5mm，需关注"},
    "严重": {"color": "#f97316", "description": "裂缝宽度0.5-2mm，需维修"},
    "危险": {"color": "#ef4444", "description": "裂缝宽度>2mm，需紧急处理"},
}
```

### 文件上传配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `ALLOWED_EXTENSIONS` | png, jpg, jpeg, bmp, tiff, webp | 允许上传的图片格式 |
| `ALLOWED_VIDEO_EXTENSIONS` | mp4, avi, mov, mkv, wmv, flv, webm | 允许上传的视频格式 |
| `MAX_FILE_SIZE` | 100 MB | 图片文件大小上限 |
| `MAX_VIDEO_FILE_SIZE` | 500 MB | 视频文件大小上限 |

### 视频处理配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `VIDEO_FRAME_INTERVAL` | 30 | 视频帧提取间隔（每 N 帧提取一帧） |
| `VIDEO_MAX_FRAMES` | 200 | 最大提取帧数 |

### 训练默认参数

```python
TRAINING_DEFAULTS = {
    "epochs": 100,
    "batch_size": 16,
    "imgsz": 640,
    "patience": 50,
    "lr0": 0.01,
    "lrf": 0.01,
    "momentum": 0.937,
    "weight_decay": 0.0005,
    "warmup_epochs": 3,
    "warmup_momentum": 0.8,
    "warmup_bias_lr": 0.1,
    "box": 7.5,
    "cls": 0.5,
    "dfl": 1.5,
    "label_smoothing": 0.0,
    "nbs": 64,
    "hsv_h": 0.015,
    "hsv_s": 0.7,
    "hsv_v": 0.4,
    "degrees": 0.0,
    "translate": 0.1,
    "scale": 0.5,
    "shear": 0.0,
    "perspective": 0.0,
    "flipud": 0.0,
    "fliplr": 0.5,
    "mosaic": 1.0,
    "mixup": 0.0,
    "copy_paste": 0.0,
}
```

### 数据集分割默认参数

```python
DATASET_SPLIT_DEFAULTS = {
    "train_ratio": 0.7,
    "val_ratio": 0.2,
    "test_ratio": 0.1,
}
```

---

## 启动服务

### 快捷启动（推荐）

项目根目录提供了三个批处理脚本：

| 脚本 | 功能 | 使用场景 |
|------|------|---------|
| `start.bat` | 启动服务 + 自动打开浏览器 | 每天开始工作 |
| `stop.bat` | 一键停止服务 | 需要重启或关闭服务 |
| `open.bat` | 仅打开浏览器 | 服务已在后台运行 |

**`start.bat` 工作流程**：
1. 检测端口 8000 是否已被占用 → 已运行则直接打开浏览器
2. 检查 Python 环境（支持 `python` 和 `py` 两种命令）
3. 后台启动服务（最小化窗口）
4. 轮询等待服务就绪
5. 自动打开浏览器访问 `http://localhost:8000`

### 服务重启与训练中断处理

服务重启时，系统会自动执行以下清理：

- 扫描 `training/` 目录，将状态为 `running` 或 `pending` 的训练标记为 `interrupted`
- 扫描 `evaluation/` 目录，将状态为 `running` 或 `pending` 的评估标记为 `interrupted`
- 前端列表中正确显示"已中断"标签，不会自动轮询

已中断的训练可通过训练页面的 **恢复训练** 功能从 `last.pt` 检查点继续。

### 开发模式

开发模式使用单进程，支持自动重载：

```powershell
cd G:\bangong\qiangtijiance
python app.py
```

默认监听地址：`http://0.0.0.0:8000`

访问 Web 界面：`http://localhost:8000`

### 生产模式

生产模式使用 Uvicorn 多进程，性能更优：

```powershell
cd G:\bangong\qiangtijiance
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

| 参数 | 说明 |
|------|------|
| `--host` | 监听地址，`0.0.0.0` 表示所有网卡 |
| `--port` | 监听端口 |
| `--workers` | 工作进程数，建议设为 CPU 核心数 |
| `--log-level` | 日志级别：debug/info/warning/error |
| `--access-log` | 启用访问日志 |
| `--ssl-keyfile` | SSL 私钥文件路径 |
| `--ssl-certfile` | SSL 证书文件路径 |

**HTTPS 配置示例**：

```powershell
uvicorn app:app --host 0.0.0.0 --port 443 \
  --ssl-keyfile /path/to/key.pem \
  --ssl-certfile /path/to/cert.pem
```

### 后台运行

**Linux（使用 nohup）**

```bash
nohup uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4 > server.log 2>&1 &
```

**Linux（使用 systemd）**

创建服务文件 `/etc/systemd/system/crack-detection.service`：

```ini
[Unit]
Description=Wall Crack Detection System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/qiangtijiance
ExecStart=/opt/qiangtijiance/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable crack-detection
sudo systemctl start crack-detection
sudo systemctl status crack-detection
```

**Windows（使用 NSSM）**

```powershell
# 安装 NSSM
# https://nssm.cc/download

# 创建服务
nssm install CrackDetection "G:\bangong\qiangtijiance\venv\Scripts\python.exe" "G:\bangong\qiangtijiance\app.py"

# 设置工作目录
nssm set CrackDetection AppDirectory "G:\bangong\qiangtijiance"

# 启动服务
nssm start CrackDetection
```

---

## DASHSCOPE_API_KEY 配置

QWEN-VL 视觉语言模型需要阿里云 DashScope API Key 才能使用。该 Key 用于调用 QWEN-VL 进行裂缝智能分析。

### 获取 API Key

1. 访问 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/)
2. 注册/登录阿里云账号
3. 开通 DashScope 服务
4. 在 API-KEY 管理页面创建新的 API Key

### 配置方式

**方式一：环境变量（推荐）**

```powershell
# Windows（临时，当前终端有效）
set DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx

# Windows（永久，写入系统环境变量）
setx DASHSCOPE_API_KEY "sk-xxxxxxxxxxxxxxxx"

# Linux/macOS（临时）
export DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx

# Linux/macOS（永久，写入 ~/.bashrc 或 ~/.zshrc）
echo 'export DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx' >> ~/.bashrc
source ~/.bashrc
```

**方式二：修改 config.py**

```python
DASHSCOPE_API_KEY = "sk-xxxxxxxxxxxxxxxx"
```

> ⚠️ 不推荐将 API Key 硬编码在代码中，存在安全风险。推荐使用环境变量方式。

### 无 API Key 时的行为

当 `DASHSCOPE_API_KEY` 为空时，系统自动切换到**模拟分析模式**：

- 基于 YOLO 检测结果生成合理推断
- 不调用外部 API，无网络延迟
- 分析结果中会标记 `"mock": True`
- 前端界面会显示提示信息

### 可用模型版本

| 模型名称 | 说明 | 适用场景 |
|----------|------|---------|
| `qwen-vl-max-latest` | 最新最强版本（默认） | 追求最佳分析质量 |
| `qwen-vl-max` | 稳定版最强模型 | 生产环境推荐 |
| `qwen-vl-plus` | 性价比版本 | 高频调用、成本敏感 |
| `qwen-vl-plus-latest` | 性价比最新版 | 平衡质量与成本 |

修改 `config.py` 中的 `QWEN_MODEL` 可切换模型版本。

---

## GPU 配置

### CUDA 安装

**1. 检查 GPU 型号**

```powershell
nvidia-smi
```

确认 GPU 驱动已安装，并查看支持的 CUDA 版本。

**2. 安装 CUDA Toolkit**

下载地址：[CUDA Toolkit Archive](https://developer.nvidia.com/cuda-toolkit-archive)

推荐版本：
- CUDA 11.8：兼容性最好
- CUDA 12.1：较新版本

**3. 安装 cuDNN**

下载地址：[cuDNN Archive](https://developer.nvidia.com/cudnn)

选择与 CUDA 版本对应的 cuDNN 版本。

### PyTorch GPU 版本

安装 PyTorch 时需选择与 CUDA 版本对应的包：

```powershell
# CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

> **注意**：`ultralytics` 包会自动安装 PyTorch，但默认安装 CPU 版本。如需 GPU 支持，需先手动安装 GPU 版本的 PyTorch，再安装 ultralytics。

### 验证 GPU 配置

```python
import torch

print(f"PyTorch 版本: {torch.__version__}")
print(f"CUDA 可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA 版本: {torch.version.cuda}")
    print(f"GPU 名称: {torch.cuda.get_device_name(0)}")
    print(f"GPU 显存: {torch.cuda.get_device_properties(0).total_mem / 1024**3:.1f} GB")
```

### GPU 常见问题

**1. CUDA not available**

```python
torch.cuda.is_available()  # 返回 False
```

解决方案：
- 确认已安装 NVIDIA GPU 驱动
- 确认已安装 CUDA Toolkit
- 确认安装了 GPU 版本的 PyTorch
- 检查 CUDA 版本与 PyTorch 版本是否匹配

**2. CUDA version mismatch**

```
RuntimeError: CUDA version mismatch
```

解决方案：
- 确保 CUDA Toolkit、PyTorch 和 GPU 驱动版本一致
- 重新安装匹配版本的 PyTorch

**3. Out of Memory**

```
RuntimeError: CUDA out of memory
```

解决方案：
- 减小 batch_size
- 减小 imgsz
- 使用更小的模型
- 关闭其他占用 GPU 的程序

---

## Docker 部署

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### GPU Docker 部署

如需 GPU 支持，使用 NVIDIA Docker 基础镜像：

```dockerfile
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose

**CPU 版本**

```yaml
version: '3.8'

services:
  crack-detection:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./datasets:/app/datasets
      - ./weights:/app/weights
      - ./training:/app/training
      - ./evaluation:/app/evaluation
      - ./static:/app/static
    environment:
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}
    restart: unless-stopped
```

**GPU 版本**

```yaml
version: '3.8'

services:
  crack-detection:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./datasets:/app/datasets
      - ./weights:/app/weights
      - ./training:/app/training
      - ./evaluation:/app/evaluation
      - ./static:/app/static
    environment:
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
```

### Docker 构建和运行

```powershell
# 构建镜像
docker build -t crack-detection .

# 运行容器（CPU）
docker run -d -p 8000:8000 -v %cd%/datasets:/app/datasets -v %cd%/weights:/app/weights crack-detection

# 运行容器（GPU）
docker run -d -p 8000:8000 --gpus all -v %cd%/datasets:/app/datasets -v %cd%/weights:/app/weights crack-detection

# 使用 docker-compose
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 环境变量配置

创建 `.env` 文件：

```
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx
```

docker-compose 会自动读取 `.env` 文件中的环境变量。

---

## 常见问题排查

### 1. 启动失败：端口被占用

```
OSError: [Errno 98] Address already in use
```

解决方案一（推荐）：双击 `stop.bat` 自动清理端口，再双击 `start.bat` 重新启动。

解决方案二（手动）：

```powershell
# 查看占用端口的进程
netstat -ano | findstr :8000

# 终止占用进程
taskkill /PID <进程ID> /F

# 或使用其他端口
python app.py  # 修改 app.py 中的 port 参数
```

### 2. 模型加载失败

```
FileNotFoundError: weights/best.pt does not exist
```

解决方案：
- 系统会自动回退到 `yolo11n.pt` 预训练模型
- 如需使用自定义模型，确保 `weights/best.pt` 文件存在

### 3. 依赖安装失败

**opencv-python 安装失败**

```powershell
# 尝试使用 headless 版本
pip install opencv-python-headless
```

**ultralytics 安装失败**

```powershell
# 确保 numpy 版本兼容
pip install "numpy>=1.23.0,<=2.1.1"
pip install ultralytics
```

### 4. 图片上传失败

- 检查图片格式是否在 `ALLOWED_EXTENSIONS` 中
- 检查图片大小是否超过 `MAX_FILE_SIZE`（100MB）
- 检查 `static/uploads/` 目录是否有写入权限

### 5. QWEN-VL 分析失败

- 检查 `DASHSCOPE_API_KEY` 是否正确配置
- 检查网络是否能访问 DashScope API
- 检查 API Key 是否有效且有足够额度
- 无 API Key 时系统会自动使用模拟模式

### 6. 训练速度极慢

- 确认是否使用了 GPU（检查 `torch.cuda.is_available()`）
- 如果只能使用 CPU，减小 `batch_size` 和 `imgsz`
- 考虑使用更小的模型（如 yolo11n.pt）

### 7. 内存不足

```
MemoryError
```

解决方案：
- 减小 `batch_size`
- 减小 `imgsz`
- 减少同时处理的图片数量
- 增加系统虚拟内存

### 8. 中文乱码

确保所有文件使用 UTF-8 编码：

```python
# 读取文件时指定编码
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 写入文件时指定编码
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
```

### 9. 跨域问题

默认配置允许所有来源的跨域请求。生产环境建议限制来源：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```
