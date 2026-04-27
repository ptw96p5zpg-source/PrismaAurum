# admin.py
# Blueprint para administração: gerir produtos, utilizadores e encomendas.
# Apenas acessível a utilizadores com is_admin = 1.

import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app

from forms import ProductForm
from models import (
    get_all_products, create_product, get_product_by_id, update_product,
    get_all_users, get_all_orders, get_order_by_id, get_order_items, update_order_status
)

admin_bp = Blueprint('admin', __name__)

def admin_required(func):
    """Decorador simples para verificar se o utilizador é admin."""
    def wrapper(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Acesso negado. Área restrita a administradores.', 'danger')
            return redirect(url_for('routes.index'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# ---------- Dashboard Admin ----------
@admin_bp.route('/admin')
@admin_required
def admin_dashboard():
    """
    Painel principal do administrador.
    """
    products = get_all_products()
    return render_template('admin.html', products=products)

# ---------- Gestão de Produtos ----------
@admin_bp.route('/admin/product/new', methods=['GET', 'POST'])
@admin_required
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        # Processar imagem
        image_filename = None
        if form.image.data:
            file = form.image.data
            filename = secure_filename(file.filename)
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            upload_folder = os.path.join(current_app.root_path, 'static', 'images', 'products')
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, filename))
            image_filename = filename

        create_product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            weight=form.weight.data,
            purity=form.purity.data,
            category=form.category.data,
            stock=form.stock.data,
            image_filename=image_filename
        )
        flash('Produto criado com sucesso!', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('product_form.html', form=form, title='Novo Produto')

@admin_bp.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash('Produto não encontrado.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

    # Converte o objeto Row em dicionário
    product_dict = {k: product[k] for k in product.keys()}
    form = ProductForm(data=product_dict)

    if form.validate_on_submit():
        # Manter imagem existente por defeito
        image_filename = product_dict.get('image_filename')
        if form.image.data:
            # Nova imagem foi enviada
            file = form.image.data
            filename = secure_filename(file.filename)
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            upload_folder = os.path.join(current_app.root_path, 'static', 'images', 'products')
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, filename))
            image_filename = filename
            # Opcional: apagar a imagem antiga
            if product_dict.get('image_filename'):
                old_path = os.path.join(upload_folder, product_dict['image_filename'])
                if os.path.exists(old_path):
                    os.remove(old_path)

        update_product(
            product_id,
            form.name.data,
            form.description.data,
            form.price.data,
            form.weight.data,
            form.purity.data,
            form.category.data,
            form.stock.data,
            image_filename
        )
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('product_form.html', form=form, title='Editar Produto', product=product)

# ---------- Gestão de Encomendas ----------
@admin_bp.route('/admin/orders')
@admin_required
def list_orders():
    """
    Lista todas as encomendas com opção de filtrar por estado.
    """
    status_filter = request.args.get('status', 'todos')
    orders = get_all_orders()
    if status_filter != 'todos':
        orders = [o for o in orders if o['status'] == status_filter]
    return render_template('admin_orders.html', orders=orders, current_filter=status_filter)

@admin_bp.route('/admin/order/<int:order_id>')
@admin_required
def order_detail(order_id):
    """
    Detalhe de uma encomenda e formulário para alterar estado.
    """
    order = get_order_by_id(order_id)
    if not order:
        flash('Encomenda não encontrada.', 'danger')
        return redirect(url_for('admin.list_orders'))
    items = get_order_items(order_id)
    return render_template('admin_order_detail.html', order=order, items=items)

@admin_bp.route('/admin/order/<int:order_id>/update', methods=['POST'])
@admin_required
def update_order_status_route(order_id):
    """
    Atualiza o estado de uma encomenda.
    """
    new_status = request.form.get('status')
    if new_status not in ['pending', 'paid', 'delivered']:
        flash('Estado inválido.', 'danger')
        return redirect(url_for('admin.order_detail', order_id=order_id))

    update_order_status(order_id, new_status)
    flash(f'Estado da encomenda #{order_id} atualizado para {new_status}.', 'success')
    return redirect(url_for('admin.order_detail', order_id=order_id))

# ---------- Gestão de Utilizadores (opcional) ----------
@admin_bp.route('/admin/users')
@admin_required
def list_users():
    """
    Lista todos os utilizadores registados.
    """
    users = get_all_users()
    return render_template('admin_users.html', users=users)