FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY .env.example .env.example

# 暴露端口
EXPOSE 8000

# 启动
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
