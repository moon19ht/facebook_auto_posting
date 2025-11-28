"""
Facebook 자동 포스팅 - Selenium 브라우저 자동화 방식

이 모듈은 Selenium WebDriver를 사용하여 페이스북에 로그인하고 게시물을 작성합니다.
⚠️ 주의: 이 방식은 계정 차단 위험이 있으므로 테스트 계정으로 먼저 테스트하세요.
"""

import os
import time
from typing import Optional, List
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException,
    ElementClickInterceptedException,
    WebDriverException
)
from webdriver_manager.chrome import ChromeDriverManager

from config import Config


class FacebookSeleniumBot:
    """Selenium을 사용한 Facebook 자동화 봇"""
    
    # 자주 사용되는 XPath/CSS 선택자
    SELECTORS = {
        # 로그인 관련
        "email_input": "//input[@id='email']",
        "password_input": "//input[@id='pass']",
        "login_button": "//button[@name='login']",
        
        # 포스팅 관련
        "whats_on_your_mind": "//span[contains(text(), '무슨 생각')]",
        "whats_on_your_mind_en": "//span[contains(text(), \"What's on your mind\")]",
        "post_box": "//div[@role='dialog']//div[@contenteditable='true']",
        "post_button": "//div[@aria-label='게시']",
        "post_button_en": "//div[@aria-label='Post']",
        "photo_video_button": "//div[@aria-label='사진/동영상']",
        "photo_video_button_en": "//div[@aria-label='Photo/video']",
        "file_input": "//input[@type='file'][@accept]",
        
        # 팝업 관련
        "close_popup": "//div[@aria-label='닫기']",
        "close_popup_en": "//div[@aria-label='Close']",
        "not_now_button": "//span[contains(text(), '나중에')]",
        "not_now_button_en": "//span[contains(text(), 'Not Now')]",
        
        # 로그인 정보 저장 팝업 (취소 버튼)
        "save_login_cancel": "//div[@aria-label='취소']",
        "save_login_cancel_en": "//div[@aria-label='Cancel']",
        "save_login_decline": "//span[contains(text(), '취소')]",
        "save_login_decline_en": "//span[contains(text(), 'Decline')]",
        "save_login_not_now": "//div[contains(@aria-label, '다음에')]",
    }
    
    def __init__(
        self, 
        email: Optional[str] = None, 
        password: Optional[str] = None,
        headless: bool = False
    ):
        """
        Selenium 봇 초기화
        
        Args:
            email: Facebook 로그인 이메일 (없으면 환경 변수에서 로드)
            password: Facebook 로그인 비밀번호 (없으면 환경 변수에서 로드)
            headless: 헤드리스 모드 여부 (True면 브라우저 창이 보이지 않음)
        """
        self.email = email or Config.EMAIL
        self.password = password or Config.PASSWORD
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        
        self._validate_credentials()
    
    def _validate_credentials(self) -> None:
        """로그인 정보 유효성 검사"""
        if not self.email or not self.password:
            raise ValueError(
                "❌ 이메일 또는 비밀번호가 설정되지 않았습니다.\n"
                "   .env 파일에 FACEBOOK_EMAIL과 FACEBOOK_PASSWORD를 설정하세요."
            )
    
    def _get_chrome_options(self) -> Options:
        """Chrome 옵션 설정"""
        options = Options()
        
        # 헤드리스 모드
        if self.headless:
            options.add_argument("--headless=new")
        
        # 봇 탐지 회피를 위한 설정
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # User-Agent 설정 (실제 브라우저처럼 보이도록)
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        options.add_argument(f"user-agent={user_agent}")
        
        # 알림 비활성화
        options.add_argument("--disable-notifications")
        
        # 기타 안정성 옵션
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--lang=ko-KR")
        
        return options
    
    def start_browser(self) -> None:
        """브라우저 시작"""
        try:
            print("🌐 브라우저를 시작합니다...")
            
            service = Service(ChromeDriverManager().install())
            options = self._get_chrome_options()
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, Config.DEFAULT_WAIT_TIME)
            
            # 자동화 탐지 회피를 위한 JavaScript 실행
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            print("✅ 브라우저 시작 완료")
            
        except WebDriverException as e:
            raise RuntimeError(f"❌ 브라우저 시작 실패: {e}")
    
    def close_browser(self) -> None:
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()
            print("🔒 브라우저를 종료했습니다.")
    
    def _find_element_with_retry(
        self, 
        selectors: List[str], 
        timeout: int = None
    ):
        """여러 선택자를 시도하여 요소 찾기"""
        timeout = timeout or Config.DEFAULT_WAIT_TIME
        wait = WebDriverWait(self.driver, timeout)
        
        for selector in selectors:
            try:
                element = wait.until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                return element
            except TimeoutException:
                continue
        
        raise TimeoutException(f"요소를 찾을 수 없습니다: {selectors}")
    
    def _click_element_with_retry(
        self, 
        selectors: List[str], 
        timeout: int = None
    ):
        """여러 선택자를 시도하여 요소 클릭"""
        timeout = timeout or Config.DEFAULT_WAIT_TIME
        wait = WebDriverWait(self.driver, timeout)
        
        for selector in selectors:
            try:
                element = wait.until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                element.click()
                return True
            except (TimeoutException, ElementClickInterceptedException):
                continue
        
        return False
    
    def _dismiss_popups(self) -> None:
        """팝업 닫기 시도 (JavaScript 클릭 사용)"""
        popup_selectors = [
            self.SELECTORS["close_popup"],
            self.SELECTORS["close_popup_en"],
            self.SELECTORS["not_now_button"],
            self.SELECTORS["not_now_button_en"],
        ]
        
        for selector in popup_selectors:
            try:
                popup = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                # JavaScript로 클릭 (다른 요소에 의해 가려져도 클릭 가능)
                self.driver.execute_script("arguments[0].click();", popup)
                print("📌 팝업을 닫았습니다.")
                time.sleep(1)
            except TimeoutException:
                pass
            except Exception:
                pass
    
    def _dismiss_save_login_popup(self) -> None:
        """로그인 정보 저장 팝업에서 취소 클릭 (JavaScript 클릭 사용)"""
        print("📌 로그인 정보 저장 팝업 확인 중...")
        
        # 먼저 빠르게 텍스트로 버튼 찾기 시도
        try:
            # role="button"인 div 요소에서 텍스트로 찾기
            buttons = self.driver.find_elements(By.XPATH, "//div[@role='button']")
            for btn in buttons:
                try:
                    btn_text = btn.text.strip().lower()
                    if btn_text in ['취소', 'cancel', 'decline', '다음에', 'not now', '나중에', '정보 저장 안 함']:
                        self.driver.execute_script("arguments[0].click();", btn)
                        print(f"📌 로그인 정보 저장 팝업에서 '{btn.text}'를 클릭했습니다.")
                        time.sleep(1)
                        return
                except:
                    continue
        except Exception:
            pass
        
        # span 텍스트로 찾아서 부모 클릭
        try:
            spans = self.driver.find_elements(By.XPATH, "//span[contains(text(), '취소') or contains(text(), 'Cancel') or contains(text(), '나중에') or contains(text(), 'Not Now') or contains(text(), '정보 저장 안 함')]")
            for span in spans:
                try:
                    # span의 클릭 가능한 부모 요소 찾기
                    parent = span.find_element(By.XPATH, "./ancestor::div[@role='button']")
                    self.driver.execute_script("arguments[0].click();", parent)
                    print(f"📌 로그인 정보 저장 팝업에서 '{span.text}'를 클릭했습니다.")
                    time.sleep(1)
                    return
                except:
                    continue
        except Exception:
            pass
        
        # aria-label로 찾기 (짧은 타임아웃)
        save_login_selectors = [
            self.SELECTORS["save_login_cancel"],
            self.SELECTORS["save_login_cancel_en"],
            self.SELECTORS["save_login_decline"],
            self.SELECTORS["save_login_decline_en"],
            self.SELECTORS["save_login_not_now"],
        ]
        
        for selector in save_login_selectors:
            try:
                cancel_btn = WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                self.driver.execute_script("arguments[0].click();", cancel_btn)
                print("📌 로그인 정보 저장 팝업에서 '취소'를 클릭했습니다.")
                time.sleep(1)
                return
            except:
                continue
        
        print("📌 로그인 정보 저장 팝업을 찾지 못했거나 이미 처리되었습니다.")
    
    def login(self) -> bool:
        """
        Facebook 로그인
        
        Returns:
            로그인 성공 여부
        """
        try:
            print("🔑 로그인을 시작합니다...")
            
            # 로그인 페이지로 이동
            self.driver.get(Config.FACEBOOK_LOGIN_URL)
            time.sleep(2)
            
            # 쿠키 동의 팝업 처리
            self._dismiss_popups()
            
            # 이메일 입력
            email_input = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, self.SELECTORS["email_input"])
                )
            )
            email_input.clear()
            email_input.send_keys(self.email)
            print("📧 이메일 입력 완료")
            
            # 비밀번호 입력
            password_input = self.driver.find_element(
                By.XPATH, self.SELECTORS["password_input"]
            )
            password_input.clear()
            password_input.send_keys(self.password)
            print("🔒 비밀번호 입력 완료")
            
            # 로그인 버튼 클릭
            login_button = self.driver.find_element(
                By.XPATH, self.SELECTORS["login_button"]
            )
            login_button.click()
            print("🚀 로그인 버튼 클릭")
            
            # 로그인 완료 대기 (홈 페이지 로딩 확인)
            time.sleep(5)
            
            # 2단계 인증 확인
            if "checkpoint" in self.driver.current_url:
                print("⚠️  2단계 인증이 필요합니다.")
                print("   30초 동안 수동으로 인증을 완료해주세요...")
                time.sleep(30)
            
            # 로그인 성공 확인
            if "facebook.com" in self.driver.current_url and "login" not in self.driver.current_url:
                print("✅ 로그인 성공!")
                
                # 로그인 정보 저장 팝업 처리
                time.sleep(2)
                self._dismiss_save_login_popup()
                self._dismiss_popups()
                return True
            else:
                print("❌ 로그인에 실패했습니다.")
                return False
                
        except TimeoutException:
            print("❌ 로그인 페이지 로딩 시간 초과")
            return False
        except Exception as e:
            print(f"❌ 로그인 중 오류 발생: {e}")
            return False
    
    def create_post(
        self, 
        message: str, 
        media_paths: Optional[List[str]] = None
    ) -> bool:
        """
        게시물 작성
        
        Args:
            message: 게시할 텍스트
            media_paths: 업로드할 이미지/동영상 파일 경로 목록
            
        Returns:
            게시 성공 여부
        """
        try:
            print("📝 게시물 작성을 시작합니다...")
            
            # 홈 페이지로 이동
            self.driver.get(Config.FACEBOOK_HOME_URL)
            time.sleep(3)
            self._dismiss_popups()
            
            # "무슨 생각을 하고 계신가요?" 클릭
            post_box_clicked = self._click_element_with_retry([
                self.SELECTORS["whats_on_your_mind"],
                self.SELECTORS["whats_on_your_mind_en"],
            ])
            
            if not post_box_clicked:
                print("❌ 게시물 입력창을 찾을 수 없습니다.")
                return False
            
            time.sleep(2)
            
            # 미디어 파일 업로드
            if media_paths:
                self._upload_media(media_paths)
            
            # 텍스트 입력창 찾기
            text_input = self._find_element_with_retry([
                self.SELECTORS["post_box"],
            ])
            
            # 메시지 입력
            text_input.click()
            time.sleep(1)
            text_input.send_keys(message)
            print(f"✏️  메시지 입력 완료: {message[:50]}...")
            
            time.sleep(2)
            
            # 게시 버튼 클릭
            post_clicked = self._click_element_with_retry([
                self.SELECTORS["post_button"],
                self.SELECTORS["post_button_en"],
            ])
            
            if post_clicked:
                print("✅ 게시물이 업로드되었습니다!")
                time.sleep(3)
                return True
            else:
                print("❌ 게시 버튼을 찾을 수 없습니다.")
                return False
                
        except TimeoutException as e:
            print(f"❌ 시간 초과: {e}")
            return False
        except Exception as e:
            print(f"❌ 게시물 작성 중 오류: {e}")
            return False
    
    def _upload_media(self, media_paths: List[str]) -> bool:
        """
        미디어 파일 업로드
        
        Args:
            media_paths: 업로드할 파일 경로 목록
            
        Returns:
            업로드 성공 여부
        """
        try:
            # 사진/동영상 버튼 클릭
            self._click_element_with_retry([
                self.SELECTORS["photo_video_button"],
                self.SELECTORS["photo_video_button_en"],
            ])
            time.sleep(2)
            
            # 파일 입력 요소 찾기
            file_inputs = self.driver.find_elements(
                By.XPATH, self.SELECTORS["file_input"]
            )
            
            if not file_inputs:
                print("❌ 파일 업로드 입력창을 찾을 수 없습니다.")
                return False
            
            # 파일 경로를 절대 경로로 변환하여 입력
            for media_path in media_paths:
                abs_path = str(Path(media_path).resolve())
                
                if not Path(abs_path).exists():
                    print(f"⚠️  파일을 찾을 수 없습니다: {abs_path}")
                    continue
                
                file_inputs[0].send_keys(abs_path)
                print(f"📎 파일 업로드: {abs_path}")
                time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"❌ 미디어 업로드 중 오류: {e}")
            return False
    
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
    print("Facebook Selenium 자동화 봇 테스트")
    print("=" * 50)
    print("⚠️  주의: 이 스크립트는 테스트 계정으로만 실행하세요!")
    print()
    
    try:
        with FacebookSeleniumBot(headless=False) as bot:
            # 로그인
            if bot.login():
                # 게시물 작성 (테스트 시 주석 해제)
                # bot.create_post(
                #     "안녕하세요! Selenium 자동화 테스트입니다. 🤖",
                #     media_paths=["./uploads/test.jpg"]
                # )
                
                # 잠시 대기 후 종료
                print("테스트 완료. 5초 후 브라우저를 종료합니다...")
                time.sleep(5)
            else:
                print("로그인에 실패했습니다.")
                
    except Exception as e:
        print(f"오류 발생: {e}")


if __name__ == "__main__":
    main()
