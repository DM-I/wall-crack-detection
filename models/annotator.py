import os
import json
import shutil
import uuid
import cv2
from datetime import datetime
from config import DATASET_DIR, CRACK_CLASSES, ALLOWED_EXTENSIONS


class Annotator:
    def create_dataset(self, name, description="", classes=None):
        dataset_id = str(uuid.uuid4())[:8]
        dataset_path = os.path.join(DATASET_DIR, dataset_id)

        os.makedirs(os.path.join(dataset_path, "images"), exist_ok=True)
        os.makedirs(os.path.join(dataset_path, "labels"), exist_ok=True)

        meta = {
            "dataset_id": dataset_id,
            "name": name,
            "description": description,
            "classes": classes or dict(CRACK_CLASSES),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "image_count": 0,
            "annotated_count": 0,
        }

        with open(os.path.join(dataset_path, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        return meta

    def import_dataset(self, name, source_dir, description=""):
        """Import an existing dataset from a folder path.
        Supports YOLO format (images + .txt labels) and plain images.
        """
        if not os.path.exists(source_dir) or not os.path.isdir(source_dir):
            return {"error": "源文件夹不存在"}

        # Create the dataset
        dataset_id = str(uuid.uuid4())[:8]
        dataset_path = os.path.join(DATASET_DIR, dataset_id)
        os.makedirs(os.path.join(dataset_path, "images"), exist_ok=True)
        os.makedirs(os.path.join(dataset_path, "labels"), exist_ok=True)

        # Scan source directory for images
        imported_images = 0
        imported_labels = 0
        detected_classes = {}

        # Check for YOLO structure (images/ and labels/ subdirs)
        src_images_dir = source_dir
        src_labels_dir = source_dir
        if os.path.exists(os.path.join(source_dir, "images")):
            src_images_dir = os.path.join(source_dir, "images")
        if os.path.exists(os.path.join(source_dir, "labels")):
            src_labels_dir = os.path.join(source_dir, "labels")

        # Scan function: walk a directory tree for images
        def _scan_dir(img_dir, lbl_dir, prefix=""):
            nonlocal imported_images, imported_labels
            for f in sorted(os.listdir(img_dir)):
                fpath = os.path.join(img_dir, f)
                # Recurse into subdirectories (train/val/test)
                if os.path.isdir(fpath):
                    sub_lbl = os.path.join(lbl_dir, f) if os.path.isdir(os.path.join(lbl_dir, f)) else lbl_dir
                    _scan_dir(fpath, sub_lbl, prefix + f + "/")
                    continue
                if not os.path.isfile(fpath):
                    continue
                ext = f.rsplit(".", 1)[-1].lower() if "." in f else ""
                if ext not in ALLOWED_EXTENSIONS:
                    continue

                # Copy image
                dst_img = os.path.join(dataset_path, "images", f)
                if not os.path.exists(dst_img):
                    shutil.copy2(fpath, dst_img)
                imported_images += 1

                # Try to find corresponding label
                label_name = os.path.splitext(f)[0] + ".txt"
                src_label = os.path.join(lbl_dir, label_name)
                dst_label = os.path.join(dataset_path, "labels", label_name)

                if os.path.exists(src_label):
                    with open(src_label, "r", encoding="utf-8") as lf:
                        lines = lf.read().strip().split("\n")
                    has_content = any(l.strip() for l in lines)
                    if has_content:
                        shutil.copy2(src_label, dst_label)
                        imported_labels += 1
                        for line in lines:
                            parts = line.strip().split()
                            if len(parts) >= 5:
                                cls_id = parts[0]
                                if cls_id not in detected_classes:
                                    detected_classes[cls_id] = int(cls_id)
                    else:
                        with open(dst_label, "w", encoding="utf-8") as lf:
                            pass

        _scan_dir(src_images_dir, src_labels_dir)

        if imported_images == 0:
            shutil.rmtree(dataset_path)
            return {"error": "源文件夹中未找到有效图片"}

        # Build classes from detected or default
        if detected_classes:
            max_id = max(detected_classes.values())
            classes = {}
            for i in range(max_id + 1):
                classes[str(i)] = CRACK_CLASSES.get(i, f"class_{i}")
        else:
            classes = dict(CRACK_CLASSES)

        # Write meta
        meta = {
            "dataset_id": dataset_id,
            "name": name,
            "description": description or f"从 {os.path.basename(source_dir)} 导入",
            "classes": classes,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "image_count": imported_images,
            "annotated_count": imported_labels,
            "source_dir": source_dir,
        }

        with open(os.path.join(dataset_path, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        return {"success": True, "dataset": meta}

    def list_datasets(self):
        datasets = []
        if not os.path.exists(DATASET_DIR):
            return datasets

        for d in os.listdir(DATASET_DIR):
            meta_path = os.path.join(DATASET_DIR, d, "meta.json")
            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    self._update_counts(meta)
                    datasets.append(meta)

        return sorted(datasets, key=lambda x: x.get("updated_at", ""), reverse=True)

    def get_dataset(self, dataset_id):
        meta_path = os.path.join(DATASET_DIR, dataset_id, "meta.json")
        if not os.path.exists(meta_path):
            return None

        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
            self._update_counts(meta)
        return meta

    def delete_dataset(self, dataset_id):
        dataset_path = os.path.join(DATASET_DIR, dataset_id)
        if os.path.exists(dataset_path):
            shutil.rmtree(dataset_path)
            return True
        return False

    def add_images(self, dataset_id, image_files):
        dataset_path = os.path.join(DATASET_DIR, dataset_id)
        images_dir = os.path.join(dataset_path, "images")
        labels_dir = os.path.join(dataset_path, "labels")

        if not os.path.exists(dataset_path):
            return None

        added = []
        for file_info in image_files:
            src_path = file_info["path"]
            if not os.path.exists(src_path):
                continue

            filename = file_info["filename"]
            dst_img = os.path.join(images_dir, filename)

            if os.path.abspath(src_path) != os.path.abspath(dst_img):
                shutil.copy2(src_path, dst_img)

            label_name = os.path.splitext(filename)[0] + ".txt"
            label_path = os.path.join(labels_dir, label_name)
            if not os.path.exists(label_path):
                with open(label_path, "w", encoding="utf-8") as f:
                    pass

            added.append({
                "filename": filename,
                "label_file": label_name,
                "has_annotation": False,
            })

        self._update_meta(dataset_id)
        return added

    def get_images(self, dataset_id, annotated_only=False, page=1, page_size=9999):
        dataset_path = os.path.join(DATASET_DIR, dataset_id)
        images_dir = os.path.join(dataset_path, "images")
        labels_dir = os.path.join(dataset_path, "labels")

        if not os.path.exists(images_dir):
            return {"images": [], "total": 0, "page": page, "page_size": page_size}

        all_images = []

        def _scan_dir(scan_dir, lbl_base_dir, prefix=""):
            results = []
            for f in sorted(os.scandir(scan_dir), key=lambda x: x.name):
                if not f.is_file():
                    continue
                ext = f.name.rsplit(".", 1)[-1].lower() if "." in f.name else ""
                if ext not in ALLOWED_EXTENSIONS:
                    continue

                rel_path = prefix + f.name
                label_rel = os.path.splitext(rel_path)[0] + ".txt"
                label_path = os.path.join(lbl_base_dir, label_rel)
                has_annotation = False
                annotation_count = 0

                if os.path.exists(label_path):
                    with open(label_path, "r", encoding="utf-8") as lf:
                        content = lf.read().strip()
                        if content:
                            has_annotation = True
                            annotation_count = len(content.split("\n"))

                if annotated_only and not has_annotation:
                    continue
                results.append({
                    "filename": rel_path.replace(os.sep, "/"),
                    "label_file": label_rel.replace(os.sep, "/"),
                    "has_annotation": has_annotation,
                    "annotation_count": annotation_count,
                })
            return results

        # Check if images are in root dir or in split subdirs
        has_root_images = False
        for f in os.scandir(images_dir):
            if f.is_file():
                has_root_images = True
                break

        if has_root_images:
            all_images = _scan_dir(images_dir, labels_dir)
        elif os.path.exists(os.path.join(images_dir, "train")):
            for split in ["train", "val", "test"]:
                split_img = os.path.join(images_dir, split)
                split_lbl = os.path.join(labels_dir, split)
                if os.path.isdir(split_img):
                    all_images.extend(_scan_dir(split_img, split_lbl, prefix=split + "/"))

        total = len(all_images)
        start = (page - 1) * page_size
        end = start + page_size
        page_images = all_images[start:end]

        return {
            "images": page_images,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_image_annotations(self, dataset_id, filename):
        dataset_path = os.path.join(DATASET_DIR, dataset_id)
        label_name = os.path.splitext(filename)[0] + ".txt"
        label_path = os.path.join(dataset_path, "labels", label_name)

        meta = self.get_dataset(dataset_id)
        if not meta:
            return None

        classes = meta.get("classes", {})

        annotations = []
        if os.path.exists(label_path):
            with open(label_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split()
                    if len(parts) >= 5:
                        cls_id = int(parts[0])
                        cx, cy, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                        cls_name = classes.get(str(cls_id), classes.get(cls_id, f"class_{cls_id}"))
                        annotations.append({
                            "class_id": cls_id,
                            "class_name": cls_name,
                            "cx": cx,
                            "cy": cy,
                            "w": w,
                            "h": h,
                        })

        img_path = os.path.join(dataset_path, "images", filename)
        img_size = {}
        if os.path.exists(img_path):
            img = cv2.imread(img_path)
            if img is not None:
                img_size = {"width": img.shape[1], "height": img.shape[0]}

        return {
            "filename": filename,
            "annotations": annotations,
            "image_size": img_size,
            "classes": classes,
        }

    def save_annotations(self, dataset_id, filename, annotations, format="yolo", extra_data=None):
        dataset_path = os.path.join(DATASET_DIR, dataset_id)

        meta = self.get_dataset(dataset_id)
        classes_dict = meta.get("classes", {}) if meta else {}
        name_to_id = {}
        for k, v in classes_dict.items():
            name_to_id[v] = int(k)

        if format == "labelme":
            # annotations is a full LabelMe JSON object
            return self._save_from_labelme(dataset_id, filename, annotations, name_to_id)

        # Default: YOLO format
        label_name = os.path.splitext(filename)[0] + ".txt"
        label_path = os.path.join(dataset_path, "labels", label_name)

        os.makedirs(os.path.dirname(label_path), exist_ok=True)

        with open(label_path, "w", encoding="utf-8") as f:
            for ann in annotations:
                cls_id = ann.get("class_id")
                if cls_id is None:
                    cls_name = ann.get("class_name", "")
                    cls_id = name_to_id.get(cls_name, 0)
                cx = ann.get("cx", 0)
                cy = ann.get("cy", 0)
                w = ann.get("w", 0)
                h = ann.get("h", 0)
                f.write(f"{cls_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")

        self._update_meta(dataset_id)
        return {"success": True, "count": len(annotations)}

    # ==================== LabelMe Format Support ====================

    def _save_from_labelme(self, dataset_id, filename, labelme_data, name_to_id):
        """Convert LabelMe JSON to internal YOLO txt format and save"""
        import cv2

        dataset_path = os.path.join(DATASET_DIR, dataset_id)
        label_name = os.path.splitext(filename)[0] + ".txt"
        label_path = os.path.join(dataset_path, "labels", label_name)

        os.makedirs(os.path.dirname(label_path), exist_ok=True)

        shapes = labelme_data.get("shapes", [])
        img_w = labelme_data.get("imageWidth", 1)
        img_h = labelme_data.get("imageHeight", 1)

        # Also try reading image to get dimensions if not in JSON
        if img_w <= 1:
            img_path = os.path.join(dataset_path, "images", filename)
            if os.path.exists(img_path):
                img = cv2.imread(img_path)
                if img is not None:
                    img_h, img_w = img.shape[:2]

        count = 0
        with open(label_path, "w", encoding="utf-8") as f:
            for shape in shapes:
                label = shape.get("label", "")
                cls_id = name_to_id.get(label)
                if cls_id is None:
                    continue  # skip unknown classes

                shape_type = shape.get("shape_type", "rectangle")
                points = shape.get("points", [])

                if shape_type == "rectangle" and len(points) >= 2:
                    x1, y1 = points[0]
                    x2, y2 = points[1]
                elif shape_type == "polygon" and len(points) >= 3:
                    # Polygon → bounding rectangle
                    xs = [p[0] for p in points]
                    ys = [p[1] for p in points]
                    x1, y1 = min(xs), min(ys)
                    x2, y2 = max(xs), max(ys)
                else:
                    continue

                # Convert absolute coords → YOLO normalized (cx, cy, w, h)
                bw = abs(x2 - x1)
                bh = abs(y2 - y1)
                cx = ((x1 + x2) / 2) / img_w
                cy = ((y1 + y2) / 2) / img_h
                w = bw / img_w
                h = bh / img_h

                f.write(f"{cls_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")
                count += 1

        self._update_meta(dataset_id)
        return {"success": True, "count": count, "format": "labelme"}

    def get_annotations_labelme(self, dataset_id, filename):
        """Get annotations in LabelMe JSON format"""
        import cv2, base64

        dataset_path = os.path.join(DATASET_DIR, dataset_id)
        meta = self.get_dataset(dataset_id)
        if not meta:
            return None

        classes = meta.get("classes", {})
        id_to_name = {}
        for k, v in classes.items():
            id_to_name[int(k)] = v

        img_path = os.path.join(dataset_path, "images", filename)
        img_h, img_w = 0, 0
        if os.path.exists(img_path):
            img = cv2.imread(img_path)
            if img is not None:
                img_h, img_w = img.shape[:2]

        # Fallback: try to get dimensions from label file bounding boxes
        if img_h == 0 or img_w == 0:
            label_name = os.path.splitext(filename)[0] + ".txt"
            label_path = os.path.join(dataset_path, "labels", label_name)
            if os.path.exists(label_path):
                with open(label_path, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            bw, bh = float(parts[3]), float(parts[4])
                            # Estimate from normalized coords — assume image at least 1000px
                            if bw > 0 and bh > 0:
                                img_w = max(img_w, 640)
                                img_h = max(img_h, 640)
            if img_w == 0:
                img_w, img_h = 640, 640  # default fallback

        label_name = os.path.splitext(filename)[0] + ".txt"
        label_path = os.path.join(dataset_path, "labels", label_name)

        shapes = []
        if os.path.exists(label_path):
            with open(label_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split()
                    if len(parts) >= 5:
                        cls_id = int(parts[0])
                        cx, cy, bw, bh = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                        # YOLO normalized → absolute coords
                        x1 = (cx - bw / 2) * img_w
                        y1 = (cy - bh / 2) * img_h
                        x2 = (cx + bw / 2) * img_w
                        y2 = (cy + bh / 2) * img_h
                        cls_name = id_to_name.get(cls_id, f"class_{cls_id}")

                        shapes.append({
                            "label": cls_name,
                            "points": [[x1, y1], [x2, y2]],
                            "group_id": None,
                            "shape_type": "rectangle",
                            "flags": {},
                        })

        labelme = {
            "version": "5.0.1",
            "flags": {},
            "shapes": shapes,
            "imagePath": filename,
            "imageData": None,
            "imageHeight": img_h,
            "imageWidth": img_w,
        }

        return labelme

    def import_labelme_dir(self, dataset_id, labelme_files):
        """Batch import LabelMe JSON files into dataset"""
        dataset_path = os.path.join(DATASET_DIR, dataset_id)
        meta = self.get_dataset(dataset_id)
        if not meta:
            return None

        classes_dict = meta.get("classes", {})
        name_to_id = {}
        for k, v in classes_dict.items():
            name_to_id[v] = int(k)

        imported, skipped = 0, 0
        for file_info in labelme_files:
            filepath = file_info.get("path", "")
            if not os.path.exists(filepath):
                skipped += 1
                continue

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    labelme_data = json.load(f)

                # Get image filename from LabelMe JSON
                image_path = labelme_data.get("imagePath", "")
                if not image_path:
                    skipped += 1
                    continue

                basename = os.path.basename(image_path)
                result = self._save_from_labelme(dataset_id, basename, labelme_data, name_to_id)
                if result.get("count", 0) > 0:
                    imported += 1
                else:
                    skipped += 1
            except Exception:
                skipped += 1

        self._update_meta(dataset_id)
        return {"imported": imported, "skipped": skipped}

    def auto_annotate(self, dataset_id, conf=0.25, iou=0.45):
        from models.detector import CrackDetector

        dataset_path = os.path.join(DATASET_DIR, dataset_id)
        images_dir = os.path.join(dataset_path, "images")
        labels_dir = os.path.join(dataset_path, "labels")

        if not os.path.exists(images_dir):
            return {"annotated": 0, "total": 0}

        detector = CrackDetector()
        annotated = 0
        total = 0

        for f in sorted(os.listdir(images_dir)):
            ext = f.rsplit(".", 1)[-1].lower() if "." in f else ""
            if ext not in ALLOWED_EXTENSIONS:
                continue

            total += 1
            img_path = os.path.join(images_dir, f)
            label_name = os.path.splitext(f)[0] + ".txt"
            label_path = os.path.join(labels_dir, label_name)

            try:
                result = detector.detect(img_path, conf_threshold=conf, iou_threshold=iou)
                detections = result.get("detections", [])

                if detections:
                    img = cv2.imread(img_path)
                    img_h, img_w = img.shape[:2] if img is not None else (0, 0)

                    with open(label_path, "w", encoding="utf-8") as lf:
                        for d in detections:
                            cls_id = d.get("class_id", 0)
                            bbox = d.get("bbox", {})
                            x1, y1, x2, y2 = bbox.get("x1", 0), bbox.get("y1", 0), bbox.get("x2", 0), bbox.get("y2", 0)
                            cx = ((x1 + x2) / 2) / img_w if img_w else 0
                            cy = ((y1 + y2) / 2) / img_h if img_h else 0
                            w = (x2 - x1) / img_w if img_w else 0
                            h = (y2 - y1) / img_h if img_h else 0
                            lf.write(f"{cls_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")

                    annotated += 1
            except Exception:
                pass

        self._update_meta(dataset_id)
        return {"annotated": annotated, "total": total}

    def split_dataset(self, dataset_id, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1, seed=42):
        import random

        dataset_path = os.path.join(DATASET_DIR, dataset_id)
        images_dir = os.path.join(dataset_path, "images")
        labels_dir = os.path.join(dataset_path, "labels")

        if not os.path.exists(images_dir):
            return None

        all_files = []
        for f in sorted(os.listdir(images_dir)):
            ext = f.rsplit(".", 1)[-1].lower() if "." in f else ""
            if ext in ALLOWED_EXTENSIONS:
                all_files.append(f)

        if not all_files:
            return None

        random.seed(seed)
        random.shuffle(all_files)

        total = len(all_files)
        train_end = int(total * train_ratio)
        val_end = train_end + int(total * val_ratio)

        splits = {
            "train": all_files[:train_end],
            "val": all_files[train_end:val_end],
            "test": all_files[val_end:],
        }

        for split_name in ["train", "val", "test"]:
            old_img = os.path.join(dataset_path, "images", split_name)
            old_lbl = os.path.join(dataset_path, "labels", split_name)
            if os.path.exists(old_img):
                shutil.rmtree(old_img)
            if os.path.exists(old_lbl):
                shutil.rmtree(old_lbl)

        for split_name, files in splits.items():
            split_img_dir = os.path.join(dataset_path, "images", split_name)
            split_lbl_dir = os.path.join(dataset_path, "labels", split_name)
            os.makedirs(split_img_dir, exist_ok=True)
            os.makedirs(split_lbl_dir, exist_ok=True)

        for split_name, files in splits.items():
            for f in files:
                src_img = os.path.join(images_dir, f)
                dst_img = os.path.join(dataset_path, "images", split_name, f)
                if os.path.exists(src_img) and not os.path.exists(dst_img):
                    shutil.copy2(src_img, dst_img)

                label_name = os.path.splitext(f)[0] + ".txt"
                src_lbl = os.path.join(labels_dir, label_name)
                dst_lbl = os.path.join(dataset_path, "labels", split_name, label_name)
                if os.path.exists(src_lbl) and not os.path.exists(dst_lbl):
                    shutil.copy2(src_lbl, dst_lbl)

        meta = self.get_dataset(dataset_id)
        classes = meta.get("classes", {})

        yaml_classes = {}
        for k, v in classes.items():
            yaml_classes[int(k)] = v

        yaml_content = f"path: {dataset_path.replace(os.sep, '/')}\n"
        yaml_content += f"train: images/train\n"
        yaml_content += f"val: images/val\n"
        yaml_content += f"test: images/test\n\n"
        yaml_content += f"nc: {len(yaml_classes)}\n"
        yaml_content += f"names: {json.dumps(yaml_classes, ensure_ascii=False)}\n"

        yaml_path = os.path.join(dataset_path, "data.yaml")
        with open(yaml_path, "w", encoding="utf-8") as f:
            f.write(yaml_content)

        split_info = {
            "dataset_id": dataset_id,
            "total": total,
            "train": len(splits["train"]),
            "val": len(splits["val"]),
            "test": len(splits["test"]),
            "ratios": {"train": train_ratio, "val": val_ratio, "test": test_ratio},
            "yaml_path": yaml_path,
        }

        meta_path = os.path.join(dataset_path, "meta.json")
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        meta["split_info"] = split_info
        meta["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        return split_info

    def export_dataset(self, dataset_id, format="yolo"):
        dataset_path = os.path.join(DATASET_DIR, dataset_id)
        if not os.path.exists(dataset_path):
            return None

        export_dir = os.path.join(dataset_path, "export")
        os.makedirs(export_dir, exist_ok=True)

        if format == "yolo":
            return self._export_yolo(dataset_path, export_dir)
        elif format == "coco":
            return self._export_coco(dataset_path, export_dir)
        elif format == "voc":
            return self._export_voc(dataset_path, export_dir)
        elif format == "labelme":
            return self._export_labelme(dataset_path, export_dir)

        return None

    def _export_yolo(self, dataset_path, export_dir):
        import zipfile

        zip_path = os.path.join(export_dir, "dataset_yolo.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            yaml_path = os.path.join(dataset_path, "data.yaml")
            if os.path.exists(yaml_path):
                zf.write(yaml_path, "data.yaml")

            for split in ["train", "val", "test"]:
                img_dir = os.path.join(dataset_path, "images", split)
                lbl_dir = os.path.join(dataset_path, "labels", split)

                if os.path.exists(img_dir):
                    for f in os.listdir(img_dir):
                        fp = os.path.join(img_dir, f)
                        if os.path.isfile(fp):
                            zf.write(fp, f"images/{split}/{f}")
                else:
                    img_root = os.path.join(dataset_path, "images")
                    if os.path.exists(img_root):
                        for f in os.listdir(img_root):
                            fp = os.path.join(img_root, f)
                            ext = f.rsplit(".", 1)[-1].lower() if "." in f else ""
                            if os.path.isfile(fp) and ext in ALLOWED_EXTENSIONS:
                                zf.write(fp, f"images/{f}")

                if os.path.exists(lbl_dir):
                    for f in os.listdir(lbl_dir):
                        fp = os.path.join(lbl_dir, f)
                        if os.path.isfile(fp):
                            zf.write(fp, f"labels/{split}/{f}")
                else:
                    lbl_root = os.path.join(dataset_path, "labels")
                    if os.path.exists(lbl_root):
                        for f in os.listdir(lbl_root):
                            fp = os.path.join(lbl_root, f)
                            if os.path.isfile(fp) and f.endswith(".txt"):
                                zf.write(os.path.join(lbl_root, f), f"labels/{f}")

        return {"path": zip_path, "format": "yolo"}

    def _export_coco(self, dataset_path, export_dir):
        import cv2

        meta = self.get_dataset(os.path.basename(dataset_path))
        classes = meta.get("classes", {}) if meta else {}
        categories = []
        for k, v in classes.items():
            categories.append({"id": int(k), "name": v})

        images_list = []
        annotations_list = []
        ann_id = 1

        images_dir = os.path.join(dataset_path, "images")
        labels_dir = os.path.join(dataset_path, "labels")

        img_files = []
        if os.path.exists(images_dir):
            for f in sorted(os.listdir(images_dir)):
                ext = f.rsplit(".", 1)[-1].lower() if "." in f else ""
                if ext in ALLOWED_EXTENSIONS:
                    img_files.append(f)

        for idx, img_file in enumerate(img_files, 1):
            img_path = os.path.join(images_dir, img_file)
            img = cv2.imread(img_path)
            if img is None:
                continue
            h, w = img.shape[:2]

            images_list.append({
                "id": idx,
                "file_name": img_file,
                "width": w,
                "height": h,
            })

            label_name = os.path.splitext(img_file)[0] + ".txt"
            label_path = os.path.join(labels_dir, label_name)

            if os.path.exists(label_path):
                with open(label_path, "r") as lf:
                    for line in lf:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            cls_id = int(parts[0])
                            cx, cy, bw, bh = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                            x = (cx - bw / 2) * w
                            y = (cy - bh / 2) * h
                            abs_w = bw * w
                            abs_h = bh * h

                            annotations_list.append({
                                "id": ann_id,
                                "image_id": idx,
                                "category_id": cls_id,
                                "bbox": [round(x, 2), round(y, 2), round(abs_w, 2), round(abs_h, 2)],
                                "area": round(abs_w * abs_h, 2),
                                "iscrowd": 0,
                            })
                            ann_id += 1

        coco = {
            "images": images_list,
            "annotations": annotations_list,
            "categories": categories,
        }

        coco_path = os.path.join(export_dir, "coco_annotations.json")
        with open(coco_path, "w", encoding="utf-8") as f:
            json.dump(coco, f, ensure_ascii=False, indent=2)

        return {"path": coco_path, "format": "coco"}

    def _export_voc(self, dataset_path, export_dir):
        import xml.etree.ElementTree as ET
        import cv2

        meta = self.get_dataset(os.path.basename(dataset_path))
        classes = meta.get("classes", {}) if meta else {}

        voc_dir = os.path.join(export_dir, "voc_labels")
        os.makedirs(voc_dir, exist_ok=True)

        images_dir = os.path.join(dataset_path, "images")
        labels_dir = os.path.join(dataset_path, "labels")

        count = 0
        if os.path.exists(images_dir):
            for f in sorted(os.listdir(images_dir)):
                ext = f.rsplit(".", 1)[-1].lower() if "." in f else ""
                if ext not in ALLOWED_EXTENSIONS:
                    continue

                img_path = os.path.join(images_dir, f)
                img = cv2.imread(img_path)
                if img is None:
                    continue
                h, w, d = img.shape

                root = ET.Element("annotation")
                ET.SubElement(root, "folder").text = "images"
                ET.SubElement(root, "filename").text = f
                size = ET.SubElement(root, "size")
                ET.SubElement(size, "width").text = str(w)
                ET.SubElement(size, "height").text = str(h)
                ET.SubElement(size, "depth").text = str(d)

                label_name = os.path.splitext(f)[0] + ".txt"
                label_path = os.path.join(labels_dir, label_name)

                if os.path.exists(label_path):
                    with open(label_path, "r") as lf:
                        for line in lf:
                            parts = line.strip().split()
                            if len(parts) >= 5:
                                cls_id = int(parts[0])
                                cx, cy, bw, bh = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                                xmin = int((cx - bw / 2) * w)
                                ymin = int((cy - bh / 2) * h)
                                xmax = int((cx + bw / 2) * w)
                                ymax = int((cy + bh / 2) * h)
                                cls_name = classes.get(str(cls_id), classes.get(cls_id, f"class_{cls_id}"))

                                obj = ET.SubElement(root, "object")
                                ET.SubElement(obj, "name").text = cls_name
                                ET.SubElement(obj, "pose").text = "Unspecified"
                                ET.SubElement(obj, "truncated").text = "0"
                                ET.SubElement(obj, "difficult").text = "0"
                                bndbox = ET.SubElement(obj, "bndbox")
                                ET.SubElement(bndbox, "xmin").text = str(max(0, xmin))
                                ET.SubElement(bndbox, "ymin").text = str(max(0, ymin))
                                ET.SubElement(bndbox, "xmax").text = str(min(w, xmax))
                                ET.SubElement(bndbox, "ymax").text = str(min(h, ymax))

                tree = ET.ElementTree(root)
                xml_name = os.path.splitext(f)[0] + ".xml"
                tree.write(os.path.join(voc_dir, xml_name), encoding="utf-8", xml_declaration=True)
                count += 1

        return {"path": voc_dir, "format": "voc", "count": count}

    def _export_labelme(self, dataset_path, export_dir):
        """Export annotations in LabelMe JSON format"""
        import cv2, base64

        meta = self.get_dataset(os.path.basename(dataset_path))
        classes = meta.get("classes", {}) if meta else {}
        id_to_name = {int(k): v for k, v in classes.items()}

        labelme_dir = os.path.join(export_dir, "labelme")
        os.makedirs(labelme_dir, exist_ok=True)

        images_dir = os.path.join(dataset_path, "images")
        labels_dir = os.path.join(dataset_path, "labels")

        exported = 0
        img_files = []
        if os.path.exists(images_dir):
            for f in sorted(os.listdir(images_dir)):
                ext = f.rsplit(".", 1)[-1].lower() if "." in f else ""
                if ext in ALLOWED_EXTENSIONS:
                    img_files.append(f)

        for img_file in img_files:
            img_path = os.path.join(images_dir, img_file)
            img = cv2.imread(img_path)
            if img is None:
                continue
            img_h, img_w = img.shape[:2]

            label_name = os.path.splitext(img_file)[0] + ".txt"
            label_path = os.path.join(labels_dir, label_name)

            shapes = []
            if os.path.exists(label_path):
                with open(label_path, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) < 5:
                            continue
                        cls_id = int(parts[0])
                        cx, cy, bw, bh = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                        x1 = (cx - bw / 2) * img_w
                        y1 = (cy - bh / 2) * img_h
                        x2 = (cx + bw / 2) * img_w
                        y2 = (cy + bh / 2) * img_h
                        cls_name = id_to_name.get(cls_id, f"class_{cls_id}")

                        shapes.append({
                            "label": cls_name,
                            "points": [[x1, y1], [x2, y2]],
                            "group_id": None,
                            "shape_type": "rectangle",
                            "flags": {},
                        })

            labelme_json = {
                "version": "5.0.1",
                "flags": {},
                "shapes": shapes,
                "imagePath": img_file,
                "imageData": None,
                "imageHeight": img_h,
                "imageWidth": img_w,
            }

            json_name = os.path.splitext(img_file)[0] + ".json"
            json_path = os.path.join(labelme_dir, json_name)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(labelme_json, f, ensure_ascii=False, indent=2)
            exported += 1

        return {"path": labelme_dir, "format": "labelme", "count": exported}

    def update_classes(self, dataset_id, classes):
        dataset_path = os.path.join(DATASET_DIR, dataset_id)
        meta_path = os.path.join(dataset_path, "meta.json")

        if not os.path.exists(meta_path):
            return None

        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        meta["classes"] = classes
        meta["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        return meta

    def delete_image(self, dataset_id, filename):
        dataset_path = os.path.join(DATASET_DIR, dataset_id)
        img_path = os.path.join(dataset_path, "images", filename)
        label_name = os.path.splitext(filename)[0] + ".txt"
        lbl_path = os.path.join(dataset_path, "labels", label_name)

        deleted = False
        if os.path.exists(img_path):
            os.remove(img_path)
            deleted = True
        if os.path.exists(lbl_path):
            os.remove(lbl_path)
            deleted = True

        self._update_meta(dataset_id)
        return deleted

    def _update_counts(self, meta):
        dataset_id = meta.get("dataset_id", "")
        dataset_path = os.path.join(DATASET_DIR, dataset_id)
        images_dir = os.path.join(dataset_path, "images")
        labels_dir = os.path.join(dataset_path, "labels")

        image_count = 0
        annotated_count = 0

        if os.path.exists(images_dir):
            for f in os.scandir(images_dir):
                if f.is_file():
                    ext = f.name.rsplit(".", 1)[-1].lower() if "." in f.name else ""
                    if ext in ALLOWED_EXTENSIONS:
                        image_count += 1
                        label_name = os.path.splitext(f.name)[0] + ".txt"
                        label_path = os.path.join(labels_dir, label_name)
                        if os.path.exists(label_path):
                            with open(label_path, "r", encoding="utf-8") as lf:
                                if lf.read().strip():
                                    annotated_count += 1

            if image_count == 0 and os.path.exists(os.path.join(images_dir, "train")):
                for split in ["train", "val", "test"]:
                    split_img = os.path.join(images_dir, split)
                    split_lbl = os.path.join(labels_dir, split)
                    if os.path.isdir(split_img):
                        for f in os.scandir(split_img):
                            if not f.is_file():
                                continue
                            ext = f.name.rsplit(".", 1)[-1].lower() if "." in f.name else ""
                            if ext not in ALLOWED_EXTENSIONS:
                                continue
                            image_count += 1
                            label_name = os.path.splitext(f.name)[0] + ".txt"
                            label_path = os.path.join(split_lbl, label_name)
                            if os.path.exists(label_path):
                                with open(label_path, "r", encoding="utf-8") as lf:
                                    if lf.read().strip():
                                        annotated_count += 1

        meta["image_count"] = image_count
        meta["annotated_count"] = annotated_count

    def _update_meta(self, dataset_id):
        meta_path = os.path.join(DATASET_DIR, dataset_id, "meta.json")
        if not os.path.exists(meta_path):
            return

        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        self._update_counts(meta)
        meta["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
