import matplotlib
matplotlib.use('Agg', force=True)

import numpy as np
import matplotlib.pyplot as plt

# 参数设置
L = 1.0          # 弦长
a = 1.0          # 波速
x = np.linspace(0, L, 2000)  # 高密度采样保证清晰度

# 驻波函数 u_n(x,t) = cos(nπa t/L) sin(nπx/L)（对应 u(x,0)=sin(nπx/L), u_t(x,0)=0）
def standing_wave(n, x, t=0):
    return np.cos(n * np.pi * a * t / L) * np.sin(n * np.pi * x / L)

# 时间点
t0 = 0.0    # t=0 用于 n=1~5
t_super = 0.1  # t=0.1 用于叠加

# 创建画布
fig, axes = plt.subplots(2, 3, figsize=(24, 18), dpi=350)

# 第一行：n=1,2,3 在 t=0
for i, n in enumerate([1, 2, 3]):
    ax = axes[0, i]
    y = standing_wave(n, x, t0)
    ax.plot(x, y, 'b-', linewidth=2)
    ax.set_title(f'n = {n}    λ = {2*L/n:.2f}', fontsize=20)
    ax.set_xlabel('x', fontsize=16)
    ax.set_ylabel('u', fontsize=16)
    ax.set_ylim(-1.2, 1.2)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.axhline(0, color='gray', linewidth=0.8)

# 第二行前两个：n=4,5 在 t=0
for i, n in enumerate([4, 5]):
    ax = axes[1, i]
    y = standing_wave(n, x, t0)
    ax.plot(x, y, 'b-', linewidth=2)
    ax.set_title(f'n = {n}    λ = {2*L/n:.2f}', fontsize=20)
    ax.set_xlabel('x', fontsize=16)
    ax.set_ylabel('u', fontsize=16)
    ax.set_ylim(-1.2, 1.2)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.axhline(0, color='gray', linewidth=0.8)

# 第二行第三个：前5个模态叠加，t=0.1
ax = axes[1, 2]
y_super = sum(standing_wave(n, x, t_super) for n in range(1, 6))
ax.plot(x, y_super, 'r-', linewidth=2, label='sum n=1..5, t=0.1')
ax.set_title('Superposition of n=1...5 at t=0.1', fontsize=20)
ax.set_xlabel('x', fontsize=16)
ax.set_ylabel('u', fontsize=16)
ax.grid(True, linestyle='--', alpha=0.6)
ax.axhline(0, color='gray', linewidth=0.8)
ax.legend(fontsize=14)

plt.tight_layout(pad=3)
plt.savefig('string_wave.png', dpi=350, bbox_inches='tight')
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
