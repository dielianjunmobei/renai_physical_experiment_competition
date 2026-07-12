import matplotlib
matplotlib.use('Agg', force=True)

import matplotlib.pyplot as plt
import socket
import os

def safe_getlogin():
    try:
        return os.getlogin()
    except Exception:
        return "UNAVAILABLE"

# 收集信息
hostname = socket.gethostname()
fqdn = socket.getfqdn()
username = safe_getlogin()
cwd = os.getcwd()

# 筛选相关环境变量
env_keys = ['PATH', 'USER', 'NAME', 'HOST', 'COMPUTERNAME', 'PROCESSOR', 'TEMP']
env_lines = []
for key in env_keys:
    for var, val in os.environ.items():
        if key in var:
            env_lines.append(f"{var} = {val}")
            break   # 只记录第一个匹配，避免重复
# 若某关键词无匹配，则跳过

# 生成所有文本行
lines = []
lines.append(f"Hostname: {hostname}")
lines.append(f"FQDN: {fqdn}")
lines.append(f"Username: {username}")
lines.append(f"CWD: {cwd}")
lines.append("")
lines.append("--- Environment Variables ---")
lines.extend(env_lines)

# 创建绘图
fig, ax = plt.subplots(figsize=(14, 8), dpi=150)
ax.axis('off')

# 使用等宽字体，逐行绘制
y = 1.0
fontsize = 12
line_height = 0.04   # 相对坐标间距
for line in lines:
    ax.text(0.02, y, line, fontsize=fontsize, family='monospace',
            verticalalignment='top')
    y -= line_height

ax.set_title("System Identity & Environment", fontsize=14, family='monospace', pad=10)
plt.tight_layout()
plt.savefig("identity.png", dpi=150, bbox_inches='tight')
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
