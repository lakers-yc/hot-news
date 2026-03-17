@echo off
chcp 65001 > nul
echo ========================================
echo   热点追踪服务启动脚本
echo ========================================
echo.

cd /d "%~dp0"

echo 检查 Python 环境...
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo 检查依赖...
pip show flask > nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements.txt
)

echo.
echo 启动服务...
echo 服务地址: http://localhost:5003
echo 按 Ctrl+C 停止服务
echo.

python server.py

pause