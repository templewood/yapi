if __name__ == "__main__":
    import sys
    sys.path.append("..")

from sqlalchemy import (
    MetaData, Table, Column, BigInteger, Enum, JSON, Numeric, create_engine
)
from schemas.couriers import CourierTypeEnum
from schemas.orders import OrderStatusEnum

metadata = MetaData()

tbl_couriers = Table(
    "couriers",
    metadata,
    Column("courier_id", BigInteger, primary_key=True, autoincrement=False),
    Column("courier_type", Enum(CourierTypeEnum)),
    Column("regions", JSON),
    Column("working_hours", JSON),
)

tbl_orders = Table(
    "orders",
    metadata,
    Column("order_id", BigInteger, primary_key=True, autoincrement=False),
    Column("weight", Numeric(precision=5, scale=2)),
    Column("region", BigInteger),
    Column("delivery_hours", JSON),
    Column("status", Enum(OrderStatusEnum), server_default=OrderStatusEnum.pending),
)

if __name__ == "__main__":
    from config import Settings
    settings = Settings(_env_file='../.env')
    engine = create_engine(settings.database_url)
    metadata.drop_all(engine)
    metadata.create_all(engine)
