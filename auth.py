# auth.py
# Blueprint responsável pelo registo, login e logout de utilizadores.

from flask import Blueprint, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm
from models import create_user, get_user_by_username

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Rota de registo.
    GET: mostra formulário de registo.
    POST: valida dados, cria utilizador e redireciona para login.
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        # Cria hash da password
        hashed = generate_password_hash(form.password.data)
        # Insere na base de dados (is_admin=0 por defeito)
        user_id = create_user(form.username.data, form.email.data, hashed, is_admin=0)
        flash('Conta criada com sucesso! Já pode fazer login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Rota de login.
    GET: mostra formulário de login.
    POST: verifica credenciais e inicia sessão.
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_username(form.username.data)
        if user and check_password_hash(user['password_hash'], form.password.data):
            # Guarda informações do utilizador na sessão
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            flash('Login efetuado com sucesso!', 'success')
            # Redireciona para dashboard ou admin conforme perfil
            if user['is_admin']:
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('routes.dashboard'))
        else:
            flash('Credenciais inválidas. Tente novamente.', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    """
    Rota de logout: limpa a sessão e redireciona para a página inicial.
    """
    session.clear()
    flash('Sessão terminada. Até breve!', 'info')
    return redirect(url_for('routes.index'))