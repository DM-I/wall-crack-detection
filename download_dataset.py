import os
import sys
import json
import zipfile
import shutil
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")

DATASETS_INFO = {
    "crack-seg": {
        "name": "Ultralytics Crack Segmentation",
        "description": "Ultralytics官方裂缝分割数据集，4029张图片，YOLO格式",
        "urls": [
            "https://github.com/ultralytics/assets/releases/download/v0.0.0/crack-seg.zip",
            "https://ghgo.xyz/https://github.com/ultralytics/assets/releases/download/v0.0.0/crack-seg.zip",
            "https://gh-proxy.com/https://github.com/ultralytics/assets/releases/download/v0.0.0/crack-seg.zip",
            "https://mirror.ghproxy.com/https://github.com/ultralytics/assets/releases/download/v0.0.0/crack-seg.zip",
        ],
        "size_mb": 91.6,
        "image_count": 4029,
        "classes": {"0": "crack"},
        "format": "yolo",
        "pre_split": True,
        "ultralytics_key": "crack-seg.yaml",
    },
    "surface-crack": {
        "name": "Surface Crack Detection (Kaggle)",
        "description": "混凝土表面裂缝检测数据集，40000张图片(正负各半)，227x227像素",
        "urls": [
            "https://www.kaggle.com/api/v1/datasets/download/arunrk7/surface-crack-detection",
        ],
        "size_mb": 233,
        "image_count": 40000,
        "classes": {"0": "Negative", "1": "Positive"},
        "format": "classification",
        "pre_split": False,
    },
    "crack-detection-yolo": {
        "name": "Crack Detection YOLO (Kaggle)",
        "description": "桥梁裂缝检测数据集，YOLO格式标注",
        "urls": [
            "https://www.kaggle.com/api/v1/datasets/download/cvvlearner/a-crack-dataset",
        ],
        "size_mb": 200,
        "image_count": 3400,
        "classes": {"0": "crack"},
        "format": "yolo",
        "pre_split": False,
    },
}


def _download_with_progress(url, save_path):
    import urllib.request

    def progress_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        pct = min(downloaded / total_size * 100, 100) if total_size > 0 else 0
        mb_downloaded = downloaded / 1024 / 1024
        mb_total = total_size / 1024 / 1024
        sys.stdout.write("\r      Progress: %.1f%% (%.1f / %.1f MB)" % (pct, mb_downloaded, mb_total))
        sys.stdout.flush()

    urllib.request.urlretrieve(url, save_path, progress_hook)
    print()


def download_dataset(dataset_key="crack-seg"):
    if dataset_key not in DATASETS_INFO:
        print("[ERROR] Unknown dataset: %s" % dataset_key)
        print("Available datasets:")
        for k, v in DATASETS_INFO.items():
            print("  %s - %s (%d images, ~%.0f MB)" % (k, v["name"], v["image_count"], v["size_mb"]))
        return None

    info = DATASETS_INFO[dataset_key]
    extract_dir = os.path.join(DATASETS_DIR, dataset_key)
    zip_path = os.path.join(DATASETS_DIR, "%s_new.zip" % dataset_key)

    if os.path.exists(extract_dir) and os.path.exists(os.path.join(extract_dir, "images")):
        print("[OK] Dataset already extracted at: %s" % extract_dir)
        return extract_dir

    print("=" * 60)
    print("  Downloading: %s" % info["name"])
    print("  Description: %s" % info["description"])
    print("  Images:      %d" % info["image_count"])
    print("  Size:        ~%.1f MB" % info["size_mb"])
    print("=" * 60)

    if not os.path.exists(zip_path):
        print("\n[1/3] Downloading...")
        downloaded = False
        for url in info["urls"]:
            try:
                print("      Trying: %s" % url[:80])
                _download_with_progress(url, zip_path)
                downloaded = True
                break
            except Exception as e:
                print("      Failed: %s" % str(e)[:80])
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                continue

        if not downloaded:
            if info.get("ultralytics_key"):
                print("\n[INFO] Trying Ultralytics built-in download...")
                try:
                    from ultralytics import YOLO
                    model = YOLO("yolo11n.pt")
                    print("      Downloading via Ultralytics API (this may take a while)...")
                    result = model.val(data=info["ultralytics_key"], imgsz=32, batch=1, epochs=1)
                    ultralytics_dir = os.path.join(os.path.expanduser("~"), "datasets", "crack-seg")
                    if os.path.exists(ultralytics_dir):
                        print("      Ultralytics download succeeded!")
                        if not os.path.exists(extract_dir):
                            shutil.copytree(ultralytics_dir, extract_dir)
                        print("[2/3] Skipping extraction (already organized by Ultralytics)")
                        _verify_yolo_dataset(extract_dir, info)
                        _create_data_yaml(extract_dir, info)
                        print("\n[DONE] Dataset ready at: %s" % extract_dir)
                        return extract_dir
                except Exception as e:
                    print("      Ultralytics download also failed: %s" % str(e)[:80])

            print("\n[ERROR] All download URLs failed.")
            print("Please download manually from:")
            for url in info["urls"]:
                print("  %s" % url)
            print("Then place the zip file at: %s" % zip_path)
            print("And run this script again.")
            return None
    else:
        try:
            with zipfile.ZipFile(zip_path, "r") as test_zf:
                test_zf.testzip()
            print("\n[1/3] ZIP file already exists, skipping download.")
        except (zipfile.BadZipFile, Exception):
            print("\n[1/3] ZIP file corrupted, re-downloading...")
            os.remove(zip_path)
            for url in info["urls"]:
                try:
                    _download_with_progress(url, zip_path)
                    break
                except Exception:
                    if os.path.exists(zip_path):
                        os.remove(zip_path)

    print("[2/3] Extracting dataset...")
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)
    print("      Extraction complete!")

    print("[3/3] Organizing dataset...")
    if info["format"] == "classification":
        _organize_classification_dataset(extract_dir, info)
    elif info["format"] == "yolo" and not info["pre_split"]:
        _organize_yolo_dataset(extract_dir, info)
    else:
        _verify_yolo_dataset(extract_dir, info)

    _create_data_yaml(extract_dir, info)

    print("\n[DONE] Dataset ready at: %s" % extract_dir)
    print("       data.yaml: %s" % os.path.join(extract_dir, "data.yaml"))
    return extract_dir


def _organize_classification_dataset(extract_dir, info):
    images_dir = os.path.join(extract_dir, "images")
    labels_dir = os.path.join(extract_dir, "labels")

    subdirs = []
    for root, dirs, files in os.walk(extract_dir):
        for d in dirs:
            dpath = os.path.join(root, d)
            img_count = sum(1 for f in os.listdir(dpath) if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")))
            if img_count > 0:
                subdirs.append((d, dpath, img_count))

    if not subdirs:
        print("      No image directories found!")
        return

    all_images = []
    for cls_id, (cls_name, cls_path, _) in enumerate(subdirs):
        for f in os.listdir(cls_path):
            ext = f.lower().rsplit(".", 1)[-1] if "." in f else ""
            if ext in ("jpg", "jpeg", "png", "bmp"):
                src = os.path.join(cls_path, f)
                dst_name = "%s_%s" % (cls_name, f)
                dst = os.path.join(images_dir, dst_name)
                os.makedirs(images_dir, exist_ok=True)
                if not os.path.exists(dst):
                    shutil.copy2(src, dst)

                label_name = os.path.splitext(dst_name)[0] + ".txt"
                label_path = os.path.join(labels_dir, label_name)
                os.makedirs(labels_dir, exist_ok=True)
                if not os.path.exists(label_path):
                    import cv2
                    img = cv2.imread(dst)
                    if img is not None:
                        h, w = img.shape[:2]
                        with open(label_path, "w") as lf:
                            lf.write("%d 0.5 0.5 1.0 1.0\n" % cls_id)

                all_images.append(dst_name)

    _split_images(extract_dir, all_images)
    print("      Organized %d images into YOLO format" % len(all_images))


def _organize_yolo_dataset(extract_dir, info):
    images_dir = os.path.join(extract_dir, "images")
    labels_dir = os.path.join(extract_dir, "labels")

    found_images = []
    found_labels = []

    for root, dirs, files in os.walk(extract_dir):
        for f in files:
            full_path = os.path.join(root, f)
            ext = f.lower().rsplit(".", 1)[-1] if "." in f else ""
            if ext in ("jpg", "jpeg", "png", "bmp"):
                found_images.append(full_path)
            elif ext == "txt" and f != "data.yaml" and f != "classes.txt":
                found_labels.append(full_path)

    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(labels_dir, exist_ok=True)

    all_images = []
    for img_path in found_images:
        fname = os.path.basename(img_path)
        dst = os.path.join(images_dir, fname)
        if os.path.abspath(img_path) != os.path.abspath(dst):
            shutil.copy2(img_path, dst)

        label_name = os.path.splitext(fname)[0] + ".txt"
        label_dst = os.path.join(labels_dir, label_name)

        for lbl_path in found_labels:
            if os.path.splitext(os.path.basename(lbl_path))[0] == os.path.splitext(fname)[0]:
                if os.path.abspath(lbl_path) != os.path.abspath(label_dst):
                    shutil.copy2(lbl_path, label_dst)
                break

        if not os.path.exists(label_dst):
            with open(label_dst, "w") as lf:
                pass

        all_images.append(fname)

    _split_images(extract_dir, all_images)
    print("      Organized %d images into YOLO format" % len(all_images))


def _verify_yolo_dataset(extract_dir, info):
    train_dir = os.path.join(extract_dir, "images", "train")
    val_dir = os.path.join(extract_dir, "images", "val")
    test_dir = os.path.join(extract_dir, "images", "test")

    train_count = len(os.listdir(train_dir)) if os.path.exists(train_dir) else 0
    val_count = len(os.listdir(val_dir)) if os.path.exists(val_dir) else 0
    test_count = len(os.listdir(test_dir)) if os.path.exists(test_dir) else 0

    print("      Train images: %d" % train_count)
    print("      Val images:   %d" % val_count)
    print("      Test images:  %d" % test_count)
    print("      Total:        %d" % (train_count + val_count + test_count))


def _split_images(extract_dir, all_images, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1, seed=42):
    random.seed(seed)
    random.shuffle(all_images)

    total = len(all_images)
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)

    splits = {
        "train": all_images[:train_end],
        "val": all_images[train_end:val_end],
        "test": all_images[val_end:],
    }

    for split_name, files in splits.items():
        split_img_dir = os.path.join(extract_dir, "images", split_name)
        split_lbl_dir = os.path.join(extract_dir, "labels", split_name)
        os.makedirs(split_img_dir, exist_ok=True)
        os.makedirs(split_lbl_dir, exist_ok=True)

        img_src_dir = os.path.join(extract_dir, "images")
        lbl_src_dir = os.path.join(extract_dir, "labels")

        for f in files:
            src_img = os.path.join(img_src_dir, f)
            dst_img = os.path.join(split_img_dir, f)
            if os.path.exists(src_img) and not os.path.exists(dst_img):
                shutil.move(src_img, dst_img)

            label_name = os.path.splitext(f)[0] + ".txt"
            src_lbl = os.path.join(lbl_src_dir, label_name)
            dst_lbl = os.path.join(split_lbl_dir, label_name)
            if os.path.exists(src_lbl) and not os.path.exists(dst_lbl):
                shutil.move(src_lbl, dst_lbl)

    for split_name in splits:
        split_img_dir = os.path.join(extract_dir, "images", split_name)
        count = len(os.listdir(split_img_dir)) if os.path.exists(split_img_dir) else 0
        print("      %s: %d images" % (split_name.capitalize(), count))


def _create_data_yaml(extract_dir, info):
    yaml_path = os.path.join(extract_dir, "data.yaml")
    classes = info.get("classes", {"0": "crack"})

    yaml_content = "path: %s\n" % extract_dir
    yaml_content += "train: images/train\n"
    yaml_content += "val: images/val\n"
    yaml_content += "test: images/test\n\n"
    yaml_content += "nc: %d\n" % len(classes)
    yaml_content += "names:\n"
    for k, v in classes.items():
        yaml_content += "  %s: %s\n" % (k, v)

    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)
    print("      Created data.yaml")


def list_available_datasets():
    print("\nAvailable datasets for download:")
    print("-" * 70)
    for key, info in DATASETS_INFO.items():
        print("  %-25s %s" % ("[%s]" % key, info["name"]))
        print("  %-25s Images: %d | Size: ~%.0f MB | Format: %s" % ("", info["image_count"], info["size_mb"], info["format"]))
        print("  %-25s %s" % ("", info["description"]))
        print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        dataset_key = sys.argv[1]
        if dataset_key == "list":
            list_available_datasets()
        elif dataset_key == "all":
            for key in DATASETS_INFO:
                download_dataset(key)
        else:
            download_dataset(dataset_key)
    else:
        list_available_datasets()
        print("Usage: python download_dataset.py [dataset_key|list|all]")
        print("Default: downloading crack-seg dataset...\n")
        download_dataset("crack-seg")
