from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime
from domain.model import order_model


class CheckoutReq(BaseModel):
    """Create order from cart. Optionally specify cart_item_ids to checkout subset."""
    cart_item_ids: Optional[list[str]] = None  # None = all cart items


class OrderItemResp(BaseModel):
    id: str
    product_id: str
    product_variant_id: Optional[str] = None
    product_name: str
    quantity: int
    price: float
    discount_percentage: Optional[float] = None
    final_price: float


class OrderResp(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    status: str
    total_price: float
    localized_total_price: str
    items: list[OrderItemResp] = []


class GetOrderListReq(BaseModel):
    status: Optional[Literal["pending", "completed", "canceled"]] = None
    page: int = 1
    limit: int = 10


class CancelOrderRespData(BaseModel):
    id: str
    status: str
    updated_at: datetime
