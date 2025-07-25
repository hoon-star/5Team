# 📚 도서 리뷰 웹사이트 (Book Review Platform)

> 독서 문화를 위한 디지털 커뮤니티 플랫폼  
> Flask · Jinja2 · MariaDB · Cloudtype · Git

---

## 📌 프로젝트 개요

- **목표:** 독서 경험을 공유하고, 리뷰를 통해 독서 문화를 확산하는 웹 플랫폼 개발
- **특징:** 회원가입 후 책에 대한 리뷰 및 평점을 남기고, 다른 사용자들의 의견을 볼 수 있음
- **기술 스택:** Flask, Jinja2, MariaDB, Git, Cloudtype

---

## 👥 팀 구성

| 이름     | 역할                       |
|----------|----------------------------|
| 이재훈   | PM / 기획, 테스트, DevOps (Git, Cloudtype 배포)          |
| 이지영   | 백엔드 (Flask, MariaDB)    |
| 윤빈     | 프론트엔드 (Jinja2, HTML/CSS) |
| 고강민   | DB 설계 및 데이터 관리     |
| 조준아   |  |

---

## 🔧 주요 기능

### ✅ 핵심 기능
- 회원가입 / 로그인
- 도서 상세 조회 및 리뷰 작성
- 리뷰 평점 등록 및 리스트 출력

### ✅ 비기능 요구사항
- 유효성 검사 (중복 아이디 확인)
- 세션을 이용한 로그인 상태 유지
- Cloudtype을 통한 외부 배포

---

## 🧱 프로젝트 구조

```bash
bookReview/
├── app.py                  # Flask 메인 애플리케이션
├── db.py                   # DB 연결, 초기화 함수
├── requirements.txt        # 라이브러리 목록
├── Procfile                # 클라우드타입 실행 명령
├── static/
│   └── css/
│       └── style.css       # UI 스타일 시트
├── templates/
│   ├── base.html           # 공통 네비게이션 포함
│   ├── index.html          # 메인 페이지
│   ├── book_detail.html    # 도서 상세 페이지
│   ├── login.html          # 로그인 페이지
│   └── register.html       # 회원가입 페이지
