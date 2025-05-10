# Rolling K Auto Trade

📈 **KOSDAQ 상위 50 종목 기반 Rolling K 변동성 돌파 자동매매 시스템**

## ✅ 구성 요소

- FastAPI 기반 백엔드 API (`/rebalance`, `/order`, `/sell`, `/dashboard` 등)
- Streamlit 기반 실시간 대시보드
- Slack & Telegram 실시간 알림 연동

---

## ⚙️ 설치 및 실행 방법

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 열고 실제 Slack/Telegram 값을 입력
```

### 3. FastAPI 실행 (백엔드 API)
```bash
bash run_api.sh
# http://localhost:8000/docs 에서 API 테스트 가능
```

### 4. Streamlit 실행 (대시보드)
```bash
bash run_dashboard.sh
# http://localhost:8501 에서 실시간 매매 대시보드 확인
```

---

## 📡 주요 API 요약

| 경로 | 설명 |
|------|------|
| `/rebalance/latest` | 이번 달 리밸런싱 종목 추천 |
| `/rebalance/run/{date}` | 해당 월 종목 자동 매수 실행 |
| `/order/status` | 현재 보유 종목 상태 확인 |
| `/sell/check` | 손절/익절 조건 충족 시 자동 매도 |
| `/dashboard` | 전체 매수/매도 로그 요약 |
| `/report` | 수익률 기반 리포트 생성 |

---

## 📨 알림 연동 설정

`.env` 파일에 아래 항목을 설정:
```env
SLACK_WEBHOOK=your_webhook
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

---

## 🛠 향후 개선 과제
- 실시간 시세 API 연동
- 매수 후 분할매도 전략 도입
- 실전 증권사 API 연동 (신한i API 등)
