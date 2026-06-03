import os
import io
import json
import uuid
import zipfile
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder

app = FastAPI(title="墙体裂缝检测与审核报告系统", version="3.0.0")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": str(exc), "type": "validation_error"})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": str(exc), "type": type(exc).__name__})


from config import (
    UPLOAD_DIR, RESULT_DIR, REPORT_DIR, EXPORT_DIR,
    DATASET_DIR, TRAINING_DIR, EVALUATION_DIR, WEIGHTS_DIR,
    ALLOWED_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS, MAX_FILE_SIZE, MAX_VIDEO_FILE_SIZE,
)
from models.detector import CrackDetector
from models.analyzer import QwenVLAnalyzer
from models.annotator import Annotator
from models.trainer import Trainer
from models.evaluator import Evaluator
from services.report import ReportGenerator

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
app.mount("/datasets", StaticFiles(directory=DATASET_DIR), name="datasets")

detector = CrackDetector()
analyzer = QwenVLAnalyzer()
report_generator = ReportGenerator()
annotator = Annotator()
trainer = Trainer()
evaluator = Evaluator()


def _check_file(file: UploadFile):
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式: .{ext}，支持: {', '.join(ALLOWED_EXTENSIONS)}")


def _check_video_file(file: UploadFile):
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的视频格式: .{ext}，支持: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}")


def _render_template(name):
    html_path = os.path.join(os.path.dirname(__file__), "templates", name)
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})


@app.get("/")
async def index():
    return _render_template("index.html")


@app.get("/annotation")
async def annotation_page():
    return _render_template("annotation.html")


@app.get("/training")
async def training_page():
    return _render_template("training.html")


@app.get("/evaluation")
async def evaluation_page():
    return _render_template("evaluation.html")


# ==================== Detection APIs ====================

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    _check_file(file)
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"文件大小超过限制({MAX_FILE_SIZE // 1024 // 1024}MB)")
    file_id = str(uuid.uuid4())[:8]
    filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(contents)
    return {"success": True, "filename": filename, "file_path": file_path, "file_size": len(contents)}


@app.post("/api/detect")
async def detect_cracks(file: UploadFile = File(...), conf: float = Form(0.25), iou: float = Form(0.45), model_path: str = Form(""), pixels_per_mm: float = Form(0)):
    _check_file(file)
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过限制")
    file_id = str(uuid.uuid4())[:8]
    filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(contents)
    det = detector
    if model_path and os.path.exists(model_path):
        from models.detector import CrackDetector as _CD
        det = _CD.__new__(_CD)
        det.model = None
        from ultralytics import YOLO
        det.model = YOLO(model_path)
    ppm = pixels_per_mm if pixels_per_mm > 0 else None
    result = det.detect(file_path, conf_threshold=conf, iou_threshold=iou, pixels_per_mm=ppm)
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    annotated_rel = os.path.relpath(result["annotated_image"], static_dir)
    result["annotated_image_url"] = f"/static/{annotated_rel.replace(os.sep, '/')}"
    return {"success": True, "result": result}


@app.post("/api/detect_with_model")
async def detect_with_model(request: Request):
    body = {}
    try:
        raw = await request.body()
        if raw:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                body = json.loads(raw.decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"请求解析失败: {str(e)}")

    model_path = body.get("model_path", "")
    image_path = body.get("image_path", "")
    conf = float(body.get("conf", 0.25))
    iou = float(body.get("iou", 0.45))

    if not model_path:
        raise HTTPException(status_code=400, detail="请指定模型路径")
    if not os.path.exists(model_path):
        raise HTTPException(status_code=400, detail=f"模型文件不存在: {model_path}")
    if not image_path or not os.path.exists(image_path):
        raise HTTPException(status_code=400, detail="图片路径不存在")

    from ultralytics import YOLO
    model = YOLO(model_path)
    results = model(image_path, conf=conf, iou=iou, verbose=False)
    result_obj = results[0]

    detections = []
    if result_obj.boxes is not None and len(result_obj.boxes) > 0:
        for box in result_obj.boxes:
            cls_id = int(box.cls[0])
            confidence = float(box.conf[0])
            xyxy = box.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = map(float, xyxy)
            cls_name = result_obj.names.get(cls_id, f"class_{cls_id}")
            detections.append({
                "class_id": cls_id,
                "class_name": cls_name,
                "confidence": round(confidence, 4),
                "bbox": {"x1": round(x1, 2), "y1": round(y1, 2), "x2": round(x2, 2), "y2": round(y2, 2)},
            })

    import cv2
    annotated = result_obj.plot()
    basename = os.path.splitext(os.path.basename(image_path))[0]
    output_path = os.path.join(RESULT_DIR, f"{basename}_custom_detected.jpg")
    cv2.imwrite(output_path, annotated)
    annotated_rel = os.path.relpath(output_path, os.path.dirname(os.path.abspath(__file__)))
    url_path = annotated_rel.replace(os.sep, '/')
    if url_path.startswith('static/'):
        url_path = url_path[len('static/'):]

    return {
        "success": True,
        "model_path": model_path,
        "detections": detections,
        "total_count": len(detections),
        "annotated_image_url": f"/static/{url_path}",
    }


@app.post("/api/analyze")
async def analyze_image(
    file: UploadFile = File(...), conf: float = Form(0.25), iou: float = Form(0.45),
    project_name: str = Form("墙体裂缝检测项目"), location: str = Form("待填写"), inspector: str = Form("AI自动检测"),
    model_path: str = Form(""), pixels_per_mm: float = Form(0),
):
    _check_file(file)
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过限制")
    file_id = str(uuid.uuid4())[:8]
    filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(contents)
    det = detector
    if model_path and os.path.exists(model_path):
        from models.detector import CrackDetector as _CD
        from ultralytics import YOLO
        det = _CD.__new__(_CD)
        det.model = None
        det.model = YOLO(model_path)
    ppm = pixels_per_mm if pixels_per_mm > 0 else None
    detection_result = det.detect(file_path, conf_threshold=conf, iou_threshold=iou, pixels_per_mm=ppm)
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    annotated_rel = os.path.relpath(detection_result["annotated_image"], static_dir)
    detection_result["annotated_image_url"] = f"/static/{annotated_rel.replace(os.sep, '/')}"
    analysis_result = analyzer.analyze_image(file_path, detection_info=detection_result)
    project_info = {"project_name": project_name, "location": location, "inspector": inspector}
    report = report_generator.generate(filename, detection_result, analysis_result, project_info)
    return {"success": True, "detection": detection_result, "analysis": analysis_result, "report": report}


@app.post("/api/analyze_batch")
async def analyze_batch(
    files: list[UploadFile] = File(...), conf: float = Form(0.25), iou: float = Form(0.45),
    project_name: str = Form("墙体裂缝检测项目"), location: str = Form("待填写"), inspector: str = Form("AI自动检测"),
    model_path: str = Form(""),
):
    if not files:
        raise HTTPException(status_code=400, detail="请上传至少一张图片")
    saved_paths = []
    for file in files:
        _check_file(file)
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            continue
        file_id = str(uuid.uuid4())[:8]
        filename = f"{file_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(contents)
        saved_paths.append(file_path)
    if not saved_paths:
        raise HTTPException(status_code=400, detail="没有有效的图片文件")
    det = detector
    if model_path and os.path.exists(model_path):
        from models.detector import CrackDetector as _CD
        from ultralytics import YOLO
        det = _CD.__new__(_CD)
        det.model = None
        det.model = YOLO(model_path)
    batch_result = det.detect_batch(saved_paths, conf_threshold=conf, iou_threshold=iou)
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    for r in batch_result.get("results", []):
        if r.get("annotated_image"):
            annotated_rel = os.path.relpath(r["annotated_image"], static_dir)
            r["annotated_image_url"] = f"/static/{annotated_rel.replace(os.sep, '/')}"
    best_image_path = saved_paths[0]
    analysis_result = analyzer.analyze_image(best_image_path, detection_info=batch_result)
    project_info = {"project_name": project_name, "location": location, "inspector": inspector}
    report = report_generator.generate_batch_report(batch_result, analysis_result, project_info)
    return {"success": True, "detection": batch_result, "analysis": analysis_result, "report": report}


@app.post("/api/analyze_video")
async def analyze_video(
    file: UploadFile = File(...), conf: float = Form(0.25), iou: float = Form(0.45),
    frame_interval: int = Form(30), project_name: str = Form("墙体裂缝检测项目"),
    location: str = Form("待填写"), inspector: str = Form("AI自动检测"),
    model_path: str = Form(""),
):
    _check_video_file(file)
    contents = await file.read()
    if len(contents) > MAX_VIDEO_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"视频文件大小超过限制({MAX_VIDEO_FILE_SIZE // 1024 // 1024}MB)")
    file_id = str(uuid.uuid4())[:8]
    filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(contents)
    det = detector
    if model_path and os.path.exists(model_path):
        from models.detector import CrackDetector as _CD
        from ultralytics import YOLO
        det = _CD.__new__(_CD)
        det.model = None
        det.model = YOLO(model_path)
    video_result = det.detect_video(file_path, conf_threshold=conf, iou_threshold=iou, frame_interval=frame_interval)
    if "error" in video_result:
        raise HTTPException(status_code=400, detail=video_result["error"])
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    for f in video_result.get("frames", []):
        if f.get("annotated_image"):
            annotated_rel = os.path.relpath(f["annotated_image"], static_dir)
            f["annotated_image_url"] = f"/static/{annotated_rel.replace(os.sep, '/')}"
    crack_frames = [f for f in video_result.get("frames", []) if f.get("total_count", 0) > 0]
    best_frame_path = None
    if crack_frames:
        best_frame = max(crack_frames, key=lambda x: x.get("total_count", 0))
        video_basename = os.path.splitext(os.path.basename(file_path))[0]
        best_frame_path = os.path.join(os.path.dirname(__file__), "static", "video_frames", video_basename, best_frame.get("source_file", ""))
    if best_frame_path and os.path.exists(best_frame_path):
        analysis_result = analyzer.analyze_image(best_frame_path, detection_info=video_result)
    else:
        analysis_result = analyzer.analyze_image(file_path, detection_info=video_result)
    project_info = {"project_name": project_name, "location": location, "inspector": inspector}
    report = report_generator.generate_video_report(video_result, analysis_result, project_info)
    return {"success": True, "detection": video_result, "analysis": analysis_result, "report": report}


@app.post("/api/export/{report_id}")
async def export_annotations(report_id: str, format: str = Form("all")):
    report_path = os.path.join(REPORT_DIR, f"report_{report_id}.json")
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="报告不存在")
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)
    export_results = report_generator.export_annotations(report, export_format=format)
    zip_path = os.path.join(EXPORT_DIR, f"export_{report_id}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        export_dir = export_results.get("export_dir", "")
        for root, dirs, files in os.walk(export_dir):
            for file in files:
                file_full_path = os.path.join(root, file)
                arcname = os.path.relpath(file_full_path, export_dir)
                zf.write(file_full_path, arcname)
        annotated_images = set()
        if report.get("report_type") == "batch":
            for item in report.get("per_image_details", []):
                ann = item.get("annotated_image", "")
                if ann and os.path.exists(ann):
                    annotated_images.add(ann)
        elif report.get("report_type") == "video":
            for item in report.get("frame_details", []):
                ann = item.get("annotated_image", "")
                if ann and os.path.exists(ann):
                    annotated_images.add(ann)
        for ann_path in annotated_images:
            if os.path.exists(ann_path):
                zf.write(ann_path, os.path.join("annotated_images", os.path.basename(ann_path)))
    return FileResponse(zip_path, media_type="application/zip", filename=f"裂缝检测标注导出_{report_id}.zip")


@app.post("/api/analyze_path")
async def analyze_by_path(
    image_path: str = Form(...), conf: float = Form(0.25), iou: float = Form(0.45),
    project_name: str = Form("墙体裂缝检测项目"), location: str = Form("待填写"), inspector: str = Form("AI自动检测"),
    model_path: str = Form(""),
):
    if not os.path.exists(image_path):
        raise HTTPException(status_code=400, detail=f"图片文件不存在: {image_path}")
    det = detector
    if model_path and os.path.exists(model_path):
        from models.detector import CrackDetector as _CD
        from ultralytics import YOLO
        det = _CD.__new__(_CD)
        det.model = None
        det.model = YOLO(model_path)
    detection_result = det.detect(image_path, conf_threshold=conf, iou_threshold=iou)
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    annotated_rel = os.path.relpath(detection_result["annotated_image"], static_dir)
    detection_result["annotated_image_url"] = f"/static/{annotated_rel.replace(os.sep, '/')}"
    analysis_result = analyzer.analyze_image(image_path, detection_info=detection_result)
    project_info = {"project_name": project_name, "location": location, "inspector": inspector}
    filename = os.path.basename(image_path)
    report = report_generator.generate(filename, detection_result, analysis_result, project_info)
    return {"success": True, "detection": detection_result, "analysis": analysis_result, "report": report}


@app.get("/api/reports")
async def list_reports():
    reports = []
    for f in os.listdir(REPORT_DIR):
        if f.endswith(".json"):
            with open(os.path.join(REPORT_DIR, f), "r", encoding="utf-8") as fp:
                report = json.load(fp)
                reports.append({
                    "report_id": report.get("report_id"),
                    "generated_at": report.get("generated_at"),
                    "severity": report.get("detection_summary", {}).get("severity") or report.get("batch_summary", {}).get("severity") or report.get("video_summary", {}).get("severity"),
                    "total_cracks": report.get("detection_summary", {}).get("total_cracks") or report.get("batch_summary", {}).get("total_cracks") or report.get("video_summary", {}).get("total_detections"),
                    "report_type": report.get("report_type", "single"),
                })
    return {"reports": sorted(reports, key=lambda x: x.get("generated_at", ""), reverse=True)}


@app.get("/api/report/{report_id}")
async def get_report(report_id: str):
    report_path = os.path.join(REPORT_DIR, f"report_{report_id}.json")
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="报告不存在")
    with open(report_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ==================== Dataset & Annotation APIs ====================

@app.get("/api/datasets")
async def list_datasets():
    return {"datasets": annotator.list_datasets()}


@app.post("/api/datasets")
async def create_dataset(name: str = Form(...), description: str = Form("")):
    meta = annotator.create_dataset(name, description)
    return {"success": True, "dataset": meta}


@app.post("/api/datasets/import")
async def import_dataset(name: str = Form(...), source_dir: str = Form(...), description: str = Form("")):
    """从本地文件夹导入数据集（支持 YOLO 格式 images+labels）"""
    if not source_dir or not os.path.exists(source_dir):
        raise HTTPException(status_code=400, detail="源文件夹不存在")
    if not os.path.isdir(source_dir):
        raise HTTPException(status_code=400, detail="源路径不是文件夹")

    result = annotator.import_dataset(name, source_dir, description)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/api/datasets/{dataset_id}")
async def get_dataset(dataset_id: str):
    meta = annotator.get_dataset(dataset_id)
    if not meta:
        raise HTTPException(status_code=404, detail="数据集不存在")
    return meta


@app.delete("/api/datasets/{dataset_id}")
async def delete_dataset(dataset_id: str):
    if annotator.delete_dataset(dataset_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="数据集不存在")


@app.get("/api/datasets/{dataset_id}/images")
async def list_dataset_images(dataset_id: str, annotated_only: bool = False, page: int = 1, page_size: int = 9999):
    result = annotator.get_images(dataset_id, annotated_only=annotated_only, page=page, page_size=page_size)
    return result


@app.post("/api/datasets/{dataset_id}/images")
async def add_dataset_images(dataset_id: str, files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="请上传至少一张图片")

    saved_files = []
    for file in files:
        _check_file(file)
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            continue
        file_id = str(uuid.uuid4())[:8]
        filename = f"{file_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(contents)
        saved_files.append({"filename": filename, "path": file_path})

    if not saved_files:
        raise HTTPException(status_code=400, detail="没有有效的图片文件")

    added = annotator.add_images(dataset_id, saved_files)
    return {"success": True, "added": added}


def _safe_filename(filename: str) -> str:
    """防止路径遍历攻击"""
    safe = os.path.normpath(filename).lstrip(os.sep).lstrip("/")
    if ".." in safe.split(os.sep):
        raise HTTPException(status_code=400, detail="非法的文件路径")
    return safe


@app.get("/api/datasets/{dataset_id}/images/{filename:path}/annotations")
async def get_image_annotations(dataset_id: str, filename: str, format: str = "yolo"):
    filename = _safe_filename(filename)
    # Check if requesting a polygon shapes sidecar file
    if filename.endswith("_shapes.json"):
        import json as _json
        shapes_path = os.path.join(DATASET_DIR, dataset_id, "labels", filename)
        if os.path.exists(shapes_path):
            with open(shapes_path, "r", encoding="utf-8") as f:
                return _json.load(f)
        return {}
    if format == "labelme":
        result = annotator.get_annotations_labelme(dataset_id, filename)
    else:
        result = annotator.get_image_annotations(dataset_id, filename)
    if result is None:
        raise HTTPException(status_code=404, detail="数据集或图片不存在")
    return result


@app.post("/api/datasets/{dataset_id}/images/{filename:path}/annotations")
async def save_image_annotations(dataset_id: str, filename: str, request: Request):
    filename = _safe_filename(filename)
    body = await request.json()
    format = body.get("format", "yolo")
    if format == "labelme":
        result = annotator.save_annotations(dataset_id, filename, body, format="labelme")
    elif body.get("_polygonOnly"):
        # Save polygon shape data as JSON sidecar (for preserving polygon vertices)
        import json as _json
        dataset_path = os.path.join(DATASET_DIR, dataset_id)
        shapes_path = os.path.join(dataset_path, "labels", filename)
        os.makedirs(os.path.dirname(shapes_path), exist_ok=True)
        with open(shapes_path, "w", encoding="utf-8") as f:
            _json.dump(body, f, ensure_ascii=False)
        result = {"success": True, "count": len(body.get("_shapes", []))}
    else:
        annotations = body.get("annotations", [])
        result = annotator.save_annotations(dataset_id, filename, annotations)
    return result


@app.post("/api/datasets/{dataset_id}/import_labelme")
async def import_labelme(dataset_id: str, files: list[UploadFile] = File(...)):
    """批量导入 LabelMe JSON 标注文件"""
    if not files:
        raise HTTPException(status_code=400, detail="请上传至少一个 LabelMe JSON 文件")

    import tempfile
    saved_files = []
    for file in files:
        if not file.filename.endswith(".json"):
            continue
        contents = await file.read()
        tmp_path = os.path.join(tempfile.gettempdir(), f"labelme_import_{uuid.uuid4().hex[:8]}.json")
        with open(tmp_path, "wb") as f:
            f.write(contents)
        saved_files.append({"path": tmp_path, "filename": file.filename})

    if not saved_files:
        raise HTTPException(status_code=400, detail="没有有效的 JSON 文件")

    result = annotator.import_labelme_dir(dataset_id, saved_files)

    # Clean up temp files
    for f in saved_files:
        try:
            os.remove(f["path"])
        except Exception:
            pass

    return {"success": True, **result}


@app.delete("/api/datasets/{dataset_id}/images/{filename:path}")
async def delete_dataset_image(dataset_id: str, filename: str):
    filename = _safe_filename(filename)
    if annotator.delete_image(dataset_id, filename):
        return {"success": True}
    raise HTTPException(status_code=404, detail="图片不存在")


@app.post("/api/datasets/{dataset_id}/auto_annotate")
async def auto_annotate_dataset(dataset_id: str, request: Request):
    body = {}
    try:
        raw = await request.body()
        if raw:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                body = json.loads(raw.decode("utf-8"))
            else:
                from urllib.parse import parse_qs
                parsed = parse_qs(raw.decode("utf-8"))
                body = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
    except Exception:
        pass
    conf = float(body.get("conf", 0.25))
    iou = float(body.get("iou", 0.45))
    result = annotator.auto_annotate(dataset_id, conf=conf, iou=iou)
    return {"success": True, **result}


@app.post("/api/datasets/{dataset_id}/split")
async def split_dataset(dataset_id: str, request: Request):
    body = {}
    try:
        raw = await request.body()
        if raw:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                body = json.loads(raw.decode("utf-8"))
            else:
                from urllib.parse import parse_qs
                parsed = parse_qs(raw.decode("utf-8"))
                body = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
    except Exception:
        pass
    train_ratio = float(body.get("train_ratio", 0.7))
    val_ratio = float(body.get("val_ratio", 0.2))
    test_ratio = float(body.get("test_ratio", 0.1))
    seed = int(body.get("seed", 42))
    result = annotator.split_dataset(dataset_id, train_ratio, val_ratio, test_ratio, seed)
    if result is None:
        raise HTTPException(status_code=400, detail="数据集分割失败，请检查数据集是否为空")
    return {"success": True, **result}


@app.post("/api/datasets/{dataset_id}/export")
async def export_dataset(dataset_id: str, request: Request):
    body = {}
    try:
        raw = await request.body()
        if raw:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                body = json.loads(raw.decode("utf-8"))
            else:
                from urllib.parse import parse_qs
                parsed = parse_qs(raw.decode("utf-8"))
                body = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
    except Exception:
        pass
    format = body.get("format", "yolo")
    result = annotator.export_dataset(dataset_id, format=format)
    if result is None:
        raise HTTPException(status_code=400, detail="导出失败")
    path = result.get("path")
    if path and os.path.exists(path):
        if os.path.isdir(path):
            zip_path = os.path.join(EXPORT_DIR, f"dataset_{dataset_id}_{format}.zip")
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_full_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_full_path, path)
                        zf.write(file_full_path, arcname)
            return FileResponse(zip_path, media_type="application/zip", filename=f"dataset_{dataset_id}_{format}.zip")
        return FileResponse(path, filename=os.path.basename(path))
    raise HTTPException(status_code=500, detail="导出文件生成失败")


@app.put("/api/datasets/{dataset_id}/classes")
async def update_dataset_classes(dataset_id: str, request: Request):
    body = await request.json()
    classes = body.get("classes", {})
    meta = annotator.update_classes(dataset_id, classes)
    if not meta:
        raise HTTPException(status_code=404, detail="数据集不存在")
    return {"success": True, "dataset": meta}


# ==================== Training APIs ====================

@app.post("/api/train/start")
async def start_training(request: Request):
    body = {}
    try:
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            body = await request.json()
        elif "multipart/form-data" in content_type or "application/x-www-form-urlencoded" in content_type:
            form = await request.form()
            body = {k: v for k, v in form.items()}
        else:
            raw = await request.body()
            if raw:
                from urllib.parse import parse_qs
                parsed = parse_qs(raw.decode("utf-8"))
                body = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"请求解析失败: {str(e)}")

    dataset_id = body.get("dataset_id", "")
    if not dataset_id:
        raise HTTPException(status_code=400, detail="请选择数据集")

    from config import TRAINING_DEFAULTS
    config = dict(TRAINING_DEFAULTS)

    param_map = {
        "model": str, "epochs": int, "batch_size": int, "imgsz": int,
        "patience": int, "lr0": float, "lrf": float, "momentum": float,
        "weight_decay": float, "warmup_epochs": int, "box": float,
        "cls": float, "dfl": float, "hsv_h": float, "hsv_s": float,
        "hsv_v": float, "degrees": float, "translate": float, "scale": float,
        "shear": float, "fliplr": float, "mosaic": float, "mixup": float,
    }

    for key, type_fn in param_map.items():
        val = body.get(key)
        if val is not None:
            try:
                config[key] = type_fn(val)
            except (ValueError, TypeError):
                pass

    try:
        result = trainer.start_training(dataset_id, config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"训练启动失败: {str(e)}")
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return {"success": True, "training": result}


@app.get("/api/train/status/{training_id}")
async def get_training_status(training_id: str):
    result = trainer.get_training_status(training_id)
    if not result:
        raise HTTPException(status_code=404, detail="训练任务不存在")
    return result


@app.get("/api/train/progress/{training_id}")
async def get_training_progress(training_id: str):
    result = trainer.get_training_progress(training_id)
    return result


@app.get("/api/train/curves/{training_id}")
async def get_training_curves(training_id: str):
    result = evaluator.get_training_curves(training_id)
    if result is None:
        return {"curves": None}
    return {"curves": result}


@app.post("/api/train/stop/{training_id}")
async def stop_training(training_id: str):
    return trainer.stop_training(training_id)


@app.post("/api/train/resume/{training_id}")
async def resume_training(training_id: str):
    result = trainer.resume_training(training_id)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return {"success": True, "training": result}


@app.get("/api/train/list")
async def list_trainings():
    return {"trainings": trainer.list_trainings()}


@app.delete("/api/train/{training_id}")
async def delete_training(training_id: str):
    return trainer.delete_training(training_id)


@app.get("/api/train/models")
async def list_available_models():
    return {"models": trainer.get_available_models()}


# ==================== Evaluation APIs ====================

@app.post("/api/eval/start")
async def start_evaluation(
    model_path: str = Form(...),
    dataset_id: str = Form(""),
    conf: float = Form(0.25),
    iou: float = Form(0.45),
    imgsz: int = Form(640),
    batch_size: int = Form(16),
    split: str = Form("val"),
):
    if not model_path:
        raise HTTPException(status_code=400, detail="请选择模型")

    result = evaluator.evaluate_model(
        model_path=model_path, dataset_id=dataset_id,
        conf=conf, iou=iou, imgsz=imgsz, batch_size=batch_size, split=split,
    )

    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return {"success": True, "evaluation": result}


@app.get("/api/eval/list")
async def list_evaluations():
    return {"evaluations": evaluator.list_evaluations()}


@app.get("/api/eval/{eval_id}")
async def get_evaluation(eval_id: str):
    result = evaluator.get_evaluation(eval_id)
    if not result:
        raise HTTPException(status_code=404, detail="评估记录不存在")
    return result


@app.delete("/api/eval/{eval_id}")
async def delete_evaluation(eval_id: str):
    if evaluator.delete_evaluation(eval_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="评估记录不存在")


@app.post("/api/eval/compare")
async def compare_models(request: Request):
    body = await request.json()
    eval_ids = body.get("eval_ids", [])
    if len(eval_ids) < 2:
        raise HTTPException(status_code=400, detail="请至少选择2个评估结果进行对比")
    result = evaluator.compare_models(eval_ids)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
