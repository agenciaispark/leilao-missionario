# Leilão Missionário

Este projeto é uma aplicação completa de leilão missionário, desenvolvida com um backend em Flask (Python) e um frontend em React, utilizando Tailwind CSS para estilização. A aplicação permite a criação de campanhas de leilão, gerenciamento de itens, lances de usuários e um painel administrativo.

## Funcionalidades

### Frontend (Público)

*   Visualização de campanhas de leilão ativas.
*   Detalhes de itens em leilão.
*   Realização de lances em itens.
*   Página inicial com listagem de itens.

### Backend (API REST)

*   Autenticação de usuários (JWT).
*   Gerenciamento de usuários.
*   Gerenciamento de campanhas de leilão.
*   Gerenciamento de categorias de itens.
*   Gerenciamento de itens de leilão.
*   Registro e validação de lances.
*   Endpoints para dashboard administrativo.

## Tecnologias Utilizadas

### Backend

*   **Python 3.11**
*   **Flask**: Framework web.
*   **SQLAlchemy**: ORM para interação com o banco de dados.
*   **Psycopg2**: Adaptador PostgreSQL para Python.
*   **PyJWT**: Para autenticação baseada em JSON Web Tokens.
*   **Bcrypt**: Para hash de senhas.
*   **python-dotenv**: Para gerenciamento de variáveis de ambiente.

### Frontend

*   **React**: Biblioteca JavaScript para construção de interfaces de usuário.
*   **Vite**: Ferramenta de build para projetos frontend.
*   **Tailwind CSS**: Framework CSS utilitário para estilização rápida.
*   **React Router DOM**: Para roteamento na aplicação SPA.
*   **Axios**: Cliente HTTP para requisições à API.

### Banco de Dados

*   **PostgreSQL**: Sistema de gerenciamento de banco de dados relacional.

### Deploy

*   **Docker** e **Docker Compose**: Para conteinerização da aplicação.
*   **Portainer**: Ferramenta de gerenciamento de containers.
*   **EasyPanel**: Plataforma de deploy simplificada.

## Estrutura do Projeto

```
leilao-missionario/
├── backend/                  # Contém o código do backend (API REST)
│   └── leilao_api/           # Aplicação Flask
│       ├── Dockerfile        # Dockerfile para o backend
│       ├── src/              # Código fonte da aplicação
│       │   ├── auth.py       # Lógica de autenticação JWT
│       │   ├── config.py     # Configurações da aplicação e DB
│       │   ├── db.py         # Conexão com o PostgreSQL
│       │   ├── main.py       # Ponto de entrada da aplicação Flask
│       │   └── routes/       # Módulos de rotas da API
│       │       ├── auth.py
│       │       ├── campanhas.py
│       │       ├── categorias.py
│       │       ├── dashboard.py
│       │       ├── itens.py
│       │       ├── lances.py
│       │       └── usuarios.py
│       ├── .env.example      # Exemplo de variáveis de ambiente
│       └── requirements.txt  # Dependências Python
├── frontend/                 # Contém o código do frontend (React)
│   └── leilao-frontend/      # Aplicação React
│       ├── Dockerfile        # Dockerfile para o frontend
│       ├── public/
│       ├── src/
│       │   ├── assets/
│       │   ├── components/
│       │   │   └── ui/       # Componentes Shadcn/ui
│       │   ├── contexts/     # Contexto de autenticação
│       │   ├── pages/        # Páginas da aplicação
│       │   │   ├── Home.jsx
│       │   │   ├── ItemDetails.jsx
│       │   │   ├── Login.jsx
│       │   │   └── Dashboard.jsx
│       │   ├── services/     # Serviço de API para comunicação com o backend
│       │   ├── App.css
│       │   ├── App.jsx       # Componente principal e rotas
│       │   ├── index.css
│       │   └── main.jsx
│       ├── .env.example      # Exemplo de variáveis de ambiente
│       └── package.json      # Dependências Node.js/React
├── database/                 # Contém scripts SQL
│   └── schema.sql            # Comandos SQL para criação das tabelas
├── docs/                     # Documentação adicional (guias de deploy)
│   ├── github_instructions.md
│   ├── portainer_deploy_instructions.md
│   └── easypanel_deploy_instructions.md
├── docker-compose.prod.yml   # Arquivo Docker Compose para deploy em produção
└── README.md                 # Este arquivo
```

## Como Executar Localmente (Desenvolvimento)

### 1. Configurar o Banco de Dados

Certifique-se de ter o PostgreSQL instalado e rodando. Crie um banco de dados chamado `leilao_missionario` e um usuário `postgres` com senha `postgres` (ou ajuste as configurações no `backend/leilao_api/src/config.py` e `docker-compose.prod.yml`).

Execute o script `schema.sql` para criar as tabelas:

```bash
psql -U postgres -d leilao_missionario -f database/schema.sql
```

### 2. Configurar e Rodar o Backend

1.  Navegue até o diretório do backend:
    ```bash
    cd backend/leilao_api
    ```
2.  Crie e ative um ambiente virtual:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
4.  Crie um arquivo `.env` na raiz de `backend/leilao_api` com base no `.env.example` e preencha as variáveis de ambiente, especialmente `SECRET_KEY` e `JWT_SECRET_KEY` com valores seguros.
5.  Execute a aplicação Flask:
    ```bash
    flask run --host=0.0.0.0 --port=5000
    ```
    O backend estará disponível em `http://localhost:5000`.

### 3. Configurar e Rodar o Frontend

1.  Navegue até o diretório do frontend:
    ```bash
    cd frontend/leilao-frontend
    ```
2.  Instale as dependências:
    ```bash
    pnpm install
    # ou npm install, ou yarn install, dependendo do seu gerenciador de pacotes
    ```
3.  Crie um arquivo `.env` na raiz de `frontend/leilao-frontend` com base no `.env.example` e defina a URL da API:
    ```
    VITE_API_URL=http://localhost:5000/api
    ```
4.  Execute a aplicação React:
    ```bash
    pnpm run dev
    # ou npm run dev, ou yarn dev
    ```
    O frontend estará disponível em `http://localhost:5173` (ou outra porta indicada pelo Vite).

## Deploy da Aplicação

Para deploy em ambientes de produção, você pode utilizar Docker e orquestradores como Portainer ou EasyPanel.

*   **Deploy no GitHub**: Siga as instruções em [`docs/github_instructions.md`](./docs/github_instructions.md) para subir o projeto no seu repositório GitHub.
*   **Deploy com Portainer**: Siga as instruções em [`docs/portainer_deploy_instructions.md`](./docs/portainer_deploy_instructions.md).
*   **Deploy com EasyPanel**: Siga as instruções em [`docs/easypanel_deploy_instructions.md`](./docs/easypanel_deploy_instructions.md).

---
