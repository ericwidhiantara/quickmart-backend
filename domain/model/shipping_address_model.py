from .base_model import MyBaseModel, _MyBaseModel_Index
from datetime import datetime


class ShippingAddressModel(MyBaseModel):
    _coll_name = "shipping_addresses"
    _custom_indexes = [
        _MyBaseModel_Index(keys=[("user_id", 1)]),
        _MyBaseModel_Index(keys=[("created_at", -1)]),
        _MyBaseModel_Index(keys=[("is_default", 1)]),
    ]

    id: str = ""
    created_at: datetime
    updated_at: datetime
    created_by: str = ""
    updated_by: str = ""

    user_id: str
    label: str  # e.g. "Home", "Office"
    recipient_name: str
    phone: str
    address_line: str
    city: str
    province: str
    postal_code: str
    country: str = "Indonesia"
    is_default: bool = False
