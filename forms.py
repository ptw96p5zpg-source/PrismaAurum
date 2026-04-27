# forms.py
# Define os formulários para registo, login, etc., usando Flask-WTF e validação.

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import get_user_by_username

class RegistrationForm(FlaskForm):
    """Formulário de registo de novo utilizador."""
    username = StringField('Nome de Utilizador', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Palavra-passe', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Palavra-passe', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registar')

    # Validação personalizada para verificar se username já existe
    def validate_username(self, username):
        user = get_user_by_username(username.data)
        if user:
            raise ValidationError('Nome de utilizador já registado. Escolha outro.')

class LoginForm(FlaskForm):
    """Formulário de login."""
    username = StringField('Nome de Utilizador', validators=[DataRequired()])
    password = PasswordField('Palavra-passe', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class ProductForm(FlaskForm):
    """Formulário para adicionar/editar produtos (admin)."""
    name = StringField('Nome do Produto', validators=[DataRequired()])
    description = TextAreaField('Descrição', validators=[DataRequired()])
    price = FloatField('Preço (Kz)', validators=[DataRequired()])
    weight = FloatField('Peso (g)', validators=[DataRequired()])
    purity = FloatField('Pureza (ex: 0.999)', validators=[DataRequired()])
    category = SelectField('Categoria', choices=[('ouro', 'Ouro'), ('prata', 'Prata')], validators=[DataRequired()])
    stock = IntegerField('Stock', validators=[DataRequired()])
    image = FileField('Imagem do Produto', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Apenas imagens permitidas.')])
    submit = SubmitField('Guardar Produto')

class AddToCartForm(FlaskForm):
    """Formulário simples para adicionar produto ao carrinho."""
    quantity = IntegerField('Quantidade', validators=[DataRequired()], default=1)
    submit = SubmitField('Adicionar ao Carrinho')