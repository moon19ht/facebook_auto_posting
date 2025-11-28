"""
Facebook 자동 포스팅 - Playwright 브라우저 자동화 방식

이 모듈은 Playwright를 사용하여 페이스북에 로그인하고 게시물을 작성합니다.
Selenium보다 빠르고 최신 웹 기술에 대한 호환성이 좋습니다.
⚠️ 주의: 이 방식은 계정 차단 위험이 있으므로 테스트 계정으로 먼저 테스트하세요.
"""

import time
from typing import Optional, List
from pathlib import Path

from playwright.sync_api import (
    sync_playwright, 
    Page, 
    Browser, 
    BrowserContext,
    TimeoutError as PlaywrightTimeoutError
)

from config import Config


class FacebookPlaywrightBot:
    """Playwright를 사용한 Facebook 자동화 봇"""
    
    # 선택자 정의
    SELECTORS = {
        # 로그인 관련
        "email_input": "#email",
        "password_input": "#pass",
        "login_button": "button[name='login']",
        
        # 포스팅 관련 (다국어 지원)
        "whats_on_your_mind": [
            "span:has-text('무슨 생각')",
            "span:has-text(\"What's on your mind\")",
            "[aria-label*='생각']",
            "[aria-label*='mind']"
        ],
        "post_textbox": "div[contenteditable='true'][role='textbox']",
        "post_button": [
            "div[aria-label='게시']",
            "div[aria-label='Post']",
            "span:has-text('게시')",
            "span:has-text('Post')"
        ],
        "photo_video_button": [
            "[aria-label='사진/동영상']",
            "[aria-label='Photo/video']",
            "[aria-label*='Photo']",
            "[aria-label*='사진']"
        ],
        
        # 팝업 관련
        "close_buttons": [
            "[aria-label='닫기']",
            "[aria-label='Close']",
            "div[aria-label='닫기']",
            "div[aria-label='Close']"
        ],
        "not_now_buttons": [
            "span:has-text('나중에')",
            "span:has-text('Not Now')",
            "span:has-text('Not now')"
        ],
        
        # 로그인 정보 저장 팝업 (취소 버튼)
        "save_login_cancel": [
            "[aria-label='취소']",
            "[aria-label='Cancel']",
            "div[aria-label='취소']",
            "div[aria-label='Cancel']",
            "span:has-text('취소')",
            "span:has-text('Decline')",
            "button:has-text('취소')",
            "button:has-text('Cancel')",
            "[aria-label*='다음에']",
            "span:has-text('다음에')"
        ]
    }
    
    def __init__(
        self, 
        email: Optional[str] = None, 
        password: Optional[str] = None,
        headless: bool = False,
        slow_mo: int = 100
    ):
        """
        Playwright 봇 초기화
        
        Args:
            email: Facebook 로그인 이메일
            password: Facebook 로그인 비밀번호
            headless: 헤드리스 모드 여부
            slow_mo: 동작 사이 지연 시간 (ms)
        """
        self.email = email or Config.EMAIL
        self.password = password or Config.PASSWORD
        self.headless = headless
        self.slow_mo = slow_mo
        
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        self._validate_credentials()
    
    def _validate_credentials(self) -> None:
        """로그인 정보 유효성 검사"""
        if not self.email or not self.password:
            raise ValueError(
                "❌ 이메일 또는 비밀번호가 설정되지 않았습니다.\n"
                "   .env 파일에 FACEBOOK_EMAIL과 FACEBOOK_PASSWORD를 설정하세요."
            )
    
    def start_browser(self) -> None:
        """브라우저 시작"""
        print("🌐 브라우저를 시작합니다...")
        
        self.playwright = sync_playwright().start()
        
        # 브라우저 런치 옵션
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-notifications",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        
        # 컨텍스트 생성 (봇 탐지 회피 설정)
        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="ko-KR",
            timezone_id="Asia/Seoul"
        )
        
        # 새 페이지 생성
        self.page = self.context.new_page()
        
        # 자동화 탐지 회피
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        print("✅ 브라우저 시작 완료")
    
    def close_browser(self) -> None:
        """브라우저 종료"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("🔒 브라우저를 종료했습니다.")
    
    def _try_click(self, selectors: List[str], timeout: int = 5000) -> bool:
        """여러 선택자 중 하나를 클릭 시도"""
        for selector in selectors:
            try:
                element = self.page.wait_for_selector(
                    selector, 
                    timeout=timeout, 
                    state="visible"
                )
                if element:
                    element.click()
                    return True
            except PlaywrightTimeoutError:
                continue
        return False
    
    def _dismiss_popups(self) -> None:
        """팝업 닫기 시도"""
        time.sleep(1)
        
        # 닫기 버튼 시도
        self._try_click(self.SELECTORS["close_buttons"], timeout=2000)
        
        # "나중에" 버튼 시도
        self._try_click(self.SELECTORS["not_now_buttons"], timeout=2000)
    
    def _dismiss_save_login_popup(self) -> None:
        """로그인 정보 저장 팝업에서 취소 클릭"""
        time.sleep(1)
        
        # 취소 버튼 클릭 시도
        if self._try_click(self.SELECTORS["save_login_cancel"], timeout=3000):
            print("📌 로그인 정보 저장 팝업에서 '취소'를 클릭했습니다.")
            return
        
        # 대체 방법: 버튼 텍스트로 찾기
        try:
            buttons = self.page.query_selector_all("button, div[role='button']")
            for btn in buttons:
                btn_text = btn.inner_text().lower() if btn.inner_text() else ""
                if btn_text in ['취소', 'cancel', 'decline', '다음에', 'not now']:
                    btn.click()
                    print("📌 로그인 정보 저장 팝업에서 '취소'를 클릭했습니다.")
                    time.sleep(1)
                    return
        except Exception:
            pass
    
    def login(self, manual_2fa_timeout: int = 30) -> bool:
        """
        Facebook 로그인
        
        Args:
            manual_2fa_timeout: 2단계 인증 수동 개입 대기 시간 (초)
            
        Returns:
            로그인 성공 여부
        """
        try:
            print("🔑 로그인을 시작합니다...")
            
            # 로그인 페이지로 이동
            self.page.goto(Config.FACEBOOK_LOGIN_URL)
            self.page.wait_for_load_state("networkidle")
            
            # 쿠키/팝업 처리
            self._dismiss_popups()
            
            # 이메일 입력
            email_input = self.page.wait_for_selector(
                self.SELECTORS["email_input"],
                timeout=10000
            )
            email_input.fill(self.email)
            print("📧 이메일 입력 완료")
            
            # 비밀번호 입력
            password_input = self.page.wait_for_selector(
                self.SELECTORS["password_input"]
            )
            password_input.fill(self.password)
            print("🔒 비밀번호 입력 완료")
            
            # 로그인 버튼 클릭
            login_button = self.page.wait_for_selector(
                self.SELECTORS["login_button"]
            )
            login_button.click()
            print("🚀 로그인 버튼 클릭")
            
            # 페이지 로딩 대기
            self.page.wait_for_load_state("networkidle")
            time.sleep(3)
            
            # 2단계 인증 확인
            if "checkpoint" in self.page.url:
                print(f"⚠️  2단계 인증이 필요합니다.")
                print(f"   {manual_2fa_timeout}초 동안 수동으로 인증을 완료해주세요...")
                print("   (인증 완료 후 Enter를 눌러 계속하거나 대기하세요)")
                
                # 사용자 입력 대기 또는 타임아웃
                try:
                    import sys
                    import select
                    
                    # 타임아웃과 함께 사용자 입력 대기
                    for i in range(manual_2fa_timeout):
                        if "checkpoint" not in self.page.url:
                            break
                        print(f"\r⏳ 남은 시간: {manual_2fa_timeout - i}초", end="", flush=True)
                        time.sleep(1)
                    print()
                except:
                    time.sleep(manual_2fa_timeout)
            
            # 로그인 성공 확인
            current_url = self.page.url
            if "facebook.com" in current_url and "login" not in current_url:
                print("✅ 로그인 성공!")
                
                # 로그인 정보 저장 팝업 처리
                time.sleep(2)
                self._dismiss_save_login_popup()
                self._dismiss_popups()
                return True
            else:
                print("❌ 로그인에 실패했습니다.")
                return False
                
        except PlaywrightTimeoutError as e:
            print(f"❌ 시간 초과: {e}")
            return False
        except Exception as e:
            print(f"❌ 로그인 중 오류 발생: {e}")
            return False
    
    def create_post(
        self, 
        message: str, 
        image_paths: Optional[List[str]] = None
    ) -> bool:
        """
        게시물 작성
        
        Args:
            message: 게시할 텍스트
            image_paths: 업로드할 이미지 파일 경로 목록
            
        Returns:
            게시 성공 여부
        """
        try:
            print("📝 게시물 작성을 시작합니다...")
            
            # 홈 페이지로 이동
            self.page.goto(Config.FACEBOOK_HOME_URL)
            self.page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            self._dismiss_popups()
            
            # "무슨 생각을 하고 계신가요?" 클릭
            if not self._try_click(self.SELECTORS["whats_on_your_mind"], timeout=10000):
                print("❌ 게시물 입력창을 찾을 수 없습니다.")
                return False
            
            time.sleep(2)
            
            # 이미지 업로드
            if image_paths:
                self._upload_images(image_paths)
            
            # 텍스트 입력
            text_input = self.page.wait_for_selector(
                self.SELECTORS["post_textbox"],
                timeout=10000
            )
            text_input.click()
            time.sleep(0.5)
            
            # 메시지 입력 (타이핑 효과)
            text_input.type(message, delay=50)
            print(f"✏️  메시지 입력 완료: {message[:50]}...")
            
            time.sleep(2)
            
            # 게시 버튼 클릭
            if self._try_click(self.SELECTORS["post_button"], timeout=10000):
                print("✅ 게시물이 업로드되었습니다!")
                time.sleep(3)
                return True
            else:
                print("❌ 게시 버튼을 찾을 수 없습니다.")
                return False
                
        except PlaywrightTimeoutError as e:
            print(f"❌ 시간 초과: {e}")
            return False
        except Exception as e:
            print(f"❌ 게시물 작성 중 오류: {e}")
            return False
    
    def _upload_images(self, image_paths: List[str]) -> bool:
        """
        이미지 업로드
        
        Args:
            image_paths: 업로드할 이미지 파일 경로 목록
            
        Returns:
            업로드 성공 여부
        """
        try:
            # 사진/동영상 버튼 클릭
            if not self._try_click(self.SELECTORS["photo_video_button"], timeout=5000):
                print("⚠️  사진/동영상 버튼을 찾을 수 없습니다.")
                return False
            
            time.sleep(1)
            
            # 파일 입력 요소 찾기 및 파일 업로드
            file_input = self.page.wait_for_selector(
                "input[type='file'][accept*='image']",
                timeout=5000
            )
            
            for image_path in image_paths:
                abs_path = str(Path(image_path).resolve())
                
                if not Path(abs_path).exists():
                    print(f"⚠️  파일을 찾을 수 없습니다: {abs_path}")
                    continue
                
                file_input.set_input_files(abs_path)
                print(f"📎 이미지 업로드: {abs_path}")
                time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"❌ 이미지 업로드 중 오류: {e}")
            return False
    
    def take_screenshot(self, path: str = "screenshot.png") -> None:
        """스크린샷 저장"""
        if self.page:
            self.page.screenshot(path=path)
            print(f"📸 스크린샷 저장: {path}")
    
    def __enter__(self):
        """Context manager 진입"""
        self.start_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.close_browser()


def main():
    """테스트 실행"""
    print("=" * 50)
    print("Facebook Playwright 자동화 봇 테스트")
    print("=" * 50)
    print("⚠️  주의: 이 스크립트는 테스트 계정으로만 실행하세요!")
    print()
    
    try:
        with FacebookPlaywrightBot(headless=False, slow_mo=100) as bot:
            # 로그인 (2FA 대기 시간 30초)
            if bot.login(manual_2fa_timeout=30):
                # 게시물 작성 (테스트 시 주석 해제)
                # bot.create_post(
                #     "안녕하세요! Playwright 자동화 테스트입니다. 🎭",
                #     image_paths=["./uploads/test.jpg"]
                # )
                
                # 스크린샷 저장
                bot.take_screenshot("facebook_home.png")
                
                # 잠시 대기 후 종료
                print("테스트 완료. 5초 후 브라우저를 종료합니다...")
                time.sleep(5)
            else:
                print("로그인에 실패했습니다.")
                bot.take_screenshot("login_failed.png")
                
    except Exception as e:
        print(f"오류 발생: {e}")


if __name__ == "__main__":
    main()
