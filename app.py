# app.py
# Ponto de entrada da aplicação. Regista os blueprints e configura a base de dados.

from flask import Flask, session  # session é necessário para o context processor
from config import Config
from database import get_db, close_db

# Importar blueprints (podem ficar fora da função, pois são módulos)
from auth import auth_bp
from routes import routes_bp
from cart import cart_bp
from admin import admin_bp


def create_app():
    """Função fábrica que cria e configura a instância da aplicação Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # ---------- CONTEXT PROCESSOR (para disponibilizar contagem do carrinho) ----------
    # Importa as funções necessárias apenas dentro do context processor
    # para evitar importação circular, ou então no topo com cuidado.
    # Vamos importar aqui dentro para garantir que a BD está acessível.
    from models import get_cart_by_user, get_cart_items

    @app.context_processor
    def inject_cart_count():
        """
        Disponibiliza a variável 'cart_items_count' em todos os templates.
        Conta a quantidade total de itens no carrinho do utilizador logado.
        """
        if 'user_id' in session:
            cart = get_cart_by_user(session['user_id'])
            items = get_cart_items(cart['id'])
            count = sum(item['quantity'] for item in items)
        else:
            count = 0
        return dict(cart_items_count=count)

    # ---------- REGISTO DOS BLUEPRINTS ----------
    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(admin_bp)

    # ---------- FECHAR LIGAÇÃO À BASE DE DADOS ----------
    app.teardown_appcontext(close_db)

    # ---------- COMANDO PARA INICIALIZAR A BASE DE DADOS ----------
    @app.cli.command('init-db')
    def init_db_command():
        """Comando flask init-db: cria as tabelas a partir do schema.sql."""
        from database import init_db
        init_db()
        print('Base de dados inicializada.')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
