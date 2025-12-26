# 🚀 Guia de Setup - Sistema de Import

## 📋 **Passo a Passo**

### **1️⃣ Criar Tabelas no Supabase**

1. Acesse seu projeto no Supabase
2. Vá em **SQL Editor**
3. Clique em **New query**
4. Copie e cole TODO o conteúdo de `scripts/create_tables.sql`
5. Clique em **RUN** (canto inferior direito)

**Verificação:**
- No SQL Editor, execute: `SELECT * FROM tipos_procedimento;`
- Deve mostrar 4 tipos: Consulta, Retorno, Exame, Cirurgia

### **2️⃣ Reiniciar o Backend**

```powershell
# Parar o servidor (Ctrl+C)
# Rodar novamente
uvicorn app.main:app --reload
```

**O que acontece:**
- SQLAlchemy cria automaticamente as tabelas (caso não existam)
- Novos endpoints são registrados

### **3️⃣ Testar no Swagger**

Acesse: **http://localhost:8000/api/docs**

Deve ver novo endpoint:
- `POST /api/import/procedimentos`

**Teste básico:**

1. Clique em **Authorize** (🔒)
2. Cole seu token JWT
3. Clique em `POST /api/import/procedimentos`
4. "Try it out"
5. Cole este exemplo:

```json
{
  "rows": [
    {
      "data": "2024-01-15",
      "nomeProcedimento": "Consulta",
      "nomeMedicos": "Dr. João Silva",
      "nomePaciente": "Maria Santos"
    },
    {
      "data": "16/01/2024",
      "nomeProcedimento": "Exame",
      "nomeMedicos": "Dr. João Silva",
      "nomePaciente": "José Oliveira"
    }
  ]
}
```

6. Execute

**Resposta esperada:**
```json
{
  "success": 2,
  "errors": [],
  "created": {
    "medicos": 1,
    "pacientes": 2,
    "tiposProcedimento": 0,
    "procedimentos": 2
  },
  "warnings": [
    "1 médico(s) foram criados automaticamente. Edite os registros para adicionar CRM e especialidade.",
    "2 paciente(s) foram criados automaticamente. Complete os dados cadastrais (CPF, telefone, etc)."
  ]
}
```

### **4️⃣ Verificar Dados no Supabase**

No **Table Editor**:
- Tabela `medicos` → deve ter 1 registro (Dr. João Silva)
- Tabela `pacientes` → deve ter 2 registros
- Tabela `procedimentos` → deve ter 2 registros

---

## 🎯 **Testar com Frontend**

### **1. Preparar CSV**

Crie um arquivo `teste.csv`:

```csv
data,nome do procedimento,nome dos medicos,nome do paciente
2024-01-15,Consulta,Dr. Carlos Silva,Maria Santos
2024-01-16,Exame,Dr. Carlos Silva,José Oliveira
2024-01-20,Consulta,Dra. Ana Paula,Maria Santos
2024-02-05,Cirurgia,Dr. Roberto Mendes,Ana Costa
```

### **2. Fazer Upload**

1. Acesse: http://localhost:5173/app/import
2. Faça upload do `teste.csv`
3. Clique em **Validar Dados**
4. Revise o preview
5. Clique em **Importar X Registros**

**Resultado:**
- ✅ 4 procedimentos criados
- ✅ 3 médicos criados
- ✅ 3 pacientes criados
- ✅ Dados aparecem no Supabase

---

## 📊 **Como Funciona**

### **Lógica de Importação**

Para cada linha do CSV:

```
1. Converter data (DD/MM/YYYY ou YYYY-MM-DD)
   ↓
2. Buscar/Criar Médico
   - Busca por nome (case-insensitive)
   - Se não existe → cria com CRM = null
   ↓
3. Buscar/Criar Paciente
   - Busca por nome (case-insensitive)
   - Se não existe → cria básico
   ↓
4. Buscar/Criar Tipo
   - Busca por nome (case-insensitive)
   - Se não existe → cria com valor = 0
   ↓
5. Criar Procedimento
   - Vincula IDs de médico, paciente e tipo
   - Registra data
   ↓
6. Retornar Estatísticas
```

### **Critérios de Busca**

**Médico:** Nome exato (ignorando maiúsculas/minúsculas)
- "Dr. João Silva" = "dr. joão silva" = "DR. JOÃO SILVA"

**Paciente:** Nome exato (ignorando maiúsculas/minúsculas)

**Tipo:** Nome exato (ignorando maiúsculas/minúsculas)

**⚠️ IMPORTANTE:** Se você escrever o nome do mesmo médico de formas diferentes, ele será duplicado!
- "Dr. João Silva" ≠ "Dr João Silva" (sem ponto)
- "Dr. João Silva" ≠ "João Silva" (sem Dr.)

**Padronize os nomes no CSV antes de importar!**

---

## 🔧 **Formatos Aceitos**

### **Data**
- `YYYY-MM-DD` → `2024-01-15` ✅
- `DD/MM/YYYY` → `15/01/2024` ✅
- Outros formatos → ❌ Erro

### **CSV**
- Separadores: `,` (vírgula), `;` (ponto-vírgula), `TAB`
- Encoding: UTF-8
- Headers obrigatórios:
  - `data`
  - `nome do procedimento` (ou `procedimento`)
  - `nome dos medicos` (ou `medico`)
  - `nome do paciente` (ou `paciente`)

---

## 🐛 **Solução de Problemas**

### Erro: "relation does not exist"

**Causa:** Tabelas não foram criadas

**Solução:**
```sql
-- Executar no Supabase SQL Editor
\i scripts/create_tables.sql
```

### Erro: "foreign key constraint"

**Causa:** Banco com dados inconsistentes

**Solução:** Limpar e recriar
```sql
DROP TABLE IF EXISTS procedimentos CASCADE;
DROP TABLE IF EXISTS medicos CASCADE;
DROP TABLE IF EXISTS pacientes CASCADE;
DROP TABLE IF EXISTS tipos_procedimento CASCADE;

-- Depois rodar create_tables.sql novamente
```

### Médicos/Pacientes Duplicados

**Causa:** Nomes escritos de formas diferentes

**Solução:** 
1. Padronize CSV antes de importar
2. Limpe duplicatas no Supabase manualmente
3. Reimporte

### Import muito lento

**Causa:** Muitos registros (>1000)

**Solução:** 
- Divida CSV em arquivos menores
- Importe em lotes de 500-1000 registros

---

## 📈 **Próximos Passos**

Após importar os dados:

1. **Editar Médicos**
   - Adicionar CRM
   - Adicionar especialidade
   - Adicionar contato

2. **Completar Pacientes**
   - Adicionar CPF
   - Adicionar data de nascimento
   - Adicionar telefone

3. **Configurar Tipos**
   - Definir valores de referência
   - Adicionar descrições

4. **Ver Dashboard**
   - Estatísticas atualizadas
   - Gráficos com dados reais

---

## ✅ **Checklist de Sucesso**

```
□ Tabelas criadas no Supabase
□ Backend rodando sem erros
□ Endpoint /api/import/procedimentos aparece no Swagger
□ Teste no Swagger retorna success
□ Dados aparecem no Supabase Table Editor
□ Frontend faz upload e valida CSV
□ Import via frontend funciona
□ Dados importados visíveis no sistema
```

---

**Está tudo pronto para importar seus dados reais!** 🎉
