# 🐍 MedControl API - Backend FastAPI

Backend REST API para o sistema MedControl, desenvolvido com FastAPI + PostgreSQL.

---

## 🚀 Início Rápido

### 1️⃣ **Pré-requisitos**

- Python 3.10+
- PostgreSQL 14+
- pip ou poetry

### 2️⃣ **Criar Banco de Dados**

```sql
-- Conectar ao PostgreSQL
psql -U postgres

-- Criar banco
CREATE DATABASE medcontrol;

-- Conectar ao banco
\c medcontrol

-- Criar tabela de usuários
\i scripts/create_users_table.sql

-- Ou copiar e colar o conteúdo do arquivo
```

### 3️⃣ **Configurar Ambiente Virtual**

```bash
# Criar venv
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Linux/Mac)
source venv/bin/activate
```

### 4️⃣ **Instalar Dependências**

```bash
pip install -r requirements.txt
```

### 5️⃣ **Configurar Variáveis de Ambiente**

Copie `.env.example` para `.env` e ajuste:

```bash
cp .env.example .env
```

Edite `.env`:
```env
DATABASE_URL=postgresql://postgres:SUA_SENHA@localhost:5432/medcontrol
SECRET_KEY=gere-uma-chave-segura-aqui
```

**Gerar SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 6️⃣ **Criar Usuário Inicial**

```bash
python scripts/create_user.py
```

Ou com argumentos:
```bash
python scripts/create_user.py \
  --email admin@medcontrol.com \
  --name "Administrador" \
  --password admin123 \
  --admin
```

### 7️⃣ **Rodar o Servidor**

```bash
# Modo desenvolvimento (com reload)
uvicorn app.main:app --reload --port 8000

# Ou
python app/main.py
```

Acesse: **http://localhost:8000**

---

## 📚 **Documentação da API**

Após iniciar o servidor:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

---

## 🔐 **Endpoints de Autenticação**

### **POST /api/auth/login**

Login do usuário.

**Request:**
```json
{
  "username": "admin@medcontrol.com",
  "password": "admin123"
}
```

**Response (200):**
```json
{
  "accessToken": "eyJhbGc...",
  "refreshToken": null,
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "admin@medcontrol.com",
    "name": "Administrador",
    "roles": ["ADMIN", "USER"],
    "avatar": null
  }
}
```

**Response (401):**
```json
{
  "detail": "Email ou senha incorretos"
}
```

---

### **GET /api/auth/me**

Retorna dados do usuário logado.

**Headers:**
```
Authorization: Bearer eyJhbGc...
```

**Response (200):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "admin@medcontrol.com",
  "name": "Administrador",
  "roles": ["ADMIN", "USER"],
  "avatar": null
}
```

**Response (401):**
```json
{
  "detail": "Could not validate credentials"
}
```

---

### **POST /api/auth/logout**

Logout do usuário (simbólico, JWT é stateless).

**Response (200):**
```json
{
  "message": "Logout successful"
}
```

---

## 🧪 **Testando a API**

### **Com cURL**

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@medcontrol.com","password":"admin123"}'

# Me (com token)
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### **Com HTTPie**

```bash
# Login
http POST :8000/api/auth/login username=admin@medcontrol.com password=admin123

# Me
http :8000/api/auth/me "Authorization: Bearer SEU_TOKEN"
```

### **Com Swagger UI**

1. Acesse http://localhost:8000/api/docs
2. Clique em **POST /api/auth/login**
3. Clique em "Try it out"
4. Preencha credenciais
5. Execute
6. Copie o `accessToken` da resposta
7. Clique no botão **Authorize** (🔒) no topo
8. Cole o token: `Bearer SEU_TOKEN`
9. Agora pode testar os outros endpoints!

---

## 🔗 **Integrando com Frontend**

### **1. Alterar URL no Frontend**

No projeto React, edite `.env`:

```env
VITE_USE_MOCKS=false
VITE_API_BASE_URL=http://localhost:8000/api
```

### **2. Reiniciar Frontend**

```bash
npm run dev
```

### **3. Testar Login**

- Acesse http://localhost:5173
- Faça login com: `admin@medcontrol.com` / `admin123`
- Deve funcionar! ✅

---

## 📁 **Estrutura do Projeto**

```
medcontrol-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # App FastAPI
│   ├── database.py          # SQLAlchemy setup
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py          # Model User
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── auth.py          # Pydantic schemas
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py          # Dependencies (get_current_user)
│   │   └── auth.py          # Rotas /auth/*
│   └── core/
│       ├── __init__.py
│       ├── config.py        # Settings
│       └── security.py      # JWT, hash
├── scripts/
│   ├── create_users_table.sql
│   └── create_user.py
├── requirements.txt
├── .env
├── .env.example
└── README.md
```

---

## 🛠️ **Comandos Úteis**

```bash
# Criar novo usuário
python scripts/create_user.py

# Rodar servidor (dev)
uvicorn app.main:app --reload

# Rodar servidor (produção)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Ver logs SQL (no .env: DEBUG=True)
```

---

## 🐛 **Troubleshooting**

### Erro: "could not connect to server"

**Causa**: PostgreSQL não está rodando

**Solução:**
```bash
# Windows (buscar no menu)
pg_ctl start

# Linux
sudo service postgresql start

# Mac
brew services start postgresql
```

---

### Erro: "database does not exist"

**Causa**: Banco `medcontrol` não foi criado

**Solução:**
```sql
psql -U postgres
CREATE DATABASE medcontrol;
```

---

### Erro: "relation users does not exist"

**Causa**: Tabela não foi criada

**Solução:**
```bash
# Executar script SQL
psql -U postgres -d medcontrol -f scripts/create_users_table.sql

# Ou rodar create_user.py que cria automaticamente
python scripts/create_user.py
```

---

### Erro: "ModuleNotFoundError"

**Causa**: Dependências não instaladas

**Solução:**
```bash
pip install -r requirements.txt
```

---

### CORS Error no Frontend

**Causa**: CORS não configurado

**Solução:** Verificar `.env`:
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 🔒 **Segurança**

### **Em Produção:**

1. **Mudar SECRET_KEY**: Gerar chave forte e aleatória
2. **HTTPS**: Usar certificado SSL/TLS
3. **Banco seguro**: Não usar senha padrão do postgres
4. **Rate limiting**: Implementar limite de requisições
5. **DEBUG=False**: Desabilitar modo debug

---

## 📊 **Próximos Endpoints (TODO)**

- [ ] CRUD de Médicos
- [ ] CRUD de Pacientes
- [ ] CRUD de Tipos de Procedimento
- [ ] CRUD de Procedimentos
- [ ] Import de CSV
- [ ] Dashboard stats
- [ ] Menu dinâmico

---

## 📝 **Licença**

Projeto interno - MedControl

---

**Desenvolvido com FastAPI + PostgreSQL** 🐍🐘
