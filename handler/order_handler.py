from fastapi import APIRouter, Depends

from core.dependencies import verifyToken, formOrJsonDependGenerator
from domain.dto import auth_dto
from domain.rest import generic_resp, order_rest
from service import order_service
from utils import request as req_utils

OrderRouter = APIRouter(
    prefix="/orders",
    tags=["Order"],
    dependencies=[Depends(verifyToken)],
)


@OrderRouter.post(
    "",
    description="Checkout — create order from cart items",
    response_model=generic_resp.RespData[order_rest.OrderResp],
    openapi_extra={
        "requestBody": req_utils.generateFormOrJsonOpenapiBody(order_rest.CheckoutReq)
    },
)
def checkout(
    payload=formOrJsonDependGenerator(order_rest.CheckoutReq),
    service: order_service.OrderService = Depends(),
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
):
    data = service.checkout(payload=payload, current_user=current_user)
    resp = generic_resp.RespData[order_rest.OrderResp](data=data)
    resp.meta.message = "Order placed successfully"
    return resp


@OrderRouter.get(
    "",
    description="Get current user's orders (paginated)",
    response_model=generic_resp.RespData[
        generic_resp.PaginatedData[order_rest.OrderResp]
    ],
)
def get_orders(
    query: order_rest.GetOrderListReq = Depends(),
    service: order_service.OrderService = Depends(),
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
):
    data, count = service.getOrders(query=query, current_user=current_user)
    paginated = generic_resp.PaginatedData[order_rest.OrderResp](
        total=count, page=query.page, limit=query.limit, data=data
    )
    return generic_resp.RespData[generic_resp.PaginatedData[order_rest.OrderResp]](data=paginated)


@OrderRouter.get(
    "/{order_id}",
    description="Get order detail",
    response_model=generic_resp.RespData[order_rest.OrderResp],
)
def get_order_detail(
    order_id: str,
    service: order_service.OrderService = Depends(),
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
):
    data = service.getOrderDetail(order_id=order_id, current_user=current_user)
    return generic_resp.RespData[order_rest.OrderResp](data=data)


@OrderRouter.patch(
    "/{order_id}/cancel",
    description="Cancel a pending order",
    response_model=generic_resp.RespData[order_rest.CancelOrderRespData],
)
def cancel_order(
    order_id: str,
    service: order_service.OrderService = Depends(),
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
):
    data = service.cancelOrder(order_id=order_id, current_user=current_user)
    resp = generic_resp.RespData[order_rest.CancelOrderRespData](data=data)
    resp.meta.message = "Order canceled"
    return resp
