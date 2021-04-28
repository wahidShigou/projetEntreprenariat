from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from entrepreneuriat.models import Entrepreneur, Projet, Feedback

class InscriptionForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    nom = StringField('Nom', validators=[DataRequired()])
    prenom = StringField('Prenom', validators=[DataRequired()])
    adresse = StringField('adresse', validators=[DataRequired()])
    mdp = PasswordField('Mot de passe', validators=[DataRequired()])
    confirmer_mdp = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('mdp')])
    submit = SubmitField('S\'inscrire')

    def validate_login(self, login):
        entrepreneur = Entrepreneur.query.filter_by(login=login.data).first()
        if entrepreneur:
            raise ValidationError('Le login existe déjà')

class ConnexionForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    mdp = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Se connecter')


class ProjetForm(FlaskForm):
    nom_projet = StringField('Nom projet', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Publier')

    
class masCompteForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired()])
    prenom = StringField('Prenom', validators=[DataRequired()])
    adresse = StringField('adresse', validators=[DataRequired()])
    submit = SubmitField('Mettre à jour')


    


