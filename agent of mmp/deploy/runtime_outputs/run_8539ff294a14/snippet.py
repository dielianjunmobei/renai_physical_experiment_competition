import matplotlib
matplotlib.use('Agg', force=True)

import subprocess
import matplotlib.pyplot as plt

# ---------- 中文字体设置 ----------
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ---------- 检查 ffmpeg ----------
def check_ffmpeg():
    """尝试运行 ffmpeg -version，返回 (是否存在, 文本信息)"""
    try:
        # 执行命令，捕获输出，超时 10 秒防止卡死
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        # 如果返回码为 0，说明存在
        if result.returncode == 0:
            # 提取输出文本，取前 3 行
            lines = result.stdout.strip().split('\n')[:3]
            # 每行可能很长，适当截断避免超出画布
            info = '\n'.join(line[:100] for line in lines)
            return True, info
        else:
            return False, f"ffmpeg returned code {result.returncode}"
    except FileNotFoundError:
        # 命令根本不存在
        return False, "ffmpeg not found (FileNotFoundError)"
    except Exception as e:
        return False, f"ffmpeg check failed: {e}"

exists, message = check_ffmpeg()

# ---------- 创建画布 ----------
fig, ax = plt.subplots(figsize=(12, 6))
ax.set_xlim(0, 12)
ax.set_ylim(0, 6)
ax.axis('off')

# 标题
ax.text(6, 5.5, "FFmpeg 检测结果", fontsize=16, ha='center',
        fontweight='bold', family='sans-serif')

# 状态指示
status_text = "✅ 已安装" if exists else "❌ 未安装"
ax.text(6, 5.0, status_text, fontsize=14, ha='center',
        color='green' if exists else 'red', family='sans-serif')

# 详细信息（版本或错误）
# 用等宽字体确保对齐
ax.text(1, 4.0, message, fontsize=12, verticalalignment='top',
        family='monospace', wrap=True, bbox=dict(facecolor='lightgrey', alpha=0.5))

# 补充提示
if not exists:
    tip = ("提示：请安装 ffmpeg 并确保其在系统 PATH 中。\n"
           "Ubuntu/Debian: sudo apt install ffmpeg\n"
           "macOS: brew install ffmpeg\n"
           "Windows: 下载后添加到环境变量")
    ax.text(1, 1.5, tip, fontsize=11, verticalalignment='top',
            color='darkblue', bbox=dict(facecolor='lightyellow', alpha=0.8))

plt.tight_layout()
plt.show()


# ---- auto-capture matplotlib outputs for the teaching agent ----
try:
    import matplotlib
    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt
    from matplotlib.animation import Animation

    saved_any = False
    import os as _os
    _existing_anim = any(
        _name.lower().endswith((".gif", ".mp4", ".webm"))
        for _name in _os.listdir(".")
    )
    if not _existing_anim:
        for _name, _value in list(globals().items()):
            if isinstance(_value, Animation):
                try:
                    _value.save("animation.gif", writer="pillow", fps=20)
                    saved_any = True
                except Exception as _anim_exc:
                    print(f"[auto-capture-warning] animation save failed: {_anim_exc}")
                break

    if plt.get_fignums():
        for _idx, _fig_num in enumerate(plt.get_fignums(), start=1):
            try:
                _fig = plt.figure(_fig_num)
                _width, _height = _fig.get_size_inches()
                _dpi = 150
                _pixels = max(_width * _dpi, 1) * max(_height * _dpi, 1)
                if _pixels > 40_000_000:
                    _scale = (40_000_000 / _pixels) ** 0.5
                    _dpi = max(30, int(_dpi * _scale))
                    print(f"[auto-capture-warning] figure too large; saving at dpi={_dpi}")
                _fig.savefig(f"figure_{_idx}.png", dpi=_dpi, bbox_inches="tight")
                saved_any = True
            except Exception as _fig_exc:
                print(f"[auto-capture-warning] figure save failed: {_fig_exc}")
except Exception as _capture_exc:
    print(f"[auto-capture-warning] {_capture_exc}")
