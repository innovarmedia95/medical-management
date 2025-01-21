import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import func, and_
import calendar

# Create Flask app
app = Flask(__name__)

# Configure database
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cabinet_medical.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Modèle Patient
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    date_naissance = db.Column(db.Date, nullable=False)
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    date_creation = db.Column(db.DateTime, nullable=True)
    visites = db.relationship('Visite', backref='patient', lazy=True)
    ordonnances = db.relationship('Ordonnance', backref='patient', lazy=True)

# Modèle Visite
class Visite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date_visite = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_controle = db.Column(db.DateTime)
    montant = db.Column(db.Float, nullable=False)
    paye = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    ordonnance = db.relationship('Ordonnance', backref='visite', lazy=True, uselist=False)

# Modèle Ordonnance
class Ordonnance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    visite_id = db.Column(db.Integer, db.ForeignKey('visite.id'), nullable=False)
    date_creation = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    contenu = db.Column(db.Text, nullable=False)
    medicaments = db.relationship('Medicament', backref='ordonnance', lazy=True)

# Modèle Medicament
class Medicament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ordonnance_id = db.Column(db.Integer, db.ForeignKey('ordonnance.id'), nullable=False)
    nom = db.Column(db.String(200), nullable=False)
    posologie = db.Column(db.String(200), nullable=False)
    duree = db.Column(db.String(100))

@app.route('/')
def accueil():
    try:
        # Statistiques pour la page d'accueil
        total_patients = Patient.query.count()
        
        visites_aujourdhui = Visite.query.filter(func.date(Visite.date_visite) == datetime.today().date()).count()
        
        revenus_mois = db.session.query(func.sum(Visite.montant)).filter(
            and_(
                func.strftime('%Y-%m', Visite.date_visite) == datetime.now().strftime('%Y-%m'),
                Visite.paye == True
            )
        ).scalar() or 0
        
        return render_template('accueil.html', 
                             total_patients=total_patients,
                             visites_aujourdhui=visites_aujourdhui,
                             revenus_mois=revenus_mois)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/patients')
def liste_patients():
    try:
        # Total Patients
        total_patients = Patient.query.count()
        
        # Nouveaux Patients (last 30 days)
        nouveaux_patients = Patient.query.filter(
            Patient.date_creation >= datetime.now() - timedelta(days=30)
        ).count()
        
        # Patients Actifs (visited in last 90 days)
        patients_actifs = db.session.query(Patient).join(Visite).filter(
            Visite.date_visite >= datetime.now() - timedelta(days=90)
        ).distinct().count()
        
        # Rendez-vous Aujourd'hui
        rendez_vous_aujourd_hui = Visite.query.filter(
            func.date(Visite.date_visite) == datetime.today().date()
        ).count()
        
        # Derniers Patients Ajoutés
        derniers_patients = Patient.query.order_by(
            Patient.date_creation.desc()
        ).limit(5).all()
        
        return render_template('patients.html', 
                               total_patients=total_patients,
                               nouveaux_patients=nouveaux_patients,
                               patients_actifs=patients_actifs,
                               rendez_vous_aujourd_hui=rendez_vous_aujourd_hui,
                               derniers_patients=derniers_patients)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/patient/nouveau', methods=['GET', 'POST'])
def nouveau_patient():
    try:
        if request.method == 'POST':
            nom = request.form['nom']
            prenom = request.form['prenom']
            date_naissance = datetime.strptime(request.form['date_naissance'], '%Y-%m-%d')
            telephone = request.form['telephone']
            email = request.form['email']

            patient = Patient(nom=nom, prenom=prenom, date_naissance=date_naissance,
                            telephone=telephone, email=email)
            db.session.add(patient)
            db.session.commit()
            flash('Patient ajouté avec succès!', 'success')
            return redirect(url_for('liste_patients'))
        return render_template('nouveau_patient.html')
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/visite/nouvelle/<int:patient_id>', methods=['GET', 'POST'])
def nouvelle_visite(patient_id):
    try:
        if request.method == 'POST':
            # Récupérer la date de visite du formulaire
            date_visite = datetime.strptime(request.form['date_visite'], '%Y-%m-%d')
            
            # Récupérer la date de contrôle si elle est spécifiée
            date_controle = None
            if request.form['date_controle']:
                date_controle = datetime.strptime(request.form['date_controle'], '%Y-%m-%d')
            
            # Créer la visite
            visite = Visite(
                patient_id=patient_id,
                date_visite=date_visite,
                date_controle=date_controle,
                montant=float(request.form['montant']),
                paye='paye' in request.form,
                notes=request.form['notes']
            )
            db.session.add(visite)
            db.session.commit()
            
            # Si une ordonnance est nécessaire, rediriger vers la création d'ordonnance
            if 'creer_ordonnance' in request.form:
                return redirect(url_for('nouvelle_ordonnance', visite_id=visite.id))
                
            flash('Visite enregistrée avec succès!', 'success')
            return redirect(url_for('liste_patients'))
        
        patient = Patient.query.get_or_404(patient_id)
        return render_template('nouvelle_visite.html', 
                             patient=patient,
                             today=datetime.now().strftime('%Y-%m-%d'))
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/calendrier')
def calendrier():
    try:
        annee = int(request.args.get('annee', datetime.now().year))
        mois = int(request.args.get('mois', datetime.now().month))
        
        # Obtenir toutes les visites du mois
        debut_mois = datetime(annee, mois, 1)
        if mois == 12:
            fin_mois = datetime(annee + 1, 1, 1)
        else:
            fin_mois = datetime(annee, mois + 1, 1)
        
        visites = Visite.query.filter(
            and_(Visite.date_visite >= debut_mois,
                 Visite.date_visite < fin_mois)
        ).all()
        
        # Créer le calendrier
        cal = calendar.monthcalendar(annee, mois)
        return render_template('calendrier.html', 
                             calendrier=cal,
                             visites=visites,
                             annee=annee,
                             mois=mois,
                             nom_mois=calendar.month_name[mois])
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/statistiques')
def statistiques():
    try:
        # Statistiques des visites
        total_visites = Visite.query.count()
        
        visites_mois = Visite.query.filter(
            func.strftime('%Y-%m', Visite.date_visite) == datetime.now().strftime('%Y-%m')
        ).count()
        
        # Statistiques financières
        revenus_total = db.session.query(func.sum(Visite.montant)).filter(Visite.paye == True).scalar() or 0
        
        revenus_mois = db.session.query(func.sum(Visite.montant)).filter(
            and_(
                func.strftime('%Y-%m', Visite.date_visite) == datetime.now().strftime('%Y-%m'),
                Visite.paye == True
            )
        ).scalar() or 0
        
        # Patients par mois
        patients_mois = Patient.query.filter(
            func.strftime('%Y-%m', Patient.id) == datetime.now().strftime('%Y-%m')
        ).count()
        
        return render_template('statistiques.html',
                             total_visites=total_visites,
                             visites_mois=visites_mois,
                             revenus_total=revenus_total,
                             revenus_mois=revenus_mois,
                             patients_mois=patients_mois)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/ordonnances/nouvelle/<int:visite_id>', methods=['GET', 'POST'])
def nouvelle_ordonnance(visite_id):
    try:
        visite = Visite.query.get_or_404(visite_id)
        if request.method == 'POST':
            ordonnance = Ordonnance(
                patient_id=visite.patient_id,
                visite_id=visite_id,
                contenu=request.form['contenu']
            )
            db.session.add(ordonnance)
            
            # Ajouter les médicaments
            medicaments = request.form.getlist('medicament[]')
            posologies = request.form.getlist('posologie[]')
            durees = request.form.getlist('duree[]')
            
            for med, pos, dur in zip(medicaments, posologies, durees):
                if med and pos:  # Vérifier que le médicament et la posologie sont renseignés
                    medicament = Medicament(
                        ordonnance=ordonnance,
                        nom=med,
                        posologie=pos,
                        duree=dur
                    )
                    db.session.add(medicament)
            
            db.session.commit()
            flash('Ordonnance créée avec succès!', 'success')
            return redirect(url_for('liste_patients'))
        return render_template('nouvelle_ordonnance.html', visite=visite)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/rapports/financier')
def rapport_financier():
    try:
        mois = int(request.args.get('mois', datetime.now().month))
        annee = int(request.args.get('annee', datetime.now().year))
        
        debut_mois = datetime(annee, mois, 1)
        if mois == 12:
            fin_mois = datetime(annee + 1, 1, 1)
        else:
            fin_mois = datetime(annee, mois + 1, 1)
        
        # Revenus du mois
        visites = Visite.query.filter(
            and_(
                Visite.date_visite >= debut_mois,
                Visite.date_visite < fin_mois
            )
        ).all()
        
        total_revenus = sum(v.montant for v in visites if v.paye)
        
        total_non_paye = sum(v.montant for v in visites if not v.paye)
        
        return render_template('rapport_financier.html',
                             visites=visites,
                             total_revenus=total_revenus,
                             total_non_paye=total_non_paye,
                             mois=mois,
                             annee=annee)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)

app = app
