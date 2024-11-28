from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    telephone: Optional[str]


class ExtendedInfo(BaseModel):
    organization: str
    region: Optional[str]
    contact_info: ContactInfo


class Item(BaseModel):
    description: str
    quantity: float
    unit_name: str


class BudgetInfo(BaseModel):
    currency: Optional[str] = None
    valueAddedTaxIncluded: Optional[bool] = None
    amount: Optional[float] = None


class Issue(BaseModel):
    type: str
    description: str


class Analysis(BaseModel):
    suspicious_level: str
    issues: Optional[List[Issue]] = []


class Tender(BaseModel):
    id: str = Field(..., alias="_id")  # Використовуємо _id як id
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
            datetime: lambda v: v.isoformat()  # Перетворення datetime в формат ISO
        }










