"""
Facebook 자동 포스팅 - 공통 설정 파일
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class Config:
    """애플리케이션 설정 클래스"""
    
    # Facebook API 설정
    ACCESS_TOKEN: str = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
    PAGE_ID: str = os.getenv("FACEBOOK_PAGE_ID", "")
    
    # Facebook 로그인 정보 (Selenium/Playwright용)
    EMAIL: str = os.getenv("FACEBOOK_EMAIL", "")
    PASSWORD: str = os.getenv("FACEBOOK_PASSWORD", "")
    
    # 브라우저 설정
    HEADLESS_MODE: bool = os.getenv("HEADLESS_MODE", "false").lower() == "true"
    BROWSER_TYPE: str = os.getenv("BROWSER_TYPE", "chrome")
    
    # Facebook URL
    FACEBOOK_LOGIN_URL: str = "https://www.facebook.com/login"
    FACEBOOK_HOME_URL: str = "https://www.facebook.com"
    
    # 대기 시간 설정 (초)
    DEFAULT_WAIT_TIME: int = 10
    LONG_WAIT_TIME: int = 30
    SHORT_WAIT_TIME: int = 3
    
    # 파일 경로
    BASE_DIR: Path = Path(__file__).parent
    UPLOADS_DIR: Path = BASE_DIR / "uploads"
    
    @classmethod
    def validate_api_config(cls) -> bool:
        """API 설정 유효성 검사"""
        if not cls.ACCESS_TOKEN or not cls.PAGE_ID:
            print("⚠️  ACCESS_TOKEN 또는 PAGE_ID가 설정되지 않았습니다.")
            print("   .env 파일을 확인하세요.")
            return False
        return True
    
    @classmethod
    def validate_login_config(cls) -> bool:
        """로그인 정보 유효성 검사"""
        if not cls.EMAIL or not cls.PASSWORD:
            print("⚠️  EMAIL 또는 PASSWORD가 설정되지 않았습니다.")
            print("   .env 파일을 확인하세요.")
            return False
        return True


# 업로드 디렉토리 생성
Config.UPLOADS_DIR.mkdir(exist_ok=True)
