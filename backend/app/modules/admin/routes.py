from flask import request, jsonify
from . import admin_bp
from app.models import ScrapedData, User
from app.extensions import db, bcrypt
from sqlalchemy import exc

# Importa nosso "porteiro" de admin
from app.modules.auth.decorators import admin_required

@admin_bp.route('/users', methods=['POST'])
@admin_required() # <-- SÓ ADMIN PODE ACESSAR
def create_user_by_admin():
    """ (ADMIN) Cria um novo usuário (vendas ou outro admin) """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    # Admin pode decidir se o novo usuário também será admin
    is_admin = data.get('is_admin', False) 

    if not email or not password:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email já cadastrado"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = User(
        email=email,
        password_hash=hashed_password,
        is_admin=is_admin
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            "message": f"Usuário {email} (admin={is_admin}) criado com sucesso!"
        }), 201
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"Erro de banco de dados: {e}"}), 500

@admin_bp.route('/users', methods=['GET'])
@admin_required() # <-- SÓ ADMIN PODE ACESSAR
def get_all_users():
    """ (ADMIN) Lista todos os usuários no sistema """
    try:
        users = User.query.all()
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "email": user.email,
                "is_admin": user.is_admin,
                "created_at": user.created_at
            })
        return jsonify(user_list), 200
    except exc.SQLAlchemyError as e:
        return jsonify({"error": f"Erro de banco de dados: {e}"}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required() # <-- SÓ ADMIN PODE ACESSAR
def delete_user(user_id):
    """ (ADMIN) Deleta um usuário pelo ID """
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404

        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"Usuário {user.email} deletado com sucesso"}), 200

    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"Erro de banco de dados: {e}"}), 500
    
# --- NOVA ROTA: Limpar o Cache de Scrape ---
@admin_bp.route('/clear-cache', methods=['POST'])
@admin_required()
def clear_scrape_cache():
    """
    (ADMIN) Apaga TODOS os registos da tabela ScrapedData (o cache).
    Isto força o re-scrape de todos os sites.
    """
    try:
        # Apaga todas as linhas da tabela ScrapedData
        num_rows_deleted = db.session.query(ScrapedData).delete()
        db.session.commit()
        return jsonify({
            "message": f"Cache de scrape limpo com sucesso! {num_rows_deleted} registos apagados."
        }), 200
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        print(f"Erro ao limpar cache: {e}")
        return jsonify({"error": f"Erro interno ao tentar limpar o cache: {e}"}), 500