#!/bin/bash

# Calendar Suite 배포 스크립트
# 사용법: ./deploy.sh

echo "🚀 배포를 시작합니다..."

# 1. 최신 코드 가져오기
echo "📥 Git Pull..."
git pull origin main

# 2. 컨테이너 재빌드 및 실행
echo "🐳 Docker Compose Up..."
docker compose down
docker compose up -d --build

# 3. 불필요한 이미지 정리 (선택)
echo "🧹 Cleaning up..."
docker image prune -f

echo "✅ 배포가 완료되었습니다!"
