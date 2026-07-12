"""图片处理模块：编码为 base64，供 vision-capable 模型使用"""
import base64
import io
from PIL import Image


def encode_image(uploaded_file) -> dict:
    """将 Streamlit 上传的图片转为 base64 data URL"""
    img = Image.open(uploaded_file)
    # 如果太大则缩放
    max_size = 2048
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    fmt = img.format or "PNG"
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    b64_data = base64.b64encode(buf.read()).decode("utf-8")
    mime = f"image/{fmt.lower()}"
    return {
        "base64": b64_data,
        "mime": mime,
        "width": img.size[0],
        "height": img.size[1],
        "data_url": f"data:{mime};base64,{b64_data}"
    }


def build_messages_with_image(system_prompt: str, history: list, user_question: str, image_data_url: str) -> list:
    """构建包含图片的多模态 messages"""
    messages = [{"role": "system", "content": system_prompt}]

    for m in history:
        messages.append({"role": m["role"], "content": m["content"]})

    # 用户消息：文本 + 图片
    user_content = [
        {"type": "text", "text": user_question or "请分析这张图片的内容"},
        {"type": "image_url", "image_url": {"url": image_data_url}}
    ]
    messages.append({"role": "user", "content": user_content})

    return messages


def send_vision_request(provider: str, model: str, messages: list, api_key: str) -> str:
    """发送多模态请求到支持 vision 的 API"""
    import requests, json

    providers = {
        "deepseek": {
            "url": "https://api.deepseek.com/v1/chat/completions",
            "resp_path": ["choices", 0, "message", "content"]
        },
        "dashscope": {
            "url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
            "resp_path": ["output", "choices", 0, "message", "content"]
        }
    }

    cfg = providers.get(provider, providers["deepseek"])
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    if provider == "dashscope":
        payload = {
            "model": model.replace("qwen-plus", "qwen-vl-plus").replace("qwen-max", "qwen-vl-max"),
            "input": {"messages": messages},
            "parameters": {"temperature": 0.3, "max_tokens": 2048}
        }
    else:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 2048
        }

    resp = requests.post(cfg["url"], headers=headers, json=payload, timeout=60)
    data = resp.json()

    if resp.status_code != 200:
        err = data.get("error", {}).get("message", data.get("message", f"HTTP {resp.status_code}"))
        if "vision" not in str(err).lower() and "image" not in str(err).lower():
            raise Exception(err)
        raise Exception(f"当前模型不支持视觉输入。请尝试切换到VL模型或使用文本提问。\n({err})")

    path = cfg["resp_path"]
    result = data
    for key in path:
        result = result[key]
    return result
