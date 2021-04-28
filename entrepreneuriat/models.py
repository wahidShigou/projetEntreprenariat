from datetime import datetime
from entrepreneuriat import db, login_manager
from flask_login import UserMixin
from sqlalchemy.sql import expression

@login_manager.user_loader
def load_entrepreneur(entrepreneur_id):
    return Entrepreneur.query.get(int(entrepreneur_id))


class Entrepreneur(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    nom = db.Column(db.String(20), nullable=False)
    prenom = db.Column(db.String(20), nullable=False)
    adresse = db.Column(db.String(20), nullable=False)
    mdp = db.Column(db.String(60), nullable=False)
    projets = db.relationship('Projet', backref='porteurP', lazy=True)
    feedbacks = db.relationship('Feedback', backref='feedbackE', lazy=True)

    def __repr__(self):
        return f"Entrepreneur('{ self.login }', '{ self.email }', '{ self.nom }', '{ self.prenom }', '{ self.adresse }', '{ self.mdp }')"

class Projet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_projet = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    date_publication = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    nbr_like = db.Column(db.String(20), nullable=False)
    nbr_deteste = db.Column(db.String(20), nullable=False)
    entrepreneur_id = db.Column(db.Integer, db.ForeignKey('entrepreneur.id'), nullable=False)
    feedbacks = db.relationship('Feedback', backref='feedbackP', lazy=True)
    def __repr__(self):
        return f"Projet('{ self.nom_projet }', '{ self.date_publication }', '{ self.description }', '{ self.nbr_like }', '{ self.nbr_deteste }')"


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commentaire = db.Column(db.String(100), nullable=False)
    aime = db.Column(db.Boolean,server_default=expression.false(), default=False, nullable=False)
    deteste = db.Column(db.Boolean,server_default=expression.false(), default=False, nullable=False)
    entrepreneur_reagi_id = db.Column(db.Integer, db.ForeignKey('entrepreneur.id'), nullable=False)
    projet_id = db.Column(db.Integer, db.ForeignKey('projet.id'), nullable=False)
    def __repr__(self):
        return f"Feedback('{ self.commentaire }', '{ self.aime }', '{ self.deteste }')"