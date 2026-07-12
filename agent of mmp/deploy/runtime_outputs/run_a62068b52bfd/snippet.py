import matplotlib
matplotlib.use('Agg', force=True)

import os
import matplotlib.pyplot as plt

try:
    env_items = list(os.environ.items())
    env_items.sort()
    max_lines = 200
    lines = []
    for i, (key, value) in enumerate(env_items):
        if i >= max_lines:
            lines.append(f"... (共 {len(env_items)} 个环境变量，仅显示前 {max_lines} 个)")
            break
        lines.append(f"{key}={value}")
    display_text = "\n".join(lines)
except Exception as e:
    display_text = f"读取环境变量出错: {e}"

fig, ax = plt.subplots(figsize=(24, 18))
ax.axis('off')
ax.text(0.02, 0.98, display_text, transform=ax.transAxes,
        fontsize=14, fontfamily='monospace',
        verticalalignment='top', horizontalalignment='left',
        linespacing=1.1,
        bbox=dict(facecolor='white', alpha=0.9, edgecolor='gray'))

plt.savefig("env_vars.png", dpi=300, bbox_inches='tight', pad_inches=0.3)
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
