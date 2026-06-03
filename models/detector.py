import os
import cv2
import numpy as np
from ultralytics import YOLO
from config import (
    YOLO_MODEL_PATH, YOLO_MODEL_DEFAULT, YOLO_CONF_THRESHOLD, YOLO_IOU_THRESHOLD,
    CRACK_CLASSES, RESULT_DIR, VIDEO_FRAMES_DIR, VIDEO_FRAME_INTERVAL, VIDEO_MAX_FRAMES,
    PIXELS_PER_MM, CRACK_WIDTH_MIN_MM, SEVERITY_LEVELS,
)


class CrackDetector:
    def __init__(self, model_path=None):
        self.model = None
        self._load_model(model_path)

    def _load_model(self, model_path=None):
        if model_path and os.path.exists(model_path):
            self.model = YOLO(model_path)
        elif os.path.exists(YOLO_MODEL_PATH):
            self.model = YOLO(YOLO_MODEL_PATH)
        else:
            self.model = YOLO(YOLO_MODEL_DEFAULT)

    def detect(self, image_path, conf_threshold=None, iou_threshold=None, pixels_per_mm=None):
        conf = conf_threshold or YOLO_CONF_THRESHOLD
        iou = iou_threshold or YOLO_IOU_THRESHOLD
        ppm = pixels_per_mm or PIXELS_PER_MM

        results = self.model(
            image_path,
            conf=conf,
            iou=iou,
            verbose=False,
        )

        result = results[0]

        detections = []
        if result.boxes is not None and len(result.boxes) > 0:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])
                xyxy = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = map(float, xyxy)

                cls_name = CRACK_CLASSES.get(cls_id, result.names.get(cls_id, f"class_{cls_id}"))
                pw = x2 - x1  # pixel width
                ph = y2 - y1  # pixel height

                # Crack dimension estimation: width = shorter side, length = longer side
                # For horizontal cracks: height=width, width=length; for vertical: width=width, height=length
                if cls_id == 0:  # 横向裂缝: 宽度方向 = 垂直，长度方向 = 水平
                    crack_width_px, crack_length_px = ph, pw
                elif cls_id == 1:  # 纵向裂缝: 宽度方向 = 水平，长度方向 = 垂直
                    crack_width_px, crack_length_px = pw, ph
                else:  # 斜向/网状/未分类: 短边=宽度，长边=长度
                    crack_width_px = min(pw, ph)
                    crack_length_px = max(pw, ph)

                crack_width_mm = round(crack_width_px / ppm, 3)
                crack_length_mm = round(crack_length_px / ppm, 1)

                # Severity based on measured width
                if crack_width_mm < 0.2:
                    severity = "轻微"
                elif crack_width_mm < 0.5:
                    severity = "一般"
                elif crack_width_mm < 2.0:
                    severity = "严重"
                else:
                    severity = "危险"

                detections.append({
                    "class_id": cls_id,
                    "class_name": cls_name,
                    "confidence": round(confidence, 4),
                    "bbox": {"x1": round(x1, 2), "y1": round(y1, 2), "x2": round(x2, 2), "y2": round(y2, 2)},
                    "width_px": round(pw, 2), "height_px": round(ph, 2),
                    "area_px": round(pw * ph, 2),
                    "crack_width_mm": crack_width_mm,
                    "crack_length_mm": crack_length_mm,
                    "severity": severity,
                    "pixels_per_mm": ppm,
                })

        annotated_image_path = self._save_annotated_image(image_path, result, detections, ppm)

        img = cv2.imread(image_path)
        img_h, img_w = img.shape[:2] if img is not None else (0, 0)

        return {
            "detections": detections,
            "total_count": len(detections),
            "annotated_image": annotated_image_path,
            "image_size": {"width": img_w, "height": img_h},
            "summary": self._generate_summary(detections),
        }

    def detect_batch(self, image_paths, conf_threshold=None, iou_threshold=None):
        results_list = []
        for path in image_paths:
            try:
                result = self.detect(path, conf_threshold, iou_threshold)
                result["source_file"] = os.path.basename(path)
                results_list.append(result)
            except Exception as e:
                results_list.append({
                    "source_file": os.path.basename(path),
                    "error": str(e),
                    "detections": [],
                    "total_count": 0,
                    "summary": {"has_crack": False, "severity": "无", "class_distribution": {}, "max_confidence": 0},
                })

        total_cracks = sum(r.get("total_count", 0) for r in results_list)
        all_severities = [r.get("summary", {}).get("severity", "无") for r in results_list]
        severity_rank = {"危险": 4, "严重": 3, "一般": 2, "轻微": 1, "无": 0}
        worst_severity = max(all_severities, key=lambda s: severity_rank.get(s, 0)) if all_severities else "无"

        combined_class_dist = {}
        for r in results_list:
            for cls, cnt in r.get("summary", {}).get("class_distribution", {}).items():
                combined_class_dist[cls] = combined_class_dist.get(cls, 0) + cnt

        max_conf = max(
            (r.get("summary", {}).get("max_confidence", 0) for r in results_list),
            default=0,
        )

        return {
            "results": results_list,
            "total_images": len(image_paths),
            "total_cracks": total_cracks,
            "worst_severity": worst_severity,
            "combined_class_distribution": combined_class_dist,
            "max_confidence": max_conf,
            "summary": {
                "has_crack": total_cracks > 0,
                "severity": worst_severity,
                "class_distribution": combined_class_dist,
                "max_confidence": max_conf,
            },
        }

    def detect_video(self, video_path, conf_threshold=None, iou_threshold=None, frame_interval=None, max_frames=None):
        conf = conf_threshold or YOLO_CONF_THRESHOLD
        iou = iou_threshold or YOLO_IOU_THRESHOLD
        interval = frame_interval or VIDEO_FRAME_INTERVAL
        max_f = max_frames or VIDEO_MAX_FRAMES

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {"error": "无法打开视频文件", "frames": [], "total_frames": 0}

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_video_frames / fps if fps > 0 else 0

        video_basename = os.path.splitext(os.path.basename(video_path))[0]
        frame_output_dir = os.path.join(VIDEO_FRAMES_DIR, video_basename)
        os.makedirs(frame_output_dir, exist_ok=True)

        frame_results = []
        frame_idx = 0
        saved_idx = 0

        while cap.isOpened() and saved_idx < max_f:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % interval == 0:
                frame_filename = f"frame_{frame_idx:06d}.jpg"
                frame_path = os.path.join(frame_output_dir, frame_filename)
                cv2.imwrite(frame_path, frame)

                try:
                    det_result = self.detect(frame_path, conf_threshold=conf, iou_threshold=iou)
                    det_result["frame_index"] = frame_idx
                    det_result["frame_time"] = round(frame_idx / fps, 2) if fps > 0 else 0
                    det_result["source_file"] = frame_filename
                    frame_results.append(det_result)
                except Exception as e:
                    frame_results.append({
                        "frame_index": frame_idx,
                        "frame_time": round(frame_idx / fps, 2) if fps > 0 else 0,
                        "source_file": frame_filename,
                        "error": str(e),
                        "detections": [],
                        "total_count": 0,
                        "summary": {"has_crack": False, "severity": "无"},
                    })

                saved_idx += 1

            frame_idx += 1

        cap.release()

        frames_with_cracks = sum(1 for r in frame_results if r.get("total_count", 0) > 0)
        total_detections = sum(r.get("total_count", 0) for r in frame_results)
        all_severities = [r.get("summary", {}).get("severity", "无") for r in frame_results]
        severity_rank = {"危险": 4, "严重": 3, "一般": 2, "轻微": 1, "无": 0}
        worst_severity = max(all_severities, key=lambda s: severity_rank.get(s, 0)) if all_severities else "无"

        combined_class_dist = {}
        for r in frame_results:
            for cls, cnt in r.get("summary", {}).get("class_distribution", {}).items():
                combined_class_dist[cls] = combined_class_dist.get(cls, 0) + cnt

        max_conf = max(
            (r.get("summary", {}).get("max_confidence", 0) for r in frame_results),
            default=0,
        )

        return {
            "video_info": {
                "filename": os.path.basename(video_path),
                "fps": round(fps, 2),
                "total_frames": total_video_frames,
                "width": video_w,
                "height": video_h,
                "duration": round(duration, 2),
                "frame_interval": interval,
                "frames_analyzed": len(frame_results),
            },
            "frames": frame_results,
            "frames_with_cracks": frames_with_cracks,
            "total_detections": total_detections,
            "worst_severity": worst_severity,
            "combined_class_distribution": combined_class_dist,
            "max_confidence": max_conf,
            "summary": {
                "has_crack": total_detections > 0,
                "severity": worst_severity,
                "class_distribution": combined_class_dist,
                "max_confidence": max_conf,
            },
        }

    def _save_annotated_image(self, image_path, result, detections=None, ppm=None):
        annotated = result.plot()

        # Draw dimension labels on the image
        if detections and ppm:
            ppm = ppm or PIXELS_PER_MM
            for i, det in enumerate(detections):
                bbox = det["bbox"]
                x1, y1 = int(bbox["x1"]), int(bbox["y1"])
                x2, y2 = int(bbox["x2"]), int(bbox["y2"])
                w_mm = det.get("crack_width_mm", 0)
                l_mm = det.get("crack_length_mm", 0)
                cls_name = det.get("class_name", "")

                # Dimension label text
                dim_text = f"W:{w_mm:.2f}mm L:{l_mm:.1f}mm"
                if w_mm > 0:
                    sev = det.get("severity", "")
                    dim_text += f" [{sev}]"

                # Position: below the box
                txt_y = min(y2 + 18, annotated.shape[0] - 5)
                txt_x = x1

                # Draw background
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.45
                thickness = 1
                (tw, th), _ = cv2.getTextSize(dim_text, font, font_scale, thickness)
                cv2.rectangle(annotated, (txt_x, txt_y - th - 4), (txt_x + tw + 6, txt_y + 2), (0, 0, 0), -1)
                cv2.putText(annotated, dim_text, (txt_x + 3, txt_y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

        basename = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(RESULT_DIR, f"{basename}_detected.jpg")
        cv2.imwrite(output_path, annotated)
        return output_path

    def _generate_summary(self, detections):
        if not detections:
            return {"has_crack": False, "severity": "无", "class_distribution": {}, "max_confidence": 0, "max_width_mm": 0, "max_length_mm": 0}

        class_dist = {}
        for det in detections:
            cls = det["class_name"]
            class_dist[cls] = class_dist.get(cls, 0) + 1

        max_conf = max(d["confidence"] for d in detections)
        max_area = max(d.get("area_px", 0) for d in detections)
        max_width = max(d.get("crack_width_mm", 0) for d in detections)
        max_length = max(d.get("crack_length_mm", 0) for d in detections)

        # Use measured severity from detections
        sevs = [d.get("severity", "轻微") for d in detections]
        severity_rank = {"危险": 4, "严重": 3, "一般": 2, "轻微": 1, "无": 0}
        severity = max(sevs, key=lambda s: severity_rank.get(s, 0)) if sevs else "轻微"

        return {
            "has_crack": True,
            "severity": severity,
            "class_distribution": class_dist,
            "max_confidence": round(max_conf, 4),
            "max_area": max_area,
            "max_width_mm": max_width,
            "max_length_mm": max_length,
        }
