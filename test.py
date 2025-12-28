from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash do banco
stored_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr9O.XVCq"

# Testar
result = pwd_context.verify("admin123", stored_hash)
print(f"Hash no banco funciona? {result}")

if not result:
    # Gerar novo hash
    new_hash = pwd_context.hash("admin123")
    print(f"\nNovo hash gerado: {new_hash}")
    
    # Testar novo hash
    test_new = pwd_context.verify("admin123", new_hash)
    print(f"Novo hash funciona? {test_new}")