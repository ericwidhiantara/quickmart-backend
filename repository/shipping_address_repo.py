from typing import Union, Optional

from fastapi import Depends
from pymongo import ReturnDocument

from config.mongodb import MongodbClient
from domain.model import shipping_address_model
from utils import helper


class ShippingAddressRepo:
    def __init__(self, mongo_db: MongodbClient = Depends()):
        self.coll = mongo_db.db[shipping_address_model.ShippingAddressModel.getCollName()]

    def create(self, address: shipping_address_model.ShippingAddressModel):
        self.coll.insert_one(address.model_dump())

    def getById(self, id: str) -> Union[shipping_address_model.ShippingAddressModel, None]:
        doc = self.coll.find_one({"id": id})
        return shipping_address_model.ShippingAddressModel(**doc) if doc else None

    def getListByUser(self, user_id: str) -> list[shipping_address_model.ShippingAddressModel]:
        docs = self.coll.find({"user_id": user_id}).sort("created_at", -1)
        return [shipping_address_model.ShippingAddressModel(**d) for d in docs]

    def getDefaultByUser(self, user_id: str) -> Union[shipping_address_model.ShippingAddressModel, None]:
        doc = self.coll.find_one({"user_id": user_id, "is_default": True})
        return shipping_address_model.ShippingAddressModel(**doc) if doc else None

    def update(
        self, id: str, data: dict
    ) -> Union[shipping_address_model.ShippingAddressModel, None]:
        doc = self.coll.find_one_and_update(
            {"id": id},
            {"$set": data},
            return_document=ReturnDocument.AFTER,
        )
        return shipping_address_model.ShippingAddressModel(**doc) if doc else None

    def clearDefault(self, user_id: str):
        """Unset is_default for all addresses of a user."""
        self.coll.update_many(
            {"user_id": user_id, "is_default": True},
            {"$set": {"is_default": False}},
        )

    def delete(self, id: str) -> Union[shipping_address_model.ShippingAddressModel, None]:
        doc = self.coll.find_one_and_delete({"id": id})
        return shipping_address_model.ShippingAddressModel(**doc) if doc else None
