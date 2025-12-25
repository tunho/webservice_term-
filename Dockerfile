FROM python:3.11-slim-bookworm

WORKDIR /app
ENV PYTHONPATH=/app/src

# 시스템 의존성 설치 (네트워크 이슈로 생략 - Wheel 사용 시도)
# RUN sed -i 's/deb.debian.org/mirror.kakao.com/g' /etc/apt/sources.list.d/debian.sources && \
#     apt-get update && apt-get install -y \
#     gcc \
#     && rm -rf /var/lib/apt/lists/*

# Python 의존성 복사 및 설치 (Offline Install)
COPY wheels /app/wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/app/wheels -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8080

# 서버 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]







