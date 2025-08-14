# Backend - API de Captado

📌 **Visão Geral**
API desenvolvida com **FastAPI**, **SQLAlchemy** e **Alembic**, utilizando **PostgreSQL** e **Redis** via Docker. Fornece dados de clientes, ativos e alocações, incluindo cálculos de valores captados e rentabilidade.

---

🚀 **Tecnologias**

* Python 3.11
* FastAPI
* SQLAlchemy
* Alembic
* PostgreSQL 15
* Redis 7
* Docker & Docker Compose

---

📂 **Estrutura Inicial**

O banco é inicializado com as seguintes tabelas:

* **clients** - dados de clientes
* **assets** - ativos financeiros
* **allocations** - alocações de ativos por cliente
* **daily\_returns** - preços de fechamento diários

---

🛠️ **Como Rodar o Projeto**

1. Clonar o repositório:

git clone <url-do-repo-backend>
cd backend

2. Subir os containers via Docker Compose:

docker compose up --build

3. Rodar o FastAPI manualmente (opcional, se não usar Docker Compose):

uvicorn main:app --reload --host 0.0.0.0 --port 8000

4. Acessar a API no navegador:

* Documentação Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
* Requisições via Postman ou outro cliente HTTP: `http://localhost:8000/`

---

📜 **Migrações com Alembic**

Para criar uma nova migração:

docker compose exec backend alembic revision --autogenerate -m "descrição da migração"

Para aplicar todas as migrações:

docker compose exec backend alembic upgrade head

---

🟢 **WebSocket e Endpoints Principais**

* WebSocket para captado: `ws://localhost:8000/ws/captado?month=<MÊS>&year=<ANO>`
* Endpoints REST:

  * `/clients` - lista de clientes
  * `/assets` - lista de ativos
  * `/allocations` - alocações por cliente
  * `/daily_returns` - preços diários de ativos

⚡ **Observações**

* Certifique-se de que o Docker e Docker Compose estão instalados.
* O FastAPI estará disponível no container **backend**.
* Redis é utilizado para WebSocket e cache de dados.
* Todas as alterações no banco de dados devem ser feitas via Alembic para manter consistência.
