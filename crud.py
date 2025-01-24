import mysql.connector
from db import crear_conexion, cerrar_conexion

def crear_persona(nombre, edad, correo, foto_url):
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        INSERT INTO personas (nombre, edad, correo, foto)
        VALUES (%s, %s, %s, %s)
        """, (nombre, edad, correo, foto_url))
        conexion.commit()
        cerrar_conexion(conexion)

def obtener_personas():
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM personas")
        personas = cursor.fetchall()
        cerrar_conexion(conexion)
        return personas

def actualizar_persona(id, nombre, edad, correo, foto_url):
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        UPDATE personas
        SET nombre = %s, edad = %s, correo = %s, foto = %s
        WHERE id = %s
        """, (nombre, edad, correo, foto_url, id))
        conexion.commit()
        cerrar_conexion(conexion)

def eliminar_persona(id):
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM personas WHERE id = %s", (id,))
        conexion.commit()
        cerrar_conexion(conexion)
