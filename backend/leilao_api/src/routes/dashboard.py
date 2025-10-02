from flask import Blueprint, request, jsonify
from src.db import get_db_connection, release_db_connection
from src.auth import token_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard(current_user):
    """Retorna dados do dashboard."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Quantidade de campanhas ativas
        cursor.execute("SELECT COUNT(*) FROM campanhas WHERE status = 'ativa'")
        campanhas_ativas = cursor.fetchone()[0]
        
        # Quantidade de itens cadastrados
        cursor.execute("SELECT COUNT(*) FROM itens")
        total_itens = cursor.fetchone()[0]
        
        # Total de lances recebidos
        cursor.execute("SELECT COUNT(*) FROM lances")
        total_lances = cursor.fetchone()[0]
        
        # Valor total arrecadado
        cursor.execute("SELECT COALESCE(SUM(valor), 0) FROM lances")
        valor_arrecadado = float(cursor.fetchone()[0])
        
        # Últimos 5 lances
        cursor.execute("""
            SELECT l.id, l.valor, l.nome_participante, l.data_lance,
                   i.id, i.nome
            FROM lances l
            JOIN itens i ON l.item_id = i.id
            ORDER BY l.data_lance DESC
            LIMIT 5
        """)
        
        lances = cursor.fetchall()
        ultimos_lances = []
        for lance in lances:
            ultimos_lances.append({
                'id': lance[0],
                'valor': float(lance[1]),
                'nome_participante': lance[2],
                'data_lance': lance[3].isoformat(),
                'item': {
                    'id': lance[4],
                    'nome': lance[5]
                }
            })
        
        return jsonify({
            'campanhas_ativas': campanhas_ativas,
            'total_itens': total_itens,
            'total_lances': total_lances,
            'valor_arrecadado': valor_arrecadado,
            'ultimos_lances': ultimos_lances
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar dados do dashboard: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@dashboard_bp.route('/configuracoes', methods=['GET'])
def get_configuracoes():
    """Retorna as configurações do sistema."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, nome_instituicao, logo, telefone, email, moeda, mensagem_home
            FROM configuracoes
            ORDER BY id DESC
            LIMIT 1
        """)
        
        config = cursor.fetchone()
        
        if not config:
            # Retorna configurações padrão se não houver nenhuma
            return jsonify({
                'nome_instituicao': 'Igreja',
                'logo': None,
                'telefone': None,
                'email': None,
                'moeda': 'R$',
                'mensagem_home': 'Bem-vindo ao Leilão Missionário!'
            }), 200
        
        return jsonify({
            'id': config[0],
            'nome_instituicao': config[1],
            'logo': config[2],
            'telefone': config[3],
            'email': config[4],
            'moeda': config[5],
            'mensagem_home': config[6]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar configurações: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

@dashboard_bp.route('/configuracoes', methods=['POST'])
@token_required
def update_configuracoes(current_user):
    """Atualiza as configurações do sistema."""
    from src.auth import admin_required
    
    @admin_required
    def _update(current_user):
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos!'}), 400
        
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Verifica se já existe uma configuração
            cursor.execute("SELECT id FROM configuracoes ORDER BY id DESC LIMIT 1")
            config = cursor.fetchone()
            
            if config:
                # Atualiza a configuração existente
                fields = []
                values = []
                
                if 'nome_instituicao' in data:
                    fields.append("nome_instituicao = %s")
                    values.append(data['nome_instituicao'])
                if 'logo' in data:
                    fields.append("logo = %s")
                    values.append(data['logo'])
                if 'telefone' in data:
                    fields.append("telefone = %s")
                    values.append(data['telefone'])
                if 'email' in data:
                    fields.append("email = %s")
                    values.append(data['email'])
                if 'moeda' in data:
                    fields.append("moeda = %s")
                    values.append(data['moeda'])
                if 'mensagem_home' in data:
                    fields.append("mensagem_home = %s")
                    values.append(data['mensagem_home'])
                
                if fields:
                    values.append(config[0])
                    query = f"UPDATE configuracoes SET {', '.join(fields)} WHERE id = %s"
                    cursor.execute(query, values)
            else:
                # Cria uma nova configuração
                cursor.execute("""
                    INSERT INTO configuracoes (nome_instituicao, logo, telefone, email, moeda, mensagem_home)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    data.get('nome_instituicao', 'Igreja'),
                    data.get('logo'),
                    data.get('telefone'),
                    data.get('email'),
                    data.get('moeda', 'R$'),
                    data.get('mensagem_home', 'Bem-vindo ao Leilão Missionário!')
                ))
            
            conn.commit()
            
            # Registra na auditoria
            cursor.execute(
                "INSERT INTO auditoria (usuario_id, acao) VALUES (%s, %s)",
                (current_user['id'], "Atualizou as configurações do sistema")
            )
            conn.commit()
            
            return jsonify({'message': 'Configurações atualizadas com sucesso!'}), 200
            
        except Exception as e:
            if conn:
                conn.rollback()
            return jsonify({'message': f'Erro ao atualizar configurações: {str(e)}'}), 500
        finally:
            if conn:
                cursor.close()
                release_db_connection(conn)
    
    return _update(current_user)

@dashboard_bp.route('/auditoria', methods=['GET'])
@token_required
def get_auditoria(current_user):
    """Retorna o log de auditoria."""
    from src.auth import admin_required
    
    @admin_required
    def _get_auditoria(current_user):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT a.id, a.acao, a.data_acao, u.id, u.nome, u.email
                FROM auditoria a
                LEFT JOIN usuarios u ON a.usuario_id = u.id
                ORDER BY a.data_acao DESC
                LIMIT 100
            """)
            
            logs = cursor.fetchall()
            
            result = []
            for log in logs:
                result.append({
                    'id': log[0],
                    'acao': log[1],
                    'data_acao': log[2].isoformat(),
                    'usuario': {
                        'id': log[3],
                        'nome': log[4],
                        'email': log[5]
                    } if log[3] else None
                })
            
            return jsonify(result), 200
            
        except Exception as e:
            return jsonify({'message': f'Erro ao buscar auditoria: {str(e)}'}), 500
        finally:
            if conn:
                cursor.close()
                release_db_connection(conn)
    
    return _get_auditoria(current_user)
