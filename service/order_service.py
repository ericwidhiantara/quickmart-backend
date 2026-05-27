from fastapi import Depends

from core.exceptions.http import CustomHttpException
from core.logging import logger
from domain.dto import auth_dto
from domain.model import order_model
from domain.rest import order_rest
from repository import cart_repo, order_repo, product_repo
from utils import helper


class OrderService:
    def __init__(
        self,
        order_repo: order_repo.OrderRepo = Depends(),
        cart_repo: cart_repo.CartRepo = Depends(),
        product_repo: product_repo.ProductRepo = Depends(),
    ) -> None:
        self.order_repo = order_repo
        self.cart_repo = cart_repo
        self.product_repo = product_repo

    def checkout(
        self,
        payload: order_rest.CheckoutReq,
        current_user: auth_dto.CurrentUser,
    ) -> order_rest.OrderResp:
        time_now = helper.timeNow()

        # get cart
        cart = self.cart_repo.getByUserId(user_id=current_user.id)
        if not cart:
            raise CustomHttpException(status_code=400, message="cart is empty")

        # get cart items (subset or all)
        all_items = self.cart_repo.getCartItemsByCartId(cart_id=cart.id)
        if not all_items:
            raise CustomHttpException(status_code=400, message="cart is empty")

        if payload.cart_item_ids:
            items = [i for i in all_items if i.id in payload.cart_item_ids]
            if not items:
                raise CustomHttpException(status_code=400, message="no matching cart items found")
        else:
            items = all_items

        # build order items + calculate total
        order_id = helper.generateUUID4()
        order_items: list[order_model.OrderItemModel] = []
        total_price: float = 0.0

        for cart_item in items:
            product = self.product_repo.getById(id=cart_item.product_id)
            if not product:
                logger.warning(f"product {cart_item.product_id} not found, skipping")
                continue

            variant = self.product_repo.getProductVariant(id=cart_item.product_variant_id)
            if not variant:
                logger.warning(f"variant {cart_item.product_variant_id} not found, skipping")
                continue

            item = order_model.OrderItemModel(
                id=helper.generateUUID4(),
                created_at=time_now,
                updated_at=time_now,
                created_by=current_user.id,
                order_id=order_id,
                product_id=cart_item.product_id,
                product_variant_id=cart_item.product_variant_id,
                price=variant.price,
                quantity=cart_item.quantity,
                discount_precentage=variant.discount_percentage,
            )
            order_items.append(item)
            total_price += item.calculate_final_price()

        if not order_items:
            raise CustomHttpException(status_code=400, message="no valid items to checkout")

        # create order
        order = order_model.OrderModel(
            id=order_id,
            created_at=time_now,
            updated_at=time_now,
            created_by=current_user.id,
            user_id=current_user.id,
            total_price=total_price,
            status="pending",
        )
        self.order_repo.create(order=order)

        # persist order items
        for oi in order_items:
            self.order_repo.createItem(item=oi)

        # remove checked-out cart items
        for cart_item in items:
            self.cart_repo.deleteCartItem(id=cart_item.id)

        return self._buildOrderResp(order=order, items=order_items, current_user=current_user)

    def getOrders(
        self,
        query: order_rest.GetOrderListReq,
        current_user: auth_dto.CurrentUser,
    ) -> tuple[list[order_rest.OrderResp], int]:
        orders, count = self.order_repo.getList(
            user_id=current_user.id,
            status=query.status,
            page=query.page,
            limit=query.limit,
        )
        resp = []
        for order in orders:
            items = self.order_repo.getItemsByOrderId(order_id=order.id)
            resp.append(self._buildOrderResp(order=order, items=items, current_user=current_user))
        return resp, count

    def getOrderDetail(
        self,
        order_id: str,
        current_user: auth_dto.CurrentUser,
    ) -> order_rest.OrderResp:
        order = self.order_repo.getById(id=order_id)
        if not order:
            raise CustomHttpException(status_code=404, message="order not found")
        if order.user_id != current_user.id:
            raise CustomHttpException(status_code=403, message="forbidden")

        items = self.order_repo.getItemsByOrderId(order_id=order.id)
        return self._buildOrderResp(order=order, items=items, current_user=current_user)

    def cancelOrder(
        self,
        order_id: str,
        current_user: auth_dto.CurrentUser,
    ) -> order_rest.CancelOrderRespData:
        order = self.order_repo.getById(id=order_id)
        if not order:
            raise CustomHttpException(status_code=404, message="order not found")
        if order.user_id != current_user.id:
            raise CustomHttpException(status_code=403, message="forbidden")
        if order.status != "pending":
            raise CustomHttpException(
                status_code=400,
                message=f"cannot cancel order with status '{order.status}'"
            )

        order.status = "canceled"
        order.updated_at = helper.timeNow()
        self.order_repo.update(id=order.id, order=order)

        return order_rest.CancelOrderRespData(
            id=order.id,
            status=order.status,
            updated_at=order.updated_at,
        )

    # ── Internal ─────────────────────────────────────────────────────────────

    def _buildOrderResp(
        self,
        order: order_model.OrderModel,
        items: list[order_model.OrderItemModel],
        current_user: auth_dto.CurrentUser,
    ) -> order_rest.OrderResp:
        item_resps: list[order_rest.OrderItemResp] = []
        for oi in items:
            product = self.product_repo.getById(id=oi.product_id)
            product_name = product.name if product else ""
            item_resps.append(
                order_rest.OrderItemResp(
                    id=oi.id,
                    product_id=oi.product_id,
                    product_variant_id=oi.product_variant_id,
                    product_name=product_name,
                    quantity=oi.quantity,
                    price=oi.price,
                    discount_percentage=oi.discount_precentage,
                    final_price=oi.calculate_final_price(),
                )
            )

        return order_rest.OrderResp(
            id=order.id,
            created_at=order.created_at,
            updated_at=order.updated_at,
            status=order.status,
            total_price=order.total_price,
            localized_total_price=helper.localizePrice(
                price=order.total_price,
                currency_code=current_user.currency,
                language_code=current_user.language,
            ),
            items=item_resps,
        )
