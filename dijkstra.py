# ============================================================
#  Camino mínimo con Dijkstra - versión simple para aprender
# ============================================================
# Idea general del programa:
#   1) El usuario crea un grafo (aleatorio o manual).
#   2) Se calcula Dijkstra y se GUARDA cada iteración en una lista.
#   3) Con el botón "Siguiente" se muestra la iteración que sigue.

import random                              # numeros al azar (para el grafo aleatorio)
from tkinter import messagebox             # ventanitas de error
import customtkinter as ctk                # ventana, botones y cajas de texto
import networkx as nx                      # guarda el grafo y lo dibuja
from matplotlib.figure import Figure       # la hoja donde se dibuja
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg   # pone la hoja en la ventana

INFINITO = float("inf")                    # distancia "infinita" para los vértices no alcanzados

# Diccionario con lo que el programa necesita recordar entre clic y clic.
datos = {
    "grafo": None,         
    "iteraciones": [],     
    "paso": 0,             
}

# PARTE 1: el grafo

def crear_grafo_aleatorio(n):
    """Solo crea aristas de i hacia j con i < j. Así nunca se forma un ciclo."""
    grafo = nx.DiGraph()
    grafo.add_nodes_from(range(1, n + 1))          # vértices 1, 2, ..., n
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            if random.random() < 0.35:             # 35 % de probabilidad de unir i con j
                peso = random.randint(1, 10)
                grafo.add_edge(i, j, weight=peso)
    return grafo


def hay_camino(grafo, inicio, fin):
    """DFS: revisa si se puede ir de 'inicio' a 'fin' siguiendo las flechas."""
    pendientes = [inicio]                          # vértices que faltan revisar
    revisados = []                                 # vértices ya revisados
    while len(pendientes) > 0:
        actual = pendientes.pop()                  # saco el último de la lista
        if actual == fin:
            return True
        if actual not in revisados:
            revisados.append(actual)
            for vecino in grafo.successors(actual):   # a dónde apuntan sus flechas
                pendientes.append(vecino)
    return False

# PARTE 2: el algoritmo de Dijkstra

def dijkstra(grafo, origen):
    """Devuelve una lista: cada elemento es un diccionario con lo que pasó en esa iteración."""
    distancia = {}                                 # distancia[v] = menor distancia conocida a v
    etiqueta = {}                                  # etiqueta[v] = texto "[d, V](n)"
    for v in grafo.nodes:
        distancia[v] = INFINITO                    # Paso 1: todos empiezan en infinito...
        etiqueta[v] = ""
    distancia[origen] = 0                          # ...menos el origen
    etiqueta[origen] = "[0, -](0)"

    visitados = []
    iteraciones = []
    n = 0                                          # número de iteración

    while True:
        # Paso 2: buscar el vértice NO visitado con la menor distancia
        elegido = None
        for v in grafo.nodes:
            if v not in visitados and distancia[v] < INFINITO:
                if elegido is None or distancia[v] < distancia[elegido]:
                    elegido = v
        if elegido is None:                        # ya no hay a quién visitar: terminamos
            break

        n = n + 1
        visitados.append(elegido)
        texto = f"Iteración {n}: se elige el vértice {elegido} con d = {distancia[elegido]}\n"

        # Pasos 3 y 4: revisar cada vecino del vértice elegido
        for vecino in grafo.successors(elegido):
            if vecino in visitados:
                continue                           # ya tiene distancia final, no se toca
            peso = grafo[elegido][vecino]["weight"]
            nueva = distancia[elegido] + peso      # nd = d(u) + w(u, v)

            if nueva < distancia[vecino]:          # encontré un camino más corto
                distancia[vecino] = nueva
                etiqueta[vecino] = f"[{nueva}, {elegido}]({n})"
                texto += f"   {vecino}: {nueva} es mejor -> nueva etiqueta {etiqueta[vecino]}\n"
            elif nueva == distancia[vecino]:       # empate: hay otro camino igual de corto
                etiqueta[vecino] += f" [{nueva}, {elegido}]({n})"
                texto += f"   {vecino}: {nueva} empata -> se agrega [{nueva}, {elegido}]({n})\n"
            else:
                texto += f"   {vecino}: {nueva} es peor -> se conserva la etiqueta\n"

        # Guardo una COPIA de cómo quedó todo en esta iteración
        iteraciones.append({
            "elegido": elegido,
            "visitados": visitados.copy(),
            "etiquetas": etiqueta.copy(),
            "distancias": distancia.copy(),
            "texto": texto,
        })

    return iteraciones


# PARTE 3: dibujar

def dibujar(iteracion=None):
    """Dibuja el grafo. Si recibe una iteración, pinta los colores y las etiquetas."""
    grafo = datos["grafo"]
    eje.clear()
    eje.axis("off")
    posiciones = nx.circular_layout(grafo)         # vértices en círculo

    colores = []
    for v in grafo.nodes:
        if iteracion and v == iteracion["elegido"]:
            colores.append("orange")               # el elegido en esta iteración
        elif iteracion and v in iteracion["visitados"]:
            colores.append("lightgreen")           # ya visitado
        else:
            colores.append("lightblue")            # todavía no

    nx.draw_networkx(grafo, posiciones, ax=eje, node_color=colores, node_size=700, edgecolors="black")
    pesos = nx.get_edge_attributes(grafo, "weight")
    nx.draw_networkx_edge_labels(grafo, posiciones, edge_labels=pesos, ax=eje, label_pos=0.3)

    if iteracion:                                  # escribo [d, V](n) encima de cada vértice
        for v, texto in iteracion["etiquetas"].items():
            x, y = posiciones[v]
            eje.text(x, y + 0.13, texto, ha="center", fontsize=8, color="darkred")

    lienzo.draw()


def escribir(texto):
    """Agrega texto en la caja de abajo."""
    caja.insert("end", texto + "\n")
    caja.see("end")

# PARTE 4: lo que hace cada botón

def boton_crear():
    try:
        n = int(entrada_n.get())
    except ValueError:
        messagebox.showerror("Error", "n debe ser un número entero")
        return
    if n < 7 or n > 16:
        messagebox.showerror("Error", "n debe estar entre 7 y 16")
        return

    if modo.get() == "Aleatorio":
        datos["grafo"] = crear_grafo_aleatorio(n)
    else:
        datos["grafo"] = nx.DiGraph()
        datos["grafo"].add_nodes_from(range(1, n + 1))   # solo vértices, sin aristas

    caja.delete("1.0", "end")
    escribir(f"Grafo creado con {n} vértices.")
    dibujar()


def boton_agregar_arista():
    grafo = datos["grafo"]
    if grafo is None:
        messagebox.showerror("Error", "Primero crea el grafo")
        return
    try:
        u = int(entrada_u.get())
        v = int(entrada_v.get())
        w = int(entrada_w.get())
    except ValueError:
        messagebox.showerror("Error", "u, v y w deben ser números enteros")
        return

    if u not in grafo.nodes or v not in grafo.nodes:
        messagebox.showerror("Error", "Ese vértice no existe")
    elif u == v:
        messagebox.showerror("Error", "No se permiten lazos (u = v)")
    elif w <= 0:
        messagebox.showerror("Error", "El peso debe ser positivo")
    elif hay_camino(grafo, v, u):                  # si ya puedo ir de v a u, u -> v cerraría un ciclo
        messagebox.showerror("Error", "Esa arista formaría un ciclo")
    else:
        grafo.add_edge(u, v, weight=w)
        escribir(f"Arista agregada: {u} -> {v} (peso {w})")
        dibujar()


def boton_iniciar():
    if datos["grafo"] is None:
        messagebox.showerror("Error", "Primero crea el grafo")
        return
    try:
        origen = int(entrada_origen.get())
    except ValueError:
        messagebox.showerror("Error", "El origen debe ser un número")
        return
    if origen not in datos["grafo"].nodes:
        messagebox.showerror("Error", "Ese vértice no existe")
        return

    datos["iteraciones"] = dijkstra(datos["grafo"], origen)   # se calcula todo de una vez
    datos["paso"] = 0                                          # pero se muestra de a poco
    caja.delete("1.0", "end")
    escribir(f"Inicio: el vértice {origen} tiene [0, -](0) y los demás d = infinito.")
    escribir("Pulsa 'Siguiente' para ver cada iteración.\n")


def boton_siguiente():
    paso = datos["paso"]
    iteraciones = datos["iteraciones"]
    if paso >= len(iteraciones):
        messagebox.showinfo("Fin", "Ya se mostraron todas las iteraciones")
        return
    iteracion = iteraciones[paso]
    escribir(iteracion["texto"])
    dibujar(iteracion)
    datos["paso"] = paso + 1

    if datos["paso"] == len(iteraciones):          # era la última: muestro las distancias finales
        escribir("Distancias mínimas desde el origen:")
        for v, d in iteracion["distancias"].items():
            if d == INFINITO:
                escribir(f"   hasta {v}: no se puede llegar")
            else:
                escribir(f"   hasta {v}: {d}")

# PARTE 5: armar la ventana

ventana = ctk.CTk()
ventana.title("Dijkstra")
ventana.geometry("1100x680")

# Panel izquierdo con los controles
panel = ctk.CTkFrame(ventana)
panel.pack(side="left", fill="y", padx=10, pady=10)

entrada_n = ctk.CTkEntry(panel, placeholder_text="n (7 a 16)")
entrada_n.pack(padx=10, pady=5)
modo = ctk.CTkSegmentedButton(panel, values=["Manual", "Aleatorio"])
modo.set("Aleatorio")
modo.pack(padx=10, pady=5)
ctk.CTkButton(panel, text="Crear grafo", command=boton_crear).pack(padx=10, pady=5)

entrada_u = ctk.CTkEntry(panel, placeholder_text="Desde u")
entrada_v = ctk.CTkEntry(panel, placeholder_text="Hacia v")
entrada_w = ctk.CTkEntry(panel, placeholder_text="Peso w")
entrada_u.pack(padx=10, pady=(25, 5))
entrada_v.pack(padx=10, pady=5)
entrada_w.pack(padx=10, pady=5)
ctk.CTkButton(panel, text="Agregar arista", command=boton_agregar_arista).pack(padx=10, pady=5)

entrada_origen = ctk.CTkEntry(panel, placeholder_text="Origen")
entrada_origen.pack(padx=10, pady=(25, 5))
ctk.CTkButton(panel, text="Iniciar Dijkstra", command=boton_iniciar).pack(padx=10, pady=5)
ctk.CTkButton(panel, text="Siguiente", command=boton_siguiente).pack(padx=10, pady=5)

# Lado derecho: dibujo arriba y texto abajo
figura = Figure(figsize=(7, 4.5))
eje = figura.add_subplot(111)
lienzo = FigureCanvasTkAgg(figura, master=ventana)
lienzo.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

caja = ctk.CTkTextbox(ventana, height=200, font=("Consolas", 13))
caja.pack(fill="x", padx=10, pady=(0, 10))

ventana.mainloop()  # deja la ventana abierta esperando clics
