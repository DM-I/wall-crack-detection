import os
import json
import csv
import uuid
import shutil
from datetime import datetime
from config import REPORT_DIR, EXPORT_DIR, SEVERITY_LEVELS


class ReportGenerator:
    def generate(self, image_name, detection_result, analysis_result, project_info=None):
        report_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now()

        analysis = analysis_result.get("analysis", {})
        summary = detection_result.get("summary", {})
        detections = detection_result.get("detections", [])

        severity = analysis.get("severity", summary.get("severity", "未知"))
        severity_info = SEVERITY_LEVELS.get(severity, SEVERITY_LEVELS.get("一般", {}))

        report = {
            "report_id": report_id,
            "report_title": "墙体裂缝检测审核报告",
            "generated_at": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "project_info": project_info or {
                "project_name": "墙体裂缝检测项目",
                "location": "待填写",
                "inspector": "AI自动检测",
            },
            "image_info": {
                "filename": image_name,
                "image_size": detection_result.get("image_size", {}),
            },
            "detection_summary": {
                "total_cracks": detection_result.get("total_count", 0),
                "has_crack": summary.get("has_crack", False),
                "severity": severity,
                "severity_color": severity_info.get("color", "#999"),
                "severity_description": severity_info.get("description", ""),
                "class_distribution": summary.get("class_distribution", {}),
                "max_confidence": summary.get("max_confidence", 0),
            },
            "detection_details": detections,
            "ai_analysis": {
                "crack_found": analysis.get("crack_found", False),
                "crack_description": analysis.get("crack_description", ""),
                "crack_types": analysis.get("crack_types", []),
                "estimated_width": analysis.get("estimated_width", "未知"),
                "possible_causes": analysis.get("possible_causes", []),
                "risk_assessment": analysis.get("risk_assessment", ""),
                "risk_level": analysis.get("risk_level", "未知"),
                "repair_suggestions": analysis.get("repair_suggestions", []),
                "urgency": analysis.get("urgency", "待评估"),
                "professional_opinion": analysis.get("professional_opinion", ""),
            },
            "conclusion": self._generate_conclusion(severity, analysis, detections),
            "recommendations": self._generate_recommendations(severity, analysis),
        }

        report_path = os.path.join(REPORT_DIR, f"report_{report_id}.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        report["report_path"] = report_path
        return report

    def generate_batch_report(self, batch_result, analysis_result, project_info=None):
        report_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now()

        analysis = analysis_result.get("analysis", {})
        summary = batch_result.get("summary", {})

        severity = analysis.get("severity", summary.get("severity", "未知"))
        severity_info = SEVERITY_LEVELS.get(severity, SEVERITY_LEVELS.get("一般", {}))

        per_image_details = []
        for r in batch_result.get("results", []):
            per_image_details.append({
                "source_file": r.get("source_file", ""),
                "total_count": r.get("total_count", 0),
                "severity": r.get("summary", {}).get("severity", "无"),
                "detections": r.get("detections", []),
                "annotated_image": r.get("annotated_image", ""),
                "image_size": r.get("image_size", {}),
            })

        report = {
            "report_id": report_id,
            "report_title": "墙体裂缝批量检测审核报告",
            "report_type": "batch",
            "generated_at": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "project_info": project_info or {},
            "batch_summary": {
                "total_images": batch_result.get("total_images", 0),
                "total_cracks": batch_result.get("total_cracks", 0),
                "worst_severity": batch_result.get("worst_severity", "无"),
                "severity": severity,
                "severity_color": severity_info.get("color", "#999"),
                "class_distribution": batch_result.get("combined_class_distribution", {}),
                "max_confidence": batch_result.get("max_confidence", 0),
            },
            "per_image_details": per_image_details,
            "ai_analysis": {
                "crack_found": analysis.get("crack_found", False),
                "crack_description": analysis.get("crack_description", ""),
                "crack_types": analysis.get("crack_types", []),
                "severity": analysis.get("severity", "未知"),
                "risk_level": analysis.get("risk_level", "未知"),
                "urgency": analysis.get("urgency", "待评估"),
                "professional_opinion": analysis.get("professional_opinion", ""),
            },
            "conclusion": self._generate_batch_conclusion(batch_result, analysis),
            "recommendations": self._generate_recommendations(severity, analysis),
        }

        report_path = os.path.join(REPORT_DIR, f"report_{report_id}.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        report["report_path"] = report_path
        return report

    def generate_video_report(self, video_result, analysis_result, project_info=None):
        report_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now()

        analysis = analysis_result.get("analysis", {})
        summary = video_result.get("summary", {})

        severity = analysis.get("severity", summary.get("severity", "未知"))
        severity_info = SEVERITY_LEVELS.get(severity, SEVERITY_LEVELS.get("一般", {}))

        frame_details = []
        for f in video_result.get("frames", []):
            if f.get("total_count", 0) > 0:
                frame_details.append({
                    "frame_index": f.get("frame_index", 0),
                    "frame_time": f.get("frame_time", 0),
                    "source_file": f.get("source_file", ""),
                    "total_count": f.get("total_count", 0),
                    "severity": f.get("summary", {}).get("severity", "无"),
                    "detections": f.get("detections", []),
                    "annotated_image": f.get("annotated_image", ""),
                })

        report = {
            "report_id": report_id,
            "report_title": "墙体裂缝视频检测审核报告",
            "report_type": "video",
            "generated_at": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "project_info": project_info or {},
            "video_info": video_result.get("video_info", {}),
            "video_summary": {
                "frames_analyzed": video_result.get("video_info", {}).get("frames_analyzed", 0),
                "frames_with_cracks": video_result.get("frames_with_cracks", 0),
                "total_detections": video_result.get("total_detections", 0),
                "worst_severity": video_result.get("worst_severity", "无"),
                "severity": severity,
                "severity_color": severity_info.get("color", "#999"),
                "class_distribution": video_result.get("combined_class_distribution", {}),
                "max_confidence": video_result.get("max_confidence", 0),
            },
            "frame_details": frame_details,
            "ai_analysis": {
                "crack_found": analysis.get("crack_found", False),
                "crack_description": analysis.get("crack_description", ""),
                "crack_types": analysis.get("crack_types", []),
                "severity": analysis.get("severity", "未知"),
                "risk_level": analysis.get("risk_level", "未知"),
                "urgency": analysis.get("urgency", "待评估"),
                "professional_opinion": analysis.get("professional_opinion", ""),
            },
            "conclusion": self._generate_video_conclusion(video_result, analysis),
            "recommendations": self._generate_recommendations(severity, analysis),
        }

        report_path = os.path.join(REPORT_DIR, f"report_{report_id}.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        report["report_path"] = report_path
        return report

    def export_annotations(self, report, export_format="all"):
        report_id = report.get("report_id", str(uuid.uuid4())[:8])
        export_dir = os.path.join(EXPORT_DIR, f"export_{report_id}")
        os.makedirs(export_dir, exist_ok=True)

        results = {}

        if export_format in ("json", "all"):
            json_path = os.path.join(export_dir, "annotations.json")
            annotations = self._build_annotations_json(report)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(annotations, f, ensure_ascii=False, indent=2)
            results["json_path"] = json_path

        if export_format in ("csv", "all"):
            csv_path = os.path.join(export_dir, "annotations.csv")
            self._write_annotations_csv(report, csv_path)
            results["csv_path"] = csv_path

        if export_format in ("yolo", "all"):
            yolo_dir = os.path.join(export_dir, "labels")
            os.makedirs(yolo_dir, exist_ok=True)
            self._write_yolo_labels(report, yolo_dir)
            results["yolo_dir"] = yolo_dir

        report_copy = dict(report)
        if report.get("detection_details"):
            det = report.get("detection_details")
            if isinstance(det, list) and len(det) > 0 and isinstance(det[0], dict):
                first_det = det[0]
                if "bbox" in first_det:
                    img_size = report.get("image_info", {}).get("image_size", {})
                    img_w = img_size.get("width", 1)
                    img_h = img_size.get("height", 1)
                    det_copy = []
                    for d in det:
                        dc = dict(d)
                        if "bbox" in dc:
                            dc["bbox_normalized"] = {
                                "x1": round(dc["bbox"]["x1"] / img_w, 6) if img_w else 0,
                                "y1": round(dc["bbox"]["y1"] / img_h, 6) if img_h else 0,
                                "x2": round(dc["bbox"]["x2"] / img_w, 6) if img_w else 0,
                                "y2": round(dc["bbox"]["y2"] / img_h, 6) if img_h else 0,
                            }
                        det_copy.append(dc)
                    report_copy["detection_details"] = det_copy

        report_path = os.path.join(export_dir, "report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_copy, f, ensure_ascii=False, indent=2)
        results["report_path"] = report_path

        results["export_dir"] = export_dir
        return results

    def _build_annotations_json(self, report):
        report_type = report.get("report_type", "single")

        if report_type == "batch":
            annotations = {
                "report_id": report.get("report_id"),
                "type": "batch",
                "images": [],
            }
            for item in report.get("per_image_details", []):
                img_ann = {
                    "filename": item.get("source_file", ""),
                    "detections": item.get("detections", []),
                }
                annotations["images"].append(img_ann)
        elif report_type == "video":
            annotations = {
                "report_id": report.get("report_id"),
                "type": "video",
                "video_info": report.get("video_info", {}),
                "frames": [],
            }
            for item in report.get("frame_details", []):
                frame_ann = {
                    "frame_index": item.get("frame_index", 0),
                    "frame_time": item.get("frame_time", 0),
                    "filename": item.get("source_file", ""),
                    "detections": item.get("detections", []),
                }
                annotations["frames"].append(frame_ann)
        else:
            annotations = {
                "report_id": report.get("report_id"),
                "type": "single",
                "filename": report.get("image_info", {}).get("filename", ""),
                "image_size": report.get("image_info", {}).get("image_size", {}),
                "detections": report.get("detection_details", []),
            }

        return annotations

    def _write_annotations_csv(self, report, csv_path):
        report_type = report.get("report_type", "single")

        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([
                "来源文件", "帧索引", "帧时间(秒)", "序号",
                "裂缝类型", "置信度", "x1", "y1", "x2", "y2", "宽度", "高度", "面积",
            ])

            if report_type == "batch":
                for item in report.get("per_image_details", []):
                    source = item.get("source_file", "")
                    for i, d in enumerate(item.get("detections", []), 1):
                        writer.writerow([
                            source, "", "", i,
                            d.get("class_name", ""),
                            d.get("confidence", 0),
                            d.get("bbox", {}).get("x1", ""),
                            d.get("bbox", {}).get("y1", ""),
                            d.get("bbox", {}).get("x2", ""),
                            d.get("bbox", {}).get("y2", ""),
                            d.get("width_px", d.get("width", "")),
                            d.get("height_px", d.get("height", "")),
                            d.get("area_px", d.get("area", "")),
                        ])
            elif report_type == "video":
                for item in report.get("frame_details", []):
                    source = item.get("source_file", "")
                    frame_idx = item.get("frame_index", "")
                    frame_time = item.get("frame_time", "")
                    for i, d in enumerate(item.get("detections", []), 1):
                        writer.writerow([
                            source, frame_idx, frame_time, i,
                            d.get("class_name", ""),
                            d.get("confidence", 0),
                            d.get("bbox", {}).get("x1", ""),
                            d.get("bbox", {}).get("y1", ""),
                            d.get("bbox", {}).get("x2", ""),
                            d.get("bbox", {}).get("y2", ""),
                            d.get("width_px", d.get("width", "")),
                            d.get("height_px", d.get("height", "")),
                            d.get("area_px", d.get("area", "")),
                        ])
            else:
                source = report.get("image_info", {}).get("filename", "")
                for i, d in enumerate(report.get("detection_details", []), 1):
                    writer.writerow([
                        source, "", "", i,
                        d.get("class_name", ""),
                        d.get("confidence", 0),
                        d.get("bbox", {}).get("x1", ""),
                        d.get("bbox", {}).get("y1", ""),
                        d.get("bbox", {}).get("x2", ""),
                        d.get("bbox", {}).get("y2", ""),
                        d.get("width_px", d.get("width", "")),
                        d.get("height_px", d.get("height", "")),
                        d.get("area_px", d.get("area", "")),
                    ])

    def _write_yolo_labels(self, report, yolo_dir):
        report_type = report.get("report_type", "single")

        if report_type == "batch":
            for item in report.get("per_image_details", []):
                source = item.get("source_file", "")
                if not source:
                    continue
                label_name = os.path.splitext(source)[0] + ".txt"
                label_path = os.path.join(yolo_dir, label_name)
                img_size = item.get("image_size", {})
                self._write_single_yolo_label(item.get("detections", []), label_path, img_size)
        elif report_type == "video":
            video_info = report.get("video_info", {})
            vw = video_info.get("width", 0)
            vh = video_info.get("height", 0)
            for item in report.get("frame_details", []):
                source = item.get("source_file", "")
                if not source:
                    continue
                label_name = os.path.splitext(source)[0] + ".txt"
                label_path = os.path.join(yolo_dir, label_name)
                img_size = {"width": vw, "height": vh}
                self._write_single_yolo_label(item.get("detections", []), label_path, img_size)
        else:
            source = report.get("image_info", {}).get("filename", "")
            if source:
                label_name = os.path.splitext(source)[0] + ".txt"
                label_path = os.path.join(yolo_dir, label_name)
                img_size = report.get("image_info", {}).get("image_size", {})
                self._write_single_yolo_label(report.get("detection_details", []), label_path, img_size)

    def _write_single_yolo_label(self, detections, label_path, img_size=None):
        img_w = (img_size or {}).get("width", 0)
        img_h = (img_size or {}).get("height", 0)
        with open(label_path, "w", encoding="utf-8") as f:
            for d in detections:
                cls_id = d.get("class_id", 0)
                bbox = d.get("bbox", {})
                x1, y1, x2, y2 = bbox.get("x1", 0), bbox.get("y1", 0), bbox.get("x2", 0), bbox.get("y2", 0)
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                w = x2 - x1
                h = y2 - y1
                if img_w > 0 and img_h > 0:
                    cx = cx / img_w
                    cy = cy / img_h
                    w = w / img_w
                    h = h / img_h
                f.write(f"{cls_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")

    def _generate_conclusion(self, severity, analysis, detections):
        if not analysis.get("crack_found", False):
            return (
                "经AI视觉检测系统分析，该墙体表面未发现明显裂缝，"
                "墙体状况良好。建议保持定期巡检，持续监测墙体状态变化。"
            )

        count = len(detections)
        crack_types = "、".join(analysis.get("crack_types", ["未知类型"]))
        risk_level = analysis.get("risk_level", "未知")

        return (
            f"经YOLO11目标检测与QWEN-VL视觉语言模型联合分析，"
            f"该墙体共检测到{count}处裂缝，裂缝类型包括{crack_types}，"
            f"严重程度评估为「{severity}」，风险等级为「{risk_level}」。"
            f"{analysis.get('professional_opinion', '')}"
        )

    def _generate_batch_conclusion(self, batch_result, analysis):
        total_images = batch_result.get("total_images", 0)
        total_cracks = batch_result.get("total_cracks", 0)
        worst = batch_result.get("worst_severity", "无")

        return (
            f"本次批量检测共处理{total_images}张图片，"
            f"累计检测到{total_cracks}处裂缝，"
            f"最严重程度为「{worst}」。"
            f"{analysis.get('professional_opinion', '')}"
        )

    def _generate_video_conclusion(self, video_result, analysis):
        info = video_result.get("video_info", {})
        frames_analyzed = info.get("frames_analyzed", 0)
        frames_with_cracks = video_result.get("frames_with_cracks", 0)
        total_det = video_result.get("total_detections", 0)
        worst = video_result.get("worst_severity", "无")

        return (
            f"本次视频检测共分析{frames_analyzed}帧，"
            f"其中{frames_with_cracks}帧检测到裂缝，"
            f"累计{total_det}处检测，最严重程度为「{worst}」。"
            f"{analysis.get('professional_opinion', '')}"
        )

    def _generate_recommendations(self, severity, analysis):
        base_recs = [
            "对检测区域进行标记，建立裂缝档案",
            "使用专业裂缝测宽仪进行精确测量",
            "记录裂缝位置、走向、宽度等参数",
        ]

        severity_recs = {
            "轻微": [
                "继续观察，建议每3个月巡检一次",
                "记录裂缝当前状态作为基线数据",
                "关注环境温湿度变化对裂缝的影响",
            ],
            "一般": [
                "建议1个月内安排专业人员现场复核",
                "对裂缝进行表面封闭处理",
                "增加巡检频率至每月一次",
            ],
            "严重": [
                "建议1周内安排专业结构工程师评估",
                "对裂缝进行注浆加固处理",
                "安装裂缝监测设备持续监测",
                "评估是否影响结构承载能力",
            ],
            "危险": [
                "立即安排结构安全评估",
                "对危险区域设置安全警示和隔离",
                "制定紧急修复方案并尽快实施",
                "考虑临时支撑等应急措施",
                "修复后进行持续监测不少于6个月",
            ],
        }

        recs = base_recs + severity_recs.get(severity, severity_recs["一般"])
        repair = analysis.get("repair_suggestions", [])
        if repair:
            recs.extend(repair)

        return recs
