from datetime import datetime
from flask import Flask, request, redirect, send_file, url_for, render_template, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.sql import func
import os
import pandas as pd
import qrcode
from zipfile import ZipFile
from io import BytesIO
from base64 import b64encode
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qrcode.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QRCodeEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    data = db.Column(db.Text, nullable=False)
    color = db.Column(db.Text, nullable=False)
    firstname = db.Column(db.Text, nullable=False)
    lastname = db.Column(db.Text, nullable=False)

ALLOWED_EXTENSIONS = {'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_field(field):
    if pd.isna(field):
        return None
    return str(field).strip()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        color = request.form.get('color', '#132DEA')
        if file and allowed_file(file.filename):
            session = Session()
            db.session.add(session)
            db.session.commit()
            process_save_data(file, session.id, color)
            flash('File uploaded and processed successfully!', 'success')
            return redirect(url_for('view_session', session_id=session.id))
        else:
            flash('Invalid file type. Please upload an .xlsx file.', 'error')
    return render_template('upload.html')

def process_save_data(file, session_id, color):
    df = pd.read_excel(file)
    for index, row in df.iterrows():
        firstname = clean_field(row.get('Prénom'))
        lastname = clean_field(row.get('Nom'))
        email = clean_field(row.get('E-mail'))
        phone = clean_field(row.get('Numéro de téléphone'))
        company = clean_field(row["Nom de l'entreprise"])
        job = clean_field(row['Intitulé du poste'])
        street = clean_field(row['Adresse postale'])
        city = clean_field(row['Ville'])
        zip_code = clean_field(row['Code postal'])
        country = clean_field(row['Pays/Région'])
        website = clean_field(row['URL du site web'])
        
        vcard_data = generate_vcard_data(firstname, lastname, email, phone, company, job, street, city, zip_code, country, website)
        qr_entry = QRCodeEntry(session_id=session_id, data=vcard_data, color=color, firstname=firstname, lastname=lastname)
        db.session.add(qr_entry)
    db.session.commit()

def generate_vcard_data(firstname, lastname, email, phone, company, job, street, city, zip, country, website):
    name = firstname + " " + lastname
    fields = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{lastname};{firstname}",
        f"FN:{name}",
        f"ORG:{company}" if company else "",
        f"TITLE:{job}" if job else "",
        f"ADR:;;{street};{city};;{zip};{country}" if street and city and zip and country else "",
        f"TEL:{phone}" if phone else "",
        f"EMAIL:{email}" if email else "",
        f"URL:{website}" if website else "",
        "END:VCARD"
    ]
    return '\n'.join(filter(None, fields))

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

@app.route('/session/<int:session_id>')
def view_session(session_id):
    session = Session.query.get_or_404(session_id)
    #qr_entries = QRCodeEntry.query.filter_by(session_id=session_id).all()
    sessions = Session.query.order_by(Session.created_at.desc()).all()
    return render_template('session_view.html', session=session, sessions=sessions)

@app.route('/download/session/<int:session_id>')
def download_session_zip(session_id):
    zip_filename = generate_and_zip_qr_codes(session_id)
    try:
        return send_file(zip_filename, as_attachment=True, download_name=f'session_{session_id}_qrcodes.zip')
    except Exception as e:
        return str(e)

def generate_and_zip_qr_codes(session_id):
    qr_entries = QRCodeEntry.query.filter_by(session_id=session_id).all()
    zip_filename = f'tmp/session_{session_id}.zip'
    os.makedirs(os.path.dirname(zip_filename), exist_ok=True)

    with ZipFile(zip_filename, 'w') as zipf:
        for entry in qr_entries:
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr.add_data(entry.data)
            qr.make(fit=True)
            img = qr.make_image(fill_color=entry.color, back_color="transparent").convert("RGBA")
            qr_filename = f'{entry.firstname}_{entry.lastname}.png'
            qr_path = f'tmp/{qr_filename}'
            img.save(qr_path)
            zipf.write(qr_path, arcname=qr_filename)
            os.remove(qr_path)
    return zip_filename