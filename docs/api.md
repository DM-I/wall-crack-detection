# API 接口文档

基础地址：`http://localhost:8000`

---

## 1. 主页面

### `GET /`

返回 Web 界面 HTML 页面。

**响应**：`text/html`

---

## 2. 上传图片

### `POST /api/upload`

上传图片到服务器，返回文件信息。

**请求**：`multipart/form-data`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | File | 是 | 图片文件 |

**成功响应**：

```json
{
    "success": true,
    "filename": "a1b2c3d4_wall.jpg",
    "file_path": "G:\\bangong\\qiangtijiance\\static\\uploads\\a1b2c3d4_wall.jpg",
    "file_size": 245678
}
```

**错误响应**：

| 状态码 | 说明 |
|--------|------|
| 400 | 文件格式不支持 |
| 400 | 文件大小超过限制 |

---

## 3. 裂缝检测

### `POST /api/detect`

仅执行 YOLO11 裂缝检测，不进行 QWEN-VL 分析。

**请求**：`multipart/form-data`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `file` | File | 是 | - | 图片文件 |
| `conf` | float | 否 | 0.25 | 置信度阈值 (0-1) |
| `iou` | float | 否 | 0.45 | NMS IOU 阈值 (0-1) |

**成功响应**：

```json
{
    "success": true,
    "result": {
        "detections": [
            {
                "class_id": 0,
                "class_name": "横向裂缝",
                "confidence": 0.8732,
                "bbox": {
                    "x1": 120.5,
                    "y1": 200.3,
                    "x2": 450.8,
                    "y2": 280.6
                },
                "width": 330.3,
                "height": 80.3,
                "area": 26523.09
            }
        ],
        "total_count": 1,
        "annotated_image": "G:\\bangong\\qiangtijiance\\static\\results\\a1b2c3d4_wall_detected.jpg",
        "annotated_image_url": "/static/results/a1b2c3d4_wall_detected.jpg",
        "image_size": {
            "width": 1920,
            "height": 1080
        },
        "summary": {
            "has_crack": true,
            "severity": "严重",
            "class_distribution": {
                "横向裂缝": 1
            },
            "max_confidence": 0.8732,
            "max_area": 26523.09
        }
    }
}
```

### 检测结果字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `detections` | Array | 检测到的裂缝列表 |
| `detections[].class_id` | int | 类别 ID |
| `detections[].class_name` | string | 类别名称 |
| `detections[].confidence` | float | 检测置信度 (0-1) |
| `detections[].bbox` | Object | 边界框坐标 (像素) |
| `detections[].width` | float | 检测框宽度 (像素) |
| `detections[].height` | float | 检测框高度 (像素) |
| `detections[].area` | float | 检测框面积 (像素²) |
| `total_count` | int | 检测到的裂缝总数 |
| `annotated_image` | string | 标注图的服务器绝对路径 |
| `annotated_image_url` | string | 标注图的 URL 访问路径 |
| `image_size` | Object | 原图尺寸 |
| `summary` | Object | 检测摘要信息 |
| `summary.has_crack` | bool | 是否检测到裂缝 |
| `summary.severity` | string | 严重程度（轻微/一般/严重/危险/无） |
| `summary.class_distribution` | Object | 各类型裂缝数量统计 |
| `summary.max_confidence` | float | 最大置信度 |
| `summary.max_area` | float | 最大检测框面积 |

---

## 4. 完整分析（检测 + AI 分析 + 报告）

### `POST /api/analyze`

执行完整的检测分析流程：YOLO11 检测 → QWEN-VL 分析 → 报告生成。

**请求**：`multipart/form-data`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `file` | File | 是 | - | 图片文件 |
| `conf` | float | 否 | 0.25 | 置信度阈值 (0-1) |
| `iou` | float | 否 | 0.45 | NMS IOU 阈值 (0-1) |
| `project_name` | string | 否 | "墙体裂缝检测项目" | 项目名称 |
| `location` | string | 否 | "待填写" | 检测位置 |
| `inspector` | string | 否 | "AI自动检测" | 检测人员 |

**成功响应**：

```json
{
    "success": true,
    "detection": {
        "detections": [...],
        "total_count": 2,
        "annotated_image": "...",
        "annotated_image_url": "...",
        "image_size": {"width": 1920, "height": 1080},
        "summary": {...}
    },
    "analysis": {
        "success": true,
        "analysis": {
            "crack_found": true,
            "crack_description": "检测到2处裂缝...",
            "crack_types": ["横向裂缝", "斜向裂缝"],
            "severity": "严重",
            "estimated_width": "0.5-2mm",
            "possible_causes": ["温度应力", "材料收缩", "地基沉降"],
            "risk_assessment": "检测到严重程度裂缝...",
            "risk_level": "高",
            "repair_suggestions": ["对裂缝进行标记和记录", "..."],
            "urgency": "尽快处理",
            "professional_opinion": "墙体存在严重程度裂缝..."
        },
        "detection_info": {...},
        "mock": false
    },
    "report": {
        "report_id": "a1b2c3d4",
        "report_title": "墙体裂缝检测审核报告",
        "generated_at": "2026-05-22 10:30:00",
        "project_info": {...},
        "image_info": {...},
        "detection_summary": {...},
        "detection_details": [...],
        "ai_analysis": {...},
        "conclusion": "经YOLO11目标检测与QWEN-VL视觉语言模型联合分析...",
        "recommendations": [...],
        "report_path": "..."
    }
}
```

### 分析结果字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `analysis.success` | bool | 分析是否成功 |
| `analysis.analysis` | Object | QWEN-VL 分析结果 |
| `analysis.analysis.crack_found` | bool | 是否发现裂缝 |
| `analysis.analysis.crack_description` | string | 裂缝详细描述 |
| `analysis.analysis.crack_types` | Array | 裂缝类型列表 |
| `analysis.analysis.severity` | string | 严重程度 |
| `analysis.analysis.estimated_width` | string | 预估裂缝宽度范围 |
| `analysis.analysis.possible_causes` | Array | 可能原因列表 |
| `analysis.analysis.risk_assessment` | string | 风险评估描述 |
| `analysis.analysis.risk_level` | string | 风险等级（低/中/高/极高） |
| `analysis.analysis.repair_suggestions` | Array | 修复建议列表 |
| `analysis.analysis.urgency` | string | 紧急程度 |
| `analysis.analysis.professional_opinion` | string | 专业综合意见 |
| `analysis.mock` | bool | 是否为模拟分析（无 API Key 时为 true） |

---

## 5. 按路径分析

### `POST /api/analyze_path`

对服务器本地路径的图片执行完整分析，无需上传文件。

**请求**：`multipart/form-data` 或 `application/x-www-form-urlencoded`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `image_path` | string | 是 | - | 服务器本地图片绝对路径 |
| `conf` | float | 否 | 0.25 | 置信度阈值 |
| `iou` | float | 否 | 0.45 | IOU 阈值 |
| `project_name` | string | 否 | "墙体裂缝检测项目" | 项目名称 |
| `location` | string | 否 | "待填写" | 检测位置 |
| `inspector` | string | 否 | "AI自动检测" | 检测人员 |

**响应格式**：与 `/api/analyze` 相同

**错误响应**：

| 状态码 | 说明 |
|--------|------|
| 400 | 图片文件不存在 |

---

## 6. 获取报告列表

### `GET /api/reports`

获取所有已生成报告的摘要列表。

**响应**：

```json
{
    "reports": [
        {
            "report_id": "a1b2c3d4",
            "generated_at": "2026-05-22 10:30:00",
            "severity": "严重",
            "total_cracks": 2
        },
        {
            "report_id": "e5f6g7h8",
            "generated_at": "2026-05-22 09:15:00",
            "severity": "一般",
            "total_cracks": 1
        }
    ]
}
```

列表按生成时间倒序排列。

---

## 7. 获取报告详情

### `GET /api/report/{report_id}`

根据报告 ID 获取完整报告内容。

**路径参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `report_id` | string | 报告 ID（8位十六进制字符串） |

**响应**：完整的报告 JSON 对象

```json
{
    "report_id": "a1b2c3d4",
    "report_title": "墙体裂缝检测审核报告",
    "generated_at": "2026-05-22 10:30:00",
    "project_info": {
        "project_name": "墙体裂缝检测项目",
        "location": "3号楼2层",
        "inspector": "张工"
    },
    "image_info": {
        "filename": "a1b2c3d4_wall.jpg",
        "image_size": {"width": 1920, "height": 1080}
    },
    "detection_summary": {
        "total_cracks": 2,
        "has_crack": true,
        "severity": "严重",
        "severity_color": "#f97316",
        "severity_description": "裂缝宽度0.5-2mm，需维修",
        "class_distribution": {"横向裂缝": 1, "斜向裂缝": 1},
        "max_confidence": 0.8732
    },
    "detection_details": [...],
    "ai_analysis": {
        "crack_found": true,
        "crack_description": "...",
        "crack_types": [...],
        "estimated_width": "...",
        "possible_causes": [...],
        "risk_assessment": "...",
        "risk_level": "高",
        "repair_suggestions": [...],
        "urgency": "尽快处理",
        "professional_opinion": "..."
    },
    "conclusion": "经YOLO11目标检测与QWEN-VL视觉语言模型联合分析...",
    "recommendations": [...]
}
```

**错误响应**：

| 状态码 | 说明 |
|--------|------|
| 404 | 报告不存在 |

---

## 8. 静态文件访问

### `GET /static/{path}`

访问静态资源文件，包括上传的图片、检测结果图等。

**常用路径**：

| 路径 | 说明 |
|------|------|
| `/static/uploads/{filename}` | 访问上传的原始图片 |
| `/static/results/{filename}` | 访问 YOLO 检测标注图 |
| `/static/reports/{filename}` | 访问 JSON 报告文件 |

---

## 调用示例

### cURL

**上传并分析**：

```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@wall_crack.jpg" \
  -F "conf=0.3" \
  -F "iou=0.45" \
  -F "project_name=3号楼检测" \
  -F "location=2层走廊" \
  -F "inspector=张工"
```

**仅检测**：

```bash
curl -X POST http://localhost:8000/api/detect \
  -F "file=@wall_crack.jpg" \
  -F "conf=0.25"
```

**获取报告列表**：

```bash
curl http://localhost:8000/api/reports
```

**获取报告详情**：

```bash
curl http://localhost:8000/api/report/a1b2c3d4
```

### Python (requests)

```python
import requests

url = "http://localhost:8000/api/analyze"

with open("wall_crack.jpg", "rb") as f:
    response = requests.post(url, data={
        "conf": 0.3,
        "iou": 0.45,
        "project_name": "3号楼检测",
        "location": "2层走廊",
        "inspector": "张工",
    }, files={"file": f})

result = response.json()
print(f"检测到 {result['detection']['total_count']} 处裂缝")
print(f"严重程度: {result['report']['detection_summary']['severity']}")
print(f"报告ID: {result['report']['report_id']}")
```

### JavaScript (fetch)

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('conf', '0.3');
formData.append('iou', '0.45');
formData.append('project_name', '3号楼检测');
formData.append('location', '2层走廊');
formData.append('inspector', '张工');

const response = await fetch('/api/analyze', {
    method: 'POST',
    body: formData
});

const data = await response.json();
console.log('检测裂缝数:', data.detection.total_count);
console.log('严重程度:', data.report.detection_summary.severity);
```

---

## 9. 批量分析

### `POST /api/analyze_batch`

对多张图片执行批量检测分析。

**请求**：`multipart/form-data`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `files` | File[] | 是 | - | 多个图片文件 |
| `conf` | float | 否 | 0.25 | 置信度阈值 |
| `iou` | float | 否 | 0.45 | IOU 阈值 |
| `project_name` | string | 否 | - | 项目名称 |
| `location` | string | 否 | - | 检测位置 |
| `inspector` | string | 否 | - | 检测人员 |

---

## 10. 视频分析

### `POST /api/analyze_video`

对视频文件进行逐帧裂缝检测分析。

**请求**：`multipart/form-data`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `file` | File | 是 | - | 视频文件 |
| `conf` | float | 否 | 0.25 | 置信度阈值 |
| `iou` | float | 否 | 0.45 | IOU 阈值 |
| `frame_interval` | int | 否 | 30 | 帧提取间隔 |
| `project_name` | string | 否 | - | 项目名称 |
| `location` | string | 否 | - | 检测位置 |
| `inspector` | string | 否 | - | 检测人员 |

支持的视频格式：mp4, avi, mov, mkv, wmv, flv, webm（最大 500MB）

---

## 11. 导出标注数据

### `POST /api/export/{report_id}`

导出报告的标注数据和图片。

**请求**：`multipart/form-data`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `format` | string | 否 | all | 导出格式（yolo/coco/all） |

**响应**：ZIP 文件下载

---

## 12. 训练管理 API

### `POST /api/train/start`
启动模型训练。详见 [训练模块使用指南](training_guide.md)。

### `GET /api/train/status/{training_id}`
获取训练状态。

| 状态值 | 说明 |
|--------|------|
| `pending` | 等待启动 |
| `running` | 训练进行中 |
| `completed` | 训练已完成 |
| `failed` | 训练失败 |
| `stopped` | 已手动停止 |
| `interrupted` | 服务重启导致中断（可恢复训练） |

### `GET /api/train/progress/{training_id}`
获取训练实时进度（epoch、loss、mAP 等）。

### `GET /api/train/curves/{training_id}`
获取训练曲线数据。

### `POST /api/train/stop/{training_id}`
停止正在进行的训练。

### `POST /api/train/resume/{training_id}`
从检查点恢复已中断的训练。

### `GET /api/train/list`
获取所有训练记录列表。

### `DELETE /api/train/{training_id}`
删除训练记录及输出文件。

### `GET /api/train/models`
获取可用模型列表（预训练 + 自定义 + 已训练）。

---

## 13. 评估管理 API

### `POST /api/eval/start`
启动模型评估。详见 [评估模块使用指南](evaluation_guide.md)。

### `GET /api/eval/list`
获取评估记录列表。

| 状态值 | 说明 |
|--------|------|
| `pending` | 等待启动 |
| `running` | 评估进行中 |
| `completed` | 评估已完成 |
| `failed` | 评估失败 |
| `interrupted` | 服务重启导致中断 |

### `GET /api/eval/{eval_id}`
获取评估详情。

### `DELETE /api/eval/{eval_id}`
删除评估记录。

### `POST /api/eval/compare`
多模型横向对比评估。

---

## 14. 数据集管理 API

### `GET /api/datasets`
获取数据集列表。

### `POST /api/datasets`
创建新数据集。

### `GET /api/datasets/{dataset_id}`
获取数据集详情。

### `DELETE /api/datasets/{dataset_id}`
删除数据集。

### `GET /api/datasets/{dataset_id}/images`
获取数据集图片列表。

### `POST /api/datasets/{dataset_id}/images`
上传图片到数据集。

### `GET /api/datasets/{dataset_id}/images/{filename}/annotations`
获取图片标注数据。

### `POST /api/datasets/{dataset_id}/images/{filename}/annotations`
保存图片标注数据。

### `POST /api/datasets/{dataset_id}/auto_annotate`
使用 YOLO 模型自动标注数据集。

### `POST /api/datasets/{dataset_id}/split`
分割数据集为训练/验证/测试集。

### `POST /api/datasets/{dataset_id}/export`
导出数据集（支持 YOLO/COCO 格式）。

---

## 错误码汇总

| HTTP 状态码 | 场景 |
|-------------|------|
| 200 | 请求成功 |
| 400 | 文件格式不支持 / 文件过大 / 图片路径不存在 / 参数无效 |
| 404 | 报告不存在 / 训练记录不存在 / 评估记录不存在 |
| 422 | 请求参数验证失败 |
| 500 | 服务器内部错误 |
