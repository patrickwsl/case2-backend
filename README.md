📌 Visão Geral
API desenvolvida com FastAPI, SQLAlchemy e Alembic, utilizando PostgreSQL e Redis via Docker.

🚀 Tecnologias
Python 3.11

FastAPI

SQLAlchemy

Alembic

PostgreSQL 15

Redis 7

Docker & Docker Compose

📂 Estrutura Inicial
O banco é inicializado com as tabelas:

clients - dados de clientes

assets - ativos financeiros

allocations - alocações de ativos por cliente

daily_returns - preços de fechamento diários

🛠️ Como Rodar o Projeto

Clonar o repositório:
git clone <url-do-repo-backend>
cd backend

Subir os containers:
docker compose up --build

Acessar a API:
Documentação Swagger: http://localhost:8000/docs

📜 Migrações
Para criar ou aplicar migrações:

docker compose exec backend alembic revision --autogenerate -m "descrição"
docker compose exec backend alembic upgrade head