import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
RESULT_DIR = os.path.join(BASE_DIR, "static", "results")
REPORT_DIR = os.path.join(BASE_DIR, "static", "reports")
VIDEO_FRAMES_DIR = os.path.join(BASE_DIR, "static", "video_frames")
EXPORT_DIR = os.path.join(BASE_DIR, "static", "exports")

DATASET_DIR = os.path.join(BASE_DIR, "datasets")
TRAINING_DIR = os.path.join(BASE_DIR, "training")
WEIGHTS_DIR = os.path.join(BASE_DIR, "weights")
EVALUATION_DIR = os.path.join(BASE_DIR, "evaluation")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(VIDEO_FRAMES_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs(TRAINING_DIR, exist_ok=True)
os.makedirs(WEIGHTS_DIR, exist_ok=True)
os.makedirs(EVALUATION_DIR, exist_ok=True)

YOLO_MODEL_PATH = os.path.join(BASE_DIR, "weights", "best.pt")
YOLO_MODEL_DEFAULT = "yolo11n.pt"

YOLO_CONF_THRESHOLD = 0.25
YOLO_IOU_THRESHOLD = 0.45

# 裂缝尺寸测量校准参数 (pixels per mm)
# 取决于拍摄距离和相机参数，用户可通过 API 传入覆盖
PIXELS_PER_MM = 5.0  # 默认每毫米5像素（约200mm宽墙面在1000px图像中）
CRACK_WIDTH_MIN_MM = 0.05  # 最小可检测裂缝宽度 (mm)

DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
QWEN_MODEL = "qwen-vl-max-latest"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tiff", "webp"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "avi", "mov", "mkv", "wmv", "flv", "webm"}
MAX_FILE_SIZE = 100 * 1024 * 1024
MAX_VIDEO_FILE_SIZE = 500 * 1024 * 1024

VIDEO_FRAME_INTERVAL = 30
VIDEO_MAX_FRAMES = 200

CRACK_CLASSES = {
    0: "横向裂缝",
    1: "纵向裂缝",
    2: "斜向裂缝",
    3: "网状裂缝",
    4: "裂缝",
}

SEVERITY_LEVELS = {
    "轻微": {"color": "#22c55e", "description": "裂缝宽度<0.2mm，无需处理"},
    "一般": {"color": "#eab308", "description": "裂缝宽度0.2-0.5mm，需关注"},
    "严重": {"color": "#f97316", "description": "裂缝宽度0.5-2mm，需维修"},
    "危险": {"color": "#ef4444", "description": "裂缝宽度>2mm，需紧急处理"},
}

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
    "pose": 12.0,
    "kobj": 2.0,
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

DATASET_SPLIT_DEFAULTS = {
    "train_ratio": 0.7,
    "val_ratio": 0.2,
    "test_ratio": 0.1,
}
