from tkinter import *
from tkinter import ttk,messagebox, filedialog
import sqlite3
from csv import reader, writer
from functools import partial
import Leer_archivo as la 
ruta_txt = "/archnucl"


def leer_archivo():
    bd = la.Leer_archivo("archivo_bd.txt")   
    archivo_bd = bd.leer()
    if archivo_bd!= False:
        entrada_ruta.delete("0", "end")
        entrada_ruta.insert(0, (archivo_bd))
    else:
        messagebox.showinfo(message="Configure la Ruta a la Base de Datos", title="Ruta Erronea")

def leer_base():
    try:
        conexion=sqlite3.connect(entrada_ruta.get())
        a = conexion.execute("""SELECT DISTINCT deposito FROM mp ;""")         
        entrada_deposito_for['values'] = list(a)   
        a = conexion.execute("""SELECT nombre from formulas;""")         
        selec_formula['values'] = list(a)           
        conexion.close()        
        selec_sector['values'] = ["Nucleos_Jarabe","Macro_Jarabe","Nucleos_Cereales","Nucleos_Comasa", "Macro_Comasa", "Macro_Cereales", "Carga_Cereales"]
    
    except:
        messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")
    
def selecionar_ruta():    
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
    
def alta_insumo():
    mp = ""
    a = entrada_mp.get()
    deposito = entrada_deposito.get().upper()
    codigo = entrada_codigo.get()    
    #try:
    if a != "":
        for i in a:
            if i ==" ":
                mp = mp + "_"
            else:
                mp = mp + i           
    conexion=sqlite3.connect(entrada_ruta.get())    
    a = conexion.execute("""SELECT * FROM depositos WHERE deposito = ?;""",(deposito,))
    b = a.fetchall()
    if b == []:
        conexion.execute("""insert into depositos (deposito)
        VALUES(?);""",(deposito,))
        conexion.commit()         
    conexion.execute("""insert into mp (mp,deposito,codmp)
    VALUES(?,?,?);""",(mp,deposito,codigo))
    conexion.commit()                     
    conexion.close()    
    buscar()
    #except:
    #    messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")

def alta_formula():  
        nom_for = ""
        sector = selec_sector.get()        
        a = str(entrada_nombre_for.get())  
        codigo = entrada_codigo_for.get()   
                 
        if a != "" and sector != "" and codigo != "":
            for i in a:
                if i ==" ":
                    nom_for = nom_for + "_"
                else:
                    nom_for = nom_for + i           
           
            conexion=sqlite3.connect(entrada_ruta.get())
            conexion.execute(""" CREATE TABLE IF NOT EXISTS '%s' (                            
                            mp TEXT NOT NULL,
                            deposito TEXT NOT NULL,
                            cantidad REAL NOT NULL,
                            sector TEXT NOT NULL,                            
                            formula TEXT NOT NULL,
                            codfor  TEXT NOT NULL,
                             codmp TEXT NOT NULL,
                            FOREIGN KEY("codfor") REFERENCES "formulas"("codfor"), 
                            FOREIGN KEY("codmp") REFERENCES "mp"("codmp"),                          
                            PRIMARY KEY(mp)
            );""" % nom_for)            
            conexion.commit()                     
            conexion.execute("""insert into formulas (nombre,sector,codfor)
            VALUES(?,?,?);""",(nom_for,sector,codigo))              
            conexion.commit()  
            a = conexion.execute("""SELECT nombre from formulas;""")         
            selec_formula['values'] = list(a)        
            conexion.close()          
            
        else:
            messagebox.showinfo(message="Ingrese el Nombre de Formula", title="Ingrese Nombre")
    
def agregar_insumo():
    nom_for = entrada_nombre_for.get()
    mp = entrada_mp_for.get()
    selec_formula.set(nom_for)
    cantidad = entrada_cantidad_for.get()
    deposito = entrada_deposito_for.get()

    if nom_for == "" or mp == "" or cantidad == "" or deposito == "":
        messagebox.showinfo(message="Complete los Campos", title="Error")
        return

    try:    
        conexion=sqlite3.connect(entrada_ruta.get())
        a = conexion.execute("""SELECT * FROM formulas WHERE nombre = ?;""",(nom_for,))
        b = a.fetchall()    
    except:
            messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error al Conectar con Base de Datos")
            conexion.close()
            return
        
    if b != []:
        try:
            d = conexion.execute("""SELECT codmp FROM mp WHERE mp = ?;""",(mp,))
            e = d.fetchall()   
            conexion.execute("""insert into %s (mp,deposito,cantidad,sector,formula,codfor,codmp)
                VALUES(?,?,?,?,?,?,?);""" % nom_for ,(mp,deposito,cantidad,b[0][1], nom_for,b[0][2],e[0][0]))
            conexion.commit()                  
            conexion.close()
            buscar_formula()
        except:
            messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error al Conectar con Base de Datos")
            conexion.close()
            return
    else:
        messagebox.showinfo(message="La Formula no Existe", title="Error al Conectar con Base de Datos")
        conexion.close()
    
def eliminar_insumo():
    nom_for = entrada_nombre_for.get()
    try:
        elemento_seleccionado = cuadro_formula.item(cuadro_formula.selection())["text"]
        
        conexion=sqlite3.connect(entrada_ruta.get()) 

        conexion.execute("""DELETE FROM %s WHERE mp = ?;""" % nom_for, (elemento_seleccionado,)) 
        conexion.commit()   
        conexion.close()
        buscar_formula()
    except:
            messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")
            
def seleccionar_deposito(s):
    dep = entrada_deposito_for.get()
    try:
        conexion=sqlite3.connect(entrada_ruta.get())
        a = conexion.execute("""SELECT mp FROM mp WHERE deposito = ?;""", (dep,))         
        entrada_mp_for['values'] = list(a)           
        conexion.close()
    except:
        messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")

def buscar():    
    try:
        conexion=sqlite3.connect(entrada_ruta.get())
        a = conexion.execute(""" SELECT * FROM mp;""")
        j = 0
        for s in cuadro.get_children():
            cuadro.delete(s)
        for i in a:
            cuadro.insert("", j, text=i[0], values=(i[1], i[2]))
            j +=1               
        conexion.close()
    except:
            messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")

def buscar_formula():    
    try:
        nom_for = selec_formula.get()
        entrada_nombre_for.delete(0,"end")
        entrada_nombre_for.insert(0,nom_for)
        
        conexion=sqlite3.connect(entrada_ruta.get())
        a = conexion.execute(""" SELECT * FROM %s;""" % nom_for)
        j = 0
        for s in cuadro_formula.get_children():
            cuadro_formula.delete(s)
        for i in a:
            cuadro_formula.insert("", j, text=i[0], values=(i[1],i[2],i[3]))
            j +=1               
        conexion.close()
    except:
            messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")
    
def eliminar():
    try:
        elemento_seleccionado = cuadro.item(cuadro.selection())["text"]
        conexion=sqlite3.connect(entrada_ruta.get())
        conexion.execute("""PRAGMA Foreign_keys = ON;""")        
        conexion.execute("""DELETE FROM mp WHERE mp = ?;""", (elemento_seleccionado,)) 
        conexion.commit()             
        conexion.close()
        buscar()
    except:
            messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")

def validar_entrada(numero):
    try:
        int(numero)
        return True
    except:
        if numero == ".":
            return True
        else:
            return False
        
def validar_entrada_nom(numero):        
    if numero != "." and numero != "*" and numero != "," and numero != "+" and numero != "/":
        return True
    else:
        return False
            

def cerrar():
    ventana.destroy()
  
ventana = Tk()
ventana.geometry("800x600")
ventana.title("Alta")
tab_control = ttk.Notebook(ventana, width=800, height=650)
tab_control.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_insumo = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_insumo.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_formula = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_formula.place(x=0, y=0, relheight=1, relwidth=1)

pestaña_conf = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_conf.place(x=0, y=0, relheight=1, relwidth=1)
tab_control.add(pestaña_insumo, text="Alta Insumos")
tab_control.add(pestaña_formula, text="Alta Formula")
tab_control.add(pestaña_conf, text="Configuracion")
label_ruta = ttk.Label(pestaña_conf, text="Ruta a Base de Datos")
label_mp = ttk.Label(pestaña_insumo, text="Materia Prima")
label_entrada_deposito = ttk.Label(pestaña_insumo, text="Deposito")
label_codigo = ttk.Label(pestaña_insumo, text="CodigoMP")
label_ruta.place(relx=0.05, rely=0.7)
label_mp.place(relx=0.01, rely=0.1)
label_entrada_deposito.place(relx=0.35, rely=0.1)
label_codigo.place(relx=0.6, rely=0.1)

entrada_ruta = ttk.Entry(pestaña_conf, width= 60)
entrada_mp = ttk.Entry(pestaña_insumo, width=25,validate="key",validatecommand=((pestaña_insumo.register(validar_entrada_nom)),"%S"))
entrada_deposito = ttk.Entry(pestaña_insumo, width=15)
entrada_codigo = ttk.Entry(pestaña_insumo, width=10)
entrada_ruta.place(relx=0.27, rely=0.7)
entrada_mp.place(relx=0.12, rely=0.1)
entrada_deposito.place(relx=0.45, rely=0.1)
entrada_codigo.place(relx=0.7, rely=0.1)

configurar_ruta = ttk.Button(pestaña_conf,command = selecionar_ruta,text="Conf. Ruta")
configurar_ruta.place(relx=0.8, rely=0.7)

alta = ttk.Button(pestaña_insumo,command=alta_insumo,text="Alta")
alta.place(relx=0.45, rely=0.3)
boton_buscar = ttk.Button(pestaña_insumo,command=buscar,text="Buscar")
boton_buscar.place(relx=0.1, rely=0.3)
boton_eliminar = ttk.Button(pestaña_insumo,command=eliminar,text="Eliminar")
boton_eliminar.place(relx=0.8, rely=0.3)
agregar = ttk.Button(pestaña_formula,command= agregar_insumo,text="Agregar MP")
agregar.place(relx=0.7, rely=0.09)
eliminar_formula= ttk.Button(pestaña_formula,command= eliminar_insumo,text="Eliminar MP")
eliminar_formula.place(relx=0.85, rely=0.09)
alta_formul = ttk.Button(pestaña_formula,command=alta_formula,text="Alta Formula")
alta_formul.place(relx=0.9, rely=0.01)
buscar_formul = ttk.Button(pestaña_formula,command=buscar_formula,text="Buscar Formula")
buscar_formul.place(relx=0.2, rely=0.17)

cuadro = ttk.Treeview(pestaña_insumo, columns=("Deposito","CodigoMP"))
barra = ttk.Scrollbar(cuadro)
cuadro.column("#0", width=120, anchor="center")
cuadro.column("Deposito", width=30, anchor="center")
cuadro.column("CodigoMP", width=30, anchor="center")
cuadro.heading("#0", text="Materia Prima")
cuadro.heading("Deposito", text="Deposito")
cuadro.heading("CodigoMP", text="CodigoMP")
cuadro.config(yscrollcommand=barra.set)
barra.config(command=cuadro.yview)
cuadro.place(relx=0.1, rely=0.4, relwidth=0.8, relheight=0.5)
barra.place(relx=0.96, rely=0.11, relheight=0.87)

cuadro_formula = ttk.Treeview(pestaña_formula, columns=("Deposito","Cantidad","Registro"))
barra_formula = ttk.Scrollbar(cuadro_formula)
cuadro_formula.column("#0", width=130, anchor="center")
cuadro_formula.column("Deposito", width=20, anchor="center")
cuadro_formula.column("Cantidad", width=20, anchor="center")
cuadro_formula.column("Registro", width=30, anchor="center")
cuadro_formula.heading("#0", text="Materia Prima")
cuadro_formula.heading("Deposito", text="Deposito")
cuadro_formula.heading("Cantidad", text="Cantidad")
cuadro_formula.heading("Registro", text="Sector")
cuadro_formula.config(yscrollcommand=barra.set)
barra_formula.config(command=cuadro.yview)
cuadro_formula.place(relx=0.05, rely=0.4, relwidth=0.9, relheight=0.5)
barra_formula.place(relx=0.964, rely=0.11, relheight=0.87)

label_nombre_formula = ttk.Label(pestaña_formula, text="Formula")
label_mp_formula = ttk.Label(pestaña_formula, text="Materia Prima")
label_entrada_deposito_for = ttk.Label(pestaña_formula, text="Deposito")
label_cantidad = ttk.Label(pestaña_formula, text="Cantidad")
label_sector = ttk.Label(pestaña_formula, text="Sector")


label_nombre_formula.place(relx=0.01, rely=0.01)
label_mp_formula.place(relx=0.23, rely=0.09)
label_entrada_deposito_for.place(relx=0.01, rely=0.09)
label_cantidad.place(relx=0.52, rely=0.09)
label_sector.place(relx=0.35, rely=0.01)

entrada_nombre_for = ttk.Entry(pestaña_formula, width=25,validate="key",
                           validatecommand=((pestaña_formula.register(validar_entrada_nom)), "%S"))
entrada_mp_for = ttk.Combobox(pestaña_formula, width=20, state="readonly")
entrada_deposito_for = ttk.Combobox(pestaña_formula, width=10, state="readonly")
entrada_deposito_for.bind("<<ComboboxSelected>>", partial(seleccionar_deposito))
entrada_cantidad_for = ttk.Entry(pestaña_formula, width=10,validate="key",
                           validatecommand=((pestaña_formula.register(validar_entrada)), "%S"))

selec_sector = ttk.Combobox(pestaña_formula, width=15,state="readonly")
entrada_nombre_for.place(relx=0.12, rely=0.01)
entrada_mp_for.place(relx=0.33, rely=0.09)
entrada_deposito_for.place(relx=0.12, rely=0.09)
entrada_cantidad_for.place(relx=0.6, rely=0.09)
selec_sector.place(relx=0.4, rely=0.01)

selec_formula = ttk.Combobox(pestaña_formula, width=15,state="readonly")
selec_formula.place(relx=0.01, rely=0.17)
entrada_codigo_for = ttk.Entry(pestaña_formula, width=20)
entrada_codigo_for.place(relx=0.7, rely=0.01)
label_cod = ttk.Label(pestaña_formula, text="Cod. Formula")
label_cod.place(relx=0.6, rely=0.01)

leer_archivo()
leer_base()
ventana.mainloop()