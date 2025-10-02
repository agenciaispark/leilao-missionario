import jwt
from functools import wraps
from flask import request, jsonify
from src.config import Config

def token_required(f):
    """Decorator para proteger rotas que requerem autenticação."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Verifica se o token está no header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Token inválido!'}), 401
        
        if not token:
            return jsonify({'message': 'Token não fornecido!'}), 401
        
        try:
            # Decodifica o token
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            current_user = {
                'id': data['user_id'],
                'email': data['email'],
                'permissao': data['permissao']
            }
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator para proteger rotas que requerem permissão de admin."""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user['permissao'] != 'admin':
            return jsonify({'message': 'Acesso negado! Requer permissão de administrador.'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated

def gestor_or_admin_required(f):
    """Decorator para proteger rotas que requerem permissão de gestor ou admin."""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user['permissao'] not in ['admin', 'gestor']:
            return jsonify({'message': 'Acesso negado! Requer permissão de gestor ou administrador.'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated
