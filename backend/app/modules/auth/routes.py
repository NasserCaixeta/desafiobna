from flask import request, jsonify
from . import auth_bp
from app.models import User
from app.extensions import db, bcrypt
from flask_jwt_extended import create_access_token
from sqlalchemy import exc

@auth_bp.route('/register', methods=['POST'])
def register_user():
    """
    Rota de registro pública.
    SÓ FUNCIONA se não houver NENHUM usuário no banco.
    O primeiro usuário a se registrar se torna admin.
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    # --- LÓGICA DE PRIMEIRO ADMIN ---
    # Verifica se já existe algum usuário no banco
    user_count = User.query.count()

    if user_count > 0:
        # Se já existem usuários, o registro público está fechado!
        return jsonify({
            "error": "Registro público desativado. Contate um administrador para criar sua conta."
        }), 403 # 403 Forbidden

    
    is_admin = True
    # --- FIM DA LÓGICA ---

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = User(
        email=email,
        password_hash=hashed_password,
        is_admin=is_admin # Será True
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            "message": f"Usuário Admin {email} criado com sucesso!",
            "is_admin": is_admin
        }), 201
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"Erro de banco de dados: {e}"}), 500

@auth_bp.route('/login', methods=['POST'])
def login_user():
    """
    Rota de login para todos os usuários (admin e vendas).
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    user = User.query.filter_by(email=email).first()

    # Verifica se o usuário existe E se a senha está correta
    if user and bcrypt.check_password_hash(user.password_hash, password):
        # Cria o token JWT.
        user_claims = {"is_admin": user.is_admin}

        access_token = create_access_token(
            identity=user.email,
            additional_claims=user_claims
        )

        return jsonify({
            "message": "Login bem-sucedido!",
            "access_token": access_token
        }), 200
    else:
        return jsonify({"error": "Credenciais inválidas"}), 401