import os
import json
import uuid
from datetime import datetime
from config import EVALUATION_DIR, DATASET_DIR, WEIGHTS_DIR, TRAINING_DIR


class Evaluator:
    def __init__(self):
        self._cleanup_stale_statuses()

    def _cleanup_stale_statuses(self):
        """服务重启时，将残留的 running/pending 状态标记为 interrupted"""
        if not os.path.exists(EVALUATION_DIR):
            return
        stale_statuses = {"running", "pending"}
        for d in os.listdir(EVALUATION_DIR):
            info_path = os.path.join(EVALUATION_DIR, d, "eval_info.json")
            if not os.path.exists(info_path):
                continue
            try:
                with open(info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
                if info.get("status") in stale_statuses:
                    info["status"] = "interrupted"
                    info["error"] = info.get("error") or "服务重启导致评估中断"
                    info["completed_at"] = info.get("completed_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with open(info_path, "w", encoding="utf-8") as f:
                        json.dump(info, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
    def evaluate_model(self, model_path, dataset_id=None, yaml_path=None, conf=0.25, iou=0.45, imgsz=640, batch_size=16, split="val"):
        if dataset_id and not yaml_path:
            yaml_path = os.path.join(DATASET_DIR, dataset_id, "data.yaml")

        if not yaml_path or not os.path.exists(yaml_path):
            return {"error": "数据集配置文件不存在，请先分割数据集"}

        if not os.path.exists(model_path) and not self._is_pretrained(model_path):
            return {"error": f"模型文件不存在: {model_path}"}

        eval_id = str(uuid.uuid4())[:8]
        eval_dir = os.path.join(EVALUATION_DIR, f"eval_{eval_id}")
        os.makedirs(eval_dir, exist_ok=True)

        eval_info = {
            "eval_id": eval_id,
            "model_path": model_path,
            "dataset_id": dataset_id,
            "yaml_path": yaml_path,
            "conf": conf,
            "iou": iou,
            "imgsz": imgsz,
            "batch_size": batch_size,
            "split": split,
            "status": "pending",
            "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "completed_at": None,
            "results": None,
            "error": None,
        }

        info_path = os.path.join(eval_dir, "eval_info.json")
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump(eval_info, f, ensure_ascii=False, indent=2)

        try:
            eval_info["status"] = "running"
            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(eval_info, f, ensure_ascii=False, indent=2)

            from ultralytics import YOLO
            model = YOLO(model_path)

            val_kwargs = {
                "data": yaml_path,
                "conf": conf,
                "iou": iou,
                "imgsz": imgsz,
                "batch": batch_size,
                "split": split,
                "project": eval_dir,
                "name": "results",
                "exist_ok": True,
                "plots": True,
                "save_json": True,
                "save_hybrid": False,
                "verbose": True,
            }

            results = model.val(**val_kwargs)

            metrics = self._extract_val_metrics(results)
            confusion_matrix = self._extract_confusion_matrix(results)

            eval_results = {
                "metrics": metrics,
                "confusion_matrix": confusion_matrix,
                "per_class_metrics": self._extract_per_class_metrics(results),
            }

            eval_info["status"] = "completed"
            eval_info["results"] = eval_results
            eval_info["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(eval_info, f, ensure_ascii=False, indent=2)

            return eval_info

        except Exception as e:
            eval_info["status"] = "failed"
            eval_info["error"] = str(e)
            eval_info["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(eval_info, f, ensure_ascii=False, indent=2)

            return eval_info

    def _is_pretrained(self, model_path):
        pretrained = ["yolo11n.pt", "yolo11s.pt", "yolo11m.pt", "yolo11l.pt", "yolo11x.pt"]
        return model_path in pretrained or os.path.basename(model_path) in pretrained

    def _extract_val_metrics(self, results):
        metrics = {}

        try:
            metrics["mAP50"] = round(float(results.box.map50), 4) if results.box.map50 is not None else 0
            metrics["mAP50-95"] = round(float(results.box.map), 4) if results.box.map is not None else 0
            metrics["precision"] = round(float(results.box.mp), 4) if results.box.mp is not None else 0
            metrics["recall"] = round(float(results.box.mr), 4) if results.box.mr is not None else 0

            if metrics["precision"] + metrics["recall"] > 0:
                metrics["f1"] = round(
                    2 * metrics["precision"] * metrics["recall"] / (metrics["precision"] + metrics["recall"]), 4
                )
            else:
                metrics["f1"] = 0

            metrics["fitness"] = round(float(results.fitness), 4) if results.fitness is not None else 0

            speed = {}
            if hasattr(results, "speed") and results.speed:
                speed["preprocess"] = round(results.speed.get("preprocess", 0), 2)
                speed["inference"] = round(results.speed.get("inference", 0), 2)
                speed["postprocess"] = round(results.speed.get("postprocess", 0), 2)
            metrics["speed"] = speed

        except Exception:
            pass

        return metrics

    def _extract_confusion_matrix(self, results):
        try:
            if hasattr(results, "confusion_matrix") and results.confusion_matrix is not None:
                cm = results.confusion_matrix
                if hasattr(cm, "matrix"):
                    return cm.matrix.tolist()
        except Exception:
            pass
        return None

    def _extract_per_class_metrics(self, results):
        per_class = []

        try:
            if hasattr(results, "box"):
                box = results.box

                if hasattr(box, "maps") and box.maps is not None:
                    for i, m in enumerate(box.maps):
                        per_class.append({
                            "class_id": i,
                            "mAP50-95": round(float(m), 4),
                        })

                if hasattr(box, "ap50") and box.ap50 is not None:
                    for i, ap in enumerate(box.ap50):
                        found = False
                        for pc in per_class:
                            if pc["class_id"] == i:
                                pc["mAP50"] = round(float(ap), 4)
                                found = True
                                break
                        if not found:
                            per_class.append({
                                "class_id": i,
                                "mAP50": round(float(ap), 4),
                            })

                if hasattr(box, "p") and box.p is not None:
                    for i, p in enumerate(box.p):
                        found = False
                        for pc in per_class:
                            if pc["class_id"] == i:
                                pc["precision"] = round(float(p), 4)
                                found = True
                                break
                        if not found:
                            per_class.append({
                                "class_id": i,
                                "precision": round(float(p), 4),
                            })

                if hasattr(box, "r") and box.r is not None:
                    for i, r in enumerate(box.r):
                        found = False
                        for pc in per_class:
                            if pc["class_id"] == i:
                                pc["recall"] = round(float(r), 4)
                                found = True
                                break
                        if not found:
                            per_class.append({
                                "class_id": i,
                                "recall": round(float(r), 4),
                            })

        except Exception:
            pass

        return per_class

    def compare_models(self, eval_ids):
        comparisons = []

        for eid in eval_ids:
            info_path = os.path.join(EVALUATION_DIR, f"eval_{eid}", "eval_info.json")
            if os.path.exists(info_path):
                with open(info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
                    if info.get("status") == "completed" and info.get("results"):
                        comparisons.append({
                            "eval_id": eid,
                            "model_path": info.get("model_path", ""),
                            "metrics": info["results"].get("metrics", {}),
                            "per_class_metrics": info["results"].get("per_class_metrics", []),
                        })

        if not comparisons:
            return {"error": "没有找到已完成的评估结果"}

        best_model = max(comparisons, key=lambda x: x["metrics"].get("mAP50-95", 0))

        return {
            "comparisons": comparisons,
            "best_model": best_model,
            "recommendation": self._generate_recommendation(comparisons),
        }

    def _generate_recommendation(self, comparisons):
        if not comparisons:
            return "无评估数据"

        best = max(comparisons, key=lambda x: x["metrics"].get("mAP50-95", 0))
        best_map = best["metrics"].get("mAP50-95", 0)
        best_p = best["metrics"].get("precision", 0)
        best_r = best["metrics"].get("recall", 0)

        recs = []
        recs.append(f"最佳模型: {os.path.basename(best['model_path'])}，mAP50-95={best_map:.4f}")

        if best_map < 0.3:
            recs.append("模型精度较低，建议增加训练数据量或调整超参数")
        elif best_map < 0.5:
            recs.append("模型精度一般，建议增加数据增强或调整学习率")
        elif best_map < 0.7:
            recs.append("模型精度良好，可尝试微调以进一步提升")
        else:
            recs.append("模型精度优秀，可用于生产部署")

        if best_p < 0.5:
            recs.append("精确率偏低，误检较多，建议提高置信度阈值或增加负样本")
        if best_r < 0.5:
            recs.append("召回率偏低，漏检较多，建议降低置信度阈值或增加正样本")

        if best_p > 0 and best_r > 0:
            f1 = 2 * best_p * best_r / (best_p + best_r)
            if f1 < 0.5:
                recs.append("F1分数偏低，精确率和召回率不均衡，建议调整检测阈值")

        return "；".join(recs)

    def list_evaluations(self):
        evals = []
        if not os.path.exists(EVALUATION_DIR):
            return evals

        for d in os.listdir(EVALUATION_DIR):
            info_path = os.path.join(EVALUATION_DIR, d, "eval_info.json")
            if os.path.exists(info_path):
                with open(info_path, "r", encoding="utf-8") as f:
                    evals.append(json.load(f))

        return sorted(evals, key=lambda x: x.get("started_at", ""), reverse=True)

    def get_evaluation(self, eval_id):
        info_path = os.path.join(EVALUATION_DIR, f"eval_{eval_id}", "eval_info.json")
        if not os.path.exists(info_path):
            return None

        with open(info_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def delete_evaluation(self, eval_id):
        eval_dir = os.path.join(EVALUATION_DIR, f"eval_{eval_id}")
        if os.path.exists(eval_dir):
            import shutil
            shutil.rmtree(eval_dir)
            return True
        return False

    def get_training_curves(self, training_id):
        run_name = f"train_{training_id}"
        results_csv = os.path.join(TRAINING_DIR, run_name, "weights", "results.csv")

        if not os.path.exists(results_csv):
            return None

        import csv
        curves = {
            "train_box_loss": [],
            "val_box_loss": [],
            "train_cls_loss": [],
            "val_cls_loss": [],
            "train_dfl_loss": [],
            "val_dfl_loss": [],
            "precision": [],
            "recall": [],
            "mAP50": [],
            "mAP50-95": [],
            "lr": [],
            "epochs": [],
        }

        with open(results_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                clean = {}
                for k, v in row.items():
                    clean[k.strip()] = v.strip() if isinstance(v, str) else v

                epoch = clean.get("epoch", "0")
                try:
                    epoch = int(float(epoch))
                except (ValueError, TypeError):
                    epoch = 0

                curves["epochs"].append(epoch)

                for key in ["train/box_loss", "val/box_loss", "train/cls_loss", "val/cls_loss",
                            "train/dfl_loss", "val/dfl_loss", "metrics/precision(B)",
                            "metrics/recall(B)", "metrics/mAP50(B)", "metrics/mAP50-95(B)",
                            "lr/pg0"]:
                    try:
                        val = float(clean.get(key, 0))
                    except (ValueError, TypeError):
                        val = 0

                    target_key = {
                        "train/box_loss": "train_box_loss",
                        "val/box_loss": "val_box_loss",
                        "train/cls_loss": "train_cls_loss",
                        "val/cls_loss": "val_cls_loss",
                        "train/dfl_loss": "train_dfl_loss",
                        "val/dfl_loss": "val_dfl_loss",
                        "metrics/precision(B)": "precision",
                        "metrics/recall(B)": "recall",
                        "metrics/mAP50(B)": "mAP50",
                        "metrics/mAP50-95(B)": "mAP50-95",
                        "lr/pg0": "lr",
                    }.get(key)

                    if target_key:
                        curves[target_key].append(val)

        return curves
