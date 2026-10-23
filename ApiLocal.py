import json
import ollama


# ---------------------------------------------------------------
# Configuración de modelos disponibles
# ---------------------------------------------------------------
MODELOS = {
    "1": {
        "nombre": "llama3.2:1b",
        "descripcion": "Modelo base (sin contexto técnico, respuestas genéricas)",
        "usa_system_personalizado": False,
    },
    "2": {
        "nombre": "mecanico-moto-3b",
        "descripcion": "Modelo especializado (con contexto técnico de moto)",
        "usa_system_personalizado": True,
    },
}


def elegir_modelo():
    """Pregunta al usuario qué modelo quiere usar al inicio."""
    print("\n" + "=" * 50)
    print("   SELECCIONA EL MODELO PARA EL DIAGNÓSTICO")
    print("=" * 50)
    for clave, info in MODELOS.items():
        print(f"  {clave}. {info['nombre']}")
        print(f"     → {info['descripcion']}")
    print("=" * 50)

    while True:
        opcion = input("\nNúmero > ").strip()
        if opcion in MODELOS:
            return MODELOS[opcion]
        print("Opción inválida. Elige 1 o 2.")


def construir_prompt(camino, hoja, usa_system_personalizado):
    """
    Si el modelo NO tiene SYSTEM personalizado (llama3.2:1b),
    le pedimos una explicación genérica.
    Si el modelo SÍ tiene SYSTEM personalizado (mecanico-moto-3b),
    solo le pasamos la ruta y la hoja; el SYSTEM ya está en el Modelfile.
    """
    if usa_system_personalizado:
        # El modelo ya sabe el formato; solo necesita la ruta y la hoja.
        return (
            f"Ruta: {' > '.join(camino)}\n"
            f"Hoja: {hoja}\n\n"
            "Genera el diagnóstico final con el formato obligatorio."
        )
    else:
        # Modelo base: no tiene SYSTEM con el formato, pedimos algo simple.
        return (
            f"Explícame qué es '{hoja}' en el contexto de la revisión "
            f"preventiva de una moto para un viaje. "
            f"La ruta completa es: {' > '.join(camino)}. "
            "Da una explicación breve y útil."
        )


def construir_system(usa_system_personalizado):
    """El modelo base necesita un system; el especializado ya lo trae."""
    if usa_system_personalizado:
        return ""  # No enviamos system, el Modelfile ya lo tiene
    return "Eres un experto en mecánica de motos. Da respuestas claras y breves."


def explorar():
    try:
        with open("EstructurasDeDatos.json", encoding="utf-8") as f:
            nodo = json.load(f)
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'EstructurasDeDatos.json'")
        return

    # Elegir modelo al inicio
    modelo_info = elegir_modelo()
    modelo_nombre = modelo_info["nombre"]
    usa_system_personalizado = modelo_info["usa_system_personalizado"]

    print(f"\n✅ Usando modelo: {modelo_nombre}")

    camino = []

    while True:
        camino.append(nodo["valor"])
        hijos = nodo.get("hijos", [])

        print(f"\n" + "=" * 30)
        print(f" UBICACIÓN: {' > '.join(camino)}")
        print("=" * 30)

        if not hijos:
            # ---------- HOJA: consultar al modelo ----------
            prompt = construir_prompt(
                camino, nodo["valor"], usa_system_personalizado
            )
            system_content = construir_system(usa_system_personalizado)

            print(f"\n[{modelo_nombre}] Generando diagnóstico local...")

            # Armamos los mensajes: si el system está vacío, no lo incluimos
            mensajes = []
            if system_content:
                mensajes.append({"role": "system", "content": system_content})
            mensajes.append({"role": "user", "content": prompt})

            try:
                response = ollama.chat(
                    model=modelo_nombre,
                    messages=mensajes,
                    options={"temperature": 0.1 if usa_system_personalizado else 0.5},
                )
                print("\nDIAGNÓSTICO:")
                print(response["message"]["content"])
            except Exception as e:
                print(f"\nError al conectar con Ollama: {e}")
                if usa_system_personalizado:
                    print(
                        f"\n💡 Verifica que el modelo '{modelo_nombre}' exista:\n"
                        f"   ollama list\n"
                        f"   Si no aparece, créalo con:\n"
                        f"   ollama create {modelo_nombre} -f ./Modelfile"
                    )

            break

        # ---------- INTERMEDIO: mostrar opciones ----------
        print(f"Selecciona una categoría:")
        for i, h in enumerate(hijos, 1):
            print(f"{i}. {h['valor']}")

        while True:
            idx = input("\nNúmero > ")
            if idx.isdigit() and 1 <= int(idx) <= len(hijos):
                nodo = hijos[int(idx) - 1]
                break
            print("Opción inválida.")


if __name__ == "__main__":
    explorar()