import matplotlib
matplotlib.use('Agg', force=True)

import os
import matplotlib.pyplot as plt

# 绝对路径列表
files = {
    "app.py": r"E:\agent\agent of mmp\deploy\app.py",
    "db.py": r"E:\agent\agent of mmp\deploy\db.py",
    "admin_api.py": r"E:\agent\agent of mmp\deploy\admin_api.py",
    "requirements.txt": r"E:\agent\agent of mmp\deploy\requirements.txt",
}

# 读取每个文件的前500个字符
def read_head(abs_path, n=500):
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            return f.read(n)
    except Exception as e:
        return f"读取失败: {e}"

contents = {}
for name, path in files.items():
    contents[name] = read_head(path, 500)

# 构建文本
text = ""
for name in ["app.py", "db.py", "admin_api.py", "requirements.txt"]:
    text += f"\n{'='*60}\n{name} (前500字符):\n{contents[name]}\n"

# 绘图
fig, ax = plt.subplots(figsize=(24, 16))
ax.axis('off')
ax.text(0.02, 0.98, text, transform=ax.transAxes,
        fontsize=18, fontfamily='monospace',
        verticalalignment='top', horizontalalignment='left',
        linespacing=1.3,
        bbox=dict(facecolor='white', alpha=0.9, edgecolor='gray'))

plt.savefig("absolute_files.png", dpi=350, bbox_inches='tight', pad_inches=0.3)
plt.close()


# ---- auto-capture matplotlib outputs for the teaching agent ----
try:
    import matplotlib
    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt
    from matplotlib.animation import Animation

    saved_any = False
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
                _fig.savefig(f"figure_{_idx}.png", dpi=150, bbox_inches="tight")
                saved_any = True
            except Exception as _fig_exc:
                print(f"[auto-capture-warning] figure save failed: {_fig_exc}")
except Exception as _capture_exc:
    print(f"[auto-capture-warning] {_capture_exc}")
