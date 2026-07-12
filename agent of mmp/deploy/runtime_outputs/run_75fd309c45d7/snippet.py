import matplotlib
matplotlib.use('Agg', force=True)

import os
import matplotlib.pyplot as plt

# 读取当前目录下的 snippet.py
try:
    with open("snippet.py", "r", encoding="utf-8") as f:
        content = f.read()
    # 如果过长则截断前1000字符并提示
    max_chars = 1000
    if len(content) > max_chars:
        display_text = content[:max_chars] + "\n\n... [截断: 文件总长度 {} 字符]".format(len(content))
    else:
        display_text = content
except FileNotFoundError:
    display_text = "文件 snippet.py 不存在于当前目录。"
except Exception as e:
    display_text = f"读取 snippet.py 出错: {e}"

# 绘图
fig, ax = plt.subplots(figsize=(18, 12))
ax.axis('off')
ax.text(0.02, 0.98, display_text, transform=ax.transAxes,
        fontsize=14, fontfamily='monospace',
        verticalalignment='top', horizontalalignment='left',
        linespacing=1.2,
        bbox=dict(facecolor='white', alpha=0.9, edgecolor='gray'))

plt.savefig("snippet_full.png", dpi=300, bbox_inches='tight', pad_inches=0.3)
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
