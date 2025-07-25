import pymysql
from pymysql import Error
# from datetime import datetime # datetime 모듈은 더 이상 필요 없으므로 제거
# from werkzeug.security import generate_password_hash # 비밀번호 해싱용 제거

# 데이터베이스 접속 정보 설정 (실제 환경에 맞게 수정!)
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'book_review_db', # 사용할 데이터베이스 이름
    'user': 'root', # MySQL/MariaDB 사용자 이름 (DB 생성 권한 있는 계정)
    'password': '1111', # MySQL/MariaDB 비밀번호 (DB 생성 권한 있는 계정)
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection(with_db=True):
    """
    데이터베이스 연결 객체를 반환합니다.
    with_db=False 시 특정 DB 지정 없이 MySQL 서버에만 연결합니다 (DB 생성용).
    """
    conn = None
    try:
        if with_db:
            conn = pymysql.connect(
                host=DB_CONFIG['host'],
                port=DB_CONFIG['port'],
                database=DB_CONFIG['database'], # 특정 데이터베이스에 연결
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                charset=DB_CONFIG['charset'],
                cursorclass=DB_CONFIG['cursorclass']
            )
        else: # 데이터베이스 생성 또는 관리용
            conn = pymysql.connect(
                host=DB_CONFIG['host'],
                port=DB_CONFIG['port'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                charset=DB_CONFIG['charset'],
                cursorclass=pymysql.cursors.DictCursor
            )
        return conn
    except Error as e:
        print(f"MariaDB 연결 중 오류 발생: {e}")
        raise # 연결 실패 시 예외 발생

def init_db_tables():
    """데이터베이스 및 모든 테이블을 초기화(생성)합니다."""
    # 1. 먼저 데이터베이스 자체를 생성 시도 (root 권한 필요)
    conn_no_db = None
    try:
        conn_no_db = get_db_connection(with_db=False) # 특정 DB 지정 없이 서버에 연결
        cursor_no_db = conn_no_db.cursor()
        
        # 데이터베이스 존재 여부 확인 후 생성
        cursor_no_db.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn_no_db.commit()
        print(f"데이터베이스 '{DB_CONFIG['database']}' 생성 완료 또는 이미 존재함.")
    except Exception as e:
        print(f"데이터베이스 '{DB_CONFIG['database']}' 생성 중 오류 발생 (권한 확인 필요): {e}")
        if conn_no_db: conn_no_db.close()
        return 
    finally:
        if conn_no_db: conn_no_db.close()

    # 2. 데이터베이스 연결 후 테이블 생성
    conn = None
    try:
        conn = get_db_connection(with_db=True) # 이제 특정 데이터베이스에 연결
        cursor = conn.cursor()

        # users 테이블 (email 컬럼 제거)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(50) NOT NULL
                -- email VARCHAR(100) UNIQUE -- 이 줄을 제거합니다.
            )
        ''')
        print("Table 'users' initialized or already exists.")

        # books 테이블 (기존과 동일)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                publisher VARCHAR(255),
                description TEXT,
                isbn VARCHAR(20) UNIQUE NOT NULL,
                image VARCHAR(255),
                pubdate VARCHAR(20)
            )
        ''')
        print("Table 'books' initialized or already exists.")

        # reviews 테이블 (기존과 동일)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                book_id INT NOT NULL,
                user_id INT NOT NULL,
                rating INT CHECK (rating >= 1 AND rating <= 5),
                content TEXT NOT NULL,
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        print("Table 'reviews' initialized or already exists.")

        conn.commit()

        # (선택 사항) 테스트 사용자 추가 (이메일 값 제거)
        try:
            cursor.execute("INSERT IGNORE INTO users (username, password) VALUES (%s, %s)",
                           ('testuser', 'testpassword')) # 이메일 값 제거
            conn.commit()
            print("Test user 'testuser' added (if not exists).")
        except Error as e:
            print(f"Test user insertion error (might already exist): {e}")

    except Exception as e:
        print(f"데이터베이스 테이블 초기화 중 오류 발생: {e}")
    finally:
        if conn:
            conn.close()

# --- 샘플 책 데이터를 직접 추가하는 함수 ---
def insert_sample_book_data():
    conn = None
    try:
        conn = get_db_connection(with_db=True)
        cursor = conn.cursor()

        sample_books = [
            {
                'title': '파이썬으로 배우는 웹 크롤링의 모든 것',
                'author': '윤인성',
                'publisher': '한빛미디어',
                'description': '웹 데이터를 수집하고 분석하는 파이썬 크롤링 기술을 쉽고 자세하게 설명하는 책입니다. 입문자도 따라 할 수 있도록 기초부터 실전까지 다룹니다.',
                'isbn': '9791162241699',
                'image': '/static/images/파이썬으로배우는.jpg',
                'pubdate': '20210310'
            },
            {
                'title': 'Do it! 점프 투 파이썬',
                'author': '박응용',
                'publisher': '이지스퍼블리싱',
                'description': '파이썬을 처음 시작하는 사람들을 위한 가장 기본적인 입문서입니다. 쉽고 재미있게 파이썬의 핵심을 배울 수 있습니다.',
                'isbn': '9791191069695',
                'image': '/static/images/점프투썬파이썬.jpg',
                'pubdate': '20200615'
            },
            {
                'title': '혼자 공부하는 파이썬',
                'author': '윤인성',
                'publisher': '한빛미디어',
                'description': '독학으로 프로그래밍을 시작하는 사람들을 위한 파이썬 입문서입니다. 친절한 설명과 다양한 예제로 파이썬 기초를 완벽하게 다질 수 있습니다.',
                'isbn': '9791162241880',
                'image': '/static/images/혼자공부.jpg',
                'pubdate': '20210201'
            },
            {
                'title': '데미안',
                'author': '헤르만 헤세',
                'publisher': '민음사',
                'description': '싱클레어라는 소년이 성장하면서 겪는 내면의 갈등과 자아 탐색 과정을 그린 소설입니다. 스승 피스토리우스를 만나면서 진정한 자아를 찾아갑니다.',
                'isbn': '9788937460292',
                'image': '/static/images/데미안.jpg',
                'pubdate': '20090810'
            },
            {
                'title': '어린 왕자',
                'author': '앙투안 드 생텍쥐페리',
                'publisher': '더클래식',
                'description': '사막에 불시착한 조종사가 만난 어린 왕자와의 이야기를 통해 인생의 소중한 가치와 진정한 사랑을 깨닫게 되는 감동적인 동화입니다.',
                'isbn': '9791157431281',
                'image': '/static/images/어린왕자.jpg',
                'pubdate': '20190101'
            }
        ]

        inserted_count = 0
        for book_data in sample_books:
            cursor.execute("SELECT id FROM books WHERE isbn = %s", (book_data['isbn'],))
            existing_book = cursor.fetchone()

            if not existing_book:
                sql = """
                INSERT INTO books (title, author, publisher, description, isbn, image, pubdate)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    book_data['title'],
                    book_data['author'],
                    book_data['publisher'],
                    book_data['description'],
                    book_data['isbn'],
                    book_data['image'],
                    book_data['pubdate']
                ))
                conn.commit()
                print(f"'{book_data['title']}' 책이 성공적으로 추가되었습니다.")
                inserted_count += 1
            else:
                print(f"'{book_data['title']}' (ISBN: {book_data['isbn']}) 책은 이미 존재합니다. 건너_ㅂ니다.")
        print(f"총 {inserted_count}권의 책이 새로 추가되었습니다.")

    except Error as e:
        print(f"샘플 책 데이터 저장 중 MySQL 오류 발생: {e}")
    except Exception as e:
        print(f"샘플 책 데이터 저장 중 일반 오류 발생: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    print("데이터베이스 및 테이블 초기화 시작...")
    init_db_tables()
    print("\n샘플 책 데이터 추가 시작...")
    insert_sample_book_data()
    print("\n데이터베이스 설정 및 초기 샘플 책 데이터 로드 완료.")