import matplotlib
matplotlib.use('Agg', force=True)

import os
import matplotlib.pyplot as plt

# 目标目录
target_dir = r"E:\agent\agent of mmp\deploy"

# 辅助函数：读取文件内容（前N字符）
def read_file_head(filepath, max_chars=300):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read(max_chars)
        return content
    except FileNotFoundError:
        return "[File not found]"
    except Exception as e:
        return f"[Error: {e}]"

# 读取三个文件
app_content = read_file_head(os.path.join(target_dir, "app.py"), 300)
db_content = read_file_head(os.path.join(target_dir, "db.py"), 300)
# requirements.txt 通常较短，读取全部
req_path = os.path.join(target_dir, "requirements.txt")
try:
    with open(req_path, 'r', encoding='utf-8') as f:
        req_content = f.read()
    if not req_content:
        req_content = "(empty file)"
except FileNotFoundError:
    req_content = "[requirements.txt not found]"
except Exception as e:
    req_content = f"[Error: {e}]"

# 构建显示文本
separator = "\n" + "="*60 + "\n"
text = (
    "=== app.py (first 300 chars) ===" + "\n" +
    app_content +
    separator +
    "=== db.py (first 300 chars) ===" + "\n" +
    db_content +
    separator +
    "=== requirements.txt (full) ===" + "\n" +
    req_content
)

# 绘图
fig, ax = plt.subplots(figsize=(20, 14))
ax.axis('off')

ax.text(
    0.02, 0.98,
    text,
    transform=ax.transAxes,
    fontsize=16,
    fontfamily='monospace',
    verticalalignment='top',
    horizontalalignment='left',
    linespacing=1.2,
    bbox=dict(facecolor='white', alpha=0.9, edgecolor='gray')
)

plt.savefig("core_files.png", dpi=350, bbox_inches='tight', pad_inches=0.3)
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
