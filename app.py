from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os
from flask import flash
import mysql.connector
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
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

def es_administrador():
    if 'usuario_id' in session:
        usuario_id = session['usuario_id']
        query = "SELECT rol FROM usuarios WHERE id = %s"
        cursor.execute(query, (usuario_id,))
        rol = cursor.fetchone()
        return rol and rol[0] == 'admin'
    return False



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


# Ruta principal (Inicio) - Mostrar "Inicio" y mostrar los botones adecuados
@app.route('/inicio')
def inicio():
    if 'usuario_id' not in session:
        return render_template('inicio.html', logged_in=False, es_administrador=False)  # Si no hay sesión, muestra los botones de login
    return render_template('inicio.html', logged_in=True, es_administrador=es_administrador())  # Pasar si el usuario es admin


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
            INSERT INTO usuarios (nombre, correo, usuario, contraseña, fecha_nacimiento, telefono, rol)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            # Asignar rol de 'user' al registrarse
            values = (nombre, correo, usuario, contraseña_hash, fecha_nacimiento, telefono, 'user')
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

# Ruta para mostrar los productos de la tienda
@app.route('/tienda', methods=['GET'])
def tienda():
    productos = obtener_productos()  # Obtener productos desde la base de datos
    return render_template('tienda.html', productos=productos)  # Mostrar la tienda con productos

@app.route('/eliminar_del_carrito/<int:id_producto>', methods=['GET'])
def eliminar_del_carrito(id_producto):
    # Si el carrito existe en la sesión
    if 'carrito' in session:
        # Buscar el producto en el carrito
        producto = next((item for item in session['carrito'] if item['id'] == id_producto), None)
        
        if producto:
            # Eliminar el producto encontrado
            session['carrito'].remove(producto)
            flash(f'El producto {producto["nombre"]} ha sido eliminado del carrito', 'success')
        else:
            flash('El producto no está en el carrito.', 'error')
    
    # Redirigir de vuelta al carrito
    return redirect(url_for('carrito'))



@app.route('/carrito', methods=['GET'])
def carrito():
    # Verifica si el carrito existe en la sesión
    if 'carrito' in session:
        total_compra = sum(float(item['cantidad']) * float(item['precio']) for item in session['carrito'])
        return render_template('carrito.html', total_compra=total_compra)  # Mostrar la plantilla del carrito
    else:
        return redirect(url_for('tienda'))  # Si el carrito está vacío, redirigir a la tienda


@app.route('/añadir_al_carrito/<int:id_producto>', methods=['POST'])
def añadir_al_carrito(id_producto):
    cantidad = int(request.form['cantidad'])  # Obtener la cantidad seleccionada por el usuario
    
    # Verificar si el carrito ya está en la sesión, si no lo está, crear uno vacío
    if 'carrito' not in session:
        session['carrito'] = []
    
    print(f"Carrito antes de añadir: {session['carrito']}")  # Depuración: mostrar el carrito actual

    # Buscar el producto en la base de datos
    cursor.execute("SELECT * FROM productos WHERE id = %s", (id_producto,))
    producto = cursor.fetchone()

    if producto:
        # Verificar si el producto ya está en el carrito
        producto_en_carrito = next((item for item in session['carrito'] if item['id'] == id_producto), None)
        
        if producto_en_carrito:
            # Si el producto ya está en el carrito, solo sumamos la cantidad
            producto_en_carrito['cantidad'] += cantidad
            print(f"Producto actualizado en el carrito: {producto_en_carrito}")  # Depuración
        else:
            # Si el producto no está en el carrito, lo añadimos
            producto_en_carrito = {
                'id': producto[0],  # ID del producto
                'nombre': producto[1],  # Nombre del producto
                'descripcion': producto[2],  # Descripción
                'precio': producto[3],  # Precio
                'foto': producto[5],  # Foto
                'cantidad': cantidad
            }
            session['carrito'].append(producto_en_carrito)
            print(f"Producto añadido al carrito: {producto_en_carrito}")  # Depuración
    
    # Guardar el carrito en la sesión
    session.modified = True

    # Verificar el contenido final del carrito
    print(f"Carrito después de añadir: {session['carrito']}")  # Depuración

    # Redirigir al carrito
    return redirect(url_for('carrito'))


@app.route('/realizar_compra', methods=['GET'])
def realizar_compra():
    if 'carrito' not in session or not session['carrito']:
        return redirect(url_for('tienda'))  # Si el carrito está vacío, redirige a la tienda
    
    # Aquí podrías procesar la compra, por ejemplo, almacenarla en la base de datos o realizar el pago
    # Por ahora, solo vamos a vaciar el carrito y mostrar un mensaje

    session.pop('carrito', None)  # Limpiar el carrito después de la compra
    
    return render_template('compra_exitosa.html')  # Redirige a una página de éxito de compra



# Ruta del inventario (Index)
@app.route('/', methods=['GET'])
def index():
    if 'usuario_id' not in session or not es_administrador():
        return redirect(url_for('inicio'))  # Si el usuario no es administrador, redirigir a inicio

    productos = obtener_productos()  # Obtener productos desde la base de datos
    return render_template('index.html', productos=productos)  # Mostrar inventario

# Ruta para crear productos (debe ser administrada por el usuario logueado)
@app.route('/crear', methods=['POST'])
def crear():
    if es_administrador():
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
            return redirect(url_for('index'))  # Redirigir al inventario después de crear
    else:
        return redirect(url_for('inicio'))  # Si no es admin, redirigir a inicio

# Ruta para actualizar productos
@app.route('/actualizar/<int:id>', methods=['GET', 'POST'])
def actualizar(id):
    if es_administrador():
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
    else:
        return redirect(url_for('inicio'))  # Si no es admin, redirigir a inicio

# Ruta para eliminar productos
@app.route('/eliminar/<int:id>')
def eliminar(id):
    if es_administrador():
        eliminar_producto(id)
    return redirect(url_for('index'))

# Ruta para generar y descargar el reporte Excel
@app.route('/generar_reporte', methods=['GET'])
def generar_reporte():
    if es_administrador():
        productos = obtener_productos()  # Obtener productos desde la base de datos
        # Crear DataFrame con pandas
        df = pd.DataFrame(productos, columns=['ID', 'Nombre', 'Descripción', 'Precio', 'Cantidad en Stock', 'Foto'])

        # Guardar el archivo Excel
        archivo = 'reporte_productos.xlsx'
        df.to_excel(archivo, index=False, engine='openpyxl')

        # Enviar el archivo como descarga
        return send_file(archivo, as_attachment=True)
    else:
        return redirect(url_for('inicio'))  # Si no es admin, redirigir a inicio

# Iniciar la aplicación Flask
if __name__ == '__main__':
    app.run(debug=True)
