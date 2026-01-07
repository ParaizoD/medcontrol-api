-- Script SQL para popular menus iniciais
-- Pode ser executado diretamente no PostgreSQL/Supabase

-- Criar extensão UUID se não existir
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Limpar menus existentes (cuidado em produção!)
-- TRUNCATE TABLE menu_items CASCADE;

-- Inserir menus principais
INSERT INTO menu_items (id, label, icon, "to", "order", roles, is_active, parent_id, created_at, updated_at)
VALUES 
    -- Dashboard
    (uuid_generate_v4(), 'Dashboard', 'LayoutDashboard', '/dashboard', 1, ARRAY['USER', 'ADMIN'], true, NULL, NOW(), NOW()),
    
    -- Médicos (menu pai)
    (uuid_generate_v4(), 'Médicos', 'Stethoscope', NULL, 2, ARRAY['USER', 'ADMIN'], true, NULL, NOW(), NOW()),
    
    -- Pacientes (menu pai)
    (uuid_generate_v4(), 'Pacientes', 'Users', NULL, 3, ARRAY['USER', 'ADMIN'], true, NULL, NOW(), NOW()),
    
    -- Procedimentos (menu pai)
    (uuid_generate_v4(), 'Procedimentos', 'FileText', NULL, 4, ARRAY['USER', 'ADMIN'], true, NULL, NOW(), NOW()),
    
    -- Importar
    (uuid_generate_v4(), 'Importar', 'Upload', '/import', 5, ARRAY['ADMIN'], true, NULL, NOW(), NOW()),
    
    -- Configurações
    (uuid_generate_v4(), 'Configurações', 'Settings', '/settings', 6, ARRAY['ADMIN'], true, NULL, NOW(), NOW());


-- Inserir submenus de Médicos
INSERT INTO menu_items (id, label, icon, "to", "order", roles, is_active, parent_id, created_at, updated_at)
SELECT 
    uuid_generate_v4(),
    'Listar Médicos',
    'List',
    '/medicos',
    1,
    ARRAY['USER', 'ADMIN'],
    true,
    id,
    NOW(),
    NOW()
FROM menu_items WHERE label = 'Médicos';

INSERT INTO menu_items (id, label, icon, "to", "order", roles, is_active, parent_id, created_at, updated_at)
SELECT 
    uuid_generate_v4(),
    'Novo Médico',
    'UserPlus',
    '/medicos/novo',
    2,
    ARRAY['ADMIN'],
    true,
    id,
    NOW(),
    NOW()
FROM menu_items WHERE label = 'Médicos';


-- Inserir submenus de Pacientes
INSERT INTO menu_items (id, label, icon, "to", "order", roles, is_active, parent_id, created_at, updated_at)
SELECT 
    uuid_generate_v4(),
    'Listar Pacientes',
    'List',
    '/pacientes',
    1,
    ARRAY['USER', 'ADMIN'],
    true,
    id,
    NOW(),
    NOW()
FROM menu_items WHERE label = 'Pacientes';

INSERT INTO menu_items (id, label, icon, "to", "order", roles, is_active, parent_id, created_at, updated_at)
SELECT 
    uuid_generate_v4(),
    'Novo Paciente',
    'UserPlus',
    '/pacientes/novo',
    2,
    ARRAY['ADMIN'],
    true,
    id,
    NOW(),
    NOW()
FROM menu_items WHERE label = 'Pacientes';


-- Inserir submenus de Procedimentos
INSERT INTO menu_items (id, label, icon, "to", "order", roles, is_active, parent_id, created_at, updated_at)
SELECT 
    uuid_generate_v4(),
    'Listar Procedimentos',
    'List',
    '/procedimentos',
    1,
    ARRAY['USER', 'ADMIN'],
    true,
    id,
    NOW(),
    NOW()
FROM menu_items WHERE label = 'Procedimentos';

INSERT INTO menu_items (id, label, icon, "to", "order", roles, is_active, parent_id, created_at, updated_at)
SELECT 
    uuid_generate_v4(),
    'Novo Procedimento',
    'PlusCircle',
    '/procedimentos/novo',
    2,
    ARRAY['ADMIN'],
    true,
    id,
    NOW(),
    NOW()
FROM menu_items WHERE label = 'Procedimentos';

INSERT INTO menu_items (id, label, icon, "to", "order", roles, is_active, parent_id, created_at, updated_at)
SELECT 
    uuid_generate_v4(),
    'Tipos de Procedimento',
    'FolderCog',
    '/procedimentos/tipos',
    3,
    ARRAY['ADMIN'],
    true,
    id,
    NOW(),
    NOW()
FROM menu_items WHERE label = 'Procedimentos';


-- Verificar resultado
SELECT 
    id,
    label,
    icon,
    "to",
    "order",
    roles,
    is_active,
    parent_id,
    created_at
FROM menu_items
ORDER BY parent_id NULLS FIRST, "order";
