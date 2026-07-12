import matplotlib
matplotlib.use('Agg', force=True)

import os
import matplotlib.pyplot as plt

# 输出当前工作目录
print("当前工作目录:", os.getcwd())

# 设置保存路径
save_dir = r"D:\math_homework"
os.makedirs(save_dir, exist_ok=True)
save_path = os.path.join(save_dir, "laurent_series.png")

# ...（中间你的绘图代码不变）...

fig.text(0.5, 0.01, f"保存路径: {save_path}", ha='center', fontsize=9, color='gray')
plt.tight_layout(rect=[0, 0.03, 1, 0.97])  # 为底部文字留空间
plt.savefig(save_path)
print(f"图片已保存至: {save_path}")
plt.show()


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
