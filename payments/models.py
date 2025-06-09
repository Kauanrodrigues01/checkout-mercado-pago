import enum
from datetime import datetime
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import table_registry


class PaymentMethod(enum.Enum):
    CREDIT_CARD = 'credit_card'
    PIX = 'pix'
    BOLETO = 'boleto'


class PaymentStatus(enum.Enum):
    PENDING = 'pending'
    PAID = 'paid'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


@table_registry.mapped_as_dataclass
class Payment:
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    amount: Mapped[float]
    transaction_id: Mapped[str]
    payment_method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod), nullable=False)
    payment_status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
