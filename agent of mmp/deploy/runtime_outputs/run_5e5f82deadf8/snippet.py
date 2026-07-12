import matplotlib
matplotlib.use('Agg', force=True)

import subprocess
import matplotlib.pyplot as plt
import os

# ---------- 中文字体设置 ----------
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ---------- 获取环境变量 ----------
def get_env_vars():
    """
    执行 'set' 命令获取全部环境变量（Windows）。
    如果在 Linux/macOS 上运行，请将命令改为 'env'。
    """
    try:
        # Windows 下使用 'set'，shell=True 确保内部命令被执行
        result = subprocess.run(
            'set',
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout
        else:
            return f"命令执行失败，返回码: {result.returncode}\n{result.stderr}"
    except FileNotFoundError:
        return "错误: 找不到 shell 命令（可能需要将 'set' 改为 'env' 用于 Linux/macOS）"
    except Exception as e:
        return f"执行异常: {e}"

env_text = get_env_vars()

# ---------- 统计行数（用于画布自适应）----------
num_lines = env_text.count('\n') + 1
# 估算所需画布高度（英寸），字体越小行数越多
# 字体大小选择 5，每行高度约 5/72 英寸，预留一些边距
font_size = 5
line_height_inch = font_size / 72 * 1.2  # 1.2倍行距
min_height_inch = num_lines * line_height_inch + 1  # +1 英寸用于标题和边距
fig_height = max(12, min_height_inch)  # 至少 12 英寸高
fig_width = 14

# ---------- 创建画布 ----------
fig, ax = plt.subplots(figsize=(fig_width, fig_height))
ax.set_xlim(0, fig_width)
ax.set_ylim(0, fig_height)
ax.axis('off')

# 标题
title = "全部环境变量 (Windows 'set' 命令输出)"
ax.text(fig_width/2, fig_height - 0.5, title, fontsize=14, ha='center',
        fontweight='bold', family='sans-serif')

# 显示环境变量文本
# 使用等宽字体、小字号，并开启自动换行
ax.text(
    0.5, fig_height - 1,        # 起始位置 (x, y)，左边留 0.5 英寸边距
    env_text,
    fontsize=font_size,
    verticalalignment='top',
    family='monospace',
    wrap=True,
    linespacing=1.2
)

# 如果文本太长，可能会超出底部，但 matplotlib 会自动裁剪，我们在底部加提示
tip = (f"共 {num_lines} 行。若底部文字被裁剪，可增大 fig_height 或减小字体。\n"
       f"查找 PATH 变量以确认 ffmpeg 目录是否在搜索路径中。")
ax.text(fig_width/2, 0.2, tip, fontsize=10, ha='center', color='darkred', wrap=True)

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
