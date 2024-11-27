from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr
from typing_extensions import Annotated, Optional, List
"""
class ContactInfo(BaseModel):
    name: str
    email: EmailStr
    telephone: str


class ExtendedInfo(BaseModel):
    organization: str
    region: str
    contact_info: ContactInfo


class Item(BaseModel):
    description: str
    quantity: float
    unit_name: str


class BudgetInfo(BaseModel):
    currency: str
    valueAddedTaxIncluded: bool
    amount: float


class Issue(BaseModel):
    type: str
    description: str


class Analysis(BaseModel):
    suspicious_level: str
    issues: Optional[List[Issue]] = Field(default_factory=list)


class Tender(BaseModel):
    id: str = Field(..., alias="_id")
    tender_id: str
    title: str
    creation_date: datetime
    extended_info: ExtendedInfo
    items: List[Item]
    deadline: datetime
    budget_info: BudgetInfo
    analysis: Analysis

    class Config:
        json_encoders = {
            ObjectId: str
        }

"""



class ContactInfo(BaseModel):
    name: str
    email: EmailStr
    telephone: str


class ExtendedInfo(BaseModel):
    organization: str
    region: str
    contact_info: ContactInfo


class Item(BaseModel):
    description: str
    quantity: float
    unit_name: str


class BudgetInfo(BaseModel):
    currency: str
    valueAddedTaxIncluded: bool
    amount: float


class Issue(BaseModel):
    type: str
    description: str


class Analysis(BaseModel):
    suspicious_level: str
    issues: Optional[List[Issue]] = Field(default_factory=list)


class Tender(BaseModel):
    id: str = Field(..., alias="_id")  # Використовуємо id як рядок
    tender_id: str
    title: str
    creation_date: datetime
    deadline: datetime
    extended_info: ExtendedInfo
    items: List[Item]
    budget_info: BudgetInfo
    analysis: Analysis

    class Config:

        json_encoders = {
            datetime: lambda v: v.isoformat()  # Преобразование datetime в строку ISO
        }









