from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from services.mercadopago import MercadoPagoService

app = FastAPI()

templates = Jinja2Templates(directory='templates')

mp = MercadoPagoService()


@app.get('/', response_class=HTMLResponse)
async def checkout_page(request: Request):
    return templates.TemplateResponse(name='checkout.html', context={'request': request})


@app.post('/checkout')
async def checkout(request: Request):
    data = await request.json()
    print(data)
    payment_method = data.get('payment_method')
    amount = float(data.get('transaction_amount', 0))
    description = data.get('description', 'Pagamento via Mercado Pago')
    payer_email = data.get('payer_email', '')
    payer_cpf = data.get('payer_cpf', '')

    try:
        if payment_method == 'pix':
            response = mp.pay_with_pix(amount=amount, description=description, payer_email=payer_email, payer_cpf=payer_cpf)

        elif payment_method == 'boleto':
            payer_first_name = data.get('payer_first_name')
            payer_last_name = data.get('payer_last_name')
            address_data = {
                'zip_code': data.get('zip_code'),
                'street_name': data.get('street_name'),
                'street_number': data.get('street_number'),
                'neighborhood': data.get('neighborhood'),
                'city': data.get('city'),
                'federal_unit': data.get('federal_unit'),
            }

            response = mp.pay_with_boleto(
                amount=amount,
                description=description,
                payer_email=payer_email,
                payer_cpf=payer_cpf,
                payer_address=address_data,
                payer_first_name=payer_first_name,
                payer_last_name=payer_last_name,
            )

        elif payment_method == 'card':
            card_data = {
                'card_number': data.get('card_number'),
                'expiration_month': data.get('expiration_month'),
                'expiration_year': data.get('expiration_year'),
                'security_code': data.get('security_code'),
                'cardholder': {'name': data.get('cardholder_name'), 'identification': {'type': 'CPF', 'number': payer_cpf}},
            }

            response = mp.pay_with_card(amount=amount, description=description, payer_email=payer_email, payer_cpf=payer_cpf, installments=int(data.get('installments', 1)), card_data=card_data)

        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Método de pagamento inválido')

        print(response)
        return JSONResponse(response)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
