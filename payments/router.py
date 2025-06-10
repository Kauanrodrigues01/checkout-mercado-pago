from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse

from services.mercadopago import MercadoPagoService

from sqlalchemy import select

from app.dependencies import T_Session
from payments.models import Payment, PaymentMethod, PaymentStatus
from payments.schemas import PaymentPublicSchema, CardPaymentSchema, BoletoPaymentSchema, PixPaymentSchema

mp = MercadoPagoService()

router = APIRouter(prefix='/payments', tags=['payments'])

@router.post('/checkout/pix')
async def checkout_pix(data: PixPaymentSchema, session: T_Session):
    try:
        response = mp.pay_with_pix(
            amount=data.transaction_amount,
            description=data.description,
            payer_email=data.payer_email,
            payer_cpf=data.payer_cpf,
        )

        payment = Payment(
            amount=data.transaction_amount,
            payment_method=PaymentMethod.PIX,
            transaction_id=str(response.get('id'))
        )
        session.add(payment)
        await session.commit()
        await session.refresh(payment)

        return JSONResponse(response)

    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.post('/checkout/boleto')
async def checkout_boleto(data: BoletoPaymentSchema, session: T_Session):
    try:
        address_data = {
            'zip_code': data.zip_code,
            'street_name': data.street_name,
            'street_number': data.street_number,
            'neighborhood': data.neighborhood,
            'city': data.city,
            'federal_unit': data.federal_unit,
        }

        response = mp.pay_with_boleto(
            amount=data.transaction_amount,
            description=data.description,
            payer_email=data.payer_email,
            payer_cpf=data.payer_cpf,
            payer_first_name=data.payer_first_name,
            payer_last_name=data.payer_last_name,
            payer_address=address_data,
        )

        payment = Payment(
            amount=data.transaction_amount,
            payment_method=PaymentMethod.BOLETO,
            transaction_id=str(response.get('id'))
        )
        session.add(payment)
        await session.commit()
        await session.refresh(payment)

        return JSONResponse(response)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.post('/checkout/card')
async def checkout_card(data: CardPaymentSchema, session: T_Session):
    try:
        card_data = {
            'card_number': data.card_number,
            'expiration_month': data.expiration_month,
            'expiration_year': data.expiration_year,
            'security_code': data.security_code,
            'cardholder': {
                'name': data.cardholder_name,
                'identification': {'type': 'CPF', 'number': data.payer_cpf},
            },
        }

        response = mp.pay_with_card(
            amount=data.transaction_amount,
            description=data.description,
            payer_email=data.payer_email,
            payer_cpf=data.payer_cpf,
            installments=data.installments,
            card_data=card_data,
        )
        
        status = response.get('status')

        payment = Payment(
            amount=data.transaction_amount,
            payment_method=PaymentMethod.CREDIT_CARD,
            transaction_id=str(response.get('id'))
        )

        if status == 'approved':
            payment.payment_status = PaymentStatus.PAID
        elif status == 'rejected':
            payment.payment_status = PaymentStatus.FAILED
        else:
            payment.payment_status = PaymentStatus.PENDING

        session.add(payment)
        await session.commit()
        await session.refresh(payment)

        return JSONResponse(response)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.post('/notification')
async def checkout_notification(request: Request, session: T_Session):
    """
    Endpoint responsável por receber notificações do Mercado Pago sobre o status dos pagamentos.
    """
    data = await request.json()
    action = data.get('action')
    transiction_id = data.get('data', {}).get('id')

    if action == 'payment.updated':
        try:
            payment_info = mp.get_payment_info(transiction_id)
            status = payment_info.get('status')
            status_detail = payment_info.get('status_detail')
            payment = await session.scalar(
                select(Payment).where(Payment.transaction_id == str(transiction_id))
            )
            
            if not payment:
                return JSONResponse(
                    {'message': 'Payment not found.'}, status_code=status.HTTP_404_NOT_FOUND
                )

            if status == 'approved' and status_detail == 'accredited':
                payment.payment_status = PaymentStatus.PAID
                await session.commit()
                return JSONResponse({'message': 'Payment updated successfully.'}, status_code=status.HTTP_200_OK)
                
            elif status == 'rejected':
                payment.payment_status = PaymentStatus.FAILED
                await session.commit()
                return JSONResponse({'message': 'Payment updated successfully.'}, status_code=status.HTTP_200_OK)
            
            elif status == 'pending':
                payment.payment_status = PaymentStatus.CANCELLED
                await session.commit()
                return JSONResponse({'message': 'Payment updated successfully.'}, status_code=status.HTTP_200_OK)

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.get('/list', response_model=list[PaymentPublicSchema])
async def list_payments(session: T_Session):
    payments = (await session.scalars(
        select(Payment)
    )).all()
    
    return payments


@router.delete('/delete/{payment_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(session: T_Session, payment_id):
    payment = await session.scalar(select(Payment).where(Payment.id == int(payment_id)))
    await session.delete(payment)
    await session.commit()