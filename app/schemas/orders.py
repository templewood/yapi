from enum import Enum
from typing import List, Optional
from decimal import Decimal

from pydantic import BaseModel, Field, PositiveInt, validator

from utils.time import validate_iso_time


class OrderStatusEnum(str, Enum):
    pending = 'pending'
    assigned = 'assigned'
    completed = 'completed'


class OrderKindaItem(BaseModel):
    """ Weak order item model for a preliminary validation """

    order_id: int

    class Config:
        extra = 'allow'


class OrderItem(BaseModel):
    """ Strict order item model for a final validation """

    order_id: PositiveInt
    weight: Decimal = Field(..., ge=Decimal('0.01'), le=Decimal('50.00'))
    region: PositiveInt
    delivery_hours: List[str]

    class Config:
        extra = 'forbid'


class OrdersPostRequest(BaseModel):
    data: List[OrderKindaItem]

    class Config:
        extra = 'forbid'


class OrdersAssignPostRequest(BaseModel):
    courier_id: PositiveInt

    class Config:
        extra = 'forbid'


class OrdersCompletePostRequest(BaseModel):
    courier_id: PositiveInt
    order_id: PositiveInt
    complete_time: str

    @validator('complete_time')
    def check_complete_time(cls, v):
        if not validate_iso_time(v):
            raise ValueError('wrong complete_time format')
        return v

    class Config:
        extra = 'forbid'
