from flask import Blueprint, request, jsonify
from src.db import get_db_connection, release_db_connection
from src.auth import token_required, gestor_or_admin_required

itens_bp = Blueprint('itens', __name__)

@itens_bp.route('/itens', methods=['GET'])
def get_itens():
    """Lista todos os itens."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Filtra por campanha se fornecido
        campanha_id = request.args.get('campanha_id')
        
        query = """
            SELECT i.id, i.nome, i.lance_inicial, i.banner_16_9, i.banner_1_1,
                   c.id, c.nome, cat.id, cat.nome,
                   COALESCE(MAX(l.valor), i.lance_inicial) as lance_atual
            FROM itens i
            JOIN campanhas c ON i.campanha_id = c.id
            JOIN categorias cat ON i.categoria_id = cat.id
            LEFT JOIN lances l ON i.id = l.item_id
        """
        
        if campanha_id:
            query += " WHERE i.campanha_id = %s"
            query += " GROUP BY i.id, c.id, cat.id ORDER BY i.id DESC"
            cursor.execute(query, (campanha_id,))
        else:
            query += " GROUP BY i.id, c.id, cat.id ORDER BY i.id DESC"
            cursor.execute(query)
        
        itens = cursor.fetchall()
        
        result = []
        for item in itens:
            result.append({
                'id': item[0],
                'nome': item[1],
                'lance_inicial': float(item[2]),
                'banner_16_9': item[3],
                'banner_1_1': item[4],
                'campanha': {
                    'id': item[5],
                    'nome': item[6]
                },
                'categoria': {
                    'id': item[7],
                    'nome': item[8]
                },
                'lance_atual': float(item[9])
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar itens: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@itens_bp.route('/itens/<int:id>', methods=['GET'])
def get_item(id):
    """Busca um item específico com seus últimos 3 lances."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Busca o item
        cursor.execute("""
            SELECT i.id, i.nome, i.lance_inicial, i.banner_16_9, i.banner_1_1,
                   c.id, c.nome, cat.id, cat.nome,
                   COALESCE(MAX(l.valor), i.lance_inicial) as lance_atual
            FROM itens i
            JOIN campanhas c ON i.campanha_id = c.id
            JOIN categorias cat ON i.categoria_id = cat.id
            LEFT JOIN lances l ON i.id = l.item_id
            WHERE i.id = %s
            GROUP BY i.id, c.id, cat.id
        """, (id,))
        
        item = cursor.fetchone()
        
        if not item:
            return jsonify({'message': 'Item não encontrado!'}), 404
        
        # Busca os últimos 3 lances
        cursor.execute("""
            SELECT valor, data_lance
            FROM lances
            WHERE item_id = %s
            ORDER BY data_lance DESC
            LIMIT 3
        """, (id,))
        
        lances = cursor.fetchall()
        
        result = {
            'id': item[0],
            'nome': item[1],
            'lance_inicial': float(item[2]),
            'banner_16_9': item[3],
            'banner_1_1': item[4],
            'campanha': {
                'id': item[5],
                'nome': item[6]
            },
            'categoria': {
                'id': item[7],
                'nome': item[8]
            },
            'lance_atual': float(item[9]),
            'ultimos_lances': [{'valor': float(l[0]), 'data': l[1].isoformat()} for l in lances]
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar item: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@itens_bp.route('/itens', methods=['POST'])
@token_required
@gestor_or_admin_required
def create_item(current_user):
    """Cria um novo item."""
    data = request.get_json()
    
    required_fields = ['nome', 'campanha_id', 'categoria_id', 'lance_inicial']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'message': 'Campos obrigatórios: nome, campanha_id, categoria_id, lance_inicial'}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se a campanha está ativa
        cursor.execute("SELECT status FROM campanhas WHERE id = %s", (data['campanha_id'],))
        campanha = cursor.fetchone()
        
        if not campanha:
            return jsonify({'message': 'Campanha não encontrada!'}), 404
        
        if campanha[0] != 'ativa':
            return jsonify({'message': 'Apenas campanhas ativas podem receber novos itens!'}), 400
        
        cursor.execute("""
            INSERT INTO itens (nome, campanha_id, categoria_id, lance_inicial, banner_16_9, banner_1_1)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data['nome'],
            data['campanha_id'],
            data['categoria_id'],
            data['lance_inicial'],
            data.get('banner_16_9'),
            data.get('banner_1_1')
        ))
        
        item_id = cursor.fetchone()[0]
        conn.commit()
        
        # Registra na auditoria
        cursor.execute(
            "INSERT INTO auditoria (usuario_id, acao) VALUES (%s, %s)",
            (current_user['id'], f"Criou o item '{data['nome']}' (ID: {item_id})")
        )
        conn.commit()
        
        return jsonify({'message': 'Item criado com sucesso!', 'id': item_id}), 201
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'message': f'Erro ao criar item: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@itens_bp.route('/itens/<int:id>', methods=['PUT'])
@token_required
@gestor_or_admin_required
def update_item(current_user, id):
    """Atualiza um item existente."""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Dados não fornecidos!'}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se o item existe
        cursor.execute("SELECT nome FROM itens WHERE id = %s", (id,))
        item = cursor.fetchone()
        
        if not item:
            return jsonify({'message': 'Item não encontrado!'}), 404
        
        # Atualiza os campos fornecidos
        fields = []
        values = []
        
        if 'nome' in data:
            fields.append("nome = %s")
            values.append(data['nome'])
        if 'campanha_id' in data:
            fields.append("campanha_id = %s")
            values.append(data['campanha_id'])
        if 'categoria_id' in data:
            fields.append("categoria_id = %s")
            values.append(data['categoria_id'])
        if 'lance_inicial' in data:
            fields.append("lance_inicial = %s")
            values.append(data['lance_inicial'])
        if 'banner_16_9' in data:
            fields.append("banner_16_9 = %s")
            values.append(data['banner_16_9'])
        if 'banner_1_1' in data:
            fields.append("banner_1_1 = %s")
            values.append(data['banner_1_1'])
        
        if not fields:
            return jsonify({'message': 'Nenhum campo para atualizar!'}), 400
        
        values.append(id)
        query = f"UPDATE itens SET {', '.join(fields)} WHERE id = %s"
        
        cursor.execute(query, values)
        conn.commit()
        
        # Registra na auditoria
        cursor.execute(
            "INSERT INTO auditoria (usuario_id, acao) VALUES (%s, %s)",
            (current_user['id'], f"Atualizou o item '{item[0]}' (ID: {id})")
        )
        conn.commit()
        
        return jsonify({'message': 'Item atualizado com sucesso!'}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'message': f'Erro ao atualizar item: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@itens_bp.route('/itens/<int:id>', methods=['DELETE'])
@token_required
@gestor_or_admin_required
def delete_item(current_user, id):
    """Deleta um item."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se o item existe
        cursor.execute("SELECT nome FROM itens WHERE id = %s", (id,))
        item = cursor.fetchone()
        
        if not item:
            return jsonify({'message': 'Item não encontrado!'}), 404
        
        cursor.execute("DELETE FROM itens WHERE id = %s", (id,))
        conn.commit()
        
        # Registra na auditoria
        cursor.execute(
            "INSERT INTO auditoria (usuario_id, acao) VALUES (%s, %s)",
            (current_user['id'], f"Deletou o item '{item[0]}' (ID: {id})")
        )
        conn.commit()
        
        return jsonify({'message': 'Item deletado com sucesso!'}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'message': f'Erro ao deletar item: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)
