from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ========== Auth ==========
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ========== User ==========
class UserCreate(BaseModel):
    username: str
    password: str
    real_name: str
    phone: Optional[str] = ""
    role: Optional[str] = "staff"


class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    username: str
    real_name: str
    phone: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


# ========== Company ==========
class CompanyCreate(BaseModel):
    name: str
    unified_code: Optional[str] = ""
    first_name: Optional[str] = ""
    middle_name: Optional[str] = ""
    last_name: Optional[str] = ""
    ssn: Optional[str] = ""
    itin: Optional[str] = ""
    dob: Optional[str] = ""
    gender: Optional[str] = "male"
    email: Optional[str] = ""
    phone: Optional[str] = ""
    address_line1: Optional[str] = ""
    address_line2: Optional[str] = ""
    city: Optional[str] = ""
    state: Optional[str] = ""
    zip_code: Optional[str] = ""
    country: Optional[str] = "US"
    registered_address: Optional[str] = ""
    business_scope: Optional[str] = ""
    registered_capital: Optional[str] = ""
    state_of_formation: Optional[str] = ""
    remark: Optional[str] = ""


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    unified_code: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    ssn: Optional[str] = None
    itin: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    registered_address: Optional[str] = None
    business_scope: Optional[str] = None
    registered_capital: Optional[str] = None
    state_of_formation: Optional[str] = None
    license_status: Optional[str] = None
    bank_account_status: Optional[str] = None
    remark: Optional[str] = None


class CompanyOut(BaseModel):
    id: int
    name: str
    unified_code: str
    first_name: str
    middle_name: str
    last_name: str
    ssn: str
    itin: str
    dob: str
    gender: str
    email: str
    phone: str
    address_line1: str
    address_line2: str
    city: str
    state: str
    zip_code: str
    country: str
    registered_address: str
    business_scope: str
    registered_capital: str
    state_of_formation: str
    license_status: str
    bank_account_status: str
    remark: str
    created_at: datetime

    class Config:
        from_attributes = True


# ========== Task ==========
class TaskCreate(BaseModel):
    title: str
    task_type: Optional[str] = "license_reg"
    description: Optional[str] = ""
    company_id: int
    assignee_id: Optional[int] = None
    priority: Optional[str] = "medium"
    deadline: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    deadline: Optional[datetime] = None


class TaskLogOut(BaseModel):
    id: int
    action: str
    content: str
    operator_id: int
    operator_name: Optional[str] = ""
    created_at: datetime

    class Config:
        from_attributes = True


class TaskOut(BaseModel):
    id: int
    title: str
    task_type: str
    description: str
    company_id: int
    company_name: Optional[str] = ""
    assignee_id: Optional[int] = None
    assignee_name: Optional[str] = ""
    creator_id: int
    creator_name: Optional[str] = ""
    status: str
    priority: str
    deadline: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ========== Document ==========
class DocumentOut(BaseModel):
    id: int
    filename: str
    file_url: str
    file_size: int
    file_type: str
    category: str
    company_id: Optional[int] = None
    task_id: Optional[int] = None
    bank_account_id: Optional[int] = None
    uploaded_by: int
    created_at: datetime

    class Config:
        from_attributes = True


# ========== BankAccount ==========
class BankAccountCreate(BaseModel):
    company_id: int
    label: Optional[str] = ""
    bank_name: str
    routing_number: Optional[str] = ""
    account_number: Optional[str] = ""
    account_type: Optional[str] = "checking"
    status: Optional[str] = "pending"
    login_url: Optional[str] = ""
    login_username: Optional[str] = ""
    login_password: Optional[str] = ""
    security_questions: Optional[str] = ""
    pin: Optional[str] = ""
    security_key: Optional[str] = ""
    two_factor_method: Optional[str] = ""
    two_factor_phone: Optional[str] = ""
    two_factor_email: Optional[str] = ""
    bank_phone: Optional[str] = ""
    bank_contact: Optional[str] = ""
    branch_address: Optional[str] = ""
    remark: Optional[str] = ""


class BankAccountUpdate(BaseModel):
    label: Optional[str] = None
    bank_name: Optional[str] = None
    routing_number: Optional[str] = None
    account_number: Optional[str] = None
    account_type: Optional[str] = None
    status: Optional[str] = None
    login_url: Optional[str] = None
    login_username: Optional[str] = None
    login_password: Optional[str] = None
    security_questions: Optional[str] = None
    pin: Optional[str] = None
    security_key: Optional[str] = None
    two_factor_method: Optional[str] = None
    two_factor_phone: Optional[str] = None
    two_factor_email: Optional[str] = None
    bank_phone: Optional[str] = None
    bank_contact: Optional[str] = None
    branch_address: Optional[str] = None
    remark: Optional[str] = None


class BankAccountOut(BaseModel):
    id: int
    company_id: int
    label: str
    bank_name: str
    routing_number: str
    account_number: str
    account_type: str
    status: str
    login_url: str
    login_username: str
    login_password: str
    security_questions: str
    pin: str
    security_key: str
    two_factor_method: str
    two_factor_phone: str
    two_factor_email: str
    bank_phone: str
    bank_contact: str
    branch_address: str
    remark: str
    created_at: datetime

    class Config:
        from_attributes = True


# ========== Common ==========
class PageResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int


# ========== PhoneNumber ==========
class PhoneNumberCreate(BaseModel):
    phone_number: str
    sms_api: Optional[str] = ""
    remark: Optional[str] = ""


class PhoneNumberBatchCreate(BaseModel):
    phones: List[str]
    sms_api: Optional[str] = ""


class PhoneNumberClaim(BaseModel):
    company_id: int
    bank_account_id: Optional[int] = None
    bank_label: str


class PhoneNumberOut(BaseModel):
    id: int
    phone_number: str
    sms_api: str
    status: str
    claimed_by: Optional[int] = None
    claimer_name: Optional[str] = ""
    company_id: Optional[int] = None
    company_name: Optional[str] = ""
    bank_account_id: Optional[int] = None
    bank_label: str
    remark: str
    created_at: datetime

    class Config:
        from_attributes = True


class PhoneNumberRelease(BaseModel):
    pass


# ========== EmailAccount ==========
class EmailAccountCreate(BaseModel):
    email: str
    password: Optional[str] = ""
    remark: Optional[str] = ""


class EmailAccountBatchCreate(BaseModel):
    emails: List[dict]  # [{email, password}]


class EmailAccountClaim(BaseModel):
    company_id: int
    bank_account_id: Optional[int] = None
    bank_label: str


class EmailAccountOut(BaseModel):
    id: int
    email: str
    password: str
    status: str
    claimed_by: Optional[int] = None
    claimer_name: Optional[str] = ""
    company_id: Optional[int] = None
    company_name: Optional[str] = ""
    bank_account_id: Optional[int] = None
    bank_label: str
    remark: str
    created_at: datetime

    class Config:
        from_attributes = True


class EmailAccountRelease(BaseModel):
    pass
