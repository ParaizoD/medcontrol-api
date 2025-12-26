-- ============================================
-- MEDCONTROL - SCRIPT DE CRIAÇÃO DE TABELAS
-- ============================================

-- 1. TABELA DE MÉDICOS
CREATE TABLE IF NOT EXISTS medicos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) NOT NULL,
    crm VARCHAR(50),
    especialidade VARCHAR(100),
    email VARCHAR(255),
    telefone VARCHAR(20),
    ativo BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_medicos_nome ON medicos(nome);
CREATE INDEX idx_medicos_crm ON medicos(crm);

COMMENT ON TABLE medicos IS 'Cadastro de médicos';
COMMENT ON COLUMN medicos.nome IS 'Nome completo do médico';
COMMENT ON COLUMN medicos.crm IS 'Número do CRM com UF (ex: 12345-SP)';
COMMENT ON COLUMN medicos.especialidade IS 'Especialidade médica';


-- 2. TABELA DE PACIENTES
CREATE TABLE IF NOT EXISTS pacientes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) NOT NULL,
    cpf VARCHAR(14),
    data_nascimento DATE,
    telefone VARCHAR(20),
    email VARCHAR(255),
    endereco TEXT,
    observacoes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pacientes_nome ON pacientes(nome);
CREATE INDEX idx_pacientes_cpf ON pacientes(cpf);

COMMENT ON TABLE pacientes IS 'Cadastro de pacientes';
COMMENT ON COLUMN pacientes.nome IS 'Nome completo do paciente';
COMMENT ON COLUMN pacientes.cpf IS 'CPF formatado (xxx.xxx.xxx-xx)';


-- 3. TABELA DE TIPOS DE PROCEDIMENTO
CREATE TABLE IF NOT EXISTS tipos_procedimento (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) NOT NULL UNIQUE,
    descricao TEXT,
    valor_referencia DECIMAL(10, 2) DEFAULT 0.00,
    ativo BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tipos_procedimento_nome ON tipos_procedimento(nome);

COMMENT ON TABLE tipos_procedimento IS 'Tipos de procedimentos médicos';
COMMENT ON COLUMN tipos_procedimento.nome IS 'Nome do tipo (ex: Consulta, Exame, Cirurgia)';
COMMENT ON COLUMN tipos_procedimento.valor_referencia IS 'Valor de referência em reais';


-- 4. TABELA DE PROCEDIMENTOS
CREATE TABLE IF NOT EXISTS procedimentos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data DATE NOT NULL,
    tipo_id UUID NOT NULL REFERENCES tipos_procedimento(id) ON DELETE RESTRICT,
    medico_id UUID NOT NULL REFERENCES medicos(id) ON DELETE RESTRICT,
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE RESTRICT,
    observacoes TEXT,
    valor DECIMAL(10, 2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_procedimentos_data ON procedimentos(data DESC);
CREATE INDEX idx_procedimentos_tipo_id ON procedimentos(tipo_id);
CREATE INDEX idx_procedimentos_medico_id ON procedimentos(medico_id);
CREATE INDEX idx_procedimentos_paciente_id ON procedimentos(paciente_id);

COMMENT ON TABLE procedimentos IS 'Registro de procedimentos realizados';
COMMENT ON COLUMN procedimentos.data IS 'Data de realização do procedimento';
COMMENT ON COLUMN procedimentos.valor IS 'Valor cobrado pelo procedimento';


-- ============================================
-- DADOS INICIAIS (OPCIONAL)
-- ============================================

-- Inserir alguns tipos de procedimento padrão
INSERT INTO tipos_procedimento (nome, descricao, valor_referencia) VALUES
    ('Consulta', 'Consulta médica padrão', 200.00),
    ('Retorno', 'Consulta de retorno', 100.00),
    ('Exame', 'Exame médico', 150.00),
    ('Cirurgia', 'Procedimento cirúrgico', 0.00)
ON CONFLICT (nome) DO NOTHING;


-- ============================================
-- VERIFICAÇÃO
-- ============================================

-- Ver todas as tabelas criadas
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Contar registros
SELECT 
    (SELECT COUNT(*) FROM users) as usuarios,
    (SELECT COUNT(*) FROM medicos) as medicos,
    (SELECT COUNT(*) FROM pacientes) as pacientes,
    (SELECT COUNT(*) FROM tipos_procedimento) as tipos,
    (SELECT COUNT(*) FROM procedimentos) as procedimentos;
