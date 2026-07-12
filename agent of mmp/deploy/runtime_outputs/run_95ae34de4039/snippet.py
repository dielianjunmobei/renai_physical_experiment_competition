import matplotlib
matplotlib.use('Agg', force=True)

import numpy as np
import matplotlib.pyplot as plt
import os

# ================= 路径设置 =================
print("当前工作目录:", os.getcwd())          # 显示当前目录
save_dir = r"D:\math_homework"                # 目标文件夹
os.makedirs(save_dir, exist_ok=True)         # 若不存在则创建
save_path = os.path.join(save_dir, "laurent_series.png")

# ================= 函数定义 =================
def f_exact(z):
    """精确函数 f(z) = 1/(1-z)"""
    return 1.0 / (1.0 - z)

def taylor_approx(z, N):
    """
    泰勒展开 (|z|<1)
    f(z) = ∑_{n=0}^{∞} z^n
    截断到 N 阶
    """
    s = np.zeros_like(z, dtype=complex)
    for n in range(N + 1):
        s += z**n
    return s

def laurent_approx(z, N, R=2.0):
    """
    洛朗展开 (1 < |z| < 2)
    f(z) = -∑_{n=1}^{N} z^{-n} - ∑_{n=0}^{N} z^n / 2^{n+1}
    """
    s = np.zeros_like(z, dtype=complex)
    # 负幂部分：-∑_{n=1}^{N} z^{-n}
    for n in range(1, N + 1):
        s -= z**(-n)
    # 正幂部分：-∑_{n=0}^{N} z^n / 2^{n+1}
    for n in range(0, N + 1):
        s -= z**n / (R**(n + 1))
    return s

# ================= 网格设置 =================
N_taylor = 5          # 泰勒展开项数
N_laurent = 5         # 洛朗展开项数
theta = np.linspace(0, 2 * np.pi, 200)   # 角度采样

# 泰勒展开区域：|z| < 0.95
r_taylor = np.linspace(0, 0.95, 50)
R_taylor, Th_taylor = np.meshgrid(r_taylor, theta)
Z_taylor = R_taylor * np.exp(1j * Th_taylor)

# 洛朗展开区域：1.05 < |z| < 1.95
r_laurent = np.linspace(1.05, 1.95, 100)
R_laurent, Th_laurent = np.meshgrid(r_laurent, theta)
Z_laurent = R_laurent * np.exp(1j * Th_laurent)

# ================= 计算函数值 =================
f_exact_taylor = f_exact(Z_taylor)
f_approx_taylor = taylor_approx(Z_taylor, N_taylor)

f_exact_laurent = f_exact(Z_laurent)
f_approx_laurent = laurent_approx(Z_laurent, N_laurent, R=2.0)

# ================= 绘图 =================
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle(r'$f(z)=1/(1-z)$ 的级数逼近比较', fontsize=16)

# ----- 泰勒展开实部 -----
ax = axes[0, 0]
c1 = ax.contourf(Z_taylor.real, Z_taylor.imag, f_exact_taylor.real,
                 levels=50, cmap='RdBu_r', alpha=0.7)
ax.contour(Z_taylor.real, Z_taylor.imag, f_approx_taylor.real,
           levels=20, colors='k', linewidths=1)
ax.set_title(f'泰勒展开实部 (N={N_taylor})')
ax.set_xlabel('Re(z)')
ax.set_ylabel('Im(z)')
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)
fig.colorbar(c1, ax=ax, fraction=0.046, pad=0.04)

# ----- 泰勒展开虚部 -----
ax = axes[0, 1]
c2 = ax.contourf(Z_taylor.real, Z_taylor.imag, f_exact_taylor.imag,
                 levels=50, cmap='RdBu_r', alpha=0.7)
ax.contour(Z_taylor.real, Z_taylor.imag, f_approx_taylor.imag,
           levels=20, colors='k', linewidths=1)
ax.set_title(f'泰勒展开虚部 (N={N_taylor})')
ax.set_xlabel('Re(z)')
ax.set_ylabel('Im(z)')
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)
fig.colorbar(c2, ax=ax, fraction=0.046, pad=0.04)

# ----- 洛朗展开实部 -----
ax = axes[1, 0]
c3 = ax.contourf(Z_laurent.real, Z_laurent.imag, f_exact_laurent.real,
                 levels=50, cmap='RdBu_r', alpha=0.7)
ax.contour(Z_laurent.real, Z_laurent.imag, f_approx_laurent.real,
           levels=20, colors='k', linewidths=1)
ax.set_title(f'洛朗展开实部 (N={N_laurent}, 1<|z|<2)')
ax.set_xlabel('Re(z)')
ax.set_ylabel('Im(z)')
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)
# 画环域边界
ax.add_patch(plt.Circle((0,0), 1.0, fill=False, color='white', linestyle='--', linewidth=1.5))
ax.add_patch(plt.Circle((0,0), 2.0, fill=False, color='white', linestyle='--', linewidth=1.5))
fig.colorbar(c3, ax=ax, fraction=0.046, pad=0.04)

# ----- 洛朗展开虚部 -----
ax = axes[1, 1]
c4 = ax.contourf(Z_laurent.real, Z_laurent.imag, f_exact_laurent.imag,
                 levels=50, cmap='RdBu_r', alpha=0.7)
ax.contour(Z_laurent.real, Z_laurent.imag, f_approx_laurent.imag,
           levels=20, colors='k', linewidths=1)
ax.set_title(f'洛朗展开虚部 (N={N_laurent}, 1<|z|<2)')
ax.set_xlabel('Re(z)')
ax.set_ylabel('Im(z)')
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)
ax.add_patch(plt.Circle((0,0), 1.0, fill=False, color='white', linestyle='--', linewidth=1.5))
ax.add_patch(plt.Circle((0,0), 2.0, fill=False, color='white', linestyle='--', linewidth=1.5))
fig.colorbar(c4, ax=ax, fraction=0.046, pad=0.04)

# 在图片底部显示保存路径
fig.text(0.5, 0.01, f"保存路径: {save_path}", ha='center', fontsize=9, color='gray')

plt.tight_layout(rect=[0, 0.03, 1, 0.97])   # 为底部文字留空间
plt.savefig(save_path, dpi=150)
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
