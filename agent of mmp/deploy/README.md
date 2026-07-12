# 📐 数学物理方法助教 - Streamlit 部署版

《数学物理方法》全部15章的 AI 教学助手，覆盖上篇复变函数论与下篇数学物理方程。

---

## 安全说明：API Key 后端配置

**本应用 API Key 完全配置在后端，前端用户不可见、不可修改。**

学生/用户界面仅显示课程内容和交互功能，不会暴露任何 API 密钥信息。

---

## 快速部署到 Streamlit Cloud（免费）

### 步骤1：配置 API Key（本地或云端）

#### 方式 A：本地开发（.streamlit/secrets.toml）

编辑 `.streamlit/secrets.toml` 文件：

```toml
provider = "deepseek"              # 可选：deepseek / kimi / dashscope
model = "deepseek-v4-pro"          # 模型名称
api_key = "sk-xxxxxxxxxxxxxxxx"    # <-- 替换为你的真实 API Key
```

#### 方式 B：Streamlit Cloud 部署（Dashboard Secrets）

1. 部署后进入 Streamlit Cloud Dashboard
2. 点击你的 App → **Settings → Secrets**
3. 添加以下配置：

```toml
provider = "deepseek"
model = "deepseek-v4-pro"
api_key = "sk-xxxxxxxxxxxxxxxx"
```

> ⚠️ **安全提醒**：
> - `secrets.toml` 已加入 `.gitignore`，不会误提交到 GitHub
> - 永远不要将 API Key 直接写入 `app.py` 代码中
> - 学生/用户在前端看不到任何 API 配置信息

---

### 步骤2：创建 GitHub 仓库

1. 在 GitHub 创建新仓库（如 `math-physics-agent`）
2. 将本目录所有文件上传（**注意**：`secrets.toml` 在 `.gitignore` 中，不会上传，这是正确的）：

   ```bash
   cd "数理方法agent/deploy"
   git init
   git remote add origin https://github.com/你的用户名/math-physics-agent.git
   git add .
   git commit -m "Initial commit"
   git push -u origin main
   ```

---

### 步骤3：部署到 Streamlit Cloud

1. 登录 [share.streamlit.io](https://share.streamlit.io)
2. 点击 **"Create app"**
3. 选择你的 GitHub 仓库
4. 设置：
   - **Main file path**: `app.py`
   - **Python version**: 3.11
5. 点击 **Deploy!**
6. 在 Dashboard → **Secrets** 中填入 API Key（见步骤1）

等待 2-3 分钟，获得链接：`https://xxx-xxx-xxx.streamlit.app`

---

### 步骤4：在课程平台添加链接

在课程中心添加外部链接：
- 名称：`📐 数学物理方法AI助教`
- 链接：`https://你的链接.streamlit.app`

---

## 本地测试

```bash
cd "数理方法agent/deploy"

# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key（在 .streamlit/secrets.toml 中）
# 3. 启动
streamlit run app.py
```

浏览器自动打开 `http://localhost:8501`

---

## 支持的 API 提供商

| 提供商 | 注册地址 | 说明 |
|--------|----------|------|
| DeepSeek | [platform.deepseek.com](https://platform.deepseek.com) | 推荐，速度快 |
| Kimi | [platform.moonshot.cn](https://platform.moonshot.cn) | 国内稳定 |
| 通义千问 | [dashscope.aliyun.com](https://dashscope.aliyun.com) | 阿里出品 |

---

## 功能特性

- **💬 聊天问答**：覆盖数学物理方法全部15章，6段式标准回答（概念定位→核心公式→详细推导→物理直觉→常见错误→自检提问）
- **📊 可视化演示**：28个 matplotlib 实时生成图像，涵盖每章核心概念
- **🔒 安全设计**：API Key 完全后端化，学生不可见

---

*基于梁昆淼《数学物理方法》教材体系构建。*
