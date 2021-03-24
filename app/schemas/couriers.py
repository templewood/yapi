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


class CourierUpdateRequest(BaseModel):
    """ Existing courier info model for a modification """

    courier_type: Optional[CourierTypeEnum] = None
    regions: Optional[List[PositiveInt]] = None
    working_hours: Optional[List[str]] = None
    class Config:
        extra = 'forbid'
