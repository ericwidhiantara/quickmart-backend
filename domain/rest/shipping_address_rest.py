from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreateShippingAddressReq(BaseModel):
    label: str
    recipient_name: str
    phone: str
    address_line: str
    city: str
    province: str
    postal_code: str
    country: str = "Indonesia"
    is_default: bool = False


class UpdateShippingAddressReq(BaseModel):
    label: Optional[str] = None
    recipient_name: Optional[str] = None
    phone: Optional[str] = None
    address_line: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    is_default: Optional[bool] = None


class ShippingAddressResp(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    user_id: str
    label: str
    recipient_name: str
    phone: str
    address_line: str
    city: str
    province: str
    postal_code: str
    country: str
    is_default: bool
