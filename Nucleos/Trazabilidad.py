import tkinter as tk
from tkinter import *
from tkinter import ttk,messagebox, filedialog
import sqlite3
from datetime import datetime
from csv import reader, writer

from functools import partial
import Leer_archivo as la 
import csv
ruta_txt = "/archnucl"
import sys
sector = ""
dic_res_stock = {}
def leer_archivo():
    bd = la.Leer_archivo("archivo_bd.txt")   
    archivo_bd = bd.leer()
    if archivo_bd!= False:
        entrada_ruta_bd.delete("0", "end")
        entrada_ruta_bd.insert(0, (archivo_bd))
    else:
        messagebox.showinfo(message="Configure la Ruta a la Base de Datos", title="Ruta Erronea")

    reg = la.Leer_archivo("archivo_ruta_registro.txt")
    archivo_reg = reg.leer()
    if archivo_reg!= False:
        entrada_ruta_registro.delete("0", "end")
        entrada_ruta_registro.insert(0, (archivo_reg))        
    else:
        messagebox.showinfo(message="Configure la Ruta a la Carpeta de Registros", title="Ruta Erronea")

def leer_base():
    try:
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        #a = conexion.execute("""SELECT mp FROM mp;""")         
        #mp['values'] = list(a)   
       
        conexion.close()        
    except:
        messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")
    
def selecionar_ruta():    
    ruta_guardar = []
    ruta_bd = filedialog.askopenfilename(initialdir="/", title="Seleccionar Base de Datos")                                        
    entrada_ruta_bd.delete("0", "end")
    entrada_ruta_bd.insert(0, str(ruta_bd))
    ruta_guardar.append(ruta_bd) 
    try: 
        archivo = open(ruta_txt + "/archivo_bd.txt", "w")
        archivo_csv = writer(archivo)
        archivo_csv.writerow(ruta_guardar)
        archivo.close()
        leer_archivo()
    except:
        messagebox.showinfo(message="Error al Configurar la Ruta", title="Ruta Erronea")
     
def buscar():        
    for s in cuadro.get_children():
            cuadro.delete(s)
    codprod = codigo.get()
    
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    a = conexion.execute("""SELECT sector FROM producciones WHERE codprod = ? ;""",(codprod,))         
    b = a.fetchall()      
    a = conexion.execute("""SELECT * FROM %s WHERE codprod = ? ; """ %b[0][0], (codprod,))         
    b = a.fetchall()  
    
    for i in b:
        cuadro.insert("", tk.END, text=i[0],
                            values=(i[11],i[2],i[3],i[1],i[4],i[6],i[7],i[5],i[8],i[9],i[12]))
    conexion.close()

    
#def buscar_lote(s):
    #MP = mp.get()
    #conexion=sqlite3.connect(entrada_ruta_bd.get())
    #a = conexion.execute("""SELECT lote FROM recepcion WHERE mp = ?;""", (MP,))         
    #lote["values"] = list(a) 

def exportar():
    try:       
        ruta = entrada_ruta_registro.get()
        with open(ruta + "/" + 'reporte.csv', 'w', newline='') as f:       
            writer = csv.writer(f,delimiter=';') 
            guardar = ["Codigo de Produccion","Formula","Fecha","Hora","N° de Batch","MP","Lote","Vto","Deposito", "Cantida", "Responsable","Comentario"]
            writer.writerow(guardar)        
            for i in cuadro.get_children():
                guardar.clear()            
                guardar.append((cuadro.item(i)["text"]))    
                for t in cuadro.item(i)["values"]:
                    guardar.append(t)
                writer.writerow(guardar)    
    except:
        messagebox.showinfo(message="Error al Exportar Datos", title="Error")

def cerrar():
    ventana.destroy
    sys.exit()

def selecionar_ruta(s):    
    if  s == "bd":
        ruta_guardar = []
        ruta_bd= filedialog.askopenfilename(initialdir="/", title="Seleccionar Base de Datos")                                        
        entrada_ruta_bd.delete("0", "end")
        entrada_ruta_bd.insert(0, str(ruta_bd))
        ruta_guardar.append(ruta_bd) 
        try: 
            archivo = open(ruta_txt + "/archivo_bd.txt", "w")
            archivo_csv = writer(archivo)
            archivo_csv.writerow(ruta_guardar)
            archivo.close()
            leer_archivo()
        except:
            messagebox.showinfo(message="Error al Configurar la Ruta", title="Ruta Erronea")
    if s == "registro":
        ruta_guardar = []
        ruta_registro= filedialog.askdirectory(initialdir="/", title="Seleccionar Base de Datos")                                        
        entrada_ruta_registro.delete("0", "end")
        entrada_ruta_registro.insert(0, str(ruta_registro))
        ruta_guardar.append(ruta_registro) 
        try: 
            archivo = open(ruta_txt + "/archivo_ruta_registro.txt", "w")
            archivo_csv = writer(archivo)
            archivo_csv.writerow(ruta_guardar)
            archivo.close()
            leer_archivo()
        except:
            messagebox.showinfo(message="Error al Configurar la Ruta de Registro", title="Ruta Erronea")


ventana = Tk()
ventana.protocol("WM_DELETE_WINDOW", cerrar)
ventana.geometry("1200x700")
ventana.title("CALIDAD")
tab_control = ttk.Notebook(ventana, width=1200, height=700)
tab_control.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_prod = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_prod.place(x=0, y=0, relheight=1, relwidth=1)

pestaña_config = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_config.place(x=0, y=0, relheight=1, relwidth=1)
tab_control.add(pestaña_prod, text="Calidad")
tab_control.add(pestaña_config, text="Configuracion")
label_ruta_bd = ttk.Label(pestaña_config, text="Ruta a Base de Datos")
label_ruta_bd.place(relx=0.1, rely=0.14)
entrada_ruta_bd = ttk.Entry(pestaña_config, width=80)
entrada_ruta_bd.place(relx=0.27, rely=0.14)
boton_ruta_bd = ttk.Button(pestaña_config, text="Config. Ruta", command = lambda: selecionar_ruta("bd"))
boton_ruta_bd.place(relx=0.8, rely=0.14)
label_codigo = ttk.Label(pestaña_prod, text="Codigo de Produccion")
label_codigo.place(relx=0.01, rely=0.01)
#label_mp = ttk.Label(pestaña_prod, text="Materia Prima")
#label_mp.place(relx=0.01, rely=0.08)
#label_sec = ttk.Label(pestaña_prod, text="Sector")
#label_sec.place(relx=0.01, rely=0.08)

#label_lote = ttk.Label(pestaña_prod, text="Lote")
#label_lote.place(relx=0.01, rely=0.22)
codigo = ttk.Entry(pestaña_prod, width=30)
codigo.place(relx=0.12, rely=0.01)
###select_sector = ttk.Combobox(pestaña_prod, width=20,values=["Nucleos_Jarabe","Macro_Jarabe","Nucleos_Cereales","Nucleos_Comasa", "Macro_Comasa", "Macro_Cereales", "Carga_Cereales"])
#select_sector.place(relx=0.11, rely=0.08)
#mp = ttk.Combobox(pestaña_prod, width=40)
#mp.place(relx=0.11, rely=0.08)
#mp.bind("<<ComboboxSelected>>", partial(buscar_lote))
#lote = ttk.Combobox(pestaña_prod, width=40)
#lote.place(relx=0.11, rely=0.22)
cuadro = ttk.Treeview(pestaña_prod, columns=("Formula","Fecha","Hora","N° de Batch","MP","Lote","Vto","Deposito","Cantidad","Responsable","Comentario"))
cuadro.column("#0", width=20, anchor="center")
cuadro.column("Formula", width=20, anchor="center")
cuadro.column("Fecha", width=20, anchor="center")
cuadro.column("Hora", width=20, anchor="center")
cuadro.column("N° de Batch", width=20, anchor="center")
cuadro.column("MP", width=80, anchor="center")
cuadro.column("Lote", width=30, anchor="center")
cuadro.column("Vto", width=30, anchor="center")
cuadro.column("Deposito", width=30, anchor="center")
cuadro.column("Cantidad", width=30, anchor="center")
cuadro.column("Responsable", width=30, anchor="center")
cuadro.column("Comentario", width=30, anchor="center")
cuadro.heading("#0", text="CodigoProd")
cuadro.heading("Formula", text="Formula")
cuadro.heading("Fecha", text="Fecha")
cuadro.heading("Hora", text="Hora")
cuadro.heading("N° de Batch", text="N° de Batch")
cuadro.heading("MP", text="MP")
cuadro.heading("Lote", text="Lote")
cuadro.heading("Vto", text="Vto")
cuadro.heading("Deposito", text="Deposito")
cuadro.heading("Cantidad", text="Cantidad")
cuadro.heading("Responsable", text="Responsable")
cuadro.heading("Comentario", text="Comentario")

barra = ttk.Scrollbar(cuadro,orient=tk.HORIZONTAL)
barra.set(0,1)
cuadro.place(relx=0.01, rely=0.25, relwidth=0.98, relheight=0.7)
barra.place(relx=0.002, rely=0.94, relwidth=0.997)
cuadro.xview_moveto(0.9)

boton_buscar = ttk.Button(pestaña_prod, text="Buscar", command=buscar)
boton_buscar.place(relx=0.3, rely=0.01, relheight=0.07)
boton_exportar = ttk.Button(pestaña_prod, text="Exportar", command= exportar)
boton_exportar.place(relx=0.3, rely=0.11, relheight=0.07)
label_ruta_registro = ttk.Label(pestaña_config, text="Ruta a Carpeta de Registros")
label_ruta_registro.place(relx=0.1, rely=0.3)
entrada_ruta_registro = ttk.Entry(pestaña_config, width= 60)
entrada_ruta_registro.place(relx=0.27, rely=0.3)
configurar_ruta_registro = ttk.Button(pestaña_config,command = partial(selecionar_ruta,"registro"),text="Conf. Ruta")
configurar_ruta_registro.place(relx=0.8, rely=0.3)
leer_archivo()
leer_base()
ventana.mainloop()
