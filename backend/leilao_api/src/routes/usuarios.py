from flask import Blueprint, request, jsonify
import bcrypt
from src.db import get_db_connection, release_db_connection
from src.auth import token_required, admin_required

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/usuarios', methods=['GET'])
@token_required
@admin_required
def get_usuarios(current_user):
    """Lista todos os usuários."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, nome, email, permissao FROM usuarios ORDER BY nome")
        usuarios = cursor.fetchall()
        
        result = []
        for usuario in usuarios:
            result.append({
                'id': usuario[0],
                'nome': usuario[1],
                'email': usuario[2],
                'permissao': usuario[3]
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar usuários: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@usuarios_bp.route('/usuarios/<int:id>', methods=['GET'])
@token_required
@admin_required
def get_usuario(current_user, id):
    """Busca um usuário específico."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, nome, email, permissao FROM usuarios WHERE id = %s", (id,))
        usuario = cursor.fetchone()
        
        if not usuario:
            return jsonify({'message': 'Usuário não encontrado!'}), 404
        
        return jsonify({
            'id': usuario[0],
            'nome': usuario[1],
            'email': usuario[2],
            'permissao': usuario[3]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar usuário: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@usuarios_bp.route('/usuarios', methods=['POST'])
@token_required
@admin_required
def create_usuario(current_user):
    """Cria um novo usuário."""
    data = request.get_json()
    
    required_fields = ['nome', 'email', 'senha', 'permissao']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'message': 'Campos obrigatórios: nome, email, senha, permissao'}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se o email já existe
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (data['email'],))
        if cursor.fetchone():
            return jsonify({'message': 'Email já cadastrado!'}), 400
        
        # Hash da senha
        senha_hash = bcrypt.hashpw(data['senha'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha, permissao)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (data['nome'], data['email'], senha_hash, data['permissao']))
        
        usuario_id = cursor.fetchone()[0]
        conn.commit()
        
        # Registra na auditoria
        cursor.execute(
            "INSERT INTO auditoria (usuario_id, acao) VALUES (%s, %s)",
            (current_user['id'], f"Criou o usuário '{data['nome']}' (ID: {usuario_id})")
        )
        conn.commit()
        
        return jsonify({'message': 'Usuário criado com sucesso!', 'id': usuario_id}), 201
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'message': f'Erro ao criar usuário: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@usuarios_bp.route('/usuarios/<int:id>', methods=['PUT'])
@token_required
@admin_required
def update_usuario(current_user, id):
    """Atualiza um usuário existente."""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Dados não fornecidos!'}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se o usuário existe
        cursor.execute("SELECT nome FROM usuarios WHERE id = %s", (id,))
        usuario = cursor.fetchone()
        
        if not usuario:
            return jsonify({'message': 'Usuário não encontrado!'}), 404
        
        # Atualiza os campos fornecidos
        fields = []
        values = []
        
        if 'nome' in data:
            fields.append("nome = %s")
            values.append(data['nome'])
        if 'email' in data:
            fields.append("email = %s")
            values.append(data['email'])
        if 'senha' in data:
            senha_hash = bcrypt.hashpw(data['senha'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            fields.append("senha = %s")
            values.append(senha_hash)
        if 'permissao' in data:
            fields.append("permissao = %s")
            values.append(data['permissao'])
        
        if not fields:
            return jsonify({'message': 'Nenhum campo para atualizar!'}), 400
        
        values.append(id)
        query = f"UPDATE usuarios SET {', '.join(fields)} WHERE id = %s"
        
        cursor.execute(query, values)
        conn.commit()
        
        # Registra na auditoria
        cursor.execute(
            "INSERT INTO auditoria (usuario_id, acao) VALUES (%s, %s)",
            (current_user['id'], f"Atualizou o usuário '{usuario[0]}' (ID: {id})")
        )
        conn.commit()
        
        return jsonify({'message': 'Usuário atualizado com sucesso!'}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'message': f'Erro ao atualizar usuário: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@usuarios_bp.route('/usuarios/<int:id>', methods=['DELETE'])
@token_required
@admin_required
def delete_usuario(current_user, id):
    """Deleta um usuário."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se o usuário existe
        cursor.execute("SELECT nome FROM usuarios WHERE id = %s", (id,))
        usuario = cursor.fetchone()
        
        if not usuario:
            return jsonify({'message': 'Usuário não encontrado!'}), 404
        
        # Não permite deletar a si mesmo
        if id == current_user['id']:
            return jsonify({'message': 'Você não pode deletar seu próprio usuário!'}), 400
        
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        conn.commit()
        
        # Registra na auditoria
        cursor.execute(
            "INSERT INTO auditoria (usuario_id, acao) VALUES (%s, %s)",
            (current_user['id'], f"Deletou o usuário '{usuario[0]}' (ID: {id})")
        )
        conn.commit()
        
        return jsonify({'message': 'Usuário deletado com sucesso!'}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'message': f'Erro ao deletar usuário: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)
