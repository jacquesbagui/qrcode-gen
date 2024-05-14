from datetime import datetime
import os
from flask import Flask, flash, request, send_from_directory, render_template, redirect, url_for
import pandas as pd
import qrcode
from PIL import Image
import zipfile
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(24)  
ALLOWED_EXTENSIONS = {'xlsx'}

# Base directories
UPLOAD_FOLDER = 'uploads'
BASE_QR_CODE_FOLDER = 'qr_codes'

# Ensure base upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_field(field):
    if pd.isna(field):
        return None
    return str(field).strip()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
        color = request.form.get('color', '#132DEA')  # Default color
        if file and allowed_file(file.filename):
            session_id = datetime.now().strftime("%Y%m%d%H%M%S")
            session_folder = os.path.join(BASE_QR_CODE_FOLDER, session_id)
            os.makedirs(session_folder, exist_ok=True)
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            flash('File uploaded successfully! Generating QR codes...', 'success')
            if generate_qr_codes(filepath, color, session_folder):
                return redirect(url_for('download_folder', folder=session_id))
        else:
            flash('Invalid file type. Please upload an .xlsx file.', 'error')
    return render_template('upload.html')


def generate_vcard_data(firstname, lastname, email, phone, company, job, street, city, zip, country, website):
    name = firstname + " " + lastname
    fields = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{lastname};{firstname}",
        f"FN:{name}"
    ]
    
    if company:
        fields.append(f"ORG:{company}")
    if job:
        fields.append(f"TITLE:{job}")
    if street and city and zip and country:
        fields.append(f"ADR:;;{street};{city};;{zip};{country}")
    if phone:
        fields.append(f"TEL:{phone}")
    if email:
        fields.append(f"EMAIL:{email}")
    if website:
        fields.append(f"URL:{website}")
    
    fields.append("END:VCARD")
    
    return '\n'.join(fields)

def generate_vcard_qr_code(firstname, lastname, email, phone, company, job, street, city, zip, country, website, color, output_path):    
    vcard_data = generate_vcard_data(firstname, lastname, email, phone, company, job, street, city, zip, country, website)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(vcard_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=color, back_color="transparent").convert("RGBA")

    # Save the final image
    img.save(output_path)


def verify_columns(df, expected_columns):
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        flash(f"Les colonnes suivantes sont manquantes dans le DataFrame: {', '.join(missing_columns)}", 'error')
        raise ValueError(f"Les colonnes suivantes sont manquantes dans le DataFrame: {', '.join(missing_columns)}")
    return True

def generate_qr_codes(filepath, color, session_folder):
    employee_data = pd.read_excel(filepath)
    
    
    # Liste des noms de colonnes attendues
    expected_columns = [
        'Prénom', 'Nom', 'E-mail', 'Numéro de téléphone', "Nom de l'entreprise", 
        'Intitulé du poste', 'Adresse postale', 'Ville', 'Code postal', 'Pays/Région', 'URL du site web'
    ]
    
    # Vérification des colonnes
    try:
        missing_columns = [col for col in expected_columns if col not in employee_data.columns]
        if missing_columns:
            flash(f"Les colonnes suivantes sont manquantes dans le DataFrame: {', '.join(missing_columns)}", 'error')
            print(f"Les colonnes suivantes sont manquantes dans le DataFrame: {', '.join(missing_columns)}")
            return False
        for index, row in employee_data.iterrows():
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
            
            output_path = f"{session_folder}/{firstname}-{lastname}.png"
            if not os.path.exists(output_path):  # Generate only if it doesn't exist
                generate_vcard_qr_code(firstname, lastname, email, phone, company, job, street, city, zip_code, country, website, color, output_path)
            else:
                print(f"Skipping generation for {output_path}: File already exists.")
        return True
    except ValueError as e:
        print(e)
        return

def zip_folder(folder_path, output_path):
    """Zip the contents of an entire folder (with subfolders) into a zip file."""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(folder_path, '..')))
                
@app.route('/download/folder/<folder>')
def download_folder(folder):
    directory = os.path.join(BASE_QR_CODE_FOLDER, folder)
    if os.path.exists(directory):
        zip_path = f"{directory}.zip"        
        if not os.path.exists(zip_path):
            zip_folder(directory, zip_path)
        return send_from_directory(os.path.dirname(zip_path), os.path.basename(zip_path), as_attachment=True)
    else:
        return "Folder not found.", 404


if __name__ == '__main__':
    app.run(debug=True)
