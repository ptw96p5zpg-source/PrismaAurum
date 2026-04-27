# database.py
# Responsável por estabelecer a conexão com SQLite e fornecer funções auxiliares.

import sqlite3
from flask import g
from config import Config

def get_db():
    """
    Função para obter a conexão com a base de dados.
    Utiliza o objeto 'g' do Flask para armazenar a conexão durante o pedido.
    """
    if 'db' not in g:
        # Conecta ao ficheiro SQLite definido na configuração
        g.db = sqlite3.connect(Config.DATABASE)
        # Permite acessar colunas por nome (row_factory)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """
    Fecha a conexão com a base de dados, se existir, no final do pedido.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """
    Inicializa a base de dados executando o script schema.sql.
    Esta função é chamada manualmente via Flask CLI.
    """
    db = get_db()
    with open('schema.sql', 'r', encoding='utf-8') as f:
        db.executescript(f.read())
    db.commit()