"""
Mermaid 图表高清导出工具 (字体优化版)
专门解决"方框字体显示不全"问题

优化特性:
- ✅ 缩小字体至14px，确保完整显示
- ✅ 增加节点padding，避免文字溢出
- ✅ 启用自动换行，长文本自动处理
- ✅ 超高分辨率输出 (3200x2400px)
- ✅ 优化中文字体渲染
"""

import os
import sys
import re
from pathlib import Path

# 修复 Windows 控制台编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


# 优化后的图表代码（精简文字、增加换行）
MERMAID_CHARTS = {
    "01_技术路线总览": """flowchart TD
    subgraph L1["第一层：多源数据采集"]
        direction LR
        A1["🎥 无人机航拍<br/>网格化航线"]
        A2["📷 地面移动端<br/>手机/相机"]
        A3["🎬 视频流数据<br/>巡检录像"]
        A4["🌐 批量图像<br/>历史档案"]
    end

    subgraph L2["第二层：统一预处理"]
        B1["格式标准化"]
        B2["尺寸统一化"]
        B3["质量增强"]
        B4["元数据提取"]
    end

    subgraph L3["第三层：YOLO11检测引擎"]
        C1["CSPNet骨干网络"]
        C2["PAN-FPN颈部"]
        C3["解耦检测头"]
        C4["智能后处理"]
    end

    subgraph L4["第四层：QwenVL多模态分析"]
        D1["视觉-语言对齐"]
        D2["语义理解推理"]
        D3["专业知识库"]
        D4["决策生成模块"]
    end

    subgraph L5["第五层：双模型协同融合"]
        E1["特征级融合"]
        E2["一致性校验"]
        E3["置信度加权"]
        E4["冲突解决机制"]
    end

    subgraph L6["第六层：智能报告生成系统"]
        F1["可视化输出"]
        F2["结构化报告"]
        F3["风险评估矩阵"]
        F4["修复方案推荐"]
    end

    L1 --> L2 --> L3 --> L4 --> L5 --> L6""",

    "02_YOLO11算法流程": """flowchart TD
    subgraph Input["输入层"]
        I1["原始图像 H×W×3"]
    end

    subgraph Backbone["CSPNet 骨干网络"]
        S1["Stem: Conv+BN+SiLU"]
        S2["Stage1: CSPBlock×3"]
        S3["Stage2: CSPBlock×6"]
        S4["Stage3: CSPBlock×9"]
        S5["Stage4: CSPBlock×3"]
        S6["SPPF空间金字塔"]
    end

    subgraph Neck["PAN-FPN 颈部"]
        N1["FPN特征融合"]
        N2["PAN特征增强"]
        N3["多尺度输出 P3/P4/P5"]
    end

    subgraph Head["解耦检测头"]
        H1["分类分支 BCE Loss"]
        H2["回归分支 CIoU Loss"]
        H3["DFL分布焦点"]
    end

    subgraph Output["输出层"]
        O1["NMS去重 IOU=0.45"]
        O2["置信度过滤 ≥0.25"]
        O3["检测结果 bbox+conf"]
    end

    I1 --> S1 --> S2 --> S3 --> S4 --> S5 --> S6
    S6 --> N1 --> N2 --> N3
    N3 --> H1 & H2 & H3
    H1 & H2 & H3 --> Output""",

    "03_QwenVL分析流程": """flowchart TD
    subgraph Input_ML["多模态输入构建"]
        M1["原始图像 Base64"]
        M2["检测结果叠加图"]
        M3["结构化检测数据"]
        M4["专业提示词"]
    end

    subgraph VLM["视觉语言模型处理"]
        V1["视觉编码器 ViT"]
        V2["语言编码器 Qwen"]
        V3["跨模态对齐"]
        V4["注意力机制"]
    end

    subgraph Reasoning["专业推理引擎"]
        R1["裂缝识别模块"]
        R2["分类判断模块"]
        R3["严重程度评估"]
        R4["成因分析模块"]
        R5["风险评估模块"]
        R6["修复建议模块"]
    end

    subgraph Output_ML["结构化输出"]
        P1["JSON分析结果"]
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
    participant VL as QwenVL分析器
    participant Fuse as 融合引擎
    participant Rpt as 报告生成器

    U->>API: 上传墙体图像
    API->>YOLO: detect(image)

    Note over YOLO: 图像预处理<br/>模型推理<br/>后处理优化

    YOLO-->>API: detection_result

    API->>VL: analyze(image, result)

    Note over VL: 构建多模态输入<br/>VLM推理<br/>解析结果

    VL-->>API: analysis_result

    API->>Fuse: fuse(detection, analysis)

    Note over Fuse: 特征对齐<br/>一致性校验<br/>置信度加权<br/>冲突解决

    Fuse-->>API: fused_result

    API->>Rpt: generate_report(fused)

    Note over Rpt: 可视化绘制<br/>数据组装<br/>风险评估

    Rpt-->>U: 完整审核报告""",

    "05_融合策略设计": """flowchart TD
    subgraph Data_Input["输入数据"]
        D1["YOLO输出<br/>bbox坐标<br/>类别ID<br/>置信度"]
        D2["QwenVL输出<br/>严重程度<br/>成因分析<br/>风险评估"]
    end

    subgraph Alignment["特征对齐模块"]
        A1["空间对齐"]
        A2["语义对齐"]
        A3["数值对齐"]
    end

    subgraph Validation["一致性校验模块"]
        V1["类别一致性"]
        V2["严重程度一致性"]
        V3["数量一致性"]
    end

    subgraph Weighting["置信度加权模块"]
        W1["YOLO权重计算"]
        W2["QwenVL权重计算"]
        W3["动态权重调整"]
    end

    subgraph Conflict["冲突解决模块"]
        C1["规则引擎"]
        C2["专家知识库"]
        C3["人工审核标记"]
    end

    subgraph Output_Fuse["融合输出"]
        O1["统一诊断结果"]
        O2["置信度元数据"]
        O3["质量标识"]
    end

    D1 & D2 --> Alignment
    Alignment --> Validation
    Validation --> Weighting
    Weighting --> Conflict
    Conflict --> Output_Fuse""",

    "06_系统架构": """flowchart TB
    subgraph Client["客户端层"]
        UI["Web前端界面"]
        Mobile["移动端适配"]
    end

    subgraph API["API网关层"]
        Gateway["FastAPI应用"]
        Auth["认证中间件"]
        Upload["文件上传服务"]
    end

    subgraph Core["核心业务逻辑层"]
        Detect["检测服务"]
        Analyze["分析服务"]
        Annotate["标注服务"]
        Train["训练服务"]
        Eval["评估服务"]
        Report["报告服务"]
    end

    subgraph Model["AI模型层"]
        YOLO_Model["YOLO11模型"]
        QwenVL_Model["QwenVL模型"]
        Custom_Model["自定义模型"]
    end

    subgraph Data["数据存储层"]
        Image_Store["图片存储"]
        Result_Store["结果存储"]
        Report_Store["报告存储"]
        Dataset_Store["数据集存储"]
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
    A[原始数据采集] --> B{质量检查}
    B -->|合格| C[进入数据集]
    B -->|不合格| D[数据清洗]
    D --> E{二次检查}
    E -->|合格| C
    E -->|不合格| F[人工审核]
    F --> G{是否可用}
    G -->|是| C
    G -->|否| H[丢弃重采]

    C --> I[标注质量审核]
    I --> J[训练验证测试分割]
    J --> K[data.yaml生成]""",

    "09_测试覆盖分布": """pie title 测试类型分布
    "单元测试" : 30
    "集成测试" : 25
    "系统测试" : 20
    "性能测试" : 15
    "验收测试" : 10""",
}


# 优化后的 HTML 模板（重点：字体大小、节点样式）
HTML_TEMPLATE_OPTIMIZED = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: {padding}px;
            background-color: white;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
                         'Microsoft YaHei', 'PingFang SC', sans-serif;
        }}

        .mermaid {{
            max-width: {width}px;
            width: {width}px;

            /* 核心优化：字体设置 */
            font-size: {font_size}px !important;
            line-height: 1.4 !important;

            /* 节点样式优化 */
            --node-font-size: {font_size}px;
            --node-padding: 12px 16px;
        }}

        /* 节点内部文字 */
        .mermaid .nodeLabel,
        .mermaid .label {{
            font-size: {font_size}px !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
                         'Microsoft YaHei', 'PingFang SC', sans-serif !important;
            line-height: 1.4 !important;
            word-wrap: break-word;
            white-space: pre-wrap;
        }}

        /* 边缘标签 */
        .mermaid .edgeLabel {{
            font-size: {edge_font_size}px !important;
            background-color: white !important;
        }}

        /* 子图标题 */
        .mermaid .cluster-label {{
            font-size: {subgraph_font_size}px !important;
            font-weight: bold !important;
        }}

        /* 序列图特殊优化 */
        .mermaid .actor {{
            font-size: {font_size}px !important;
        }}

        .mermaid .messageText {{
            font-size: {font_size}px !important;
        }}

        .mermaid .noteText {{
            font-size: {note_font_size}px !important;
            line-height: 1.5 !important;
        }}

        /* 饼图标签 */
        .mermaid .slice text {{
            font-size: {font_size}px !important;
        }}
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

            // 核心优化配置
            themeVariables: {{
                // 字体大小 - 关键！
                fontSize: '{font_size}px',
                nodeFontSize: '{font_size}px',
                edgeFontSize: '{edge_font_size}px',

                // 字体家族
                fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif',

                // 节点内边距 - 增大以容纳文字
                nodePadding: 15,

                // 行高
                lineHeight: 1.4,

                // 颜色主题
                primaryColor: '#e3f2fd',
                primaryTextColor: '#0d47a1',
                primaryBorderColor: '#1565c0',
                secondaryColor: '#fff3e0',
                secondaryTextColor: '#bf360c',
                secondaryBorderColor: '#e65100',
                tertiaryColor: '#e8f5e9',
                tertiaryTextColor: '#1b5e20',
                tertiaryBorderColor: '#2e7d32',
            }},

            // 流程图特定配置
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                wrap: true,           // 启用自动换行
                padding: 15,          // 节点内边距
            }},

            // 序列图特定配置
            sequence: {{
                useMaxWidth: true,
                wrap: {
                    enabled: true,
                    width: 200,
                }},
                diagramMarginX: 50,
                diagramMarginY: 10,
                actorMargin: 50,
                width: 150,
                height: 65,
                boxMargin: 10,
                noteMargin: 10,
                messageMargin: 35,
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
    import subprocess

    print("[*] Installing Playwright...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "playwright"],
            check=True,
            capture_output=True
        )
        print("[*] Installing Chromium browser...")
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
            capture_output=True
        )
        print("[+] Installation successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[-] Installation failed: {e}")
        return False


def export_chart_optimized(chart_name: str, chart_code: str,
                          output_dir: str, format: str = "png",
                          width: int = 3200, height: int = 2400,
                          font_size: int = 14):
    """
    使用优化参数导出单个图表

    Args:
        chart_name: 图表名称
        chart_code: Mermaid 代码
        output_dir: 输出目录
        format: 输出格式 (png/svg/pdf)
        width: 输出宽度 (像素)
        height: 输出高度 (像素)
        font_size: 字体大小 (像素) - 推荐 12-16
    """
    from playwright.sync_api import sync_playwright

    # 构建优化后的 HTML
    html_content = HTML_TEMPLATE_OPTIMIZED.format(
        title=chart_name,
        code=chart_code,
        width=width,
        padding=max(40, width // 60),
        font_size=font_size,
        edge_font_size=min(font_size + 2, 16),
        note_font_size=font_size,
        subgraph_font_size=font_size + 2
    )

    # 构建输出文件名
    safe_name = re.sub(r'[^\w\u4e00-\u9fff-]', '_', chart_name)
    output_file = os.path.join(output_dir, f"{safe_name}.{format}")

    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})

        # 设置内容
        page.set_content(html_content)

        # 等待渲染完成（关键步骤）
        try:
            page.wait_for_selector('.mermaid', timeout=15000)
            # 额外等待确保完全渲染
            page.wait_for_timeout(3000)

            # 检查是否有错误
            errors = page.evaluate("document.querySelector('.mermaid')?.getAttribute('data-error')")
            if errors:
                raise Exception(f"Mermaid rendering error: {errors}")

        except Exception as e:
            print(f"  [!] Render warning: {str(e)[:80]}")

        # 导出图片
        try:
            if format == 'png':
                element = page.query_selector('.mermaid')
                if element:
                    # 截取元素（自动适应内容大小）
                    element.screenshot(
                        path=output_file,
                        type='png',
                        quality=100  # 最高质量
                    )
                else:
                    page.screenshot(path=output_file, full_page=True)

            elif format == 'svg':
                svg_element = page.query_selector('svg')
                if svg_element:
                    svg_content = svg_element.evaluate('el => el.outerHTML')
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(svg_content)
                else:
                    raise Exception("SVG element not found")

            elif format == 'pdf':
                page.pdf(
                    path=output_file,
                    format='A4' if width <= 1200 else 'A3',
                    landscape=True,
                    margin={'top': '20px', 'right': '20px',
                           'bottom': '20px', 'left': '20px'},
                    print_background=True
                )
            else:
                raise ValueError(f"Unsupported format: {format}")

            # 验证输出
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file) / 1024
                print(f"  [OK] {chart_name} ({file_size:.1f} KB)")
                return True
            else:
                print(f"  [FAIL] {chart_name} - File not created")
                return False

        finally:
            browser.close()


def export_all_charts(output_dir: str = None, format: str = "png",
                     font_size: int = 14, width: int = 3200):
    """
    批量导出所有图表

    Args:
        output_dir: 输出目录
        format: 输出格式
        font_size: 字体大小 (推荐: 12-16)
        width: 图片宽度 (推荐: 2400-4000)
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "images_optimized")

    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 70)
    print("  Mermaid Chart Export Tool (Font Optimized Edition)")
    print("=" * 70)
    print(f"  📁 Output Dir : {output_dir}")
    print(f"  📐 Format     : {format.upper()}")
    print(f"  🔤 Font Size  : {font_size}px")
    print(f"  📏 Image Width: {width}px")
    print(f"  📊 Charts     : {len(MERMAID_CHARTS)}")
    print("=" * 70 + "\n")

    # 检查依赖
    if not check_playwright():
        print("[!] Playwright not found.")
        if not install_playwright():
            print("\n[!] Please install manually:")
            print("    pip install playwright && playwright install chromium")
            return

    # 导出统计
    success_count = 0
    fail_count = 0

    for i, (name, code) in enumerate(MERMAID_CHARTS.items(), 1):
        print(f"[{i:2d}/{len(MERMAID_CHARTS)}] Exporting: {name}")
        try:
            if export_chart_optimized(name, code, output_dir, format,
                                     width=width, font_size=font_size):
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"  [ERROR] {str(e)[:100]}")
            fail_count += 1

    # 结果汇总
    print("\n" + "=" * 70)
    print(f"  ✅ Export Complete!")
    print(f"     Success: {success_count}/{len(MERMAID_CHARTS)} charts")
    print(f"     Failed:  {fail_count} charts")
    print(f"  📂 Location: {os.path.abspath(output_dir)}")
    print("=" * 70)

    # 使用建议
    if success_count > 0:
        print("\n💡 Tips:")
        print("   • If text is still cut off, reduce font size (--font 12)")
        print("   • For higher resolution, increase width (--width 4000)")
        print("   • For presentations, use PNG format")
        print("   • For documents/papers, use SVG format\n")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Export Mermaid charts with optimized font rendering",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python %(prog)s                      # Default settings
  python %(prog)s --font 12             # Smaller font (better fit)
  python %(prog)s --font 16             # Larger font (if space allows)
  python %(prog)s --width 4000          # Higher resolution
  python %(prog)s -f svg               # Vector graphics
  python %(prog)s -o ./my_charts       # Custom output directory
        """
    )
    parser.add_argument("-o", "--output", default=None,
                       help="Output directory (default: ./images_optimized)")
    parser.add_argument("-f", "--format",
                       choices=["png", "svg", "pdf"],
                       default="png",
                       help="Output format (default: png)")
    parser.add_argument("--font", type=int, default=14,
                       choices=[10, 11, 12, 13, 14, 15, 16, 18, 20],
                       help="Font size in pixels (default: 14, recommended: 12-16)")
    parser.add_argument("--width", type=int, default=3200,
                       help="Image width in pixels (default: 3200)")
    parser.add_argument("--list", action="store_true",
                       help="List available charts")

    args = parser.parse_args()

    if args.list:
        print("\nAvailable Charts:\n")
        for i, name in enumerate(MERMAID_CHARTS.keys(), 1):
            print(f"  {i:2d}. {name}")
        print()
        return

    export_all_charts(args.output, args.format, args.font, args.width)


if __name__ == "__main__":
    main()
