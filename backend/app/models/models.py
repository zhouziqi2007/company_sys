import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Enum, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """用户/员工表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(50), nullable=False)
    phone = Column(String(20), default="")
    role = Column(Enum("admin", "manager", "staff", name="user_role"), default="staff")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 关系
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    created_tasks = relationship("Task", back_populates="creator", foreign_keys="Task.creator_id")
    task_logs = relationship("TaskLog", back_populates="operator")


class Company(Base):
    """公司资料表"""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True, comment="公司名称")
    unified_code = Column(String(50), default="", comment="EIN/Tax ID")
    # 法人个人信息（外国人资料）
    first_name = Column(String(50), default="", comment="First Name")
    middle_name = Column(String(50), default="", comment="Middle Name")
    last_name = Column(String(50), default="", comment="Last Name")
    ssn = Column(String(20), default="", comment="SSN")
    itin = Column(String(20), default="", comment="ITIN")
    dob = Column(String(20), default="", comment="Date of Birth")
    gender = Column(Enum("male", "female", "other", name="gender_type"), default="male", comment="性别")
    email = Column(String(100), default="", comment="Email")
    phone = Column(String(30), default="", comment="Phone")
    # 法人地址
    address_line1 = Column(String(300), default="", comment="Address Line 1")
    address_line2 = Column(String(300), default="", comment="Address Line 2")
    city = Column(String(100), default="", comment="City")
    state = Column(String(50), default="", comment="State")
    zip_code = Column(String(20), default="", comment="Zip Code")
    country = Column(String(50), default="US", comment="Country")
    # 公司注册信息
    registered_address = Column(String(300), default="", comment="注册地址")
    business_scope = Column(Text, default="", comment="经营范围")
    registered_capital = Column(String(50), default="", comment="注册资本")
    state_of_formation = Column(String(50), default="", comment="State of Formation")
    # 营业执照状态
    license_status = Column(
        Enum("pending", "processing", "completed", "rejected", name="license_status"),
        default="pending", comment="营业执照状态"
    )
    # 银行公户状态
    bank_account_status = Column(
        Enum("pending", "processing", "completed", "rejected", name="bank_status"),
        default="pending", comment="银行公户状态"
    )
    remark = Column(Text, default="", comment="备注")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 关系
    tasks = relationship("Task", back_populates="company")
    documents = relationship("Document", back_populates="company")
    bank_accounts = relationship("BankAccount", back_populates="company", order_by="BankAccount.created_at.desc()")
    phone_numbers = relationship("PhoneNumber", back_populates="company")
    email_accounts = relationship("EmailAccount", back_populates="company")


class Task(Base):
    """任务表"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, comment="任务标题")
    task_type = Column(
        Enum("license_reg", "bank_account", "change", "cancel", "other", name="task_type"),
        default="license_reg", comment="任务类型: 执照注册/银行开户/变更/注销/其他"
    )
    description = Column(Text, default="", comment="任务描述")
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="负责人")
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="创建人")
    status = Column(
        Enum("pending", "in_progress", "submitted", "approved", "rejected", "completed", name="task_status"),
        default="pending", comment="任务状态"
    )
    priority = Column(Enum("low", "medium", "high", "urgent", name="task_priority"), default="medium")
    deadline = Column(DateTime, nullable=True, comment="截止日期")
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 关系
    company = relationship("Company", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks", foreign_keys=[assignee_id])
    creator = relationship("User", back_populates="created_tasks", foreign_keys=[creator_id])
    logs = relationship("TaskLog", back_populates="task", order_by="TaskLog.created_at.desc()")
    documents = relationship("Document", back_populates="task")


class TaskLog(Base):
    """任务操作日志"""
    __tablename__ = "task_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False, comment="操作类型")
    content = Column(Text, default="", comment="操作内容/备注")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    task = relationship("Task", back_populates="logs")
    operator = relationship("User", back_populates="task_logs")


class Document(Base):
    """文件/资料表"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False, comment="原始文件名")
    storage_key = Column(String(500), nullable=False, comment="云存储key")
    file_url = Column(String(500), default="", comment="文件访问URL")
    file_size = Column(Integer, default=0, comment="文件大小(bytes)")
    file_type = Column(String(50), default="", comment="文件MIME类型")
    category = Column(
        Enum("id_card", "license", "bank_doc", "contract", "other", name="doc_category"),
        default="other", comment="文件分类: 身份证/营业执照/银行资料/合同/其他"
    )
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=True)

    company = relationship("Company", back_populates="documents")
    task = relationship("Task", back_populates="documents")
    bank_account = relationship("BankAccount", back_populates="documents")


class BankAccount(Base):
    """银行资料表 - 与公司一对多"""
    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    # 银行标签/类型
    label = Column(String(50), default="", comment="标签: checking/savings/business等")
    bank_name = Column(String(200), nullable=False, comment="银行名称")
    # 核心账户信息
    routing_number = Column(String(30), default="", comment="Routing Number")
    account_number = Column(String(50), default="", comment="Account Number")
    account_type = Column(
        Enum("checking", "savings", "business_checking", "business_savings", "other", name="bank_account_type"),
        default="checking", comment="账户类型"
    )
    status = Column(
        Enum("pending", "active", "frozen", "closed", name="bank_acct_status"),
        default="pending", comment="账户状态"
    )
    # 在线银行登录信息
    login_url = Column(String(300), default="", comment="网银登录地址")
    login_username = Column(String(100), default="", comment="网银用户名")
    login_password = Column(String(255), default="", comment="网银密码")
    security_questions = Column(Text, default="", comment="安全问题及答案(JSON)")
    # 密钥与安全
    pin = Column(String(20), default="", comment="PIN码")
    security_key = Column(Text, default="", comment="密钥/Token")
    two_factor_method = Column(String(50), default="", comment="二次验证方式")
    two_factor_phone = Column(String(30), default="", comment="二次验证手机号")
    two_factor_email = Column(String(100), default="", comment="二次验证邮箱")
    # 联系信息
    bank_phone = Column(String(30), default="", comment="银行客服电话")
    bank_contact = Column(String(100), default="", comment="银行联系人")
    branch_address = Column(String(300), default="", comment="开户行地址")
    # 其他
    remark = Column(Text, default="", comment="备注")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 关系
    company = relationship("Company", back_populates="bank_accounts")
    documents = relationship("Document", back_populates="bank_account")
    phone_numbers = relationship("PhoneNumber", back_populates="bank_account")
    email_accounts = relationship("EmailAccount", back_populates="bank_account")


class PhoneNumber(Base):
    """电话号码库"""
    __tablename__ = "phone_numbers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String(30), unique=True, nullable=False, index=True, comment="电话号码")
    sms_api = Column(String(200), default="", comment="短信API")
    status = Column(
        Enum("available", "claimed", name="phone_status"),
        default="available", comment="状态: 可用/已领用"
    )
    claimed_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="领用人")
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, comment="关联公司")
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=True, comment="关联银行")
    bank_label = Column(String(100), default="", comment="银行标签")
    remark = Column(Text, default="", comment="备注")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    claimer = relationship("User", foreign_keys=[claimed_by])
    company = relationship("Company", back_populates="phone_numbers")
    bank_account = relationship("BankAccount", back_populates="phone_numbers")


class EmailAccount(Base):
    """邮箱库"""
    __tablename__ = "email_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(200), unique=True, nullable=False, index=True, comment="邮箱地址")
    password = Column(String(255), default="", comment="邮箱密码")
    status = Column(
        Enum("available", "claimed", name="email_status"),
        default="available", comment="状态: 可用/已领用"
    )
    claimed_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="领用人")
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, comment="关联公司")
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=True, comment="关联银行")
    bank_label = Column(String(100), default="", comment="银行标签")
    remark = Column(Text, default="", comment="备注")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    claimer = relationship("User", foreign_keys=[claimed_by])
    company = relationship("Company", back_populates="email_accounts")
    bank_account = relationship("BankAccount", back_populates="email_accounts")
