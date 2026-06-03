@echo off
chcp 65001 >nul
title 墙体裂缝检测系统

cd /d "%~dp0"

echo ============================================
echo   墙体裂缝检测与审核报告系统 v3.0
echo ============================================
echo.

:: 检查端口是否已占用
netstat -ano | findstr ":8000.*LISTENING" >nul
if %errorlevel%==0 (
    echo [提示] 服务已在运行，直接打开浏览器...
    start http://localhost:8000
    goto :end
)

:: 检查 Python
set PYTHON_CMD=
python --version >nul 2>&1
if %errorlevel%==0 (
    set PYTHON_CMD=python
) else (
    py --version >nul 2>&1
    if %errorlevel%==0 (
        set PYTHON_CMD=py
    ) else (
        echo [错误] 未找到 Python，请确认已安装 Python 3.10+
        echo        下载地址：https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

echo [启动] 正在启动服务...
echo.
start "墙体裂缝检测服务" /MIN %PYTHON_CMD% "%~dp0_run_server.py"

:: 等待服务就绪（使用 Python 健康检查，避免依赖 curl）
echo [等待] 等待服务就绪...
:wait
timeout /t 2 /nobreak >nul
%PYTHON_CMD% -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=2)" >nul 2>&1
if %errorlevel% neq 0 (
    goto :wait
)

echo [就绪] 服务启动成功！
start http://localhost:8000
echo ============================================
echo   浏览器已打开 http://localhost:8000
echo   关闭此窗口不会停止服务
echo   停止服务请运行: stop.bat
echo ============================================

:end
timeout /t 3 /nobreak >nul
