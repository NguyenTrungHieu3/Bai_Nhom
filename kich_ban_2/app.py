from flask import Flask, render_template, request, redirect, url_for, flash, session
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import hashlib

app = Flask(__name__)
app.secret_key = 'asdsasdadsasdas'

# Thiết lập SQLAlchemy
engine = create_engine('sqlite:///database.db', echo=False)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    role = Column(String(20), nullable=False, default='user')

class Admin(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    role = Column(String(20), nullable=False, default='admin')

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db_session = Session()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_admin():
    admin_username1 = 'admin3'
    admin_password1 = hash_password('admin123')
    admin1_exist = db_session.query(Admin).filter_by(username=admin_username1).first()
    if not admin1_exist:
        admin1 = Admin(username=admin_username1, password=admin_password1, role='admin')
        db_session.add(admin1)
        db_session.commit()
        print("Admin mặc định đã được tạo!")
    else:
        print("Admin đã tồn tại, không cần tạo thêm.")


# initialize_admin()


# Route chính
@app.route('/')
def home():
    if 'username' in session:
        user = db_session.query(User).filter_by(username=session['username']).first()
        if user:
            return render_template('home.html', username=user.username, role=user.role)
    return redirect(url_for('login'))


# Route đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db_session.query(User).filter_by(username=username).first()
        admin = db_session.query(Admin).filter_by(username=username).first()

        if user and user.password == hash_password(password):
            session['username'] = username
            session['role'] = user.role
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('home'))
        elif admin and admin.password == hash_password(password):
            session['username'] = username
            session['role'] = admin.role
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'error')

    return render_template('login.html')


# Route đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form.get('role', 'user')

        if password != confirm_password:
            flash('Mật khẩu không khớp!', 'error')
            return render_template('register.html')

        if db_session.query(User).filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại!', 'error')
            return render_template('register.html')

        new_user = User(username=username, password=hash_password(password), role=role)
        db_session.add(new_user)

        try:
            db_session.commit()
            flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
            return redirect(url_for('login'))
        except:
            db_session.rollback()
            flash('Có lỗi xảy ra, vui lòng thử lại!', 'error')

    return render_template('register.html')


# Route đăng xuất
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash('Đã đăng xuất!', 'info')
    return redirect(url_for('login'))


# Route dành cho quản trị viên
@app.route('/admin')
def admin_dashboard():
    if 'role' in session and session['role'] == 'admin':
        users = db_session.query(User).all()
        return render_template('dashboard.html', users=users, current_user=session.get('username'))
    flash('Bạn không có quyền truy cập!', 'error')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
