# Sistema de Menus Dinâmicos - MedControl

## 📋 Visão Geral

Sistema completo de gerenciamento de menus hierárquicos com controle de permissões por role.

## 🎯 Funcionalidades

- ✅ Menus hierárquicos (suporte a submenus)
- ✅ Controle de acesso por role (USER, ADMIN)
- ✅ Ordenação customizável
- ✅ Ativar/Desativar menus
- ✅ Ícones do Lucide React
- ✅ CRUD completo para admins
- ✅ Endpoint `/my-menus` para usuários

## 📁 Arquivos Criados

### Backend
```
app/
├── models/
│   └── menu_item.py          # Model com hierarquia
├── schemas/
│   └── menu_schema.py        # Schemas Pydantic
└── api/
    └── menu_routes.py        # Endpoints REST

scripts/
├── seed_menus.py             # Seeder Python
└── seed_menus.sql            # Seeder SQL
```

## 🚀 Deploy e Configuração

### 1. Criar Tabela no Banco

**Opção A: Deixar o SQLAlchemy criar (recomendado)**
```bash
# A tabela será criada automaticamente no próximo deploy
# O SQLAlchemy usa Base.metadata.create_all() no main.py
```

**Opção B: Criar manualmente via SQL**
```sql
CREATE TABLE menu_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    label VARCHAR(100) NOT NULL,
    icon VARCHAR(50),
    "to" VARCHAR(255),
    "order" INTEGER DEFAULT 0 NOT NULL,
    roles TEXT[] NOT NULL DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    parent_id UUID REFERENCES menu_items(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_menu_items_parent ON menu_items(parent_id);
CREATE INDEX idx_menu_items_order ON menu_items("order");
```

### 2. Popular Menus Iniciais

**Opção A: Via Script Python (após deploy)**
```bash
# SSH no Render ou execute localmente
python scripts/seed_menus.py
```

**Opção B: Via SQL no Supabase**
```bash
# Copie o conteúdo de scripts/seed_menus.sql
# Execute no SQL Editor do Supabase
```

### 3. Deploy no Render

```bash
git add .
git commit -m "feat: Sistema de menus dinâmicos"
git push origin main
```

O Render vai:
1. Instalar dependências
2. Criar a tabela `menu_items` automaticamente
3. Iniciar a API

Depois do deploy, execute o seeder para popular os menus.

## 📡 Endpoints Disponíveis

### Para Usuários Comuns

#### GET `/api/menus/my-menus`
Retorna os menus que o usuário tem permissão de ver (hierárquico)

**Response:**
```json
[
  {
    "id": "uuid",
    "label": "Dashboard",
    "icon": "LayoutDashboard",
    "to": "/dashboard",
    "order": 1,
    "roles": ["USER", "ADMIN"],
    "is_active": true,
    "parent_id": null,
    "children": [],
    "created_at": "2025-01-07T20:00:00",
    "updated_at": "2025-01-07T20:00:00"
  },
  {
    "id": "uuid",
    "label": "Médicos",
    "icon": "Stethoscope",
    "to": null,
    "order": 2,
    "roles": ["USER", "ADMIN"],
    "is_active": true,
    "parent_id": null,
    "children": [
      {
        "id": "uuid",
        "label": "Listar Médicos",
        "icon": "List",
        "to": "/medicos",
        "order": 1,
        "roles": ["USER", "ADMIN"],
        "is_active": true,
        "parent_id": "parent-uuid",
        "children": []
      }
    ]
  }
]
```

### Para Administradores

#### GET `/api/menus`
Lista todos os menus (flat list)

**Query Params:**
- `skip`: int (default: 0)
- `limit`: int (default: 100)
- `search`: string (opcional)
- `show_inactive`: bool (default: false)

#### GET `/api/menus/tree`
Árvore completa de menus

**Query Params:**
- `show_inactive`: bool (default: false)

#### GET `/api/menus/{menu_id}`
Detalhes de um menu específico

#### POST `/api/menus`
Criar novo menu

**Body:**
```json
{
  "label": "Relatórios",
  "icon": "FileBarChart",
  "to": "/relatorios",
  "order": 7,
  "roles": ["ADMIN"],
  "is_active": true,
  "parent_id": null
}
```

#### PUT `/api/menus/{menu_id}`
Atualizar menu existente

**Body:** (todos os campos opcionais)
```json
{
  "label": "Novo Nome",
  "is_active": false
}
```

#### DELETE `/api/menus/{menu_id}`
Deletar menu (cascade nos filhos)

## 🔐 Sistema de Permissões

### Roles Disponíveis
- `USER`: Usuário comum (acesso básico)
- `ADMIN`: Administrador (acesso total)

### Como Funciona

1. Cada menu tem um array de `roles` permitidos
2. Se `roles` estiver vazio `[]`, **todos** podem ver
3. O usuário precisa ter pelo menos um dos roles listados
4. Admins automaticamente têm role `ADMIN` + `USER`
5. Usuários comuns têm apenas role `USER`

### Exemplo de Controle

```json
{
  "label": "Configurações",
  "roles": ["ADMIN"]           // Apenas admins veem
}

{
  "label": "Dashboard", 
  "roles": ["USER", "ADMIN"]   // Todos veem
}

{
  "label": "Relatórios Públicos",
  "roles": []                  // Todos veem (sem restrição)
}
```

## 🎨 Ícones Disponíveis

Todos os ícones do **Lucide React** são suportados. Principais usados:

```javascript
// Já mapeados no frontend
LayoutDashboard  // Dashboard
Stethoscope      // Médicos
Users            // Pacientes  
FileText         // Procedimentos
List             // Listagens
PlusCircle       // Adicionar
UserPlus         // Novo usuário
UserCog          // Gerenciar usuário
FolderCog        // Configurações de pasta
Upload           // Import
Settings         // Configurações
```

## 🔧 Frontend - Ajustes Necessários

O frontend **já está pronto** para usar o sistema! Só precisa garantir que:

### 1. Service está configurado
```typescript
// src/services/menu.service.ts
export const menuService = {
  async getMyMenus() {
    const response = await api.get('/menus/my-menus');
    return response.data;
  }
};
```

### 2. Types estão definidos
```typescript
// src/types/index.ts
export interface MenuItem {
  id: string;
  label: string;
  icon?: string;
  to?: string;
  order: number;
  roles: string[];
  is_active: boolean;
  parent_id?: string;
  children?: MenuItem[];
}
```

## 📊 Estrutura dos Menus Iniciais

```
📊 Dashboard
👨‍⚕️ Médicos
    └── 📋 Listar Médicos
    └── ➕ Novo Médico (ADMIN)
👥 Pacientes
    └── 📋 Listar Pacientes
    └── ➕ Novo Paciente (ADMIN)
📄 Procedimentos
    └── 📋 Listar Procedimentos
    └── ➕ Novo Procedimento (ADMIN)
    └── 📁 Tipos de Procedimento (ADMIN)
📤 Importar (ADMIN)
⚙️ Configurações (ADMIN)
```

## 🧪 Testando

### 1. Testar como Usuário Comum
```bash
# Login com usuário não-admin
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "senha123"
}

# Ver menus disponíveis
GET /api/menus/my-menus
# Deve retornar apenas menus com role USER
```

### 2. Testar como Admin
```bash
# Login com admin
POST /api/auth/login
{
  "email": "admin@medcontrol.com",
  "password": "admin123"
}

# Ver todos os menus
GET /api/menus/tree
# Deve retornar TODOS os menus
```

## 🚨 Troubleshooting

### Menus não aparecem no frontend
1. Verificar se o seeder foi executado: `SELECT COUNT(*) FROM menu_items;`
2. Verificar se o endpoint `/my-menus` está retornando dados
3. Verificar console do browser por erros
4. Verificar se o token JWT é válido

### Erro 403 ao acessar endpoints admin
1. Verificar se o usuário tem `is_admin = true`
2. Testar com o usuário admin padrão
3. Verificar os roles no token JWT

### Submenus não aparecem
1. Verificar se `parent_id` está correto
2. Verificar se o menu pai está ativo
3. Verificar se o usuário tem permissão no submenu

## 🎯 Próximos Passos

### Futuras Melhorias
- [ ] Cache de menus no Redis
- [ ] Versionamento de menus
- [ ] Audit log de mudanças
- [ ] Import/Export de configurações
- [ ] Menus personalizados por usuário
- [ ] Badges/contadores nos menus
- [ ] Menus favoritos

## 📚 Referências

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Relationships](https://docs.sqlalchemy.org/en/14/orm/relationships.html)
- [Lucide Icons](https://lucide.dev/)

---

**Desenvolvido para MedControl** 🏥
