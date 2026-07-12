import streamlit as st
import requests
import json
import sys
import os
import time
import traceback
import base64
import uuid
import subprocess
import io
import random
import re
from PIL import Image

MAX_UPLOAD_BYTES = 12 * 1024 * 1024
MAX_IMAGE_PIXELS = 40_000_000

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_APP_ROOT = os.path.dirname(_BASE_DIR)
sys.path.insert(0, _BASE_DIR)

try:
    import db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

try:
    import image_handler as ih
    IMG_AVAILABLE = True
except ImportError:
    IMG_AVAILABLE = False

try:
    import visualize as viz
    VIZ_AVAILABLE = True
except ImportError:
    VIZ_AVAILABLE = False

try:
    import rag
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

try:
    import code_runner
    CODE_RUNNER_AVAILABLE = True
except ImportError:
    CODE_RUNNER_AVAILABLE = False

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="📐 数学物理方法助教",
    page_icon="📐",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    .thinking-banner {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.85rem 1rem;
        margin: 0.25rem 0 0.75rem 0;
        border: 1px solid #f2c94c;
        border-left: 6px solid #f2994a;
        border-radius: 8px;
        background: #fff8df;
        color: #5a3b00;
        font-weight: 650;
        box-shadow: 0 6px 20px rgba(242, 153, 74, 0.16);
    }
    .thinking-dot {
        width: 0.62rem;
        height: 0.62rem;
        border-radius: 999px;
        background: #f2994a;
        animation: thinkingPulse 0.9s infinite ease-in-out;
        flex: 0 0 auto;
    }
    .thinking-dot:nth-child(2) { animation-delay: 0.15s; }
    .thinking-dot:nth-child(3) { animation-delay: 0.30s; }
    @keyframes thinkingPulse {
        0%, 80%, 100% { transform: scale(0.65); opacity: 0.35; }
        40% { transform: scale(1); opacity: 1; }
    }
    [data-testid="stSidebar"] h1 {
        font-size: 1.9rem;
        line-height: 1.22;
        margin-bottom: 0.7rem;
        color: var(--text-color);
    }
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin: 1.2rem 0 0.7rem 0;
        min-width: 0;
    }
    .sidebar-brand-icon {
        flex: 0 0 auto;
        font-size: 1.85rem;
        line-height: 1;
    }
    .sidebar-brand-title {
        flex: 1 1 auto;
        min-width: 0;
        color: var(--text-color);
        font-size: clamp(1.55rem, 1.1rem + 1vw, 1.95rem) !important;
        line-height: 1.15 !important;
        font-weight: 800;
        letter-spacing: 0;
        white-space: nowrap;
        word-break: keep-all;
        overflow-wrap: normal;
    }
    .sidebar-brand-subtitle {
        margin: 0 0 1.35rem 0;
        font-size: 1.04rem !important;
        line-height: 1.45 !important;
        color: color-mix(in srgb, var(--text-color) 78%, transparent);
        white-space: nowrap;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] div {
        font-size: 1.08rem;
        line-height: 1.65;
        color: var(--text-color);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong {
        font-size: 1.22rem;
        color: var(--text-color);
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [role="radiogroup"] label {
        font-size: 1.08rem;
        color: var(--text-color);
    }
    [data-testid="stSidebar"] [role="radiogroup"] p {
        font-size: 1.12rem;
        font-weight: 700;
        color: var(--text-color);
    }
    [data-testid="stSidebar"] button {
        min-height: 2.9rem;
    }
    [data-testid="stSidebar"] button p {
        font-size: 1.06rem;
        font-weight: 650;
        line-height: 1.35;
        color: var(--text-color);
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(128, 128, 128, 0.35);
    }
    .sidebar-muted {
        color: color-mix(in srgb, var(--text-color) 72%, transparent);
    }
    .sidebar-note {
        color: color-mix(in srgb, var(--text-color) 78%, transparent);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==================== 后端 API 配置 ====================
try:
    api_key = st.secrets["api_key"]
    provider = st.secrets.get("provider", "deepseek")
    model = st.secrets.get("model", "deepseek-v4-pro")
    vision_provider = st.secrets.get("vision_provider", provider)
    vision_model = st.secrets.get("vision_model", "")
    vision_api_key = st.secrets.get("vision_api_key", api_key if vision_provider == provider else "")
    local_fallback_enabled = st.secrets.get("local_fallback_enabled", True)
    local_fallback_url = st.secrets.get("local_fallback_url", "http://127.0.0.1:1234/v1/chat/completions")
    local_fallback_model = st.secrets.get("local_fallback_model", "qwen/qwen3-vl-4b")
    local_fallback_api_key = st.secrets.get("local_fallback_api_key", "lm-studio")
    response_max_tokens = int(st.secrets.get("response_max_tokens", 8192))
    vision_max_tokens = int(st.secrets.get("vision_max_tokens", 3072))
    code_runner_enabled = bool(st.secrets.get("code_runner_enabled", True))
except Exception:
    api_key = os.environ.get("API_KEY", "")
    provider = os.environ.get("API_PROVIDER", "deepseek")
    model = os.environ.get("API_MODEL", "deepseek-v4-pro")
    vision_provider = os.environ.get("VISION_API_PROVIDER", provider)
    vision_model = os.environ.get("VISION_API_MODEL", "")
    vision_api_key = os.environ.get("VISION_API_KEY", api_key if vision_provider == provider else "")
    local_fallback_enabled = os.environ.get("LOCAL_FALLBACK_ENABLED", "true").lower() not in ("0", "false", "no")
    local_fallback_url = os.environ.get("LOCAL_FALLBACK_URL", "http://127.0.0.1:1234/v1/chat/completions")
    local_fallback_model = os.environ.get("LOCAL_FALLBACK_MODEL", "qwen/qwen3-vl-4b")
    local_fallback_api_key = os.environ.get("LOCAL_FALLBACK_API_KEY", "lm-studio")
    response_max_tokens = int(os.environ.get("RESPONSE_MAX_TOKENS", "8192"))
    vision_max_tokens = int(os.environ.get("VISION_MAX_TOKENS", "3072"))
    code_runner_enabled = os.environ.get("CODE_RUNNER_ENABLED", "true").lower() in ("1", "true", "yes")

API_CONFIG = {
    "kimi": {
        "url": "https://api.moonshot.cn/v1/chat/completions",
        "default_model": "moonshot-v1-8k",
        "resp_path": ["choices", 0, "message", "content"],
        "vision_model": "moonshot-v1-8k-vision-preview",
        "vision_models_available": [
            "moonshot-v1-8k-vision-preview",
            "moonshot-v1-32k-vision-preview",
            "moonshot-v1-128k-vision-preview"
        ]
    },
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "default_model": "gpt-4o-mini",
        "resp_path": ["choices", 0, "message", "content"],
        "vision_model": "gpt-4o-mini",
        "vision_models_available": ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1"]
    },
    "deepseek": {
        "url": "https://api.deepseek.com/v1/chat/completions",
        "default_model": "deepseek-v4-pro",
        "resp_path": ["choices", 0, "message", "content"],
        "vision_model": None
    },
    "dashscope": {
        "url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
        "default_model": "qwen-plus",
        "resp_path": ["output", "choices", 0, "message", "content"],
        "vision_url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
        "compatible_vision_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "vision_model": "qwen-vl-plus",
        "vision_models_available": ["qwen-vl-plus", "qwen-vl-max", "qwen2.5-vl-72b-instruct"]
    },
    "qwen_token_plan": {
        "url": "https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions",
        "default_model": "qwen3.7-plus",
        "resp_path": ["choices", 0, "message", "content"],
        "vision_model": "qwen3.7-plus",
        "vision_models_available": ["qwen3.7-plus", "qwen3.6-plus"]
    },
    "lmstudio": {
        "url": local_fallback_url,
        "default_model": local_fallback_model,
        "resp_path": ["choices", 0, "message", "content"],
        "vision_model": local_fallback_model,
        "vision_models_available": [local_fallback_model]
    }
}

MODEL_PREFIX_MAP = {
    "kimi": ["kimi", "moonshot"],
    "openai": ["gpt"],
    "deepseek": ["deepseek"],
    "dashscope": ["qwen"],
    "qwen_token_plan": ["qwen"],
    "lmstudio": ["qwen", "local", "lm"]
}

PROVIDER_DISPLAY_NAMES = {
    "kimi": "Kimi",
    "openai": "ChatGPT/OpenAI",
    "deepseek": "DeepSeek",
    "dashscope": "Qwen-VL",
    "qwen_token_plan": "Qwen Token Plan",
    "lmstudio": "本地备用模型"
}


def _resolve_model(prov, mdl):
    cfg = API_CONFIG.get(prov, API_CONFIG["deepseek"])
    prefixes = MODEL_PREFIX_MAP.get(prov, [cfg["default_model"].split("-")[0]])
    return mdl if any(mdl.startswith(p) for p in prefixes) else cfg["default_model"]


def _encode_image(file_bytes, mime_type="image/jpeg"):
    """Normalize uploaded images to PNG data URLs accepted by Qwen-VL."""
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise ValueError("图片文件过大，请上传不超过 12 MB 的图片。")
    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            width, height = img.size
            if width * height > MAX_IMAGE_PIXELS:
                raise ValueError("图片像素数量过大，已拒绝处理。")
            img.load()

            # Qwen-VL rejects tiny images; upscale thumbnails used in smoke tests.
            min_side = min(img.size)
            if min_side < 12:
                scale = 12 / max(min_side, 1)
                img = img.resize(
                    (max(12, int(img.width * scale)), max(12, int(img.height * scale))),
                    Image.Resampling.NEAREST,
                )

            max_side = max(img.size)
            if max_side > 2048:
                scale = 2048 / max_side
                img = img.resize(
                    (int(img.width * scale), int(img.height * scale)),
                    Image.Resampling.LANCZOS,
                )

            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA" if "A" in img.getbands() else "RGB")

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            return f"data:image/png;base64,{b64}"
    except Image.DecompressionBombError as exc:
        raise ValueError("图片像素数量超过安全限制，已拒绝处理。") from exc
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("无法安全解析该图片文件。") from exc


def _normalize_image_data_url(image_data_url):
    """Re-normalize an existing data URL from session state to a PNG data URL."""
    if not image_data_url or not isinstance(image_data_url, str):
        return image_data_url
    if not image_data_url.startswith("data:") or "," not in image_data_url:
        return image_data_url
    header, payload = image_data_url.split(",", 1)
    mime = "image/png"
    if header.startswith("data:") and ";" in header:
        mime = header[5:].split(";", 1)[0] or mime
    try:
        raw = base64.b64decode(payload, validate=False)
    except Exception:
        return image_data_url
    return _encode_image(raw, mime)


def _build_mm_content(text, image_data_url, prov):
    """构建多模态消息内容：DashScope 用 image 字段，其他用 image_url 格式"""
    if prov == "dashscope":
        return [
            {"image": image_data_url},
            {"text": text}
        ]
    return [
        {"type": "text", "text": text},
        {"type": "image_url", "image_url": {"url": image_data_url, "detail": "auto"}}
    ]


def _build_openai_mm_content(text, image_data_url):
    return [
        {"type": "image_url", "image_url": {"url": image_data_url}},
        {"type": "text", "text": text}
    ]


def _supports_multimodal(mdl):
    """检查模型是否本身支持多模态图片输入"""
    # 注意：deepseek-v4-pro / deepseek-v3 / deepseek-chat 等文本模型可能不支持多模态
    # 多模态需要使用专门的视觉模型，如 deepseek-vl、qwen-vl-plus、gpt-4o 等
    mm_models = ["vl", "vision", "qwen2", "gpt-4o", "gpt-4-turbo", "claude-3", "gemini"]
    return any(kw in mdl.lower() for kw in mm_models)


def _get_vision_model(prov, current_model):
    """获取可用的视觉模型，若当前模型已是视觉模型则返回自身"""
    cfg = API_CONFIG.get(prov, {})
    if _supports_multimodal(current_model):
        return current_model, None  # 已经是视觉模型
    vmodel = cfg.get("vision_model")
    if vmodel:
        return vmodel, cfg.get("vision_url")
    return None, None  # 该提供商不支持视觉


def _provider_display_name(prov):
    return PROVIDER_DISPLAY_NAMES.get(prov, prov)


def _local_fallback_available():
    return bool(local_fallback_enabled and local_fallback_url and local_fallback_model)


def _auth_headers(key):
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    return headers


def _request_timeout(prov, default):
    return 180 if prov == "lmstudio" else default


def _normalize_openai_vision_messages(messages):
    converted_messages = []
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, list):
            text_parts = []
            image_parts = []
            normalized_parts = []
            for part in content:
                if "text" in part and "type" not in part:
                    text_parts.append(part.get("text", ""))
                elif "image" in part:
                    image_parts.append(part.get("image", ""))
                else:
                    normalized_parts.append(part)
            if image_parts:
                content = _build_openai_mm_content("\n".join(text_parts), image_parts[0])
            elif normalized_parts:
                content = normalized_parts
        converted_messages.append({"role": msg.get("role", "user"), "content": content})
    return converted_messages


def _chat_value_field(value, field, default=None):
    if hasattr(value, field):
        return getattr(value, field)
    if isinstance(value, dict):
        return value.get(field, default)
    try:
        return value[field]
    except Exception:
        return default


def _render_thinking_banner(text):
    st.markdown(
        f"""
        <div class="thinking-banner">
            <div class="thinking-dot"></div>
            <div class="thinking-dot"></div>
            <div class="thinking-dot"></div>
            <div>{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _call_vision_llm_once(prov, current_model, messages, api_key):
    """调用视觉模型处理含图片的消息"""
    cfg = API_CONFIG.get(prov, API_CONFIG["deepseek"])
    vmodel, vurl = _get_vision_model(prov, current_model)

    if not vmodel:
        raise Exception("当前视觉配置不可用，请检查图片理解服务配置。")

    url = vurl or cfg.get("url")
    headers = _auth_headers(api_key)
    compatible_dashscope = False

    if prov == "dashscope":
        # The OpenAI-compatible DashScope endpoint is more stable with data URL uploads.
        compatible_url = cfg.get("compatible_vision_url")
        if compatible_url:
            compatible_dashscope = True
            converted_messages = _normalize_openai_vision_messages(messages)
            payload = {
                "model": vmodel,
                "messages": converted_messages,
                "temperature": 0.3,
                "max_tokens": vision_max_tokens,
            }
            url = compatible_url
        else:
            payload = {
                "model": vmodel,
                "input": {"messages": messages},
                "parameters": {"temperature": 0.3, "max_tokens": vision_max_tokens}
            }
    else:
        payload = {
            "model": vmodel,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": vision_max_tokens
        }

    resp = requests.post(url, headers=headers, json=payload, timeout=_request_timeout(prov, 90))
    data = resp.json()

    if resp.status_code != 200:
        err = data.get("error", {}).get("message", data.get("message", f"HTTP {resp.status_code}"))
        raise Exception(f"视觉模型调用失败: {err}")

    # 解析响应（DashScope VL 返回 content 为数组，其他返回字符串）
    path = ["choices", 0, "message", "content"] if compatible_dashscope else cfg.get("resp_path", ["choices", 0, "message", "content"])
    result = data
    for key in path:
        result = result[key]

    if isinstance(result, list):
        result = "".join(p.get("text", "") for p in result)

    return result, vmodel


def call_vision_llm(prov, current_model, messages, api_key):
    try:
        return _call_vision_llm_once(prov, current_model, messages, api_key)
    except Exception as primary_exc:
        if prov != "lmstudio" and _local_fallback_available():
            try:
                return _call_vision_llm_once(
                    "lmstudio",
                    local_fallback_model,
                    _normalize_openai_vision_messages(messages),
                    local_fallback_api_key,
                )
            except Exception as fallback_exc:
                raise Exception(f"图片理解服务失败；本地备用服务也不可用: {fallback_exc}") from primary_exc
        raise


def build_vision_extraction_prompt(user_prompt):
    """Prompt the vision model to extract visual information only, leaving reasoning to the text model."""
    return (
        "你负责图片理解，不负责最终解题。请忠实提取图片中的可见信息，"
        "包括题干、公式、符号、坐标轴、图形关系、边界条件、手写内容和可能的歧义。"
        "若图片中有数学/物理题，请尽量转写为 Markdown + LaTeX。"
        "不要补充图片中没有的信息，不要给最终答案。\n\n"
        f"用户原始问题：{user_prompt or '请分析图片内容'}"
    )


def _normalize_math_markdown(text):
    """Convert common raw-LaTeX delimiters to Streamlit-friendly Markdown math."""
    if not text or not isinstance(text, str):
        return text

    normalized = text

    # Repair model output where several dollar signs are used as opening
    # delimiters but none of them is closed, leaving the whole formula raw.
    repaired_lines = []
    for line in normalized.splitlines():
        dollar_positions = [i for i, char in enumerate(line) if char == "$" and (i == 0 or line[i - 1] != "\\")]
        has_latex_command = re.search(r"\\(?:int|frac|sum|omega|infty|partial|nabla|bar|hat|sqrt)\b", line)
        all_openers = dollar_positions and all(
            line[pos + 1:].lstrip().startswith("\\") for pos in dollar_positions
        )
        if len(dollar_positions) >= 2 and has_latex_command and (len(dollar_positions) % 2 == 1 or all_openers):
            line = line.replace("$", "")
            repaired_lines.append("$$")
            repaired_lines.append(line.strip())
            repaired_lines.append("$$")
        else:
            repaired_lines.append(line)
    normalized = "\n".join(repaired_lines)

    normalized = re.sub(r"\\\\\((.+?)\\\\\)", r"$\1$", normalized, flags=re.DOTALL)
    normalized = re.sub(r"\\\\\[(.+?)\\\\\]", r"$$\n\1\n$$", normalized, flags=re.DOTALL)
    normalized = re.sub(r"\\\((.+?)\\\)", r"$\1$", normalized, flags=re.DOTALL)
    normalized = re.sub(r"\\\[(.+?)\\\]", r"$$\n\1\n$$", normalized, flags=re.DOTALL)
    normalized = re.sub(
        r"\\begin\{equation\*?\}(.+?)\\end\{equation\*?\}",
        r"$$\n\1\n$$",
        normalized,
        flags=re.DOTALL,
    )

    def _clean_display_math(match):
        content = match.group(1).replace("$", "")
        return f"$$\n{content.strip()}\n$$"

    # Models sometimes put inline dollar signs inside an already complete
    # display block. They split an otherwise valid formula into raw text.
    normalized = re.sub(r"\$\$(.+?)\$\$", _clean_display_math, normalized, flags=re.DOTALL)

    def _clean_malformed_inline_math(match):
        content = match.group(1).replace("$", "")
        suffix = match.group(2) or ""
        return f"${content.strip()}{suffix}$"

    normalized = normalized.replace("-$-\\", "-\\").replace("+$+\\", "+\\")
    normalized = re.sub(r"([+-])\$\\", r"\1\\", normalized)
    normalized = re.sub(r"\$(?!\$)([^\n]+?)\$\$([)\]}.,;:]?)", _clean_malformed_inline_math, normalized)

    # Some local/OpenAI-compatible models emit escaped backslashes as visible text.
    math_commands = (
        "overline", "mathbb", "hat", "frac", "sqrt", "infty", "cup", "cap",
        "to", "sum", "int", "oint", "partial", "nabla", "alpha", "beta",
        "gamma", "delta", "theta", "phi", "pi", "sin", "cos", "exp", "log",
        "begin", "end", "left", "right", "cdot", "times", "leq", "geq",
    )
    for command in math_commands:
        normalized = normalized.replace(f"\\\\{command}", f"\\{command}")
    normalized = normalized.replace("\\\\{", "\\{").replace("\\\\}", "\\}")

    command_group = "|".join(math_commands)
    mathish = r"[A-Za-z0-9\\{}_^+\-=,.:;\s|<>/]+"
    normalized = re.sub(
        rf"([（(])({mathish}\\(?:{command_group}){mathish})([）)])",
        lambda m: f"{m.group(1)}${m.group(2).strip()}${m.group(3)}",
        normalized,
    )

    def _repair_remaining_inline(match):
        content = match.group(1).replace("$", "")
        suffix = match.group(2) or ""
        return f"${content.strip()}{suffix}$"

    normalized = re.sub(r"\$(?!\$)([^\n]*?)\$\$([)\]}]?)", _repair_remaining_inline, normalized)

    normalized = normalized.replace(r"\left($", r"\left(")
    normalized = normalized.replace(r"\right$)", r"\right)").replace(r"\right$", r"\right)")
    normalized = normalized.replace("($-", "(-").replace("$)$", ")$")
    expanded_lines = []
    for line in normalized.splitlines():
        if "$$" in line and line.strip() != "$$":
            pieces = line.split("$$")
            for idx, piece in enumerate(pieces):
                if piece:
                    expanded_lines.append(piece)
                if idx < len(pieces) - 1:
                    expanded_lines.append("$$")
        else:
            expanded_lines.append(line)
    normalized = "\n".join(expanded_lines)
    formula_lines = []
    latex_line_pattern = re.compile(
        r"\\(?:sum|int|oint|frac|sqrt|sin|cos|tan|exp|log|bar|hat|left|right|infty|pi|omega|psi|phi|alpha|beta|delta|lambda|partial)\b"
    )
    in_display = False
    display_lines = normalized.splitlines()
    for line_index, line in enumerate(display_lines):
        if line.strip() == "$$":
            in_display = not in_display
            formula_lines.append(line)
            continue
        has_cjk = re.search(r"[\u3400-\u9fff]", line) is not None
        looks_like_formula = latex_line_pattern.search(line) and not has_cjk
        if in_display:
            formula_lines.append(line)
            next_line = display_lines[line_index + 1] if line_index + 1 < len(display_lines) else ""
            next_is_prose = bool(re.search(r"[\u3400-\u9fff]", next_line)) or next_line.lstrip().startswith(("#", ">"))
            if looks_like_formula and (not next_line.strip() or next_is_prose):
                formula_lines.append("$$")
                in_display = False
        elif looks_like_formula and "$" not in line and not line.lstrip().startswith(("#", ">")):
            formula_lines.extend(["$$", line.strip(), "$$"])
        else:
            formula_lines.append(line)
    if in_display:
        formula_lines.append("$$")
    normalized = "\n".join(formula_lines)

    # Do not apply broad bare-LaTeX wrapping after repairing delimiters: it
    # can introduce new dollar signs inside already valid inline formulas.
    return normalized

    bare_latex = re.compile(
        rf"(?<![$`])((?:\\(?:{command_group})[A-Za-z0-9\\{{}}_^+\-=,.:;|<>/]*(?:[ \t]+[A-Za-z0-9\\{{}}_^+\-=,.:;|<>/]+)*)+)"
    )
    display_blocks = []

    def _protect_display_block(match):
        display_blocks.append(match.group(0))
        return f"__MATH_DISPLAY_BLOCK_{len(display_blocks) - 1}__"

    protected = re.sub(r"\$\$(.+?)\$\$", _protect_display_block, normalized, flags=re.DOTALL)
    parts = protected.split("$")
    for idx in range(0, len(parts), 2):
        parts[idx] = bare_latex.sub(lambda m: f"${m.group(1).strip()}$", parts[idx])
    normalized = "$".join(parts)
    for idx, block in enumerate(display_blocks):
        normalized = normalized.replace(f"__MATH_DISPLAY_BLOCK_{idx}__", block)

    # Final pass for inline expressions such as $t\in(-$-\infty,\infty$$).
    def _final_inline_repair(match):
        content = match.group(1).replace("$", "")
        suffix = match.group(2) or ""
        return f"${content.strip()}{suffix}$"

    normalized = re.sub(r"\$(?!\$)(.+?)\$\$([)\]}])\$?", _final_inline_repair, normalized)
    normalized = re.sub(r"\$\$(.+?)\$\$", _clean_display_math, normalized, flags=re.DOTALL)

    return normalized


def _markdown(content, *args, **kwargs):
    st.markdown(_normalize_math_markdown(content), *args, **kwargs)


def _render_message(msg):
    """渲染单条消息，支持文本+图片"""
    content = msg.get("content", "")
    image_data = msg.get("image_data")
    if image_data:
        st.image(image_data, use_container_width=True)
    if content:
        _markdown(content)


def _safe_render_image(path, max_pixels=80_000_000):
    """Render an image only if it is reasonably sized for the browser and PIL."""
    try:
        with Image.open(path) as img:
            width, height = img.size
            pixels = width * height
    except Image.DecompressionBombError as exc:
        st.warning(f"图片尺寸过大，已跳过预览：{os.path.basename(path)}")
        st.caption(str(exc))
        st.code(path, language="text")
        return
    except Exception as exc:
        st.warning(f"图片无法预览：{os.path.basename(path)}")
        st.caption(str(exc))
        st.code(path, language="text")
        return

    if pixels > max_pixels:
        st.warning(
            f"图片过大，已跳过预览：{os.path.basename(path)} "
            f"({width} x {height}, {pixels:,} 像素)"
        )
        st.code(path, language="text")
        return

    try:
        st.image(path, use_container_width=True)
    except Image.DecompressionBombError as exc:
        st.warning(f"图片尺寸过大，已跳过预览：{os.path.basename(path)}")
        st.caption(str(exc))
        st.code(path, language="text")
    except Exception as exc:
        st.warning(f"图片预览失败：{os.path.basename(path)}")
        st.caption(str(exc))
        st.code(path, language="text")


def _render_python_code_runner(content, key_prefix):
    """Render opt-in execution controls for Python visualization code blocks."""
    if not CODE_RUNNER_AVAILABLE or not code_runner_enabled:
        return

    blocks = code_runner.extract_python_blocks(content)
    if not blocks:
        return

    with st.expander("运行回答中的 Python 可视化代码", expanded=False):
        st.caption("代码会在本机临时目录中执行；请只运行你信任的代码。支持自动捕获 matplotlib 图像和 GIF 动画。")
        selected = 0
        if len(blocks) > 1:
            selected = st.selectbox(
                "选择代码块",
                options=list(range(len(blocks))),
                format_func=lambda i: f"代码块 {i + 1}",
                key=f"{key_prefix}_code_select",
            )
            if selected is None:
                selected = 0
        selected_block = blocks[selected]
        looks_like_animation = any(
            marker in selected_block
            for marker in ("FuncAnimation", "Animation(", ".save(", "animation.gif", "writer='pillow'", 'writer="pillow"')
        )
        timeout = 90
        if False:
            timeout = st.slider(
            "超时时间（秒）",
            5,
            180,
            default_timeout,
            key=f"{key_prefix}_timeout",
            help="动画保存 GIF 通常需要更长时间。"
        )
        if st.button("运行并显示结果", key=f"{key_prefix}_run_code"):
            output_root = os.path.join(_BASE_DIR, "runtime_outputs")
            code_runner.cleanup_old_runs(output_root)
            run_status = st.status("正在计算，请稍候……", expanded=False)
            try:
                result = code_runner.run_python_block(blocks[selected], output_root, timeout=timeout)
                run_status.update(label="计算完成", state="complete")
            except subprocess.TimeoutExpired:
                run_status.update(label="计算超时，已停止运行", state="error")
                st.error(f"代码运行超过 {timeout} 秒，已停止，请检查代码后重试。")
                return
            except Exception as exc:
                run_status.update(label="计算失败", state="error")
                st.error(f"代码运行失败：{exc}")
                st.code(traceback.format_exc(), language="text")
                return

            if result.get("blocked"):
                st.error("代码已被安全策略阻止执行。")
                st.caption(result.get("block_reason", "该代码可能读取或泄露敏感运行环境信息。"))
                return

            if result["stdout"]:
                st.code(result["stdout"], language="text")
                if result.get("stdout_truncated"):
                    st.info("标准输出较长，页面仅显示末尾预览；完整输出已保存。")
                    st.code(result.get("stdout_path", ""), language="text")
            if result["stderr"]:
                st.code(result["stderr"], language="text")
                if result.get("stderr_truncated"):
                    st.info("错误输出较长，页面仅显示末尾预览；完整输出已保存。")
                    st.code(result.get("stderr_path", ""), language="text")
            if result["returncode"] != 0:
                st.error(f"Python 进程退出码：{result['returncode']}")

            visuals = result["visuals"]
            if not visuals:
                st.info("代码已运行，但没有捕获到 GIF/PNG/JPG/MP4 输出。若要显示动画，请创建 matplotlib.animation.Animation 对象，或保存为 animation.gif。")
            for path in visuals:
                lower = path.lower()
                if lower.endswith((".gif", ".png", ".jpg", ".jpeg")):
                    _safe_render_image(path)
                elif lower.endswith((".mp4", ".webm")):
                    st.video(path)


def _application_video_title(path):
    name = os.path.splitext(os.path.basename(path))[0]
    name = re.sub(r"^\d+(?:\.\d+)?", "", name).lstrip(" _-")
    return name.replace("_", " · ")


def _find_application_videos():
    video_root = os.path.join(_APP_ROOT, "new resources")
    if not os.path.isdir(video_root):
        return []

    videos = []
    for root, _, files in os.walk(video_root):
        for filename in files:
            if not filename.lower().endswith(".mp4"):
                continue
            path = os.path.join(root, filename)
            try:
                size_mb = os.path.getsize(path) / (1024 * 1024)
            except OSError:
                size_mb = 0
            videos.append({
                "title": _application_video_title(path),
                "filename": filename,
                "path": path,
                "size_mb": size_mb,
            })
    return sorted(videos, key=lambda item: item["filename"])


@st.cache_data(show_spinner=False)
def _load_video_bytes(path, mtime, size):
    with open(path, "rb") as f:
        return f.read()


def _set_application_video_idx(idx):
    st.session_state.application_video_idx = idx


def _render_application_videos():
    st.markdown("---")
    st.header("🎥 应用实例视频")
    videos = _find_application_videos()
    if not videos:
        st.info("暂未发现应用实例视频。请将 mp4 文件放入 `new resources` 文件夹。")
        return

    if "application_video_idx" not in st.session_state:
        st.session_state.application_video_idx = 0
    if st.session_state.application_video_idx >= len(videos):
        st.session_state.application_video_idx = 0

    selected_idx = st.selectbox(
        "选择视频",
        options=list(range(len(videos))),
        format_func=lambda idx: videos[idx]["title"],
        key="application_video_idx",
    )

    cols = st.columns(min(len(videos), 5))
    for idx, item in enumerate(videos):
        with cols[idx % len(cols)]:
            button_type = "primary" if idx == st.session_state.application_video_idx else "secondary"
            st.button(
                f"{idx + 1}",
                key=f"application_video_btn_{idx}",
                type=button_type,
                help=item["title"],
                on_click=_set_application_video_idx,
                args=(idx,),
            )

    selected_idx = st.session_state.application_video_idx
    video = videos[selected_idx]
    st.caption(f"{video['filename']} · {video['size_mb']:.1f} MB")
    try:
        mtime = os.path.getmtime(video["path"])
        size = os.path.getsize(video["path"])
        video_bytes = _load_video_bytes(video["path"], mtime, size)
        st.video(video_bytes, format="video/mp4")
    except OSError as exc:
        st.error(f"视频读取失败：{exc}")

    with st.expander("全部应用实例视频", expanded=False):
        for idx, item in enumerate(videos):
            st.markdown(f"- **{idx + 1}. {item['title']}** · `{item['filename']}` · {item['size_mb']:.1f} MB")


def _build_payload(prov, actual_model, messages):
    if prov == "dashscope":
        return {
            "model": actual_model,
            "input": {"messages": messages},
            "parameters": {"temperature": 0.3, "max_tokens": response_max_tokens, "result_format": "message"}
        }
    return {
        "model": actual_model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": response_max_tokens,
        "stream": True
    }


def _extract_answer(prov, data):
    path = API_CONFIG.get(prov, API_CONFIG["deepseek"])["resp_path"]
    result = data
    for key in path:
        result = result[key]
    return result


def _call_llm_streaming_once(prov, mdl, messages, api_key, placeholder):
    """流式调用 LLM，逐字输出到 placeholder；返回 (answer, elapsed_ms, approx_tokens)"""
    cfg = API_CONFIG.get(prov, API_CONFIG["deepseek"])
    actual_model = _resolve_model(prov, mdl)
    headers = _auth_headers(api_key)
    t_start = time.time()

    if prov == "dashscope":
        payload = {
            "model": actual_model,
            "input": {"messages": messages},
            "parameters": {"temperature": 0.3, "max_tokens": response_max_tokens, "result_format": "message"}
        }
        resp = requests.post(cfg["url"], headers=headers, json=payload, timeout=_request_timeout(prov, 60))
        data = resp.json()
        if resp.status_code != 200:
            err = data.get("error", {}).get("message", data.get("message", f"HTTP {resp.status_code}"))
            raise Exception(err)
        answer = _extract_answer(prov, data)
        answer = _normalize_math_markdown(answer)
        elapsed = int((time.time() - t_start) * 1000)
        placeholder.markdown(answer)
        approx_out = len(answer) // 2  # rough estimate
        return answer, elapsed, 0, approx_out

    payload = {
        "model": actual_model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": response_max_tokens,
        "stream": True
    }

    resp = requests.post(cfg["url"], headers=headers, json=payload, timeout=_request_timeout(prov, 60), stream=True)

    if resp.status_code != 200:
        data = resp.json()
        err = data.get("error", {}).get("message", f"HTTP {resp.status_code}")
        raise Exception(err)

    full_answer = ""
    for line in resp.iter_lines():
        if not line:
            continue
        line_str = line.decode("utf-8")
        if not line_str.startswith("data: "):
            continue
        json_str = line_str[6:]
        if json_str.strip() == "[DONE]":
            break
        try:
            chunk = json.loads(json_str)
            delta = chunk.get("choices", [{}])[0].get("delta", {})
            content = delta.get("content", "")
            if content:
                full_answer += content
                placeholder.markdown(_normalize_math_markdown(full_answer) + "▌")
        except json.JSONDecodeError:
            continue

    elapsed = int((time.time() - t_start) * 1000)
    full_answer = _normalize_math_markdown(full_answer)
    placeholder.markdown(full_answer)

    # 粗略估算系统prompt + 消息的input token数
    def _content_len(c):
        if isinstance(c, list):
            return sum(len(item.get("text", item.get("image", ""))) for item in c)
        return len(c)
    total_input_chars = sum(_content_len(m.get("content", "")) for m in messages)
    approx_in = total_input_chars // 2
    approx_out = len(full_answer) // 2

    return full_answer, elapsed, approx_in, approx_out


def call_llm_streaming(prov, mdl, messages, api_key, placeholder):
    try:
        return _call_llm_streaming_once(prov, mdl, messages, api_key, placeholder)
    except Exception as primary_exc:
        if prov != "lmstudio" and _local_fallback_available():
            placeholder.markdown("远程服务暂时不可用，正在切换到本地备用服务...")
            try:
                return _call_llm_streaming_once(
                    "lmstudio",
                    local_fallback_model,
                    messages,
                    local_fallback_api_key,
                    placeholder,
                )
            except Exception as fallback_exc:
                raise Exception(f"远程服务失败；本地备用服务也不可用: {fallback_exc}") from primary_exc
        raise


def _call_llm_once(prov, mdl, messages, api_key):
    """非流式调用（用于快速提问等场景）"""
    cfg = API_CONFIG.get(prov, API_CONFIG["deepseek"])
    actual_model = _resolve_model(prov, mdl)
    headers = _auth_headers(api_key)
    payload = _build_payload(prov, actual_model, messages)
    if "stream" in payload:
        del payload["stream"]
    resp = requests.post(cfg["url"], headers=headers, json=payload, timeout=_request_timeout(prov, 60))
    data = resp.json()
    if resp.status_code != 200:
        err = data.get("error", {}).get("message", data.get("message", f"HTTP {resp.status_code}"))
        raise Exception(err)
    return _extract_answer(prov, data)


def call_llm(prov, mdl, messages, api_key):
    try:
        return _call_llm_once(prov, mdl, messages, api_key)
    except Exception as primary_exc:
        if prov != "lmstudio" and _local_fallback_available():
            try:
                return _call_llm_once("lmstudio", local_fallback_model, messages, local_fallback_api_key)
            except Exception as fallback_exc:
                raise Exception(f"远程服务失败；本地备用服务也不可用: {fallback_exc}") from primary_exc
        raise


# ==================== 系统提示词 ====================
SYSTEM_PROMPT = """你是一位专注于《数学物理方法》课程的资深助教。你的任务是帮助学生理解课程中全部15章的核心概念、公式推导和解题方法。

课程分为上篇（复变函数论）和下篇（数学物理方程）：

上篇 · 复变函数论（第1-6章）：
- 第1章 复变函数：复数表示、解析函数（含实解析性与复解析性的区别）、C-R方程、初等函数、调和函数
- 第2章 复变函数的积分：柯西定理、积分公式、高阶导数、Morera定理
- 第3章 幂级数展开：泰勒级数、洛朗级数、收敛性、孤立奇点
- 第4章 留数定理：孤立奇点分类、留数计算、实积分应用
- 第5章 傅里叶变换：变换对、性质、δ函数、频谱分析
- 第6章 拉普拉斯变换：定义、性质、反演、ODE求解

下篇 · 数学物理方程（第7-15章）：
- 第7章 数学物理定解问题：三类方程、定解条件、分类、达朗贝尔公式
- 第8章 分离变数法：核心思想、五步骤、本征值问题、叠加原理
- 第9章 二阶常微分方程级数解法：S-L方程、本征值问题、广义傅里叶级数
- 第10章 球函数：勒让德方程、多项式、连带勒让德、球谐函数
- 第11章 柱函数：贝塞尔方程、三类柱函数、递推关系、正交性
- 第12章 格林函数法：点源响应、积分公式、电像法、本征函数展开
- 第13章 积分变换法：傅里叶/拉普拉斯变换解PDE、互补性
- 第14章 保角变换法：保角性、常用变换、二维拉普拉斯方程边值问题
- 第15章 非线性数学物理问题简介：孤立子、KdV方程、混沌

你的回答必须满足以下教学标准：
1. 每个回答必须包含以下部分：①概念定位（一句话说明这个问题属于哪个章节/知识点） ②核心公式（写出关键数学表达式，用LaTeX） ③详细推导（如果涉及证明/计算，分步展示，每步说明依据） ④物理直觉（用一句话或一个类比解释"这个数学结果意味着什么"） ⑤常见错误（列出学生最容易犯的1-2个错误及纠正） ⑥自检提问（向学生反问一个相关问题，检验是否真理解）
2. 公式格式规范（重要）：所有数学公式必须使用标准 Markdown LaTeX 格式。行内公式用单个美元符号 $...$，例如 $f(z) = u + iv$；独立公式（行间）用双美元符号 $$...$$，独占一行，例如 $$\\oint_C f(z)dz = 2\\pi i \\sum \\text{Res}(f,z_k)$$。禁止使用 \\( ... \\)、\\[ ... \\]、\\begin{equation}...\\end{equation} 等纯 LaTeX 命令形式。矩阵和分段函数用 $$...$$ 包裹，内部可用 \\begin{pmatrix}、\\begin{cases} 等环境。
3. 使用中文，公式用标准 Markdown LaTeX 格式（$...$ 和 $$...$$）。对大二/大三物理专业学生的知识水平
4. 避免过度抽象，每个数学结论必须给出物理/几何解释
5. 推导步骤不可跳过，不可说"显然"
6. 当用户要求生成 Python、Mathematica、Matlab 或其他程序代码时，必须给出可直接运行的完整代码块。不要用“略”“省略”“其余同理”“...”代替代码；如果代码较长，也要保持同一个代码块完整闭合。

超出课程范围的问题（如泛函分析、群论、拓扑学等）应礼貌拒绝，并说明不属于本课程范畴。"""


def build_system_prompt(question: str) -> str:
    """构建带 RAG 知识的系统提示词"""
    base = SYSTEM_PROMPT
    if not RAG_AVAILABLE:
        return base

    retrieved = rag.retrieve(question, top_k=4)
    if not retrieved:
        return base

    return base + f"\n\n---\n\n以下是与问题相关的课程知识参考，请结合使用：\n\n{retrieved}"


# ==================== 动画缓存 ====================
@st.cache_data(show_spinner=False)
def get_cached_animation(anim_key: str) -> bytes:
    if not VIZ_AVAILABLE or not hasattr(viz, 'ANIMATIONS'):
        return b""
    info = viz.ANIMATIONS.get(anim_key)
    if not info:
        return b""
    return info["function"]()


# ==================== CSS ====================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1B3A5C 0%, #0D1F33 100%);
        padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px;
    }
    .main-header h1 { font-size: 28px; margin-bottom: 8px; }
    .main-header p { color: rgba(255, 255, 255, 0.78); font-size: 14px; }
    .viz-recommend {
        background: var(--secondary-background-color); border-left: 3px solid #C8923A; padding: 12px 16px;
        border-radius: 0 8px 8px 0; margin: 12px 0;
    }
    .viz-recommend h4 { margin: 0 0 8px 0; color: var(--text-color); font-size: 14px; }
    .viz-recommend button { margin: 3px 4px 3px 0 !important; }
    .learning-stats {
        background: var(--secondary-background-color); padding: 10px 14px; border-radius: 8px;
        font-size: 12px; color: var(--text-color); margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)


def _show_viz_recommend(recs):
    """在回答下方展示推荐的可视化"""
    st.markdown('<div class="viz-recommend"><h4>📊 相关可视化推荐</h4></div>', unsafe_allow_html=True)

    all_keys = recs["static"] + recs["anim"]
    if not all_keys:
        return

    cols = st.columns(min(len(all_keys), 4))
    col_idx = 0

    for key in recs["static"]:
        if key in viz.VISUALIZATIONS and col_idx < len(cols):
            info = viz.VISUALIZATIONS[key]
            with cols[col_idx]:
                if st.button(f"📈 {info['title'][:15]}", key=f"rec_s_{key}"):
                    try:
                        fig = info["function"]()
                        st.pyplot(fig)
                        st.caption(info["description"])
                    except Exception as e:
                        st.error(f"生成出错：{e}")
            col_idx += 1

    for key in recs["anim"]:
        if hasattr(viz, 'ANIMATIONS') and key in viz.ANIMATIONS and col_idx < len(cols):
            info = viz.ANIMATIONS[key]
            with cols[col_idx]:
                if st.button(f"🎬 {info['title'][:15]}", key=f"rec_a_{key}"):
                    with st.spinner("🎬 生成动画中..."):
                        try:
                            gif_bytes = get_cached_animation(key)
                            if gif_bytes:
                                st.image(gif_bytes, caption=info["description"], use_container_width=True)
                        except Exception as e:
                            st.error(f"生成出错：{e}")
            col_idx += 1


def _clear_user_runtime_state():
    for key in [
        "messages",
        "question_history",
        "pending_images",
        "active_run",
        "needs_final_rerun",
        "queued_chat_request",
        "quick_question",
        "total_questions",
        "total_errors",
        "session_id",
    ]:
        st.session_state.pop(key, None)


def _welcome_message():
    return """👋 你好！我是**数学物理方法助教**，覆盖全部15章内容。

**已启用功能**：
- 📚 **知识库增强**：回答时自动检索课程知识库，提高准确性
- ⚡ **流式输出**：回答逐字显示，无需等待
- 🎨 **可视化推荐**：回答后自动推荐相关图形和动画

**上篇 · 复变函数论（第1-6章）**：解析函数、复积分、级数、留数、傅里叶/拉普拉斯变换

**下篇 · 数学物理方程（第7-15章）**：定解问题、分离变量法、特殊函数、格林函数、积分变换、保角变换、非线性问题

💡 输入框支持 LaTeX 公式，按 **Enter** 发送。"""


def _load_user_chat_history(user_id, limit=20):
    messages = [{"role": "assistant", "content": _welcome_message()}]
    if not DB_AVAILABLE or not user_id:
        return messages

    history = db.get_user_recent_interactions(user_id, limit=limit)
    if history:
        messages.append({
            "role": "assistant",
            "content": f"已为你恢复最近 {len(history)} 轮历史对话。"
        })
    for item in history:
        messages.append({"role": "user", "content": item.get("question", "")})
        messages.append({"role": "assistant", "content": item.get("answer", "")})
    return messages


def _current_user_id():
    user = st.session_state.get("current_user")
    return user.get("id") if user else None


def _user_history_download():
    """Build a user-scoped JSON export without exposing internal model metadata."""
    if not DB_AVAILABLE or not _current_user_id():
        return "[]"
    records = db.get_user_interactions(_current_user_id())
    return json.dumps(records, ensure_ascii=False, indent=2)


def _user_history_markdown_download():
    """Build a readable Markdown export for the current user's conversations."""
    if not DB_AVAILABLE or not _current_user_id():
        return "# 数学物理方法对话记录\n\n暂无对话记录。\n"
    records = db.get_user_interactions(_current_user_id())
    lines = ["# 数学物理方法对话记录", ""]
    if not records:
        lines.append("暂无对话记录。")
        return "\n".join(lines) + "\n"
    for index, record in enumerate(records, start=1):
        timestamp = record.get("timestamp", "")
        chapter = record.get("chapter") or "未分类"
        question = record.get("question", "").strip()
        answer = record.get("answer", "").strip()
        lines.extend([
            f"## {index}. {timestamp}",
            "",
            f"**章节：** {chapter}",
            "",
            "### 问题",
            "",
            question,
            "",
            "### 回答",
            "",
            answer,
            "",
            "---",
            "",
        ])
    return "\n".join(lines)


def _login_user(user):
    st.session_state.anonymous_mode = False
    st.session_state.current_user = user
    _clear_user_runtime_state()
    st.session_state.messages = _load_user_chat_history(user.get("id"))
    if DB_AVAILABLE:
        st.session_state.saved_interaction_count = db.get_user_interaction_count(user.get("id"))
    if DB_AVAILABLE:
        st.session_state.session_id = db.start_session(user.get("id"))
    st.rerun()


def _enter_anonymous_mode():
    st.session_state.current_user = None
    st.session_state.anonymous_mode = True
    _clear_user_runtime_state()
    if DB_AVAILABLE:
        st.session_state.session_id = db.start_session(None)
    st.rerun()


def _logout_user():
    st.session_state.pop("current_user", None)
    st.session_state.anonymous_mode = False
    _clear_user_runtime_state()
    st.rerun()


def _queue_quick_question(question):
    st.session_state.app_mode = "💬 聊天问答"
    st.session_state.quick_question = question
    st.session_state.quick_question_clean_switch = True


def _render_auth_page():
    st.markdown("""
    <div class="main-header">
        <h1>📐 数学物理方法助教</h1>
        <p>登录后开始学习，系统会记录你的本次学习进度。</p>
    </div>
    """, unsafe_allow_html=True)

    if not DB_AVAILABLE:
        st.error("用户系统暂不可用：数据库模块未加载。")
        return

    login_tab, register_tab = st.tabs(["登录", "注册"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("用户名", key="login_username")
            password = st.text_input("密码", type="password", key="login_password")
            submitted = st.form_submit_button("登录", type="primary")
        if submitted:
            user = db.authenticate_user(username, password)
            if user:
                _login_user(user)
            else:
                st.error("用户名或密码错误。")

        st.markdown("---")
        if st.button("匿名进入", key="enter_anonymous", help="不注册账号，直接开始本次学习。"):
            _enter_anonymous_mode()
        st.caption("匿名模式不会绑定个人账号；本次问答仍会作为匿名会话用于服务维护。")

    with register_tab:
        with st.form("register_form"):
            new_username = st.text_input("用户名", key="register_username", help="至少 3 个字符")
            display_name = st.text_input("显示名称", key="register_display_name")
            new_password = st.text_input("密码", type="password", key="register_password", help="至少 6 个字符")
            confirm_password = st.text_input("确认密码", type="password", key="register_confirm_password")
            submitted = st.form_submit_button("注册并登录", type="primary")
        if submitted:
            if new_password != confirm_password:
                st.error("两次输入的密码不一致。")
            else:
                try:
                    user = db.create_user(new_username, new_password, display_name)
                    _login_user(user)
                except ValueError as exc:
                    st.error(str(exc))


# ==================== 侧边栏 ====================
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "anonymous_mode" not in st.session_state:
    st.session_state.anonymous_mode = False
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "💬 聊天问答"

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-icon">📐</div>
            <div class="sidebar-brand-title">数学物理方法</div>
        </div>
        <div class="sidebar-brand-subtitle">AI 教学助手 · 15章全覆盖</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    current_user = st.session_state.get("current_user")
    if current_user:
        display_name = current_user.get("display_name") or current_user.get("username")
        st.markdown("👤 **当前用户**")
        st.markdown(f"<div class='sidebar-note'>{display_name}</div>", unsafe_allow_html=True)
        saved_count = st.session_state.get("saved_interaction_count")
        if saved_count is not None:
            st.markdown(f"<div class='sidebar-muted'>已保存 {saved_count} 条问答记录</div>", unsafe_allow_html=True)
        if st.button("隐藏当前历史", key="hide_loaded_history", help="只清空当前页面显示，不删除数据库记录。"):
            st.session_state.messages = [{"role": "assistant", "content": _welcome_message()}]
            st.rerun()
        if st.button("退出登录", key="logout_user"):
            _logout_user()
        st.markdown("---")
    elif st.session_state.get("anonymous_mode"):
        st.markdown("👤 **当前用户**")
        st.markdown("<div class='sidebar-note'>匿名使用</div>", unsafe_allow_html=True)
        if st.button("退出匿名模式", key="logout_anonymous"):
            _logout_user()
        st.markdown("---")

if not st.session_state.get("current_user") and not st.session_state.get("anonymous_mode"):
    _render_auth_page()
    st.stop()

if DB_AVAILABLE:
    db.touch_session(st.session_state.get("session_id"))
    active_user_count = db.get_active_session_count()
else:
    active_user_count = 0

with st.sidebar:
    if DB_AVAILABLE:
        st.markdown(f"<div class='sidebar-muted'>当前在线人数：{active_user_count}</div>", unsafe_allow_html=True)
        st.markdown("---")
    if st.session_state.get("current_user") and DB_AVAILABLE:
        st.download_button(
            "下载 JSON 对话记录",
            data=_user_history_download().encode("utf-8"),
            file_name="数学物理方法_对话记录.json",
            mime="application/json",
            key="download_user_history",
            help="下载当前登录账号保存的全部问答记录，适合数据备份。",
            use_container_width=True,
        )
        st.download_button(
            "下载 Markdown 对话记录",
            data=_user_history_markdown_download().encode("utf-8"),
            file_name="数学物理方法_对话记录.md",
            mime="text/markdown",
            key="download_user_history_markdown",
            help="下载适合阅读和编辑的 Markdown 格式对话记录。",
            use_container_width=True,
        )
        st.markdown("---")

    app_mode = st.radio(
        "🎛️ 模式",
        ["💬 聊天问答", "📊 可视化演示"],
        key="app_mode",
        help="切换聊天模式或可视化演示。"
    )

    st.markdown("---")

    st.markdown("📚 **使用说明**")
    st.markdown('<div class="sidebar-note">本Agent覆盖《数学物理方法》全部15章。知识库已内置，回答时自动检索相关内容。</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("📝 **快速提问**")

    quick_question_pool = [
        "判断 f(z)=z² 是否解析",
        "计算 ∮ e^z/(z-1) dz",
        "用留数定理计算 ∫dx/(1+x²)",
        "用分离变量法解弦振动方程",
        "验证勒让德方程是S-L型",
        "求上半平面→单位圆的保角变换",
        "解释柯西-黎曼条件的几何意义",
        "计算 z=0 处 sin z / z 的留数",
        "说明傅里叶变换和拉普拉斯变换的区别",
        "用傅里叶级数展开周期方波",
        "判断 u_t=a²u_xx 属于哪类方程",
        "写出达朗贝尔公式并解释物理意义",
        "用分离变量法求热传导方程的基本步骤",
        "说明 Sturm-Liouville 问题的正交性",
        "解释勒让德多项式的生成函数",
        "说明贝塞尔函数在圆域问题中的作用",
        "解释格林函数的物理含义",
        "用积分变换法求解偏微分方程的思路",
        "说明保角变换为什么保持角度",
        "举例说明非线性方程中的孤立波"
    ]

    if "quick_question_sample" not in st.session_state:
        st.session_state.quick_question_sample = random.sample(quick_question_pool, 6)

    if st.button("🔀 换一组", key="shuffle_quick_questions"):
        st.session_state.quick_question_sample = random.sample(quick_question_pool, 6)
        st.rerun()

    quick_questions = st.session_state.quick_question_sample

    for q in quick_questions:
        st.button(
            q,
            key=f"btn_{q}",
            on_click=_queue_quick_question,
            args=(q,),
        )

    st.markdown("---")

    # 学习追踪统计
    if "question_history" in st.session_state and st.session_state.question_history:
        st.markdown("📊 **本次学习统计**")
        history = st.session_state.question_history
        chapter_counts = {}
        for ch in history:
            chapter_counts[ch] = chapter_counts.get(ch, 0) + 1
        for ch, count in sorted(chapter_counts.items()):
            st.markdown(f"<div class='sidebar-note'>{ch}: {count} 题</div>", unsafe_allow_html=True)
        total_q = st.session_state.get("total_questions", len(history))
        total_e = st.session_state.get("total_errors", 0)
        st.markdown(f"<div class='sidebar-muted'>共 {total_q} 问 / {total_e} 错</div>", unsafe_allow_html=True)

# ==================== 聊天问答模式 ====================
if app_mode == "💬 聊天问答":
    st.markdown("""
    <div class="main-header">
        <h1>📐 数学物理方法助教</h1>
        <p>《数学物理方法》全课程 · 15章AI教学助手 · 知识库增强</p>
    </div>
    """, unsafe_allow_html=True)

    if "session_id" not in st.session_state:
        st.session_state.session_id = db.start_session(_current_user_id()) if DB_AVAILABLE else ""
    if "total_questions" not in st.session_state:
        st.session_state.total_questions = 0
    if "total_errors" not in st.session_state:
        st.session_state.total_errors = 0
    if "question_history" not in st.session_state:
        st.session_state.question_history = []
    if "pending_images" not in st.session_state:
        st.session_state.pending_images = []
    if "active_run" not in st.session_state:
        st.session_state.active_run = False
    if "needs_final_rerun" not in st.session_state:
        st.session_state.needs_final_rerun = False
    if "queued_chat_request" not in st.session_state:
        st.session_state.queued_chat_request = None

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": _welcome_message()
            }
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            _render_message(msg)
            if msg["role"] == "assistant":
                msg_key = f"msg_{abs(hash(msg.get('content', ''))) % 10_000_000}"
                _render_python_code_runner(msg.get("content", ""), msg_key)

    def _handle_question(prompt, image_data=None):
        if image_data:
            image_data = _normalize_image_data_url(image_data)

        actual_model = model
        actual_provider = provider
        using_vision = bool(image_data)
        vision_notice = ""

        if not api_key and not _local_fallback_available():
            user_msg = {"role": "user", "content": prompt}
            if image_data:
                user_msg["image_data"] = image_data
            st.session_state.messages.append(user_msg)
            st.session_state.messages.append({"role": "assistant", "content": "⚠️ 服务暂不可用，请稍后再试。"})
            st.rerun()

        user_msg = {"role": "user", "content": prompt}
        if image_data:
            user_msg["image_data"] = image_data
        st.session_state.messages.append(user_msg)

        # RAG: 检测章节
        detected_chapters = []
        rag_chunks_info = None
        if RAG_AVAILABLE:
            detected_chapters = rag.detect_chapters(prompt)
            for ch in detected_chapters:
                if "question_history" in st.session_state:
                    st.session_state.question_history.append(ch)
            rag_chunks_info = detected_chapters

        enhanced_prompt = build_system_prompt(prompt)
        recent = st.session_state.messages[-12:]

        chapter_str = ", ".join(detected_chapters) if detected_chapters else None
        answer = ""
        elapsed_ms = 0
        approx_in = 0
        approx_out = 0
        error_occurred = False
        error_info = None  # <-- 保存错误信息，避免在 except 块外引用 e

        with st.chat_message("assistant"):
            placeholder = st.empty()
            try:
                vision_summary = ""
                if image_data:
                    if not vision_api_key and not _local_fallback_available():
                        raise Exception("未配置图片理解服务密钥，请检查服务配置。")
                    vmodel, _ = _get_vision_model(vision_provider, vision_model)
                    if not vmodel and not _local_fallback_available():
                        raise Exception("尚未配置可用的图片理解服务。")

                    with st.status("正在识别图片内容...", expanded=True) as status:
                        _render_thinking_banner("正在读取图片、转写公式与题干")
                        vision_messages = [
                            {
                                "role": "system",
                                "content": "你是数学物理课程图片信息提取助手，只做图片转写、OCR 和视觉描述。"
                            },
                            {
                                "role": "user",
                                "content": _build_mm_content(
                                    build_vision_extraction_prompt(prompt),
                                    image_data,
                                    vision_provider
                                )
                            }
                        ]
                        vision_summary, used_vision_model = call_vision_llm(
                            vision_provider, vision_model, vision_messages, vision_api_key
                        )
                        status.update(label="图片识别完成", state="complete", expanded=False)
                    placeholder.markdown("图片识别已完成，正在组织答案...")

                api_messages = [{"role": "system", "content": enhanced_prompt}]
                for m in recent:
                    if m.get("image_data"):
                        text_content = m["content"]
                        if m is recent[-1] and vision_summary:
                            text_content += (
                                "\n\n【图片识别结果，仅作为图像内容上下文】\n"
                                f"{vision_summary}\n\n"
                                "请基于以上图片识别结果和用户问题进行数学物理推理与解答。"
                            )
                        else:
                            text_content += "\n\n【说明】这条历史消息包含图片，图片内容已在当前轮上下文中转写或省略。"
                        api_messages.append({"role": m["role"], "content": text_content})
                    else:
                        api_messages.append({"role": m["role"], "content": m["content"]})

                _render_thinking_banner("正在推理并组织答案")
                answer, elapsed_ms, approx_in, approx_out = call_llm_streaming(
                    actual_provider, actual_model, api_messages, api_key, placeholder
                )

                if vision_summary:
                    answer = (
                        "### 图片识别结果\n\n"
                        f"{vision_summary}\n\n"
                        "---\n\n"
                        f"{answer}"
                    )
                    answer = _normalize_math_markdown(answer)
                    placeholder.markdown(answer)

                st.session_state.messages.append({"role": "assistant", "content": answer})
                _render_python_code_runner(answer, f"latest_{len(st.session_state.messages)}")

                if RAG_AVAILABLE and VIZ_AVAILABLE:
                    recs = rag.get_viz_recommendations(prompt)
                    if recs["static"] or recs["anim"]:
                        _show_viz_recommend(recs)

                # ====== 反馈按钮 ======
                feedback_key = f"fb_{len(st.session_state.messages)}"
                col1, col2, col3 = st.columns([1, 1, 4])
                with col1:
                    if st.button("👍", key=f"{feedback_key}_good", help="回答有帮助"):
                        if DB_AVAILABLE:
                            db.log_feedback(None, st.session_state.session_id, "good", "", user_id=_current_user_id())
                        st.toast("感谢反馈！👍")
                with col2:
                    if st.button("👎", key=f"{feedback_key}_bad", help="回答有问题"):
                        if DB_AVAILABLE:
                            db.log_feedback(None, st.session_state.session_id, "bad", "", user_id=_current_user_id())
                        st.toast("已记录，我们会改进！")

            except Exception as e:
                error_occurred = True
                error_info = str(e)
                err_msg = f"❌ 出错了：{error_info}\n\n请检查：\n1. 网络连接是否正常\n2. 服务配置是否正确\n3. API 余额是否充足"
                
                # 图片分析特殊提示
                if actual_provider == "deepseek" and using_vision and "deepseek-vl" in actual_model:
                    err_msg += (
                        "\n\n💡 图片理解服务提示：\n"
                        "- 请确认服务密钥有图片理解调用权限\n"
                        "- 如仍失败，请检查后台视觉服务配置"
                    )
                
                placeholder.markdown(_normalize_math_markdown(err_msg))
                answer = err_msg
                st.session_state.messages.append({"role": "assistant", "content": err_msg})

                if DB_AVAILABLE:
                    db.log_error(
                        st.session_state.session_id, prompt,
                        type(e).__name__, error_info,
                        traceback.format_exc(),
                        user_id=_current_user_id()
                    )

        # ====== 记录到数据库 ======
        if DB_AVAILABLE:
            db.log_interaction(
                session_id=st.session_state.session_id,
                question=prompt,
                answer=answer,
                chapter=chapter_str,
                provider=provider,
                model=model,
                tokens_input=approx_in,
                tokens_output=approx_out,
                response_time_ms=elapsed_ms,
                error=error_info,  # <-- 使用 error_info 代替 str(e)
                rag_chunks=rag_chunks_info,
                user_id=_current_user_id()
            )
            if _current_user_id():
                st.session_state.saved_interaction_count = db.get_user_interaction_count(_current_user_id())

        if error_occurred:
            st.session_state.total_errors = st.session_state.get("total_errors", 0) + 1
        st.session_state.total_questions = st.session_state.get("total_questions", 0) + 1
        st.session_state.active_run = False
        st.session_state.needs_final_rerun = True

    defer_quick_question = False
    if st.session_state.pop("quick_question_clean_switch", False):
        st.session_state.quick_question_deferred = st.session_state.get("quick_question")
        st.session_state.quick_question = None
        defer_quick_question = True

    if "quick_question" in st.session_state and st.session_state.quick_question:
        prompt = st.session_state.quick_question
        st.session_state.quick_question = None
        _handle_question(prompt)

    if st.session_state.queued_chat_request:
        queued = st.session_state.queued_chat_request
        st.session_state.queued_chat_request = None
        st.session_state.active_run = True
        _handle_question(queued["prompt"], image_data=queued.get("image_data"))

    if st.session_state.needs_final_rerun:
        st.session_state.needs_final_rerun = False
        st.rerun()

    # ====== 聊天输入区域（支持图像输入） ======
    st.markdown("---")

    vmodel_for_ui, _ = _get_vision_model(vision_provider, vision_model)
    vision_ui_name = _provider_display_name(vision_provider)

    with st.container():
        # 模型能力提示
        if vmodel_for_ui:
            st.info("📷 上传图片后：系统会先理解图片内容，再结合课程知识进行文字推理。")
        else:
            st.warning("⚠️ 视觉模型配置尚未生效。请检查 `vision_provider`、`vision_model` 和 `vision_api_key`。")

        # 图片上传区（拖放 + 点击）
        uploaded_files = st.file_uploader(
            "📎 拖放或点击添加图片",
            type=["jpg", "jpeg", "png", "gif", "webp", "bmp"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="chat_image_uploader"
        )

        # 处理新上传的图片
        if uploaded_files:
            normalized_images = []
            for uf in uploaded_files:
                file_bytes = uf.getvalue()
                if not file_bytes:
                    continue
                mime_type = uf.type or "image/jpeg"
                try:
                    data_url = _encode_image(file_bytes, mime_type)
                except ValueError as exc:
                    st.warning(f"{uf.name}：{exc}")
                    continue
                normalized_images.append({
                    "name": uf.name,
                    "data_url": data_url,
                    "mime_type": "image/png",
                    "bytes": len(data_url)
                })
            # Match the current uploader state exactly; do not keep stale session images.
            st.session_state.pending_images = normalized_images

        # 显示已选图片缩略图（可删除 + 发送按钮）
        if st.session_state.pending_images and not st.session_state.active_run:
            n_imgs = len(st.session_state.pending_images)
            n_cols = min(n_imgs + 2, 6)  # 图片 + 数量提示 + 发送按钮

            cols = st.columns(n_cols)
            for i, img in enumerate(st.session_state.pending_images):
                with cols[i % n_cols]:
                    st.image(img["data_url"], use_container_width=True)
                    st.caption(f"{img.get('mime_type', 'image/png')} · {img.get('bytes', len(img.get('data_url', '')))//1024} KB")
                    if st.button("❌", key=f"del_img_{i}", help=f"移除 {img['name']}"):
                        st.session_state.pending_images.pop(i)
                        st.rerun()

            # 数量提示放在最后一个图片后的列
            with cols[min(n_imgs, n_cols - 2)]:
                st.caption(f"共 {n_imgs} 张")

            # 发送按钮放在最后一列（如果列数足够）
            if n_cols > n_imgs:
                with cols[-1]:
                    if st.button("🚀 分析图片", key="send_image_only", type="primary", help="直接发送图片给模型分析，无需输入文字"):
                        default_prompt = (
                            "请详细分析图片中的内容。如果图片包含数学/物理问题，请给出完整的解答步骤、"
                            "公式推导和最终答案。如果图片包含图形或公式，请解释其含义。"
                        )
                        image_data = st.session_state.pending_images[0]["data_url"]
                        selected_images = list(st.session_state.pending_images)
                        st.session_state.pending_images = []
                        st.session_state.active_run = True
                        if len(selected_images) > 1:
                            other_names = ", ".join([p["name"] for p in selected_images[1:]])
                            default_prompt += f"\n\n（同时上传了其他图片: {other_names}）"
                        if not vmodel_for_ui:
                            default_prompt += (
                                f"\n\n[系统提示: 用户上传了图片 `{selected_images[0]['name']}`，"
                                f"但当前模型不支持图片分析。请根据常识推断图片可能的内容并回答。]"
                            )
                        st.session_state.queued_chat_request = {
                            "prompt": default_prompt,
                            "image_data": image_data,
                        }
                        st.rerun()

    # 文字输入框
    placeholder_text = (
        "输入问题，或直接粘贴/拖入图片后按 Enter..."
        if not st.session_state.pending_images
        else "输入你的问题，或点击上方【分析图片】按钮..."
    )

    chat_value = st.chat_input(
        placeholder_text,
        accept_file="multiple",
        file_type=["jpg", "jpeg", "png", "gif", "webp", "bmp"],
        key="chat_input_with_images",
    )

    if chat_value:
        pasted_files = []
        if isinstance(chat_value, str):
            prompt = chat_value
        else:
            prompt = _chat_value_field(chat_value, "text", "") or ""
            pasted_files = _chat_value_field(chat_value, "files", []) or []

        image_data = None
        pasted_images = []
        for pf in pasted_files:
            file_bytes = pf.getvalue()
            if not file_bytes:
                continue
            try:
                data_url = _encode_image(file_bytes, getattr(pf, "type", "image/png") or "image/png")
            except ValueError as exc:
                st.warning(f"{getattr(pf, 'name', '图片')}：{exc}")
                continue
            pasted_images.append({
                "name": getattr(pf, "name", "pasted-image.png"),
                "data_url": data_url,
                "mime_type": "image/png",
                "bytes": len(data_url),
            })

        if pasted_images:
            image_data = pasted_images[0]["data_url"]
            selected_images = pasted_images
            st.session_state.pending_images = []
            st.session_state.active_run = True
            if not prompt:
                prompt = (
                    "请详细分析图片中的内容。如果图片包含数学/物理问题，请给出完整的解答步骤、"
                    "公式推导和最终答案。如果图片包含图形或公式，请解释其含义。"
                )
            if len(selected_images) > 1:
                other_names = ", ".join([p["name"] for p in selected_images[1:]])
                prompt += f"\n\n（同时粘贴/上传了其他图片: {other_names}）"
            if not vmodel_for_ui:
                prompt += (
                    f"\n\n[系统提示: 用户上传了图片 `{selected_images[0]['name']}`，"
                    f"但当前模型不支持图片分析。请根据文字描述回答。]"
                )
        if st.session_state.pending_images:
            image_data = st.session_state.pending_images[0]["data_url"]
            selected_images = list(st.session_state.pending_images)
            st.session_state.pending_images = []
            st.session_state.active_run = True
            if len(selected_images) > 1:
                other_names = ", ".join([p["name"] for p in selected_images[1:]])
                prompt += f"\n\n（同时上传了其他图片: {other_names}）"
            if not vmodel_for_ui:
                prompt += (
                    f"\n\n[系统提示: 用户上传了图片 `{selected_images[0]['name']}`，"
                    f"但当前模型不支持图片分析。请根据文字描述回答。]"
                )
        elif not pasted_images:
            st.session_state.active_run = True

        st.session_state.queued_chat_request = {
            "prompt": prompt,
            "image_data": image_data,
        }
        st.rerun()

    if defer_quick_question:
        st.session_state.quick_question = st.session_state.pop("quick_question_deferred", None)
        st.rerun()

# ==================== 可视化演示模式 ====================
elif app_mode == "📊 可视化演示":
    st.markdown("""
    <div class="main-header">
        <h1>📊 数学物理方法可视化</h1>
        <p>全部15章图形演示 · 直观理解抽象概念</p>
    </div>
    """, unsafe_allow_html=True)

    if not VIZ_AVAILABLE:
        st.warning("⚠️ 可视化模块未加载。请确保已安装 matplotlib、numpy、scipy")
    else:
        st.info("📌 点击下方按钮生成对应的可视化图像。")

        chapter_groups = {
            "📘 上篇 · 复变函数论": {
                "第1章 复变函数": [
                    "z_squared_mapping", "z_cubed_mapping", "exp_mapping",
                    "harmonic_z2", "harmonic_exp", "complex_exp", "complex_sine",
                    "cr_geometry", "conformal_angle",
                    "anim_cr_grad", "anim_mapping", "anim_log_branches", "anim_sine"
                ],
                "第2章 复变函数的积分": [
                    "cauchy_path", "cauchy_integral_formula",
                    "anim_path_def", "anim_cauchy_formula"
                ],
                "第3章 幂级数展开": [
                    "taylor_convergence", "laurent_annulus",
                    "anim_taylor", "anim_laurent"
                ],
                "第4章 留数定理": [
                    "residue_contour",
                    "anim_residue"
                ],
                "第5章 傅里叶变换": [
                    "fourier_spectrum",
                    "anim_fourier_sq", "anim_fourier_dual"
                ],
                "第6章 拉普拉斯变换": [
                    "laplace_poles",
                    "anim_laplace"
                ],
            },
            "📗 下篇 · 数学物理方程": {
                "第7章 定解问题": [
                    "pde_classification", "dalembert_formula",
                    "anim_dalembert", "anim_pde_types"
                ],
                "第8章 分离变数法": [
                    "separation_modes", "heat_evolution",
                    "anim_separation", "anim_heat"
                ],
                "第9章 S-L方程": [
                    "sl_eigenfunctions", "sl_orthogonality",
                    "anim_sl_overlay", "anim_sl_ortho"
                ],
                "第10章 球函数": [
                    "legendre_polynomials", "spherical_harmonics",
                    "anim_legendre", "anim_spherical"
                ],
                "第11章 柱函数": [
                    "bessel_functions", "bessel_zeros",
                    "anim_bessel", "anim_drum"
                ],
                "第12章 格林函数": [
                    "green_function_1d", "green_superposition",
                    "anim_green"
                ],
                "第13章 积分变换法": [
                    "heat_kernel_diffusion",
                    "anim_kernel", "anim_fourier_pde"
                ],
                "第14章 保角变换": [
                    "conformal_examples",
                    "anim_conformal"
                ],
                "第15章 非线性问题": [
                    "kdv_soliton",
                    "anim_kdv", "anim_lorenz"
                ],
            }
        }

        for section_name, chapters in chapter_groups.items():
            st.markdown("---")
            st.header(section_name)

            cols = st.columns(2)
            col_idx = 0

            for chapter_title, keys in chapters.items():
                with cols[col_idx % 2]:
                    with st.expander(f"**{chapter_title}**", expanded=False):
                        for key in keys:
                            # 优先从 VISUALIZATIONS 查找
                            info = viz.VISUALIZATIONS.get(key)
                            source = "viz"
                            if not info and hasattr(viz, 'ANIMATIONS'):
                                info = viz.ANIMATIONS.get(key)
                                source = "anim"
                            if not info:
                                continue

                            viz_type = info.get("type", "static")
                            is_anim = viz_type == "animation" or source == "anim"
                            btn_icon = "🎬" if is_anim else "▶"
                            if st.button(f"{btn_icon} {info['title']}", key=f"viz_{key}"):
                                with st.spinner("🎨 正在生成..."):
                                    try:
                                        if source == "anim":
                                            gif_bytes = get_cached_animation(key)
                                            if gif_bytes:
                                                st.image(gif_bytes, caption=info["description"], use_container_width=True)
                                        else:
                                            result = info["function"]()
                                            if is_anim:
                                                st.image(result, caption=info["description"], use_container_width=True)
                                            else:
                                                st.pyplot(result)
                                                st.caption(info["description"])
                                    except Exception as e:
                                        st.error(f"生成出错：{e}")
                col_idx += 1

        _render_application_videos()

        st.markdown("---")
        st.markdown("""
        💡 **使用提示**：
        - 点击 🎬 按钮生成动态 GIF 动画，点击 ▶ 按钮生成静态图像
        - 在“应用实例视频”中选择 mp4，可直接播放课程应用案例
        - 动画首次生成需 5-10 秒，之后自动缓存秒开
        - 可以截图保存到课件中作为教学素材
        """)

# ==================== 数据分析仪表板 ====================
else:
    st.markdown("""
    <div class="main-header">
        <h1>📈 数据分析仪表板</h1>
        <p>问答日志 · 错误追踪 · 章节统计 · 用于Agent迭代升级</p>
    </div>
    """, unsafe_allow_html=True)

    if not DB_AVAILABLE:
        st.warning("⚠️ 数据库模块未加载。")
    else:
        # 总体统计
        stats = db.get_total_stats()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总提问数", stats["total_questions"])
        with col2:
            st.metric("错误数", stats["total_errors"], delta="-" + stats["error_rate"], delta_color="inverse")
        with col3:
            st.metric("总Input Tokens", f"{stats['total_input_tokens']:,}")
        with col4:
            st.metric("总Sessions", stats["total_sessions"])

        st.markdown("---")

        # 章节统计
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("📚 各章节提问分布")
            chapter_stats = db.get_chapter_stats()
            if chapter_stats:
                for cs in chapter_stats:
                    ch = cs["chapter"] or "未分类"
                    cnt = cs["cnt"]
                    st.markdown(f"**{ch}**: {cnt} 题 | input={cs['ti']:,} output={cs['to_tokens']:,}")
            else:
                st.info("暂无数据")

        with col_right:
            st.subheader("📅 每日用量")
            daily = db.get_daily_stats()
            if daily:
                for d in daily[:14]:
                    st.markdown(f"**{d['day']}**: {d['questions']} 题 | in={d['ti']:,} out={d['to_tokens']:,}")

            st.subheader("💬 反馈统计")
            fb_stats = db.get_feedback_stats()
            if fb_stats:
                for fs in fb_stats:
                    icon = "👍" if fs["rating"] == "good" else "👎"
                    st.markdown(f"{icon} {fs['rating']}: {fs['cnt']} 次")
            else:
                st.info("暂无反馈")

        st.markdown("---")

        # 最近错误
        st.subheader("🚨 最近错误记录")
        errors = db.get_recent_errors(15)
        if errors:
            for e in errors:
                with st.expander(f"{e['timestamp'][:19]} | {e['error_type']}: {e['error_message'][:80]}", expanded=False):
                    st.caption(f"提问: {e['question'][:200]}")
                    st.code(e.get("traceback", "")[:500] if "traceback" in e else "")
        else:
            st.success("🎉 暂无错误记录！")

        st.markdown("---")

        # 未回答成功的问题
        st.subheader("❓ 未成功回答的问题")
        unanswered = db.get_unanswered_questions()
        if unanswered:
            for u in unanswered[:20]:
                ch = u.get("chapter", "")
                st.markdown(f"- [{ch}] {u['question'][:100]}")
                st.caption(f"  错误: {u['error'][:120]}  |  {u['timestamp'][:19]}")
        else:
            st.success("全部问题均已成功回答！")

        st.markdown("---")
        st.caption("💡 以上数据存储在 `agent_logs.db` 中，可用于分析薄弱环节、改进系统提示词、补充知识库。")
