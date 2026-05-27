from fastapi import Depends

from core.exceptions.http import CustomHttpException
from domain.dto import auth_dto
from domain.model import shipping_address_model
from domain.rest import shipping_address_rest
from repository import shipping_address_repo
from utils import helper


class ShippingAddressService:
    def __init__(
        self,
        address_repo: shipping_address_repo.ShippingAddressRepo = Depends(),
    ) -> None:
        self.address_repo = address_repo

    def createAddress(
        self,
        payload: shipping_address_rest.CreateShippingAddressReq,
        current_user: auth_dto.CurrentUser,
    ) -> shipping_address_rest.ShippingAddressResp:
        time_now = helper.timeNow()

        # If new address is default, clear existing defaults first
        if payload.is_default:
            self.address_repo.clearDefault(user_id=current_user.id)

        address = shipping_address_model.ShippingAddressModel(
            id=helper.generateUUID4(),
            created_at=time_now,
            updated_at=time_now,
            created_by=current_user.id,
            user_id=current_user.id,
            label=payload.label,
            recipient_name=payload.recipient_name,
            phone=payload.phone,
            address_line=payload.address_line,
            city=payload.city,
            province=payload.province,
            postal_code=payload.postal_code,
            country=payload.country,
            is_default=payload.is_default,
        )
        self.address_repo.create(address=address)
        return self._toResp(address)

    def getMyAddresses(
        self,
        current_user: auth_dto.CurrentUser,
    ) -> list[shipping_address_rest.ShippingAddressResp]:
        addresses = self.address_repo.getListByUser(user_id=current_user.id)
        return [self._toResp(a) for a in addresses]

    def getAddressById(
        self,
        address_id: str,
        current_user: auth_dto.CurrentUser,
    ) -> shipping_address_rest.ShippingAddressResp:
        address = self.address_repo.getById(id=address_id)
        if not address:
            raise CustomHttpException(status_code=404, message="address not found")
        if address.user_id != current_user.id:
            raise CustomHttpException(status_code=403, message="forbidden")
        return self._toResp(address)

    def updateAddress(
        self,
        address_id: str,
        payload: shipping_address_rest.UpdateShippingAddressReq,
        current_user: auth_dto.CurrentUser,
    ) -> shipping_address_rest.ShippingAddressResp:
        address = self.address_repo.getById(id=address_id)
        if not address:
            raise CustomHttpException(status_code=404, message="address not found")
        if address.user_id != current_user.id:
            raise CustomHttpException(status_code=403, message="forbidden")

        data = payload.model_dump(exclude_none=True)
        data["updated_at"] = helper.timeNow()
        data["updated_by"] = current_user.id

        # If setting as default, clear others first
        if payload.is_default:
            self.address_repo.clearDefault(user_id=current_user.id)

        updated = self.address_repo.update(id=address_id, data=data)
        return self._toResp(updated)

    def deleteAddress(
        self,
        address_id: str,
        current_user: auth_dto.CurrentUser,
    ) -> None:
        address = self.address_repo.getById(id=address_id)
        if not address:
            raise CustomHttpException(status_code=404, message="address not found")
        if address.user_id != current_user.id:
            raise CustomHttpException(status_code=403, message="forbidden")
        self.address_repo.delete(id=address_id)

    def setDefault(
        self,
        address_id: str,
        current_user: auth_dto.CurrentUser,
    ) -> shipping_address_rest.ShippingAddressResp:
        address = self.address_repo.getById(id=address_id)
        if not address:
            raise CustomHttpException(status_code=404, message="address not found")
        if address.user_id != current_user.id:
            raise CustomHttpException(status_code=403, message="forbidden")

        self.address_repo.clearDefault(user_id=current_user.id)
        updated = self.address_repo.update(
            id=address_id,
            data={"is_default": True, "updated_at": helper.timeNow(), "updated_by": current_user.id},
        )
        return self._toResp(updated)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _toResp(self, address: shipping_address_model.ShippingAddressModel) -> shipping_address_rest.ShippingAddressResp:
        return shipping_address_rest.ShippingAddressResp(
            id=address.id,
            created_at=address.created_at,
            updated_at=address.updated_at,
            user_id=address.user_id,
            label=address.label,
            recipient_name=address.recipient_name,
            phone=address.phone,
            address_line=address.address_line,
            city=address.city,
            province=address.province,
            postal_code=address.postal_code,
            country=address.country,
            is_default=address.is_default,
        )
