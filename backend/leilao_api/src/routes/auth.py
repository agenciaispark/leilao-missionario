from flask import Blueprint, request, jsonify
import jwt
import bcrypt
from datetime import datetime, timedelta
from src.db import get_db_connection, release_db_connection
from src.config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint de login que retorna um token JWT."""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('senha'):
        return jsonify({'message': 'Email e senha são obrigatórios!'}), 400
    
    email = data['email']
    senha = data['senha']
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Busca o usuário pelo email
        cursor.execute(
            "SELECT id, nome, email, senha, permissao FROM usuarios WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'message': 'Credenciais inválidas!'}), 401
        
        user_id, nome, user_email, senha_hash, permissao = user
        
        # Verifica a senha
        if not bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')):
            return jsonify({'message': 'Credenciais inválidas!'}), 401
        
        # Gera o token JWT
        token = jwt.encode({
            'user_id': user_id,
            'email': user_email,
            'permissao': permissao,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, Config.JWT_SECRET_KEY, algorithm="HS256")
        
        return jsonify({
            'token': token,
            'user': {
                'id': user_id,
                'nome': nome,
                'email': user_email,
                'permissao': permissao
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao realizar login: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Retorna informações do usuário autenticado."""
    from src.auth import token_required
    
    @token_required
    def _get_user(current_user):
        return jsonify({'user': current_user}), 200
    
    return _get_user()
