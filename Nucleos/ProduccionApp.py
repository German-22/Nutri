import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from tkinter import ttk,messagebox, filedialog
import Leer_archivo as la 
ruta_txt = "/archnucl"

class ProduccionPesosApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Registro Producción y Pesos")
        self.geometry("900x600")        
        
        # Combo producto arriba
        frame_producto = ttk.Frame(self)
        frame_producto.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_producto, text="Producto del día:").pack(side="left")
        
        
        # Pestañas
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(expand=True, fill="both", padx=10, pady=10)

        self.tab_produccion = ttk.Frame(self.tabs)
        self.tab_pesos = ttk.Frame(self.tabs)
        self.tab_detector = ttk.Frame(self.tabs)
        self.tab_control = ttk.Frame(self.tabs)
        self.tab_config = ttk.Frame(self.tabs)

        self.tabs.add(self.tab_produccion, text="Producción diaria")
        self.tabs.add(self.tab_pesos, text="Registro de pesos")
        self.tabs.add(self.tab_detector, text="Detector de Metales")
        self.tabs.add(self.tab_control, text="Control Embalajes")
        self.tabs.add(self.tab_config, text="Config")
        # Producto seleccionado
        self.crear_tab_config()
        self.leer_archivo()
        PRODUCTOS = self.leer_base()
        self.producto_combo = ttk.Combobox(frame_producto, values=PRODUCTOS, state="readonly", width=40)
        self.producto_combo.pack(side="left", padx=5)
        self.producto_combo.bind("<<ComboboxSelected>>", lambda e: self.cargar_datos())    
        
        self.crear_tab_produccion()
        self.crear_tab_pesos()
        self.crear_tab_detector()
        self.crear_formulario_control_embalaje()
            
         
     
  
    def crear_tab_produccion(self):
        frm = self.tab_produccion

        # Formulario
        form = ttk.Frame(frm)
        form.pack(fill="x", pady=10)

        ttk.Label(form, text="N° de Pallet:").grid(row=0, column=0, sticky="e", padx=5, pady=3)
        vcmd = (frm.register(self.validar_entero), "%P")
        self.entry_pallet = ttk.Entry(form,validate="key",validatecommand=vcmd)
        self.entry_pallet.grid(row=0, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(form, text="Lote:").grid(row=0, column=2, sticky="e", padx=5, pady=3)
        self.entry_lote = ttk.Entry(form)
        self.entry_lote.grid(row=0, column=3, sticky="w", padx=5, pady=3)

        ttk.Label(form, text="Cantidad de cajas:").grid(row=1, column=0, sticky="e", padx=5, pady=3)
        self.entry_cantidad = ttk.Entry(form,validate="key",validatecommand=vcmd)
        self.entry_cantidad.grid(row=1, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(form, text="Comentario:").grid(row=1, column=2, sticky="e", padx=5, pady=3)
        self.entry_comentario = ttk.Entry(form, width=40)
        self.entry_comentario.grid(row=1, column=3, sticky="w", padx=5, pady=3)

        btn_guardar = ttk.Button(form, text="Agregar registro", command=self.agregar_registro_produccion)
        btn_guardar.grid(row=2, column=0, columnspan=4, pady=8)

        # Tabla con scrollbar
        tabla_frame = ttk.Frame(frm)
        tabla_frame.pack(fill="both", expand=True)

        columnas = ("hora", "pallet", "lote", "cantidad", "comentario")
        self.tree_produccion = ttk.Treeview(tabla_frame, columns=columnas, show="headings")
        for col in columnas:
            self.tree_produccion.heading(col, text=col.capitalize())
            self.tree_produccion.column(col, anchor="center",width=30)
        self.tree_produccion.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tree_produccion.yview)
        self.tree_produccion.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def agregar_registro_produccion(self):
        pallet = self.entry_pallet.get().strip()
        lote = self.entry_lote.get().strip()
        cantidad = self.entry_cantidad.get().strip()
        comentario = self.entry_comentario.get().strip()
        conexion = sqlite3.connect(self.entrada_ruta.get())
        if not pallet or not lote or not cantidad:
            messagebox.showwarning("Datos incompletos", "Completa los campos N° de Pallet, Lote y Cantidad de cajas.")
            return

        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Dato inválido", "Cantidad de cajas debe ser un número entero positivo.")
            return

        hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        producto = self.producto_combo.get()
        try:
            conexion.execute('''
                INSERT INTO produccion (producto, hora, pallet, lote, cantidad, comentario)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (producto, hora, pallet, lote, cantidad, comentario))
            conexion.commit()
            conexion.close()
        except:
            messagebox.showinfo(message="Dato Invalido", title="Error")
            conexion.close()
            return

        self.entry_pallet.delete(0, tk.END)        
        self.entry_comentario.delete(0, tk.END)
        self.cargar_datos()
        #messagebox.showinfo("Registro guardado", "Registro de producción agregado correctamente.")
        conexion.close()
 
    def crear_tab_pesos(self):
        frm = self.tab_pesos

        form = ttk.Frame(frm)
        form.pack(fill="x", pady=10)

        ttk.Label(form, text="Peso del paquete:").grid(row=0, column=0, sticky="e", padx=5, pady=3)
        self.entry_peso_paquete = ttk.Entry(form)
        self.entry_peso_paquete.grid(row=0, column=1, sticky="w", padx=5, pady=3)
        self.entry_peso_paquete.bind("<Return>", lambda e: self.agregar_peso(paquete=True))

        ttk.Label(form, text="Peso de la caja:").grid(row=0, column=2, sticky="e", padx=5, pady=3)
        self.entry_peso_caja = ttk.Entry(form)
        self.entry_peso_caja.grid(row=0, column=3, sticky="w", padx=5, pady=3)
        self.entry_peso_caja.bind("<Return>", lambda e: self.agregar_peso(paquete=False))

        # Frame contenedor con grid
        tabla_frame = ttk.Frame(frm)
        tabla_frame.pack(fill="both", expand=True)

        tabla_frame.columnconfigure(0, weight=1)
        tabla_frame.columnconfigure(1, weight=1)
        for i in range(8):
            tabla_frame.rowconfigure(i, weight=1)

        # Treeview izquierdo (todo el alto)
        columnas1 = ("id", "peso_paquete", "peso_caja", "fecha")
        self.tree_pesos = ttk.Treeview(tabla_frame, columns=columnas1, show="headings")
        for col in columnas1:
            self.tree_pesos.heading(col, text=col.replace("_", " ").capitalize())
            self.tree_pesos.column(col, anchor="center")
        self.tree_pesos.grid(row=0, column=0, rowspan=8, sticky="nsew", padx=5, pady=5)

        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tree_pesos.yview)
        self.tree_pesos.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=0, rowspan=8, sticky="nse", padx=(0, 5))

        # Treeview derecho (solo 1/8 de la altura, fila 0)
        columnas2 = ("Presentacion", "Peso Nominal", "Peso Max", "Peso Min")
        self.tree_pesos2 = ttk.Treeview(tabla_frame, columns=columnas2, show="headings", height=2)
        for col in columnas2:
            self.tree_pesos2.heading(col, text=col.replace("_", " ").capitalize())
            self.tree_pesos2.column(col, anchor="center", minwidth=20, width=100)
        self.tree_pesos2.grid(row=0, column=1, sticky="new", padx=5, pady=5)

    
    def crear_tab_detector(self):
        frm = self.tab_detector

        form = ttk.Frame(frm)
        form.pack(fill="x", pady=10)

        ttk.Label(form, text="Observación:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_observacion_detector = ttk.Entry(form, width=40)
        self.entry_observacion_detector.grid(row=0, column=1, padx=5, pady=5)

        btn_guardar = ttk.Button(form, text="Registrar control", command=self.registrar_control_detector)
        btn_guardar.grid(row=0, column=2, padx=5, pady=5)

        # Tabla historial
        tabla_frame = ttk.Frame(frm)
        tabla_frame.pack(fill="both", expand=True)

        columnas = ("id", "producto", "observacion", "fecha")
        self.tree_detector = ttk.Treeview(tabla_frame, columns=columnas, show="headings")
        for col in columnas:
            self.tree_detector.heading(col, text=col.capitalize())
            self.tree_detector.column(col, anchor="center")
        self.tree_detector.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tree_detector.yview)
        self.tree_detector.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        def guardar_control_detector(self):
            operador = self.entry_operador.get().strip()
            resultado = self.combo_resultado.get().strip()
            observaciones = self.entry_obs.get().strip()
            producto = self.producto_combo.get()
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if not operador or not resultado:
                messagebox.showwarning("Faltan datos", "Debes ingresar el operador y el resultado.")
                return

            try:
                conexion = sqlite3.connect(self.entrada_ruta.get())
                conexion.execute('''
                    INSERT INTO detector_metales (producto, operador, resultado, observaciones, fecha)
                    VALUES (?, ?, ?, ?, ?)
                ''', (producto, operador, resultado, observaciones, fecha))
                conexion.commit()
                conexion.close()

                # Limpiar campos
                self.entry_operador.delete(0, tk.END)
                self.combo_resultado.set("")
                self.entry_obs.delete(0, tk.END)

                # Recargar historial
                self.cargar_datos()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el control: {e}")

    def crear_tab_config(self):
        frm = self.tab_config      
        label_ruta = ttk.Label(frm, text="Ruta a Base de Datos")
        label_ruta.place(relx=0.05, rely=0.7)        
        self.entrada_ruta = ttk.Entry(frm, width= 60)
        self.entrada_ruta.place(relx=0.27, rely=0.7)  
        btn_guardar = ttk.Button(frm, text="Conf. Ruta", command= self.selecionar_ruta)
        btn_guardar.place(relx=0.8, rely=0.7)

      
    def selecionar_ruta(d):    
        ruta_guardar = []
        ruta_bd= filedialog.askopenfilename(initialdir="/", title="Seleccionar Base de Datos")                                        
        entrada_ruta.delete("0", "end")
        entrada_ruta.insert(0, str(ruta_bd))
        ruta_guardar.append(ruta_bd) 
        try: 
            archivo = open(ruta_txt + "/archivo_bd.txt", "w")
            archivo_csv = writer(archivo)
            archivo_csv.writerow(ruta_guardar)
            archivo.close()
            leer_archivo()
        except:
            messagebox.showinfo(message="Error al Configurar la Ruta", title="Ruta Erronea")
            
    def agregar_peso(self, paquete=None, both=False):
        producto = self.producto_combo.get()
        peso_paquete_text = self.entry_peso_paquete.get().strip()
        peso_caja_text = self.entry_peso_caja.get().strip()

        peso_paquete = None
        peso_caja = None

        if both:
            try:
                peso_paquete = float(peso_paquete_text)
                peso_caja = float(peso_caja_text)
                if peso_paquete <= 0 or peso_caja <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Dato inválido", "Ingresa pesos válidos mayores que 0 para paquete y caja.")
                return
        else:
            if paquete:
                try:
                    peso_paquete = float(peso_paquete_text)
                    if peso_paquete <= 0:
                        raise ValueError
                except ValueError:
                    messagebox.showwarning("Dato inválido", "Ingresa un peso válido mayor que 0 para paquete.")
                    return
            else:
                try:
                    peso_caja = float(peso_caja_text)
                    if peso_caja <= 0:
                        raise ValueError
                except ValueError:
                    messagebox.showwarning("Dato inválido", "Ingresa un peso válido mayor que 0 para caja.")
                    return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conexion=sqlite3.connect(self.entrada_ruta.get())   
        conexion.execute('''
            INSERT INTO pesos (producto, peso_paquete, peso_caja, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (producto, peso_paquete, peso_caja, timestamp))
        conexion.commit()
        conexion.close()
        self.entry_peso_paquete.delete(0, tk.END)
        self.entry_peso_caja.delete(0, tk.END)

        self.cargar_datos()
        messagebox.showinfo("Registro guardado", "Peso registrado correctamente.")
      
    def registrar_control_detector(self):
        producto = self.producto_combo.get()
        observacion = self.entry_observacion_detector.get().strip()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not observacion:
            messagebox.showwarning("Campo vacío", "Por favor, ingresa una observación.")
            return

        conexion = sqlite3.connect(self.entrada_ruta.get())
        try:
            conexion.execute("""
                INSERT INTO detector_metales (producto, observacion, fecha)
                VALUES (?, ?, ?)
            """, (producto, observacion, fecha))
            conexion.commit()
            self.entry_observacion_detector.delete(0, tk.END)
            self.cargar_datos()
        except:
            messagebox.showinfo("Error", "No se pudo guardar el registro.")
        finally:
            conexion.close()


    def leer_base(self):
        try:
            conexion=sqlite3.connect(self.entrada_ruta.get())            
            a = conexion.execute("""SELECT formula from producciones where estado = ? and (sector = ? or sector = ? or formula = ?);""",("programado","Nucleos_Comasa","Nucleos_Cereales","Leche_en_Polvo_Abanderadox800g"))  
            b = a.fetchall()                                    
            conexion.close()                        
            return list(b)
        
        except:
            messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")

    def leer_archivo(self):
        bd = la.Leer_archivo("archivo_bd.txt")   
        archivo_bd = bd.leer()
        if archivo_bd!= False:
            self.entrada_ruta.delete("0", "end")
            self.entrada_ruta.insert(0, (archivo_bd))
        else:
            messagebox.showinfo(message="Configure la Ruta a la Base de Datos", title="Ruta Erronea")

    def validar_entero(valor):
        return valor.isdigit() or valor == ""

    def cargar_datos(self):
        producto = self.producto_combo.get()

        # Cargar produccion
        for i in self.tree_produccion.get_children():
            self.tree_produccion.delete(i)
        conexion=sqlite3.connect(self.entrada_ruta.get())
        a = conexion.execute('''
            SELECT hora, pallet, lote, cantidad, comentario
            FROM produccion WHERE producto=?
            ORDER BY id DESC
        ''', (producto,))
        for fila in a.fetchall():
            self.tree_produccion.insert("", "end", values=fila)

        # Cargar pesos
        for i in self.tree_pesos.get_children():
            self.tree_pesos.delete(i)

        a = conexion.execute('''
            SELECT id, peso_paquete, peso_caja, timestamp
            FROM pesos WHERE producto=?
            ORDER BY id DESC
        ''', (producto,))
        b = a.fetchall()
        
        for fila in b:
            self.tree_pesos.insert("", "end", values=fila)
        
        c = conexion.execute("""SELECT presentacion, nom,max,min from limite_pesos where producto=?;""",(producto,))  
        d = c.fetchall()        
        
        for i in self.tree_pesos2.get_children():
            self.tree_pesos2.delete(i)
        
        for fila in d:
            self.tree_pesos2.insert("", "end", values=fila)
        conexion.close()

    def crear_formulario_control_embalaje(self):
           # Crear canvas con scrollbar dentro de la pestaña
        canvas = tk.Canvas(self.tab_control)
        scrollbar = ttk.Scrollbar(self.tab_control, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Frame scrollable donde van los formularios
        scrollable_frame = ttk.Frame(canvas)

        # Vincular el tamaño del frame al scroll
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def crear_seccion_control_paquete():
            frm = scrollable_frame
            frame = ttk.Frame(frm)
            frame.pack(fill="x", pady=10)
            ttk.Label(frame, text="CONTROL PAQUETE").grid(row=0, columnspan=8, pady=5)
            hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            producto = self.producto_combo.get()
            lote = self.entry_lote.get()
            entries = {}
            campos = ["Fechado", "Sellado", "Hermeticidad", "Resp. Control", "Resp. Verificación"]
            for i, campo in enumerate(campos):
                ttk.Label(frame, text=campo).grid(row=1, column=i)
                entries[campo] = ttk.Entry(frame)
                entries[campo].grid(row=2, column=i)
            
            ttk.Button(frame, text="Guardar", command=lambda: insertar_control_paquete(
                hora, producto, lote,entries["Fechado"].get(), entries["Sellado"].get(), entries["Hermeticidad"].get(),
                entries["Resp. Control"].get(), entries["Resp. Verificación"].get())).grid(row=3, columnspan=8, pady=5)
            
            campos = ["Hora", "Producto", "Lote", "Fechado", "Sellado", "Hermeticidad", "Resp. Control", "Resp. Verificación"]
            tree = ttk.Treeview(frame, columns=campos, show="headings", height=5)
            for campo in campos:
                tree.heading(campo, text=campo)
                tree.column(campo,width=120)
            tree.grid(row=4, columnspan=8, pady=5)

            def mostrar():
                tree.delete(*tree.get_children())
                registros = ejecutar_consulta("SELECT * FROM control_paquete").fetchall()
                for fila in registros:
                    tree.insert("", "end", values=fila)

            def eliminar():
                seleccionado = tree.selection()
                if not seleccionado:
                    return
                valores = tree.item(seleccionado[0])["values"]
                ejecutar_consulta("DELETE FROM control_paquete WHERE hora=? AND producto=? AND lote=?",
                                (valores[0], valores[1], valores[2]))
                tree.delete(seleccionado[0])

            ttk.Button(frame, text="Mostrar", command=mostrar).grid(row=5, column=2)
            ttk.Button(frame, text="Eliminar", command=eliminar).grid(row=5, column=3)

        def crear_seccion_control_cajas():
            frm = scrollable_frame
            frame = ttk.Frame(frm)
            frame.pack(fill="x", pady=10)
            ttk.Label(frame, text="CONTROL CAJAS").grid(row=6, columnspan=6, pady=5)
            hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            producto = self.producto_combo.get()
            lote = self.entry_lote.get()
            entries = {}
            campos = ["Fechado", "Etiqueta", "Responsable"]
            for i, campo in enumerate(campos):
                ttk.Label(frame, text=campo).grid(row=7, column=i)
                entries[campo] = ttk.Entry(frame)
                entries[campo].grid(row=8, column=i)

            ttk.Button(frame, text="Guardar", command=lambda: insertar_control_cajas(
                hora, producto, lote,
                entries["Fechado"].get(), entries["Etiqueta"].get(), entries["Responsable"].get())).grid(row=9, columnspan=6, pady=5)
            campos = ["Hora", "Producto", "Lote", "Fechado", "Etiqueta", "Responsable"]
            tree = ttk.Treeview(frame, columns=campos, show="headings", height=5)
            for campo in campos:
                tree.heading(campo, text=campo)
                tree.column(campo,width=120)
            tree.grid(row=10, columnspan=6, pady=5)

            def mostrar():
                tree.delete(*tree.get_children())
                registros = ejecutar_consulta("SELECT * FROM control_cajas").fetchall()
                for fila in registros:
                    tree.insert("", "end", values=fila)

            def eliminar():
                seleccionado = tree.selection()
                if not seleccionado:
                    return
                valores = tree.item(seleccionado[0])["values"]
                ejecutar_consulta("DELETE FROM control_cajas WHERE hora=? AND producto=? AND lote=?",
                                (valores[0], valores[1], valores[2]))
                tree.delete(seleccionado[0])

            ttk.Button(frame, text="Mostrar", command=mostrar).grid(row=11, column=2)
            ttk.Button(frame, text="Eliminar", command=eliminar).grid(row=11, column=3)

        def crear_seccion_control_palletizado():
            frm = scrollable_frame
            frame = ttk.Frame(frm)
            frame.pack(fill="x", pady=10)
            ttk.Label(frame, text="CONTROL PALLETIZADO").grid(row=12, columnspan=7, pady=5)
            hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            producto = self.producto_combo.get()
            lote = self.entry_lote.get()
            entries = {}
            campos = ["Armado", "Stretchado", "Identificación", "Responsable"]
            for i, campo in enumerate(campos):
                ttk.Label(frame, text=campo).grid(row=13, column=i)
                entries[campo] = ttk.Entry(frame)
                entries[campo].grid(row=14, column=i)

            ttk.Button(frame, text="Guardar", command=lambda: insertar_control_palletizado(
                hora, producto, lote,
                entries["Armado"].get(), entries["Stretchado"].get(), entries["Identificación"].get(),
                entries["Responsable"].get())).grid(row=15, columnspan=7, pady=5)
            campos = ["Hora", "Producto", "Lote", "Armado", "Stretchado", "Identificación", "Responsable"]
            tree = ttk.Treeview(frame, columns=campos, show="headings", height=5)
            for campo in campos:
                tree.heading(campo, text=campo)
                tree.column(campo,width=120)
            tree.grid(row=16, columnspan=7, pady=5)

            def mostrar():
                tree.delete(*tree.get_children())
                registros = ejecutar_consulta("SELECT * FROM control_palletizado").fetchall()
                for fila in registros:
                    tree.insert("", "end", values=fila)

            def eliminar():
                seleccionado = tree.selection()
                if not seleccionado:
                    return
                valores = tree.item(seleccionado[0])["values"]
                ejecutar_consulta("DELETE FROM control_palletizado WHERE producto=? AND hora=? AND lote=?",
                                (valores[1], valores[0], valores[2]))
                tree.delete(seleccionado[0])

            ttk.Button(frame, text="Mostrar", command=mostrar).grid(row=17, column=2)
            ttk.Button(frame, text="Eliminar", command=eliminar).grid(row=17, column=3)

        def crear_seccion_lotes_embalaje():
            frm = scrollable_frame
            frame = ttk.Frame(frm)
            frame.pack(fill="x", pady=10)
            ttk.Label(frame, text="LOTES EMBALAJE").grid(row=18, columnspan=6, pady=5)
            hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            producto = self.producto_combo.get()
            lote = self.entry_lote.get()
            entries = {}
            campos = ["Lote Film Bolsa", "Lote Caja", "Lote Etiqueta", "Motivo", "Responsable"]
            for i, campo in enumerate(campos):
                ttk.Label(frame, text=campo).grid(row=19, column=i)
                entries[campo] = ttk.Entry(frame)
                entries[campo].grid(row=20, column=i)

            ttk.Button(frame, text="Guardar", command=lambda: insertar_lotes_embalaje(hora,
                producto, lote, entries["Lote Film Bolsa"].get(),
                entries["Lote Caja"].get(), entries["Lote Etiqueta"].get(), entries["Motivo"].get(),entries["Responsable"].get())).grid(row=21, columnspan=6, pady=5)
            campos = ["Hora","Producto", "Lote", "Lote Film Bolsa", "Lote Caja", "Lote Etiqueta", "Motivo","Responsable"]
            tree = ttk.Treeview(frame, columns=campos, show="headings", height=5)
            for campo in campos:
                tree.heading(campo, text=campo)
                tree.column(campo,width=120)
            tree.grid(row=22, columnspan=6, pady=5)

            def mostrar():
                tree.delete(*tree.get_children())
                registros = ejecutar_consulta("SELECT * FROM lotes_embalaje").fetchall()
                for fila in registros:
                    tree.insert("", "end", values=fila)

            def eliminar():
                seleccionado = tree.selection()
                if not seleccionado:
                    return
                producto = tree.item(seleccionado[0])["values"][0]
                ejecutar_consulta("DELETE FROM lotes_embalaje WHERE producto=?", (producto,))
                tree.delete(seleccionado[0])

            ttk.Button(frame, text="Mostrar", command=mostrar).grid(row=23, column=2)
            ttk.Button(frame, text="Eliminar", command=eliminar).grid(row=23, column=3)
        
        crear_seccion_control_paquete()
        crear_seccion_control_cajas()
        crear_seccion_control_palletizado()
        crear_seccion_lotes_embalaje()

    def insertar_control_paquete(hora, producto, lote, fechado, sellado, hermeticidad, resp_control, resp_verificacion):
        query = """INSERT INTO control_paquete (hora, producto, lote, fechado, sellado, hermeticidad, resp_control, resp_verificacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
        try:
            ejecutar_consulta(query, (hora, producto, lote, fechado, sellado, hermeticidad, resp_control, resp_verificacion))
            messagebox.showinfo("Éxito", "Registro de control paquete guardado.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Registro duplicado o error en los datos.")

    def insertar_control_cajas(hora, producto, lote, fechado, etiqueta, responsable):
        query = """INSERT INTO control_cajas (hora, producto, lote, fechado, etiqueta, responsable)
                VALUES (?, ?, ?, ?, ?, ?)"""
        try:
            ejecutar_consulta(query, (hora, producto, lote, fechado, etiqueta, responsable))
            messagebox.showinfo("Éxito", "Registro de control cajas guardado.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Registro duplicado o error en los datos.")

    def insertar_control_palletizado(hora, producto, lote, armado, stretchado, identificacion, responsable):
        query = """INSERT INTO control_palletizado (hora, producto, lote, armado_conforme, stretchado_conforme, identificacion, responsable)
                VALUES (?, ?, ?, ?, ?, ?, ?)"""
        try:
            ejecutar_consulta(query, (hora, producto, lote, armado, stretchado, identificacion, responsable))
            messagebox.showinfo("Éxito", "Registro de palletizado guardado.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Registro duplicado o error en los datos.")

    def insertar_lotes_embalaje(producto, lote, lote_film_bolsa, lote_caja, loe_etiqueta, motivo):
        query = """INSERT INTO lotes_embalaje (producto, lote, lote_film_bolsa, lote_caja, loe_etiqueta, motivo)
                VALUES (?, ?, ?, ?, ?, ?) 
                ON CONFLICT(producto) DO UPDATE SET 
                lote=excluded.lote, lote_film_bolsa=excluded.lote_film_bolsa,
                lote_caja=excluded.lote_caja, loe_etiqueta=excluded.loe_etiqueta, motivo=excluded.motivo"""
        ejecutar_consulta(query, (producto, lote, lote_film_bolsa, lote_caja, loe_etiqueta, motivo))
        messagebox.showinfo("Éxito", "Registro de lotes de embalaje guardado o actualizado.")


if __name__ == "__main__":
    app = ProduccionPesosApp()      
    app.mainloop()