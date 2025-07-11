import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from tkinter import ttk,messagebox, filedialog
import Leer_archivo as la 
from csv import reader, writer
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
        self.tab_config = ttk.Frame(self.tabs)

        self.tabs.add(self.tab_produccion, text="Producción diaria")       
        self.tabs.add(self.tab_config, text="Config")
        # Producto seleccionado
        self.crear_tab_config()
        self.leer_archivo()
        PRODUCTOS = self.leer_base()
        self.producto_combo = ttk.Combobox(frame_producto, values=PRODUCTOS, state="readonly", width=40)
        self.producto_combo.pack(side="left", padx=5)
        self.producto_combo.bind("<<ComboboxSelected>>", lambda e: self.cargar_datos())    
        
        self.crear_tab_produccion()
            
       
    def crear_tab_produccion(self):
        frm = self.tab_produccion

        # Formulario
        form = ttk.Frame(frm)
        form.pack(fill="x", pady=10)

        ttk.Label(form, text="N° de Pallet:").grid(row=0, column=0, sticky="e", padx=5, pady=3)
        
        self.entry_pallet = ttk.Entry(form,validate="key",validatecommand=(frm.register(self.validar_entero),"%S"))
        self.entry_pallet.grid(row=0, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(form, text="Lote:").grid(row=0, column=2, sticky="e", padx=5, pady=3)
        self.entry_lote = ttk.Entry(form)
        self.entry_lote.grid(row=0, column=3, sticky="w", padx=5, pady=3)

        ttk.Label(form, text="Vto:").grid(row=0, column=4, sticky="e", padx=5, pady=3)
        self.entry_vto = ttk.Entry(form)
        self.entry_vto.grid(row=0, column=5, sticky="w", padx=5, pady=3)

        ttk.Label(form, text="Cantidad de cajas:").grid(row=1, column=0, sticky="e", padx=5, pady=3)
        self.entry_cantidad = ttk.Entry(form,validate="key",validatecommand=(frm.register(self.validar_entero),"%S"))
        self.entry_cantidad.grid(row=1, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(form, text="Comentario:").grid(row=1, column=2, sticky="e", padx=5, pady=3)
        self.entry_comentario = ttk.Entry(form, width=30)
        self.entry_comentario.grid(row=1, column=3, sticky="w", padx=5, pady=3)
        ttk.Label(form, text="Responsable:").grid(row=1, column=4, sticky="e", padx=5, pady=3)
        self.entry_resp = ttk.Entry(form, width=30)
        self.entry_resp.grid(row=1, column=5, sticky="w", padx=5, pady=3)

        btn_guardar = ttk.Button(form, text="Agregar registro", command=self.agregar_registro_produccion)
        btn_guardar.grid(row=2, column=0, columnspan=4, pady=8)
        btn_eliminar = ttk.Button(form, text="Eliminar registro seleccionado", command=self.eliminar_registro)
        btn_eliminar.grid(row=2, column=4, columnspan=2, pady=8)

        # Tabla con scrollbar
        tabla_frame = ttk.Frame(frm)
        tabla_frame.pack(fill="both", expand=True)

        columnas = ("id", "hora","Producto","pallet", "lote","Vto" ,"cantidad", "comentario")
        self.tree_produccion = ttk.Treeview(tabla_frame, columns=columnas, show="headings")
        for col in columnas:
            self.tree_produccion.heading(col, text=col.capitalize())
            if col == "id":
                self.tree_produccion.column(col, width=0, stretch=False)  # Oculta ID
            else:
                self.tree_produccion.column(col, anchor="center",minwidth=10 , width=50)
        self.tree_produccion.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tree_produccion.yview)
        self.tree_produccion.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

      
    def agregar_registro_produccion(self):
        vto = self.entry_vto.get().strip()
        pallet = self.entry_pallet.get().strip()
        lote = self.entry_lote.get().strip()
        cantidad = self.entry_cantidad.get().strip()
        comentario = self.entry_comentario.get().strip()
        conexion = sqlite3.connect(self.entrada_ruta.get())
        resp = self.entry_resp.get()
        if not pallet or not lote or not cantidad or not vto:
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
                INSERT INTO despacho (hora,producto,pallet, lote,vto,cantidad, comentario, responsable)
                VALUES (?, ?, ?, ?, ?, ?,?,?)
            ''', (hora,producto, pallet, lote,vto ,cantidad, comentario,resp))
            conexion.commit()
            conexion.execute('''
                UPDATE ordenes SET producido = producido + ? where Producto = ? and Estado = pendiente''', (cantidad,producto))
            conexion.commit()
            conexion.close()
        except:
            messagebox.showinfo(message="Dato Invalido", title="Error")
            conexion.close()
            return

        #self.entry_pallet.delete(0, tk.END)        
        self.entry_comentario.delete(0, tk.END)
        self.cargar_datos()
        #messagebox.showinfo("Registro guardado", "Registro de producción agregado correctamente.")
        conexion.close()
 
    def eliminar_registro(self):
        seleccionado = self.tree_produccion.selection()
        if not seleccionado:
            messagebox.showwarning("Sin selección", "Selecciona un registro para eliminar.")
            return

        item = self.tree_produccion.item(seleccionado[0])
        id_registro = item["values"][0]  # ID está en la primera posición

        try:
            conexion = sqlite3.connect(self.entrada_ruta.get())
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM despacho WHERE id = ?", (id_registro,))
            conexion.commit()
            conexion.close()
        except Exception as e:
            messagebox.showerror("Error al eliminar", f"No se pudo eliminar el registro:\n{e}")
            return

        self.tree_produccion.delete(seleccionado[0])
        messagebox.showinfo("Registro eliminado", "El registro fue eliminado correctamente.")
    
    
    def crear_tab_config(self):
        frm = self.tab_config      
        label_ruta = ttk.Label(frm, text="Ruta a Base de Datos")
        label_ruta.place(relx=0.05, rely=0.7)        
        self.entrada_ruta = ttk.Entry(frm, width= 60)
        self.entrada_ruta.place(relx=0.27, rely=0.7)  
        btn_guardar = ttk.Button(frm, text="Conf. Ruta", command= self.selecionar_ruta)
        btn_guardar.place(relx=0.8, rely=0.7)

      
    def selecionar_ruta(self):    
        ruta_guardar = []
        ruta_bd= filedialog.askopenfilename(initialdir="/", title="Seleccionar Base de Datos")                                        
        self.entrada_ruta.delete("0", "end")
        self.entrada_ruta.insert(0, str(ruta_bd))
        ruta_guardar.append(ruta_bd) 
        try: 
            archivo = open(ruta_txt + "/archivo_bd.txt", "w")
            archivo_csv = writer(archivo)
            archivo_csv.writerow(ruta_guardar)
            archivo.close()
            self.leer_archivo()
        except:
            messagebox.showinfo(message="Error al Configurar la Ruta", title="Ruta Erronea")
            
    

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

    def validar_entero(s,valor):
        try:
            int(valor)
            return True
        except:      
            return False        

    def cargar_datos(self):
        producto = self.producto_combo.get()

        # Cargar produccion
        for i in self.tree_produccion.get_children():
            self.tree_produccion.delete(i)
        conexion=sqlite3.connect(self.entrada_ruta.get())
        a = conexion.execute('''
            SELECT id, hora,producto,pallet, lote,vto,cantidad, comentario
            FROM despacho WHERE producto=?
            ORDER BY id DESC
        ''', (producto,))
        for fila in a.fetchall():
            self.tree_produccion.insert("", "end", values=fila)

   
if __name__ == "__main__":
    app = ProduccionPesosApp()      
    app.mainloop()