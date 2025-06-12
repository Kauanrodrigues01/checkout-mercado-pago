from typing import Annotated

from pydantic import BaseModel, EmailStr, StringConstraints

from payments.models import PaymentMethod, PaymentStatus


class PaymentPublicSchema(BaseModel):
    id: int
    amount: float
    transaction_id: str
    payment_method: PaymentMethod
    payment_status: PaymentStatus


CPFStr = Annotated[str, StringConstraints(min_length=11, max_length=14, pattern=r'^\d+$')]
CardNumberStr = Annotated[str, StringConstraints(min_length=13, max_length=19)]
SecurityCodeStr = Annotated[str, StringConstraints(min_length=3, max_length=4)]
MonthStr = Annotated[str, StringConstraints(min_length=1, max_length=2)]
YearStr = Annotated[str, StringConstraints(min_length=4, max_length=4)]
UFStr = Annotated[str, StringConstraints(min_length=2, max_length=2)]


class PaymentBaseSchema(BaseModel):
    payer_email: EmailStr
    transaction_amount: float
    description: str = 'Pagamento via Mercado Pago'


class PixPaymentSchema(PaymentBaseSchema):
    payer_cpf: CPFStr


class BoletoPaymentSchema(PaymentBaseSchema):
    payer_first_name: str
    payer_last_name: str
    payer_cpf: CPFStr
    zip_code: str
    street_name: str
    street_number: str
    neighborhood: str
    city: str
    federal_unit: UFStr


class CardPaymentSchema(PaymentBaseSchema):
    card_number: CardNumberStr
    expiration_month: MonthStr
    expiration_year: YearStr
    security_code: SecurityCodeStr
    cardholder_name: str
    payer_cpf: CPFStr
    installments: int
