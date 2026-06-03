import requests
import json
import time
import os

BASE = "http://localhost:8000"

def step1_test_annotation():
    print("=" * 60)
    print("  STEP 1: 标注模块测试")
    print("=" * 60)

    print("\n[1.1] 获取数据集列表...")
    r = requests.get(f"{BASE}/api/datasets")
    datasets = r.json().get("datasets", [])
    crack_ds = None
    for ds in datasets:
        if "Crack" in ds.get("name", ""):
            crack_ds = ds
            break

    if not crack_ds:
        print("  [ERROR] Crack Segmentation 数据集未找到，请先运行: python import_crack_seg.py")
        return None

    ds_id = crack_ds["dataset_id"]
    print(f"  找到数据集: {crack_ds['name']} (ID: {ds_id})")
    print(f"  图片数: {crack_ds['image_count']}, 已标注: {crack_ds['annotated_count']}")

    print("\n[1.2] 获取图片列表...")
    r = requests.get(f"{BASE}/api/datasets/{ds_id}/images?page=1&page_size=3")
    img_data = r.json()
    print(f"  总图片数: {img_data['total']}")
    images = img_data["images"]
    for img in images[:3]:
        print(f"    {img['filename']}  annotated={img['has_annotation']}  count={img['annotation_count']}")

    if not images:
        print("  [ERROR] 没有图片")
        return None

    fname = images[0]["filename"]
    print(f"\n[1.3] 获取图片标注: {fname}")
    r = requests.get(f"{BASE}/api/datasets/{ds_id}/images/{fname}/annotations")
    if r.status_code != 200:
        print(f"  [ERROR] 获取标注失败: {r.status_code} {r.text[:200]}")
        return None
    ann = r.json()
    print(f"  标注数: {len(ann['annotations'])}")
    if ann["annotations"]:
        a = ann["annotations"][0]
        print(f"  第一个标注: class={a['class_name']} cx={a['cx']:.4f} cy={a['cy']:.4f} w={a['w']:.4f} h={a['h']:.4f}")

    print(f"\n[1.4] 保存标注...")
    test_annotations = [
        {"class_id": 0, "class_name": "crack", "cx": 0.5, "cy": 0.5, "w": 0.3, "h": 0.1},
        {"class_id": 0, "class_name": "crack", "cx": 0.2, "cy": 0.8, "w": 0.15, "h": 0.05},
    ]
    r = requests.post(
        f"{BASE}/api/datasets/{ds_id}/images/{fname}/annotations",
        json={"annotations": test_annotations},
    )
    if r.status_code != 200:
        print(f"  [ERROR] 保存标注失败: {r.status_code} {r.text[:200]}")
        return None
    print(f"  保存成功: {r.json()}")

    print(f"\n[1.5] 验证保存结果...")
    r = requests.get(f"{BASE}/api/datasets/{ds_id}/images/{fname}/annotations")
    ann = r.json()
    print(f"  标注数: {len(ann['annotations'])}")
    for a in ann["annotations"]:
        print(f"    class={a['class_name']} cx={a['cx']:.4f} cy={a['cy']:.4f}")

    original_annotations = ann["annotations"]
    r = requests.post(
        f"{BASE}/api/datasets/{ds_id}/images/{fname}/annotations",
        json={"annotations": original_annotations},
    )
    print(f"  恢复原始标注: {'OK' if r.status_code == 200 else 'FAIL'}")

    print("\n[1.6] 检查数据集分割状态...")
    r = requests.get(f"{BASE}/api/datasets/{ds_id}")
    ds_info = r.json()
    split_info = ds_info.get("split_info")
    if split_info:
        print(f"  已分割: train={split_info['train']} val={split_info['val']} test={split_info['test']}")
        print(f"  data.yaml: {split_info.get('yaml_path', 'N/A')}")
    else:
        print("  未分割，需要执行分割...")

    return ds_id


def step2_test_training(ds_id):
    print("\n" + "=" * 60)
    print("  STEP 2: 训练模块测试")
    print("=" * 60)

    print(f"\n[2.1] 启动训练 (数据集: {ds_id})...")
    print("  配置: epochs=3, batch=4, imgsz=320, patience=10")
    print("  (使用最小参数进行快速测试)")

    fd = {
        "dataset_id": ds_id,
        "model": "yolo11n.pt",
        "epochs": "3",
        "batch_size": "4",
        "imgsz": "320",
        "patience": "10",
        "lr0": "0.01",
        "lrf": "0.01",
        "momentum": "0.937",
        "weight_decay": "0.0005",
        "warmup_epochs": "1",
        "box": "7.5",
        "cls": "0.5",
        "dfl": "1.5",
    }

    r = requests.post(f"{BASE}/api/train/start", data=fd)
    if r.status_code != 200:
        print(f"  [ERROR] 启动训练失败: {r.status_code} {r.text[:300]}")
        return None

    train_info = r.json()
    training = train_info.get("training", {})
    training_id = training.get("training_id")
    print(f"  训练已启动! ID: {training_id}")
    print(f"  状态: {training.get('status')}")

    print(f"\n[2.2] 监控训练进度...")
    max_wait = 600
    start_time = time.time()
    last_status = None

    while time.time() - start_time < max_wait:
        r = requests.get(f"{BASE}/api/train/status/{training_id}")
        if r.status_code != 200:
            print(f"  获取状态失败: {r.status_code}")
            time.sleep(10)
            continue

        status_data = r.json()
        status = status_data.get("status")

        if status != last_status:
            elapsed = int(time.time() - start_time)
            print(f"  [{elapsed}s] 状态: {status}")
            last_status = status

        if status == "completed":
            results = status_data.get("results", {})
            best_weight = results.get("best_weight")
            metrics = results.get("metrics", {})
            last_epoch = metrics.get("last_epoch", {})
            print(f"\n  训练完成!")
            print(f"  最佳权重: {best_weight}")
            print(f"  权重文件存在: {os.path.exists(best_weight) if best_weight else False}")
            if last_epoch:
                for k in ["metrics/mAP50(B)", "metrics/mAP50-95(B)", "metrics/precision(B)", "metrics/recall(B)"]:
                    if k in last_epoch:
                        print(f"  {k}: {last_epoch[k]}")
            return training_id

        elif status == "failed":
            error = status_data.get("error", "Unknown error")
            print(f"\n  训练失败: {error[:300]}")
            return None

        r2 = requests.get(f"{BASE}/api/train/progress/{training_id}")
        if r2.status_code == 200:
            progress = r2.json()
            epochs_done = progress.get("epochs_completed", 0)
            total_epochs = progress.get("total_epochs", 0)
            if total_epochs > 0:
                elapsed = int(time.time() - start_time)
                print(f"  [{elapsed}s] Epoch: {epochs_done}/{total_epochs}")

        time.sleep(15)

    print(f"\n  训练超时 ({max_wait}s)")
    return training_id


def step3_test_evaluation(training_id):
    print("\n" + "=" * 60)
    print("  STEP 3: 评估模块测试")
    print("=" * 60)

    if not training_id:
        print("  [SKIP] 没有训练结果，跳过评估")
        return

    r = requests.get(f"{BASE}/api/train/status/{training_id}")
    train_data = r.json()
    best_weight = train_data.get("results", {}).get("best_weight")
    ds_id = train_data.get("dataset_id")

    if not best_weight or not os.path.exists(best_weight):
        print(f"  [ERROR] 权重文件不存在: {best_weight}")
        return

    print(f"\n[3.1] 启动评估...")
    print(f"  模型: {best_weight}")
    print(f"  数据集: {ds_id}")

    fd = {
        "model_path": best_weight,
        "dataset_id": ds_id,
        "conf": "0.25",
        "iou": "0.45",
        "imgsz": "320",
        "batch_size": "4",
        "split": "val",
    }

    r = requests.post(f"{BASE}/api/eval/start", data=fd)
    if r.status_code != 200:
        print(f"  [ERROR] 启动评估失败: {r.status_code} {r.text[:300]}")
        return

    eval_data = r.json().get("evaluation", {})
    eval_id = eval_data.get("eval_id")
    print(f"  评估已启动! ID: {eval_id}")

    print(f"\n[3.2] 等待评估完成...")
    max_wait = 300
    start_time = time.time()

    while time.time() - start_time < max_wait:
        r = requests.get(f"{BASE}/api/eval/{eval_id}")
        status = r.json().get("status")

        if status == "completed":
            results = r.json().get("results", {})
            metrics = results.get("metrics", {})
            print(f"\n  评估完成!")
            print(f"  mAP50:     {metrics.get('mAP50', 'N/A')}")
            print(f"  mAP50-95:  {metrics.get('mAP50-95', 'N/A')}")
            print(f"  Precision: {metrics.get('precision', 'N/A')}")
            print(f"  Recall:    {metrics.get('recall', 'N/A')}")
            print(f"  F1:        {metrics.get('f1', 'N/A')}")

            per_class = results.get("per_class_metrics", [])
            if per_class:
                print(f"\n  各类别指标:")
                for pc in per_class:
                    print(f"    Class {pc.get('class_id', '?')}: mAP50={pc.get('mAP50', 'N/A')} mAP50-95={pc.get('mAP50-95', 'N/A')} P={pc.get('precision', 'N/A')} R={pc.get('recall', 'N/A')}")

            return best_weight

        elif status == "failed":
            error = r.json().get("error", "Unknown")
            print(f"\n  评估失败: {error[:300]}")
            return None

        elapsed = int(time.time() - start_time)
        print(f"  [{elapsed}s] 状态: {status}")
        time.sleep(10)

    print(f"\n  评估超时")
    return best_weight


def step4_test_detection_with_custom_model(best_weight):
    print("\n" + "=" * 60)
    print("  STEP 4: 使用微调模型进行检测")
    print("=" * 60)

    if not best_weight or not os.path.exists(best_weight):
        print("  [SKIP] 没有可用的微调模型")
        return

    print(f"\n[4.1] 使用微调模型检测: {best_weight}")

    from models.detector import CrackDetector
    detector = CrackDetector(model_path=best_weight)

    test_imgs = []
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
    if os.path.exists(upload_dir):
        for f in os.listdir(upload_dir):
            ext = f.lower().rsplit(".", 1)[-1] if "." in f else ""
            if ext in ("jpg", "jpeg", "png", "bmp"):
                test_imgs.append(os.path.join(upload_dir, f))
                if len(test_imgs) >= 2:
                    break

    if not test_imgs:
        print("  [WARN] 没有测试图片")
        return

    for img_path in test_imgs:
        print(f"\n  检测: {os.path.basename(img_path)}")
        result = detector.detect(img_path, conf_threshold=0.25, iou_threshold=0.45)
        print(f"  检测到 {result['total_count']} 个目标")
        for d in result.get("detections", [])[:3]:
            print(f"    {d['class_name']} conf={d['confidence']:.3f} bbox=({d['bbox']['x1']:.0f},{d['bbox']['y1']:.0f},{d['bbox']['x2']:.0f},{d['bbox']['y2']:.0f})")

    print("\n[4.2] 通过 API 使用微调模型检测...")
    print("  在首页的检测参数区域，可以手动修改模型路径为微调后的权重文件")
    print(f"  微调模型路径: {best_weight}")
    print("  或者将 best.pt 复制到 weights/ 目录覆盖默认模型")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  墙体裂缝检测系统 - 闭环测试")
    print("  标注 → 训练 → 评估 → 使用微调模型检测")
    print("=" * 60)

    ds_id = step1_test_annotation()
    if ds_id:
        training_id = step2_test_training(ds_id)
        best_weight = step3_test_evaluation(training_id)
        step4_test_detection_with_custom_model(best_weight)

    print("\n" + "=" * 60)
    print("  闭环测试完成!")
    print("=" * 60)
