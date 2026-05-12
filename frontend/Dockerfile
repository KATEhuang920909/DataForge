# Build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY ../backend .
RUN npm run build

# Production stage
FROM nginx:stable-alpine AS production
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
# 使用阿里云上海节点的公开镜像（无需登录，但可能较旧）
FROM python:3.11-slim

WORKDIR /app

COPY ../backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../backend .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
