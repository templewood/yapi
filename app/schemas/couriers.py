from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, PositiveInt, validator
from utils.time import validate_hours_input


class CourierTypeEnum(str, Enum):
    foot = 'foot'
    bike = 'bike'
    car = 'car'

    @classmethod
    def max_weight(cls, type):
        weights = {
            cls.foot: 10,
            cls.bike: 15,
            cls.car: 50
        }
        return weights[type]

    @classmethod
    def get_coeff(cls, type):
        coeffs = {
            cls.foot: 2,
            cls.bike: 5,
            cls.car: 9
        }
        return coeffs[type]


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

    @validator('working_hours')
    def check_working_hours(cls, v):
        if v and not validate_hours_input(v):
            raise ValueError('wrong date format')
        return v

    class Config:
        extra = 'forbid'
