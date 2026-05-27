from pydantic import BaseModel, field_validator
from typing import Optional, Literal
from datetime import datetime


class CreateReviewReq(BaseModel):
    product_id: str
    rating: int
    comment: Optional[str] = None

    @field_validator("rating", mode="before")
    def rating_range(cls, v):
        if not (1 <= int(v) <= 5):
            raise ValueError("rating must be 1–5")
        return v


class ReviewResp(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    user_id: str
    product_id: str
    rating: int
    comment: Optional[str] = None
    reviewer_name: str = ""


class GetProductReviewsReq(BaseModel):
    rating: Optional[int] = None
    sort_by: Literal["created_at", "rating"] = "created_at"
    sort_order: Literal["asc", "desc"] = "desc"
    page: int = 1
    limit: int = 10


class ReviewSummaryResp(BaseModel):
    average_rating: float
    total_reviews: int
    reviews: list[ReviewResp] = []
