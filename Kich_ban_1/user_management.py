from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

Base = declarative_base()

# Định nghĩa bảng Role (quyền)
class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)  # Tên quyền: Quản trị viên, Người dùng, Người quản lý nội dung

    # Quan hệ với User
    users = relationship("User", back_populates="role")

# Định nghĩa bảng User (người dùng)
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)  # Mã hóa mật khẩu khi lưu
    email = Column(String(100), nullable=False, unique=True)
    role_id = Column(Integer, ForeignKey('roles.id'))  # Liên kết với Role

    # Quan hệ với Role
    role = relationship("Role", back_populates="users")


# Kết nối đến cơ sở dữ liệu
engine = create_engine('sqlite:///user_management.db', echo=True)

# Tạo bảng trong cơ sở dữ liệu
Base.metadata.create_all(engine)

# Tạo session để làm việc với cơ sở dữ liệu
Session = sessionmaker(bind=engine)
session = Session()

# Thêm dữ liệu mẫu
def seed_data():
    # Tạo quyền
    admin_role = Role(name="Quản trị viên")
    normal_user_role = Role(name="Người dùng bình thường")
    content_manager_role = Role(name="Người quản lý nội dung")
    session.add_all([admin_role, normal_user_role, content_manager_role])
    session.commit()

    # Tạo người dùng mẫu
    admin_user = User(username="admin", password="admin123", email="admin@example.com", role=admin_role)
    normal_user = User(username="user1", password="user123", email="user1@example.com", role=normal_user_role)
    content_manager_user = User(username="manager", password="manager123", email="manager@example.com", role=content_manager_role)
    session.add_all([admin_user, normal_user, content_manager_user])
    session.commit()

# Chạy hàm seed dữ liệu
seed_data()

# Hiển thị danh sách người dùng
users = session.query(User).all()
for user in users:
    print(f"Username: {user.username}, Email: {user.email}, Role: {user.role.name}")
