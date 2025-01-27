import mysql.connector
from db import crear_conexion, cerrar_conexion

# Crear un producto
def crear_producto(nombre, descripcion, precio, cantidad_stock, foto_url):
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        INSERT INTO productos (nombre, descripcion, precio, cantidad_stock, foto)
        VALUES (%s, %s, %s, %s, %s)
        """, (nombre, descripcion, precio, cantidad_stock, foto_url))
        conexion.commit()
        cerrar_conexion(conexion)

# Obtener todos los productos
def obtener_productos():
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM productos")
        productos = cursor.fetchall()
        cerrar_conexion(conexion)
        return productos

# Actualizar un producto
def actualizar_producto(id, nombre, descripcion, precio, cantidad_stock, foto_url):
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        UPDATE productos
        SET nombre = %s, descripcion = %s, precio = %s, cantidad_stock = %s, foto = %s
        WHERE id = %s
        """, (nombre, descripcion, precio, cantidad_stock, foto_url, id))
        conexion.commit()
        cerrar_conexion(conexion)

# Eliminar un producto
def eliminar_producto(id):
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
        conexion.commit()
        cerrar_conexion(conexion)
