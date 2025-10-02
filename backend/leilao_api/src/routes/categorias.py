from flask import Blueprint, request, jsonify
from src.db import get_db_connection, release_db_connection
from src.auth import token_required, gestor_or_admin_required

categorias_bp = Blueprint('categorias', __name__)

@categorias_bp.route('/categorias', methods=['GET'])
def get_categorias():
    """Lista todas as categorias."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, nome FROM categorias ORDER BY nome")
        categorias = cursor.fetchall()
        
        result = []
        for categoria in categorias:
            result.append({
                'id': categoria[0],
                'nome': categoria[1]
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar categorias: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@categorias_bp.route('/categorias/<int:id>', methods=['GET'])
def get_categoria(id):
    """Busca uma categoria específica."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, nome FROM categorias WHERE id = %s", (id,))
        categoria = cursor.fetchone()
        
        if not categoria:
            return jsonify({'message': 'Categoria não encontrada!'}), 404
        
        return jsonify({
            'id': categoria[0],
            'nome': categoria[1]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar categoria: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@categorias_bp.route('/categorias', methods=['POST'])
@token_required
@gestor_or_admin_required
def create_categoria(current_user):
    """Cria uma nova categoria."""
    data = request.get_json()
    
    if not data or not data.get('nome'):
        return jsonify({'message': 'Nome é obrigatório!'}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO categorias (nome) VALUES (%s) RETURNING id",
            (data['nome'],)
        )
        categoria_id = cursor.fetchone()[0]
        conn.commit()
        
        return jsonify({'message': 'Categoria criada com sucesso!', 'id': categoria_id}), 201
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'message': f'Erro ao criar categoria: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@categorias_bp.route('/categorias/<int:id>', methods=['PUT'])
@token_required
@gestor_or_admin_required
def update_categoria(current_user, id):
    """Atualiza uma categoria existente."""
    data = request.get_json()
    
    if not data or not data.get('nome'):
        return jsonify({'message': 'Nome é obrigatório!'}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM categorias WHERE id = %s", (id,))
        if not cursor.fetchone():
            return jsonify({'message': 'Categoria não encontrada!'}), 404
        
        cursor.execute(
            "UPDATE categorias SET nome = %s WHERE id = %s",
            (data['nome'], id)
        )
        conn.commit()
        
        return jsonify({'message': 'Categoria atualizada com sucesso!'}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'message': f'Erro ao atualizar categoria: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@categorias_bp.route('/categorias/<int:id>', methods=['DELETE'])
@token_required
@gestor_or_admin_required
def delete_categoria(current_user, id):
    """Deleta uma categoria."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM categorias WHERE id = %s", (id,))
        if not cursor.fetchone():
            return jsonify({'message': 'Categoria não encontrada!'}), 404
        
        cursor.execute("DELETE FROM categorias WHERE id = %s", (id,))
        conn.commit()
        
        return jsonify({'message': 'Categoria deletada com sucesso!'}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'message': f'Erro ao deletar categoria: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)
