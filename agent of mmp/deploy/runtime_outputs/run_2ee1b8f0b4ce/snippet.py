import matplotlib
matplotlib.use('Agg', force=True)

import platform
import matplotlib.pyplot as plt
import os

# ---------- 中文字体设置（避免方框）----------
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ---------- 获取系统信息 ----------
os_name = platform.system()                  # 操作系统名称，如 'Windows', 'Linux', 'Darwin'
processor = platform.processor()             # 处理器架构，如 'Intel64 Family 6 Model ...' 或 'ARM'
python_ver = platform.python_version()       # Python 版本号（x.y.z 格式，不含日期）

# 如果是 macOS 且 processor 返回空，可以用 platform.machine() 作为补充
if not processor:
    processor = platform.machine()           # 如 'arm64', 'x86_64'

# 路径分隔符示例（已内置在 os.sep 中）
path_sep = os.sep                           # Windows 下为 '\'，Linux/macOS 下为 '/'

# ---------- 创建画布 ----------
fig, ax = plt.subplots(figsize=(10, 4))
ax.set_xlim(0, 10)
ax.set_ylim(0, 4)
ax.axis('off')  # 隐藏坐标轴

# 主体信息
info_text = (
    f"操作系统: {os_name}\n"
    f"处理器/架构: {processor}\n"
    f"Python 版本: {python_ver}\n"
    f"当前平台路径分隔符: {repr(path_sep)}"
)
ax.text(0.5, 3.5, info_text, fontsize=12, verticalalignment='top',
        family='monospace', wrap=True)

# 补充说明
note = (f"注意: platform.processor() 在某些平台可能返回空字符串，"
        f"此时已替换为 platform.machine() 的值 ({platform.machine()}) "
        f"以确保信息完整。")
ax.text(0.5, 1.5, note, fontsize=10, verticalalignment='top',
        color='gray', wrap=True)

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
