from flask import Blueprint, request, jsonify
from src.db import get_db_connection, release_db_connection
from src.auth import token_required, gestor_or_admin_required

campanhas_bp = Blueprint('campanhas', __name__)

@campanhas_bp.route('/campanhas', methods=['GET'])
def get_campanhas():
    """Lista todas as campanhas."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Filtra por status se fornecido
        status = request.args.get('status')
        
        if status:
            cursor.execute(
                "SELECT id, nome, ano, status, banner FROM campanhas WHERE status = %s ORDER BY ano DESC",
                (status,)
            )
        else:
            cursor.execute(
                "SELECT id, nome, ano, status, banner FROM campanhas ORDER BY ano DESC"
            )
        
        campanhas = cursor.fetchall()
        
        result = []
        for campanha in campanhas:
            result.append({
                'id': campanha[0],
                'nome': campanha[1],
                'ano': campanha[2],
                'status': campanha[3],
                'banner': campanha[4]
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar campanhas: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@campanhas_bp.route('/campanhas/<int:id>', methods=['GET'])
def get_campanha(id):
    """Busca uma campanha específica."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, nome, ano, status, banner FROM campanhas WHERE id = %s",
            (id,)
        )
        campanha = cursor.fetchone()
        
        if not campanha:
            return jsonify({'message': 'Campanha não encontrada!'}), 404
        
        return jsonify({
            'id': campanha[0],
            'nome': campanha[1],
            'ano': campanha[2],
            'status': campanha[3],
            'banner': campanha[4]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar campanha: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@campanhas_bp.route('/campanhas', methods=['POST'])
@token_required
@gestor_or_admin_required
def create_campanha(current_user):
    """Cria uma nova campanha."""
    data = request.get_json()
    
    if not data or not data.get('nome') or not data.get('ano') or not data.get('status'):
        return jsonify({'message': 'Nome, ano e status são obrigatórios!'}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO campanhas (nome, ano, status, banner) VALUES (%s, %s, %s, %s) RETURNING id",
            (data['nome'], data['ano'], data['status'], data.get('banner'))
        )
        campanha_id = cursor.fetchone()[0]
        conn.commit()
        
        # Registra na auditoria
        cursor.execute(
            "INSERT INTO auditoria (usuario_id, acao) VALUES (%s, %s)",
            (current_user['id'], f"Criou a campanha '{data['nome']}' (ID: {campanha_id})")
        )
        conn.commit()
        
        return jsonify({'message': 'Campanha criada com sucesso!', 'id': campanha_id}), 201
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'message': f'Erro ao criar campanha: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@campanhas_bp.route('/campanhas/<int:id>', methods=['PUT'])
@token_required
@gestor_or_admin_required
def update_campanha(current_user, id):
    """Atualiza uma campanha existente."""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Dados não fornecidos!'}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se a campanha existe
        cursor.execute("SELECT id, nome FROM campanhas WHERE id = %s", (id,))
        campanha = cursor.fetchone()
        
        if not campanha:
            return jsonify({'message': 'Campanha não encontrada!'}), 404
        
        # Atualiza os campos fornecidos
        fields = []
        values = []
        
        if 'nome' in data:
            fields.append("nome = %s")
            values.append(data['nome'])
        if 'ano' in data:
            fields.append("ano = %s")
            values.append(data['ano'])
        if 'status' in data:
            fields.append("status = %s")
            values.append(data['status'])
        if 'banner' in data:
            fields.append("banner = %s")
            values.append(data['banner'])
        
        if not fields:
            return jsonify({'message': 'Nenhum campo para atualizar!'}), 400
        
        values.append(id)
        query = f"UPDATE campanhas SET {', '.join(fields)} WHERE id = %s"
        
        cursor.execute(query, values)
        conn.commit()
        
        # Registra na auditoria
        cursor.execute(
            "INSERT INTO auditoria (usuario_id, acao) VALUES (%s, %s)",
            (current_user['id'], f"Atualizou a campanha '{campanha[1]}' (ID: {id})")
        )
        conn.commit()
        
        return jsonify({'message': 'Campanha atualizada com sucesso!'}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'message': f'Erro ao atualizar campanha: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@campanhas_bp.route('/campanhas/<int:id>', methods=['DELETE'])
@token_required
@gestor_or_admin_required
def delete_campanha(current_user, id):
    """Deleta uma campanha."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se a campanha existe
        cursor.execute("SELECT nome FROM campanhas WHERE id = %s", (id,))
        campanha = cursor.fetchone()
        
        if not campanha:
            return jsonify({'message': 'Campanha não encontrada!'}), 404
        
        cursor.execute("DELETE FROM campanhas WHERE id = %s", (id,))
        conn.commit()
        
        # Registra na auditoria
        cursor.execute(
            "INSERT INTO auditoria (usuario_id, acao) VALUES (%s, %s)",
            (current_user['id'], f"Deletou a campanha '{campanha[0]}' (ID: {id})")
        )
        conn.commit()
        
        return jsonify({'message': 'Campanha deletada com sucesso!'}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'message': f'Erro ao deletar campanha: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)
