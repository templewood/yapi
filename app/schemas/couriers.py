from enum import Enum

from typing import List, Optional
from pydantic import BaseModel, PositiveInt


class CourierTypeEnum(str, Enum):
    foot = 'foot'
    bike = 'bike'
    car = 'car'

    @classmethod
    def max_weight(cls, type):
        weights = {
            cls.foot : 10,
            cls.bike : 15,
            cls.car : 50
        }
        return weights[type]


class CourierKindaItem(BaseModel):
    """ Weak courier item model for a preliminary validation """

    courier_id: int
    class Config:
        extra = 'allow'


class CourierItem(BaseModel):
    """ Strict courier item model for a final validation """

    courier_id: PositiveInt
    courier_type: CourierTypeEnum
    regions: List[PositiveInt]
    working_hours: List[str]
    class Config:
        extra = 'forbid'


class CouriersPostRequest(BaseModel):
    data: List[CourierKindaItem]
    class Config:
        extra = 'forbid'
