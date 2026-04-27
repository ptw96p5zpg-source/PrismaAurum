# models.py
# Define a estrutura das tabelas e funções para interagir com os dados.

from database import get_db

# ---------- Tabela de Utilizadores ----------
def create_user(username, email, password_hash, is_admin=0):
    """
    Insere um novo utilizador na base de dados.
    is_admin: 0 para cliente normal, 1 para administrador.
    """
    db = get_db()
    cursor = db.execute(
        "INSERT INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)",
        (username, email, password_hash, is_admin)
    )
    db.commit()
    return cursor.lastrowid

def get_user_by_username(username):
    """Retorna um dicionário com os dados do utilizador a partir do username."""
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    return user

def get_user_by_id(user_id):
    """Retorna um dicionário com os dados do utilizador a partir do ID."""
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return user

def get_all_users():
    """Retorna todos os utilizadores (para admin)."""
    db = get_db()
    users = db.execute("SELECT id, username, email, is_admin, created_at FROM users").fetchall()
    return users

# ---------- Tabela de Produtos ----------
def create_product(name, description, price, weight, purity, category, stock, image_filename=None):
    """
    Insere um novo produto (ouro/prata fracionado) na base de dados.
    category: 'ouro' ou 'prata'
    """
    db = get_db()
    cursor = db.execute(
        "INSERT INTO products (name, description, price, weight, purity, category, stock, image_filename) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (name, description, price, weight, purity, category, stock, image_filename)
    )
    db.commit()
    return cursor.lastrowid

def update_product(product_id, name, description, price, weight, purity, category, stock, image_filename=None):
    """Atualiza todos os campos de um produto."""
    db = get_db()
    db.execute(
        """UPDATE products
           SET name = ?, description = ?, price = ?, weight = ?, purity = ?, category = ?, stock = ?, image_filename = ?
           WHERE id = ?""",
        (name, description, price, weight, purity, category, stock, image_filename, product_id)
    )
    db.commit()

def get_all_products():
    """Retorna todos os produtos disponíveis."""
    db = get_db()
    products = db.execute("SELECT * FROM products").fetchall()
    return products

def get_product_by_id(product_id):
    """Retorna um produto específico pelo ID."""
    db = get_db()
    product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    return product

def update_product_stock(product_id, new_stock):
    """Atualiza o stock de um produto."""
    db = get_db()
    db.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))
    db.commit()

# ---------- Tabela de Carrinhos ----------
def create_cart(user_id):
    """Cria um carrinho vazio para um utilizador."""
    db = get_db()
    cursor = db.execute("INSERT INTO carts (user_id) VALUES (?)", (user_id,))
    db.commit()
    return cursor.lastrowid

def get_cart_by_user(user_id):
    """Retorna o carrinho ativo de um utilizador (assumindo apenas um carrinho)."""
    db = get_db()
    cart = db.execute("SELECT * FROM carts WHERE user_id = ?", (user_id,)).fetchone()
    if not cart:
        cart_id = create_cart(user_id)
        cart = db.execute("SELECT * FROM carts WHERE id = ?", (cart_id,)).fetchone()
    return cart

def add_item_to_cart(cart_id, product_id, quantity):
    """Adiciona um item ao carrinho ou atualiza quantidade se já existir."""
    db = get_db()
    existing = db.execute(
        "SELECT * FROM cart_items WHERE cart_id = ? AND product_id = ?",
        (cart_id, product_id)
    ).fetchone()
    if existing:
        db.execute(
            "UPDATE cart_items SET quantity = quantity + ? WHERE cart_id = ? AND product_id = ?",
            (quantity, cart_id, product_id)
        )
    else:
        db.execute(
            "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, ?)",
            (cart_id, product_id, quantity)
        )
    db.commit()

def get_cart_items(cart_id):
    """Retorna todos os itens do carrinho com detalhes do produto."""
    db = get_db()
    items = db.execute(
        "SELECT ci.*, p.name, p.price, p.weight, p.purity, p.category "
        "FROM cart_items ci JOIN products p ON ci.product_id = p.id "
        "WHERE ci.cart_id = ?",
        (cart_id,)
    ).fetchall()
    return items

def clear_cart(cart_id):
    """Remove todos os itens do carrinho."""
    db = get_db()
    db.execute("DELETE FROM cart_items WHERE cart_id = ?", (cart_id,))
    db.commit()

# ---------- Tabela de Encomendas (checkout) ----------
def create_order(user_id, total_amount, status='pending'):
    """Cria um novo registo de encomenda."""
    db = get_db()
    cursor = db.execute(
        "INSERT INTO orders (user_id, total_amount, status) VALUES (?, ?, ?)",
        (user_id, total_amount, status)
    )
    db.commit()
    return cursor.lastrowid

def create_order_items(order_id, cart_items):
    """Transfere os itens do carrinho para a tabela order_items."""
    db = get_db()
    for item in cart_items:
        db.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price_at_time) VALUES (?, ?, ?, ?)",
            (order_id, item['product_id'], item['quantity'], item['price'])
        )
    db.commit()

def get_all_orders():
    """Retorna todas as encomendas (para admin), ordenadas da mais recente para a mais antiga."""
    db = get_db()
    orders = db.execute(
        "SELECT o.*, u.username FROM orders o JOIN users u ON o.user_id = u.id ORDER BY o.created_at DESC"
    ).fetchall()
    return orders

def get_orders_by_user(user_id):
    """Retorna as encomendas de um utilizador específico."""
    db = get_db()
    orders = db.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    return orders

def get_order_by_id(order_id):
    """Retorna uma encomenda pelo ID."""
    db = get_db()
    order = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    return order

def get_order_items(order_id):
    """Retorna os itens de uma encomenda com detalhes do produto."""
    db = get_db()
    items = db.execute(
        "SELECT oi.*, p.name, p.weight, p.purity, p.category "
        "FROM order_items oi JOIN products p ON oi.product_id = p.id "
        "WHERE oi.order_id = ?",
        (order_id,)
    ).fetchall()
    return items

def update_order_status(order_id, new_status):
    """Atualiza o estado de uma encomenda."""
    db = get_db()
    db.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
    db.commit()