#!/usr/bin/env python3
"""
Facebook 자동 포스팅 - 메인 실행 스크립트

이 스크립트는 세 가지 방식 중 하나를 선택하여 Facebook에 자동으로 포스팅합니다:
1. 공식 API (facebook-sdk) - 권장
2. Selenium 브라우저 자동화
3. Playwright 브라우저 자동화
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, List

# 색상 출력을 위한 colorama
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    # colorama가 없으면 색상 없이 진행
    class Fore:
        RED = GREEN = YELLOW = CYAN = MAGENTA = RESET = ""
    class Style:
        BRIGHT = RESET_ALL = ""


def print_banner():
    """배너 출력"""
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   🔵 Facebook Auto Posting Tool                          ║
║                                                          ║
║   세 가지 방식으로 페이스북 자동 포스팅을 지원합니다      ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def print_menu():
    """메뉴 출력"""
    menu = f"""
{Fore.YELLOW}📋 포스팅 방식 선택:{Style.RESET_ALL}

  {Fore.GREEN}1.{Style.RESET_ALL} 공식 API 방식 (facebook-sdk) {Fore.GREEN}[권장]{Style.RESET_ALL}
     • 안정적이고 계정 차단 위험 없음
     • 개발자 등록 및 액세스 토큰 필요

  {Fore.YELLOW}2.{Style.RESET_ALL} Selenium 브라우저 자동화
     • 개발자 등록 불필요
     • 계정 차단 위험 있음 (테스트 계정 권장)

  {Fore.YELLOW}3.{Style.RESET_ALL} Playwright 브라우저 자동화
     • Selenium보다 빠르고 안정적
     • 계정 차단 위험 있음 (테스트 계정 권장)

  {Fore.RED}0.{Style.RESET_ALL} 종료

"""
    print(menu)


def get_post_content() -> tuple[str, Optional[List[str]]]:
    """게시물 내용 입력받기"""
    print(f"\n{Fore.CYAN}📝 게시물 내용을 입력하세요:{Style.RESET_ALL}")
    
    message = input("메시지: ").strip()
    if not message:
        message = "자동 포스팅 테스트입니다! 🎉"
    
    media_paths = []
    add_media = input("\n미디어 파일을 추가하시겠습니까? (y/N): ").strip().lower()
    
    if add_media == 'y':
        print("파일 경로를 입력하세요 (빈 줄 입력 시 종료):")
        while True:
            path = input("  파일 경로: ").strip()
            if not path:
                break
            if Path(path).exists():
                media_paths.append(path)
                print(f"  ✅ 추가됨: {path}")
            else:
                print(f"  ❌ 파일을 찾을 수 없습니다: {path}")
    
    return message, media_paths if media_paths else None


def run_api_mode(message: str, media_paths: Optional[List[str]] = None):
    """공식 API 방식 실행"""
    print(f"\n{Fore.GREEN}🚀 공식 API 방식으로 포스팅합니다...{Style.RESET_ALL}\n")
    
    try:
        from facebook_api_poster import FacebookAPIClient
        
        client = FacebookAPIClient()
        
        # 페이지 정보 확인
        page_info = client.get_page_info()
        print(f"📄 연결된 페이지: {page_info.get('name')}\n")
        
        # 미디어에 따라 포스팅 방식 결정
        if media_paths:
            # 첫 번째 파일 확인
            first_file = Path(media_paths[0])
            
            if first_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                client.post_image(media_paths[0], message)
            elif first_file.suffix.lower() in ['.mp4', '.mov', '.avi', '.wmv', '.flv']:
                client.post_video(media_paths[0], description=message)
            else:
                print(f"⚠️  지원하지 않는 파일 형식입니다. 텍스트만 포스팅합니다.")
                client.post_text(message)
        else:
            client.post_text(message)
            
    except ImportError as e:
        print(f"{Fore.RED}❌ 필요한 패키지가 설치되지 않았습니다: {e}{Style.RESET_ALL}")
        print("   pip install facebook-sdk python-dotenv 를 실행하세요.")
    except Exception as e:
        print(f"{Fore.RED}❌ 오류 발생: {e}{Style.RESET_ALL}")


def run_selenium_mode(message: str, media_paths: Optional[List[str]] = None):
    """Selenium 방식 실행"""
    print(f"\n{Fore.YELLOW}🤖 Selenium 방식으로 포스팅합니다...{Style.RESET_ALL}")
    print(f"{Fore.RED}⚠️  주의: 테스트 계정으로만 사용하세요!{Style.RESET_ALL}\n")
    
    try:
        from facebook_selenium_bot import FacebookSeleniumBot
        
        with FacebookSeleniumBot(headless=False) as bot:
            if bot.login():
                bot.create_post(message, media_paths)
            else:
                print(f"{Fore.RED}❌ 로그인에 실패했습니다.{Style.RESET_ALL}")
                
    except ImportError as e:
        print(f"{Fore.RED}❌ 필요한 패키지가 설치되지 않았습니다: {e}{Style.RESET_ALL}")
        print("   pip install selenium webdriver-manager python-dotenv 를 실행하세요.")
    except Exception as e:
        print(f"{Fore.RED}❌ 오류 발생: {e}{Style.RESET_ALL}")


def run_playwright_mode(message: str, media_paths: Optional[List[str]] = None):
    """Playwright 방식 실행"""
    print(f"\n{Fore.MAGENTA}🎭 Playwright 방식으로 포스팅합니다...{Style.RESET_ALL}")
    print(f"{Fore.RED}⚠️  주의: 테스트 계정으로만 사용하세요!{Style.RESET_ALL}\n")
    
    try:
        from facebook_playwright_bot import FacebookPlaywrightBot
        
        with FacebookPlaywrightBot(headless=False, slow_mo=100) as bot:
            if bot.login(manual_2fa_timeout=30):
                bot.create_post(message, media_paths)
            else:
                print(f"{Fore.RED}❌ 로그인에 실패했습니다.{Style.RESET_ALL}")
                
    except ImportError as e:
        print(f"{Fore.RED}❌ 필요한 패키지가 설치되지 않았습니다: {e}{Style.RESET_ALL}")
        print("   pip install playwright python-dotenv 를 실행하세요.")
        print("   playwright install chromium 도 실행해야 합니다.")
    except Exception as e:
        print(f"{Fore.RED}❌ 오류 발생: {e}{Style.RESET_ALL}")


def interactive_mode():
    """대화형 모드"""
    print_banner()
    
    while True:
        print_menu()
        choice = input("선택 (0-3): ").strip()
        
        if choice == "0":
            print(f"\n{Fore.CYAN}👋 프로그램을 종료합니다.{Style.RESET_ALL}\n")
            break
        elif choice in ["1", "2", "3"]:
            message, media_paths = get_post_content()
            
            if choice == "1":
                run_api_mode(message, media_paths)
            elif choice == "2":
                run_selenium_mode(message, media_paths)
            elif choice == "3":
                run_playwright_mode(message, media_paths)
            
            input(f"\n{Fore.CYAN}Enter를 눌러 계속...{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}잘못된 선택입니다. 다시 시도하세요.{Style.RESET_ALL}")


def cli_mode(args):
    """CLI 모드"""
    if args.mode == "api":
        run_api_mode(args.message, args.media)
    elif args.mode == "selenium":
        run_selenium_mode(args.message, args.media)
    elif args.mode == "playwright":
        run_playwright_mode(args.message, args.media)


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="Facebook 자동 포스팅 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 대화형 모드 실행
  python main.py

  # CLI 모드로 API 방식 사용
  python main.py --mode api --message "안녕하세요!"

  # 이미지와 함께 포스팅
  python main.py --mode api --message "사진 공유" --media ./photo.jpg

  # Selenium 방식 사용
  python main.py --mode selenium --message "테스트 포스팅"
        """
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["api", "selenium", "playwright"],
        help="포스팅 방식 선택 (api/selenium/playwright)"
    )
    
    parser.add_argument(
        "--message", "-msg",
        type=str,
        help="게시할 메시지"
    )
    
    parser.add_argument(
        "--media",
        type=str,
        nargs="+",
        help="업로드할 미디어 파일 경로"
    )
    
    args = parser.parse_args()
    
    # CLI 인자가 있으면 CLI 모드, 없으면 대화형 모드
    if args.mode and args.message:
        cli_mode(args)
    elif args.mode or args.message:
        print(f"{Fore.RED}❌ --mode와 --message 둘 다 지정해야 합니다.{Style.RESET_ALL}")
        parser.print_help()
        sys.exit(1)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
