# name, nidNumber, mothersName, fathersName, presentAddress, permenentAddress, contactNumber, email, plotNumber, road, sector
from datetime import datetime

from pydantic import BaseModel, validator, constr, EmailStr, conint


class ConnectionModel(BaseModel):
    # userName: constr(max_length=20, min_length=5, regex=r"^[a-zA-Z0-9_-]{4,20}$")
    customerName: constr(min_length=2, max_length=255)
    customerNid: str
    customerPhone: str
    customerEmail: EmailStr
    password: str
    confirmPassword: str
    dob: str
    nid: str
    fathersName: constr(min_length=2, max_length=255)
    mothersName: constr(min_length=2, max_length=255)
    # employeeId: constr(min_length=2, max_length=255)
    address: constr(min_length=5, max_length=500)
    userType: constr(min_length=5, max_length=50)

    # isActive: constr(min_length=5, max_length=50)

    @validator('confirmPassword')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v
