# ---------- Build stage ----------
FROM node:20-alpine AS build
WORKDIR /app

# 의존성 설치
COPY package*.json ./
RUN npm install --no-audit --no-fund

# 소스 복사 & 빌드
COPY . .
RUN npm run build

# ---------- Runtime stage ----------
FROM nginx:1.27-alpine AS runtime

# Nginx 기본 정적 경로
WORKDIR /usr/share/nginx/html

# 기존 기본 파일들 삭제 (index.html 등)
RUN rm -rf ./*

# CRA 빌드 결과 복사
COPY --from=build /app/build ./

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
