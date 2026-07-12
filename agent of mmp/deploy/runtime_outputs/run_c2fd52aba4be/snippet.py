import matplotlib
matplotlib.use('Agg', force=True)

import sys
import matplotlib.pyplot as plt
import matplotlib

# ---------- 尝试解决中文显示为方框 ----------
# 1. 优先使用系统自带的黑体/雅黑，若没有则 fallback 到 sans-serif
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
# 2. 解决负号 '-' 显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False

# ---------- 获取系统信息 ----------
exec_path = sys.executable        # Python 解释器的完整路径
prefix = sys.prefix               # Python 安装的前缀目录
version = sys.version             # Python 版本号字符串
font_cache_dir = matplotlib.get_cachedir()  # matplotlib 字体缓存目录

# ---------- 创建画布并绘制文本 ----------
fig, ax = plt.subplots(figsize=(10, 4))
ax.set_xlim(0, 10)
ax.set_ylim(0, 4)
ax.axis('off')   # 隐藏坐标轴，简洁截图

# 主体信息（解释器路径、前缀、版本）
info_text = (
    f"Python 解释器路径: {exec_path}\n"
    f"安装前缀: {prefix}\n"
    f"Python 版本: {version}"
)
ax.text(0.5, 3.5, info_text, fontsize=12, verticalalignment='top',
        family='monospace', wrap=True)

# 补充信息（字体缓存位置 + 诊断提示）
cache_text = f"Matplotlib 字体缓存目录: {font_cache_dir}"
ax.text(0.5, 2.0, cache_text, fontsize=12, verticalalignment='top',
        family='monospace', wrap=True)

warning_text = "⚠ 若上方中文仍显示为方框，请检查上述缓存目录或安装中文字体"
ax.text(0.5, 1.0, warning_text, fontsize=12, verticalalignment='top',
        color='red', wrap=True)

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
