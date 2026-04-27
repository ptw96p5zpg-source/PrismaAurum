# cart.py
# Blueprint para funcionalidades do carrinho: visualizar e finalizar compra via WhatsApp.

from flask import Blueprint, render_template, session, redirect, url_for, flash
from models import (
    get_cart_by_user, get_cart_items, clear_cart,
    create_order, create_order_items, update_product_stock, get_product_by_id
)
from urllib.parse import quote

cart_bp = Blueprint('cart', __name__)

# Número de WhatsApp do proprietário (Leo Pereira) com código do país, sem espaços nem '+'
WHATSAPP_NUMBER = "244956741648"

@cart_bp.route('/cart')
def view_cart():
    """
    Mostra o conteúdo do carrinho do utilizador logado.
    """
    if 'user_id' not in session:
        flash('Acesso restrito. Faça login.', 'danger')
        return redirect(url_for('auth.login'))

    cart = get_cart_by_user(session['user_id'])
    items = get_cart_items(cart['id'])
    total = sum(item['quantity'] * item['price'] for item in items)
    return render_template('cart.html', items=items, total=total)

@cart_bp.route('/checkout', methods=['POST'])
def checkout():
    """
    Regista a encomenda na base de dados, atualiza stocks e redireciona para WhatsApp.
    """
    # 1. Verificar se o utilizador está logado
    if 'user_id' not in session:
        flash('Acesso restrito. Faça login.', 'danger')
        return redirect(url_for('auth.login'))

    # 2. Obter carrinho e itens
    cart = get_cart_by_user(session['user_id'])
    items = get_cart_items(cart['id'])
    if not items:
        flash('Carrinho vazio. Não é possível finalizar a compra.', 'warning')
        return redirect(url_for('cart.view_cart'))

    # 3. Calcular total
    total = sum(item['quantity'] * item['price'] for item in items)

    # 4. Criar encomenda na base de dados (status = 'pending')
    order_id = create_order(session['user_id'], total, status='pending')

    # 5. Criar itens da encomenda e atualizar stock
    for item in items:
        product = get_product_by_id(item['product_id'])
        new_stock = product['stock'] - item['quantity']
        update_product_stock(item['product_id'], new_stock)

    create_order_items(order_id, items)

    # 6. Limpar carrinho (opcional, mas recomendado para evitar duplicações)
    clear_cart(cart['id'])

    # 7. Construir a mensagem para o WhatsApp
    username = session.get('username', 'Cliente')
    mensagem = f"Olá, sou {username} (ID do pedido: {order_id}) e gostaria de finalizar a compra dos seguintes itens:\n\n"
    for item in items:
        subtotal = item['quantity'] * item['price']
        mensagem += f"• {item['name']} (x{item['quantity']}) - €{item['price']:.2f} cada = €{subtotal:.2f}\n"
    mensagem += f"\nTotal: €{total:.2f}\n\nPor favor, confirme o pagamento. Obrigado!"

    # 8. Codificar a mensagem para a URL
    mensagem_codificada = quote(mensagem)
    whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={mensagem_codificada}"

    # 9. Redirecionar para o WhatsApp
    return redirect(whatsapp_url)