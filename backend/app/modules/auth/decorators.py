from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def admin_required():
    """
    Um decorador personalizado que verifica se o usuário logado
    tem a claim 'is_admin' definida como True no seu token JWT.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request() # Verifica se o token é válido
            claims = get_jwt() # Pega os dados do token

            if claims.get("is_admin", False):
                return fn(*args, **kwargs) # Permite a passagem
            else:
                return jsonify({"error": "Acesso restrito a administradores"}), 403 # 403 Forbidden
        return decorator
    return wrapper