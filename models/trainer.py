import os
import json
import shutil
import threading
import uuid
from datetime import datetime
from config import TRAINING_DIR, WEIGHTS_DIR, DATASET_DIR, TRAINING_DEFAULTS


class Trainer:
    def __init__(self):
        self._active_training = {}
        self._training_lock = threading.Lock()
        self._cleanup_stale_statuses()

    def _cleanup_stale_statuses(self):
        """服务重启时，将残留的 running/pending 状态标记为 interrupted"""
        if not os.path.exists(TRAINING_DIR):
            return
        stale_statuses = {"running", "pending"}
        for d in os.listdir(TRAINING_DIR):
            info_path = os.path.join(TRAINING_DIR, d, "training_info.json")
            if not os.path.exists(info_path):
                continue
            try:
                with open(info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
                if info.get("status") in stale_statuses:
                    info["status"] = "interrupted"
                    info["error"] = info.get("error") or "服务重启导致训练中断"
                    info["completed_at"] = info.get("completed_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with open(info_path, "w", encoding="utf-8") as f:
                        json.dump(info, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

    def start_training(self, dataset_id, config=None):
        dataset_path = os.path.join(DATASET_DIR, dataset_id)
        yaml_path = os.path.join(dataset_path, "data.yaml")

        if not os.path.exists(yaml_path):
            return {"error": "数据集未分割，请先执行数据集分割操作"}

        cfg = dict(TRAINING_DEFAULTS)
        if config:
            cfg.update(config)

        training_id = str(uuid.uuid4())[:8]
        run_name = f"train_{training_id}"
        project_dir = os.path.join(TRAINING_DIR, run_name)
        os.makedirs(project_dir, exist_ok=True)

        training_info = {
            "training_id": training_id,
            "dataset_id": dataset_id,
            "run_name": run_name,
            "config": cfg,
            "status": "pending",
            "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "completed_at": None,
            "project_dir": project_dir,
            "yaml_path": yaml_path,
            "results": None,
            "error": None,
        }

        info_path = os.path.join(project_dir, "training_info.json")
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump(training_info, f, ensure_ascii=False, indent=2)

        with self._training_lock:
            self._active_training[training_id] = training_info

        thread = threading.Thread(
            target=self._run_training,
            args=(training_id, yaml_path, project_dir, cfg),
            daemon=True,
        )
        thread.start()

        return training_info

    def _run_training(self, training_id, yaml_path, project_dir, cfg):
        info_path = os.path.join(project_dir, "training_info.json")

        try:
            self._update_status(training_id, "running", project_dir)

            from ultralytics import YOLO

            model_path = cfg.get("model", "yolo11n.pt")
            model = YOLO(model_path)

            train_kwargs = {
                "data": yaml_path,
                "epochs": cfg.get("epochs", 100),
                "batch": cfg.get("batch_size", 16),
                "imgsz": cfg.get("imgsz", 640),
                "patience": cfg.get("patience", 50),
                "lr0": cfg.get("lr0", 0.01),
                "lrf": cfg.get("lrf", 0.01),
                "momentum": cfg.get("momentum", 0.937),
                "weight_decay": cfg.get("weight_decay", 0.0005),
                "warmup_epochs": cfg.get("warmup_epochs", 3),
                "warmup_momentum": cfg.get("warmup_momentum", 0.8),
                "warmup_bias_lr": cfg.get("warmup_bias_lr", 0.1),
                "box": cfg.get("box", 7.5),
                "cls": cfg.get("cls", 0.5),
                "dfl": cfg.get("dfl", 1.5),
                "label_smoothing": cfg.get("label_smoothing", 0.0),
                "hsv_h": cfg.get("hsv_h", 0.015),
                "hsv_s": cfg.get("hsv_s", 0.7),
                "hsv_v": cfg.get("hsv_v", 0.4),
                "degrees": cfg.get("degrees", 0.0),
                "translate": cfg.get("translate", 0.1),
                "scale": cfg.get("scale", 0.5),
                "shear": cfg.get("shear", 0.0),
                "perspective": cfg.get("perspective", 0.0),
                "flipud": cfg.get("flipud", 0.0),
                "fliplr": cfg.get("fliplr", 0.5),
                "mosaic": cfg.get("mosaic", 1.0),
                "mixup": cfg.get("mixup", 0.0),
                "copy_paste": cfg.get("copy_paste", 0.0),
                "project": project_dir,
                "name": "weights",
                "exist_ok": True,
                "verbose": True,
                "val": True,
                "plots": True,
                "save": True,
                "save_period": cfg.get("save_period", -1),
            }

            # YOLO 训练：epochs 轮训练 + 1 轮最终验证 = 共 epochs+1 次记录入 CSV
            results = model.train(**train_kwargs)

            # === 训练完成，立即更新状态为 completed（放在最前面确保必定执行）===
            completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Step 1: 先收集训练产出信息（即使部分失败也不影响状态更新）
            weights_dir = os.path.join(project_dir, "weights")
            best_weight = os.path.join(weights_dir, "weights", "best.pt")
            last_weight = os.path.join(weights_dir, "weights", "last.pt")

            final_best = os.path.join(project_dir, "best.pt")
            final_last = os.path.join(project_dir, "last.pt")

            try:
                if os.path.exists(best_weight):
                    shutil.copy2(best_weight, final_best)
                if os.path.exists(last_weight):
                    shutil.copy2(last_weight, final_last)
            except Exception:
                pass  # 权重拷贝失败不阻塞状态更新

            try:
                metrics = self._extract_metrics(weights_dir)
            except Exception:
                metrics = {"best_epoch": {}, "last_epoch": {}}

            training_results = {
                "best_weight": final_best if os.path.exists(final_best) else None,
                "last_weight": final_last if os.path.exists(final_last) else None,
                "metrics": metrics,
            }

            # Step 2: 更新内存状态
            with self._training_lock:
                if training_id in self._active_training:
                    self._active_training[training_id]["status"] = "completed"
                    self._active_training[training_id]["results"] = training_results
                    self._active_training[training_id]["completed_at"] = completed_at

            # Step 3: 持久化到磁盘（原子化写入）
            try:
                with open(info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
            except Exception:
                info = {}
            info["status"] = "completed"
            info["results"] = training_results
            info["completed_at"] = completed_at
            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(info, f, ensure_ascii=False, indent=2)

        except Exception as e:
            error_msg = str(e)

            with self._training_lock:
                if training_id in self._active_training:
                    self._active_training[training_id]["status"] = "failed"
                    self._active_training[training_id]["error"] = error_msg

            try:
                with open(info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
            except Exception:
                info = {}
            info["status"] = "failed"
            info["error"] = error_msg
            info["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(info, f, ensure_ascii=False, indent=2)

    def _update_status(self, training_id, status, project_dir):
        info_path = os.path.join(project_dir, "training_info.json")
        with self._training_lock:
            if training_id in self._active_training:
                self._active_training[training_id]["status"] = status

        with open(info_path, "r", encoding="utf-8") as f:
            info = json.load(f)
        info["status"] = status
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

    def _extract_metrics(self, weights_dir):
        results_csv = os.path.join(weights_dir, "results.csv")
        metrics = {}

        if os.path.exists(results_csv):
            import csv
            # 显式指定 UTF-8 编码，避免 Windows GBK 默认编码导致读取失败
            with open(results_csv, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if rows:
                    # YOLO 会在配置的 epochs 之后追加一轮最终验证
                    # 例如 epochs=100 时 CSV 有 101 行（100 轮训练 + 1 轮最终验证）
                    # 取最后一行作为 last_epoch
                    last_row = rows[-1]
                    clean_last = {}
                    for k, v in last_row.items():
                        clean_last[k.strip()] = v.strip() if isinstance(v, str) else v
                    metrics["last_epoch"] = clean_last

                    # 遍历所有行找 mAP50-95 最大值对应的 epoch
                    best_map = 0
                    best_row = None
                    for row in rows:
                        clean_row = {}
                        for k, v in row.items():
                            clean_row[k.strip()] = v.strip() if isinstance(v, str) else v
                        try:
                            m = float(clean_row.get("metrics/mAP50-95(B)", 0))
                            if m > best_map:
                                best_map = m
                                best_row = clean_row
                        except (ValueError, TypeError):
                            pass
                    if best_row:
                        metrics["best_epoch"] = best_row

        return metrics

    def get_training_status(self, training_id):
        with self._training_lock:
            if training_id in self._active_training:
                return self._active_training[training_id]

        info_path = os.path.join(TRAINING_DIR, f"train_{training_id}", "training_info.json")
        if os.path.exists(info_path):
            with open(info_path, "r", encoding="utf-8") as f:
                return json.load(f)

        return None

    def get_training_progress(self, training_id):
        run_name = f"train_{training_id}"
        project_dir = os.path.join(TRAINING_DIR, run_name)
        weights_dir = os.path.join(project_dir, "weights")
        results_csv = os.path.join(weights_dir, "results.csv")

        if not os.path.exists(results_csv):
            return {"epochs_completed": 0, "total_epochs": 0, "metrics": []}

        import csv
        epochs = []
        with open(results_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                clean = {}
                for k, v in row.items():
                    clean[k.strip()] = v.strip() if isinstance(v, str) else v
                epochs.append(clean)

        total_epochs = 0
        info_path = os.path.join(project_dir, "training_info.json")
        if os.path.exists(info_path):
            with open(info_path, "r", encoding="utf-8") as f:
                info = json.load(f)
                total_epochs = info.get("config", {}).get("epochs", 0)

        return {
            "epochs_completed": len(epochs),
            "total_epochs": total_epochs,
            "metrics": epochs,
        }

    def list_trainings(self):
        trainings = []
        if not os.path.exists(TRAINING_DIR):
            return trainings

        for d in os.listdir(TRAINING_DIR):
            info_path = os.path.join(TRAINING_DIR, d, "training_info.json")
            if os.path.exists(info_path):
                with open(info_path, "r", encoding="utf-8") as f:
                    trainings.append(json.load(f))

        return sorted(trainings, key=lambda x: x.get("started_at", ""), reverse=True)

    def stop_training(self, training_id):
        with self._training_lock:
            if training_id in self._active_training:
                self._active_training[training_id]["status"] = "stopped"

        info_path = os.path.join(TRAINING_DIR, f"train_{training_id}", "training_info.json")
        if os.path.exists(info_path):
            with open(info_path, "r", encoding="utf-8") as f:
                info = json.load(f)
            info["status"] = "stopped"
            info["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(info, f, ensure_ascii=False, indent=2)

        return {"success": True, "training_id": training_id}

    def resume_training(self, training_id):
        project_dir = os.path.join(TRAINING_DIR, f"train_{training_id}")
        info_path = os.path.join(project_dir, "training_info.json")

        if not os.path.exists(info_path):
            return {"error": "训练记录不存在"}

        with open(info_path, "r", encoding="utf-8") as f:
            info = json.load(f)

        if info.get("status") == "running":
            return {"error": "训练已在运行中"}

        # Find the last checkpoint
        last_pt = os.path.join(project_dir, "last.pt")
        if not os.path.exists(last_pt):
            last_pt = os.path.join(project_dir, "weights", "last.pt")
        if not os.path.exists(last_pt):
            last_pt = os.path.join(project_dir, "weights", "weights", "last.pt")

        if not os.path.exists(last_pt):
            return {"error": "未找到可恢复的检查点文件，请重新开始训练"}

        cfg = info.get("config", {})
        yaml_path = info.get("yaml_path", "")

        if not yaml_path or not os.path.exists(yaml_path):
            return {"error": "数据集配置文件不存在"}

        # Keep the same training_id but update status
        info["status"] = "pending"
        info["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        info["completed_at"] = None
        info["results"] = None
        info["error"] = None
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

        with self._training_lock:
            self._active_training[training_id] = info

        thread = threading.Thread(
            target=self._run_resume_training,
            args=(training_id, last_pt, yaml_path, project_dir, cfg),
            daemon=True,
        )
        thread.start()

        return info

    def _run_resume_training(self, training_id, checkpoint_path, yaml_path, project_dir, cfg):
        info_path = os.path.join(project_dir, "training_info.json")

        try:
            self._update_status(training_id, "running", project_dir)

            from ultralytics import YOLO

            model = YOLO(checkpoint_path)

            results = model.train(resume=True, project=project_dir, name="weights", exist_ok=True)

            # === 训练完成，立即更新状态 ===
            completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            weights_dir = os.path.join(project_dir, "weights")
            best_weight = os.path.join(weights_dir, "weights", "best.pt")
            last_weight = os.path.join(weights_dir, "weights", "last.pt")

            final_best = os.path.join(project_dir, "best.pt")
            final_last = os.path.join(project_dir, "last.pt")

            try:
                if os.path.exists(best_weight):
                    shutil.copy2(best_weight, final_best)
                if os.path.exists(last_weight):
                    shutil.copy2(last_weight, final_last)
            except Exception:
                pass

            try:
                metrics = self._extract_metrics(weights_dir)
            except Exception:
                metrics = {"best_epoch": {}, "last_epoch": {}}

            training_results = {
                "best_weight": final_best if os.path.exists(final_best) else None,
                "last_weight": final_last if os.path.exists(final_last) else None,
                "metrics": metrics,
            }

            with self._training_lock:
                if training_id in self._active_training:
                    self._active_training[training_id]["status"] = "completed"
                    self._active_training[training_id]["results"] = training_results
                    self._active_training[training_id]["completed_at"] = completed_at

            try:
                with open(info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
            except Exception:
                info = {}
            info["status"] = "completed"
            info["results"] = training_results
            info["completed_at"] = completed_at
            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(info, f, ensure_ascii=False, indent=2)

        except Exception as e:
            error_msg = str(e)
            with self._training_lock:
                if training_id in self._active_training:
                    self._active_training[training_id]["status"] = "failed"
                    self._active_training[training_id]["error"] = error_msg

            try:
                with open(info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
            except Exception:
                info = {}
            info["status"] = "failed"
            info["error"] = error_msg
            info["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(info, f, ensure_ascii=False, indent=2)

    def delete_training(self, training_id):
        run_name = f"train_{training_id}"
        project_dir = os.path.join(TRAINING_DIR, run_name)
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)

        with self._training_lock:
            self._active_training.pop(training_id, None)

        return {"success": True}

    def get_available_models(self):
        models = []

        pretrained_names = {"yolo11n.pt", "yolo11s.pt", "yolo11m.pt", "yolo11l.pt", "yolo11x.pt"}

        if os.path.exists(WEIGHTS_DIR):
            for f in os.listdir(WEIGHTS_DIR):
                if f.endswith(".pt") and f not in pretrained_names:
                    models.append({
                        "name": f,
                        "path": os.path.join(WEIGHTS_DIR, f),
                        "type": "custom",
                    })

        for m in sorted(pretrained_names):
            models.append({
                "name": m,
                "path": m,
                "type": "pretrained",
            })

        if os.path.exists(TRAINING_DIR):
            for d in os.listdir(TRAINING_DIR):
                train_dir = os.path.join(TRAINING_DIR, d)
                if not os.path.isdir(train_dir):
                    continue
                best_path = os.path.join(train_dir, "best.pt")
                if not os.path.exists(best_path):
                    best_path = os.path.join(train_dir, "weights", "best.pt")
                if not os.path.exists(best_path):
                    best_path = os.path.join(train_dir, "weights", "weights", "best.pt")
                if os.path.exists(best_path):
                    info_path = os.path.join(train_dir, "training_info.json")
                    train_info = {}
                    if os.path.exists(info_path):
                        try:
                            import json
                            train_info = json.load(open(info_path, "r", encoding="utf-8"))
                        except:
                            pass
                    status = train_info.get("status", "")
                    name = train_info.get("run_name", d)
                    if status == "completed":
                        name += " (已完成)"
                    elif status == "running":
                        name += " (训练中)"
                    models.append({
                        "name": name,
                        "path": best_path,
                        "type": "trained",
                    })

        return models
