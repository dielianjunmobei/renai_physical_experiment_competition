# 📐 解析函数助教 - 部署指南

> **目标**：将"解析函数助教"AI Agent 部署到 Streamlit Cloud（免费），获得公网链接，添加到湖南大学课程中心。

---

## 目录

1. [前置准备](#一前置准备)
2. [本地测试](#二本地测试)
3. [推送到 GitHub](#三推送到-github)
4. [部署到 Streamlit Cloud](#四部署到-streamlit-cloud)
5. [添加到课程平台](#五添加到课程平台)
6. [常见问题排查](#六常见问题排查)

---

## 一、前置准备

### 1.1 注册 GitHub 账号

GitHub 是全球最大的代码托管平台，用于存储你的项目代码。

| 步骤 | 操作 | 截图示意 |
|------|------|----------|
| 1 | 打开 [github.com](https://github.com) | 点击右上角 **Sign up** |
| 2 | 填写邮箱、密码、用户名 | 用户名建议用英文，如 `dai_teacher` |
| 3 | 验证邮箱 | 查收邮件，点击验证链接 |
| 4 | 选择免费计划 | 选 **Free** 即可 |
| 5 | 完成注册 | 记住你的用户名（如 `dai_teacher`） |

> **你需要记住**：你的 GitHub 用户名（如 `dai_teacher`）

### 1.2 安装 Git

Git 是版本控制工具，用于把代码上传到 GitHub。

| 步骤 | 操作 |
|------|------|
| 1 | 打开 [git-scm.com/download/win](https://git-scm.com/download/win) |
| 2 | 下载并安装（一直点"下一步"即可） |
| 3 | 验证安装：打开命令提示符，输入 `git --version` |
| 4 | 显示版本号即安装成功 |

### 1.3 获取 AI API Key

Agent 需要调用大模型 API，推荐 Kimi（国内速度快）。

| 步骤 | 操作 |
|------|------|
| 1 | 打开 [platform.moonshot.cn](https://platform.moonshot.cn) |
| 2 | 用手机号注册并登录 |
| 3 | 点击左侧 **API Key 管理** |
| 4 | 点击 **创建 API Key** |
| 5 | 复制生成的 Key（格式如 `sk-abc123...`） |

> **重要**：API Key 是敏感信息，不要截图分享，不要上传到 GitHub！

### 1.4 安装 Python（如未安装）

| 步骤 | 操作 |
|------|------|
| 1 | 打开 [python.org/downloads](https://www.python.org/downloads/) |
| 2 | 下载 Python 3.11（Windows Installer 64-bit） |
| 3 | 安装时勾选 **"Add Python to PATH"** |
| 4 | 验证：命令行输入 `python --version` |

---

## 二、本地测试

在部署到公网之前，先在本地测试确保一切正常。

### 2.1 运行测试脚本

打开 **命令提示符（CMD）** 或 **PowerShell**：

```bash
cd "D:\AI\Sample\解析函数\deploy"
python test_local.py
```

**预期输出**：

```
============================================================
📐 解析函数助教 - 本地环境测试
============================================================
🐍 Python 版本: 3.11.x
   Python 路径: C:\Python311\python.exe

📦 检查依赖包...
  ✅ streamlit 已安装
  ✅ requests 已安装

📄 检查 app.py 语法...
   文件路径: D:\AI\Sample\解析函数\deploy\app.py
  ✅ app.py 语法正确！

📋 检查系统提示词完整性:
     ✅ 概念定位
     ✅ 核心公式
     ✅ 详细推导
     ✅ 物理直觉
     ✅ 常见错误
     ✅ 自检提问

============================================================
🎉 测试通过！可以运行本地服务了。
============================================================

启动命令:
  cd "D:\AI\Sample\解析函数\deploy"
  streamlit run app.py

然后在浏览器中打开:
  http://localhost:8501
```

### 2.2 如果缺少依赖

如果显示 `❌ streamlit 未安装`，运行：

```bash
pip install streamlit requests
```

等待安装完成（约 1-2 分钟）。

### 2.3 启动本地服务

```bash
cd "D:\AI\Sample\解析函数\deploy"
streamlit run app.py
```

**预期现象**：
- 命令行显示：`You can now view your Streamlit app in your browser.`
- 浏览器自动打开 `http://localhost:8501`

### 2.4 本地测试界面

1. 在左侧边栏的 **API Key** 输入框中填入你的 `sk-...` Key
2. 选择 **API 提供商**（推荐 `kimi`）
3. 选择 **模型**（推荐 `moonshot-v1-8k`）
4. 在下方聊天框输入测试问题：
   ```
   判断 f(z) = z^2 是否解析？
   ```
5. 按 **Enter** 发送，等待回复

**预期回复**（6 部分格式）：

```
📌 概念定位：复变函数的导数与解析性判定

📐 核心公式：
f'(z) = lim_{Δz→0} [f(z+Δz)-f(z)]/Δz

📝 详细推导：
步骤1：...
步骤2：...

💡 物理直觉：...

⚠️ 常见错误：
1. ...
2. ...

🎯 自检提问：...
```

如果看到以上格式，说明本地测试成功！

---

## 三、推送到 GitHub

### 3.1 方式一：双击脚本（推荐，最简单）

1. 打开文件资源管理器，进入：
   ```
   D:\AI\Sample\解析函数\deploy\
   ```
2. 双击 `deploy_to_github.bat`
3. 按提示输入：
   - GitHub 用户名（如 `dai_teacher`）
   - 仓库名称（建议 `math-agent`，或自定义）
   - 确认推送（输入 `Y`）

**脚本自动执行**：
- 初始化 Git 仓库
- 配置 Git 用户信息
- 添加远程仓库地址
- 提交所有文件
- 推送到 GitHub

### 3.2 方式二：手动命令（如果脚本失败）

如果脚本执行失败，可以手动执行：

```bash
# 1. 进入目录
cd "D:\AI\Sample\解析函数\deploy"

# 2. 初始化 Git 仓库
git init

# 3. 配置用户信息（只需一次）
git config user.email "your@email.com"
git config user.name "Your Name"

# 4. 添加远程仓库（替换为你的用户名）
git remote add origin https://github.com/你的用户名/math-agent.git

# 5. 提交文件
git add -A
git commit -m "Initial commit: 解析函数助教"

# 6. 推送到 GitHub
git branch -M main
git push -u origin main
```

### 3.3 在 GitHub 上创建仓库（如果未创建）

如果推送失败提示仓库不存在：

1. 打开 [github.com/new](https://github.com/new)
2. **Repository name**：输入 `math-agent`（与你输入的仓库名一致）
3. **Description**：可选，如 `数学物理方法-解析函数助教`
4. **Public** / **Private**：选 **Public**（免费且方便部署）
5. 取消勾选 **Add a README file**（我们已有文件）
6. 点击 **Create repository**
7. 重新运行推送脚本或命令

### 3.4 验证推送成功

1. 打开 `https://github.com/你的用户名/math-agent`
2. 应看到以下文件列表：
   ```
   app.py
   requirements.txt
   .gitignore
   README.md
   ```

---

## 四、部署到 Streamlit Cloud

Streamlit Cloud 是免费的 Python 应用托管平台，与 GitHub 无缝集成。

### 4.1 注册 Streamlit Cloud

1. 打开 [streamlit.io/cloud](https://streamlit.io/cloud)
2. 点击 **Sign in with GitHub**
3. 使用你的 GitHub 账号授权登录
4. 完成注册

### 4.2 创建应用

1. 登录后，点击页面右上角 **"Create app"**
2. 在弹出的界面中：
   - **Repository**：从下拉列表中选择 `你的用户名/math-agent`
   - **Branch**：`main`
   - **Main file path**：`app.py`
   - **Python version**：`3.11`
3. 点击 **Deploy!**

### 4.3 等待部署

- 页面会显示部署进度（约 2-3 分钟）
- 成功后会显示：
  ```
  🎉 Your app is ready!
  https://你的用户名-math-agent-xxx.streamlit.app
  ```
- 点击链接即可访问

### 4.4 验证公网访问

1. 用浏览器打开 `https://你的用户名-math-agent-xxx.streamlit.app`
2. 应看到与本地测试相同的界面
3. 填入 API Key，测试提问

> **注意**：Streamlit Cloud 免费版会休眠，如果 7 天无人访问，首次打开可能需要等待 30 秒唤醒。

---

## 五、添加到课程平台

现在将公网链接添加到湖南大学课程中心，学生可以直接从课程页面访问。

### 5.1 登录课程中心

1. 打开 [课程中心](http://kczx.hnu.edu.cn)
2. 使用教师账号登录
3. 进入课程：`G2S/Template/View.aspx?courseId=10916`

### 5.2 添加外部链接模块

不同课程平台版本界面可能略有不同，一般路径如下：

**路径一：课程资源 → 添加外部链接**

1. 找到课程管理后台中的 **"课程资源"** 或 **"教学资源"**
2. 点击 **"添加"** 或 **"新建"**
3. 选择类型：**"外部链接"**（或 **"网页链接"**）
4. 填写：
   | 字段 | 内容 |
   |------|------|
   | 名称 | `📐 解析函数AI助教` |
   | 链接 | `https://你的用户名-math-agent-xxx.streamlit.app` |
   | 描述 | 数学物理方法-解析函数章节的AI教学助手，支持C-R方程、解析性判定、调和函数等问题的24小时在线答疑 |
5. 点击 **保存**

**路径二：自定义模块 → 嵌入网页**

如果平台不支持外部链接，可以尝试：
1. 找到 **"自定义内容"** 或 **"HTML模块"**
2. 插入以下 HTML 代码：
   ```html
   <a href="https://你的用户名-math-agent-xxx.streamlit.app" 
      target="_blank" 
      style="display:block; background:#1B3A5C; color:white; padding:15px; text-align:center; border-radius:8px; text-decoration:none; font-size:16px;">
      📐 打开解析函数AI助教
   </a>
   ```

### 5.3 在课程公告中宣传

1. 发布课程公告：
   ```
   【新工具】解析函数AI助教已上线
   
   同学们好！
   
   为了辅助大家学习"解析函数与复变函数基础"章节，
   课程组部署了AI助教，支持以下功能：
   - 判断函数是否解析
   - 已知实部/虚部求解析函数
   - 解析函数性质证明
   - 初等复变函数分析
   
   使用方法：点击课程页面右侧的"📐 解析函数AI助教"链接，
   输入你的 Kimi API Key（免费注册）即可使用。
   
   提示：请自备 API Key，使用免费额度即可。
   ```

### 5.4 在课件中嵌入二维码

1. 用任意二维码生成器（如 [草料二维码](https://cli.im)）
2. 输入你的 Streamlit 链接
3. 生成二维码图片
4. 在 PPT 最后一页或课程资料中插入二维码

---

## 六、常见问题排查

### 6.1 本地测试问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `python 不是内部或外部命令` | Python 未添加到 PATH | 重装 Python，勾选 "Add to PATH" |
| `pip install 失败` | 网络问题 | 换国内源：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple streamlit` |
| `streamlit run 报错` | 端口被占用 | 换端口：`streamlit run app.py --server.port 8502` |
| `API Key 无效` | Key 错误/过期 | 重新到 platform.moonshot.cn 创建新 Key |
| `回复为空或报错` | 免费额度用完 | 检查 API 余额，或换 DeepSeek API |

### 6.2 GitHub 推送问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `fatal: not a git repository` | 未在 deploy 目录下运行 | `cd D:\AI\Sample\解析函数\deploy` |
| `Authentication failed` | 未登录 GitHub | 运行 `git credential-manager github login` |
| `Repository not found` | 仓库未创建 | 先到 github.com/new 创建仓库 |
| `Permission denied` | 无推送权限 | 检查仓库是否属于自己，或 Token 是否含 repo 权限 |

### 6.3 Streamlit Cloud 部署问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 部署失败，提示依赖错误 | requirements.txt 格式问题 | 确保文件内容只有 `streamlit>=1.30.0` 和 `requests>=2.31.0` |
| 页面加载慢 | 免费版休眠机制 | 等待 30 秒唤醒，或升级付费版 |
| 页面显示 "Error" | app.py 运行时错误 | 检查 app.py 中 API Key 输入逻辑是否正确 |
| 无法选择仓库 | GitHub 授权问题 | 重新授权 Streamlit 访问 GitHub 仓库 |

### 6.4 课程平台添加问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 找不到"添加外部链接" | 平台版本不同 | 联系信息中心或尝试"自定义模块" |
| 链接点击后空白 | 学校网络限制 | 尝试用手机流量测试，或联系网络中心 |
| 学生不会获取 API Key | 需要额外指导 | 在课程公告中附加 "API Key 获取教程" |

---

## 附录

### A. 完整文件清单

```
D:\AI\Sample\解析函数\deploy\
├── app.py                  ← Streamlit 主应用（核心文件）
├── requirements.txt        ← Python 依赖列表
├── .gitignore              ← Git 忽略配置
├── README.md               ← 项目说明
├── test_local.py           ← 本地测试脚本
├── deploy_to_github.bat    ← Windows 一键部署脚本
├── deploy_to_github.sh     ← Git Bash 一键部署脚本
└── DEPLOY_GUIDE.md         ← 本文件（部署指南）
```

### B. 技术架构

```
用户浏览器
    ↓ HTTP
Streamlit Cloud (免费托管)
    ↓ Python
app.py (前端UI + 后端逻辑)
    ↓ HTTPS API
Kimi / DeepSeek (大模型推理)
    ↓
System Prompt (教学提示词)
    ↓
结构化回答 (6部分格式)
```

### C. 费用说明

| 项目 | 费用 | 说明 |
|------|------|------|
| GitHub | 免费 | 代码托管 |
| Streamlit Cloud | 免费 | 应用托管（免费版有资源限制） |
| Kimi API | 免费额度 | 新用户送 15 元额度，约 15 万次请求 |
| DeepSeek API | 免费额度 | 新用户送 5000 万 tokens |

> **总计**：零成本启动，可支持一个班级（约 30-50 人）使用一学期。

### D. 更新维护

如果后续需要修改 Agent 的回答风格或知识内容：

1. 修改 `app.py` 中的 `SYSTEM_PROMPT` 变量
2. 重新提交到 GitHub：
   ```bash
   cd "D:\AI\Sample\解析函数\deploy"
   git add -A
   git commit -m "更新系统提示词"
   git push origin main
   ```
3. Streamlit Cloud 会自动检测代码更新并重新部署

---

*文档版本：v1.0 | 创建日期：2025-06-22 | 适用课程：数学物理方法（复变函数基础）*
