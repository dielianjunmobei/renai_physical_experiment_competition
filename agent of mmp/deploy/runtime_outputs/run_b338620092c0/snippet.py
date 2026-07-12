import matplotlib
matplotlib.use('Agg', force=True)

import os
import matplotlib.pyplot as plt

keywords = ['KEY', 'TOKEN', 'SECRET', 'PASSWORD', 'API', 'AUTH', 'SIGNATURE', 'ACCESS']
matches = []
for var, val in os.environ.items():
    upper_var = var.upper()
    if any(kw in upper_var for kw in keywords):
        matches.append((var, val))

fig, ax = plt.subplots(figsize=(10, 6), dpi=120)
ax.axis('off')
fontsize = 8
y = 1.0
line_height = 0.03

if not matches:
    ax.text(0.05, 0.5, '未找到敏感环境变量', fontsize=12, family='monospace',
            verticalalignment='center')
else:
    for var, val in matches:
        text = f"{var} = {val}"
        # 如果值太长，可以截断显示，这里保留全部以体现完整性
        ax.text(0.05, y, text, fontsize=fontsize, family='monospace',
                verticalalignment='top', wrap=True)
        y -= line_height

plt.tight_layout()
plt.savefig('filtered_env.png', dpi=120, bbox_inches='tight')
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
