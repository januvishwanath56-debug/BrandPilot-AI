FROM node:22-alpine AS ui
WORKDIR /workspace/frontend
COPY frontend/package*.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /workspace
COPY requirements-lock.txt ./
RUN pip install --no-cache-dir -r requirements-lock.txt
COPY backend/ ./backend/
COPY --from=ui /workspace/frontend/dist ./frontend/dist
ENV PYTHONUNBUFFERED=1
RUN useradd --create-home appuser && chown -R appuser:appuser /workspace
USER appuser
EXPOSE 8000
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
