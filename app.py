
from flask import Flask, render_template, redirect, url_for
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
app = Flask(__name__)
bcrypt = Bcrypt(app)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SECRET_KEY'] ='mysecretkey'
# initialize the app with the extension
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(str(Users))




class Users(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    identifiant = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

class RegisterForm(FlaskForm):
    identifiant = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Identifiant"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Register")

    def validate_identifiant(self, identifiant):
        existing_user_identifiant = Users.query.filter_by(
            identifiant=identifiant.data).first()

        if existing_user_identifiant:
            raise ValidationError(
                "that identifiant alredy exists. please choose a different identifiant"
            )

class LoginForm(FlaskForm):
        identifiant = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                                      render_kw={"placeholder": "Identifiant"})
        password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)],
                                     render_kw={"placeholder": "Password"})

        submit = SubmitField("Login")




class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(255), nullable=False)
    depense = db.relationship('Depense', backref='service')
    recette = db.relationship('Recette', backref='Service')


class Depense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_compta = db.Column(db.Integer, nullable=False)
    beneficiaire = db.Column(db.Integer, nullable=False)
    montant = db.Column(db.Integer, nullable=False)
    motif = db.Column(db.String(255), nullable=False)
    service_id = db.Column(db.String, db.ForeignKey('service.id'))



class Recette(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_compta = db.Column(db.Integer, nullable=False)
    montant = db.Column(db.Integer, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))




@app.route("/login", methods=["POST", "GET"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(identifiant=form.identifiant.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                load_user(user)
                return redirect(url_for('tab_afficher_depense'))
    return render_template('pages/betails/login.html', form=form)

@app.route("/", methods=["POST", "GET"])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        new_identifiant=Users(identifiant=form.identifiant.data, password=hash_password)
        db.session.add(new_identifiant)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('pages/betails/register.html', form=form)


@app.route("/index")
def home():
    render_template('index.html')


@app.route("/form_ajout_depense_betails", methods=["GET", "POST"])
def form_ajout_depense_betails():
        if request.method == "POST":
            depense=Depense(
            plan_compta = request.form['plan_compta'],
            beneficiaire = request.form['beneficiaire'],
            montant = request.form['montant'],
            motif = request.form['motif'],
            service_id = request.form['service'])
            db.session.add(depense)
            db.session.commit()
        return render_template('./pages/betails/form_ajout_depense_betails.html')

@app.route("/tab_afficher_depense")
def tab_afficher_depense():
    depense=Depense.query.all()
    return render_template('pages/betails/tab_afficher_depense.html', depense=depense)

@app.route("/<int:depense_id>", methods=["GET", "POST"])
def modifier_depense_betails(depense_id):
    depense = Depense.query.get_or_404(depense_id)
    if request.method == "POST":
       
       
        beneficiaire = request.form['beneficiaire']
        plan_compta = request.form['plan_compta']
        motif = request.form['motif']
        montant = request.form['montant']


        depense.plan_compta = plan_compta
        depense.beneficiaire = beneficiaire
        depense.motif = motif
        depense.montant = montant


        db.session.add(depense)
        db.session.commit()
        return redirect(url_for('tab_afficher_depense'))
    return render_template('pages/betails/modifier_depense_betails.html', depense=depense)


@app.route("/delete/<int:id>", methods=('GET','POST'))
def delete_depense_betails(id):
    if request.method == "GET":
        depense = Depense.query.filter_by(id=id).first()
        db.session.delete(depense)
        db.session.commit()
        return redirect('/tab_afficher_depense')
    return render_template("pages/betails/tab_afficher_depense.html")









@app.route("/form_ajout_recette_betails", methods=["GET", "POST"])
def form_ajout_recette_betails():
    if request.method == "POST":
        recette = Recette(
        plan_compta=request.form['plan_compta'],
        montant=request.form['montant'])
        db.session.add(recette)
        db.session.commit()
    return render_template('./pages/betails/form_ajout_recette_betails.html')

@app.route("/tab_afficher_recette")
def tab_afficher_recette():
        recette = Recette.query.all()
        return render_template('pages/betails/tab_afficher_recette.html', recette=recette)


@app.route("/<int:recette_id>/modifier_recette_betails", methods=["GET", "POST"])
def modifier_recette_betails(recette_id):
    recette = Recette.query.get_or_404(recette_id)
    if request.method =="POST":

        plan_compta = request.form['plan_compta']
        montant = request.form['montant']

        recette.plan_compta = plan_compta
        recette.montant = montant

        db.session.add(recette)
        db.session.commit()

        return redirect(url_for('tab_afficher_recette'))
    return render_template('pages/betails/modifier_recette_betails.html', recette=recette)


@app.route("/delete/<int:id>", methods=('GET', 'POST'))
def delete_recette_betails(id):
    if request.method == "GET":
        recette = Recette.query.filter_by(id=id).first()
        db.session.delete(recette)
        db.session.commit()
        return redirect('/tab_afficher_recette')
    return render_template("pages/betails/tab_afficher_recette.html")






@app.route("/form_ajout_depense_abattage", methods=["GET", "POST"])
def form_ajout_depense_abattage():
    if request.method == "POST":
            depense = Depense(
            plan_compta = request.form['plan_compta'],
            beneficiaire = request.form['beneficiaire'],
            montant = request.form['montant'],
            motif=request.form['motif'],
            service_id = request.form['service'])
            db.session.add(depense)
            db.session.commit()
    return render_template("pages/abattage/form_ajout_depense_abattage.html")



@app.route("/tab_afficher_depense_abattage")
def tab_afficher_depense_abattage():
    depense=Depense.query.all()
    return render_template('pages/abattage/tab_afficher_depense_abattage.html', depense=depense)


@app.route("/<int:depense_id>", methods=["GET", "POST"])
def modifier_depense_abattage(depense_id):
    depense = Depense.query.get_or_404(depense_id)
    if request.method == "POST":

        beneficiaire = request.form['beneficiaire']
        plan_compta = request.form['plan_compta']
        motif = request.form['motif']
        montant = request.form['montant']

        depense.plan_compta = plan_compta
        depense.beneficiaire = beneficiaire
        depense.motif = motif
        depense.montant = montant

        db.session.add(depense)
        db.session.commit()
        return redirect(url_for('tab_afficher_depense_abattage'))
    return render_template('pages/betails/ modifier_depense_abattage.html', depense=depense)



@app.route("/delete/<int:id>", methods=["GET", "POST"])

def delete_depense_abattage(id):
    if request.method=="GET":
        depense = Depense.query.filter_by(id=id).first()
        db.session.delete(depense)
        db.session.commit()
        return redirect('/tab_afficher_depense_abattage')
    return render_template("pages/abattage/tab_afficher_depense_abattage.html")







@app.route("/form_ajout_recette_abattage", methods=["GET", "POST"])
def form_ajout_recette_abattage():
    if request.method == "POST":
            recette = Recette(
            plan_compta=request.form['plan_compta'],
            montant=request.form['montant'])
            db.session.add(recette)
            db.session.commit()
    return render_template("pages/abattage/form_ajout_recette_abattage.html")


@app.route("/tab_afficher_recette_abattage")
def tab_afficher_recette_abattage():
    recette=Recette.query.all()
    return render_template("pages/abattage/tab_afficher_recette_abattage.html", recette=recette)



@app.route("/<int:recette_id>/modifier_recette_abattage", methods=["GET", "POST"])
def modifier_recette_abattage(recette_id):
    recette = Recette.query.get_or_404(recette_id)
    if request.method == "POST":
        plan_compta = request.form['plan_compta']
        montant = request.form['montant']

        recette.plan_compta = plan_compta
        recette.montant = montant

        db.session.add(recette)
        db.session.commit()
        return redirect(url_for('tab_afficher_recette_abattage'))
    return render_template("pages/abattage/modifier_recette_abattage.html", recette=recette)


@app.route("/delete<int:id>", methods=["GET", "POST"])
def delete_recette_abattage(id):
    if request.method == "GET":
        recette = Recette.query.filter_by(id=id).first()
        db.session.delete(recette)
        db.session.commit()
        return redirect(url_for('tab_afficher_recette_abattage'))
    return render_template("pages/abattage/tab_afficher_recette_abattage.html")


@app.route("/form_ajout_depense_loyer", methods=["GET", "POST"])
def form_ajout_depense_loyer():
    if request.method == "POST":
            depense=Depense(
            plan_compta=request.form['plan_compta'],
            beneficiaire=request.form['beneficiaire'],
            montant =request.form['montant'],
            motif=request.form['motif'],
            service_id =request.form['service'])
            db.session.add(depense)
            db.session.commit()
    return render_template("pages/loyer/form_ajout_depense_loyer.html")


@app.route("/tab_afficher_depense_loyer")
def tab_afficher_depense_loyer():
    depense=Depense.query.all()
    return render_template("pages/loyer/tab_afficher_depense_loyer.html", depense=depense)

@app.route("/<int:depense_id>", methods=["GET", "POST"])
def modifier_depense_loyer(depense_id):
    depense=Depense.query.get_or_404(depense_id)

    if request.method =="POST":
        beneficiaire=request.form['beneficiaire']
        plan_compta=request.form['plan_compta']
        motif=request.form['motif']
        montant=request.form['montant']

        depense.plan_compta=plan_compta
        depense.beneficiaire=beneficiaire
        depense.motif=motif
        depense.montant=montant

        db.session.add(depense)
        db.session.commit()
        return redirect(url_for('tab_afficher_depense_loyer'))
    return render_template('pages/loyer/modifier_depense_loyer.html', depense=depense)



@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete_depense_loyer(id):
    if request.method=="GET":
        depense=Depense.query.filter_by(id=id).first()
        db.session.delete(depense)
        db.session.commit()
    return render_template("pages/loyer/tab_afficher_depense_loyer.html")



@app.route("/form_ajout_recette_loyer", methods=["GET", "POST"])
def form_ajout_recette_loyer():
    if request.method=="POST":
            recette= Recette(
            plan_compta=request.form['plan_compta'],
            montant=request.form['montant'])
            db.session.add(recette)
            db.session.commit()
    return render_template('pages/loyer/form_ajout_recette_loyer.html')


@app.route("/tab_afficher_recette_loyer")
def tab_afficher_recette_loyer():
    recette=Recette.query.all()
    return render_template('pages/loyer/tab_afficher_recette_loyer.html', recette=recette)


@app.route("/<int:recette_id>/modifier_recette_loyer", methods=["GET","POST"])
def modifier_recette_loyer(recette_id):
    recette=Recette.query.get_or_404(recette_id)
    if request.method=="POST":
        plan_compta=request.form['plan_compta']
        montant=request.form['montant']

        recette.plan_compta=plan_compta
        recette.montant=montant

        db.session.add(recette)
        db.session.commit()
        return redirect((url_for('tab_afficher_recette_loyer')))
    return render_template('pages/loyer/modifier_recette_loyer.html', recette=recette)



@app.route("/delete/<int:id>", methods=["GET","POST"])
def delete_recette_loyer(id):
    if request.method == "GET":
        recette = Recette.query.filter_by(id=id).first()
        db.session.delete(recette)
        db.session.commit()
        return redirect(url_for('tab_afficher_recette_loyer'))
    return render_template("pages/loyer/tab_afficher_recette_loyer.html")





if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)