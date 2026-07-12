@echo off
chcp 65001 >nul
cls

echo ============================================
echo  📐 解析函数助教 - GitHub 一键部署脚本
echo ============================================
echo.

REM 检查 git 是否安装
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到 Git，请先安装：
    echo    https://git-scm.com/download/win
    pause
    exit /b 1
)
echo ✅ Git 已安装

REM 检查当前目录
if not exist "app.py" (
    echo ❌ 未找到 app.py，请确保在 deploy 目录下运行此脚本
    echo    当前目录: %CD%
    pause
    exit /b 1
)
echo ✅ 当前目录正确: %CD%
echo.

REM 输入配置
set /p GITHUB_USERNAME=请输入你的 GitHub 用户名: 
set /p REPO_NAME=请输入仓库名称 (默认: math-agent): 
if "%REPO_NAME%"=="" set REPO_NAME=math-agent

echo.
echo ============================================
echo  配置信息：
echo    GitHub 用户名: %GITHUB_USERNAME%
echo    仓库名: %REPO_NAME%
echo ============================================
echo.

set /p CONFIRM=确认无误？按 Y 继续，按 N 取消: 
if /i not "%CONFIRM%"=="Y" (
    echo 已取消
    pause
    exit /b 0
)

REM 初始化 Git 仓库
echo.
echo 🔄 初始化 Git 仓库...
if not exist .git (
    git init
    echo ✅ Git 仓库初始化完成
) else (
    echo ⚠️  Git 仓库已存在
)

REM 配置 Git 用户信息（如果未设置）
git config user.email >nul 2>&1
if errorlevel 1 (
    echo 📝 配置 Git 用户信息...
    git config user.email "teacher@hnu.edu.cn"
    git config user.name "Math Teacher"
    echo ✅ Git 用户信息已配置
)

REM 添加远程仓库
echo.
echo 🔄 添加远程仓库...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
echo ✅ 远程仓库已添加: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git

REM 创建提交
echo.
echo 📦 提交文件...
git add -A
git commit -m "Initial commit: 解析函数助教 Streamlit 应用"
if errorlevel 1 (
    echo ⚠️  提交可能已存在，尝试强制提交...
)
echo ✅ 文件已提交

REM 推送到 GitHub
echo.
echo 🚀 推送到 GitHub...
echo    如果需要登录，请输入你的 GitHub 账号密码或 Token...
git branch -M main
git push -u origin main
if errorlevel 1 (
    echo.
    echo ❌ 推送失败！请检查以下问题：
    echo    1. 是否已在 GitHub 上创建仓库: %REPO_NAME%
    echo    2. GitHub 用户名是否正确: %GITHUB_USERNAME%
    echo    3. 是否已登录 GitHub (git credential-manager)
    echo.
    echo    如果仓库未创建，请访问：
    echo    https://github.com/new?name=%REPO_NAME%
    echo.
    pause
    exit /b 1
)

echo ✅ 推送成功！
echo.

REM 输出下一步指引
echo ============================================
echo  🎉 部署完成！下一步操作：
echo ============================================
echo.
echo 1. 打开 Streamlit Cloud：
echo    https://share.streamlit.io
echo.
echo 2. 点击 "Create app"，选择仓库：
echo    %GITHUB_USERNAME%/%REPO_NAME%
echo.
echo 3. 设置：
echo    - Main file path: app.py
echo    - Python version: 3.11
echo.
echo 4. 点击 "Deploy!" 等待 2-3 分钟
echo.
echo 5. 获得链接后，添加到课程平台：
echo    https://kczx.hnu.edu.cn/G2S/Template/View.aspx?courseId=10916
echo.
echo ============================================
echo.

REM 可选：打开浏览器
echo 🌐 是否打开 Streamlit Cloud？
set /p OPEN_BROWSER=按 Y 打开浏览器，按 N 退出: 
if /i "%OPEN_BROWSER%"=="Y" (
    start https://share.streamlit.io
)

pause
