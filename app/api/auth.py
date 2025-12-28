from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, UserResponse
from app.core.security import verify_password, create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login do usuário
    
    - **email**: email do usuário
    - **password**: senha
    
    Retorna token JWT e dados do usuário
    """
    
    print(f"🔍 DEBUG: Tentativa de login com email: {credentials.email}")
    
    # Buscar usuário por email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    print(f"🔍 DEBUG: Usuário encontrado? {user is not None}")
    
    # Validações
    if not user:
        print(f"❌ DEBUG: Usuário não encontrado no banco")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    print(f"🔍 DEBUG: Email do usuário: {user.email}")
    print(f"🔍 DEBUG: Hash no banco: {user.hashed_password[:30]}...")
    print(f"🔍 DEBUG: Senha recebida: {credentials.password}")
    
    # Verificar senha
    password_valid = verify_password(credentials.password, user.hashed_password)
    print(f"🔍 DEBUG: Senha válida? {password_valid}")
    
    if not password_valid:
        print(f"❌ DEBUG: Senha incorreta!")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    print(f"🔍 DEBUG: is_active? {user.is_active}")
    
    if not user.is_active:
        print(f"❌ DEBUG: Usuário inativo")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    # Criar token JWT
    print(f"✅ DEBUG: Criando token...")
    access_token = create_access_token(data={"sub": user.email})
    
    print(f"✅ DEBUG: Login bem-sucedido!")
    
    # Retornar resposta
    return LoginResponse(
        accessToken=access_token,
        user=UserResponse.from_user(user)
    )


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    Logout do usuário
    
    Nota: Com JWT, o logout é feito no client removendo o token.
    Este endpoint existe apenas para compatibilidade.
    """
    return {"message": "Logout successful"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Retorna dados do usuário logado
    """
    return UserResponse.from_user(current_user)
