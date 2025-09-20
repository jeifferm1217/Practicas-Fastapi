# Crear archivo test_auth.py para probar
from auth import hash_password, verify_password, create_access_token, verify_token

def test_password_hashing():
    password = "mi_password_123"

    # Hashear password
    hashed = hash_password(password)
    print(f"Password original: {password}")
    print(f"Password hasheado: {hashed}")

    # Verificar password
    is_valid = verify_password(password, hashed)
    print(f"Password es válido: {is_valid}")

    # Verificar password incorrecto
    is_invalid = verify_password("password_incorrecto", hashed)
    print(f"Password incorrecto es válido: {is_invalid}")

def test_jwt_tokens():
    username = "juan123"

    # Crear token
    token = create_access_token(username)
    print(f"Token creado: {token}")

    # Verificar token
    decoded_username = verify_token(token)
    print(f"Username desde token: {decoded_username}")

if __name__ == "__main__":
    print("=== Test Password Hashing ===")
    test_password_hashing()

    print("\n=== Test JWT Tokens ===")
    test_jwt_tokens()