"""
Facebook 자동 포스팅 - 공식 API 방식 (facebook-sdk)

이 모듈은 Facebook Graph API를 사용하여 페이지에 글, 사진, 영상을 업로드합니다.
"""

import facebook
import requests
from typing import Optional, Dict, Any
from pathlib import Path
from config import Config


class FacebookAPIClient:
    """Facebook 공식 API를 사용한 포스팅 클라이언트"""
    
    def __init__(self, access_token: Optional[str] = None, page_id: Optional[str] = None):
        """
        Facebook API 클라이언트 초기화
        
        Args:
            access_token: Facebook 페이지 액세스 토큰 (없으면 환경 변수에서 로드)
            page_id: 포스팅할 페이지 ID (없으면 환경 변수에서 로드)
        """
        self.access_token = access_token or Config.ACCESS_TOKEN
        self.page_id = page_id or Config.PAGE_ID
        self.graph: Optional[facebook.GraphAPI] = None
        
        self._validate_credentials()
        self._initialize_graph()
    
    def _validate_credentials(self) -> None:
        """인증 정보 유효성 검사"""
        if not self.access_token:
            raise ValueError("❌ Access Token이 설정되지 않았습니다.")
        if not self.page_id:
            raise ValueError("❌ Page ID가 설정되지 않았습니다.")
    
    def _initialize_graph(self) -> None:
        """Graph API 클라이언트 초기화"""
        try:
            self.graph = facebook.GraphAPI(
                access_token=self.access_token,
                version="3.1"
            )
            print("✅ Facebook API 연결 성공")
        except Exception as e:
            raise ConnectionError(f"❌ Facebook API 연결 실패: {e}")
    
    def post_text(self, message: str) -> Dict[str, Any]:
        """
        텍스트 게시물 업로드
        
        Args:
            message: 게시할 텍스트 내용
            
        Returns:
            API 응답 (post_id 포함)
        """
        if not message:
            raise ValueError("❌ 메시지 내용이 비어있습니다.")
        
        try:
            response = self.graph.put_object(
                parent_object=self.page_id,
                connection_name="feed",
                message=message
            )
            print(f"✅ 텍스트 게시물 업로드 성공! Post ID: {response.get('id')}")
            return response
        except facebook.GraphAPIError as e:
            print(f"❌ 텍스트 업로드 실패: {e.message}")
            raise
        except Exception as e:
            print(f"❌ 예기치 못한 오류: {e}")
            raise
    
    def post_image(
        self, 
        image_path: str, 
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        이미지 게시물 업로드
        
        Args:
            image_path: 업로드할 이미지 파일 경로
            message: 이미지와 함께 게시할 텍스트 (선택사항)
            
        Returns:
            API 응답 (post_id 포함)
        """
        image_file = Path(image_path)
        
        if not image_file.exists():
            raise FileNotFoundError(f"❌ 이미지 파일을 찾을 수 없습니다: {image_path}")
        
        if not image_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            raise ValueError(f"❌ 지원하지 않는 이미지 형식입니다: {image_file.suffix}")
        
        try:
            with open(image_path, 'rb') as image:
                response = self.graph.put_photo(
                    image=image,
                    message=message or "",
                    album_path=f"{self.page_id}/photos"
                )
            print(f"✅ 이미지 업로드 성공! Post ID: {response.get('post_id', response.get('id'))}")
            return response
        except facebook.GraphAPIError as e:
            print(f"❌ 이미지 업로드 실패: {e.message}")
            raise
        except Exception as e:
            print(f"❌ 예기치 못한 오류: {e}")
            raise
    
    def post_video(
        self, 
        video_path: str, 
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        비디오 게시물 업로드
        
        Args:
            video_path: 업로드할 비디오 파일 경로
            title: 비디오 제목 (선택사항)
            description: 비디오 설명 (선택사항)
            
        Returns:
            API 응답 (video_id 포함)
        """
        video_file = Path(video_path)
        
        if not video_file.exists():
            raise FileNotFoundError(f"❌ 비디오 파일을 찾을 수 없습니다: {video_path}")
        
        supported_formats = ['.mp4', '.mov', '.avi', '.wmv', '.flv', '.mkv', '.webm']
        if not video_file.suffix.lower() in supported_formats:
            raise ValueError(f"❌ 지원하지 않는 비디오 형식입니다: {video_file.suffix}")
        
        # 비디오 업로드는 별도의 엔드포인트 사용
        upload_url = f"https://graph-video.facebook.com/v3.1/{self.page_id}/videos"
        
        try:
            with open(video_path, 'rb') as video:
                files = {'source': video}
                data = {
                    'access_token': self.access_token,
                    'title': title or "",
                    'description': description or ""
                }
                
                response = requests.post(upload_url, files=files, data=data)
                response.raise_for_status()
                result = response.json()
                
            print(f"✅ 비디오 업로드 성공! Video ID: {result.get('id')}")
            return result
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response else {}
            error_message = error_data.get('error', {}).get('message', str(e))
            print(f"❌ 비디오 업로드 실패: {error_message}")
            raise
        except Exception as e:
            print(f"❌ 예기치 못한 오류: {e}")
            raise
    
    def post_link(
        self, 
        link: str, 
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        링크 게시물 업로드
        
        Args:
            link: 공유할 URL
            message: 링크와 함께 게시할 텍스트 (선택사항)
            
        Returns:
            API 응답 (post_id 포함)
        """
        if not link:
            raise ValueError("❌ 링크가 비어있습니다.")
        
        try:
            response = self.graph.put_object(
                parent_object=self.page_id,
                connection_name="feed",
                message=message or "",
                link=link
            )
            print(f"✅ 링크 게시물 업로드 성공! Post ID: {response.get('id')}")
            return response
        except facebook.GraphAPIError as e:
            print(f"❌ 링크 업로드 실패: {e.message}")
            raise
        except Exception as e:
            print(f"❌ 예기치 못한 오류: {e}")
            raise
    
    def get_page_info(self) -> Dict[str, Any]:
        """
        페이지 정보 조회
        
        Returns:
            페이지 정보 (이름, ID, 팔로워 수 등)
        """
        try:
            page_info = self.graph.get_object(
                id=self.page_id,
                fields="id,name,fan_count,followers_count"
            )
            print(f"📄 페이지 정보: {page_info.get('name')}")
            return page_info
        except facebook.GraphAPIError as e:
            print(f"❌ 페이지 정보 조회 실패: {e.message}")
            raise


def main():
    """테스트 실행"""
    print("=" * 50)
    print("Facebook 공식 API 포스팅 테스트")
    print("=" * 50)
    
    try:
        # 클라이언트 초기화
        client = FacebookAPIClient()
        
        # 페이지 정보 확인
        page_info = client.get_page_info()
        print(f"연결된 페이지: {page_info.get('name')}")
        
        # 테스트 포스팅 (실제 사용 시 주석 해제)
        # client.post_text("안녕하세요! 자동 포스팅 테스트입니다. 🎉")
        # client.post_image("./uploads/test.jpg", "이미지 테스트")
        # client.post_video("./uploads/test.mp4", "비디오 제목", "비디오 설명")
        
    except Exception as e:
        print(f"오류 발생: {e}")


if __name__ == "__main__":
    main()
