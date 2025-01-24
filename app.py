from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from crud import crear_persona, obtener_personas, actualizar_persona, eliminar_persona

app = Flask(__name__)

# Definir la carpeta donde se almacenarán las imágenes
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Función para verificar si el archivo tiene una extensión válida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    personas = obtener_personas()
    return render_template('index.html', personas=personas)

@app.route('/crear', methods=['POST'])
def crear():
    if request.method == 'POST':
        nombre = request.form['nombre']
        edad = int(request.form['edad'])
        correo = request.form['correo']
        
        # Manejo de la imagen
        foto = request.files.get('foto')
        foto_url = ''
        if foto and allowed_file(foto.filename):
            filename = secure_filename(foto.filename)
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            foto_url = url_for('static', filename='uploads/' + filename)

        crear_persona(nombre, edad, correo, foto_url)  # Pasamos la URL de la foto
        return redirect(url_for('index'))

@app.route('/actualizar/<int:id>', methods=['GET', 'POST'])
def actualizar(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        edad = int(request.form['edad'])
        correo = request.form['correo']

        # Actualizar la imagen si se sube una nueva
        foto = request.files.get('foto')
        foto_url = ''
        if foto and allowed_file(foto.filename):
            filename = secure_filename(foto.filename)
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            foto_url = url_for('static', filename='uploads/' + filename)
        
        actualizar_persona(id, nombre, edad, correo, foto_url)
        return redirect(url_for('index'))
    else:
        persona = obtener_personas()
        return render_template('actualizar.html', persona=persona)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    eliminar_persona(id)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)


    
