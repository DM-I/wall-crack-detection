"""
摄影测量技术路线图导出工具
基于用户提供的图片复原的技术路线图
"""

import os
import sys
import re

# 修复 Windows 控制台编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


# 复原的图表代码
PHOTOGRAMMETRY_CHARTS = {
    "10_摄影测量技术路线总览": """flowchart TB
    subgraph Input["数据采集与输入层"]
        direction LR
        I1["无人机<br/>全景相机<br/>普通相机<br/>航迹大师等<br/>航线规划软件"]
        I2["Context Capture<br/>大疆智图<br/>重建大师<br/>Metashape Pro<br/>Pix4Dmapper<br/>DP-Smart和<br/>全景摄影测量系统"]
        I3["DP-Modeler<br/>模方<br/>SVSModeler"]
        I4["DP-Modeler<br/>MicroStation"]
        I5["CAD<br/>......"]
    end

    subgraph Process["数据处理流程"]
        P1["建筑地形/<br/>室内外影像<br/>等采集"]
        P2["航线或路径<br/>等规划"]
        P3["垂直摄影<br/>倾斜摄影<br/>贴近摄影<br/>全景拍摄<br/>普通拍摄"]
        P4["摄影测量<br/>处理"]
    end

    subgraph Model3D["实景三维建模分支"]
        M1["实景三维<br/>建模修模"]
        M2a["在实景三维<br/>模型中绘制"]
        M2b["参照实景<br/>三维模型绘制"]
        M2c["平面剖等<br/>纹理投影"]
        M3["基于纹理<br/>影像绘制"]
        M4["平面立面<br/>剖面大样<br/>图纸"]
    end

    subgraph LightWeight["模型轻量化分支"]
        L1["模型轻量化"]
        L2a["基于实景三维<br/>模型BIM建模"]
        L2b["在实景三维<br/>模型中单体化<br/>拆解建模"]
        L3a["BIM模型"]
        L3b["单体化<br/>拆解模型"]
    end

    subgraph Output["输出与应用层"]
        O1["DP-Modeler<br/>模方<br/>SVSModeler<br/>MicroStation"]
        O2["Revit<br/>MicroStation"]
        O3["神经辐射场<br/>NeRF<br/>实景三维建模"]
        O4["元宇宙环境应用<br/>XR(VR/AR/MR)"]
        O5["3D Max<br/>Mars软件<br/>虚幻引擎等<br/>游戏引擎"]
    end

    P1 --> P2 --> P3 --> P4

    I1 --> P1
    I2 --> P4
    I3 --> M1
    I4 --> M4
    I5 --> M4

    P4 --> M1
    M1 --> M2a & M2b & M2c
    M2c --> M3
    M2a & M2b & M3 --> M4

    M1 --> L1
    L1 --> L2a & L2b
    L2a --> L3a
    L2b --> L3b

    M4 --> O1
    L3a --> O2
    L3b --> O1
    P3 --> O3
    O3 --> O4
    P4 --> O5

    style Input fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style Process fill:#fff3e0,stroke:#e65100,color:#bf360c
    style Model3D fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    style LightWeight fill:#fce4ec,stroke:#c62828,color:#b71c1c
    style Output fill:#f3e5f5,stroke:#7b1fa2,color:#4a148c""",

    "11_数据采集输入层": """flowchart LR
    subgraph Source1["影像数据源"]
        S1_1["无人机"]
        S1_2["全景相机"]
        S1_3["普通相机"]
        S1_4["航线规划软件<br/>(航迹大师等)"]
    end

    subgraph Source2["摄影测量软件"]
        S2_1["Context Capture"]
        S2_2["大疆智图"]
        S2_3["重建大师"]
        S2_4["Metashape Pro"]
        S2_5["Pix4Dmapper"]
        S2_6["DP-Smart"]
        S2_7["全景摄影测量系统"]
    end

    subgraph Source3["建模软件"]
        S3_1["DP-Modeler 模方"]
        S3_2["SVSModeler"]
        S3_3["MicroStation"]
    end

    subgraph Source4["辅助工具"]
        S4_1["CAD"]
    end

    Source1 --> Source2
    Source2 --> Source3
    Source3 --> Source4

    style Source1 fill:#bbdefb,stroke:#1976d2
    style Source2 fill:#c8e6c9,stroke:#388e3c
    style Source3 fill:#ffccbc,stroke:#f57c00
    style Source4 fill:#e1bee7,stroke:#8e24aa""",

    "12_核心处理流程": """flowchart LR
    A[("建筑地形/<br/>室内外影像<br/>等采集")] --> B[("航线或路径<br/>等规划")]
    B --> C[("垂直摄影<br/>倾斜摄影<br/>贴近摄影<br/>全景拍摄<br/>普通拍摄")]
    C --> D[("摄影测量<br/>处理")]

    style A fill:#e3f2fd,stroke:#1565c0
    style B fill:#e8f5e9,stroke:#2e7d32
    style C fill:#fff3e0,stroke:#e65100
    style D fill:#fce4ec,stroke:#c62828""",

    "13_实景三维建模分支": """flowchart TB
    Start["摄影测量<br/>处理"] --> Model["实景三维<br/>建模修模"]

    Model --> Draw1["在实景三维<br/>模型中绘制"]
    Model --> Draw2["参照实景<br/>三维模型绘制"]
    Model --> Section["平面剖等<br/>纹理投影"]

    Section --> TextureDraw["基于纹理<br/>影像绘制"]

    Draw1 --> Output["平面立面<br/>剖面大样<br/>图纸"]
    Draw2 --> Output
    TextureDraw --> Output

    style Start fill:#e3f2fd,stroke:#1565c0
    style Model fill:#fff3e0,stroke:#e65100
    style Draw1 fill:#e8f5e9,stroke:#2e7d32
    style Draw2 fill:#e8f5e9,stroke:#2e7d32
    style Section fill:#fce4ec,stroke:#c62828
    style TextureDraw fill:#fce4ec,stroke:#c62828
    style Output fill:#f3e5f5,stroke:#7b1fa2""",

    "14_模型轻量化BIM分支": """flowchart TB
    ModelIn["实景三维<br/>建模修模"] --> Light["模型轻量化"]

    Light --> BIM1["基于实景三维<br/>模型BIM建模"]
    Light --> BIM2["在实景三维<br/>模型中<br/>单体化拆解建模"]

    BIM1 --> Out1["BIM模型"]
    BIM2 --> Out2["单体化<br/>拆解模型"]

    Out1 --> Revit["Revit<br/>MicroStation"]
    Out2 --> DPS["DP-Modeler<br/>模方<br/>SVSModeler<br/>MicroStation"]

    style ModelIn fill:#e3f2fd,stroke:#1565c0
    style Light fill:#fff3e0,stroke:#e65100
    style BIM1 fill:#e8f5e9,stroke:#2e7d32
    style BIM2 fill:#e8f5e9,stroke:#2e7d32
    style Out1 fill:#c8e6c9,stroke:#388e3c
    style Out2 fill:#c8e6c9,stroke:#388e3c
    style Revit fill:#ffe0b2,stroke:#ef6c00
    style DPS fill:#e1bee7,stroke:#8e24aa""",

    "15_新兴技术应用": """flowchart TB
    Photo["摄影测量<br/>处理"] --> NeRF["神经辐射场<br/>NeRF<br/>实景三维建模"]
    Shoot["垂直摄影<br/>倾斜摄影<br/>贴近摄影<br/>全景拍摄"] --> Game["3D Max<br/>Mars软件<br/>虚幻引擎等<br/>游戏引擎"]

    NeRF --> Meta["元宇宙环境应用<br/>XR(VR/AR/MR)"]

    style Photo fill:#e3f2fd,stroke:#1565c0
    style NeRF fill:#fce4ec,stroke:#c62828
    style Meta fill:#f3e5f5,stroke:#7b1fa2
    style Shoot fill:#fff3e0,stroke:#e65100
    style Game fill:#e0f7fa,stroke:#00838f""",
}


# HTML 模板（优化字体显示）
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
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
            font-size: {font_size}px !important;
            line-height: 1.4 !important;
        }}
        .mermaid .nodeLabel,
        .mermaid .label {{
            font-size: {font_size}px !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
                         'Microsoft YaHei', 'PingFang SC', sans-serif !important;
            line-height: 1.4 !important;
            word-wrap: break-word;
            white-space: pre-wrap;
        }}
        .mermaid .edgeLabel {{
            font-size: {edge_font_size}px !important;
            background-color: white !important;
        }}
        .mermaid .cluster-label {{
            font-size: {subgraph_font_size}px !important;
            font-weight: bold !important;
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
            themeVariables: {{
                fontSize: '{font_size}px',
                nodeFontSize: '{font_size}px',
                edgeFontSize: '{edge_font_size}px',
                fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif',
                nodePadding: 15,
                lineHeight: 1.4,
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
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                wrap: true,
                padding: 15,
            }},
            securityLevel: 'loose'
        }});
    </script>
</body>
</html>
"""


def check_playwright():
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        return False


def export_chart(chart_name: str, chart_code: str, output_dir: str,
                 format: str = "png", width: int = 3200, font_size: int = 14):
    from playwright.sync_api import sync_playwright

    html_content = HTML_TEMPLATE.format(
        title=chart_name,
        code=chart_code,
        width=width,
        padding=max(40, width // 60),
        font_size=font_size,
        edge_font_size=min(font_size + 2, 16),
        subgraph_font_size=font_size + 2
    )

    safe_name = re.sub(r'[^\w\u4e00-\u9fff-]', '_', chart_name)
    output_file = os.path.join(output_dir, f"{safe_name}.{format}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": 2400})
        page.set_content(html_content)

        try:
            page.wait_for_selector('.mermaid', timeout=15000)
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"  [!] Render warning: {str(e)[:80]}")

        try:
            if format == 'png':
                element = page.query_selector('.mermaid')
                if element:
                    element.screenshot(path=output_file, type='png', quality=100)
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
                page.pdf(path=output_file, format='A3', landscape=True,
                        margin={'top': '20px', 'right': '20px',
                               'bottom': '20px', 'left': '20px'})
            else:
                raise ValueError(f"Unsupported format: {format}")

            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file) / 1024
                print(f"  [OK] {chart_name} ({file_size:.1f} KB)")
                return True
            else:
                print(f"  [FAIL] {chart_name}")
                return False
        finally:
            browser.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Export Photogrammetry Technology Roadmap Charts"
    )
    parser.add_argument("-o", "--output", default=None, help="Output directory")
    parser.add_argument("-f", "--format", choices=["png", "svg", "pdf"],
                       default="png", help="Output format")
    parser.add_argument("--font", type=int, default=14,
                       help="Font size (default: 14)")
    parser.add_argument("--width", type=int, default=3200,
                       help="Image width (default: 3200)")
    parser.add_argument("--list", action="store_true",
                       help="List available charts")

    args = parser.parse_args()

    if args.list:
        print("\nAvailable Charts:\n")
        for i, name in enumerate(PHOTOGRAMMETRY_CHARTS.keys(), 1):
            print(f"  {i:2d}. {name}")
        print()
        return

    output_dir = args.output or os.path.join(os.path.dirname(__file__), "images_photogrammetry")
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 70)
    print("  Photogrammetry Technology Roadmap Export Tool")
    print("=" * 70)
    print(f"  Output : {output_dir}")
    print(f"  Format : {args.format.upper()}")
    print(f"  Font   : {args.font}px")
    print(f"  Width  : {args.width}px")
    print(f"  Charts : {len(PHOTOGRAMMETRY_CHARTS)}")
    print("=" * 70 + "\n")

    if not check_playwright():
        print("[!] Playwright not found.")
        print("[!] Install: pip install playwright && playwright install chromium")
        return

    success = 0
    fail = 0
    for i, (name, code) in enumerate(PHOTOGRAMMETRY_CHARTS.items(), 1):
        print(f"[{i:2d}/{len(PHOTOGRAMMETRY_CHARTS)}] {name}")
        try:
            if export_chart(name, code, output_dir, args.format,
                           args.width, args.font):
                success += 1
            else:
                fail += 1
        except Exception as e:
            print(f"  [ERROR] {str(e)[:100]}")
            fail += 1

    print("\n" + "=" * 70)
    print(f"  Complete! Success: {success}, Failed: {fail}")
    print(f"  Location: {os.path.abspath(output_dir)}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
