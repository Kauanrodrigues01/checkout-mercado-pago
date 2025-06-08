import uuid
from datetime import datetime, timedelta
from typing import Dict
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests

from app.settings import settings


class MercadoPagoService:
    """
    Serviço para interagir com a API de pagamentos do Mercado Pago.
    """

    # --- Mapeamentos de Status e Detalhes ---
    STATUS_MAP = {
        'unknown': 'Status desconhecido.',
        'pending': 'O usuário ainda não concluiu o processo de pagamento (por exemplo, ao gerar um boleto).',
        'approved': 'O pagamento foi aprovado e creditado com sucesso.',
        'authorized': 'O pagamento foi autorizado, mas ainda não foi capturado.',
        'in_process': 'O pagamento está em análise.',
        'in_mediation': 'O usuário iniciou uma disputa.',
        'rejected': 'O pagamento foi rejeitado (o usuário pode tentar pagar novamente).',
        'cancelled': 'O pagamento foi cancelado por uma das partes ou o prazo de pagamento expirou.',
        'refunded': 'O pagamento foi reembolsado ao usuário.',
        'charged_back': 'Um chargeback foi aplicado no cartão de crédito do comprador.',
    }

    STATUS_DETAIL_MAP = {
        'unknown': 'Status desconhecido.',
        'accredited': 'Pagamento creditado.',
        'partially_refunded': 'O pagamento foi feito com pelo menos um reembolso parcial.',
        'pending_capture': 'O pagamento foi autorizado e aguarda captura.',
        'offline_process': 'Por falta de processamento online, o pagamento está sendo processado de maneira offline.',
        'pending_contingency': 'Falha temporária. O pagamento será processado diferido.',
        'pending_review_manual': 'O pagamento está em revisão para determinar sua aprovação ou rejeição.',
        'pending_waiting_transfer': 'Aguardando que o usuário finalize o processo de pagamento no seu banco.',
        'pending_waiting_payment': 'Pendente até que o usuário realize o pagamento.',
        'pending_challenge': 'Pagamento com cartão de crédito com confirmação pendente (challenge).',
        'bank_error': 'Pagamento rejeitado por um erro com o banco.',
        'cc_rejected_3ds_mandatory': 'Pagamento rejeitado por não ter o challenge 3DS quando é obrigatório.',
        'cc_rejected_bad_filled_card_number': 'Número de cartão incorreto.',
        'cc_rejected_bad_filled_date': 'Data de validade incorreta.',
        'cc_rejected_bad_filled_other': 'Detalhes do cartão incorretos.',
        'cc_rejected_bad_filled_security_code': 'Código de segurança (CVV) incorreto.',
        'cc_rejected_blacklist': 'O cartão está desativado ou em uma lista de restrições (roubo/fraude).',
        'cc_rejected_call_for_authorize': 'O método de pagamento requer autorização prévia para o valor.',
        'cc_rejected_card_disabled': 'O cartão está inativo.',
        'cc_rejected_duplicated_payment': 'Pagamento duplicado.',
        'cc_rejected_high_risk': 'Recusado por prevenção de fraudes.',
        'cc_rejected_insufficient_amount': 'Limite do cartão insuficiente.',
        'cc_rejected_invalid_installments': 'Número inválido de parcelas.',
        'cc_rejected_max_attempts': 'Número máximo de tentativas excedido.',
        'cc_rejected_other_reason': 'Erro genérico do processador de pagamento.',
        'cc_rejected_time_out': 'A transação expirou (timeout).',
        'cc_amount_rate_limit_exceeded': 'Superou o limite de valor para o meio de pagamento.',
        'rejected_high_risk': 'Rejeitado por suspeita de fraude.',
        'rejected_insufficient_data': 'Rejeitado por falta de informações obrigatórias.',
        'rejected_by_bank': 'Operação recusada pelo banco.',
        'rejected_by_regulations': 'Pagamento recusado devido a regulamentações.',
        'rejected_by_biz_rule': 'Pagamento recusado devido a regras de negócio.',
    }

    def __init__(self):
        if not settings.MP_ACCESS_TOKEN:
            raise ValueError('A variável de ambiente MP_ACCESS_TOKEN não foi definida.')

        self._access_token = settings.MP_ACCESS_TOKEN
        self._base_url = settings.MP_BASE_API_URL
        self._notification_url = settings.NOTIFICATION_URL
        self._headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self._access_token}',
        }

    def generate_payment_expiration_date(self, days: int | None = None, hours: int | None = None, minutes: int | None = None):
        """
        Gera uma data de expiração no formato ISO 8601 com base no fuso horário configurado.
        """
        try:
            timezone = ZoneInfo(settings.DEFAULT_TIMEZONE)
        except ZoneInfoNotFoundError:
            raise ValueError(f'Timezone "{settings.DEFAULT_TIMEZONE}" não encontrado. Verifique a configuração.')

        current_time = datetime.now(timezone)
        time_delta = timedelta(days=days or 0, hours=hours or 0, minutes=minutes or 0)
        expiration_date = current_time + time_delta

        return expiration_date.isoformat(timespec='milliseconds')

    def pay_with_pix(self, amount: float, payer_email: str, payer_cpf: str, description: str = 'Pagamento'):
        """
        Cria um pagamento via Pix.
        """
        payload = {
            'payment_method_id': 'pix',
            'transaction_amount': float(amount),
            'description': description,
            'date_of_expiration': self.generate_payment_expiration_date(minutes=30),
            'payer': {'email': payer_email, 'identification': {'type': 'CPF', 'number': payer_cpf}},
            'external_reference': f'ID-PIX-{uuid.uuid4()}',
        }
        return self._create_payment(payload)

    def pay_with_boleto(
        self, amount: float, payer_email: str, payer_first_name: str, payer_last_name: str, payer_cpf: str, payer_address: Dict[str, str], description: str = 'Pagamento', days_to_expire: int = 3
    ):
        """
        Cria um pagamento via Boleto Bancário.
        """
        payload = {
            'transaction_amount': float(amount),
            'description': description,
            'payment_method_id': 'bolbradesco',
            'date_of_expiration': self.generate_payment_expiration_date(days=days_to_expire),
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
        return self._create_payment(payload)

    def pay_with_card(self, amount: float, payer_email: str, payer_cpf: str, card_data: dict, installments: int = 1, description: str = 'Pagamento'):
        """
        Cria um pagamento via Cartão de Crédito.
        """
        card_token = self._get_card_token(card_data)

        payload = {
            'transaction_amount': float(amount),
            'token': card_token.get('id'),
            'description': description,
            'installments': installments,
            'payer': {'email': payer_email, 'identification': {'type': 'CPF', 'number': payer_cpf}},
            'external_reference': f'ID-CARTAO-{uuid.uuid4()}',
            'statement_descriptor': 'Compra Online',
        }
        return self._create_payment(payload)

    # --- Métodos Internos Auxiliares ---

    def _handle_api_error(self, response: requests.Response):
        """
        Processa uma resposta de erro da API, enriquecendo a mensagem com os mapeamentos de status.
        """
        status_code = response.status_code
        try:
            error_data = response.json()
            status = error_data.get('status', 'unknown')
            status_detail = error_data.get('status_detail', 'unknown')

            status_map_message = self.STATUS_MAP.get(status, 'Erro desconhecido.')
            status_detail_map_message = self.STATUS_DETAIL_MAP.get(status_detail, 'Detalhe desconhecido.')

            return f'Erro na API do Mercado Pago ({status_code}): {status_map_message} - {status_detail_map_message}'

        except (requests.JSONDecodeError, IndexError):
            return f'Erro na API do Mercado Pago ({status_code}): {response.text}'

    def _post(self, path: str, payload: dict, use_idempotency_key: bool = True):
        """
        Executa uma requisição POST para a API do Mercado Pago.
        """
        url = f'{self._base_url}{path}'
        headers = self._headers.copy()

        if use_idempotency_key:
            headers['X-Idempotency-Key'] = str(uuid.uuid4())

        response = requests.post(url, headers=headers, json=payload)

        try:
            response.raise_for_status()
        except requests.HTTPError:
            error_message = self._handle_api_error(response)
            raise RuntimeError(error_message)

        return response.json()

    def _get_card_token(self, card_data: dict):
        """
        Obtém um token de cartão de crédito.
        """
        return self._post('/v1/card_tokens', card_data, use_idempotency_key=False)

    def _create_payment(self, payload: dict):
        """
        Cria um novo pagamento, adicionando a URL de notificação se configurada.
        """
        if self._notification_url:
            payload['notification_url'] = self._notification_url

        return self._post('/v1/payments', payload)


def run_test_pay_with_pix():
    """
    Função de teste para pagamento via Pix.
    """
    try:
        response = mp_service.pay_with_pix(
            amount=100.00,
            payer_email='test_user_123@testuser.com',
            payer_cpf='12345678909',
            description='Teste de pagamento com Pix',
        )
        print('--- Resposta PIX ---')
        print(response)
    except Exception as e:
        print(f'Erro ao processar pagamento PIX: {e}')


def run_test_pay_with_boleto():
    address_data = {'zip_code': '01001-000', 'street_name': 'Praça da Sé', 'street_number': 's/n', 'neighborhood': 'Sé', 'city': 'São Paulo', 'federal_unit': 'SP'}

    try:
        response = mp_service.pay_with_boleto(
            amount=150.75,
            payer_email='test82281@gmail.com',
            payer_first_name='Carlos',
            payer_last_name='Junior',
            payer_cpf='12345678909',
            payer_address=address_data,
            description='Compra de teste com Boleto',
        )
        print('--- Resposta BOLETO ---')
        print(response)
    except Exception as e:
        print(f'Erro ao processar pagamento com boleto: {e}')


def run_test_pay_with_card():
    """
    Função de teste para pagamento via Cartão de Crédito.
    """
    try:
        card_data = {
            'card_number': '5031433215406351',
            'expiration_month': '11',
            'expiration_year': '2030',
            'security_code': '143',
            'cardholder': {
                # 'name': 'Test User', # Se usar este vai ser aprovado, com as credenciais de teste do Mercado Pago
                'name': 'Other User',  # Se usar este vai ser reprovado, com as credenciais de teste do Mercado Pago
                'identification': {'type': 'CPF', 'number': '12345678909'},
            },
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


if __name__ == '__main__':
    mp_service = MercadoPagoService()

    # TEST PIX 💰
    run_test_pay_with_pix()
    print()
    print('---' * 10)

    # TEST BOLETO 📄
    run_test_pay_with_boleto()
    print()
    print('---' * 10)

    # TEST CARTÃO 💳
    run_test_pay_with_card()
    print()
    print('---' * 10)
