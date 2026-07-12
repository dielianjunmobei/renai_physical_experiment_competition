import matplotlib
matplotlib.use('Agg', force=True)

import os
import matplotlib.pyplot as plt

# 切换到项目根目录
os.chdir(r"E:\agent\agent of mmp\deploy")
cwd = os.getcwd()

# 辅助函数：读取文件前N字符
def read_head(filename, n=500):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read(n)
    except FileNotFoundError:
        return f"[FileNotFoundError: {filename} 不存在于 {cwd}]"
    except Exception as e:
        return f"[读取 {filename} 错误: {e}]"

# 读取需求文件全部
def read_all(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"[FileNotFoundError: {filename} 不存在于 {cwd}]"
    except Exception as e:
        return f"[读取 {filename} 错误: {e}]"

# 读取各个文件
app_text = read_head("app.py", 500)
db_text = read_head("db.py", 500)
admin_text = read_head("admin_api.py", 500)
req_text = read_all("requirements.txt")
if not req_text.strip():
    req_text = "(empty)"

# 构建显示文本
sep = "\n" + "="*70 + "\n"
full_text = (
    f"Working Directory: {cwd}\n"
    + "="*70 + "\n"
    + "app.py (first 500 chars):\n" + app_text
    + sep
    + "db.py (first 500 chars):\n" + db_text
    + sep
    + "admin_api.py (first 500 chars):\n" + admin_text
    + sep
    + "requirements.txt (full):\n" + req_text
)

# 绘图
fig, ax = plt.subplots(figsize=(22, 16))
ax.axis('off')
ax.text(0.02, 0.98, full_text, transform=ax.transAxes,
        fontsize=16, fontfamily='monospace',
        verticalalignment='top', horizontalalignment='left',
        linespacing=1.2,
        bbox=dict(facecolor='white', alpha=0.9, edgecolor='gray'))

plt.savefig("project_files.png", dpi=350, bbox_inches='tight', pad_inches=0.3)
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
