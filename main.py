from crud import crear_persona, obtener_personas, actualizar_persona, eliminar_persona

def mostrar_menu():
    """Muestra el menú de opciones al usuario."""
    print("\nMenu de opciones:")
    print("1. Crear persona")     
    print("2. Ver personas")     
    print("3. Actualizar persona")
    print("4. Eliminar persona")  
    print("5. Salir")

def main():
    while True:
        mostrar_menu()  # Aquí ya se llama a la función correctamente
        opcion = input("Elija una opción (1-5): ")

        if opcion == "1":
            nombre = input("Ingrese el nombre: ")
            edad = int(input("Ingrese la edad: "))
            correo = input("Ingrese el correo: ")
            crear_persona(nombre, edad, correo)

        elif opcion == "2":
            personas = obtener_personas()
            print("\nLista de personas:")
            for persona in personas:
                print(f"{persona[0]}. {persona[1]} - {persona[2]} años - {persona[3]}")

        elif opcion == "3":
            id_persona = int(input("Ingrese el ID de la persona a actualizar: "))
            nombre = input("Ingrese el nuevo nombre: ")
            edad = int(input("Ingrese la nueva edad: "))
            correo = input("Ingrese el nuevo correo: ")
            actualizar_persona(id_persona, nombre, edad, correo)

        elif opcion == "4":
            id_persona = int(input("Ingrese el ID de la persona a eliminar: "))
            eliminar_persona(id_persona)

        elif opcion == "5":
            print("Saliendo...")
            break

        else:
            print("Opción no válida, intente de nuevo.")

if __name__ == "__main__":
    main()
