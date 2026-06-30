@echo off
cd /d D:\python_code\Agent-Langchain-RAG-FastAPI

echo ========================================
echo  启动后端服务（前台窗口，请勿关闭）
echo ========================================
echo.

echo [1/2] 启动 FastAPIUserService (端口 8000)...
start "FastAPIUserService" cmd /k ".venv\Scripts\python.exe -m uvicorn FastAPIUserService.main:app --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] 启动 Backend Agent (端口 8001)...
start "BackendAgent" cmd /k "set USER_SERVICE_URL=http://localhost:8000 && .venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8001"

echo.
echo ========================================
echo  两个后端服务已启动!
echo  FastAPIUserService : http://localhost:8000  (登录/新闻/收藏/历史)
echo  Backend Agent      : http://localhost:8001  (AI 问答/知识库)
echo  前端启动命令: cd xwzx-news ^&^& npm run dev
echo ========================================
echo.
echo 提示: 每个服务都在独立窗口中运行，关闭窗口即可停止
pause
