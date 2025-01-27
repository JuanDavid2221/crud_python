from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from crud import crear_producto, obtener_productos, actualizar_producto, eliminar_producto

# Crear la instancia de Flask
app = Flask(__name__)

# Definir la carpeta donde se almacenarán las imágenes
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Función para verificar si el archivo tiene una extensión válida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/inicio')
def inicio():
    return render_template('inicio.html')


# Ruta principal
@app.route('/')
def index():
    productos = obtener_productos()  # Obtener productos
    return render_template('index.html', productos=productos)

# Rutas para crear, actualizar, eliminar productos...
@app.route('/crear', methods=['POST'])
def crear():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        cantidad = int(request.form['cantidad'])

        # Manejo de la imagen
        foto = request.files.get('foto')
        foto_url = ''
        if foto and allowed_file(foto.filename):
            filename = secure_filename(foto.filename)
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            foto_url = url_for('static', filename='uploads/' + filename)

        crear_producto(nombre, descripcion, precio, cantidad, foto_url)  # Agregar el producto
        return redirect(url_for('index'))

@app.route('/actualizar/<int:id>', methods=['GET', 'POST'])
def actualizar(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        cantidad = int(request.form['cantidad'])
        foto = request.files.get('foto')
        foto_url = ''
        if foto and allowed_file(foto.filename):
            filename = secure_filename(foto.filename)
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            foto_url = url_for('static', filename='uploads/' + filename)

        actualizar_producto(id, nombre, descripcion, precio, cantidad, foto_url)
        return redirect(url_for('index'))
    else:
        productos = obtener_productos()
        producto = next(p for p in productos if p[0] == id)
        return render_template('actualizar.html', producto=producto)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    eliminar_producto(id)
    return redirect(url_for('index'))

# Iniciar la aplicación Flask
if __name__ == '__main__':
    app.run(debug=True)
