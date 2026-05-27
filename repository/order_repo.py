from typing import Optional, Literal, Union

from fastapi import Depends
from pymongo import ReturnDocument

from config.mongodb import MongodbClient
from core.logging import logger
from domain.model import order_model
from utils import helper


class OrderRepo:
    def __init__(self, mongo_db: MongodbClient = Depends()):
        self.order_coll = mongo_db.db[order_model.OrderModel.getCollName()]
        self.order_item_coll = mongo_db.db[order_model.OrderItemModel.getCollName()]

    # ── Orders ──────────────────────────────────────────────────────────────

    def create(self, order: order_model.OrderModel) -> order_model.OrderModel:
        self.order_coll.insert_one(order.model_dump())
        return order

    def getById(self, id: str) -> Union[order_model.OrderModel, None]:
        doc = self.order_coll.find_one({"id": id})
        return order_model.OrderModel(**doc) if doc else None

    def update(self, id: str, order: order_model.OrderModel) -> Union[order_model.OrderModel, None]:
        doc = self.order_coll.find_one_and_update(
            {"id": id},
            {"$set": order.model_dump(exclude={"id"})},
            return_document=ReturnDocument.AFTER,
        )
        return order_model.OrderModel(**doc) if doc else None

    def getList(
        self,
        user_id: str,
        status: Optional[Literal["pending", "completed", "canceled"]] = None,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[order_model.OrderModel], int]:
        match: dict = {"user_id": user_id}
        if status:
            match["status"] = status

        skip = helper.generateSkip(page=page, limit=limit)
        pipeline = [
            {"$match": match},
            {"$sort": {"created_at": -1}},
            {
                "$facet": {
                    "paginated_results": [{"$skip": skip}, {"$limit": limit}],
                    "total": [{"$count": "count"}],
                }
            },
        ]
        cursor = list(self.order_coll.aggregate(pipeline))
        orders = []
        count = 0
        try:
            orders = [order_model.OrderModel(**o) for o in cursor[0].get("paginated_results") or []]
            count = cursor[0]["total"][0]["count"]
        except Exception as e:
            logger.warning(f"order getList cursor empty: {e}")
        return orders, count

    # ── Order Items ──────────────────────────────────────────────────────────

    def createItem(self, item: order_model.OrderItemModel) -> order_model.OrderItemModel:
        self.order_item_coll.insert_one(item.model_dump())
        return item

    def getItemsByOrderId(self, order_id: str) -> list[order_model.OrderItemModel]:
        docs = self.order_item_coll.find({"order_id": order_id})
        return [order_model.OrderItemModel(**d) for d in docs]
