"""
Mermaid 图表导出工具 (Playwright 版本)
无需安装 Node.js/npm，直接使用 Python 导出 Mermaid 图表为 PNG/SVG/PDF
"""

import os
import sys
import re
import base64
import asyncio
from pathlib import Path

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


# Mermaid 图表代码定义
MERMAID_CHARTS = {
    "01_技术路线总览": """flowchart TD
    subgraph L1["第一层：多源数据采集与接入"]
        direction LR
        A1["无人机航拍影像<br/>网格化航线·高分辨率"]
        A2["地面移动端影像<br/>智能手机/专业相机"]
        A3["视频流数据<br/>巡检录像/实时监控"]
        A4["批量图像数据<br/>历史档案/定期检测"]
    end

    subgraph L2["第二层：统一预处理管道"]
        B1["格式标准化<br/>PNG/JPG/BMP/TIFF/WebP"]
        B2["尺寸自适应<br/>640x640 / 1280x1280"]
        B3["质量增强<br/>去噪/去雾/对比度增强"]
        B4["元数据提取<br/>EXIF/GPS/时间戳"]
    end

    subgraph L3["第三层：YOLO11 视觉检测引擎"]
        C1["CSPNet骨干网络<br/>多层次特征金字塔"]
        C2["PAN-FPN颈部<br/>多尺度特征融合"]
        C3["解耦检测头<br/>分类+回归+DFL"]
        C4["智能后处理<br/>NMS/SAHI/TTA"]
    end

    subgraph L4["第四层：QwenVL 多模态分析引擎"]
        D1["视觉-语言对齐<br/>检测框+原图+提示词"]
        D2["语义理解推理<br/>裂缝形态+建筑背景"]
        D3["专业知识库<br/>结构工程规范"]
        D4["决策生成模块<br/>评估/归因/建议"]
    end

    subgraph L5["第五层：双模型协同融合"]
        E1["特征级融合<br/>定量数据+定性文本"]
        E2["一致性校验<br/>交叉验证结果可信度"]
        E3["置信度加权<br/>动态调整输出权重"]
        E4["冲突解决机制<br/>规则引擎+专家知识"]
    end

    subgraph L6["第六层：智能报告生成系统"]
        F1["可视化输出<br/>标注图/热力图/分布图"]
        F2["结构化报告<br/>JSON/PDF/Word格式"]
        F3["风险评估矩阵<br/>等级划分+优先级排序"]
        F4["修复方案推荐<br/>工艺+材料/工期"]
    end

    L1 --> L2 --> L3 --> L4 --> L5 --> L6""",

    "02_YOLO11算法流程": """flowchart TD
    subgraph Input["输入层"]
        I1["原始图像<br/>HxWx3"]
    end

    subgraph Backbone["CSPNet 骨干网络"]
        S1["Stem: Conv+BN+SiLU<br/>640x640x3 -> 160x160x32"]
        S2["Stage1: CSPBlockx3<br/>160x160->80x80<br/>通道: 32->64"]
        S3["Stage2: CSPBlockx6<br/>80x80->40x40<br/>通道: 64->128"]
        S4["Stage3: CSPBlockx9<br/>40x40->20x20<br/>通道: 128->256"]
        S5["Stage4: CSPBlockx3<br/>20x20->10x10<br/>通道: 256->512"]
        S6["SPPF空间金字塔<br/>全局上下文特征"]
    end

    subgraph Neck["PAN-FPN 颈部网络"]
        N1["自顶向下路径<br/>FPN特征融合"]
        N2["自底向上路径<br/>PAN特征增强"]
        N3["多尺度输出<br/>P3/P4/P5"]
    end

    subgraph Head["解耦检测头"]
        H1["分类分支<br/>BCE Loss<br/>裂缝类型概率"]
        H2["回归分支<br/>CIoU Loss<br/>边界框坐标"]
        H3["DFL分布焦点<br/>定位精度优化"]
    end

    subgraph Output["输出层"]
        O1["后处理:NMS去重<br/>IOU阈值=0.45"]
        O2["置信度过滤<br/>阈值=0.25"]
        O3["检测结果<br/>bbox+class+conf"]
    end

    I1 --> S1 --> S2 --> S3 --> S4 --> S5 --> S6
    S6 --> N1 --> N2 --> N3
    N3 --> H1 & H2 & H3
    H1 & H2 & H3 --> Output""",

    "03_QwenVL分析流程": """flowchart TD
    subgraph Input_ML["多模态输入构建"]
        M1["原始图像<br/>Base64编码"]
        M2["YOLO检测结果<br/>检测框叠加图"]
        M3["结构化检测数据<br/>JSON格式"]
        M4["专业提示词<br/>工程领域知识"]
    end

    subgraph VLM["视觉语言模型处理"]
        V1["视觉编码器<br/>ViT/Vision Transformer<br/>图像->特征向量"]
        V2["语言编码器<br/>Qwen-LLM<br/>文本->语义表示"]
        V3["跨模态对齐<br/>视觉-语言联合空间"]
        V4["注意力机制<br/>图像区域-文本词对齐"]
    end

    subgraph Reasoning["专业推理引擎"]
        R1["裂缝识别模块<br/>形态学分析"]
        R2["分类判断模块<br/>横向/纵向/斜向/网状"]
        R3["严重程度评估<br/>宽度/长度/深度推断"]
        R4["成因分析模块<br/>沉降/温度/材料/施工"]
        R5["风险评估模块<br/>结构安全影响"]
        R6["修复建议模块<br/>方案/材料/工艺"]
    end

    subgraph Output_ML["结构化输出"]
        P1["JSON格式分析结果"]
        P2["自然语言描述"]
        P3["置信度评分"]
        P4["处理优先级"]
    end

    M1 & M2 & M3 & M4 --> VLM
    VLM --> Reasoning
    Reasoning --> Output_ML""",

    "04_协同工作流程": """sequenceDiagram
    participant U as 用户
    participant API as FastAPI服务
    participant YOLO as YOLO11检测器
    participant QwenVL as QwenVL分析器
    participant Fuse as 融合引擎
    participant Report as 报告生成器

    U->>API: 上传墙体图像
    API->>YOLO: detect(image_path)
    Note over YOLO: 图像预处理<br/>模型推理<br/>后处理优化
    YOLO-->>API: detection_result
    API->>QwenVL: analyze_image(image, detection_result)
    Note over QwenVL: 构建多模态输入<br/>VLM推理<br/>解析JSON结果
    QwenVL-->>API: analysis_result
    API->>Fuse: fuse_results(detection, analysis)
    Note over Fuse: 特征对齐<br/>一致性校验<br/>置信度加权<br/>冲突解决
    Fuse-->>API: fused_result
    API->>Report: generate_report(fused_result)
    Note over Report: 可视化绘制<br/>结构化数据组装<br/>风险评估计算
    Report-->>U: 完整审核报告""",

    "05_融合策略设计": """flowchart TD
    subgraph Data_Input["输入数据"]
        D1["YOLO输出<br/>bbox坐标<br/>类别ID<br/>置信度分数"]
        D2["QwenVL输出<br/>严重程度<br/>成因分析<br/>风险评估"]
    end

    subgraph Alignment["特征对齐模块"]
        A1["空间对齐<br/>检测框<->图像区域"]
        A2["语义对齐<br/>类别名称<->类型描述"]
        A3["数值对齐<br/>置信度<->确定性评分"]
    end

    subgraph Validation["一致性校验模块"]
        V1["类别一致性<br/>YOLO类别 vs VL类型"]
        V2["严重程度一致性<br/>YOLO置信度 vs VL评级"]
        V3["数量一致性<br/>检测数量 vs 描述数量"]
    end

    subgraph Weighting["置信度加权模块"]
        W1["YOLO权重计算<br/>w_yolo = f(conf, iou, area)"]
        W2["QwenVL权重计算<br/>w_vl = g(severity, coherence)"]
        W3["动态权重调整<br/>alpha = w_yolo / (w_yolo + w_vl)"]
    end

    subgraph Conflict["冲突解决模块"]
        C1["规则引擎<br/>基于建筑规范"]
        C2["专家知识库<br/>历史案例匹配"]
        C3["人工审核标记<br/>低置信度预警"]
    end

    subgraph Output_Fuse["融合输出"]
        O1["统一诊断结果<br/>定量+定性综合"]
        O2["置信度元数据<br/>各来源贡献度"]
        O3["质量标识<br/>自动/需审核"]
    end

    D1 & D2 --> Alignment
    Alignment --> Validation
    Validation --> Weighting
    Weighting --> Conflict
    Conflict --> Output_Fuse""",

    "06_系统架构": """flowchart TB
    subgraph Client["客户端层"]
        UI["Web前端界面<br/>HTML/CSS/JavaScript"]
        Mobile["移动端适配<br/>响应式设计"]
    end

    subgraph API["API网关层"]
        Gateway["FastAPI应用<br/>RESTful API"]
        Auth["认证中间件<br/>CORS/异常处理"]
        Upload["文件上传服务<br/>UUID命名/大小限制"]
    end

    subgraph Core["核心业务逻辑层"]
        Detect["检测服务<br/>CrackDetector"]
        Analyze["分析服务<br/>QwenVLAnalyzer"]
        Annotate["标注服务<br/>Annotator"]
        Train["训练服务<br/>Trainer"]
        Eval["评估服务<br/>Evaluator"]
        Report["报告服务<br/>ReportGenerator"]
    end

    subgraph Model["AI模型层"]
        YOLO_Model["YOLO11模型<br/>Ultralytics框架"]
        QwenVL_Model["QwenVL模型<br/>DashScope API"]
        Custom_Model["自定义模型<br/>用户训练权重"]
    end

    subgraph Data["数据存储层"]
        Image_Store["图片存储<br/>static/uploads/"]
        Result_Store["结果存储<br/>static/results/"]
        Report_Store["报告存储<br/>static/reports/"]
        Dataset_Store["数据集存储<br/>datasets/"]
    end

    Client --> API
    API --> Core
    Core --> Model
    Core --> Data""",

    "07_数据流架构": """flowchart LR
    subgraph Ingestion["数据摄入"]
        Upload["文件上传接口"]
        Batch["批量导入"]
        Video["视频流处理"]
        Path["路径直接访问"]
    end

    subgraph Processing["数据处理管道"]
        Preprocess["统一预处理"]
        Queue["任务队列"]
        Worker["异步Worker"]
    end

    subgraph AI_Pipeline["AI处理流水线"]
        Step1["Step1: YOLO检测"]
        Step2["Step2: QwenVL分析"]
        Step3["Step3: 结果融合"]
        Step4["Step4: 报告生成"]
    end

    subgraph Storage["持久化存储"]
        DB_Image["图像数据库"]
        DB_Result["结果数据库"]
        DB_Report["报告数据库"]
    end

    subgraph Output["输出服务"]
        API_Response["API响应"]
        Web_Display["Web展示"]
        Export["导出下载"]
    end

    Ingestion --> Processing
    Processing --> AI_Pipeline
    AI_Pipeline --> Storage
    Storage --> Output""",

    "08_质量控制流程": """flowchart TD
    A[原始数据采集] --> B{数据质量检查}
    B -->|合格| C[进入数据集]
    B -->|不合格| D[数据清洗]
    D --> E{二次检查}
    E -->|合格| C
    E -->|不合格| F[人工审核]
    F --> G{是否可用}
    G -->|是| C
    G -->|否| H[丢弃/重新采集]

    C --> I[标注质量审核]
    I --> J[训练/验证/测试分割]
    J --> K[data.yaml生成]""",

    "09_测试覆盖分布": """pie title 测试类型分布
    "单元测试" : 30
    "集成测试" : 25
    "系统测试" : 20
    "性能测试" : 15
    "用户验收测试" : 10""",
}


# HTML 模板（包含 Mermaid.js 库）
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Mermaid Chart</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
    <style>
        body {
            margin: 0;
            padding: 20px;
            background-color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .mermaid {
            max-width: {width}px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
    </style>
</head>
<body>
    <div class="mermaid">
{code}
    </div>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            themeVariables: {{
                fontSize: '18px',
                fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            }},
            securityLevel: 'loose'
        }});
    </script>
</body>
</html>
"""


def check_playwright():
    """检查 playwright 是否已安装"""
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        return False


def install_playwright():
    """安装 playwright 及浏览器"""
    print("正在安装 playwright...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        print("安装成功！")
        return True
    except Exception as e:
        print(f"安装失败: {e}")
        return False


def export_chart_with_playwright(chart_name: str, chart_code: str, output_dir: str, format: str = "png"):
    """
    使用 Playwright 导出单个图表

    Args:
        chart_name: 图表名称
        chart_code: Mermaid 代码
        output_dir: 输出目录
        format: 输出格式 (png/svg/pdf)
    """
    from playwright.sync_api import sync_playwright

    # 构建 HTML 内容
    html_content = HTML_TEMPLATE.format(
        code=chart_code,
        width=2400 if format == 'png' else 1200
    )

    # 构建输出文件名
    safe_name = re.sub(r'[^\w\u4e00-\u9fff-]', '_', chart_name)
    output_file = os.path.join(output_dir, f"{safe_name}.{format}")

    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 2400, "height": 1800})

        # 设置内容
        page.set_content(html_content)

        # 等待渲染完成
        page.wait_for_selector('.mermaid', timeout=10000)
        page.wait_for_timeout(2000)  # 额外等待确保完全渲染

        # 根据格式导出
        try:
            if format == 'png':
                # 获取图表元素并截图
                element = page.query_selector('.mermaid')
                if element:
                    element.screenshot(path=output_file)
                else:
                    page.screenshot(path=output_file, full_page=True)

            elif format == 'svg':
                # 获取 SVG 内容
                svg_element = page.query_selector('svg')
                if svg_element:
                    svg_content = svg_element.evaluate('el => el.outerHTML')
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(svg_content)
                else:
                    raise Exception("未找到 SVG 元素")

            elif format == 'pdf':
                page.pdf(
                    path=output_file,
                    format='A4',
                    landscape=True,
                    margin={'top': '20px', 'right': '20px', 'bottom': '20px', 'left': '20px'}
                )

            else:
                raise ValueError(f"不支持的格式: {format}")

            # 检查文件是否生成
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file) / 1024
                print(f"  [OK] {chart_name}.{format} ({file_size:.1f} KB)")
                return True
            else:
                print(f"  [FAIL] {chart_name} - 文件未生成")
                return False

        finally:
            browser.close()


def export_all_charts(output_dir: str = None, format: str = "png"):
    """
    导出所有图表

    Args:
        output_dir: 输出目录
        format: 输出格式 (png/svg/pdf)
    """
    import subprocess

    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "images")

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 60)
    print("  Mermaid Chart Export Tool (Playwright Edition)")
    print("=" * 60)
    print(f"  Output Dir: {output_dir}")
    print(f"  Format: {format.upper()}")
    print(f"  Charts: {len(MERMAID_CHARTS)}")
    print("=" * 60 + "\n")

    # 检查 playwright
    if not check_playwright():
        print("[!] Playwright not found, installing...")
        if not install_playwright():
            print("\n[!] Manual installation:")
            print("    pip install playwright")
            print("    playwright install chromium")
            print("\n[!] Alternative: Use online tool https://mermaid.live")
            return

    # 导出每个图表
    success_count = 0
    fail_count = 0

    for i, (name, code) in enumerate(MERMAID_CHARTS.items(), 1):
        print(f"[{i}/{len(MERMAID_CHARTS)}] Exporting: {name}")
        try:
            if export_chart_with_playwright(name, code, output_dir, format):
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"  [ERROR] {name}: {str(e)[:100]}")
            fail_count += 1

    # 输出统计
    print("\n" + "=" * 60)
    print(f"  Export Complete!")
    print(f"    Success: {success_count} charts")
    print(f"    Failed:  {fail_count} charts")
    print(f"  Location: {os.path.abspath(output_dir)}")
    print("=" * 60 + "\n")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Export Mermaid charts to images using Playwright"
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output directory (default: ./images)"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["png", "svg", "pdf"],
        default="png",
        help="Output format (default: png)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available charts"
    )

    args = parser.parse_args()

    if args.list:
        print("\nAvailable Charts:\n")
        for i, name in enumerate(MERMAID_CHARTS.keys(), 1):
            print(f"  {i:2d}. {name}")
        print()
        return

    export_all_charts(args.output, args.format)


if __name__ == "__main__":
    main()
