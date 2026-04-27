# create_admin.py
import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('prisma_aurum.db')
cursor = conn.cursor()

username = 'leo_pereira'
email = 'leopereira615@icloud.com.pt'
password = 'Catipia123'  # Altera para uma password segura

hashed = generate_password_hash(password)

try:
    cursor.execute("""
        INSERT INTO users (username, email, password_hash, is_admin)
        VALUES (?, ?, ?, ?)
    """, (username, email, hashed, 1))
    conn.commit()
    print("Administrador criado com sucesso!")
except sqlite3.IntegrityError:
    print("Erro: Utilizador já existe.")
finally:
    conn.close()