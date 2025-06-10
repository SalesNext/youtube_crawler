from pydantic import BaseModel
from typing import List, Optional

class Company(BaseModel):
    company_id: Optional[str] = None
    company_name: Optional[str] = None
    company_address: Optional[str] = None
    company_representative: Optional[str] = None
    company_address: Optional[str] = None
    company_phone_number: Optional[str] = None
    company_industry: Optional[str] = None
    company_hp_url: Optional[str] = None
    company_business_detail: Optional[str] = None
    