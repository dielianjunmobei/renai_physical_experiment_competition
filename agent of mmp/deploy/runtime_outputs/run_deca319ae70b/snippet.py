import matplotlib
matplotlib.use('Agg', force=True)

import os
import matplotlib.pyplot as plt

# 路径信息
cwd = os.getcwd()
parent_dir = os.path.dirname(cwd)
grandparent_dir = os.path.dirname(parent_dir)

# 父目录内容
try:
    parent_contents = os.listdir(parent_dir)
except PermissionError:
    parent_contents = ["Permission denied"]

parent_list_str = "\n".join(parent_contents)
if not parent_contents:
    parent_list_str = "(empty)"

# 祖父目录内容
try:
    grandparent_contents = os.listdir(grandparent_dir)
except PermissionError:
    grandparent_contents = ["Permission denied"]

grandparent_list_str = "\n".join(grandparent_contents)
if not grandparent_contents:
    grandparent_list_str = "(empty)"

# 读取 snippet.py 的前200字符
snippet_path = os.path.join(cwd, "snippet.py")
try:
    with open(snippet_path, "r", encoding="utf-8") as f:
        snippet_text = f.read(200)
except FileNotFoundError:
    snippet_text = "[snippet.py not found]"
except Exception as e:
    snippet_text = f"[Error reading snippet.py: {e}]"

# 构建完整文本
text_lines = [
    f"Current working directory:",
    f"  {cwd}",
    "",
    f"Parent directory:",
    f"  {parent_dir}",
    f"Contents:",
    f"{parent_list_str}",
    "",
    f"Grandparent directory:",
    f"  {grandparent_dir}",
    f"Contents:",
    f"{grandparent_list_str}",
    "",
    f"snippet.py (first 200 chars):",
    f"{snippet_text}"
]
full_text = "\n".join(text_lines)

# 绘图
fig, ax = plt.subplots(figsize=(18, 12))
ax.axis('off')

ax.text(
    0.02, 0.98,
    full_text,
    transform=ax.transAxes,
    fontsize=18,
    fontfamily='monospace',
    verticalalignment='top',
    horizontalalignment='left',
    linespacing=1.2,
    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none')
)

plt.savefig("find_data.png", dpi=350, bbox_inches='tight', pad_inches=0.2)
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
