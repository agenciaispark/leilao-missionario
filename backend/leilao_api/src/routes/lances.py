from flask import Blueprint, request, jsonify
from src.db import get_db_connection, release_db_connection
from src.auth import token_required

lances_bp = Blueprint('lances', __name__)

@lances_bp.route('/lances', methods=['GET'])
@token_required
def get_lances(current_user):
    """Lista todos os lances (protegido)."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Filtros opcionais
        item_id = request.args.get('item_id')
        categoria_id = request.args.get('categoria_id')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = """
            SELECT l.id, l.valor, l.nome_participante, l.telefone, l.data_lance,
                   i.id, i.nome, cat.id, cat.nome
            FROM lances l
            JOIN itens i ON l.item_id = i.id
            JOIN categorias cat ON i.categoria_id = cat.id
            WHERE 1=1
        """
        params = []
        
        if item_id:
            query += " AND l.item_id = %s"
            params.append(item_id)
        
        if categoria_id:
            query += " AND i.categoria_id = %s"
            params.append(categoria_id)
        
        if data_inicio:
            query += " AND l.data_lance >= %s"
            params.append(data_inicio)
        
        if data_fim:
            query += " AND l.data_lance <= %s"
            params.append(data_fim)
        
        query += " ORDER BY l.data_lance DESC"
        
        cursor.execute(query, params)
        lances = cursor.fetchall()
        
        result = []
        for lance in lances:
            result.append({
                'id': lance[0],
                'valor': float(lance[1]),
                'nome_participante': lance[2],
                'telefone': lance[3],
                'data_lance': lance[4].isoformat(),
                'item': {
                    'id': lance[5],
                    'nome': lance[6]
                },
                'categoria': {
                    'id': lance[7],
                    'nome': lance[8]
                }
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar lances: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@lances_bp.route('/lances', methods=['POST'])
def create_lance():
    """Cria um novo lance (público)."""
    data = request.get_json()
    
    required_fields = ['item_id', 'valor', 'nome_participante', 'telefone']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'message': 'Campos obrigatórios: item_id, valor, nome_participante, telefone'}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Busca o lance atual do item
        cursor.execute("""
            SELECT COALESCE(MAX(l.valor), i.lance_inicial) as lance_atual
            FROM itens i
            LEFT JOIN lances l ON i.id = l.item_id
            WHERE i.id = %s
            GROUP BY i.lance_inicial
        """, (data['item_id'],))
        
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'message': 'Item não encontrado!'}), 404
        
        lance_atual = float(result[0])
        
        # Valida se o novo lance é maior que o atual
        if float(data['valor']) <= lance_atual:
            return jsonify({
                'message': f'O lance deve ser maior que o lance atual de R$ {lance_atual:.2f}',
                'lance_atual': lance_atual
            }), 400
        
        # Insere o novo lance
        cursor.execute("""
            INSERT INTO lances (item_id, valor, nome_participante, telefone)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (
            data['item_id'],
            data['valor'],
            data['nome_participante'],
            data['telefone']
        ))
        
        lance_id = cursor.fetchone()[0]
        conn.commit()
        
        return jsonify({
            'message': 'Lance registrado com sucesso!',
            'id': lance_id
        }), 201
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'message': f'Erro ao registrar lance: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@lances_bp.route('/lances/ultimos', methods=['GET'])
@token_required
def get_ultimos_lances(current_user):
    """Retorna os últimos 5 lances (para dashboard)."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT l.id, l.valor, l.nome_participante, l.telefone, l.data_lance,
                   i.id, i.nome
            FROM lances l
            JOIN itens i ON l.item_id = i.id
            ORDER BY l.data_lance DESC
            LIMIT 5
        """)
        
        lances = cursor.fetchall()
        
        result = []
        for lance in lances:
            result.append({
                'id': lance[0],
                'valor': float(lance[1]),
                'nome_participante': lance[2],
                'telefone': lance[3],
                'data_lance': lance[4].isoformat(),
                'item': {
                    'id': lance[5],
                    'nome': lance[6]
                }
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar últimos lances: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@lances_bp.route('/lances/exportar', methods=['GET'])
@token_required
def exportar_lances(current_user):
    """Exporta lances em formato CSV."""
    import csv
    from io import StringIO
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT l.id, i.nome as item, cat.nome as categoria, l.valor,
                   l.nome_participante, l.telefone, l.data_lance
            FROM lances l
            JOIN itens i ON l.item_id = i.id
            JOIN categorias cat ON i.categoria_id = cat.id
            ORDER BY l.data_lance DESC
        """)
        
        lances = cursor.fetchall()
        
        # Cria CSV em memória
        output = StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow(['ID', 'Item', 'Categoria', 'Valor', 'Participante', 'Telefone', 'Data'])
        
        # Dados
        for lance in lances:
            writer.writerow([
                lance[0],
                lance[1],
                lance[2],
                f'R$ {float(lance[3]):.2f}',
                lance[4],
                lance[5],
                lance[6].strftime('%d/%m/%Y %H:%M:%S')
            ])
        
        output.seek(0)
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=lances.csv'}
        )
        
    except Exception as e:
        return jsonify({'message': f'Erro ao exportar lances: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)
