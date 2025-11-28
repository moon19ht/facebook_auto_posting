# 🔵 Facebook Auto Posting Tool

페이스북 자동 포스팅을 위한 Python 프로그램입니다. 세 가지 방식을 지원합니다.

## ✨ 주요 특징

- 🔐 **공식 API 지원**: facebook-sdk를 통한 안전한 포스팅
- 🤖 **브라우저 자동화**: Selenium, Playwright 지원
- 🔒 **보안 강화**: 환경 변수를 통한 민감 정보 관리
- 🌐 **다국어 팝업 처리**: 한국어/영어 UI 자동 대응
- 📝 **로그인 정보 저장 팝업 자동 처리**: 취소 버튼 자동 클릭
- 🖥️ **CLI & 대화형 모드**: 다양한 실행 방식 제공

## 📋 지원 기능

| 방식 | 텍스트 | 이미지 | 동영상 | 안정성 | 설정 난이도 |
|------|:------:|:------:|:------:|:------:|:-----------:|
| **공식 API** | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ | 중간 |
| **Selenium** | ✅ | ✅ | ✅ | ⭐⭐⭐ | 쉬움 |
| **Playwright** | ✅ | ✅ | ⚠️ | ⭐⭐⭐⭐ | 쉬움 |

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/moon19ht/facebook_auto_posting.git
cd facebook_auto_posting
```

### 2. 가상환경 생성 (권장)
```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 의존성 설치
```bash
# 전체 설치
pip install -r requirements.txt

# 또는 필요한 방식만 설치
pip install python-dotenv facebook-sdk requests  # API 방식
pip install python-dotenv selenium webdriver-manager  # Selenium 방식
pip install python-dotenv playwright && playwright install chromium  # Playwright 방식
```

### 4. 환경 변수 설정
```bash
cp .env.example .env
```

`.env` 파일을 편집하여 인증 정보를 입력합니다:
```env
# 공식 API 방식 사용 시
FACEBOOK_ACCESS_TOKEN=your_access_token_here
FACEBOOK_PAGE_ID=your_page_id_here

# Selenium/Playwright 방식 사용 시
FACEBOOK_EMAIL=your_email@example.com
FACEBOOK_PASSWORD=your_password_here
```

### 5. 실행
```bash
# 대화형 모드
python main.py

# CLI 모드
python main.py --mode api --message "안녕하세요!"
```

---

## 📘 방식별 상세 가이드

### 1️⃣ 공식 API 방식 (권장)

가장 안정적이고 안전한 방식입니다. 페이스북 개발자 계정이 필요합니다.

#### 사전 준비
1. [Facebook Developers](https://developers.facebook.com/)에서 앱 생성
2. 페이지 관리 권한 획득 (`pages_manage_posts`, `pages_read_engagement`)
3. 액세스 토큰 발급

#### 사용 예시
```python
from facebook_api_poster import FacebookAPIClient

client = FacebookAPIClient()

# 텍스트 게시
client.post_text("안녕하세요! 🎉")

# 이미지 게시
client.post_image("./uploads/photo.jpg", "사진과 함께 포스팅")

# 동영상 게시
client.post_video("./uploads/video.mp4", title="영상 제목", description="설명")

# 링크 공유
client.post_link("https://example.com", "이 링크를 확인해보세요!")
```

---

### 2️⃣ Selenium 브라우저 자동화

실제 브라우저를 조작하여 포스팅합니다. 개발자 계정이 필요 없습니다.

#### ⚠️ 주의사항
- **테스트 계정 사용 필수**: 본 계정 사용 시 차단될 수 있습니다
- UI 변경 시 코드 수정이 필요할 수 있습니다
- 자동화 탐지로 인한 보안 문자 발생 가능

#### 자동 처리 기능
- ✅ 로그인 정보 저장 팝업 자동 취소
- ✅ 알림 권한 요청 팝업 자동 닫기
- ✅ 기타 방해 팝업 자동 처리

#### 사용 예시
```python
from facebook_selenium_bot import FacebookSeleniumBot

# Context manager 사용 (권장)
with FacebookSeleniumBot(headless=False) as bot:
    if bot.login():
        bot.create_post(
            "Selenium 자동 포스팅! 🤖",
            media_paths=["./uploads/image.jpg"]
        )
```

---

### 3️⃣ Playwright 브라우저 자동화

Selenium보다 빠르고 안정적인 최신 자동화 도구입니다.

#### Playwright 설치
```bash
pip install playwright
playwright install chromium
```

#### 사용 예시
```python
from facebook_playwright_bot import FacebookPlaywrightBot

with FacebookPlaywrightBot(headless=False, slow_mo=100) as bot:
    # 2FA 대기 시간 30초 설정
    if bot.login(manual_2fa_timeout=30):
        bot.create_post(
            "Playwright 자동 포스팅! 🎭",
            image_paths=["./uploads/image.jpg"]
        )
        bot.take_screenshot("result.png")
```

---

## 🛠️ CLI 사용법

```bash
# 대화형 모드
python main.py

# API 방식으로 텍스트 포스팅
python main.py --mode api --message "안녕하세요!"

# Selenium으로 이미지 포스팅
python main.py --mode selenium --message "사진 공유" --media ./photo.jpg

# Playwright로 여러 이미지 포스팅
python main.py --mode playwright --message "여러 사진" --media img1.jpg img2.jpg
```

---

## 📁 프로젝트 구조

```
facebook_auto_posting/
├── config.py                  # 공통 설정
├── main.py                    # 메인 실행 스크립트
├── facebook_api_poster.py     # 공식 API 방식
├── facebook_selenium_bot.py   # Selenium 방식
├── facebook_playwright_bot.py # Playwright 방식
├── requirements.txt           # 의존성 목록
├── .env.example              # 환경 변수 예시
├── .env                      # 환경 변수 (git ignore)
├── uploads/                  # 업로드 파일 디렉토리
└── README.md                 # 이 문서
```

---

## 🔒 보안 주의사항

1. **절대 `.env` 파일을 Git에 커밋하지 마세요**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **액세스 토큰은 주기적으로 갱신하세요**

3. **브라우저 자동화 방식은 테스트 계정으로만 사용하세요**

4. **2단계 인증(2FA)을 활성화하세요**

---

## 🐛 문제 해결

### 로그인 실패
- 이메일/비밀번호 확인
- 2단계 인증 활성화 여부 확인
- 계정 보안 설정 확인

### ChromeDriver 오류
```bash
pip install --upgrade webdriver-manager
```

### Playwright 브라우저 미설치
```bash
playwright install chromium
```

### API 권한 오류
- 액세스 토큰 만료 여부 확인
- 필요한 권한이 부여되었는지 확인
- 앱이 라이브 모드인지 확인

---

## 📜 라이선스

MIT License

---

## 🤝 기여

이슈 및 PR 환영합니다!

---

## ⚠️ 면책 조항

이 도구는 교육 목적으로 제작되었습니다. 페이스북의 이용약관을 준수하여 사용하세요. 
자동화 도구의 무분별한 사용은 계정 정지를 초래할 수 있습니다.

---

## 📅 업데이트 내역

### v1.0.0 (2025-11-28)
- 🎉 최초 릴리스
- 공식 API 방식 (facebook-sdk) 구현
- Selenium 브라우저 자동화 구현
- Playwright 브라우저 자동화 구현
- 로그인 정보 저장 팝업 자동 취소 기능
- 다국어 팝업 처리 (한국어/영어)
- CLI 및 대화형 모드 지원
