import mysql.connector
from db import crear_conexion, cerrar_conexion

def crear_persona(nombre, edad, correo):
    """Crea una nueva persona en la base de datos"""
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        INSERT INTO personas (nombre, edad, correo)
        VALUES (%s, %s, %s)
        """, (nombre, edad, correo))
        conexion.commit()
        print("Persona creada exitosamente.")
        cerrar_conexion(conexion)

def obtener_personas():
    """Obtiene todas las personas de la base de datos"""
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM personas")
        personas = cursor.fetchall()
        cerrar_conexion(conexion)
        return personas

def actualizar_persona(id, nombre, edad, correo):
    """Actualiza los datos de una persona"""
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        UPDATE personas
        SET nombre = %s, edad = %s, correo = %s
        WHERE id = %s
        """, (nombre, edad, correo, id))
        conexion.commit()
        print("Persona actualizada exitosamente.")
        cerrar_conexion(conexion)

def eliminar_persona(id):
    """Elimina una persona de la base de datos"""
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM personas WHERE id = %s", (id,))
        conexion.commit()
        print("Persona eliminada exitosamente.")
        cerrar_conexion(conexion)
