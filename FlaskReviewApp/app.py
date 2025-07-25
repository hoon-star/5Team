import os # 템플릿 로더 디버깅용으로 남겨둠
from flask import Flask, render_template, request, redirect, url_for, flash, session
# Flask-Login 관련 임포트 모두 제거
# from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
# werkzeug.security 관련 임포트 모두 제거
# from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
from pymysql import Error
# from datetime import datetime # datetime은 더 이상 필요 없으므로 제거

# db.py에서 직접 연결 함수 사용
from db import get_db_connection, init_db_tables

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key' # 세션 관리를 위해 여전히 필요

# --- User 모델 (Flask-Login 제거로 더 이상 필요 없음) ---
# Flask-Login을 사용하지 않으므로 UserMixin 상속은 제거
# 하지만 user_loader에서 사용자 객체를 반환하는 방식은 유지
class User: # UserMixin 상속 제거
    def __init__(self, id, username, password): # password_hash 대신 password
        self.id = id
        self.username = username
        self.password = password # 해싱되지 않은 비밀번호

    # Flask-Login의 UserMixin이 제공하던 메서드를 수동으로 구현 (간단 버전)
    def is_active(self): return True
    def is_authenticated(self): return 'user_id' in session # 세션에 user_id가 있으면 인증된 것으로 간주
    def is_anonymous(self): return False
    def get_id(self): return str(self.id) # user_id는 문자열로 반환해야 함

    @staticmethod
    def get(user_id):
        conn = None
        try:
            conn = get_db_connection(with_db=True)
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            if user_data:
                return User(user_data['id'], user_data['username'], user_data['password'])
            return None
        except Error as e:
            print(f"User.get DB Error: {e}")
            return None
        finally:
            if conn:
                conn.close()

# Flask-Login의 user_loader 대체 함수 (세션 기반)
def load_user(user_id):
    # 이 함수는 Flask-Login에서 사용되지만, Flask-Login을 제거했으므로 더 이상 직접 호출되지 않습니다.
    # 그러나 User 클래스 자체는 여전히 로그인 성공 시 사용자 정보 관리에 유용합니다.
    return User.get(user_id)


# Flask 앱 시작 시 데이터베이스 테이블 초기화
with app.app_context():
    init_db_tables()

# 템플릿 로더 디버깅용 (문제 해결되면 제거해도 됩니다)
print(f"DEBUG: Template folder path: {app.template_folder}")
print(f"DEBUG: Current working directory: {os.getcwd()}")


# --- 라우트 정의 ---

@app.route('/')
def index():
    conn = None
    books = []
    try:
        conn = get_db_connection(with_db=True)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books ORDER BY title ASC")
        books = cursor.fetchall()
        print(f"DEBUG: Number of books fetched: {len(books)}") 
    except Error as e:
        flash(f"책 목록을 불러오는 중 오류 발생: {e}", "error")
        print(f"Error fetching books: {e}")
    finally:
        if conn:
            conn.close()
    
    # 세션에서 사용자 정보 가져오기
    username = session.get('username')
    return render_template('index.html', books=books, username=username)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    conn = None
    book = None
    reviews = []
    try:
        conn = get_db_connection(with_db=True)
        cursor = conn.cursor()

        # 책 정보 가져오기
        cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        book = cursor.fetchone()

        if book:
            # 리뷰 정보 가져오기 (작성자 이름과 함께)
            cursor.execute("""
                SELECT r.id, r.content, r.rating, u.username
                FROM reviews r
                JOIN users u ON r.user_id = u.id
                WHERE r.book_id = %s
                ORDER BY r.id DESC 
            """, (book_id,))
            reviews = cursor.fetchall()
        else:
            flash("책을 찾을 수 없습니다.", "error")
            return redirect(url_for('index'))
            
    except Error as e:
        flash(f"책 상세 정보를 불러오는 중 오류 발생: {e}", "error")
        print(f"Error fetching book detail or reviews: {e}")
    finally:
        if conn:
            conn.close()
    
    # 세션에서 사용자 정보 가져오기
    logged_in = 'user_id' in session # 로그인 여부 확인
    username = session.get('username')
    return render_template('book_detail.html', book=book, reviews=reviews, logged_in=logged_in, username=username)

@app.route('/add_review/<int:book_id>', methods=['POST'])
def add_review(book_id):
    # 로그인 여부 수동 확인
    if 'user_id' not in session:
        flash("리뷰를 작성하려면 로그인해야 합니다.", "error")
        return redirect(url_for('login'))

    content = request.form.get('content')
    rating = request.form.get('rating')

    if not content:
        flash("리뷰 내용을 입력해주세요.", "warning")
        return redirect(url_for('book_detail', book_id=book_id))

    user_id = session['user_id'] # 세션에서 user_id 가져오기

    conn = None
    try:
        conn = get_db_connection(with_db=True)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reviews (book_id, user_id, content, rating) VALUES (%s, %s, %s, %s)",
            (book_id, user_id, content, rating)
        )
        conn.commit()
        flash("리뷰가 성공적으로 작성되었습니다.", "success")
    except Error as e:
        flash(f"리뷰 저장 중 오류 발생: {e}", "error")
        print(f"Error adding review: {e}")
    finally:
        if conn:
            conn.close()
            
    return redirect(url_for('book_detail', book_id=book_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    # 이미 로그인되어 있다면 리다이렉트
    if 'user_id' in session:
        flash("이미 로그인되어 있습니다.", "info")
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # email = request.form.get('email') # 이메일 제거

        if not username or not password:
            flash("사용자 이름과 비밀번호를 입력해주세요.", "warning")
            return render_template('register.html')
        
        conn = None
        try:
            conn = get_db_connection(with_db=True)
            cursor = conn.cursor()
            # INSERT 문에서 email 컬럼 제거
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                           (username, password))
            conn.commit()
            flash("회원가입이 성공적으로 완료되었습니다! 로그인해주세요.", "success")
            return redirect(url_for('login'))
        except Error as e:
            if e.args[0] == 1062: # MySQL Duplicate entry error code (username만 해당)
                flash("이미 존재하는 사용자 이름입니다.", "error")
            else:
                flash(f"회원가입 중 오류 발생: {e}", "error")
            print(f"Register DB Error: {e}")
            # return render_template('register.html', username=username, email=email) # email 제거
            return render_template('register.html', username=username)
        finally:
            if conn:
                conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # 이미 로그인되어 있다면 리다이렉트
    if 'user_id' in session:
        flash("이미 로그인되어 있습니다.", "info")
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = None
        try:
            conn = get_db_connection(with_db=True)
            cursor = conn.cursor()
            # 이메일 컬럼 제거에 맞춰 SELECT 문 변경
            cursor.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
            user_data = cursor.fetchone()

            if user_data and user_data['password'] == password: # 평문 비밀번호 비교
                session['user_id'] = user_data['id'] # 세션에 user_id 저장
                session['username'] = user_data['username'] # 세션에 username 저장
                flash(f"환영합니다, {user_data['username']}!", "success")
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
            else:
                flash("로그인에 실패했습니다. 사용자 이름 또는 비밀번호를 확인해주세요.", "error")
        except Error as e:
            flash(f"로그인 중 오류 발생: {e}", "error")
            print(f"Login DB Error: {e}")
        finally:
            if conn:
                conn.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() # 세션의 모든 정보 삭제
    flash("로그아웃 되었습니다.", "info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)