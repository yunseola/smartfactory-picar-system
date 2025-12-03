# ── Build stage ─────────────────────────────────────────────
FROM gradle:8.9-jdk21-alpine AS build
WORKDIR /src

# gradle/wrapper 관련 파일 먼저 복사해서 캐시 활용
COPY build.gradle settings.gradle gradlew ./
COPY gradle ./gradle
RUN chmod +x gradlew
RUN ./gradlew --version

# 나머지 소스 복사
COPY . .

# 테스트는 CI에서 하니까 빌드 시 제외
RUN ./gradlew clean bootJar -x test

# ── Runtime stage ───────────────────────────────────────────
FROM eclipse-temurin:21-jre
WORKDIR /app

# (curl 필요하면) 여기서 설치
# Debian/Ubuntu 베이스일 때만 유효
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

# 빌드 산출물 복사
COPY --from=build /src/build/libs/*.jar /app/app.jar

# 포트는 선택
EXPOSE 8080

# 실행
ENTRYPOINT ["java","-jar","/app/app.jar"]
