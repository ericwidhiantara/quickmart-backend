from fastapi import APIRouter, Depends

from core.dependencies import verifyToken
from domain.dto import auth_dto
from domain.rest import generic_resp, shipping_address_rest
from service import shipping_address_service

ShippingAddressRouter = APIRouter(
    tags=["Shipping Address"],
    dependencies=[Depends(verifyToken)],
)


@ShippingAddressRouter.post(
    "/shipping-addresses",
    description="Create a new shipping address",
    response_model=generic_resp.RespData[shipping_address_rest.ShippingAddressResp],
)
def create_address(
    payload: shipping_address_rest.CreateShippingAddressReq,
    service: shipping_address_service.ShippingAddressService = Depends(),
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
):
    data = service.createAddress(payload=payload, current_user=current_user)
    resp = generic_resp.RespData[shipping_address_rest.ShippingAddressResp](data=data)
    resp.meta.message = "Address created"
    return resp


@ShippingAddressRouter.get(
    "/shipping-addresses",
    description="Get my shipping addresses",
    response_model=generic_resp.RespData[list[shipping_address_rest.ShippingAddressResp]],
)
def get_my_addresses(
    service: shipping_address_service.ShippingAddressService = Depends(),
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
):
    data = service.getMyAddresses(current_user=current_user)
    return generic_resp.RespData[list[shipping_address_rest.ShippingAddressResp]](data=data)


@ShippingAddressRouter.get(
    "/shipping-addresses/{address_id}",
    description="Get shipping address by ID",
    response_model=generic_resp.RespData[shipping_address_rest.ShippingAddressResp],
)
def get_address(
    address_id: str,
    service: shipping_address_service.ShippingAddressService = Depends(),
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
):
    data = service.getAddressById(address_id=address_id, current_user=current_user)
    return generic_resp.RespData[shipping_address_rest.ShippingAddressResp](data=data)


@ShippingAddressRouter.put(
    "/shipping-addresses/{address_id}",
    description="Update shipping address",
    response_model=generic_resp.RespData[shipping_address_rest.ShippingAddressResp],
)
def update_address(
    address_id: str,
    payload: shipping_address_rest.UpdateShippingAddressReq,
    service: shipping_address_service.ShippingAddressService = Depends(),
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
):
    data = service.updateAddress(address_id=address_id, payload=payload, current_user=current_user)
    resp = generic_resp.RespData[shipping_address_rest.ShippingAddressResp](data=data)
    resp.meta.message = "Address updated"
    return resp


@ShippingAddressRouter.patch(
    "/shipping-addresses/{address_id}/set-default",
    description="Set address as default",
    response_model=generic_resp.RespData[shipping_address_rest.ShippingAddressResp],
)
def set_default_address(
    address_id: str,
    service: shipping_address_service.ShippingAddressService = Depends(),
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
):
    data = service.setDefault(address_id=address_id, current_user=current_user)
    resp = generic_resp.RespData[shipping_address_rest.ShippingAddressResp](data=data)
    resp.meta.message = "Default address updated"
    return resp


@ShippingAddressRouter.delete(
    "/shipping-addresses/{address_id}",
    description="Delete shipping address",
    response_model=generic_resp.RespData,
)
def delete_address(
    address_id: str,
    service: shipping_address_service.ShippingAddressService = Depends(),
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
):
    service.deleteAddress(address_id=address_id, current_user=current_user)
    resp = generic_resp.RespData()
    resp.meta.message = "Address deleted"
    return resp
