import os
import json
import shutil
import uuid
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")
CRACK_SEG_DIR = os.path.join(DATASETS_DIR, "crack-seg")


def import_crack_seg():
    if not os.path.exists(CRACK_SEG_DIR):
        print("[ERROR] crack-seg dataset not found at: %s" % CRACK_SEG_DIR)
        print("Please run: python download_dataset.py crack-seg")
        return

    dataset_id = str(uuid.uuid4())[:8]
    dataset_path = os.path.join(DATASETS_DIR, dataset_id)

    os.makedirs(os.path.join(dataset_path, "images"), exist_ok=True)
    os.makedirs(os.path.join(dataset_path, "labels"), exist_ok=True)

    meta = {
        "dataset_id": dataset_id,
        "name": "Crack Segmentation 示例数据集",
        "description": "Ultralytics官方裂缝分割数据集，包含4029张道路和墙壁裂缝图片，已预分割为训练/验证/测试集",
        "classes": {"0": "crack"},
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "image_count": 0,
        "annotated_count": 0,
        "split_info": None,
    }

    total_images = 0
    total_annotated = 0

    for split in ["train", "val", "test"]:
        src_img_dir = os.path.join(CRACK_SEG_DIR, "images", split)
        src_lbl_dir = os.path.join(CRACK_SEG_DIR, "labels", split)

        if not os.path.exists(src_img_dir):
            print("[WARN] %s images dir not found, skipping" % split)
            continue

        dst_img_dir = os.path.join(dataset_path, "images", split)
        dst_lbl_dir = os.path.join(dataset_path, "labels", split)
        os.makedirs(dst_img_dir, exist_ok=True)
        os.makedirs(dst_lbl_dir, exist_ok=True)

        img_count = 0
        for f in os.listdir(src_img_dir):
            ext = f.lower().rsplit(".", 1)[-1] if "." in f else ""
            if ext not in ("jpg", "jpeg", "png", "bmp"):
                continue

            src_img = os.path.join(src_img_dir, f)
            dst_img = os.path.join(dst_img_dir, f)
            if not os.path.exists(dst_img):
                shutil.copy2(src_img, dst_img)

            label_name = os.path.splitext(f)[0] + ".txt"
            src_lbl = os.path.join(src_lbl_dir, label_name)
            dst_lbl = os.path.join(dst_lbl_dir, label_name)

            if os.path.exists(src_lbl):
                if not os.path.exists(dst_lbl):
                    shutil.copy2(src_lbl, dst_lbl)
                with open(src_lbl, "r") as lf:
                    if lf.read().strip():
                        total_annotated += 1
            else:
                if not os.path.exists(dst_lbl):
                    with open(dst_lbl, "w") as lf:
                        pass

            img_count += 1
            total_images += 1

        print("  %s: %d images copied" % (split, img_count))

    meta["image_count"] = total_images
    meta["annotated_count"] = total_annotated
    meta["split_info"] = {
        "dataset_id": dataset_id,
        "total": total_images,
        "train": len(os.listdir(os.path.join(dataset_path, "images", "train"))) if os.path.exists(os.path.join(dataset_path, "images", "train")) else 0,
        "val": len(os.listdir(os.path.join(dataset_path, "images", "val"))) if os.path.exists(os.path.join(dataset_path, "images", "val")) else 0,
        "test": len(os.listdir(os.path.join(dataset_path, "images", "test"))) if os.path.exists(os.path.join(dataset_path, "images", "test")) else 0,
        "ratios": {"train": 0.7, "val": 0.2, "test": 0.1},
        "yaml_path": os.path.join(dataset_path, "data.yaml"),
    }

    yaml_content = "path: %s\n" % dataset_path
    yaml_content += "train: images/train\n"
    yaml_content += "val: images/val\n"
    yaml_content += "test: images/test\n\n"
    yaml_content += "nc: 1\n"
    yaml_content += "names:\n  0: crack\n"
    with open(os.path.join(dataset_path, "data.yaml"), "w", encoding="utf-8") as f:
        f.write(yaml_content)

    with open(os.path.join(dataset_path, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print("\n[DONE] Dataset imported successfully!")
    print("  Dataset ID:   %s" % dataset_id)
    print("  Name:         %s" % meta["name"])
    print("  Total images: %d" % total_images)
    print("  Annotated:    %d" % total_annotated)
    print("  Path:         %s" % dataset_path)
    print("  data.yaml:    %s" % os.path.join(dataset_path, "data.yaml"))
    return dataset_id


if __name__ == "__main__":
    import_crack_seg()
