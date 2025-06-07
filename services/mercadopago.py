import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests
from decouple import config

# --- Módulo de Configuração ---
# Carrega as configurações a partir de variáveis de ambiente ou arquivo .env
MP_ACCESS_TOKEN = config('MP_ACCESS_TOKEN', default=None)
MP_BASE_API_URL = config('MP_BASE_API_URL', default='https://api.mercadopago.com')
NOTIFICATION_URL = config('NOTIFICATION_URL', default=None)
DEFAULT_TIMEZONE = config('TIMEZONE', default='America/Sao_Paulo')


class MercadoPagoService:
    """
    Serviço para interagir com a API de pagamentos do Mercado Pago.
    """
    def __init__(self):
        if not MP_ACCESS_TOKEN:
            raise ValueError("A variável de ambiente MP_ACCESS_TOKEN não foi definida.")

        self.__access_token = MP_ACCESS_TOKEN
        self.__base_url = MP_BASE_API_URL
        self.__notification_url = NOTIFICATION_URL
        self.__headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.__access_token}',
        }

    def __post(self, path: str, payload: dict):
        """
        Executa uma requisição POST para a API do Mercado Pago.
        """
        url = f'{self.__base_url}{path}'
        idempotency_key = str(uuid.uuid4())

        response = requests.post(
            url,
            headers={**self.__headers, 'X-Idempotency-Key': idempotency_key},
            json=payload
        )

        try:
            response.raise_for_status()
        except requests.HTTPError:
            error_details = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
            raise RuntimeError(f'Erro na API do Mercado Pago ({response.status_code}): {error_details}')

        return response.json()

    def __create_payment(self, payload: dict):
        """
        Cria um novo pagamento enviando os dados para o endpoint /v1/payments.
        """
        return self.__post('/v1/payments', payload)

    def generate_payment_expiration_date(self, days: Optional[int] = None, hours: Optional[int] = None, minutes: Optional[int] = None):
        """
        Gera uma data de expiração no formato ISO 8601 com base no fuso horário configurado.
        """
        try:
            timezone = ZoneInfo(DEFAULT_TIMEZONE)
        except ZoneInfoNotFoundError:
            raise ValueError(f'Timezone "{DEFAULT_TIMEZONE}" não encontrado. Verifique a configuração.')

        current_time = datetime.now(timezone)
        time_delta = timedelta(days=days or 0, hours=hours or 0, minutes=minutes or 0)
        expiration_date = current_time + time_delta

        return expiration_date.isoformat(timespec='milliseconds')

    def pay_with_pix(self, amount: float, payer_email: str, payer_cpf: str, description: str = 'Pagamento'):
        """
        Cria um pagamento via Pix.
        """
        expiration_date = self.generate_payment_expiration_date(minutes=30)

        payload = {
            'payment_method_id': 'pix',
            'transaction_amount': float(amount),
            'description': description,
            'date_of_expiration': expiration_date,
            'payer': {
                'email': payer_email,
                'identification': {
                    'type': 'CPF',
                    'number': payer_cpf
                }
            },
            'external_reference': f'ID-PIX-{uuid.uuid4()}'
        }

        if self.__notification_url:
            payload['notification_url'] = self.__notification_url

        return self.__create_payment(payload)


if __name__ == '__main__':
    mp_service = MercadoPagoService()

    # TEST PIX
    try:
        response = mp_service.pay_with_pix(
            amount=100.00,
            payer_email='test_user_123@testuser.com',
            payer_cpf='12345678909',
            description='Teste de pagamento com Pix',
        )
        print("--- Resposta PIX ---")
        print(response)
    except Exception as e:
        print(f'Erro ao processar pagamento PIX: {e}')
