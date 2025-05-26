import tkinter as tk
from tkinter import ttk

# Lista original de opciones
opciones = ['Rojo', 'Verde', 'Azul', 'Amarillo', 'Naranja', 'Violeta', 'Blanco', 'Negro']

def filtrar_opciones(event):
    entrada = combo_var.get().lower()
    
    # Filtrar opciones que contengan el texto
    filtradas = [op for op in opciones if entrada in op.lower()]
    
    # Guardar posición del cursor y texto actual
    cursor_pos = combobox.index(tk.INSERT)
    
    # Actualizar valores del Combobox
    combobox['values'] = filtradas if filtradas else opciones
    
    # Restaurar el texto y la posición del cursor
    combobox.delete(0, tk.END)
    combobox.insert(0, combo_var.get())
    combobox.icursor(cursor_pos)
    
    # Autocompletar si hay una sola opción
    if len(filtradas) == 1:
        combobox.delete(0, tk.END)
        combobox.insert(0, filtradas[0])
        combobox.icursor(tk.END)

    # Mostrar menú desplegable
    combobox.event_generate('<Down>')

# Crear la ventana principal
root = tk.Tk()
root.title("Combobox con búsqueda fluida")

combo_var = tk.StringVar()
combobox = ttk.Combobox(root, textvariable=combo_var)
combobox['values'] = opciones
combobox.pack(padx=20, pady=20)

# Conectar evento
combobox.bind('<Return>', filtrar_opciones)

root.mainloop()