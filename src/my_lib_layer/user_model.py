import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator, constr, EmailStr, conint


class UserModel(BaseModel):
    id: Optional[int]
    # userName: constr(max_length=20, min_length=5, regex=r"^[a-zA-Z0-9_-]{4,20}$")
    name: constr(min_length=2, max_length=255)
    mothersName: constr(min_length=2, max_length=255)
    fathersName: constr(min_length=2, max_length=255)
    # employeeId: constr(min_length=2, max_length=255)
    address: constr(min_length=5, max_length=500)
    userType: constr(min_length=5, max_length=50)
    # isActive: constr(min_length=5, max_length=50)
    dob: str
    email: EmailStr
    password: str
    phoneNumber: str

    # @validator('userName', each_item=True)
    # def check_names_not_empty(cls, v):
    #     assert v != '', 'Empty strings are not allowed.'
    #     return v
    @validator('phoneNumber')
    def validate_phone_number(cls, phoneNumber):
        pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
        if not pattern.match(phoneNumber):
            raise ValueError('Invalid phone number')
        return phoneNumber

    @validator('password')
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in value):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in value):
            raise ValueError('Password must contain at least one lowercase letter')
        return value

    @validator('dob')
    def validate_dob(cls, dob):
        try:
            # Ensure the input string is in the expected format
            dob_obj = datetime.strptime(dob, '%Y-%m-%d')
            # Ensure the person is not born in the future
            if dob_obj > datetime.now():
                raise ValueError('Invalid date of birth')
        except ValueError:
            raise ValueError('Invalid date of birth')
        return dob


class UserEditModel(BaseModel):
    name: constr(min_length=2, max_length=255)
    mothersName: constr(min_length=2, max_length=255)
    fathersName: constr(min_length=2, max_length=255)
    address: constr(min_length=5, max_length=500)
    userType: constr(min_length=5, max_length=50)
    dob: str
    id: int

    @validator('dob')
    def validate_dob(cls, dob):
        try:
            # Ensure the input string is in the expected format
            dob_obj = datetime.strptime(dob, '%Y-%m-%d')
            # Ensure the person is not born in the future
            if dob_obj > datetime.now():
                raise ValueError('Invalid date of birth')
        except ValueError:
            raise ValueError('Invalid date of birth')
        return dob
