# routes.py
# Blueprint com as rotas acessíveis a todos os visitantes e ao cliente logado.

from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from models import (
    get_all_products, get_product_by_id, get_cart_by_user,
    get_cart_items, add_item_to_cart, get_orders_by_user, get_order_items
)
from forms import AddToCartForm

routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/')
def index():
    """
    Página inicial: mostra uma demonstração dos serviços e produtos.
    """
    products = get_all_products()[:4]
    return render_template('index.html', products=products)

@routes_bp.route('/products')
def products():
    """
    Página que lista todos os produtos disponíveis.
    """
    all_products = get_all_products()
    return render_template('products.html', products=all_products)

@routes_bp.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    """
    Página de detalhe de um produto específico.
    Permite adicionar ao carrinho se o utilizador estiver logado.
    """
    product = get_product_by_id(product_id)
    if not product:
        flash('Produto não encontrado.', 'danger')
        return redirect(url_for('routes.products'))

    form = AddToCartForm()
    if form.validate_on_submit():
        if 'user_id' not in session:
            flash('Por favor, faça login para adicionar itens ao carrinho.', 'warning')
            return redirect(url_for('auth.login'))

        cart = get_cart_by_user(session['user_id'])
        add_item_to_cart(cart['id'], product_id, form.quantity.data)
        flash('Produto adicionado ao carrinho!', 'success')
        return redirect(url_for('routes.product_detail', product_id=product_id))

    return render_template('product_detail.html', product=product, form=form)

@routes_bp.route('/dashboard')
def dashboard():
    """
    Dashboard do cliente logado.
    Mostra resumo do carrinho e histórico de encomendas.
    """
    if 'user_id' not in session:
        flash('Acesso restrito. Faça login primeiro.', 'danger')
        return redirect(url_for('auth.login'))

    # Obter carrinho atual
    cart = get_cart_by_user(session['user_id'])
    cart_items = get_cart_items(cart['id'])
    cart_total = sum(item['quantity'] * item['price'] for item in cart_items)

    # Obter encomendas do utilizador
    orders = get_orders_by_user(session['user_id'])
    # Para cada encomenda, podemos buscar os itens se quisermos, mas para já só listamos
    # Vamos criar uma lista de dicionários com info adicional (quantidade de itens, etc.)
    orders_list = []
    for order in orders:
        items = get_order_items(order['id'])
        total_items = sum(item['quantity'] for item in items)
        orders_list.append({
            'id': order['id'],
            'total_amount': order['total_amount'],
            'status': order['status'],
            'created_at': order['created_at'],
            'items_count': total_items
        })

    return render_template(
        'dashboard.html',
        username=session['username'],
        cart_items=cart_items,
        cart_total=cart_total,
        orders=orders_list
    )

@routes_bp.route('/order/<int:order_id>')
def order_detail(order_id):
    """
    Página de detalhe de uma encomenda específica para o cliente.
    """
    if 'user_id' not in session:
        flash('Acesso restrito. Faça login primeiro.', 'danger')
        return redirect(url_for('auth.login'))

    from models import get_order_by_id, get_order_items
    order = get_order_by_id(order_id)
    if not order or order['user_id'] != session['user_id']:
        flash('Encomenda não encontrada ou não pertence a este utilizador.', 'danger')
        return redirect(url_for('routes.dashboard'))

    items = get_order_items(order_id)
    return render_template('order_detail.html', order=order, items=items)