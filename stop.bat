@echo off
chcp 65001 >nul
title 停止墙体裂缝检测服务

echo ============================================
echo   停止墙体裂缝检测服务
echo ============================================

:: 查找占用 8000 端口的进程并终止
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING"') do (
    echo [停止] 终止进程 PID: %%a
    taskkill /f /pid %%a 2>nul
)

echo [完成] 服务已停止
timeout /t 2 /nobreak >nul
exit /b 0
