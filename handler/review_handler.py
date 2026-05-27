from fastapi import APIRouter, Depends

from core.dependencies import verifyToken, formOrJsonDependGenerator
from domain.dto import auth_dto
from domain.rest import generic_resp, review_rest
from service import review_service
from utils import request as req_utils

ReviewRouter = APIRouter(
    tags=["Review"],
    dependencies=[Depends(verifyToken)],
)


@ReviewRouter.post(
    "/products/{product_id}/reviews",
    description="Create review for a product (one per user per product)",
    response_model=generic_resp.RespData[review_rest.ReviewResp],
    openapi_extra={
        "requestBody": req_utils.generateFormOrJsonOpenapiBody(review_rest.CreateReviewReq)
    },
)
def create_review(
    product_id: str,
    payload=formOrJsonDependGenerator(review_rest.CreateReviewReq),
    service: review_service.ReviewService = Depends(),
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
):
    # inject product_id from path into payload
    payload.product_id = product_id
    data = service.createReview(payload=payload, current_user=current_user)
    resp = generic_resp.RespData[review_rest.ReviewResp](data=data)
    resp.meta.message = "Review submitted"
    return resp


@ReviewRouter.get(
    "/products/{product_id}/reviews",
    description="Get reviews for a product with rating average",
    response_model=generic_resp.RespData[review_rest.ReviewSummaryResp],
)
def get_product_reviews(
    product_id: str,
    query: review_rest.GetProductReviewsReq = Depends(),
    service: review_service.ReviewService = Depends(),
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
):
    data = service.getProductReviews(
        product_id=product_id, query=query, current_user=current_user
    )
    return generic_resp.RespData[review_rest.ReviewSummaryResp](data=data)


@ReviewRouter.delete(
    "/reviews/{review_id}",
    description="Delete own review",
    response_model=generic_resp.RespData,
)
def delete_review(
    review_id: str,
    service: review_service.ReviewService = Depends(),
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
):
    service.deleteReview(review_id=review_id, current_user=current_user)
    resp = generic_resp.RespData()
    resp.meta.message = "Review deleted"
    return resp
