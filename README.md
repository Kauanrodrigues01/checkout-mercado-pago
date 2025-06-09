# Integração de Pagamentos com Mercado Pago 💳

<p align="center">
  <img src="https://raw.githubusercontent.com/Kauanrodrigues01/Kauanrodrigues01/refs/heads/main/images/projetos/checkout-mercado-pago/checkout-cartao.png" width="32%">
  <img src="https://raw.githubusercontent.com/Kauanrodrigues01/Kauanrodrigues01/refs/heads/main/images/projetos/checkout-mercado-pago/tela-mp-pix.png" width="32%">
  <img src="https://raw.githubusercontent.com/Kauanrodrigues01/Kauanrodrigues01/refs/heads/main/images/projetos/checkout-mercado-pago/checkout-boleto.png" width="32%">
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
* **Interface Web Simples:** Um frontend básico criado com HTML e Jinja2 para interagir com o backend.
* **Serviço Modular:** A lógica de comunicação com o Mercado Pago está encapsulada na classe `MercadoPagoService`, facilitando a manutenção e o reuso do código.

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
    ```

6.  **Inicie o servidor local:**
    ```sh
    uvicorn main:app --reload
    ```

7.  Abra seu navegador e acesse [http://127.0.0.1:8000](http://127.0.0.1:8000) para ver a aplicação funcionando.

---

## 👨‍💻 Autor

[![LinkedIn](https://img.shields.io/badge/linkedin-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kauan-rodrigues-lima/)
[![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Kauanrodrigues01)
