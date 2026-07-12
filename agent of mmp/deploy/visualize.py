import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.animation import FuncAnimation
import io
import base64
import tempfile
import os
import math

plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['figure.dpi'] = 120
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ==================== 第1章 复变函数 ====================

def plot_analytic_grid(f, title="复变函数映射", zlim=2, n_grid=20):
    x = np.linspace(-zlim, zlim, n_grid)
    y = np.linspace(-zlim, zlim, n_grid)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    W = f(Z)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    ax = axes[0]
    for i in range(len(x)):
        ax.plot(X[i, :], Y[i, :], 'b-', alpha=0.5, linewidth=0.8)
        ax.plot(X[:, i], Y[:, i], 'r-', alpha=0.5, linewidth=0.8)
    ax.set_xlim(-zlim, zlim); ax.set_ylim(-zlim, zlim)
    ax.set_aspect('equal'); ax.set_title('z-平面 (原像)', fontsize=12)
    ax.set_xlabel('Re(z)'); ax.set_ylabel('Im(z)'); ax.grid(True, alpha=0.3)
    ax = axes[1]
    U, V = W.real, W.imag
    for i in range(len(x)):
        ax.plot(U[i, :], V[i, :], 'b-', alpha=0.5, linewidth=0.8)
        ax.plot(U[:, i], V[:, i], 'r-', alpha=0.5, linewidth=0.8)
    ax.set_aspect('equal'); ax.set_title('w-平面 (像)', fontsize=12)
    ax.set_xlabel('Re(w)'); ax.set_ylabel('Im(w)'); ax.grid(True, alpha=0.3)
    plt.suptitle(title, fontsize=14, fontweight='bold', color='#1B3A5C')
    plt.tight_layout(); return fig


def plot_harmonic_contours(u_func, v_func=None, title="调和函数可视化", xlim=2, ylim=2, levels=20):
    x = np.linspace(-xlim, xlim, 400); y = np.linspace(-ylim, ylim, 400)
    X, Y = np.meshgrid(x, y); U = u_func(X, Y)
    fig, ax = plt.subplots(figsize=(8, 7))
    cs1 = ax.contour(X, Y, U, levels=levels, colors='#1B3A5C', linewidths=1.5, alpha=0.8)
    ax.clabel(cs1, inline=True, fontsize=8, fmt='u=%1.1f')
    if v_func is not None:
        V = v_func(X, Y)
        cs2 = ax.contour(X, Y, V, levels=levels, colors='#C8923A', linewidths=1.5, alpha=0.8, linestyles='--')
        ax.clabel(cs2, inline=True, fontsize=8, fmt='v=%1.1f')
    ax.set_xlabel('x'); ax.set_ylabel('y')
    ax.set_title(title, fontsize=13, color='#1B3A5C', fontweight='bold')
    ax.set_aspect('equal'); ax.grid(True, alpha=0.3)
    legend_elements = [Line2D([0], [0], color='#1B3A5C', lw=1.5, label='等势线 u = 常数')]
    if v_func is not None:
        legend_elements.append(Line2D([0], [0], color='#C8923A', lw=1.5, linestyle='--', label='流线 v = 常数'))
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    ax.text(0.02, 0.02, '等势线 ⟂ 流线：C-R 方程的几何体现', transform=ax.transAxes, fontsize=9, color='gray', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    plt.tight_layout(); return fig


def plot_complex_exponential(xlim=2*np.pi, ylim=3):
    x = np.linspace(-xlim, xlim, 400); y = np.linspace(-ylim, ylim, 400)
    X, Y = np.meshgrid(x, y); Z = X + 1j*Y; W = np.exp(Z)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    ax = axes[0]
    im = ax.contourf(X, Y, np.abs(W), levels=50, cmap='YlOrRd')
    plt.colorbar(im, ax=ax, label='|e^z|')
    ax.set_title(r'$|e^z| = e^x$（仅与 x 有关）', fontsize=11); ax.set_xlabel('x'); ax.set_ylabel('y')
    ax.axvline(x=0, color='white', linestyle='--', alpha=0.7)
    ax = axes[1]
    im = ax.contourf(X, Y, np.angle(W), levels=50, cmap='twilight')
    plt.colorbar(im, ax=ax, label='arg(e^z)')
    ax.set_title(r'$\arg(e^z) = y$（仅与 y 有关）', fontsize=11); ax.set_xlabel('x'); ax.set_ylabel('y')
    ax.axhline(y=0, color='white', linestyle='--', alpha=0.7)
    ax.axhline(y=2*np.pi, color='white', linestyle='--', alpha=0.5)
    ax.axhline(y=-2*np.pi, color='white', linestyle='--', alpha=0.5)
    ax = axes[2]
    im = ax.contourf(X, Y, np.real(W), levels=50, cmap='RdBu_r')
    plt.colorbar(im, ax=ax, label='Re(e^z)')
    ax.set_title(r'$\Re(e^z) = e^x \cos y$（周期 $2\pi$）', fontsize=11); ax.set_xlabel('x'); ax.set_ylabel('y')
    plt.suptitle('复指数函数 $e^z$ 的可视化', fontsize=14, fontweight='bold', color='#1B3A5C')
    plt.tight_layout(); return fig


def plot_complex_sine(xlim=np.pi, ylim=3):
    x = np.linspace(-xlim, xlim, 400); y = np.linspace(-ylim, ylim, 400)
    X, Y = np.meshgrid(x, y); Z = X + 1j*Y; W = np.sin(Z)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    ax = axes[0]
    modulus = np.abs(W)
    im = ax.contourf(X, Y, modulus, levels=50, cmap='magma', vmax=np.percentile(modulus, 95))
    plt.colorbar(im, ax=ax, label='|sin z|')
    ax.set_title(r'$|\sin z|$ 的分布（虚轴方向指数增长）', fontsize=11); ax.set_xlabel('x'); ax.set_ylabel('y')
    for n in range(-1, 2): ax.axvline(x=n*np.pi, color='cyan', linestyle='--', alpha=0.7)
    ax = axes[1]
    im = ax.contourf(X, Y, np.real(W), levels=50, cmap='RdBu_r')
    plt.colorbar(im, ax=ax, label='Re(sin z)')
    ax.set_title(r'$\Re(\sin z) = \sin x \cosh y$', fontsize=11); ax.set_xlabel('x'); ax.set_ylabel('y')
    plt.suptitle(r'复三角函数 $\sin z$ 的可视化', fontsize=14, fontweight='bold', color='#1B3A5C')
    plt.tight_layout(); return fig


def plot_cr_geometric():
    fig, ax = plt.subplots(figsize=(7, 7))
    points = np.array([[-1, -1], [0, 0], [1, 1], [-1, 1], [1, -1]])
    for (x, y) in points:
        du = np.array([2*x, -2*y]) * 0.15
        dv = np.array([2*y, 2*x]) * 0.15
        ax.annotate('', xy=(x+du[0], y+du[1]), xytext=(x, y), arrowprops=dict(arrowstyle='->', color='#1B3A5C', lw=2))
        ax.annotate('', xy=(x+dv[0], y+dv[1]), xytext=(x, y), arrowprops=dict(arrowstyle='->', color='#C8923A', lw=2))
        ax.plot(x, y, 'ko', markersize=6)
    x = np.linspace(-1.5, 1.5, 100); y = np.linspace(-1.5, 1.5, 100)
    X, Y = np.meshgrid(x, y); U = X**2 - Y**2; V = 2*X*Y
    ax.contour(X, Y, U, levels=10, colors='#1B3A5C', alpha=0.3, linewidths=0.8)
    ax.contour(X, Y, V, levels=10, colors='#C8923A', alpha=0.3, linewidths=0.8, linestyles='--')
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5); ax.set_aspect('equal')
    ax.set_xlabel('x'); ax.set_ylabel('y')
    ax.set_title('C-R 方程的几何意义：∇u ⟂ ∇v 且 |∇u| = |∇v|', fontsize=13, color='#1B3A5C', fontweight='bold')
    ax.grid(True, alpha=0.3)
    legend_elements = [Line2D([0], [0], color='#1B3A5C', lw=2, label=r'$\nabla u$'), Line2D([0], [0], color='#C8923A', lw=2, label=r'$\nabla v$')]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
    ax.text(0.5, -0.12, r'$\nabla u \cdot \nabla v = 0$  ⟹  等势线 ⟂ 流线', transform=ax.transAxes, fontsize=11, ha='center', bbox=dict(boxstyle='round', facecolor='#f0f4f8', alpha=0.8))
    plt.tight_layout(); return fig


def plot_conformal_angle():
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    t = np.linspace(0, 1.5, 100)
    ax = axes[0]
    ax.plot(t*np.cos(np.pi/4), t*np.sin(np.pi/4), 'b-', lw=2, label='射线1')
    ax.plot(t*np.cos(5*np.pi/12), t*np.sin(5*np.pi/12), 'r-', lw=2, label='射线2')
    ax.annotate('', xy=(0.3*np.cos(5*np.pi/12), 0.3*np.sin(5*np.pi/12)), xytext=(0.3*np.cos(np.pi/4), 0.3*np.sin(np.pi/4)), arrowprops=dict(arrowstyle='->', color='green', lw=1.5))
    ax.text(0.25, 0.35, r'$\theta = 30°$', fontsize=11, color='green')
    ax.set_xlim(-0.2, 1.5); ax.set_ylim(-0.2, 1.5); ax.set_aspect('equal')
    ax.set_title('z-平面：两条射线夹角 30°', fontsize=12); ax.set_xlabel('Re(z)'); ax.set_ylabel('Im(z)')
    ax.legend(loc='lower right'); ax.grid(True, alpha=0.3); ax.plot(0, 0, 'ko', markersize=8)
    ax = axes[1]
    w1 = (t**2)*np.cos(np.pi/2) + 1j*(t**2)*np.sin(np.pi/2)
    w2 = (t**2)*np.cos(5*np.pi/6) + 1j*(t**2)*np.sin(5*np.pi/6)
    ax.plot(w1.real, w1.imag, 'b-', lw=2, label='像1')
    ax.plot(w2.real, w2.imag, 'r-', lw=2, label='像2')
    ax.annotate('', xy=(0.3*np.cos(5*np.pi/6), 0.3*np.sin(5*np.pi/6)), xytext=(0.3*np.cos(np.pi/2), 0.3*np.sin(np.pi/2)), arrowprops=dict(arrowstyle='->', color='green', lw=1.5))
    ax.text(-0.2, 0.35, r'$\theta = 30°$（不变）', fontsize=11, color='green')
    ax.set_xlim(-0.5, 2.5); ax.set_ylim(-0.2, 1.5); ax.set_aspect('equal')
    ax.set_title('w-平面：$w = z^2$，夹角仍保持 30°', fontsize=12); ax.set_xlabel('Re(w)'); ax.set_ylabel('Im(w)')
    ax.legend(loc='lower right'); ax.grid(True, alpha=0.3); ax.plot(0, 0, 'ko', markersize=8)
    plt.suptitle('共形映射：角度保持性（$f(z)=z^2$ 在 $z \neq 0$ 处）', fontsize=14, fontweight='bold', color='#1B3A5C')
    plt.tight_layout(); return fig


# ==================== 第2章 复变函数的积分 ====================

def plot_cauchy_integral_path():
    """展示柯西定理：同端点不同路径积分结果相同"""
    fig, ax = plt.subplots(figsize=(9, 7))
    z1, z2 = -1+0.5j, 1+0.5j
    t = np.linspace(0, 1, 100)
    path1 = z1 + t*(z2 - z1)
    center = (z1 + z2)/2
    radius = abs(z2 - z1)/2
    angles = np.linspace(np.pi, 0, 100)
    path2 = center + radius * np.exp(1j * angles)
    angles3 = np.linspace(-np.pi, 0, 100)
    path3 = center + radius * np.exp(1j * angles3)
    ax.plot(path1.real, path1.imag, 'b-', lw=2.5, label='路径1：直线')
    ax.plot(path2.real, path2.imag, 'r--', lw=2.5, label='路径2：上半圆弧')
    ax.plot(path3.real, path3.imag, 'g:', lw=2.5, label='路径3：下半圆弧')
    ax.plot(z1.real, z1.imag, 'ko', markersize=10)
    ax.plot(z2.real, z2.imag, 'ko', markersize=10)
    ax.annotate('z1', xy=(z1.real, z1.imag), xytext=(-1.2, 0.8), fontsize=12, arrowprops=dict(arrowstyle='->', color='black'))
    ax.annotate('z2', xy=(z2.real, z2.imag), xytext=(1.1, 0.8), fontsize=12, arrowprops=dict(arrowstyle='->', color='black'))
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-0.8, 1.2); ax.set_aspect('equal')
    ax.set_xlabel('Re(z)'); ax.set_ylabel('Im(z)')
    ax.set_title('柯西定理：解析函数积分与路径无关', fontsize=13, color='#1B3A5C', fontweight='bold')
    ax.legend(loc='upper right', fontsize=10); ax.grid(True, alpha=0.3)
    ax.text(0.5, -0.08, '∫_路径1 f(z)dz = ∫_路径2 f(z)dz = ∫_路径3 f(z)dz', transform=ax.transAxes, fontsize=11, ha='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    plt.tight_layout(); return fig


def plot_cauchy_integral_formula():
    """展示柯西积分公式：边界值决定内部值"""
    theta = np.linspace(0, 2*np.pi, 100)
    r = 1.0
    boundary = r * np.exp(1j * theta)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot(boundary.real, boundary.imag, 'b-', lw=2.5, label='积分路径 C: |z|=1')
    interior_points = [0.3+0.2j, -0.4+0.5j, 0.5-0.3j]
    colors = ['#C8923A', '#2E8B57', '#8B4513']
    for i, z0 in enumerate(interior_points):
        ax.plot(z0.real, z0.imag, 'o', color=colors[i], markersize=10)
        ax.annotate(f'z{i+1}', xy=(z0.real, z0.imag), xytext=(z0.real+0.15, z0.imag+0.15), fontsize=11, color=colors[i])
        for j in range(0, len(theta), 10):
            z = boundary[j]
            ax.plot([z0.real, z.real], [z0.imag, z.imag], color=colors[i], alpha=0.1, lw=0.5)
    ax.set_xlim(-1.3, 1.3); ax.set_ylim(-1.3, 1.3); ax.set_aspect('equal')
    ax.set_xlabel('Re(z)'); ax.set_ylabel('Im(z)')
    ax.set_title('柯西积分公式：边界值决定内部值\nf(z0) = (1/2πi)∮_C f(z)/(z-z0) dz', fontsize=12, color='#1B3A5C', fontweight='bold')
    ax.legend(loc='upper right'); ax.grid(True, alpha=0.3)
    ax.text(0.5, -0.08, '解析函数在区域内的值完全由边界值决定', transform=ax.transAxes, fontsize=10, ha='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    plt.tight_layout(); return fig


# ==================== 第3章 幂级数展开 ====================

def plot_taylor_convergence():
    """展示泰勒级数的收敛圆"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    ax = axes[0]
    theta = np.linspace(0, 2*np.pi, 100)
    R = 1.0
    ax.plot(R*np.cos(theta), R*np.sin(theta), 'b-', lw=2, label='收敛圆 |z|=1')
    ax.plot(0, 0, 'ko', markersize=8, label='展开中心 z0=0')
    ax.plot(1, 0, 'rx', markersize=12, markeredgewidth=3, label='奇点 z=1')
    ax.fill(R*np.cos(theta), R*np.sin(theta), alpha=0.1, color='blue')
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5); ax.set_aspect('equal')
    ax.set_xlabel('Re(z)'); ax.set_ylabel('Im(z)')
    ax.set_title('泰勒级数收敛圆：f(z)=1/(1-z) 在 z0=0', fontsize=12, color='#1B3A5C')
    ax.legend(loc='upper left'); ax.grid(True, alpha=0.3)
    ax = axes[1]
    x_real = np.linspace(-0.99, 0.99, 200)
    ax.plot(x_real, 1/(1-x_real), 'k-', lw=2, label='精确 f(x)=1/(1-x)')
    colors = ['#1B3A5C', '#C8923A', '#2E8B57', '#8B4513']
    for n, c in zip([1, 3, 5, 10], colors):
        partial = sum([x_real**k for k in range(n+1)])
        ax.plot(x_real, partial, '--', color=c, lw=1.5, label=f'S_{n}(x)=Σ_{{k=0}}^{n} x^k')
    ax.set_xlim(-1, 1); ax.set_ylim(-1, 5)
    ax.set_xlabel('x (实轴)'); ax.set_ylabel('f(x)')
    ax.set_title('泰勒部分和逼近：收敛半径 R=1', fontsize=12, color='#1B3A5C')
    ax.legend(loc='upper left', fontsize=9); ax.grid(True, alpha=0.3)
    plt.suptitle('第3章 幂级数展开：收敛圆与部分和', fontsize=14, fontweight='bold', color='#1B3A5C')
    plt.tight_layout(); return fig


def plot_laurent_annulus():
    """展示洛朗级数的圆环收敛区域"""
    fig, ax = plt.subplots(figsize=(8, 8))
    theta = np.linspace(0, 2*np.pi, 100)
    r2 = 1.0
    ax.fill_between(np.cos(theta), np.sin(theta), 0, alpha=0.1, color='green', label='|z|<1: 泰勒级数')
    r1 = 0.3; r2 = 0.8
    ax.fill_between(r2*np.cos(theta), r2*np.sin(theta), r1*np.cos(theta), alpha=0.2, color='orange', label='圆环 r<|z|<R: 洛朗级数')
    ax.plot(r2*np.cos(theta), r2*np.sin(theta), 'orange', lw=2, linestyle='--')
    ax.plot(r1*np.cos(theta), r1*np.sin(theta), 'orange', lw=2, linestyle='--')
    ax.plot(0, 0, 'rx', markersize=12, markeredgewidth=3, label='奇点 z=0')
    ax.plot(1, 0, 'bx', markersize=12, markeredgewidth=3, label='奇点 z=1')
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5); ax.set_aspect('equal')
    ax.set_xlabel('Re(z)'); ax.set_ylabel('Im(z)')
    ax.set_title('洛朗级数收敛圆环：f(z)=1/(z(z-1))\n在 z0=0 附近，0<|z|<1 为洛朗区域', fontsize=12, color='#1B3A5C', fontweight='bold')
    ax.legend(loc='upper left'); ax.grid(True, alpha=0.3)
    plt.tight_layout(); return fig


# ==================== 第4章 留数定理 ====================

def plot_residue_contour():
    """展示留数定理的围道积分"""
    fig, ax = plt.subplots(figsize=(9, 8))
    theta = np.linspace(0, 2*np.pi, 100)
    R = 2.0
    ax.plot(R*np.cos(theta), R*np.sin(theta), 'b-', lw=2.5, label='大围道 C: |z|=2')
    singularities = [0.5+0.3j, -0.3-0.5j, 0.8-0.2j]
    colors = ['#C8923A', '#2E8B57', '#8B4513']
    for i, z0 in enumerate(singularities):
        ax.plot(z0.real, z0.imag, 'x', color=colors[i], markersize=14, markeredgewidth=3, label=f'奇点 z{i+1}')
        r_small = 0.2
        small_circle = z0 + r_small * np.exp(1j * theta)
        ax.plot(small_circle.real, small_circle.imag, '--', color=colors[i], lw=1.5)
    ax.set_xlim(-2.5, 2.5); ax.set_ylim(-2.5, 2.5); ax.set_aspect('equal')
    ax.set_xlabel('Re(z)'); ax.set_ylabel('Im(z)')
    ax.set_title('留数定理：∮_C f(z)dz = 2πi · Σ Res(f, z_k)\n大围道积分 = 2πi × 内部所有留数之和', fontsize=12, color='#1B3A5C', fontweight='bold')
    ax.legend(loc='upper right', fontsize=9); ax.grid(True, alpha=0.3)
    plt.tight_layout(); return fig


# ==================== 第5章 傅里叶变换 ====================

def plot_fourier_spectrum():
    """展示傅里叶变换：方波的频谱"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    x = np.linspace(-5, 5, 1000)
    ax = axes[0, 0]
    square = np.sign(np.sin(np.pi * x))
    ax.plot(x, square, 'k-', lw=2, label='方波 f(x)')
    for n, c in zip([1, 3, 5, 15], ['#1B3A5C', '#C8923A', '#2E8B57', '#8B4513']):
        partial = sum([4/np.pi * np.sin((2*k+1)*np.pi*x)/(2*k+1) for k in range(n)])
        ax.plot(x, partial, '--', color=c, lw=1.2, label=f'前{n}项')
    ax.set_xlim(-2.5, 2.5); ax.set_ylim(-1.5, 1.5)
    ax.set_xlabel('x'); ax.set_ylabel('f(x)')
    ax.set_title('方波的傅里叶级数逼近', fontsize=12, color='#1B3A5C')
    ax.legend(loc='upper right', fontsize=8); ax.grid(True, alpha=0.3)
    ax = axes[0, 1]
    omega = np.linspace(-10, 10, 500)
    spectrum = 2 * np.sin(omega) / (omega + 1e-10)
    ax.plot(omega, spectrum, '#1B3A5C', lw=2)
    ax.axhline(y=0, color='k', lw=0.5)
    ax.set_xlabel('ω'); ax.set_ylabel('F(ω)')
    ax.set_title('频谱 F(ω) = 2sin(ω)/ω：sinc 函数', fontsize=12, color='#1B3A5C')
    ax.grid(True, alpha=0.3)
    ax = axes[1, 0]
    gaussian = np.exp(-x**2)
    ax.plot(x, gaussian, '#C8923A', lw=2, label='f(x) = e^{-x²}')
    ax.set_xlabel('x'); ax.set_ylabel('f(x)')
    ax.set_title('高斯脉冲：时域宽 → 频域窄', fontsize=12, color='#1B3A5C')
    ax.legend(); ax.grid(True, alpha=0.3)
    ax = axes[1, 1]
    gauss_spec = np.sqrt(np.pi) * np.exp(-omega**2/4)
    ax.plot(omega, gauss_spec, '#C8923A', lw=2, label='F(ω) = √π e^{-ω²/4}')
    ax.set_xlabel('ω'); ax.set_ylabel('F(ω)')
    ax.set_title('高斯频谱：自身型变换', fontsize=12, color='#1B3A5C')
    ax.legend(); ax.grid(True, alpha=0.3)
    plt.suptitle('第5章 傅里叶变换：时域与频域的对偶性', fontsize=14, fontweight='bold', color='#1B3A5C')
    plt.tight_layout(); return fig


# ==================== 第6章 拉普拉斯变换 ====================

def plot_laplace_poles():
    """展示拉普拉斯变换：极点位置与时间响应的关系"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    ax = axes[0]
    ax.axhline(y=0, color='k', lw=0.5); ax.axvline(x=0, color='k', lw=0.5)
    poles = [(-1, 0), (-0.5, 2), (-0.5, -2), (-2, 0), (0.3, 0)]
    labels = ['稳定实极点', '稳定共轭复极点', '稳定共轭复极点', '快速衰减', '不稳定极点']
    colors = ['#1B3A5C', '#C8923A', '#C8923A', '#2E8B57', '#8B0000']
    for (sr, si), label, c in zip(poles, labels, colors):
        ax.plot(sr, si, 'x', color=c, markersize=12, markeredgewidth=2, label=label if si>=0 else '')
    ax.set_xlim(-3, 1); ax.set_ylim(-3, 3); ax.set_aspect('equal')
    ax.set_xlabel('Re(s) = σ'); ax.set_ylabel('Im(s) = ω')
    ax.set_title('s平面：极点位置决定系统稳定性\n左半平面 → 稳定，右半平面 → 不稳定', fontsize=11, color='#1B3A5C')
    ax.legend(loc='upper left', fontsize=8); ax.grid(True, alpha=0.3)
    ax = axes[1]
    t = np.linspace(0, 5, 500)
    responses = [
        (np.exp(-t), 'e^{-t} (σ=-1)', '#1B3A5C'),
        (np.exp(-0.5*t)*np.cos(2*t), 'e^{-0.5t}cos(2t) (σ=-0.5, ω=2)', '#C8923A'),
        (np.exp(-2*t), 'e^{-2t} (σ=-2)', '#2E8B57'),
        (np.exp(0.3*t), 'e^{0.3t} 发散! (σ=0.3)', '#8B0000'),
    ]
    for y, label, c in responses:
        ax.plot(t, y, color=c, lw=2, label=label)
    ax.set_xlabel('t'); ax.set_ylabel('y(t)')
    ax.set_title('时间响应：极点实部决定衰减速率\n虚部决定振荡频率', fontsize=11, color='#1B3A5C')
    ax.legend(loc='upper right', fontsize=8); ax.grid(True, alpha=0.3)
    ax.set_ylim(-1.5, 3)
    plt.suptitle('第6章 拉普拉斯变换：极点与系统响应', fontsize=14, fontweight='bold', color='#1B3A5C')
    plt.tight_layout(); return fig

# ==================== 第7章 数学物理定解问题 ====================

def plot_pde_classification():
    """展示三类偏微分方程的特征"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    x = np.linspace(0, 10, 200); t = np.linspace(0, 5, 100)
    X, T = np.meshgrid(x, t)
    # 双曲型：波动方程（行波）
    ax = axes[0]
    a = 1.0
    u_wave = np.sin(X - a*T) + 0.5*np.sin(X + a*T)
    im = ax.contourf(X, T, u_wave, levels=50, cmap='RdBu_r')
    plt.colorbar(im, ax=ax, label='u(x,t)')
    for t_line in [0, 1, 2, 3, 4]:
        ax.plot(x, (x - 5)/a + t_line, 'w--', alpha=0.5, lw=0.8)
        ax.plot(x, -(x - 5)/a + t_line, 'w--', alpha=0.5, lw=0.8)
    ax.set_xlabel('x'); ax.set_ylabel('t')
    ax.set_title('双曲型：波动方程\n$u_{tt} = a^2 u_{xx}$\n特征线：x±at = 常数', fontsize=11, color='#1B3A5C')
    # 抛物型：热传导（扩散）
    ax = axes[1]
    a = 0.5
    u_heat = np.exp(-X**2/(4*a**2*(T+0.1))) / np.sqrt(4*np.pi*a**2*(T+0.1))
    im = ax.contourf(X, T, u_heat, levels=50, cmap='YlOrRd')
    plt.colorbar(im, ax=ax, label='u(x,t)')
    ax.set_xlabel('x'); ax.set_ylabel('t')
    ax.set_title('抛物型：热传导方程\n$u_t = a^2 u_{xx}$\n扩散过程：信息单向传播', fontsize=11, color='#1B3A5C')
    # 椭圆型：拉普拉斯（稳态）
    ax = axes[2]
    x2 = np.linspace(-5, 5, 200); y2 = np.linspace(-5, 5, 200)
    X2, Y2 = np.meshgrid(x2, y2)
    u_laplace = np.sin(X2) * np.cosh(Y2) / np.cosh(5)
    im = ax.contourf(X2, Y2, u_laplace, levels=50, cmap='viridis')
    plt.colorbar(im, ax=ax, label='u(x,y)')
    ax.set_xlabel('x'); ax.set_ylabel('y')
    ax.set_title('椭圆型：拉普拉斯方程\n$\\nabla^2 u = 0$\n稳态：无时间依赖', fontsize=11, color='#1B3A5C')
    plt.suptitle('第7章 三类偏微分方程的特征对比', fontsize=14, fontweight='bold', color='#1B3A5C')
    plt.tight_layout(); return fig


def plot_dalembert():
    """展示达朗贝尔公式：波动分解"""
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    x = np.linspace(-10, 10, 500); a = 1.0
    phi = np.zeros_like(x)
    phi[(x > -2) & (x < 2)] = 1 - np.abs(x[(x > -2) & (x < 2)]) / 2
    times = [0, 1, 2, 3, 4, 5]
    for idx, t in enumerate(times):
        ax = axes[idx // 3, idx % 3]
        phi_right = np.interp(x + a*t, x, phi, left=0, right=0)
        phi_left = np.interp(x - a*t, x, phi, left=0, right=0)
        u = 0.5 * (phi_right + phi_left)
        ax.fill_between(x, 0, phi_right, alpha=0.3, color='blue', label='φ(x+at) 右行波')
        ax.fill_between(x, 0, phi_left, alpha=0.3, color='red', label='φ(x-at) 左行波')
        ax.plot(x, u, 'k-', lw=2.5, label='u(x,t) = [φ(x+at)+φ(x-at)]/2')
        ax.set_xlim(-10, 10); ax.set_ylim(-0.5, 1.5)
        ax.set_title(f't = {t}', fontsize=12, color='#1B3A5C')
        ax.set_xlabel('x'); ax.set_ylabel('u')
        if idx == 0: ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3)
    plt.suptitle('第7章 达朗贝尔公式：初始位移分解为左右传播的两列波', fontsize=14, fontweight='bold', color='#1B3A5C')
    plt.tight_layout(); return fig


# ==================== 第8章 分离变数法 ====================

def plot_separation_modes():
    """展示分离变量法的驻波叠加"""
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    x = np.linspace(0, 1, 500); L = 1.0; a = 1.0
    times = [0, 0.3, 0.6, 0.9, 1.2, 1.5]
    for idx, t in enumerate(times):
        ax = axes[idx // 3, idx % 3]
        u = np.zeros_like(x)
        colors = ['#1B3A5C', '#C8923A', '#2E8B57']
        for n, c in zip([1, 2, 3], colors):
            mode = np.sin(n*np.pi*x/L) * np.cos(n*np.pi*a*t/L)
            u += mode * (2/np.pi) * ((-1)**(n+1) + 1) / n
            ax.plot(x, mode, '--', color=c, lw=1, alpha=0.6, label=f'模式 n={n}')
        ax.plot(x, u, 'k-', lw=2.5, label='叠加 u(x,t)')
        ax.set_xlim(0, 1); ax.set_ylim(-1.5, 1.5)
        ax.set_title(f't = {t:.1f}', fontsize=12, color='#1B3A5C')
        ax.set_xlabel('x'); ax.set_ylabel('u')
        if idx == 0: ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3)
    plt.suptitle('第8章 分离变量法：弦振动的前3个驻波模式叠加', fontsize=14, fontweight='bold', color='#1B3A5C')
    plt.tight_layout(); return fig


def plot_heat_evolution():
    """展示热传导方程的温度演化"""
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    x = np.linspace(0, 1, 500); L = 1.0; a = 1.0
    times = [0, 0.05, 0.1, 0.2, 0.5, 1.0]
    for idx, t in enumerate(times):
        ax = axes[idx // 3, idx % 3]
        u = np.zeros_like(x)
        for n, A in [(1, 1.0), (3, 0.3), (5, 0.1)]:
            u += A * np.sin(n*np.pi*x/L) * np.exp(-(n*np.pi*a/L)**2 * t)
        ax.fill_between(x, 0, u, alpha=0.3, color='#C8923A')
        ax.plot(x, u, '#1B3A5C', lw=2.5)
        ax.set_xlim(0, 1); ax.set_ylim(-0.2, 1.5)
        ax.set_title(f't = {t:.2f}', fontsize=12, color='#1B3A5C')
        ax.set_xlabel('x'); ax.set_ylabel('T(x,t)')
        ax.grid(True, alpha=0.3)
    plt.suptitle('第8章 热传导方程：温度分布随时间衰减到稳态', fontsize=14, fontweight='bold', color='#1B3A5C')
    plt.tight_layout(); return fig


# ==================== 第9章 S-L方程 ====================

def plot_sl_eigenfunctions():
    x = np.linspace(0, 1, 500); n_values = [1, 2, 3, 4]; colors = ['#1B3A5C', '#C8923A', '#2E8B57', '#8B4513']
    fig, ax = plt.subplots(figsize=(10, 6))
    for n, color in zip(n_values, colors):
        y = np.sin(n * np.pi * x)
        ax.plot(x, y, color=color, lw=2, label=f'n={n}: $y_n = \\sin({n}\\pi x)$, $\\lambda_n = {n}^2\\pi^2$')
        zeros = np.arange(1, n) / n
        for z in zeros: ax.axvline(x=z, color=color, linestyle='--', alpha=0.3, linewidth=0.8)
    ax.axhline(y=0, color='k', lw=0.8)
    ax.set_title('S-L 本征函数族：$y\'\' + \\lambda y = 0$, $y(0)=y(1)=0$\n本征函数 $y_n = \\sin(n\\pi x)$, 本征值 $\\lambda_n = n^2\\pi^2$', fontsize=12, color='#1B3A5C', fontweight='bold')
    ax.set_xlabel('x'); ax.set_ylabel('y'); ax.set_xlim(0, 1); ax.set_ylim(-1.5, 1.5); ax.grid(True, alpha=0.3); ax.legend(loc='upper right', fontsize=9)
    ax.text(0.02, 0.98, 'Sturm 零点定理：\n第 n 个本征函数有 n-1 个内部零点', transform=ax.transAxes, fontsize=9, verticalalignment='top', color='#1B3A5C', bbox=dict(boxstyle='round', facecolor='#f0f4f8', alpha=0.8))
    plt.tight_layout(); return fig


def plot_sl_orthogonality():
    x = np.linspace(0, 1, 500); m, n = 1, 2
    y_m = np.sin(m * np.pi * x); y_n = np.sin(n * np.pi * x)
    product_mn = y_m * y_n; product_mm = y_m * y_m
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    ax = axes[0, 0]
    ax.plot(x, y_m, '#1B3A5C', lw=2, label=f'$y_m = \\sin({m}\\pi x)$')
    ax.plot(x, y_n, '#C8923A', lw=2, label=f'$y_n = \\sin({n}\\pi x)$')
    ax.axhline(y=0, color='k', lw=0.5)
    ax.set_title(f'本征函数 $y_m$ 和 $y_n$', fontsize=12, color='#1B3A5C'); ax.set_xlabel('x'); ax.legend(loc='upper right'); ax.set_xlim(0, 1); ax.grid(True, alpha=0.3)
    ax = axes[0, 1]; ax.axis('off')
    text = r"S-L 正交性：" + "\n\n" + r"$\int_0^1 y_m(x) \, y_n(x) \, dx = 0$" + "\n" + r"$(m \neq n)$" + "\n\n" + r"$\int_0^1 y_m^2(x) \, dx = \frac{1}{2} > 0$" + "\n" + r"（带权正交）" + "\n\n" + r"物理意义：不同" + "\n" + r"振动模式互相独立，" + "\n" + r"能量不耦合。"
    ax.text(0.5, 0.5, text, transform=ax.transAxes, fontsize=12, verticalalignment='center', horizontalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    ax = axes[1, 0]
    ax.fill_between(x, product_mn, 0, where=(product_mn > 0), color='green', alpha=0.4, label='正面积')
    ax.fill_between(x, product_mn, 0, where=(product_mn < 0), color='red', alpha=0.4, label='负面积')
    ax.plot(x, product_mn, 'k-', lw=1.5); ax.axhline(y=0, color='k', lw=0.5)
    integral_mn = np.trapezoid(product_mn, x)
    ax.set_title(f'$y_m \\cdot y_n$ 乘积曲线\n积分 = {integral_mn:.4f} ≈ 0（正负抵消）', fontsize=11, color='#1B3A5C')
    ax.set_xlabel('x'); ax.set_ylabel('$y_m \\cdot y_n$'); ax.legend(loc='upper right'); ax.set_xlim(0, 1); ax.grid(True, alpha=0.3)
    ax = axes[1, 1]
    ax.fill_between(x, product_mm, 0, color='#1B3A5C', alpha=0.5); ax.plot(x, product_mm, '#1B3A5C', lw=2); ax.axhline(y=0, color='k', lw=0.5)
    integral_mm = np.trapezoid(product_mm, x)
    ax.set_title(f'$y_m^2$ 平方曲线\n积分 = {integral_mm:.4f} > 0（正定）', fontsize=11, color='#1B3A5C')
    ax.set_xlabel('x'); ax.set_ylabel('$y_m^2$'); ax.set_xlim(0, 1); ax.grid(True, alpha=0.3)
    plt.suptitle('Sturm-Liouville 正交性定理：不同本征函数正交，同一函数正定', fontsize=14, fontweight='bold', color='#1B3A5C')
    plt.tight_layout(); return fig


# ==================== 第10章 球函数 ====================

def plot_legendre_polynomials():
    """展示勒让德多项式 P_l(x)"""
    x = np.linspace(-1, 1, 500)
    fig, ax = plt.subplots(figsize=(10, 6))
    P = [np.ones_like(x), x, 0.5*(3*x**2-1), 0.5*(5*x**3-3*x), (1/8)*(35*x**4-30*x**2+3)]
    labels = ['P0(x)=1', 'P1(x)=x', 'P2(x)=(3x2-1)/2', 'P3(x)=(5x3-3x)/2', 'P4(x)=(35x4-30x2+3)/8']
    colors = ['#1B3A5C', '#C8923A', '#2E8B57', '#8B4513', '#4B0082']
    for p, label, c in zip(P, labels, colors):
        ax.plot(x, p, color=c, lw=2, label=label)
    ax.axhline(y=0, color='k', lw=0.5); ax.axvline(x=0, color='k', lw=0.5)
    ax.set_xlim(-1, 1); ax.set_ylim(-1.2, 1.2)
    ax.set_xlabel('x'); ax.set_ylabel('Pl(x)')
    ax.set_title('勒让德多项式 Pl(x)：前 5 个\nRodrigue 公式：Pl(x) = (1/2^l l!) d^l/dx^l (x2-1)^l', fontsize=12, color='#1B3A5C', fontweight='bold')
    ax.legend(loc='upper left', fontsize=10); ax.grid(True, alpha=0.3)
    ax.text(0.5, -0.12, 'Pl(1)=1, Pl(-1)=(-1)^l, 零点数=l', transform=ax.transAxes, fontsize=10, ha='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    plt.tight_layout(); return fig


def plot_spherical_harmonics():
    """展示球谐函数的模分布"""
    theta = np.linspace(0, np.pi, 200); phi = np.linspace(0, 2*np.pi, 200)
    THETA, PHI = np.meshgrid(theta, phi)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), subplot_kw=dict(projection='polar'))
    Y00 = np.ones_like(THETA) * 0.5
    ax = axes[0]
    ax.contourf(PHI, THETA, np.abs(Y00), levels=20, cmap='viridis')
    ax.set_title('Y00 = 常数\n(l=0, 球对称)', fontsize=11, color='#1B3A5C', pad=20)
    Y10 = np.cos(THETA)
    ax = axes[1]
    ax.contourf(PHI, THETA, np.abs(Y10), levels=20, cmap='RdBu_r')
    ax.set_title('Y10 ∝ cos(θ)\n(l=1, 偶极)', fontsize=11, color='#1B3A5C', pad=20)
    Y20 = 0.5*(3*np.cos(THETA)**2 - 1)
    ax = axes[2]
    ax.contourf(PHI, THETA, np.abs(Y20), levels=20, cmap='plasma')
    ax.set_title('Y20 ∝ (3cos2θ-1)\n(l=2, 四极)', fontsize=11, color='#1B3A5C', pad=20)
    plt.suptitle('第10章 球谐函数：|Ylm(θ,φ)| 的角分布', fontsize=14, fontweight='bold', color='#1B3A5C')
    plt.tight_layout(); return fig


# ==================== 第11章 柱函数 ====================

def plot_bessel_functions():
    """展示贝塞尔函数 J_ν(x)"""
    x = np.linspace(0, 20, 500)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    ax = axes[0]
    from scipy.special import jv
    orders = [0, 1, 2, 3]; colors = ['#1B3A5C', '#C8923A', '#2E8B57', '#8B4513']
    for nu, c in zip(orders, colors):
        ax.plot(x, jv(nu, x), color=c, lw=2, label=f'J_{nu}(x)')
    ax.axhline(y=0, color='k', lw=0.5)
    ax.set_xlim(0, 20); ax.set_ylim(-0.6, 1.1)
    ax.set_xlabel('x'); ax.set_ylabel('Jν(x)')
    ax.set_title('贝塞尔函数 Jν(x)：前 4 个阶数\nJ0(0)=1, Jν(0)=0 (ν>0)', fontsize=12, color='#1B3A5C')
    ax.legend(loc='upper right'); ax.grid(True, alpha=0.3)
    ax = axes[1]
    x_large = np.linspace(5, 50, 500)
    J0_large = jv(0, x_large)
    envelope = np.sqrt(2/(np.pi*x_large))
    ax.plot(x_large, J0_large, '#1B3A5C', lw=1.5, label='J0(x)')
    ax.plot(x_large, envelope, 'r--', lw=1.5, label='包络 √(2/πx)')
    ax.plot(x_large, -envelope, 'r--', lw=1.5)
    ax.fill_between(x_large, envelope, -envelope, alpha=0.1, color='red')
    ax.axhline(y=0, color='k', lw=0.5)
    ax.set_xlim(5, 50); ax.set_ylim(-0.4, 0.4)
    ax.set_xlabel('x'); ax.set_ylabel('J0(x)')
    ax.set_title('渐近行为：Jν(x) ~ √(2/πx) cos(x-νπ/2-π/4)\n振幅按 1/√x 衰减', fontsize=12, color='#1B3A5C')
    ax.legend(loc='upper right'); ax.grid(True, alpha=0.3)
    plt.suptitle('第11章 贝塞尔函数：振荡衰减特性', fontsize=14, fontweight='bold', color='#1B3A5C')
    plt.tight_layout(); return fig


def plot_bessel_zeros():
    """展示贝塞尔函数的零点分布"""
    from scipy.special import jv, jn_zeros
    x = np.linspace(0, 20, 500)
    fig, ax = plt.subplots(figsize=(10, 6))
    J0 = jv(0, x); J1 = jv(1, x)
    ax.plot(x, J0, '#1B3A5C', lw=2, label='J0(x)')
    ax.plot(x, J1, '#C8923A', lw=2, label='J1(x)')
    zeros_j0 = jn_zeros(0, 5)
    colors = ['green', 'purple', 'brown', 'pink', 'gray']
    for i, z in enumerate(zeros_j0):
        ax.axvline(x=z, color=colors[i], linestyle='--', alpha=0.7, lw=1.5)
        ax.plot(z, 0, 'o', color=colors[i], markersize=10)
        ax.text(z, 0.15, f'z_{i+1}={z:.3f}', fontsize=9, color=colors[i], ha='center')
    ax.axhline(y=0, color='k', lw=0.8)
    ax.set_xlim(0, 16); ax.set_ylim(-0.6, 1.1)
    ax.set_xlabel('x'); ax.set_ylabel('Jν(x)')
    ax.set_title('贝塞尔函数零点分布：J0(x) 的前 5 个正零点\n零点间距趋近于 π（渐近行为）', fontsize=12, color='#1B3A5C', fontweight='bold')
    ax.legend(loc='upper right'); ax.grid(True, alpha=0.3)
    plt.tight_layout(); return fig


# ==================== 第12章 格林函数 ====================

def plot_green_function_1d():
    """展示一维格林函数：分段线性"""
    x = np.linspace(0, 1, 500); x_prime = 0.3
    fig, ax = plt.subplots(figsize=(10, 6))
    x_primes = [0.2, 0.5, 0.8]
    colors = ['#1B3A5C', '#C8923A', '#2E8B57']
    for xp, c in zip(x_primes, colors):
        G = np.zeros_like(x)
        for i, xi in enumerate(x):
            if xi < xp: G[i] = -xi*(1-xp)
            else: G[i] = -xp*(1-xi)
        ax.plot(x, G, color=c, lw=2.5, label=f'G(x, x\'={xp})')
        ax.plot(xp, 0, 'o', color=c, markersize=10)
    ax.axhline(y=0, color='k', lw=0.8)
    ax.set_xlim(0, 1); ax.set_ylim(-0.3, 0.1)
    ax.set_xlabel('x'); ax.set_ylabel('G(x, x\')')
    ax.set_title('一维格林函数：G(x, x\') = -x(1-x\') (x<x\') 或 -x\'(1-x) (x>x\')\n在 x=x\' 处斜率跃变 = 1，其余处线性', fontsize=12, color='#1B3A5C', fontweight='bold')
    ax.legend(loc='lower left'); ax.grid(True, alpha=0.3)
    ax.text(0.5, -0.12, '物理意义：在 x\' 处施加单位力，弦的位移分布', transform=ax.transAxes, fontsize=10, ha='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    plt.tight_layout(); return fig


def plot_green_superposition():
    """展示格林函数的叠加原理"""
    x = np.linspace(0, 1, 500)
    fig, ax = plt.subplots(figsize=(10, 6))
    f = np.sin(np.pi * x)
    u_exact = np.sin(np.pi * x) / np.pi**2
    ax.fill_between(x, 0, f, alpha=0.2, color='red', label='源分布 f(x)=sin(πx)')
    ax.plot(x, f, 'r--', lw=1.5, label='')
    ax.plot(x, u_exact, '#1B3A5C', lw=2.5, label='响应 u(x) = ∫ G(x,x\')f(x\')dx\' = sin(πx)/π²')
    ax.axhline(y=0, color='k', lw=0.5)
    ax.set_xlim(0, 1); ax.set_ylim(-0.2, 1.2)
    ax.set_xlabel('x'); ax.set_ylabel('u(x)')
    ax.set_title('格林函数叠加原理：连续分布源 = 各点源响应的积分叠加', fontsize=12, color='#1B3A5C', fontweight='bold')
    ax.legend(loc='upper right'); ax.grid(True, alpha=0.3)
    plt.tight_layout(); return fig


# ==================== 第13章 积分变换法 ====================

def plot_heat_kernel_diffusion():
    """展示热核扩散过程"""
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    x = np.linspace(-5, 5, 500); a = 1.0
    times = [0.01, 0.05, 0.1, 0.3, 0.5, 1.0]
    for idx, t in enumerate(times):
        ax = axes[idx // 3, idx % 3]
        kernel = 1/(2*a*np.sqrt(np.pi*t)) * np.exp(-x**2/(4*a**2*t))
        ax.fill_between(x, 0, kernel, alpha=0.4, color='#C8923A')
        ax.plot(x, kernel, '#1B3A5C', lw=2.5)
        ax.set_xlim(-5, 5); ax.set_ylim(0, 3)
        ax.set_title(f't = {t:.2f}', fontsize=12, color='#1B3A5C')
        ax.set_xlabel('x'); ax.set_ylabel('u(x,t)')
        ax.grid(True, alpha=0.3)
    plt.suptitle('第13章 热核扩散：初始点热源 u(x,0)=δ(x) 的演化\nu(x,t) = (1/2a√πt) exp(-x²/4a²t)', fontsize=14, fontweight='bold', color='#1B3A5C')
    plt.tight_layout(); return fig


# ==================== 第14章 保角变换 ====================

def plot_conformal_examples():
    """展示常用保角变换的效果"""
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    x = np.linspace(-2, 2, 20); y = np.linspace(-2, 2, 20)
    X, Y = np.meshgrid(x, y); Z = X + 1j*Y
    # 1. z^2
    ax = axes[0, 0]
    W = Z**2; U, V = W.real, W.imag
    for i in range(len(x)): ax.plot(U[i, :], V[i, :], 'b-', alpha=0.4, lw=0.8); ax.plot(U[:, i], V[:, i], 'r-', alpha=0.4, lw=0.8)
    ax.set_aspect('equal'); ax.set_title('w = z²\n第一象限 → 上半平面', fontsize=11, color='#1B3A5C')
    ax.set_xlabel('Re(w)'); ax.set_ylabel('Im(w)'); ax.grid(True, alpha=0.3)
    # 2. e^z
    ax = axes[0, 1]
    x2 = np.linspace(-1, 1, 20); y2 = np.linspace(0, np.pi, 20)
    X2, Y2 = np.meshgrid(x2, y2); Z2 = X2 + 1j*Y2; W2 = np.exp(Z2); U2, V2 = W2.real, W2.imag
    for i in range(len(x2)): ax.plot(U2[i, :], V2[i, :], 'b-', alpha=0.4, lw=0.8); ax.plot(U2[:, i], V2[:, i], 'r-', alpha=0.4, lw=0.8)
    ax.set_aspect('equal'); ax.set_title('w = e^z\n带域 0<Im(z)<π → 上半平面', fontsize=11, color='#1B3A5C')
    ax.set_xlabel('Re(w)'); ax.set_ylabel('Im(w)'); ax.grid(True, alpha=0.3)
    # 3. 1/z
    ax = axes[0, 2]
    x3 = np.linspace(1, 3, 20); y3 = np.linspace(-2, 2, 20)
    X3, Y3 = np.meshgrid(x3, y3); Z3 = X3 + 1j*Y3; W3 = 1/Z3; U3, V3 = W3.real, W3.imag
    for i in range(len(x3)): ax.plot(U3[i, :], V3[i, :], 'b-', alpha=0.4, lw=0.8); ax.plot(U3[:, i], V3[:, i], 'r-', alpha=0.4, lw=0.8)
    ax.set_aspect('equal'); ax.set_title('w = 1/z\n圆外 → 圆内（反演）', fontsize=11, color='#1B3A5C')
    ax.set_xlabel('Re(w)'); ax.set_ylabel('Im(w)'); ax.grid(True, alpha=0.3)
    # 4. 分式线性
    ax = axes[1, 0]
    theta = np.linspace(0, 2*np.pi, 100)
    ax.plot(np.cos(theta), np.sin(theta), 'b-', lw=2, label='原圆 |z|=1')
    ax.set_aspect('equal'); ax.set_title('分式线性变换\n保圆性：圆/直线 → 圆/直线', fontsize=11, color='#1B3A5C')
    ax.set_xlabel('Re(w)'); ax.set_ylabel('Im(w)'); ax.grid(True, alpha=0.3); ax.legend()
    # 5. ln z
    ax = axes[1, 1]
    x5 = np.linspace(0.5, 3, 20); y5 = np.linspace(0.5, 3, 20)
    X5, Y5 = np.meshgrid(x5, y5); Z5 = X5 + 1j*Y5; W5 = np.log(Z5); U5, V5 = W5.real, W5.imag
    for i in range(len(x5)): ax.plot(U5[i, :], V5[i, :], 'b-', alpha=0.4, lw=0.8); ax.plot(U5[:, i], V5[:, i], 'r-', alpha=0.4, lw=0.8)
    ax.set_aspect('equal'); ax.set_title('w = ln z\n第一象限 → 带域', fontsize=11, color='#1B3A5C')
    ax.set_xlabel('Re(w)'); ax.set_ylabel('Im(w)'); ax.grid(True, alpha=0.3)
    # 6. z^0.5
    ax = axes[1, 2]
    x6 = np.linspace(0, 2, 20); y6 = np.linspace(0, 2, 20)
    X6, Y6 = np.meshgrid(x6, y6); Z6 = X6 + 1j*Y6; W6 = Z6**0.5; U6, V6 = W6.real, W6.imag
    for i in range(len(x6)): ax.plot(U6[i, :], V6[i, :], 'b-', alpha=0.4, lw=0.8); ax.plot(U6[:, i], V6[:, i], 'r-', alpha=0.4, lw=0.8)
    ax.set_aspect('equal'); ax.set_title('w = z^{1/2}\n第一象限 → 第一象限（展宽）', fontsize=11, color='#1B3A5C')
    ax.set_xlabel('Re(w)'); ax.set_ylabel('Im(w)'); ax.grid(True, alpha=0.3)
    plt.suptitle('第14章 保角变换：常用变换的映射效果', fontsize=14, fontweight='bold', color='#1B3A5C')
    plt.tight_layout(); return fig


# ==================== 第15章 非线性问题 ====================

def plot_kdv_soliton():
    """展示KdV方程的孤立子解"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    x = np.linspace(-10, 10, 500); t_values = [0, 2, 4, 6]
    colors = ['#1B3A5C', '#C8923A', '#2E8B57', '#8B4513']
    ax = axes[0]
    c = 1.0
    for t, color in zip(t_values, colors):
        xi = x - c*t
        u = -0.5*c * (1/np.cosh(np.sqrt(c)*xi/2))**2
        ax.plot(x, u, color=color, lw=2, label=f't = {t}')
    ax.set_xlim(-10, 10); ax.set_ylim(-0.6, 0.1)
    ax.set_xlabel('x'); ax.set_ylabel('u(x,t)')
    ax.set_title('KdV 孤立子解：形状不变，速度恒定\nu(x,t) = -c/2 · sech²[√c(x-ct)/2]', fontsize=12, color='#1B3A5C')
    ax.legend(loc='upper right'); ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', lw=0.5)
    ax = axes[1]
    x_spacetime = np.linspace(-10, 15, 300); t_spacetime = np.linspace(0, 8, 300)
    X_st, T_st = np.meshgrid(x_spacetime, t_spacetime)
    U_st = -0.5*c * (1/np.cosh(np.sqrt(c)*(X_st - c*T_st)/2))**2
    im = ax.contourf(X_st, T_st, U_st, levels=50, cmap='RdBu_r')
    plt.colorbar(im, ax=ax, label='u(x,t)')
    ax.set_xlabel('x'); ax.set_ylabel('t')
    ax.set_title('孤立子时空轨迹：直线 x = ct', fontsize=12, color='#1B3A5C')
    ax.grid(True, alpha=0.3)
    plt.suptitle('第15章 KdV 孤立子：色散与非线性的平衡', fontsize=14, fontweight='bold', color='#1B3A5C')
    plt.tight_layout(); return fig


# ==================== 动态动画函数 ====================

def _save_anim_to_bytes(anim, fps=10, dpi=120):
    """将 FuncAnimation 保存为 GIF 并返回 bytes"""
    with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as tmp:
        tmp_path = tmp.name
    try:
        anim.save(tmp_path, writer='pillow', fps=fps, dpi=dpi)
        with open(tmp_path, 'rb') as f:
            return f.read()
    finally:
        plt.close()
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def _fig_to_gif_bytes(fig, frames=60, interval=80):
    """将 matplotlib Figure 渲染为 GIF 并返回 bytes"""
    anim = FuncAnimation(fig, lambda i: None, frames=frames, interval=interval)
    return _save_anim_to_bytes(anim, fps=1000//interval, dpi=120)


def animate_dalembert():
    """达朗贝尔公式：波传播动画"""
    x = np.linspace(-10, 10, 500)
    a = 1.0
    phi = np.zeros_like(x)
    phi[(x > -2) & (x < 2)] = 1 - np.abs(x[(x > -2) & (x < 2)]) / 2

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(-10, 10); ax.set_ylim(-0.5, 1.5)
    ax.set_xlabel('x'); ax.set_ylabel('u(x,t)')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', lw=0.5)

    line_right, = ax.plot([], [], 'b-', alpha=0.5, lw=2.5, label='φ(x+at) 右行波')
    line_left, = ax.plot([], [], 'r-', alpha=0.5, lw=2.5, label='φ(x-at) 左行波')
    line_sum, = ax.plot([], [], 'k-', lw=3, label='u(x,t) 合成波')
    time_text = ax.text(0.02, 0.92, '', transform=ax.transAxes, fontsize=12)

    ax.set_title('达朗贝尔公式：初始位移分解为左右传播的两列波', fontsize=13, color='#1B3A5C', fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)

    def init():
        line_right.set_data([], []); line_left.set_data([], []); line_sum.set_data([], [])
        time_text.set_text('')
        return line_right, line_left, line_sum, time_text

    def update(frame):
        t = frame * 0.1
        phi_right = np.interp(x + a*t, x, phi, left=0, right=0)
        phi_left = np.interp(x - a*t, x, phi, left=0, right=0)
        u = 0.5 * (phi_right + phi_left)
        line_right.set_data(x, phi_right)
        line_left.set_data(x, phi_left)
        line_sum.set_data(x, u)
        time_text.set_text(f't = {t:.1f}')
        return line_right, line_left, line_sum, time_text

    anim = FuncAnimation(fig, update, frames=50, init_func=init, interval=100, blit=True)
    return _save_anim_to_bytes(anim, fps=10)


def animate_separation_modes():
    """分离变量法：驻波模式叠加动画"""
    x = np.linspace(0, 1, 500)
    L, a_v = 1.0, 1.0

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 1); ax.set_ylim(-1.8, 1.8)
    ax.set_xlabel('x'); ax.set_ylabel('u(x,t)')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', lw=0.5)

    line1, = ax.plot([], [], '--', color='#1B3A5C', lw=1, alpha=0.6, label='模式 n=1')
    line2, = ax.plot([], [], '--', color='#C8923A', lw=1, alpha=0.6, label='模式 n=2')
    line3, = ax.plot([], [], '--', color='#2E8B57', lw=1, alpha=0.6, label='模式 n=3')
    line_sum, = ax.plot([], [], 'k-', lw=3, label='叠加 u(x,t)')
    time_text = ax.text(0.02, 0.92, '', transform=ax.transAxes, fontsize=12)

    ax.set_title('分离变量法：弦振动前3个驻波模式叠加', fontsize=13, color='#1B3A5C', fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)

    def init():
        line1.set_data([], []); line2.set_data([], []); line3.set_data([], [])
        line_sum.set_data([], []); time_text.set_text('')
        return line1, line2, line3, line_sum, time_text

    def update(frame):
        t = frame * 0.03
        u = np.zeros_like(x)
        m1 = np.sin(1*np.pi*x/L) * np.cos(1*np.pi*a_v*t/L)
        m2 = np.sin(2*np.pi*x/L) * np.cos(2*np.pi*a_v*t/L)
        m3 = np.sin(3*np.pi*x/L) * np.cos(3*np.pi*a_v*t/L)
        u = m1 * (4/np.pi) + m3 * (4/(3*np.pi))
        line1.set_data(x, m1); line2.set_data(x, m2); line3.set_data(x, m3)
        line_sum.set_data(x, u)
        time_text.set_text(f't = {t:.2f}')
        return line1, line2, line3, line_sum, time_text

    anim = FuncAnimation(fig, update, frames=70, init_func=init, interval=100, blit=True)
    return _save_anim_to_bytes(anim, fps=10)


def animate_heat_evolution():
    """热传导方程：温度演化动画"""
    x = np.linspace(0, 1, 500)
    L, a_v = 1.0, 1.0

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 1); ax.set_ylim(-0.2, 1.5)
    ax.set_xlabel('x'); ax.set_ylabel('T(x,t)')
    ax.grid(True, alpha=0.3)

    fill = ax.fill_between([], [], alpha=0.3, color='#C8923A')
    line, = ax.plot([], [], '#1B3A5C', lw=2.5)
    time_text = ax.text(0.02, 0.92, '', transform=ax.transAxes, fontsize=12)

    ax.set_title('热传导方程：温度分布随时间衰减到稳态', fontsize=13, color='#1B3A5C', fontweight='bold')

    def init():
        line.set_data([], []); time_text.set_text('')
        return line, time_text

    def update(frame):
        t = frame * 0.002
        u = np.zeros_like(x)
        for n, A in [(1, 1.0), (3, 0.3), (5, 0.1)]:
            u += A * np.sin(n*np.pi*x/L) * np.exp(-(n*np.pi*a_v/L)**2 * t)
        for coll in list(ax.collections): coll.remove()
        ax.fill_between(x, 0, u, alpha=0.3, color='#C8923A')
        line.set_data(x, u)
        time_text.set_text(f't = {t:.3f}')
        return line, time_text

    anim = FuncAnimation(fig, update, frames=100, init_func=init, interval=80, blit=False)
    return _save_anim_to_bytes(anim, fps=12)


def animate_heat_kernel():
    """热核扩散动画"""
    x = np.linspace(-5, 5, 500)
    a = 1.0

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(-5, 5); ax.set_ylim(0, 3)
    ax.set_xlabel('x'); ax.set_ylabel('u(x,t)')
    ax.grid(True, alpha=0.3)

    fill = ax.fill_between([], [], alpha=0.4, color='#C8923A')
    line, = ax.plot([], [], '#1B3A5C', lw=2.5)
    time_text = ax.text(0.02, 0.92, '', transform=ax.transAxes, fontsize=12)

    ax.set_title('热核扩散：初始点热源 u(x,0)=δ(x) 的演化\nu(x,t) = exp(-x²/4a²t) / (2a√πt)', fontsize=12, color='#1B3A5C', fontweight='bold')

    def init():
        line.set_data([], []); time_text.set_text('')
        return line, time_text

    def update(frame):
        t = 0.01 + frame * 0.015
        kernel = 1/(2*a*np.sqrt(np.pi*t)) * np.exp(-x**2/(4*a**2*t))
        for coll in list(ax.collections): coll.remove()
        ax.fill_between(x, 0, kernel, alpha=0.4, color='#C8923A')
        line.set_data(x, kernel)
        time_text.set_text(f't = {t:.3f}  宽度 ∝ √t')
        return line, time_text

    anim = FuncAnimation(fig, update, frames=80, init_func=init, interval=80, blit=False)
    return _save_anim_to_bytes(anim, fps=12)


def animate_kdv_soliton():
    """KdV孤立子行进动画"""
    x = np.linspace(-10, 15, 500)
    c = 1.0

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(-10, 15); ax.set_ylim(-0.6, 0.1)
    ax.set_xlabel('x'); ax.set_ylabel('u(x,t)')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', lw=0.5)

    fill = ax.fill_between([], [], alpha=0.35, color='#C8923A')
    line, = ax.plot([], [], '#1B3A5C', lw=2.5)
    time_text = ax.text(0.02, 0.92, '', transform=ax.transAxes, fontsize=12)

    ax.set_title('KdV孤立子：形状不变、速度恒定的行波\nu(x,t) = -c/2 · sech²[√c(x-ct)/2]', fontsize=12, color='#1B3A5C', fontweight='bold')

    def init():
        line.set_data([], []); time_text.set_text('')
        return line, time_text

    def update(frame):
        t = frame * 0.15
        xi = x - c*t
        u = -0.5*c * (1/np.cosh(np.sqrt(c)*xi/2))**2
        for coll in list(ax.collections): coll.remove()
        ax.fill_between(x, 0, u, alpha=0.35, color='#C8923A')
        line.set_data(x, u)
        time_text.set_text(f't = {t:.1f}  速度 c={c}')
        return line, time_text

    anim = FuncAnimation(fig, update, frames=80, init_func=init, interval=80, blit=False)
    return _save_anim_to_bytes(anim, fps=12)


def animate_complex_sine_build():
    """复三角函数 |sin z| 从实轴到复平面的构建动画"""
    x = np.linspace(-np.pi, np.pi, 200)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_xlim(-np.pi, np.pi); ax.set_ylim(0, 4)
    ax.set_xlabel('x'); ax.set_ylabel('|sin z|')
    ax.grid(True, alpha=0.3)
    for n in range(-1, 2): ax.axvline(x=n*np.pi, color='cyan', linestyle='--', alpha=0.5)

    line, = ax.plot([], [], '#C8923A', lw=2.5)
    y_text = ax.text(0.02, 0.92, '', transform=ax.transAxes, fontsize=12)
    ax.set_title('复三角函数 |sin z|：随虚部 y 增大而指数增长', fontsize=13, color='#1B3A5C', fontweight='bold')

    def init():
        line.set_data([], []); y_text.set_text('')
        return line, y_text

    def update(frame):
        y = frame * 0.05
        z = x + 1j*y
        modulus = np.abs(np.sin(z))
        line.set_data(x, modulus)
        y_text.set_text(f'y = {y:.2f}   |sin(x+iy)|² = sin²x + sinh²y')
        ax.set_ylim(0, max(4, np.max(modulus)*1.1))
        return line, y_text

    anim = FuncAnimation(fig, update, frames=60, init_func=init, interval=80, blit=True)
    return _save_anim_to_bytes(anim, fps=12)


# -------------------- 第1章: C-R 方程梯度旋转动画 --------------------
def animate_cr_gradient():
    """展示C-R方程梯度正交性：旋转箭头"""
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_xlim(-1.8, 1.8); ax.set_ylim(-1.8, 1.8)
    ax.set_aspect('equal'); ax.grid(True, alpha=0.3)
    x_g = np.linspace(-1.5, 1.5, 100); y_g = np.linspace(-1.5, 1.5, 100)
    X_g, Y_g = np.meshgrid(x_g, y_g)
    U_bg = X_g**2 - Y_g**2; V_bg = 2*X_g*Y_g
    ax.contour(X_g, Y_g, U_bg, levels=8, colors='#1B3A5C', alpha=0.25, linewidths=0.6)
    ax.contour(X_g, Y_g, V_bg, levels=8, colors='#C8923A', alpha=0.25, linewidths=0.6, linestyles='--')

    theta_angle = np.linspace(0, 2*np.pi, 12)
    r = 1.0
    points = np.array([[r*np.cos(t), r*np.sin(t)] for t in theta_angle])
    px0, py0 = points[0]
    du0 = np.array([2*px0, -2*py0]) * 0.18
    dv0 = np.array([2*py0, 2*px0]) * 0.18
    X_q = np.array([px0, px0])
    Y_q = np.array([py0, py0])
    U_q = np.array([du0[0], dv0[0]])
    V_q = np.array([du0[1], dv0[1]])
    quiver = ax.quiver(X_q, Y_q, U_q, V_q, scale=3, width=0.008, color=['#1B3A5C','#C8923A'])
    dot, = ax.plot([px0], [py0], 'ko', markersize=4)
    title_text = ax.text(0.5, 1.02, 'C-R方程几何: ∇u ⟂ ∇v   |∇u|=|∇v|',
                         transform=ax.transAxes, fontsize=12, ha='center', color='#1B3A5C', fontweight='bold')

    def update(frame):
        px, py = points[frame % 12]
        du = np.array([2*px, -2*py]) * 0.18
        dv = np.array([2*py, 2*px]) * 0.18
        quiver.set_offsets([[px, py], [px, py]])
        quiver.set_UVC([du[0], dv[0]], [du[1], dv[1]])
        dot.set_data([px], [py])
        title_text.set_text(f'C-R方程几何: ∇u ⟂ ∇v   |∇u|=|∇v|  点: ({px:.1f},{py:.1f})')
        return quiver, dot, title_text

    anim = FuncAnimation(fig, update, frames=60, interval=120, blit=True)
    return _save_anim_to_bytes(anim, fps=8)


# -------------------- 第1章: 解析函数映射过程动画 --------------------
def animate_analytic_mapping():
    """展示z^2映射过程：从z平面连续过渡到w平面"""
    z_lim = 2.0; n_grid = 16
    x = np.linspace(-z_lim, z_lim, n_grid); y = np.linspace(-z_lim, z_lim, n_grid)
    X, Y = np.meshgrid(x, y); Z = X + 1j*Y

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    ax_z, ax_w = axes[0], axes[1]
    for ax in axes:
        ax.set_aspect('equal'); ax.set_xlim(-z_lim, z_lim); ax.set_ylim(-z_lim, z_lim)
        ax.set_xlabel('Re'); ax.set_ylabel('Im'); ax.grid(True, alpha=0.3)

    lines_z_h = [ax_z.plot([], [], 'b-', alpha=0.5, lw=0.7)[0] for _ in range(n_grid)]
    lines_z_v = [ax_z.plot([], [], 'r-', alpha=0.5, lw=0.7)[0] for _ in range(n_grid)]
    lines_w_h = [ax_w.plot([], [], 'b-', alpha=0.5, lw=0.7)[0] for _ in range(n_grid)]
    lines_w_v = [ax_w.plot([], [], 'r-', alpha=0.5, lw=0.7)[0] for _ in range(n_grid)]
    title_z = ax_z.set_title('z-平面 (原像)', fontsize=12, color='#1B3A5C')
    title_w = ax_w.set_title('w-平面 (像): w=z²', fontsize=12, color='#C8923A')

    def init():
        for l in lines_z_h + lines_z_v + lines_w_h + lines_w_v:
            l.set_data([], [])
        return lines_z_h + lines_z_v + lines_w_h + lines_w_v

    def update(frame):
        t = frame / 40.0  # 0到1插值
        for i in range(n_grid):
            lines_z_h[i].set_data(X[i,:], Y[i,:])
            lines_z_v[i].set_data(X[:,i], Y[:,i])
            W = Z**2; W_interp = (1-t)*Z + t*W
            U, V = W_interp.real, W_interp.imag
            lines_w_h[i].set_data(U[i,:], V[i,:])
            lines_w_v[i].set_data(U[:,i], V[:,i])
        title_w.set_text(f'w-平面 (像): t={t:.2f}  w=z²')
        return lines_z_h + lines_z_v + lines_w_h + lines_w_v

    anim = FuncAnimation(fig, update, frames=45, init_func=init, interval=100, blit=True)
    plt.suptitle('解析函数映射过程: z → z²', fontsize=14, fontweight='bold', color='#1B3A5C')
    return _save_anim_to_bytes(anim, fps=10)


# -------------------- 第1章: 通用解析函数映射动画 (z^n) --------------------
def animate_analytic_mapping_power(n=2, title_suffix="z²"):
    """展示z^n映射过程：从z平面连续过渡到w平面"""
    z_lim = 2.0 if n <= 2 else 1.5
    n_grid = 16
    x = np.linspace(-z_lim, z_lim, n_grid); y = np.linspace(-z_lim, z_lim, n_grid)
    X, Y = np.meshgrid(x, y); Z = X + 1j*Y

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    ax_z, ax_w = axes[0], axes[1]
    for ax in axes:
        ax.set_aspect('equal'); ax.set_xlim(-z_lim, z_lim); ax.set_ylim(-z_lim, z_lim)
        ax.set_xlabel('Re'); ax.set_ylabel('Im'); ax.grid(True, alpha=0.3)

    lines_z_h = [ax_z.plot([], [], 'b-', alpha=0.5, lw=0.7)[0] for _ in range(n_grid)]
    lines_z_v = [ax_z.plot([], [], 'r-', alpha=0.5, lw=0.7)[0] for _ in range(n_grid)]
    lines_w_h = [ax_w.plot([], [], 'b-', alpha=0.5, lw=0.7)[0] for _ in range(n_grid)]
    lines_w_v = [ax_w.plot([], [], 'r-', alpha=0.5, lw=0.7)[0] for _ in range(n_grid)]
    title_z = ax_z.set_title('z-平面 (原像)', fontsize=12, color='#1B3A5C')
    title_w = ax_w.set_title(f'w-平面 (像): w={title_suffix}', fontsize=12, color='#C8923A')

    def init():
        for l in lines_z_h + lines_z_v + lines_w_h + lines_w_v:
            l.set_data([], [])
        return lines_z_h + lines_z_v + lines_w_h + lines_w_v

    def update(frame):
        t = frame / 40.0
        for i in range(n_grid):
            lines_z_h[i].set_data(X[i,:], Y[i,:])
            lines_z_v[i].set_data(X[:,i], Y[:,i])
            W = Z**n; W_interp = (1-t)*Z + t*W
            U, V = W_interp.real, W_interp.imag
            lines_w_h[i].set_data(U[i,:], V[i,:])
            lines_w_v[i].set_data(U[:,i], V[:,i])
        title_w.set_text(f'w-平面 (像): t={t:.2f}  w={title_suffix}')
        return lines_z_h + lines_z_v + lines_w_h + lines_w_v

    anim = FuncAnimation(fig, update, frames=45, init_func=init, interval=100, blit=True)
    plt.suptitle(f'解析函数映射过程: z → {title_suffix}', fontsize=14, fontweight='bold', color='#1B3A5C')
    return _save_anim_to_bytes(anim, fps=10)


def animate_z_cubed_mapping():
    """展示z^3映射过程"""
    return animate_analytic_mapping_power(n=3, title_suffix="z³")


def animate_exp_mapping():
    """展示e^z映射过程"""
    z_lim = 2.0; n_grid = 16
    x = np.linspace(-z_lim, z_lim, n_grid); y = np.linspace(-z_lim, z_lim, n_grid)
    X, Y = np.meshgrid(x, y); Z = X + 1j*Y

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    ax_z, ax_w = axes[0], axes[1]
    ax_z.set_aspect('equal'); ax_z.set_xlim(-z_lim, z_lim); ax_z.set_ylim(-z_lim, z_lim)
    ax_w.set_aspect('auto'); ax_w.set_xlim(-5, 5); ax_w.set_ylim(-5, 5)
    for ax in axes:
        ax.set_xlabel('Re'); ax.set_ylabel('Im'); ax.grid(True, alpha=0.3)

    lines_z_h = [ax_z.plot([], [], 'b-', alpha=0.5, lw=0.7)[0] for _ in range(n_grid)]
    lines_z_v = [ax_z.plot([], [], 'r-', alpha=0.5, lw=0.7)[0] for _ in range(n_grid)]
    lines_w_h = [ax_w.plot([], [], 'b-', alpha=0.5, lw=0.7)[0] for _ in range(n_grid)]
    lines_w_v = [ax_w.plot([], [], 'r-', alpha=0.5, lw=0.7)[0] for _ in range(n_grid)]
    title_z = ax_z.set_title('z-平面 (原像)', fontsize=12, color='#1B3A5C')
    title_w = ax_w.set_title('w-平面 (像): w=e^z', fontsize=12, color='#C8923A')

    def init():
        for l in lines_z_h + lines_z_v + lines_w_h + lines_w_v:
            l.set_data([], [])
        return lines_z_h + lines_z_v + lines_w_h + lines_w_v

    def update(frame):
        t = frame / 40.0
        for i in range(n_grid):
            lines_z_h[i].set_data(X[i,:], Y[i,:])
            lines_z_v[i].set_data(X[:,i], Y[:,i])
            W = np.exp(Z); W_interp = (1-t)*Z + t*W
            U, V = W_interp.real, W_interp.imag
            lines_w_h[i].set_data(U[i,:], V[i,:])
            lines_w_v[i].set_data(U[:,i], V[:,i])
        title_w.set_text(f'w-平面 (像): t={t:.2f}  w=e^z')
        return lines_z_h + lines_z_v + lines_w_h + lines_w_v

    anim = FuncAnimation(fig, update, frames=45, init_func=init, interval=100, blit=True)
    plt.suptitle('解析函数映射过程: z → e^z', fontsize=14, fontweight='bold', color='#1B3A5C')
    return _save_anim_to_bytes(anim, fps=10)


# -------------------- 第1章: 调和函数等势线/流线动画 --------------------
def animate_harmonic_z2():
    """展示f(z)=z^2的调和函数u=x^2-y^2和v=2xy的等势线逐渐绘制"""
    x = np.linspace(-2, 2, 300); y = np.linspace(-2, 2, 300)
    X, Y = np.meshgrid(x, y); U = X**2 - Y**2; V = 2*X*Y
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.set_xlim(-2, 2); ax.set_ylim(-2, 2); ax.set_aspect('equal')
    ax.set_xlabel('x'); ax.set_ylabel('y')
    ax.set_title('调和函数 f(z)=z²: 等势线 u=常数（蓝）与流线 v=常数（橙）\n正交相交 ⟂', fontsize=12, color='#1B3A5C', fontweight='bold')
    ax.grid(True, alpha=0.3)
    legend_elements = [Line2D([0], [0], color='#1B3A5C', lw=1.5, label='等势线 u = 常数'),
                       Line2D([0], [0], color='#C8923A', lw=1.5, linestyle='--', label='流线 v = 常数')]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

    def update(frame):
        ax.clear(); ax.set_xlim(-2, 2); ax.set_ylim(-2, 2); ax.set_aspect('equal')
        ax.set_xlabel('x'); ax.set_ylabel('y'); ax.grid(True, alpha=0.3)
        t = (frame + 1) / 30.0
        levels = int(4 + t * 16)
        cs1 = ax.contour(X, Y, U, levels=levels, colors='#1B3A5C', linewidths=1.5, alpha=0.8)
        ax.clabel(cs1, inline=True, fontsize=8, fmt='u=%1.1f')
        cs2 = ax.contour(X, Y, V, levels=levels, colors='#C8923A', linewidths=1.5, alpha=0.8, linestyles='--')
        ax.clabel(cs2, inline=True, fontsize=8, fmt='v=%1.1f')
        ax.set_title(f'调和函数 f(z)=z²: 等势线+流线 (t={t:.2f})\n正交相交 ⟂', fontsize=12, color='#1B3A5C', fontweight='bold')
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
        return []

    anim = FuncAnimation(fig, update, frames=30, interval=120, blit=False)
    return _save_anim_to_bytes(anim, fps=8)


def animate_harmonic_exp():
    """展示f(z)=e^z的调和函数e^x cos y和e^x sin y的等势线逐渐绘制"""
    x = np.linspace(-2, 2, 300); y = np.linspace(-2*np.pi, 2*np.pi, 300)
    X, Y = np.meshgrid(x, y); U = np.exp(X) * np.cos(Y); V = np.exp(X) * np.sin(Y)
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.set_xlim(-2, 2); ax.set_ylim(-2*np.pi, 2*np.pi); ax.set_aspect('equal')
    ax.set_xlabel('x'); ax.set_ylabel('y')
    ax.set_title('调和函数 f(z)=e^z: 等势线 u=e^x cos y 与流线 v=e^x sin y', fontsize=12, color='#1B3A5C', fontweight='bold')
    ax.grid(True, alpha=0.3)
    legend_elements = [Line2D([0], [0], color='#1B3A5C', lw=1.5, label='等势线 u = 常数'),
                       Line2D([0], [0], color='#C8923A', lw=1.5, linestyle='--', label='流线 v = 常数')]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

    def update(frame):
        ax.clear(); ax.set_xlim(-2, 2); ax.set_ylim(-2*np.pi, 2*np.pi); ax.set_aspect('equal')
        ax.set_xlabel('x'); ax.set_ylabel('y'); ax.grid(True, alpha=0.3)
        t = (frame + 1) / 30.0
        levels = int(4 + t * 16)
        cs1 = ax.contour(X, Y, U, levels=levels, colors='#1B3A5C', linewidths=1.5, alpha=0.8)
        ax.clabel(cs1, inline=True, fontsize=8, fmt='u=%1.1f')
        cs2 = ax.contour(X, Y, V, levels=levels, colors='#C8923A', linewidths=1.5, alpha=0.8, linestyles='--')
        ax.clabel(cs2, inline=True, fontsize=8, fmt='v=%1.1f')
        ax.set_title(f'调和函数 f(z)=e^z: 等势线+流线 (t={t:.2f})\n正交相交 ⟂', fontsize=12, color='#1B3A5C', fontweight='bold')
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
        return []

    anim = FuncAnimation(fig, update, frames=30, interval=120, blit=False)
    return _save_anim_to_bytes(anim, fps=8)


# -------------------- 第1章: 复指数模分布动态扫描 --------------------
def animate_complex_exp_scan():
    """展示|e^z|随虚部y变化的扫描过程"""
    x = np.linspace(-2*np.pi, 2*np.pi, 400); y = np.linspace(-3, 3, 400)
    X, Y = np.meshgrid(x, y)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    ax1, ax2 = axes[0], axes[1]
    im1 = ax1.imshow(np.zeros_like(X), extent=[-2*np.pi, 2*np.pi, -3, 3], cmap='YlOrRd', vmin=0, vmax=20, origin='lower')
    ax1.set_xlabel('x'); ax1.set_ylabel('y'); ax1.set_title('|e^z| = e^x (随x指数变化)', fontsize=12, color='#1B3A5C')
    plt.colorbar(im1, ax=ax1, label='|e^z|')
    ax2.set_xlim(-2*np.pi, 2*np.pi); ax2.set_ylim(0, 20)
    ax2.set_xlabel('x'); ax2.set_ylabel('|e^z|'); ax2.set_title('沿 y=常数 截面的 |e^z| 分布', fontsize=12, color='#1B3A5C')
    ax2.grid(True, alpha=0.3)
    line_y, = ax2.plot([], [], '#1B3A5C', lw=2)
    y_text = ax2.text(0.02, 0.95, '', transform=ax2.transAxes, fontsize=12)

    def init():
        im1.set_data(np.zeros_like(X)); line_y.set_data([], []); y_text.set_text('')
        return im1, line_y, y_text

    def update(frame):
        y_slice = -3 + frame * 6 / 40.0
        Y_scan = np.full_like(X, y_slice)
        Z = X + 1j*Y_scan; W = np.exp(Z)
        modulus = np.abs(W)
        im1.set_data(modulus)
        ax1.set_title(f'|e^z| 扫描: y={y_slice:.2f}', fontsize=12, color='#1B3A5C')
        line_y.set_data(x, modulus[int(len(y)/2), :])
        y_text.set_text(f'y = {y_slice:.2f}')
        return im1, line_y, y_text

    anim = FuncAnimation(fig, update, frames=40, init_func=init, interval=120, blit=False)
    plt.suptitle('复指数 e^z: |e^z|=e^x 的模分布扫描', fontsize=14, fontweight='bold', color='#1B3A5C')
    return _save_anim_to_bytes(anim, fps=8)


# -------------------- 第1章: 共形映射角度保持动画 --------------------
def animate_conformal_angle():
    """展示两条曲线在z平面和w=z^2平面的夹角保持不变"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    ax_z, ax_w = axes[0], axes[1]
    ax_z.set_xlim(-0.5, 2); ax_z.set_ylim(-0.5, 2); ax_z.set_aspect('equal')
    ax_w.set_xlim(-1, 4); ax_w.set_ylim(-1, 3); ax_w.set_aspect('equal')
    ax_z.set_xlabel('Re(z)'); ax_z.set_ylabel('Im(z)')
    ax_w.set_xlabel('Re(w)'); ax_w.set_ylabel('Im(w)')
    ax_z.set_title('z-平面: 两条射线夹角 θ', fontsize=12, color='#1B3A5C')
    ax_w.set_title('w-平面: w=z², 夹角保持不变', fontsize=12, color='#1B3A5C')
    ax_z.grid(True, alpha=0.3); ax_w.grid(True, alpha=0.3)

    ray1_z, = ax_z.plot([], [], 'b-', lw=2, label='射线1')
    ray2_z, = ax_z.plot([], [], 'r-', lw=2, label='射线2')
    ray1_w, = ax_w.plot([], [], 'b-', lw=2, label='像1')
    ray2_w, = ax_w.plot([], [], 'r-', lw=2, label='像2')
    angle_z = ax_z.annotate('', xy=(0,0), xytext=(0,0), arrowprops=dict(arrowstyle='->', color='green', lw=1.5))
    angle_w = ax_w.annotate('', xy=(0,0), xytext=(0,0), arrowprops=dict(arrowstyle='->', color='green', lw=1.5))
    z_text = ax_z.text(0.5, -0.12, '', transform=ax_z.transAxes, fontsize=11, ha='center', color='green')
    w_text = ax_w.text(0.5, -0.12, '', transform=ax_w.transAxes, fontsize=11, ha='center', color='green')

    def init():
        for l in [ray1_z, ray2_z, ray1_w, ray2_w]:
            l.set_data([], [])
        z_text.set_text(''); w_text.set_text('')
        return ray1_z, ray2_z, ray1_w, ray2_w, z_text, w_text

    def update(frame):
        t = frame / 30.0
        theta = np.pi/4 + t * np.pi/6  # 角度变化
        phi = theta + np.pi/6  # 固定夹角30°
        r = np.linspace(0, 1.5, 100)
        ray1_z.set_data(r*np.cos(theta), r*np.sin(theta))
        ray2_z.set_data(r*np.cos(phi), r*np.sin(phi))
        w1 = r**2 * np.cos(2*theta) + 1j * r**2 * np.sin(2*theta)
        w2 = r**2 * np.cos(2*phi) + 1j * r**2 * np.sin(2*phi)
        ray1_w.set_data(w1.real, w1.imag)
        ray2_w.set_data(w2.real, w2.imag)
        z_text.set_text(f'夹角 = 30°')
        w_text.set_text(f'夹角 = 30° (不变)')
        return ray1_z, ray2_z, ray1_w, ray2_w, z_text, w_text

    anim = FuncAnimation(fig, update, frames=30, init_func=init, interval=150, blit=False)
    plt.suptitle('共形映射: 角度保持性 (f(z)=z²)', fontsize=14, fontweight='bold', color='#1B3A5C')
    return _save_anim_to_bytes(anim, fps=8)


# -------------------- 第1章: ln(z)多值函数分支动画 --------------------
def animate_log_branches():
    """展示ln(z)的多值性：不同k对应的虚部"""
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure(figsize=(12, 7))
    ax = fig.add_subplot(111, projection='3d')
    r = np.linspace(0.1, 2, 60); theta = np.linspace(-np.pi, np.pi, 120)
    R, THETA = np.meshgrid(r, theta)
    X_s, Y_s = R*np.cos(THETA), R*np.sin(THETA)

    surf = ax.plot_surface(X_s, Y_s, np.log(R), cmap='RdBu_r', alpha=0.7, vmin=-3, vmax=3)
    ax.set_xlabel('Re(z)'); ax.set_ylabel('Im(z)'); ax.set_zlabel('Im(ln z)')
    ax.set_title('多值函数 ln(z): 展开为螺旋面', fontsize=12, color='#1B3A5C', fontweight='bold')
    ax.view_init(elev=25, azim=-60)

    def update(frame):
        ax.cla()
        k = (frame % 30) / 30.0 * 3  # k从0到3
        # 绘制多层
        for branch in range(3):
            alpha_b = 0.7 if abs(branch-k) < 0.5 else 0.15
            Z_im = THETA + 2*branch*np.pi
            surf = ax.plot_surface(X_s, Y_s, Z_im, cmap='RdBu_r', alpha=alpha_b, vmin=-3, vmax=3)
        ax.set_xlabel('Re(z)'); ax.set_ylabel('Im(z)'); ax.set_zlabel('Im(ln z)')
        ax.set_title(f'ln(z) 的多值分支 (k=0,1,2): 当前层 k≈{k:.1f}', fontsize=12, color='#1B3A5C', fontweight='bold')
        ax.set_zlim(-3, 18)
        return []

    anim = FuncAnimation(fig, update, frames=90, interval=100, blit=False)
    return _save_anim_to_bytes(anim, fps=10)


# -------------------- 第2章: 柯西定理路径连续变形动画 --------------------
def animate_path_deformation():
    """展示柯西定理：路径连续变形而积分值不变"""
    theta = np.linspace(0, 2*np.pi, 200)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-1.5, 2.5); ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal'); ax.grid(True, alpha=0.3)
    ax.set_xlabel('Re(z)'); ax.set_ylabel('Im(z)')
    ax.plot(0, 0, 'rx', markersize=12, markeredgewidth=3, label='奇点(不在区域内)')

    path_line, = ax.plot([], [], 'b-', lw=2.5)
    start_pt, = ax.plot([], [], 'ko', markersize=8)
    end_pt, = ax.plot([], [], 'ko', markersize=8)
    integral_text = ax.text(0.5, -0.12, '', transform=ax.transAxes, fontsize=11, ha='center')
    ax.set_title('柯西定理: 路径连续变形, 积分值不变', fontsize=13, color='#1B3A5C', fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)

    z1, z2 = -1+0.5j, 1+0.5j

    def init():
        path_line.set_data([], []); start_pt.set_data([], []); end_pt.set_data([], [])
        integral_text.set_text('')
        return path_line, start_pt, end_pt, integral_text

    def update(frame):
        t = frame / 50.0
        # 从上圆弧(π→0)连续变形到下圆弧(-π→0)
        center = (z1+z2)/2; radius = abs(z2-z1)/2
        angle_max = np.pi*(1-t)
        angle_min = 0 if t<0.5 else -np.pi*(t-0.5)*2
        angles = np.linspace(angle_max, angle_min, 100)
        path = center + radius*np.exp(1j*angles)
        path_line.set_data(path.real, path.imag)
        start_pt.set_data([z1.real], [z1.imag])
        end_pt.set_data([z2.real], [z2.imag])
        integral_text.set_text(f'路径从上半圆连续变形 → ∫f(z)dz = 相同值 (t={t:.2f})')
        return path_line, start_pt, end_pt, integral_text

    anim = FuncAnimation(fig, update, frames=50, init_func=init, interval=100, blit=True)
    return _save_anim_to_bytes(anim, fps=10)


# -------------------- 第2章: 柯西积分公式动画 --------------------
def animate_cauchy_formula():
    """柯西积分公式: 边界值决定内部值"""
    theta = np.linspace(0, 2*np.pi, 100)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal'); ax.grid(True, alpha=0.3)
    ax.plot(np.cos(theta), np.sin(theta), 'b-', lw=2.5, label='|z|=1')
    dot, = ax.plot([], [], 'o', color='#C8923A', markersize=12)
    lines = []
    for _ in range(10):
        l, = ax.plot([], [], color='#C8923A', alpha=0.25, lw=0.8)
        lines.append(l)
    title_text = ax.text(0.5, 1.05, '', transform=ax.transAxes, fontsize=11, ha='center', color='#1B3A5C')
    ax.set_xlabel('Re(z)'); ax.set_ylabel('Im(z)'); ax.legend(loc='upper right')

    z0_vals = [0.5+0.3j, -0.3-0.4j, 0.1-0.5j, 0.6-0.1j, -0.5+0.2j]

    def init():
        dot.set_data([], []); title_text.set_text('')
        for l in lines: l.set_data([], [])
        return [dot] + lines + [title_text]

    def update(frame):
        z0 = z0_vals[frame % 5]
        dot.set_data([z0.real], [z0.imag])
        for i, l in enumerate(lines):
            z_boundary = np.exp(1j*theta[i*10])
            l.set_data([z0.real, z_boundary.real], [z0.imag, z_boundary.imag])
        title_text.set_text(f'f({z0.real:.1f}{z0.imag:+.1f}i) = 沿边界积分唯一确定')
        return [dot] + lines + [title_text]

    anim = FuncAnimation(fig, update, frames=40, init_func=init, interval=150, blit=True)
    return _save_anim_to_bytes(anim, fps=7)


# -------------------- 第3章: 泰勒级数逐项逼近动画 --------------------
def animate_taylor_approximation():
    """泰勒级数逐项逼近 sin(x)"""
    x = np.linspace(-2*np.pi, 2*np.pi, 400)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(-2*np.pi, 2*np.pi); ax.set_ylim(-1.5, 1.5)
    ax.axhline(y=0, color='k', lw=0.5); ax.axvline(x=0, color='k', lw=0.5)
    ax.set_xlabel('x'); ax.set_ylabel('f(x)'); ax.grid(True, alpha=0.3)
    target_line, = ax.plot(x, np.sin(x), 'k-', lw=2, label='精确 sin(x)')
    approx_line, = ax.plot([], [], '#C8923A', lw=2.5)
    order_text = ax.text(0.02, 0.92, '', transform=ax.transAxes, fontsize=12)
    ax.set_title('泰勒级数逐项逼近 sin(x)', fontsize=13, color='#1B3A5C', fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)

    def init():
        approx_line.set_data([], []); order_text.set_text('')
        return approx_line, order_text

    def update(frame):
        n = frame + 1
        taylor = np.zeros_like(x)
        for k in range(n):
            taylor += ((-1)**k / math.factorial(2*k+1)) * x**(2*k+1)
        approx_line.set_data(x, taylor)
        order_text.set_text(f'阶数 n = {n} (x=0处展开)')
        return approx_line, order_text

    anim = FuncAnimation(fig, update, frames=12, init_func=init, interval=150, blit=True)
    return _save_anim_to_bytes(anim, fps=7)


# -------------------- 第3章: 洛朗级数正负幂动画 --------------------
def animate_laurent_series():
    """展示洛朗级数：逐步添加正幂项和负幂项"""
    x = np.linspace(0.15, 0.95, 300)
    f_exact = 1/(x*(1-x))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 1); ax.set_ylim(0, 20)
    ax.set_xlabel('x'); ax.set_ylabel('f(x)'); ax.grid(True, alpha=0.3)
    exact_line, = ax.plot(x, f_exact, 'k-', lw=2, label='精确 f(x)=1/(x(1-x))')
    approx_line, = ax.plot([], [], '#C8923A', lw=2.5)
    info_text = ax.text(0.02, 0.92, '', transform=ax.transAxes, fontsize=11)
    ax.set_title('洛朗级数: 正幂+负幂联合逼近 (0<|x|<1)', fontsize=13, color='#1B3A5C', fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)

    def init():
        approx_line.set_data([], []); info_text.set_text('')
        return approx_line, info_text

    def update(frame):
        n_pos = min(frame+1, 8)
        n_neg = max(0, frame-5)
        approx = -1/x
        for k in range(n_pos):
            approx -= x**k
        approx_line.set_data(x, approx)
        info_text.set_text(f'负幂项 (1/z): 1项  |  正幂项 Σx^k: {n_pos}项')
        return approx_line, info_text

    anim = FuncAnimation(fig, update, frames=30, init_func=init, interval=100, blit=True)
    return _save_anim_to_bytes(anim, fps=10)


# -------------------- 第4章: 留数定理围道变形动画 --------------------
def animate_residue_contour():
    """展示留数定理: 大围道收缩为小圆"""
    theta = np.linspace(0, 2*np.pi, 200)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-2.5, 2.5); ax.set_ylim(-2.5, 2.5)
    ax.set_aspect('equal'); ax.grid(True, alpha=0.3)
    ax.set_xlabel('Re(z)'); ax.set_ylabel('Im(z)')

    singularities = [0.5+0.3j, -0.3-0.5j, 0.8-0.2j]
    colors = ['#C8923A', '#2E8B57', '#8B4513']
    for z0, c in zip(singularities, colors):
        ax.plot(z0.real, z0.imag, 'x', color=c, markersize=14, markeredgewidth=3)

    contour_line, = ax.plot([], [], 'b-', lw=2.5)
    small_circles = []
    for c in colors:
        l, = ax.plot([], [], '--', color=c, lw=1.5)
        small_circles.append(l)
    residue_text = ax.text(0.5, -0.12, '', transform=ax.transAxes, fontsize=11, ha='center')
    ax.set_title('留数定理: 大围道连续收缩到奇点', fontsize=13, color='#1B3A5C', fontweight='bold')

    def init():
        contour_line.set_data([], []); residue_text.set_text('')
        for l in small_circles: l.set_data([], [])
        return [contour_line] + small_circles + [residue_text]

    def update(frame):
        R = 2.0 - frame*0.04
        R = max(R, 0.15)
        contour = R*np.exp(1j*theta)
        contour_line.set_data(contour.real, contour.imag)
        r_small = 0.2 if R > 0.5 else R*0.8
        for i, z0 in enumerate(singularities):
            sc = z0 + r_small*np.exp(1j*theta)
            small_circles[i].set_data(sc.real, sc.imag)
        residue_text.set_text(f'围道半径 R={R:.2f} → 收缩到内部奇点 (留数不变)')
        return [contour_line] + small_circles + [residue_text]

    anim = FuncAnimation(fig, update, frames=50, init_func=init, interval=100, blit=True)
    return _save_anim_to_bytes(anim, fps=10)


# -------------------- 第5章: 傅里叶级数方波叠加动画 --------------------
def animate_fourier_square():
    """傅里叶级数逐项叠加逼近方波"""
    x = np.linspace(-3, 3, 500)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(-3, 3); ax.set_ylim(-1.8, 1.8)
    ax.axhline(y=0, color='k', lw=0.5)
    ax.set_xlabel('x'); ax.set_ylabel('f(x)'); ax.grid(True, alpha=0.3)
    target_line, = ax.plot(x, np.sign(np.sin(np.pi*x)), 'k-', lw=1.5, alpha=0.6, label='方波')
    approx_line, = ax.plot([], [], '#C8923A', lw=2.5)
    order_text = ax.text(0.02, 0.92, '', transform=ax.transAxes, fontsize=12)
    ax.set_title('傅里叶级数逐项叠加逼近方波 (Gibbs现象)', fontsize=13, color='#1B3A5C', fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)

    def init():
        approx_line.set_data([], []); order_text.set_text('')
        return approx_line, order_text

    def update(frame):
        n = frame + 1
        approx = np.zeros_like(x)
        for k in range(n):
            approx += 4/np.pi * np.sin((2*k+1)*np.pi*x) / (2*k+1)
        approx_line.set_data(x, approx)
        order_text.set_text(f'谐波数 N = {n} (仅含奇数项)')
        return approx_line, order_text

    anim = FuncAnimation(fig, update, frames=20, init_func=init, interval=120, blit=True)
    return _save_anim_to_bytes(anim, fps=8)


# -------------------- 第5章: 傅里叶频谱扫描动画 --------------------
def animate_fourier_spectrum_scan():
    """展示高斯脉冲的时域-频域对偶性"""
    x = np.linspace(-5, 5, 400); omega = np.linspace(-5, 5, 400)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax in axes:
        ax.grid(True, alpha=0.3)
    axes[0].set_xlim(-5, 5); axes[0].set_ylim(0, 1.2)
    axes[0].set_xlabel('x (时域)'); axes[0].set_ylabel('f(x)')
    axes[1].set_xlim(-5, 5); axes[1].set_ylim(0, 2)
    axes[1].set_xlabel('ω (频域)'); axes[1].set_ylabel('F(ω)')

    time_line, = axes[0].plot([], [], '#1B3A5C', lw=2.5)
    freq_line, = axes[1].plot([], [], '#C8923A', lw=2.5)
    sigma_text = axes[0].text(0.02, 0.92, '', transform=axes[0].transAxes, fontsize=11)

    def init():
        time_line.set_data([], []); freq_line.set_data([], []); sigma_text.set_text('')
        return time_line, freq_line, sigma_text

    def update(frame):
        sigma = 0.3 + frame*0.1
        f_t = np.exp(-x**2/(2*sigma**2)) / (sigma*np.sqrt(2*np.pi))
        F_w = np.exp(-sigma**2*omega**2/2)
        time_line.set_data(x, f_t); freq_line.set_data(omega, F_w)
        sigma_text.set_text(f'σ = {sigma:.1f}: 时域宽 ↔ 频域窄')
        axes[1].set_ylim(0, max(1.2, 1.0/sigma))
        return time_line, freq_line, sigma_text

    anim = FuncAnimation(fig, update, frames=40, init_func=init, interval=120, blit=True)
    plt.suptitle('傅里叶变换对偶性: 时域越窄, 频域越宽', fontsize=13, color='#1B3A5C', fontweight='bold')
    return _save_anim_to_bytes(anim, fps=8)


# -------------------- 第6章: 拉普拉斯极点移动动画 --------------------
def animate_laplace_response():
    """展示极点位置与时间响应的连续变化"""
    t = np.linspace(0, 8, 400)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    ax_s = axes[0]; ax_t = axes[1]
    ax_s.set_xlim(-3, 1); ax_s.set_ylim(-3, 3); ax_s.set_aspect('equal')
    ax_s.axhline(y=0, color='k', lw=0.5); ax_s.axvline(x=0, color='k', lw=0.5)
    ax_s.set_xlabel('Re(s)=σ'); ax_s.set_ylabel('Im(s)=ω'); ax_s.grid(True, alpha=0.3)
    ax_t.set_xlim(0, 8); ax_t.set_ylim(-2, 3)
    ax_t.axhline(y=0, color='k', lw=0.5); ax_t.set_xlabel('t'); ax_t.set_ylabel('y(t)')
    ax_t.grid(True, alpha=0.3)

    pole_dot, = ax_s.plot([], [], 'x', color='#C8923A', markersize=14, markeredgewidth=3)
    resp_line, = ax_t.plot([], [], '#1B3A5C', lw=2.5)
    info_text = ax_s.text(0.02, 0.92, '', transform=ax_s.transAxes, fontsize=10)

    def init():
        pole_dot.set_data([], []); resp_line.set_data([], []); info_text.set_text('')
        return pole_dot, resp_line, info_text

    def update(frame):
        # 极点从右半平面(-0.5+2i)逐步移到左半平面(-2+2i)
        sigma = 0.3 - frame*0.05  # 从0.3到-2
        omega = 1.5 + 0.5*np.sin(frame/8)
        y_t = np.exp(sigma*t)*np.cos(omega*t)
        pole_dot.set_data([sigma], [omega])
        resp_line.set_data(t, y_t)
        stability = '不稳定 (右半平面)' if sigma > 0 else '稳定 (左半平面)'
        info_text.set_text(f'极点: σ={sigma:.2f}+{omega:.1f}i\n{stability}')
        ax_t.set_ylim(min(-2, np.min(y_t)*1.1), max(3, np.max(y_t)*1.1))
        return pole_dot, resp_line, info_text

    anim = FuncAnimation(fig, update, frames=50, init_func=init, interval=120, blit=True)
    plt.suptitle('拉普拉斯变换: 极点位置与时间响应', fontsize=13, color='#1B3A5C', fontweight='bold')
    return _save_anim_to_bytes(anim, fps=8)


# -------------------- 第7章: 三类PDE传播特征动画 --------------------
def animate_pde_types():
    """对比三类PDE解的传播特征"""
    x = np.linspace(-8, 8, 400)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax in axes:
        ax.set_xlim(-8, 8); ax.set_ylim(-0.5, 1.5)
        ax.set_xlabel('x'); ax.grid(True, alpha=0.3); ax.axhline(y=0, color='k', lw=0.5)
    titles = ['双曲型 (波动)', '抛物型 (扩散)', '椭圆型 (稳态)']
    colors = ['#1B3A5C', '#C8923A', '#2E8B57']

    lines = []
    for ax, title, c in zip(axes, titles, colors):
        l, = ax.plot([], [], c, lw=2.5)
        lines.append(l)
        ax.set_title(title, fontsize=11, color=c)

    def init():
        for l in lines: l.set_data([], [])
        return lines

    def update(frame):
        t = frame*0.15
        # 波动: 行波
        u_wave = 0.5*(np.exp(-(x-2-t)**2/2) + np.exp(-(x-2+t)**2/2))
        lines[0].set_data(x, u_wave)
        # 扩散: 高斯展宽
        t_heat = t + 0.1
        u_heat = np.exp(-x**2/(4*t_heat)) / np.sqrt(4*np.pi*t_heat)*3
        lines[1].set_data(x, u_heat)
        # 稳态
        u_steady = np.sin(x)*np.cos(t*0.3)
        lines[2].set_data(x, 0.5*u_steady + 0.5)
        return lines

    anim = FuncAnimation(fig, update, frames=60, init_func=init, interval=120, blit=True)
    plt.suptitle('三类PDE解的特征: 波动传播 vs 扩散展宽 vs 稳态驻留', fontsize=13, color='#1B3A5C', fontweight='bold')
    return _save_anim_to_bytes(anim, fps=8)


# -------------------- 第9章: S-L本征函数叠加动画 --------------------
def animate_sl_eigen_overlay():
    """展示S-L本征函数逐个叠加"""
    x = np.linspace(0, 1, 400)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 1); ax.set_ylim(-2, 2)
    ax.set_xlabel('x'); ax.set_ylabel('y(x)'); ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', lw=0.5)

    main_line, = ax.plot([], [], 'k-', lw=2.5, label='叠加结果')
    mode_lines = [ax.plot([], [], '--', alpha=0.4, lw=1, color=c)[0]
                  for c in ['#1B3A5C','#C8923A','#2E8B57','#8B4513','#4B0082','#800020']]
    n_text = ax.text(0.02, 0.92, '', transform=ax.transAxes, fontsize=12)

    ax.set_title('S-L本征函数叠加: 用 sin(nπx) 逼近任意函数', fontsize=13, color='#1B3A5C', fontweight='bold')

    # 目标: 锯齿波 f(x)=2x-1 (在[0,1])
    target = 0.5 - x

    def init():
        main_line.set_data([], []); n_text.set_text('')
        for l in mode_lines: l.set_data([], [])
        return [main_line] + mode_lines + [n_text]

    def update(frame):
        n = frame + 1
        approx = np.zeros_like(x)
        for k in range(1, n+1):
            coeff = 2*np.trapezoid(target*np.sin(k*np.pi*x), x)
            mode = coeff * np.sin(k*np.pi*x)
            approx += mode
            if k <= 6:
                mode_lines[k-1].set_data(x, mode)
        for k in range(n, 6):
            mode_lines[k].set_data([], [])
        main_line.set_data(x, approx)
        n_text.set_text(f'前 {n} 个本征函数叠加')
        return [main_line] + mode_lines + [n_text]

    anim = FuncAnimation(fig, update, frames=30, init_func=init, interval=120, blit=False)
    return _save_anim_to_bytes(anim, fps=8)


# -------------------- 第9章: S-L正交性积分动画 --------------------
def animate_sl_orthogonality():
    """展示本征函数乘积积分的正负抵消过程"""
    x = np.linspace(0, 1, 500)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 1); ax.set_ylim(-1.5, 1.5)
    ax.axhline(y=0, color='k', lw=0.5)
    ax.set_xlabel('x'); ax.grid(True, alpha=0.3)

    m, n_fixed = 2, 3
    area_pos = ax.fill_between(x[:1], 0, 0, alpha=0.3, color='green')
    area_neg = ax.fill_between(x[:1], 0, 0, alpha=0.3, color='red')
    product_line, = ax.plot([], [], 'k-', lw=2)
    integral_text = ax.text(0.5, 0.08, '', transform=ax.transAxes, fontsize=12, ha='center',
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    mode_text = ax.text(0.02, 0.92, '', transform=ax.transAxes, fontsize=11)

    ax.set_title('S-L正交性: m≠n时乘积积分正负抵消为零', fontsize=13, color='#1B3A5C', fontweight='bold')

    def init():
        product_line.set_data([], []); integral_text.set_text(''); mode_text.set_text('')
        return product_line, integral_text, mode_text

    def update(frame):
        n = frame + 1
        if n == m:
            n = m + 1
        prod = np.sin(m*np.pi*x) * np.sin(n*np.pi*x)
        product_line.set_data(x, prod)
        running_int = np.array([np.trapezoid(prod[:i], x[:i]) for i in range(1, len(x)+1)])
        for coll in list(ax.collections):
            coll.remove()
        mask_pos = prod > 0
        ax.fill_between(x[mask_pos], 0, prod[mask_pos], alpha=0.3, color='green')
        mask_neg = prod < 0
        ax.fill_between(x[mask_neg], 0, prod[mask_neg], alpha=0.3, color='red')
        total = np.trapezoid(prod, x)
        integral_text.set_text(f'∫ sin({m}πx)·sin({n}πx) dx = {total:.4f} ≈ 0')
        mode_text.set_text(f'm={m}, n={n} (m≠n)')
        return product_line, integral_text, mode_text

    anim = FuncAnimation(fig, update, frames=20, init_func=init, interval=120, blit=False)
    return _save_anim_to_bytes(anim, fps=8)


# -------------------- 第10章: 勒让德多项式阶数扫描动画 --------------------
def animate_legendre_order():
    """展示不同阶数勒让德多项式的过渡"""
    x = np.linspace(-1, 1, 300)
    from scipy.special import legendre
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(-1, 1); ax.set_ylim(-1.2, 1.2)
    ax.axhline(y=0, color='k', lw=0.5); ax.axvline(x=0, color='k', lw=0.5)
    ax.set_xlabel('x'); ax.set_ylabel('P_l(x)'); ax.grid(True, alpha=0.3)

    line, = ax.plot([], [], '#1B3A5C', lw=2.5)
    zeros_y = ax.scatter([], [], c='#C8923A', s=60, zorder=5)
    l_text = ax.text(0.02, 0.92, '', transform=ax.transAxes, fontsize=13)
    ax.set_title('勒让德多项式 P_l(x): 阶数连续变化', fontsize=13, color='#1B3A5C', fontweight='bold')

    def init():
        line.set_data([], []); zeros_y.set_offsets(np.empty((0,2))); l_text.set_text('')
        return line, zeros_y, l_text

    def update(frame):
        l = frame*0.2
        poly = legendre(int(max(0, min(10, l))))
        y_vals = poly(x)
        line.set_data(x, y_vals)
        # 零点估算
        z_list = poly.roots
        real_zeros = z_list[np.abs(z_list.imag) < 1e-10].real
        real_zeros = real_zeros[(real_zeros > -1) & (real_zeros < 1)]
        if len(real_zeros) > 0:
            zeros_y.set_offsets(np.column_stack([real_zeros, np.zeros_like(real_zeros)]))
        else:
            zeros_y.set_offsets(np.empty((0,2)))
        l_text.set_text(f'l = {l:.1f}  零点数 = {int(l)}  P_l(1)=1, P_l(-1)=(-1)^{int(l)}')
        return line, zeros_y, l_text

    anim = FuncAnimation(fig, update, frames=60, init_func=init, interval=120, blit=False)
    return _save_anim_to_bytes(anim, fps=8)


# -------------------- 第10章: 球谐函数旋转动画 --------------------
def animate_spherical_rotation():
    """球谐函数Y20在球面上旋转"""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    u = np.linspace(0, 2*np.pi, 50); v = np.linspace(0, np.pi, 50)
    x_s = np.outer(np.cos(u), np.sin(v))
    y_s = np.outer(np.sin(u), np.sin(v))
    z_s = np.outer(np.ones_like(u), np.cos(v))

    def update(frame):
        ax.clear()
        phi_rot = frame*np.pi/20
        theta = v
        Y20 = 0.5*(3*np.cos(theta)**2 - 1)
        r = 1.0 + 0.3*Y20
        u_rot = u + phi_rot
        x_plot = r * np.outer(np.cos(u_rot), np.sin(v))
        y_plot = r * np.outer(np.sin(u_rot), np.sin(v))
        z_plot = r * np.outer(np.ones_like(u), np.cos(v))
        Y20_2d = np.tile(np.abs(Y20), (50, 1))
        ax.plot_surface(x_plot, y_plot, z_plot, facecolors=plt.cm.RdBu_r(Y20_2d/Y20_2d.max()),
                       alpha=0.85, antialiased=True)
        ax.set_xlim(-1.3, 1.3); ax.set_ylim(-1.3, 1.3); ax.set_zlim(-1.3, 1.3)
        ax.set_title(f'球谐函数 |Y2^0| 四极分布旋转 (angle={phi_rot:.1f}rad)', fontsize=12, color='#1B3A5C', fontweight='bold')
        ax.set_xlabel('x'); ax.set_ylabel('y'); ax.set_zlabel('z')
        return []

    anim = FuncAnimation(fig, update, frames=60, interval=100, blit=False)
    return _save_anim_to_bytes(anim, fps=10)


# -------------------- 第11章: 贝塞尔函数阶数扫描动画 --------------------
def animate_bessel_order():
    """展示贝塞尔函数随阶数变化"""
    from scipy.special import jv
    x = np.linspace(0, 15, 400)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 15); ax.set_ylim(-0.5, 1.1)
    ax.axhline(y=0, color='k', lw=0.5)
    ax.set_xlabel('x'); ax.set_ylabel('J_ν(x)'); ax.grid(True, alpha=0.3)

    line, = ax.plot([], [], '#1B3A5C', lw=2.5)
    nu_text = ax.text(0.02, 0.92, '', transform=ax.transAxes, fontsize=13)
    ax.set_title('贝塞尔函数 J_ν(x): 阶数连续变化', fontsize=13, color='#1B3A5C', fontweight='bold')

    def init():
        line.set_data([], []); nu_text.set_text('')
        return line, nu_text

    def update(frame):
        nu = frame*0.15
        y = jv(nu, x)
        line.set_data(x, y)
        nu_text.set_text(f'ν = {nu:.2f}  振荡衰减  振幅∝1/√x')
        return line, nu_text

    anim = FuncAnimation(fig, update, frames=60, init_func=init, interval=120, blit=True)
    return _save_anim_to_bytes(anim, fps=8)


# -------------------- 第11章: 圆膜振动模式动画 --------------------
def animate_drum_modes():
    """展示圆膜的前几个本征振动模式"""
    from scipy.special import jv, jn_zeros
    r = np.linspace(0, 1, 80); theta = np.linspace(0, 2*np.pi, 100)
    R, THETA = np.meshgrid(r, theta)
    X_d = R*np.cos(THETA); Y_d = R*np.sin(THETA)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax in axes:
        ax.set_aspect('equal'); ax.set_xlim(-1.2, 1.2); ax.set_ylim(-1.2, 1.2)
        ax.set_xticks([]); ax.set_yticks([])

    zero_01 = jn_zeros(0, 1)[0]; zero_11 = jn_zeros(1, 1)[0]

    def init():
        for ax in axes: ax.clear()
        return []

    def update(frame):
        for i, ax in enumerate(axes):
            ax.clear(); ax.set_aspect('equal')
            ax.set_xlim(-1.2, 1.2); ax.set_ylim(-1.2, 1.2)
            ax.set_xticks([]); ax.set_yticks([])
            t = frame*0.06
            if i == 0:
                mode = jv(0, zero_01*R) * np.cos(t)
                ax.set_title('(0,1) 基模: 中心最大振幅', fontsize=11, color='#1B3A5C')
            else:
                mode = jv(1, zero_11*R) * np.cos(THETA) * np.cos(t)
                ax.set_title('(1,1) 模式: 一条节线', fontsize=11, color='#C8923A')
            ax.contourf(X_d, Y_d, mode, levels=30, cmap='RdBu_r', vmin=-1, vmax=1)
            ax.add_artist(plt.Circle((0,0), 1, fill=False, color='k', lw=2))
        return []

    anim = FuncAnimation(fig, update, frames=60, init_func=init, interval=100, blit=False)
    plt.suptitle('圆膜振动: 贝塞尔本征模式 (0,1)基模 和 (1,1)模式', fontsize=13, color='#1B3A5C', fontweight='bold')
    return _save_anim_to_bytes(anim, fps=10)


# -------------------- 第12章: 格林函数构造动画 --------------------
def animate_green_construction():
    """展示格林函数: 移动点源位置观察响应变化"""
    x = np.linspace(0, 1, 400)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 1); ax.set_ylim(-0.35, 0.05)
    ax.axhline(y=0, color='k', lw=0.5)
    ax.set_xlabel('x'); ax.set_ylabel('G(x,x\')'); ax.grid(True, alpha=0.3)

    line, = ax.plot([], [], '#1B3A5C', lw=2.5)
    source_dot, = ax.plot([], [], 'ro', markersize=10)
    xp_text = ax.text(0.02, 0.92, '', transform=ax.transAxes, fontsize=12)
    ax.set_title('格林函数构造: 移动点源x\', 观察分段线性响应', fontsize=13, color='#1B3A5C', fontweight='bold')

    def init():
        line.set_data([], []); source_dot.set_data([], []); xp_text.set_text('')
        return line, source_dot, xp_text

    def update(frame):
        xp = 0.1 + frame*0.02
        G = np.zeros_like(x)
        for i, xi in enumerate(x):
            if xi < xp: G[i] = -xi*(1-xp)
            else: G[i] = -xp*(1-xi)
        line.set_data(x, G)
        source_dot.set_data([xp], [0])
        xp_text.set_text(f'点源位置 x\' = {xp:.2f}  斜率跃变=1  G(x\',x\')=-x\'(1-x\')={-xp*(1-xp):.3f}')
        return line, source_dot, xp_text

    anim = FuncAnimation(fig, update, frames=45, init_func=init, interval=120, blit=True)
    return _save_anim_to_bytes(anim, fps=8)


# -------------------- 第13章: 傅里叶变换解PDE动画 --------------------
def animate_fourier_pde():
    """展示傅里叶变换法如何将PDE转为ODE"""
    x = np.linspace(-10, 10, 300); t_max = 2.0
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax in axes:
        ax.grid(True, alpha=0.3)

    axes[0].set_xlim(-10, 10); axes[0].set_ylim(0, 1.1)
    axes[0].set_xlabel('x (空间域)'); axes[0].set_ylabel('u(x,t)')
    axes[1].set_xlim(-5, 5); axes[1].set_ylim(0, 1.2)
    axes[1].set_xlabel('ω (频率域)'); axes[1].set_ylabel('U(ω,t)')

    spatial_line, = axes[0].plot([], [], '#1B3A5C', lw=2.5)
    freq_line, = axes[1].plot([], [], '#C8923A', lw=2.5)
    t_text = axes[0].text(0.02, 0.92, '', transform=axes[0].transAxes, fontsize=12)
    axes[0].set_title('空间域: 热扩散展宽', fontsize=12, color='#1B3A5C')
    axes[1].set_title('频率域: 高频快速衰减 (乘法)', fontsize=12, color='#C8923A')

    def init():
        spatial_line.set_data([], []); freq_line.set_data([], []); t_text.set_text('')
        return spatial_line, freq_line, t_text

    def update(frame):
        t = 0.02 + frame*0.02
        a = 1.0
        u = 1/(2*a*np.sqrt(np.pi*t)) * np.exp(-x**2/(4*a**2*t))
        spatial_line.set_data(x, u)
        omega = np.linspace(-5, 5, 300)
        U_w = np.exp(-a**2*omega**2*t)
        freq_line.set_data(omega, U_w)
        t_text.set_text(f't = {t:.2f}  PDE: u_t=a²u_xx → ODE: U_t=-a²ω²U')
        axes[0].set_ylim(0, max(1.1, 1.0/np.sqrt(t*4)))
        return spatial_line, freq_line, t_text

    anim = FuncAnimation(fig, update, frames=50, init_func=init, interval=100, blit=True)
    return _save_anim_to_bytes(anim, fps=10)


# -------------------- 第14章: 保角变换映射过程动画 --------------------
def animate_conformal_mapping():
    """展示z²保角变换: 从z平面连续映射到w平面"""
    z_lim = 2.0; n_grid = 12
    x = np.linspace(0.5, z_lim, n_grid); y = np.linspace(0.5, z_lim, n_grid)
    X, Y = np.meshgrid(x, y); Z = X + 1j*Y

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-2, z_lim*2); ax.set_ylim(-2, z_lim*2)
    ax.set_aspect('equal'); ax.set_xlabel('Re'); ax.set_ylabel('Im'); ax.grid(True, alpha=0.3)

    # 显示原像网格
    for i in range(n_grid):
        ax.plot(X[i,:], Y[i,:], 'b-', alpha=0.3, lw=0.6)
        ax.plot(X[:,i], Y[:,i], 'r-', alpha=0.3, lw=0.6)

    mapped_lines_h = [ax.plot([], [], 'b-', alpha=0.7, lw=0.8)[0] for _ in range(n_grid)]
    mapped_lines_v = [ax.plot([], [], 'r-', alpha=0.7, lw=0.8)[0] for _ in range(n_grid)]
    t_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=12,
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax.set_title('保角变换 w=z²: 从原像连续变换到像', fontsize=13, color='#1B3A5C', fontweight='bold')

    def init():
        for l in mapped_lines_h + mapped_lines_v: l.set_data([], [])
        t_text.set_text('')
        return mapped_lines_h + mapped_lines_v + [t_text]

    def update(frame):
        t = frame/40.0
        W = Z**2; W_interp = (1-t)*Z + t*W
        U, V = W_interp.real, W_interp.imag
        for i in range(n_grid):
            mapped_lines_h[i].set_data(U[i,:], V[i,:])
            mapped_lines_v[i].set_data(U[:,i], V[:,i])
        t_text.set_text(f'变换进度: {t:.2f}  w=z²')
        return mapped_lines_h + mapped_lines_v + [t_text]

    anim = FuncAnimation(fig, update, frames=45, init_func=init, interval=100, blit=True)
    return _save_anim_to_bytes(anim, fps=10)


# -------------------- 第15章: Lorenz混沌吸引子动画 --------------------
def animate_lorenz_attractor():
    """绘制Lorenz系统的混沌吸引子"""
    sigma, beta, rho = 10.0, 8/3, 28.0
    dt = 0.01; n_steps = 1500
    x_arr = np.zeros(n_steps); y_arr = np.zeros(n_steps); z_arr = np.zeros(n_steps)
    x_arr[0], y_arr[0], z_arr[0] = 1.0, 0.0, 0.0
    for i in range(n_steps-1):
        dx = sigma*(y_arr[i] - x_arr[i])
        dy = x_arr[i]*(rho - z_arr[i]) - y_arr[i]
        dz = x_arr[i]*y_arr[i] - beta*z_arr[i]
        x_arr[i+1] = x_arr[i] + dx*dt
        y_arr[i+1] = y_arr[i] + dy*dt
        z_arr[i+1] = z_arr[i] + dz*dt

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('x'); ax.set_ylabel('y'); ax.set_zlabel('z')
    ax.set_title('Lorenz混沌吸引子: 初值敏感的蝴蝶效应', fontsize=13, color='#1B3A5C', fontweight='bold')

    line, = ax.plot([], [], [], '#C8923A', lw=1.2)
    point, = ax.plot([], [], [], 'ro', markersize=4)

    def init():
        line.set_data_3d([], [], []); point.set_data_3d([], [], [])
        ax.set_xlim(-20, 20); ax.set_ylim(-30, 30); ax.set_zlim(0, 50)
        return line, point

    def update(frame):
        end = (frame+1)*12
        line.set_data_3d(x_arr[:end], y_arr[:end], z_arr[:end])
        point.set_data_3d([x_arr[end-1]], [y_arr[end-1]], [z_arr[end-1]])
        ax.set_xlim(-20, 20); ax.set_ylim(-30, 30); ax.set_zlim(0, 50)
        return line, point

    anim = FuncAnimation(fig, update, frames=100, init_func=init, interval=80, blit=False)
    return _save_anim_to_bytes(anim, fps=12)


# ==================== 辅助函数 ====================
def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=120)
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    return img_str


# ==================== 可视化注册表 ====================
VISUALIZATIONS = {
    # 第1章 复变函数 (已改造为动态动画)
    "z_squared_mapping": {"title": "🎬 解析函数 $f(z)=z^2$ 的映射动画", "description": "展示 $z^2$ 将正方形网格映射为曲边网格的动态过程，保持局部角度。", "function": animate_analytic_mapping, "chapter": "第1章", "type": "animation"},
    "z_cubed_mapping": {"title": "🎬 解析函数 $f(z)=z^3$ 的映射动画", "description": "展示 $z^3$ 将网格映射的动态过程，在原点处角度放大 3 倍。", "function": animate_z_cubed_mapping, "chapter": "第1章", "type": "animation"},
    "exp_mapping": {"title": "🎬 指数函数 $e^z$ 的映射动画", "description": "$e^z$ 将带状区域映射为环形区域的动态过程。", "function": animate_exp_mapping, "chapter": "第1章", "type": "animation"},
    "harmonic_z2": {"title": "🎬 调和函数 $u=x^2-y^2$ 的等势线绘制动画", "description": "$u=x^2-y^2$（实部）和 $v=2xy$（虚部）正交相交的动态绘制过程。", "function": animate_harmonic_z2, "chapter": "第1章", "type": "animation"},
    "harmonic_exp": {"title": "🎬 调和函数 $u=e^x \\cos y$ 的等势线绘制动画", "description": "$e^x \\cos y$ 和 $e^x \\sin y$ 构成正交曲线网的动态绘制。", "function": animate_harmonic_exp, "chapter": "第1章", "type": "animation"},
    "complex_exp": {"title": "🎬 复指数 $e^z$ 的模分布扫描动画", "description": "$|e^z|=e^x$ 与 $x$ 无关，$\\arg(e^z)=y$ 与 $y$ 无关，周期 $2\\pi i$。", "function": animate_complex_exp_scan, "chapter": "第1章", "type": "animation"},
    "complex_sine": {"title": "🎬 复三角函数 $\\sin z$ 的模构建动画", "description": "$|\\sin z|$ 在虚轴方向呈指数增长，从实轴出发逐步构建复平面分布。", "function": animate_complex_sine_build, "chapter": "第1章", "type": "animation"},
    "cr_geometry": {"title": "🎬 C-R 方程的几何解释：梯度旋转动画", "description": "$\\nabla u \\perp \\nabla v$ 且 $|\\nabla u| = |\\nabla v|$，在复平面上旋转观测点实时展示。", "function": animate_cr_gradient, "chapter": "第1章", "type": "animation"},
    "conformal_angle": {"title": "🎬 共形映射的角度保持性动画", "description": "$f(z)=z^2$ 在 $z \\neq 0$ 处保持任意两条曲线的夹角不变。", "function": animate_conformal_angle, "chapter": "第1章", "type": "animation"},
    # 第2章 复变函数的积分
    "cauchy_path": {"title": "柯西定理：积分与路径无关", "description": "解析函数沿不同路径从 z1 到 z2 的积分结果相同。", "function": plot_cauchy_integral_path, "chapter": "第2章"},
    "cauchy_integral_formula": {"title": "柯西积分公式：边界值决定内部值", "description": "解析函数在区域内任意点的值由边界上的积分完全确定。", "function": plot_cauchy_integral_formula, "chapter": "第2章"},
    # 第3章 幂级数展开
    "taylor_convergence": {"title": "泰勒级数收敛圆与部分和", "description": "f(z)=1/(1-z) 在 z0=0 展开，收敛半径 R=1（到最近奇点距离）。", "function": plot_taylor_convergence, "chapter": "第3章"},
    "laurent_annulus": {"title": "洛朗级数收敛圆环", "description": "f(z)=1/(z(z-1)) 在 z0=0 附近，0<|z|<1 为洛朗区域。", "function": plot_laurent_annulus, "chapter": "第3章"},
    # 第4章 留数定理
    "residue_contour": {"title": "留数定理：围道积分与留数", "description": "∮_C f(z)dz = 2πi × Σ Res(f, z_k)，内部所有奇点留数之和。", "function": plot_residue_contour, "chapter": "第4章"},
    # 第5章 傅里叶变换
    "fourier_spectrum": {"title": "傅里叶变换：时域与频域", "description": "方波的 sinc 频谱、高斯脉冲的自身型变换。", "function": plot_fourier_spectrum, "chapter": "第5章"},
    # 第6章 拉普拉斯变换
    "laplace_poles": {"title": "拉普拉斯变换：极点与系统响应", "description": "s平面极点位置决定时间响应：左半平面稳定，右半平面发散。", "function": plot_laplace_poles, "chapter": "第6章"},
    # 第7章 数学物理定解问题
    "pde_classification": {"title": "三类偏微分方程对比", "description": "双曲型（波动）、抛物型（热传导）、椭圆型（拉普拉斯）的特征对比。", "function": plot_pde_classification, "chapter": "第7章"},
    "dalembert_formula": {"title": "达朗贝尔公式：波动分解", "description": "初始位移分解为左右传播的两列波，速度为 a。", "function": plot_dalembert, "chapter": "第7章"},
    # 第8章 分离变数法
    "separation_modes": {"title": "分离变量法：驻波模式叠加", "description": "弦振动的前3个本征模式叠加形成完整解。", "function": plot_separation_modes, "chapter": "第8章"},
    "heat_evolution": {"title": "热传导方程：温度演化", "description": "各本征模式按指数衰减，最终趋于稳态。", "function": plot_heat_evolution, "chapter": "第8章"},
    # 第9章 S-L方程
    "sl_eigenfunctions": {"title": "S-L 本征函数族与零点定理", "description": "$y\'\'+\\lambda y=0$, $y(0)=y(1)=0$ 的本征函数，展示 Sturm 零点定理。", "function": plot_sl_eigenfunctions, "chapter": "第9章"},
    "sl_orthogonality": {"title": "S-L 正交性定理演示", "description": "不同本征函数乘积积分为0（正负抵消），同一函数平方积分为正（正定）。", "function": plot_sl_orthogonality, "chapter": "第9章"},
    # 第10章 球函数
    "legendre_polynomials": {"title": "勒让德多项式 P_l(x)", "description": "前5个勒让德多项式，展示 Rodrigue 公式和零点分布。", "function": plot_legendre_polynomials, "chapter": "第10章"},
    "spherical_harmonics": {"title": "球谐函数 |Y_l^m(θ,φ)| 分布", "description": "Y0^0（球对称）、Y1^0（偶极）、Y2^0（四极）的角分布。", "function": plot_spherical_harmonics, "chapter": "第10章"},
    # 第11章 柱函数
    "bessel_functions": {"title": "贝塞尔函数 J_ν(x) 与渐近行为", "description": "前4个阶数的贝塞尔函数，振幅按 1/√x 衰减。", "function": plot_bessel_functions, "chapter": "第11章"},
    "bessel_zeros": {"title": "贝塞尔函数零点分布", "description": "J0(x) 的前5个正零点，间距趋近于 π。", "function": plot_bessel_zeros, "chapter": "第11章"},
    # 第12章 格林函数
    "green_function_1d": {"title": "一维格林函数 G(x, x\')", "description": "分段线性函数，在 x=x\' 处斜率跃变 = 1。", "function": plot_green_function_1d, "chapter": "第12章"},
    "green_superposition": {"title": "格林函数叠加原理", "description": "连续分布源 = 各点源响应的积分叠加。", "function": plot_green_superposition, "chapter": "第12章"},
    # 第13章 积分变换法
    "heat_kernel_diffusion": {"title": "热核扩散过程", "description": "初始点热源 δ(x) 随时间的演化，高斯分布宽度按 √t 增长。", "function": plot_heat_kernel_diffusion, "chapter": "第13章"},
    # 第14章 保角变换
    "conformal_examples": {"title": "常用保角变换的映射效果", "description": "z²、e^z、1/z、ln z、z^{1/2} 等常用变换的映射效果。", "function": plot_conformal_examples, "chapter": "第14章"},
    # 第15章 非线性问题
    "kdv_soliton": {"title": "KdV 孤立子解", "description": "形状不变、速度恒定的行波，色散与非线性平衡的结果。", "function": plot_kdv_soliton, "chapter": "第15章"},
}

# ==================== 动画注册表 ====================
ANIMATIONS = {
    # 第1章 复变函数
    "anim_cr_grad": {"title": "🎬 C-R方程几何: 梯度旋转动画", "description": "在复平面上旋转观测点，实时展示∇u⟂∇v且等长。", "function": animate_cr_gradient, "chapter": "第1章"},
    "anim_mapping": {"title": "🎬 解析函数映射过程: z→z²", "description": "从z平面网格连续变换到w平面，观察网格如何被扭曲。", "function": animate_analytic_mapping, "chapter": "第1章"},
    "anim_log_branches": {"title": "🎬 多值函数 ln(z): 分支螺旋面", "description": "ln(z)沿不同k分支的高亮展示，直观理解多值性。", "function": animate_log_branches, "chapter": "第1章"},
    "anim_sine": {"title": "🎬 |sin z| 模的复平面构建", "description": "从实轴出发逐步增加虚部y，观察|sin z|的指数增长行为。", "function": animate_complex_sine_build, "chapter": "第1章"},
    # 第2章 复变函数的积分
    "anim_path_def": {"title": "🎬 柯西定理: 路径连续变形", "description": "从上半圆连续变形到下弧，积分值始终不变。", "function": animate_path_deformation, "chapter": "第2章"},
    "anim_cauchy_formula": {"title": "🎬 柯西积分公式: 边界决定内部", "description": "解析函数内部值由边界积分唯一确定。", "function": animate_cauchy_formula, "chapter": "第2章"},
    # 第3章 幂级数展开
    "anim_taylor": {"title": "🎬 泰勒级数: 逐项逼近 sin(x)", "description": "逐步添加高阶项，逼近效果越来越好。", "function": animate_taylor_approximation, "chapter": "第3章"},
    "anim_laurent": {"title": "🎬 洛朗级数: 正负幂联合逼近", "description": "负幂项+正幂项联合逼近，展示洛朗级数结构。", "function": animate_laurent_series, "chapter": "第3章"},
    # 第4章 留数定理
    "anim_residue": {"title": "🎬 留数定理: 大围道收缩到奇点", "description": "大围道连续收缩到内部奇点，留数保持不变。", "function": animate_residue_contour, "chapter": "第4章"},
    # 第5章 傅里叶变换
    "anim_fourier_sq": {"title": "🎬 傅里叶级数: 方波叠加 (Gibbs)", "description": "逐项叠加谐波逼近方波，观察Gibbs过冲现象。", "function": animate_fourier_square, "chapter": "第5章"},
    "anim_fourier_dual": {"title": "🎬 傅里叶对偶: 时域宽↔频域窄", "description": "高斯脉冲宽度连续变化，展示不确定性原理。", "function": animate_fourier_spectrum_scan, "chapter": "第5章"},
    # 第6章 拉普拉斯变换
    "anim_laplace": {"title": "🎬 拉普拉斯: 极点移动与响应", "description": "极点从右半平面滑向左半平面，系统从发散到稳定。", "function": animate_laplace_response, "chapter": "第6章"},
    # 第7章 数学物理定解问题
    "anim_dalembert": {"title": "🎬 达朗贝尔公式: 波传播动画", "description": "初始位移分解为左右两列行波，观察波的传播与叠加。", "function": animate_dalembert, "chapter": "第7章"},
    "anim_pde_types": {"title": "🎬 三类PDE特征对比", "description": "同时展示波动传播、扩散展宽、稳态驻留的差异。", "function": animate_pde_types, "chapter": "第7章"},
    # 第8章 分离变数法
    "anim_separation": {"title": "🎬 分离变量法: 驻波模式叠加", "description": "前3个驻波模式实时叠加，展示弦振动解的形成。", "function": animate_separation_modes, "chapter": "第8章"},
    "anim_heat": {"title": "🎬 热传导方程: 温度演化动画", "description": "各本征模式指数衰减，温度分布趋于稳态。", "function": animate_heat_evolution, "chapter": "第8章"},
    # 第9章 S-L方程
    "anim_sl_overlay": {"title": "🎬 S-L本征函数叠加", "description": "用sin本征函数逼近锯齿波，展示完备性。", "function": animate_sl_eigen_overlay, "chapter": "第9章"},
    "anim_sl_ortho": {"title": "🎬 S-L正交性积分演示", "description": "m≠n时乘积积分正负面积抵消为零。", "function": animate_sl_orthogonality, "chapter": "第9章"},
    # 第10章 球函数
    "anim_legendre": {"title": "🎬 勒让德多项式: 阶数扫描", "description": "P_l(x)随l连续变化，零点数=l，展示零点嵌入定理。", "function": animate_legendre_order, "chapter": "第10章"},
    "anim_spherical": {"title": "🎬 球谐函数: 3D旋转动画", "description": "Y2^0的四极分布绕z轴旋转。", "function": animate_spherical_rotation, "chapter": "第10章"},
    # 第11章 柱函数
    "anim_bessel": {"title": "🎬 贝塞尔函数: 阶数连续扫描", "description": "J_ν(x)随ν连续变化，振荡衰减，振幅∝1/√x。", "function": animate_bessel_order, "chapter": "第11章"},
    "anim_drum": {"title": "🎬 圆膜振动: 本征模式动画", "description": "(0,1)基模和(1,1)模式的实时振动。", "function": animate_drum_modes, "chapter": "第11章"},
    # 第12章 格林函数
    "anim_green": {"title": "🎬 格林函数: 点源移动构造", "description": "点源x'来回滑动，分段线性响应连续变化。", "function": animate_green_construction, "chapter": "第12章"},
    # 第13章 积分变换法
    "anim_kernel": {"title": "🎬 热核扩散: 点源演化", "description": "初始δ点源随时间的扩散，高斯宽度按√t增长。", "function": animate_heat_kernel, "chapter": "第13章"},
    "anim_fourier_pde": {"title": "🎬 傅里叶变换解PDE: 空域↔频域", "description": "空间域扩散展宽 vs 频率域高频衰减的同步展示。", "function": animate_fourier_pde, "chapter": "第13章"},
    # 第14章 保角变换
    "anim_conformal": {"title": "🎬 保角变换: 映射过程动画", "description": "z²变换将第一象限网格连续映射到对应区域。", "function": animate_conformal_mapping, "chapter": "第14章"},
    # 第15章 非线性问题
    "anim_kdv": {"title": "🎬 KdV孤立子: 行波传播", "description": "孤立子形状不变、速度恒定，色散与非线性平衡。", "function": animate_kdv_soliton, "chapter": "第15章"},
    "anim_lorenz": {"title": "🎬 Lorenz混沌吸引子", "description": "蝴蝶效应: 确定性系统中的不可预测性。", "function": animate_lorenz_attractor, "chapter": "第15章"},
}


if __name__ == "__main__":
    import os
    os.makedirs("images", exist_ok=True)
    for key, info in VISUALIZATIONS.items():
        try:
            fig = info["function"]()
            fig.savefig(f"images/{key}.png", dpi=150, bbox_inches='tight')
            plt.close(fig)
            print(f"已生成: images/{key}.png ({info['chapter']})")
        except Exception as e:
            print(f"失败 {key}: {e}")
    print("\n所有图片已生成到 images/ 目录")
