import secrets
import os
import flask
from PIL import Image
from flask import render_template, flash, redirect, url_for, request, abort
from entrepreneuriat import app, db, bcrypt
from entrepreneuriat.forms import InscriptionForm, ConnexionForm, ProjetForm, masCompteForm
from entrepreneuriat.models import Entrepreneur, Projet, Feedback
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime


@app.route('/home')
def home():
    projets = Projet.query.all()
    return render_template('home.html', projets = projets)

@app.route('/feed/<int:projet_id>/<action>',  methods=['GET'])
@login_required
def feed_action(projet_id, action):
    if flask.request.method == 'GET':
        projet = Projet.query.filter_by(id=projet_id).first()
        feedback = Feedback.query.filter_by(id=projet_id).first()
        if action == 'like':
            if feedback == None or feedback.entrepreneur_reagi_id != current_user.id :
                projet.nbr_like = str(int(projet.nbr_like) + 1)
                feedback = Feedback(commentaire="", aime=True, deteste=False, feedbackE=current_user, feedbackP=projet)
                projet.feedbacks.append(feedback)
            db.session.commit()
        if action == 'unlike':
            if feedback == None or feedback.entrepreneur_reagi_id != current_user :
                projet.nbr_deteste = str(int(projet.nbr_deteste) + 1)
                feedback = Feedback(commentaire="", aime=False, deteste=True, feedbackE=current_user, feedbackP=projet)
                projet.feedbacks.append(feedback)
            db.session.commit()
        return redirect(url_for('home'))

@app.route('/feed/<int:projet_id>')
def get_nbr_like(projet_id):
    feedbacks = Feedback.query.filter_by(projet_id=projet_id).all()
    nbr_like = 0
    for feedback in feedbacks:
        if feedback.aime:
            nbr_like = nbr_like + 1
    return nbr_like


@app.route('/about')
def about():
    return render_template('about.html', title = 'about')
    
@app.route('/',  methods=['GET', 'POST'])
@app.route('/inscription', methods=['GET', 'POST'])
def inscrire():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = InscriptionForm()
    if form.validate_on_submit():
        mdp_crypte = bcrypt.generate_password_hash(form.mdp.data).decode('utf-8')
        entrepreneur = Entrepreneur(login = form.login.data, email=form.email.data,nom = form.nom.data,prenom = form.prenom.data, adresse = form.adresse.data, mdp=mdp_crypte)
        db.session.add(entrepreneur)
        db.session.commit()
        flash(f'Votre compte a été créé', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form=form)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ConnexionForm()
    if form.validate_on_submit():
        entrepreneur = Entrepreneur.query.filter_by(login=form.login.data).first()
        if entrepreneur and bcrypt.check_password_hash(entrepreneur.mdp, form.mdp.data):
            login_user(entrepreneur)
            return redirect(url_for('home'))
        else:
            flash('Erreur lors de la connexion', 'danger')
    return render_template('login.html', title = 'Connexion', form=form)
    
    
@app.route('/deconnexion')
def deconnexion():
    logout_user()
    return redirect(url_for('login'))




@app.route('/compte',  methods=['GET', 'POST'])
@login_required
def compte():
    form = masCompteForm()
    if form.validate_on_submit():
        current_user.nom = form.nom.data
        current_user.prenom = form.prenom.data
        current_user.adresse = form.adresse.data
        db.session.commit()
        flash('La mise à jour a été effectué!', 'success')
        return redirect(url_for('compte'))
    elif request.method == 'GET':
        form.nom.data = current_user.nom
        form.prenom.data = current_user.prenom
        form.adresse.data = current_user.adresse
    return render_template('account.html', title = 'Compte',  form = form)

@app.route('/nouveau_projet',  methods=['GET','POST'])
@login_required
def nouveau_projet():
    form = ProjetForm()
    if form.validate_on_submit():
        projet = Projet(nom_projet=form.nom_projet.data, description=form.description.data, porteurP=current_user, nbr_like="0",nbr_deteste="0")
        db.session.add(projet)
        db.session.commit()
        flash('Votre projet a été ajouté', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title = 'Nouveau projet', form=form, legend='Nouveau projet')

@app.route('/nouveau_projet/<int:projet_id>/<action>',  methods=['GET','POST'])
@login_required
def modification_projet(projet_id, action):
    projet = Projet.query.get_or_404(projet_id)
    form = ProjetForm()
    if action == 'delete':
        projet = Projet.query.get_or_404(projet_id)
        for feed in projet.feedbacks:
            db.session.delete(feed)
        db.session.delete(projet)
        db.session.commit()
        flash('Projet supprimé', 'success')
        projets = Projet.query.all()
        return render_template('mes_projets.html', projets = projets)
    if form.validate_on_submit():
        projet.nom_projet = form.nom_projet.data
        projet.description = form.description.data
        db.session.commit()
        flash('Le projet a été mis à jour', 'success')
        projets = Projet.query.all()
        return render_template('mes_projets.html', projets = projets)
    elif request.method == 'GET':
        form.nom_projet.data = projet.nom_projet
        form.description.data = projet.description
    return render_template('modification_projet.html', title = 'MAS projet', form = form, legend='Mis à jour du projet')

@app.route('/mes_projets/liste',  methods=['GET', 'POST'])
@login_required
def mes_projets():
    projets = Projet.query.filter_by(porteurP=current_user).all()
    return render_template('mes_projets.html', projets = projets)


@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route('/post/<int:post_id>/update',  methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('mesprojets.html', title = 'Update post', form = form, legend='Update Post')

@app.route('/post/<int:post_id>/delete',  methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('home'))