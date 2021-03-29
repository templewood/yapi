if __name__ == "__main__":
    import sys
    sys.path.append("..")

from sqlalchemy import (
    MetaData, Table, Column, BigInteger, Enum, JSON, Numeric, Integer,
    ForeignKey, create_engine
)
from sqlalchemy.dialects.mysql import DATETIME

from schemas.couriers import CourierTypeEnum
from schemas.orders import OrderStatusEnum

metadata = MetaData()

tbl_couriers = Table(
    "couriers",
    metadata,
    Column("courier_id", BigInteger, primary_key=True, autoincrement=False),
    Column("courier_type", Enum(CourierTypeEnum), nullable=False),
    Column("regions", JSON, nullable=False),
    Column("working_hours", JSON, nullable=False),
)

tbl_orders = Table(
    "orders",
    metadata,
    Column("order_id", BigInteger, primary_key=True, autoincrement=False),
    Column("weight", Numeric(precision=5, scale=2), nullable=False),
    Column("region", BigInteger, nullable=False),
    Column("delivery_hours", JSON, nullable=False),
    Column("status", Enum(OrderStatusEnum), server_default=OrderStatusEnum.pending),
    Column("completed_at", DATETIME(fsp=2)),
)

tbl_deliveries = Table(
    "deliveries",
    metadata,
    Column("delivery_id", Integer, primary_key=True),
    Column("courier_id", BigInteger, nullable=False),
    Column("status", Enum(OrderStatusEnum), server_default=OrderStatusEnum.assigned),
    Column("assigned_at", DATETIME(fsp=2), nullable=False),
    Column("coeff", Integer, nullable=False),
)

tbl_deliveries_orders = Table(
    "deliveries_orders",
    metadata,
    Column("delivery_id", Integer, ForeignKey('deliveries.delivery_id',
        ondelete="CASCADE"), nullable=False),
    Column("order_id", BigInteger, nullable=False),
)

if __name__ == "__main__":
    from config import settings
    engine = create_engine(settings.database_url)
    metadata.drop_all(engine)
    metadata.create_all(engine)
