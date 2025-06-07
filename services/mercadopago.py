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
            raise ValueError('A variável de ambiente MP_ACCESS_TOKEN não foi definida.')

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

        response = requests.post(url, headers={**self.__headers, 'X-Idempotency-Key': idempotency_key}, json=payload)

        try:
            response.raise_for_status()
        except requests.HTTPError:
            error_details = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
            raise RuntimeError(f'Erro na API do Mercado Pago ({response.status_code}): {error_details}')

        return response.json()

    def __get_card_info(self, card_data: dict):
        """
        Obtém informações do cartão de crédito enviando os dados para o endpoint /v1/card_tokens.
        """
        url = f'{self.__base_url}/v1/card_tokens'

        response = requests.post(url, headers=self.__headers, json=card_data)

        try:
            response.raise_for_status()
        except requests.HTTPError:
            try:
                error = response.json()
            except ValueError:
                error = response.text
            raise RuntimeError(f'Erro ao criar token de cartão ({response.status_code}): {error}')

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
            'payer': {'email': payer_email, 'identification': {'type': 'CPF', 'number': payer_cpf}},
            'external_reference': f'ID-PIX-{uuid.uuid4()}',
        }

        if self.__notification_url:
            payload['notification_url'] = self.__notification_url

        return self.__create_payment(payload)

    def pay_with_boleto(
        self, amount: float, payer_email: str, payer_first_name: str, payer_last_name: str, payer_cpf: str, payer_address: Dict[str, str], description: str = 'Pagamento', days_to_expire: int = 3
    ):
        """
        Cria um pagamento via Boleto Bancário.
        """
        expiration_date = self.generate_payment_expiration_date(days=days_to_expire)

        payload = {
            'transaction_amount': float(amount),
            'description': description,
            'payment_method_id': 'bolbradesco',
            'date_of_expiration': expiration_date,
            'payer': {
                'first_name': payer_first_name,
                'last_name': payer_last_name,
                'email': payer_email,
                'identification': {'type': 'CPF', 'number': payer_cpf},
                'address': {
                    'zip_code': payer_address.get('zip_code'),
                    'street_name': payer_address.get('street_name'),
                    'street_number': payer_address.get('street_number'),
                    'neighborhood': payer_address.get('neighborhood'),
                    'city': payer_address.get('city'),
                    'federal_unit': payer_address.get('federal_unit'),
                },
            },
            'external_reference': f'ID-BOLETO-{uuid.uuid4()}',
        }

        if self.__notification_url:
            payload['notification_url'] = self.__notification_url

        return self.__create_payment(payload)

    def pay_with_card(self, amount: float, payer_email: str, payer_cpf: str, card_data: dict, installments: int = 1, description: str = 'Pagamento'):
        """
        Cria um pagamento via Cartão de Crédito.
        """
        payload = {
            'transaction_amount': float(amount),
            'token': self.__get_card_info(card_data).get('id'),
            'description': description,
            'installments': installments,  # Número de parcelas
            # 'payment_method_id': 'visa',
            'payer': {'email': payer_email, 'identification': {'type': 'CPF', 'number': payer_cpf}},
            'external_reference': f'ID-CARTAO-{uuid.uuid4()}',
        }

        if self.__notification_url:
            payload['notification_url'] = self.__notification_url

        return self.__create_payment(payload)


if __name__ == '__main__':
    mp_service = MercadoPagoService()

    # TEST PIX
    # try:
    #     response = mp_service.pay_with_pix(
    #         amount=100.00,
    #         payer_email='test_user_123@testuser.com',
    #         payer_cpf='12345678909',
    #         description='Teste de pagamento com Pix',
    #     )
    #     print("--- Resposta PIX ---")
    #     print(response)
    # except Exception as e:
    #     print(f'Erro ao processar pagamento PIX: {e}')

    # TEST BOLETO 📄
    # address_data = {
    #     'zip_code': '01001-000',
    #     'street_name': 'Praça da Sé',
    #     'street_number': 's/n',
    #     'neighborhood': 'Sé',
    #     'city': 'São Paulo',
    #     'federal_unit': 'SP'
    # }

    # try:
    #     response = mp_service.pay_with_boleto(
    #         amount=150.75,
    #         payer_email='test82281@gmail.com',
    #         payer_first_name='Carlos',
    #         payer_last_name='Junior',
    #         payer_cpf='12345678909',
    #         payer_address=address_data,
    #         description='Compra de teste com Boleto'
    #     )
    #     print("--- Resposta BOLETO ---")
    #     print(response)
    # except Exception as e:
    #     print(f'Erro ao processar pagamento com boleto: {e}')

    # TEST CARTÃO 💳
    try:
        card_data = {
            'card_number': '5031433215406351',
            'expiration_month': '11',
            'expiration_year': '2030',
            'security_code': '123',
            'cardholder': {'name': 'Test User', 'identification': {'type': 'CPF', 'number': '12345678909'}},
        }

        response = mp_service.pay_with_card(
            amount=200.00,
            card_data=card_data,
            description='Teste de pagamento com Cartão',
            payer_cpf='12345678909',
            payer_email='test1717@gmail.com',
        )
        print('--- Resposta CARTÃO ---')
        print(response)
    except Exception as e:
        print(f'Erro ao processar pagamento com cartão: {e}')
