import os
import json
import base64
import dashscope
from dashscope import MultiModalConversation
from config import DASHSCOPE_API_KEY, QWEN_MODEL


class QwenVLAnalyzer:
    def __init__(self):
        dashscope.api_key = DASHSCOPE_API_KEY

    def analyze_image(self, image_path, detection_info=None):
        if not DASHSCOPE_API_KEY:
            return self._mock_analysis(image_path, detection_info)

        image_url = self._encode_image(image_path)

        prompt = self._build_prompt(detection_info)

        messages = [
            {
                "role": "user",
                "content": [
                    {"image": image_url},
                    {"text": prompt},
                ],
            }
        ]

        try:
            response = MultiModalConversation.call(
                model=QWEN_MODEL,
                messages=messages,
            )

            if response.status_code == 200:
                result_text = response.output.choices[0].message.content[0]["text"]
                return self._parse_analysis(result_text, detection_info)
            else:
                # API Key valid but model not activated — fallback to mock
                code = getattr(response, 'code', '')
                msg = getattr(response, 'message', str(response))
                result = self._mock_analysis(image_path, detection_info)
                result["mock"] = True
                result["api_error"] = f"{code} - {msg}"
                result["api_error_hint"] = "请前往阿里云 DashScope 控制台开通 QWEN-VL 模型服务"
                return result
        except Exception as e:
            # API call failed — fallback to mock
            result = self._mock_analysis(image_path, detection_info)
            result["mock"] = True
            result["api_error"] = str(e)
            result["api_error_hint"] = "请在阿里云控制台确认已开通模型服务且账户余额充足"
            return result

    def _encode_image(self, image_path):
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        ext = os.path.splitext(image_path)[1].lower()
        mime_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".bmp": "image/bmp",
            ".webp": "image/webp",
        }
        mime_type = mime_map.get(ext, "image/jpeg")
        return f"data:{mime_type};base64,{image_data}"

    def _build_prompt(self, detection_info):
        base_prompt = """你是一名专业的建筑结构安全检测工程师。请对这张墙体图片进行专业的裂缝检测分析。

请从以下几个方面进行详细分析，并以JSON格式输出：

1. **裂缝识别**：识别图片中是否存在裂缝，描述裂缝的形态、位置和数量
2. **裂缝分类**：将裂缝分为以下类型：横向裂缝、纵向裂缝、斜向裂缝、网状裂缝、龟裂
3. **严重程度评估**：根据裂缝的宽度、长度、深度特征评估严重程度（轻微/一般/严重/危险）
4. **可能原因分析**：分析裂缝产生的可能原因（如：沉降、温度应力、材料老化、施工质量等）
5. **风险评估**：评估裂缝对建筑结构安全的影响
6. **修复建议**：给出具体的修复方案和建议

请严格按照以下JSON格式输出：
```json
{
    "crack_found": true/false,
    "crack_description": "裂缝的详细描述",
    "crack_types": ["类型1", "类型2"],
    "severity": "轻微/一般/严重/危险",
    "estimated_width": "预估裂缝宽度范围(mm)",
    "possible_causes": ["原因1", "原因2"],
    "risk_assessment": "风险评估详细描述",
    "risk_level": "低/中/高/极高",
    "repair_suggestions": ["建议1", "建议2"],
    "urgency": "立即处理/尽快处理/计划处理/持续观察",
    "professional_opinion": "专业综合意见"
}
```"""

        if detection_info and detection_info.get("total_count", 0) > 0:
            summary = detection_info.get("summary", {})
            detections = detection_info.get("detections", [])
            det_info = f"""

补充信息 - YOLO目标检测结果：
- 检测到 {detection_info['total_count']} 处裂缝
- 严重程度: {summary.get('severity', '未知')}
- 最大置信度: {summary.get('max_confidence', 0)}
- 裂缝类型分布: {json.dumps(summary.get('class_distribution', {}), ensure_ascii=False)}
- 各检测框详情: {json.dumps([{'类型': d['class_name'], '置信度': d['confidence'], '面积': d.get('area_px', d.get('area', 0))} for d in detections], ensure_ascii=False)}

请结合以上目标检测结果进行更精确的分析。"""

            return base_prompt + det_info

        return base_prompt

    def _parse_analysis(self, result_text, detection_info):
        try:
            json_start = result_text.find("{")
            json_end = result_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = result_text[json_start:json_end]
                analysis = json.loads(json_str)
                return {
                    "success": True,
                    "analysis": analysis,
                    "detection_info": detection_info,
                }
        except json.JSONDecodeError:
            pass

        return {
            "success": True,
            "analysis": {
                "crack_found": True,
                "crack_description": result_text,
                "severity": "待评估",
                "professional_opinion": result_text,
            },
            "detection_info": detection_info,
            "raw_text": result_text,
        }

    def _mock_analysis(self, image_path, detection_info):
        has_crack = detection_info and detection_info.get("total_count", 0) > 0
        severity = detection_info.get("summary", {}).get("severity", "无") if detection_info else "无"

        if not has_crack:
            analysis = {
                "crack_found": False,
                "crack_description": "未检测到明显裂缝",
                "crack_types": [],
                "severity": "轻微",
                "estimated_width": "0mm",
                "possible_causes": [],
                "risk_assessment": "墙体表面状况良好，未发现明显裂缝",
                "risk_level": "低",
                "repair_suggestions": ["建议定期巡检，持续观察"],
                "urgency": "持续观察",
                "professional_opinion": "当前墙体状况良好，无需特殊处理，建议保持定期检查。",
            }
        else:
            class_dist = detection_info.get("summary", {}).get("class_distribution", {})
            crack_types = list(class_dist.keys()) if class_dist else ["裂缝"]

            severity_map = {
                "轻微": ("0.1-0.2mm", "低", "持续观察"),
                "一般": ("0.2-0.5mm", "中", "计划处理"),
                "严重": ("0.5-2mm", "高", "尽快处理"),
                "危险": (">2mm", "极高", "立即处理"),
            }
            width, risk, urgency = severity_map.get(severity, ("未知", "中", "计划处理"))

            analysis = {
                "crack_found": True,
                "crack_description": f"检测到{len(detection_info.get('detections', []))}处裂缝，类型包括{', '.join(crack_types)}",
                "crack_types": crack_types,
                "severity": severity,
                "estimated_width": width,
                "possible_causes": ["温度应力", "材料收缩", "地基沉降"],
                "risk_assessment": f"检测到{severity}程度裂缝，需{urgency}",
                "risk_level": risk,
                "repair_suggestions": [
                    "对裂缝进行标记和记录",
                    "使用裂缝测宽仪精确测量裂缝宽度",
                    "根据裂缝类型选择合适的修复方案",
                    "修复后持续观察是否有新发展",
                ],
                "urgency": urgency,
                "professional_opinion": f"墙体存在{severity}程度裂缝，建议{urgency}。需进一步检测确认裂缝深度和走向，评估对结构安全的影响。",
            }

        return {
            "success": True,
            "analysis": analysis,
            "detection_info": detection_info,
            "mock": True,
        }
