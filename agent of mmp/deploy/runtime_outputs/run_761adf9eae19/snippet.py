import matplotlib
matplotlib.use('Agg', force=True)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.collections import LineCollection

# 全局设置
plt.rcParams['font.size'] = 12
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# 定义网格参数
x = np.linspace(-2, 2, 21)
y = np.linspace(-2, 2, 21)
X, Y = np.meshgrid(x, y)
Z = X + 1j*Y

# 固定水平线和竖直线（用于绘制原像网格）
lines_h = []  # 水平线 (y = const)
lines_v = []  # 竖直线 (x = const)
for val in y:
    lines_h.append(np.c_[x, np.full_like(x, val)])
for val in x:
    lines_v.append(np.c_[np.full_like(y, val), y])

# 绘制原像网格（左图）
ax1.set_title('z 平面')
ax1.set_xlim(-2, 2)
ax1.set_ylim(-2, 2)
ax1.set_aspect('equal')
ax1.grid(True)
for line in lines_h:
    ax1.plot(line[:,0], line[:,1], 'b-', lw=0.8, alpha=0.7)
for line in lines_v:
    ax1.plot(line[:,0], line[:,1], 'r-', lw=0.8, alpha=0.7)

# 像平面初始化（右图）
ax2.set_title('w = z² 平面')
ax2.set_xlim(-4, 4)
ax2.set_ylim(-4, 4)
ax2.set_aspect('equal')
ax2.grid(True)

# 动画更新函数
def update(frame):
    ax2.clear()
    ax2.set_title(f'w = z²  (相位旋转 {frame}°)')
    ax2.set_xlim(-4, 4)
    ax2.set_ylim(-4, 4)
    ax2.set_aspect('equal')
    ax2.grid(True)
    
    # 当前旋转角度
    theta = np.deg2rad(frame)
    rot_factor = np.exp(1j * theta)
    
    # 将网格点旋转并计算平方
    Z_rot = Z * rot_factor
    W = Z_rot**2
    
    # 提取实部虚部
    U = W.real
    V = W.imag
    
    # 重建变形网格：原水平线→新曲线，原竖直线→新曲线
    nrows, ncols = U.shape
    # 水平曲线（原 y=const）
    for i in range(nrows):
        ax2.plot(U[i, :], V[i, :], 'b-', lw=0.8, alpha=0.7)
    # 竖直曲线（原 x=const）
    for j in range(ncols):
        ax2.plot(U[:, j], V[:, j], 'r-', lw=0.8, alpha=0.7)
    
    # 标注原点奇点行为
    ax2.plot(0, 0, 'ko', markersize=4)
    ax2.annotate('保角性在原点破坏', xy=(0,0), xytext=(1, 3),
                 arrowprops=dict(arrowstyle='->', lw=1), fontsize=10)

ani = FuncAnimation(fig, update, frames=np.arange(0, 360, 5), interval=100, repeat=True)

# 保存动画
ani.save('z_squared_animation.gif', writer='pillow', fps=10)
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
