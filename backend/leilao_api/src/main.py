import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.config import Config
from src.db import init_db_pool, close_db_pool

# Importa os blueprints
from src.routes.auth import auth_bp
from src.routes.campanhas import campanhas_bp
from src.routes.categorias import categorias_bp
from src.routes.itens import itens_bp
from src.routes.lances import lances_bp
from src.routes.usuarios import usuarios_bp
from src.routes.dashboard import dashboard_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Habilita CORS para desenvolvimento
CORS(app)

# Inicializa o pool de conexões com o banco de dados
try:
    init_db_pool()
except Exception as e:
    print(f"Erro ao inicializar o banco de dados: {e}")
    print("A aplicação continuará, mas as operações de banco de dados falharão.")

# Registra os blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(campanhas_bp, url_prefix='/api')
app.register_blueprint(categorias_bp, url_prefix='/api')
app.register_blueprint(itens_bp, url_prefix='/api')
app.register_blueprint(lances_bp, url_prefix='/api')
app.register_blueprint(usuarios_bp, url_prefix='/api')
app.register_blueprint(dashboard_bp, url_prefix='/api')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve o frontend React."""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.teardown_appcontext
def shutdown_session(exception=None):
    """Fecha o pool de conexões ao encerrar a aplicação."""
    close_db_pool()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
