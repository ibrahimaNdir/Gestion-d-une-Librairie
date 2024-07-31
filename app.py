from flask import Flask, render_template,request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,login_required, logout_user,current_user,LoginManager,UserMixin
from datetime import datetime , timedelta
from sqlalchemy import and_
import os
from dotenv import load_dotenv 
from werkzeug.utils import secure_filename




# Charger les variables d'environnement
load_dotenv()

# Initialiser l'application Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'

# Charger la configuration depuis le fichier config.py
app.config.from_object('config.Config')

# Initialiser SQLAlchemy
db = SQLAlchemy(app)
migrate = Migrate(app, db)



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  

app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
 
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False) 
    email = db.Column(db.String(150), unique=True, nullable=False)  
    password = db.Column(db.String(200), nullable=False)  
    adresse = db.Column(db.String(200))  
    emprunt = db.relationship('Emprunt', backref='user', lazy=True) 


class Livre(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), unique=True, nullable=False) 
    auteur = db.Column(db.String(150), nullable=False)  
    annee = db.Column(db.Integer, nullable=False)
    image_path = db.Column(db.String(150), nullable=False) 
    emprunt = db.relationship('Emprunt', backref='livre', lazy=True)


class Emprunt(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150),  nullable=False) 
    date_pret = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_fin_pret = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)   
    livre_id = db.Column(db.Integer, db.ForeignKey('livre.id'), nullable=False)
       
       



@login_manager.user_loader
def load_user(user_id):
    return User.query.get_or_404(int(user_id))

# LOGIN ADMIN
@app.route('/A_login',methods=['GET','POST'])  
def A_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password =   request.form.get('password')  

        user = User.query.filter_by( username = username ).first() 
        if user and check_password_hash(user.password,password): #le mdp du users et le mdp fourni dans le formulaire on les compare
            login_user(user)                                     #  enregister le user connecter dans le session
            flash('Connexion Reussi')
            return redirect(url_for('A_acceuil')) 
        else:
            flash('Erreur de Connexion')
            return redirect(url_for('A_login'))
        
    return render_template('A_login.html')
    
# LOGIN USER

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password =   request.form.get('password')  

        user = User.query.filter_by( username = username ).first() 
        if user and check_password_hash(user.password,password): #le mdp du users et le mdp fourni dans le formulaire on les compare
            login_user(user)                                     #  enregister le user connecter dans le session
            flash('Connexion Reussi')
            return redirect(url_for('acceuil')) 
        else:
            flash('Erreur de Connexion')
            return redirect(url_for('login'))

        

    return render_template('login.html')

# REGISTER ADMIN

@app.route('/A_register',methods=['GET','POST'])  #register admin
def A_register():                      
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        adresse = request.form.get('adresse')
        password = request.form.get('password')

        # Vérifier que tous les champs sont remplis
        if not username or not email or not password:
            flash('Tous les champs obligatoires doivent être remplis')
            return redirect(url_for('A_register'))

        # Vérifier si l'utilisateur ou l'email existe déjà
        user_by_username = User.query.filter_by(username=username).first()
        user_by_email = User.query.filter_by(email=email).first()
        
        if user_by_username or user_by_email:
            flash('Ce nom d\'utilisateur ou cet email existe déjà dans la base')
            return redirect(url_for('A_register'))

        # Hasher le mot de passe
        hashed_password = generate_password_hash(password)

        # Créer un nouvel utilisateur
        new_user = User(username=username, email=email, adresse=adresse, password=hashed_password)

        # Ajouter l'utilisateur à la base de données
        db.session.add(new_user)
        db.session.commit()

        flash('Inscription réussie')
        return redirect(url_for('A_login'))

    return render_template('A_register.html')

# REGISTER USER

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        adresse = request.form.get('adresse')
        password = request.form.get('password')

        # Vérifier que tous les champs sont remplis
        if not username or not email or not password:
            flash('Tous les champs obligatoires doivent être remplis')
            return redirect(url_for('register'))

        # Vérifier si l'utilisateur ou l'email existe déjà
        user_by_username = User.query.filter_by(username=username).first()
        user_by_email = User.query.filter_by(email=email).first()
        
        if user_by_username or user_by_email:
            flash('Ce nom d\'utilisateur ou cet email existe déjà dans la base')
            return redirect(url_for('register'))

        # Hasher le mot de passe
        hashed_password = generate_password_hash(password)

        # Créer un nouvel utilisateur
        new_user = User(username=username, email=email, adresse=adresse, password=hashed_password)

        # Ajouter l'utilisateur à la base de données
        db.session.add(new_user)
        db.session.commit()

        flash('Inscription réussie')
        return redirect(url_for('login'))

    return render_template('register.html')
    

@app.route('/A')
@login_required
def A_acceuil():
   return render_template('A_acceuil.html')

@app.route('/')
@login_required
def acceuil():
   livres = Livre.query.all()
   return render_template('acceuil.html', livres=livres) 

@app.route('/A_logout') 
@login_required
def A_logout():
    logout_user()
    return redirect(url_for('A_login'))

@app.route('/logout') 
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/addLivre', methods=['GET', 'POST'])
@login_required
def addLivre():
    if request.method == 'POST':
        nom = request.form.get('nom')
        auteur = request.form.get('auteur')
        annee = request.form.get('annee')
        image = request.files['image']

        # Valider les données
        if not nom or not auteur or not annee or not image:
            flash('Tous les champs doivent être remplis')
            return redirect(url_for('addLivre'))

        # Enregistrer l'image
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
       

        # Créer un nouvel livre avec le chemin d'accès relatif de l'image
        new_book = Livre(nom=nom, auteur=auteur, annee=annee, image_path= filename)

        # Ajouter le livre à la base de données
        db.session.add(new_book)
        db.session.commit()

        flash('Livre ajouté avec succès')
        return redirect(url_for('acceuil'))

    return render_template('addLivre.html')



# Liste les contacts suivants d'éventuels filtres  
@app.route('/searchlivre', methods=['GET', 'POST'])
def get_search_livre():
    nom = request.form.get('nom')
    auteur = request.form.get('auteur')
    annee = request.form.get('annee')

    filters = []
    if nom:
        filters.append(Livre.nom.ilike(f'%{nom}%'))
    if auteur:
        filters.append(Livre.auteur.ilike(f'%{auteur}%'))
    if annee:
        filters.append(Livre.annee.ilike(f'%{annee}%'))
       

    if filters:
        livres = Livre.query.filter(and_(*filters)).all()
    else:
        livres = Livre.query.all()

    return render_template('search_livre.html', livres=livres)


@app.route('/users')
@login_required
def users():
    users = User.query.all()
    return render_template('users.html', users=users)   


@app.route('/livres')
@login_required
def livres():
    livres = Livre.query.all()
    return render_template('livres.html', livres=livres)   

@app.route('/tabemprunts')
@login_required
def tabemprunts():
    tabemprunts = Emprunt.query.all()
    return render_template('tabemprunts.html', tabemprunts=tabemprunts)   


@app.route('/useremprunts')
@login_required
def useremprunts():
    useremprunts = Emprunt.query.all()
    return render_template('useremprunt.html', useremprunts=useremprunts)   


                                                                                                                                                           
@app.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Utilisateur supprimé avec succès')
    return redirect(url_for('users'))


@app.route('/delete_livre/<int:livre_id>')
@login_required
def delete_livre(livre_id):
    livre = Livre.query.get_or_404(livre_id) 
    db.session.delete(livre)
    db.session.commit()
    flash(' supprimé avec succès')
    return redirect(url_for('livres')) 

@app.route('/delete_emprunt/<int:emprunt_id>')
@login_required
def delete_emprunt(emprunt_id):
    emprunt = Emprunt.query.get_or_404(emprunt_id) 
    db.session.delete(emprunt)
    db.session.commit()
    flash(' Emprunt supprimé avec succès')
    return redirect(url_for('tabemprunts'))

@app.route("/update_livre/<int:id>", methods=["GET", "POST"])
@login_required
def update_livre(livre_id):
    livre = Livre.query.get_or_404(livre_id)
    if request.method == "POST":
        livre.nom = request.form.get("nom")
        livre.auteur = request.form.get("auteur")
        annee = request.form.get("annee")
        if annee:
            livre.annee = int(annee)
        
        db.session.commit()
        flash('Livre mis à jour avec succès', 'success')
        return redirect(url_for('livres'))
    
    return render_template("update_livre.html", livre=livre)
    


@app.route('/emprunt-livre/<int:livre_id>', methods=['GET', 'POST'])
@login_required
def emprunt_livre(livre_id):
    livre = Livre.query.get_or_404(livre_id)
    nom_livre = livre.nom
    date_pret = datetime.utcnow().date()
    date_retour = date_pret + timedelta(days=15)

    if request.method == 'POST':
        date_pret = datetime.strptime(request.form.get('date_pret'), '%Y-%m-%d').date()
        date_retour = datetime.strptime(request.form.get('date_retour'), '%Y-%m-%d').date()

        if date_retour <= date_pret:
            flash('La date de retour doit être postérieure à la date de prêt')
            return redirect(url_for('emprunt_livre', livre_id=livre.id))

        if (date_retour - date_pret).days > 15:
            flash('L\'écart entre la date de prêt et la date de retour ne doit pas dépasser 7 jours')
            return redirect(url_for('emprunt_livre', livre_id=livre.id))

        new_emprunt = Emprunt(
            nom=nom_livre,
            date_pret=date_pret,
            date_fin_pret=date_retour,
            user_id=current_user.id,
            livre_id=livre.id
        )

        db.session.add(new_emprunt)
        db.session.commit()

        flash('Emprunt effectué avec succès')
        return redirect(url_for('acceuil'))

    return render_template('emprunt.html', livre=livre, nom_livre=nom_livre, date_pret=date_pret, date_retour=date_retour)


if __name__ == "__main__":
    app.run(debug=True)
