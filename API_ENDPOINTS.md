# 📊 API de Visualização - Endpoints

## 🏥 **Médicos**

### **GET /api/medicos**
Lista todos os médicos

**Query Parameters:**
- `skip` (int): Pular N registros (default: 0)
- `limit` (int): Limitar resultados (default: 100, max: 500)
- `search` (string): Buscar por nome ou CRM

**Exemplo:**
```bash
GET /api/medicos?search=João&limit=10
```

**Resposta:**
```json
[
  {
    "id": "uuid",
    "nome": "Dr. João Silva",
    "crm": "12345-SP",
    "especialidade": "Cardiologia"
  }
]
```

---

### **GET /api/medicos/{id}**
Detalhes de um médico + estatísticas

**Resposta:**
```json
{
  "id": "uuid",
  "nome": "Dr. João Silva",
  "crm": "12345-SP",
  "especialidade": "Cardiologia",
  "email": "joao@email.com",
  "telefone": "(11) 99999-9999",
  "ativo": true,
  "created_at": "2024-01-15T10:00:00",
  "stats": {
    "total_procedimentos": 150,
    "ultima_atividade": "2024-12-20"
  }
}
```

---

### **GET /api/medicos/{id}/procedimentos**
Lista procedimentos de um médico

**Query Parameters:**
- `skip` (int): Paginação
- `limit` (int): Limite (max: 200)

**Resposta:**
```json
{
  "medico": {
    "id": "uuid",
    "nome": "Dr. João Silva"
  },
  "procedimentos": [
    {
      "id": "uuid",
      "data": "2024-01-15",
      "tipo": "Consulta",
      "paciente": "Maria Santos",
      "valor": 200.00
    }
  ],
  "total": 150
}
```

---

## 👤 **Pacientes**

### **GET /api/pacientes**
Lista todos os pacientes

**Query Parameters:**
- `skip` (int): Paginação
- `limit` (int): Limite (max: 500)
- `search` (string): Buscar por nome ou CPF

**Exemplo:**
```bash
GET /api/pacientes?search=Maria&limit=20
```

---

### **GET /api/pacientes/{id}**
Detalhes de um paciente + estatísticas

**Resposta:**
```json
{
  "id": "uuid",
  "nome": "Maria Santos",
  "cpf": "123.456.789-00",
  "data_nascimento": "1980-05-15",
  "telefone": "(11) 98888-8888",
  "email": "maria@email.com",
  "endereco": "Rua ABC, 123",
  "observacoes": null,
  "created_at": "2024-01-15T10:00:00",
  "stats": {
    "total_procedimentos": 25,
    "ultima_visita": "2024-12-20"
  }
}
```

---

### **GET /api/pacientes/{id}/procedimentos**
Lista procedimentos de um paciente

---

## 📋 **Procedimentos**

### **GET /api/procedimentos**
Lista procedimentos com filtros

**Query Parameters:**
- `skip` (int): Paginação
- `limit` (int): Limite (max: 200)
- `data_inicio` (date): Filtrar a partir desta data (YYYY-MM-DD)
- `data_fim` (date): Filtrar até esta data (YYYY-MM-DD)
- `medico_id` (uuid): Filtrar por médico
- `paciente_id` (uuid): Filtrar por paciente
- `tipo_id` (uuid): Filtrar por tipo

**Exemplos:**
```bash
# Procedimentos de dezembro
GET /api/procedimentos?data_inicio=2024-12-01&data_fim=2024-12-31

# Procedimentos de um médico específico
GET /api/procedimentos?medico_id=uuid-do-medico

# Combinação de filtros
GET /api/procedimentos?data_inicio=2024-01-01&medico_id=uuid&limit=50
```

**Resposta:**
```json
{
  "procedimentos": [
    {
      "id": "uuid",
      "data": "2024-01-15",
      "tipo": {
        "id": "uuid",
        "nome": "Consulta",
        "valor_referencia": 200.00
      },
      "medico": {
        "id": "uuid",
        "nome": "Dr. João Silva",
        "crm": "12345-SP"
      },
      "paciente": {
        "id": "uuid",
        "nome": "Maria Santos"
      },
      "valor": 200.00,
      "observacoes": null
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 50
}
```

---

### **GET /api/procedimentos/{id}**
Detalhes completos de um procedimento

**Resposta:**
```json
{
  "id": "uuid",
  "data": "2024-01-15",
  "tipo": {
    "id": "uuid",
    "nome": "Consulta",
    "descricao": "Consulta médica padrão",
    "valor_referencia": 200.00
  },
  "medico": {
    "id": "uuid",
    "nome": "Dr. João Silva",
    "crm": "12345-SP",
    "especialidade": "Cardiologia",
    "email": "joao@email.com",
    "telefone": "(11) 99999-9999"
  },
  "paciente": {
    "id": "uuid",
    "nome": "Maria Santos",
    "cpf": "123.456.789-00",
    "telefone": "(11) 98888-8888",
    "email": "maria@email.com"
  },
  "valor": 200.00,
  "observacoes": null,
  "created_at": "2024-01-15T10:00:00"
}
```

---

## 📊 **Dashboard**

### **GET /api/dashboard/stats**
Estatísticas gerais do sistema

**Query Parameters:**
- `data_inicio` (date): Filtrar procedimentos
- `data_fim` (date): Filtrar procedimentos

**Exemplo:**
```bash
# Estatísticas gerais
GET /api/dashboard/stats

# Estatísticas de um período
GET /api/dashboard/stats?data_inicio=2024-01-01&data_fim=2024-12-31
```

**Resposta:**
```json
{
  "totais": {
    "medicos": 15,
    "pacientes": 120,
    "tipos_procedimento": 8,
    "procedimentos": 450,
    "procedimentos_mes_atual": 35,
    "valor_total": 90000.00
  },
  "top_medicos": [
    {
      "id": "uuid",
      "nome": "Dr. João Silva",
      "total_procedimentos": 150
    }
  ],
  "top_tipos": [
    {
      "id": "uuid",
      "nome": "Consulta",
      "total": 250
    }
  ],
  "procedimentos_por_mes": [
    {
      "ano": 2024,
      "mes": 7,
      "total": 45
    },
    {
      "ano": 2024,
      "mes": 8,
      "total": 52
    }
  ],
  "ultimos_procedimentos": [
    {
      "id": "uuid",
      "data": "2024-12-20",
      "tipo": "Consulta",
      "medico": "Dr. João Silva",
      "paciente": "Maria Santos",
      "valor": 200.00
    }
  ]
}
```

---

### **GET /api/dashboard/relatorio-mensal**
Relatório detalhado de um mês

**Query Parameters:**
- `ano` (int): Ano (2020-2100)
- `mes` (int): Mês (1-12)

**Exemplo:**
```bash
GET /api/dashboard/relatorio-mensal?ano=2024&mes=12
```

**Resposta:**
```json
{
  "periodo": {
    "ano": 2024,
    "mes": 12
  },
  "resumo": {
    "total_procedimentos": 35,
    "valor_total": 7000.00
  },
  "por_tipo": [
    {
      "tipo": "Consulta",
      "quantidade": 20,
      "valor": 4000.00
    },
    {
      "tipo": "Exame",
      "quantidade": 15,
      "valor": 3000.00
    }
  ],
  "por_medico": [
    {
      "medico": "Dr. João Silva",
      "quantidade": 18,
      "valor": 3600.00
    },
    {
      "medico": "Dra. Ana Paula",
      "quantidade": 17,
      "valor": 3400.00
    }
  ]
}
```

---

## 🔐 **Autenticação**

Todos os endpoints requerem autenticação via JWT token.

**Header necessário:**
```
Authorization: Bearer SEU_TOKEN_JWT
```

---

## 📖 **Swagger UI**

Acesse a documentação interativa em:
```
http://localhost:8000/api/docs
```

Lá você pode:
- ✅ Ver todos os endpoints
- ✅ Testar diretamente no navegador
- ✅ Ver exemplos de request/response
- ✅ Autorizar com seu token JWT

---

## 🎯 **Casos de Uso Comuns**

### **1. Dashboard Inicial**
```bash
GET /api/dashboard/stats
```

### **2. Buscar Médico**
```bash
GET /api/medicos?search=João
```

### **3. Ver Histórico do Paciente**
```bash
GET /api/pacientes/{id}/procedimentos
```

### **4. Procedimentos do Mês**
```bash
GET /api/procedimentos?data_inicio=2024-12-01&data_fim=2024-12-31
```

### **5. Relatório Mensal**
```bash
GET /api/dashboard/relatorio-mensal?ano=2024&mes=12
```

---

## ⚡ **Performance**

- Paginação padrão: 50-100 registros
- Máximo por requisição: 500 registros
- Índices no banco: data, médico_id, paciente_id, tipo_id
- Queries otimizadas com joins

---

## 🐛 **Códigos de Erro**

- `401`: Token inválido ou expirado
- `404`: Recurso não encontrado
- `422`: Parâmetros inválidos
- `500`: Erro interno do servidor
