import mysql.connector
from mysql.connector import Error

def crear_conexion():
    """Establece la conexión con la base de datos MySQL"""
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',  # El usuario por defecto en XAMPP
            password='',  # La contraseña por defecto está vacía en XAMPP
            database='crud_db'
        )
        if conexion.is_connected():
            print("Conexión exitosa a la base de datos MySQL.")
            return conexion
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def cerrar_conexion(conexion):
    """Cierra la conexión con la base de datos MySQL"""
    if conexion.is_connected():
        conexion.close()
        print("Conexión cerrada.")
