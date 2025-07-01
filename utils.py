import bcrypt

def hash_senha(senha):
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode("utf-8")

def verificar_senha(senha, hash_salvo):
    # Garante que hash_salvo é bytes
    if isinstance(hash_salvo, str):
        hash_salvo = hash_salvo.encode("utf-8")
    return bcrypt.checkpw(senha.encode(), hash_salvo)