from flask import Flask, render_template, request, redirect, url_for, session
import os
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
import mysql.connector
from crud import crear_producto, obtener_productos, actualizar_producto, eliminar_producto

# Crear la instancia de Flask
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Necesario para mantener sesiones en Flask

# Configurar la conexión a la base de datos
db = mysql.connector.connect(
    host="localhost",
    user="root",  # Cambia esto si usas otro usuario de MySQL
    password="",  # Cambia esto si tienes contraseña para MySQL
    database="crud_db"  # El nombre de tu base de datos
)

cursor = db.cursor()

# Definir la carpeta donde se almacenarán las imágenes
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Función para verificar si el archivo tiene una extensión válida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Función para verificar usuario y contraseña
def verificar_usuario(campo, valor, contraseña):
    query = f"SELECT * FROM usuarios WHERE {campo} = %s"
    cursor.execute(query, (valor,))
    usuario = cursor.fetchone()
    if usuario and check_password_hash(usuario[4], contraseña):  # Verifica la contraseña con hash
        return usuario
    return None

# Ruta de inicio de sesión
@app.route('/sesion', methods=['GET', 'POST'])
def sesion():
    if request.method == 'POST':
        login = request.form['login']
        contraseña = request.form['contraseña']

        # Verifica si es correo o nombre de usuario
        usuario = None
        if '@' in login:
            # Buscar por correo
            usuario = verificar_usuario('correo', login, contraseña)
        else:
            # Buscar por nombre de usuario
            usuario = verificar_usuario('usuario', login, contraseña)

        if usuario:
            # Si el usuario existe y la contraseña es correcta, inicia sesión
            session['usuario_id'] = usuario[0]  # Guardamos el id del usuario en la sesión
            session['nombre_usuario'] = usuario[2]  # Guardamos el nombre de usuario
            return redirect(url_for('inicio'))  # Redirigir a la página de inicio
        else:
            # Si no se encuentra el usuario o la contraseña es incorrecta
            return render_template('sesion.html', error="Usuario o contraseña incorrectos.")
    
    return render_template('sesion.html')

# Ruta de inicio
@app.route('/inicio')
def inicio():
    if 'usuario_id' not in session:
        return redirect(url_for('sesion'))  # Si no hay sesión, redirige al login
    return render_template('inicio.html')

# Ruta de registro
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']
        confirmar_contraseña = request.form['confirmar-contraseña']
        fecha_nacimiento = request.form['fecha-nacimiento']
        telefono = request.form.get('telefono', '')  # Si no se proporciona, se dejará vacío

        # Validación de contraseñas
        if contraseña != confirmar_contraseña:
            return render_template('registro.html', error="Las contraseñas no coinciden.")

        # Encriptar la contraseña
        contraseña_hash = generate_password_hash(contraseña)

        # Registrar el usuario
        try:
            query = """
            INSERT INTO usuarios (nombre, correo, usuario, contraseña, fecha_nacimiento, telefono)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (nombre, correo, usuario, contraseña_hash, fecha_nacimiento, telefono)
            cursor.execute(query, values)
            db.commit()  # Guardar los cambios en la base de datos
        except mysql.connector.Error as err:
            print(f"Error al registrar el usuario: {err}")
            db.rollback()  # Deshacer si ocurre un error

        return redirect(url_for('inicio'))  # Redirigir al inicio después de un registro exitoso

    return render_template('registro.html')

# Ruta de logout
@app.route('/logout')
def logout():
    session.pop('usuario_id', None)  # Elimina el usuario de la sesión
    session.pop('nombre_usuario', None)
    return redirect(url_for('sesion'))  # Redirige al login

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
