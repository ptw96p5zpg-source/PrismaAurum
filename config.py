# config.py
# Ficheiro de configuração: contém definições globais como chave secreta, tipo de base de dados, etc.

import os

class Config:
    # Chave secreta para sessões e proteção CSRF. Em produção, use variável de ambiente.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-super-secreta-para-desenvolvimento'
    
    # Caminho para o ficheiro da base de dados SQLite
    DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'prisma_aurum.db')