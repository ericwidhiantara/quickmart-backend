from fastapi import Depends

from core.exceptions.http import CustomHttpException
from core.logging import logger
from domain.dto import auth_dto
from domain.model import review_model
from domain.rest import review_rest
from repository import product_repo, review_repo, user_repo
from utils import helper


class ReviewService:
    def __init__(
        self,
        review_repo: review_repo.ReviewRepo = Depends(),
        product_repo: product_repo.ProductRepo = Depends(),
        user_repo: user_repo.UserRepo = Depends(),
    ) -> None:
        self.review_repo = review_repo
        self.product_repo = product_repo
        self.user_repo = user_repo

    def createReview(
        self,
        payload: review_rest.CreateReviewReq,
        current_user: auth_dto.CurrentUser,
    ) -> review_rest.ReviewResp:
        # product must exist
        product = self.product_repo.getById(id=payload.product_id)
        if not product:
            raise CustomHttpException(status_code=404, message="product not found")

        # one review per user per product
        existing = None
        try:
            existing = self.review_repo.get(user_id=current_user.id, product_id=payload.product_id)
        except Exception:
            pass
        if existing:
            raise CustomHttpException(status_code=400, message="already reviewed this product")

        time_now = helper.timeNow()
        review = review_model.ReviewModel(
            id=helper.generateUUID4(),
            created_at=time_now,
            updated_at=time_now,
            created_by=current_user.id,
            user_id=current_user.id,
            product_id=payload.product_id,
            rating=payload.rating,
            comment=payload.comment,
        )
        self.review_repo.create(review=review)
        return self._toResp(review=review, reviewer_name=current_user.fullname)

    def getProductReviews(
        self,
        product_id: str,
        query: review_rest.GetProductReviewsReq,
        current_user: auth_dto.CurrentUser,
    ) -> review_rest.ReviewSummaryResp:
        product = self.product_repo.getById(id=product_id)
        if not product:
            raise CustomHttpException(status_code=404, message="product not found")

        sort_order = -1 if query.sort_order == "desc" else 1
        reviews, total = self.review_repo.getList(
            product_id=product_id,
            rating=query.rating,
            sort_by=query.sort_by,
            sort_order=sort_order,
            page=query.page,
            limit=query.limit,
        )
        average = self.review_repo.getRatingAverage(product_id=product_id)

        review_resps = []
        for r in reviews:
            name = ""
            try:
                user = self.user_repo.getById(id=r.user_id)
                if user:
                    name = user.fullname
            except Exception as e:
                logger.warning(f"could not fetch reviewer: {e}")
            review_resps.append(self._toResp(review=r, reviewer_name=name))

        return review_rest.ReviewSummaryResp(
            average_rating=round(average, 1),
            total_reviews=total,
            reviews=review_resps,
        )

    def deleteReview(
        self,
        review_id: str,
        current_user: auth_dto.CurrentUser,
    ) -> None:
        review = self.review_repo.getById(id=review_id)
        if not review:
            raise CustomHttpException(status_code=404, message="review not found")
        if review.user_id != current_user.id:
            raise CustomHttpException(status_code=403, message="forbidden")
        self.review_repo.delete(id=review_id)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _toResp(self, review: review_model.ReviewModel, reviewer_name: str = "") -> review_rest.ReviewResp:
        return review_rest.ReviewResp(
            id=review.id,
            created_at=review.created_at,
            updated_at=review.updated_at,
            user_id=review.user_id,
            product_id=review.product_id,
            rating=review.rating,
            comment=review.comment,
            reviewer_name=reviewer_name,
        )
