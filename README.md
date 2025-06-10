# Integração de Pagamentos com Mercado Pago 💳

<p align="center">
  <img src="https://raw.githubusercontent.com/Kauanrodrigues01/Kauanrodrigues01/refs/heads/main/images/projetos/checkout-mercado-pago/checkout-cartao.png" width="49%">
  <img src="https://raw.githubusercontent.com/Kauanrodrigues01/Kauanrodrigues01/refs/heads/main/images/projetos/checkout-mercado-pago/tela-mp-pix.png" width="49%">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/Kauanrodrigues01/Kauanrodrigues01/refs/heads/main/images/projetos/checkout-mercado-pago/docs.png" width="60%">
</p>


Um projeto de estudo focado na integração de diferentes métodos de pagamento (PIX, Boleto e Cartão de Crédito) através da API do Mercado Pago, utilizando **FastAPI** como backend e **Jinja2** para a renderização de templates HTML.

## 📖 Sobre o Projeto

Este repositório foi desenvolvido como uma ferramenta de aprendizado para compreender o fluxo de comunicação com uma API de pagamentos externa. O objetivo principal foi construir um cliente Python robusto e modular, capaz de gerenciar as três formas de pagamento mais populares no Brasil, expondo-as através de uma interface web simples e funcional.

O projeto simula um checkout básico, onde o usuário pode escolher o método de pagamento e visualizar o resultado da transação gerado pela API do Mercado Pago.

---

## ✨ Principais Funcionalidades

* **Pagamento com PIX:** Geração de QR Code e código "Copia e Cola" com tempo de expiração.
* **Pagamento com Boleto Bancário:** Geração de boleto com informações do pagador e data de vencimento.
* **Pagamento com Cartão de Crédito:** Processamento de pagamento com validação de dados do cartão, incluindo nome do titular e CPF.
* **Notificações via Webhooks:** Endpoint dedicado para receber e processar notificações do Mercado Pago, atualizando o status do pagamento (aprovado, recusado, cancelado) em tempo real no banco de dados.
* **Interface Web Simples:** Um frontend básico criado com HTML e Jinja2 para interagir com o backend.
* **Serviço Modular:** A lógica de comunicação com o Mercado Pago está encapsulada na classe `MercadoPagoService`, facilitando a manutenção e o reuso do código.

## 🎣 Webhooks: Recebendo Notificações em Tempo Real

Uma das funcionalidades cruciais deste projeto é a capacidade de receber notificações via **webhooks do Mercado Pago**. Isso permite que nossa aplicação seja informada sobre atualizações nos pagamentos de forma **assíncrona** e **imediata**.

### Como funciona?

#### 1. Configuração
Uma URL da nossa aplicação é registrada na plataforma do **Mercado Pago** como um **endpoint de webhook**.

#### 2. Notificação
Quando um evento ocorre (ex: um cliente paga um boleto ou um pagamento de cartão é aprovado), o **Mercado Pago envia uma notificação** (um `POST` request) para essa URL.

#### 3. Processamento
A aplicação:
- recebe a notificação,
- verifica sua autenticidade,
- utiliza os dados para **atualizar o status do pagamento** correspondente no banco de dados.

✅ Esse mecanismo garante que o **status dos pagamentos** em nosso sistema esteja **sempre sincronizado** com o Mercado Pago, **sem a necessidade de consultar a API repetidamente**.

---

## 🛠️ Tecnologias Utilizadas

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLalchemy](https://img.shields.io/badge/sqlalchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Jinja](https://img.shields.io/badge/-Jinja-4B0082?logo=jinja&logoColor=white&style=flat)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

---

## 🚀 Como Executar o Projeto Localmente

Siga os passos abaixo para rodar a aplicação em sua máquina.

### Pré-requisitos

* [Git](https://git-scm.com/)
* [Python 3.9+](https://www.python.org/downloads/)
* Um gerenciador de pacotes como `pip`

### Passos

1.  **Clone o repositório:**
    ```sh
    git clone [https://github.com/Kauanrodrigues01/integracao-pagamento-mercado-pago.git](https://github.com/Kauanrodrigues01/checkout-mercado-pago.git)
    ```

2.  **Acesse o diretório do projeto:**
    ```sh
    cd integracao-pagamento-mercado-pago
    ```

3.  **Crie e ative um ambiente virtual (Recomendado):**
    ```sh
    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Para macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

4.  **Instale as dependências necessárias:**
    ```sh
    pip install -r requirements.txt
    ```

5.  **Configure as variáveis de ambiente:**
    Crie um arquivo chamado `.env` na raiz do projeto, copiando o conteúdo do arquivo `.env.example` (se houver) ou usando o modelo abaixo. Você precisará do seu **Access Token** de testes do Mercado Pago.

    ```ini
    # Arquivo .env
    MP_PUBLIC_KEY=your-public-key-here
    MP_ACCESS_TOKEN=your-access-token-here
    MP_BASE_API_URL=https://api.mercadopago.com
    DEFAULT_TIMEZONE=America/Fortaleza
    NOTIFICATION_URL=https://your-domain.com.br/api/notifications
    DATABASE_URL=postgresql+asyncpg://admin:senha123@localhost:5432/meubanco
    ```

6.  **Inicie o servidor local:**
    ```sh
    uvicorn main:app --reload
    ```

7.  Abra seu navegador e acesse [http://127.0.0.1:8000](http://127.0.0.1:8000) para ver a aplicação funcionando.

---
