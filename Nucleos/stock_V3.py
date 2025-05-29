import tkinter as tk
from tkinter import *
from tkinter import ttk,messagebox, filedialog
import sqlite3
from datetime import datetime
import csv
from csv import writer
from functools import partial
import Leer_archivo as la 
import time

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
        a = conexion.execute("""SELECT DISTINCT mp FROM stock;""")
        combobox['values'] = list(a)        
        a = conexion.execute("""SELECT DISTINCT lote FROM stock;""") 
        combobox_lote['values'] = list(a)
        a = conexion.execute("""SELECT DISTINCT deposito FROM stock;""") 
        combobox_deposito['values'] = list(a)
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
     
def buscar(s,t):
    if s == "mp":
        for s in cuadro.get_children():
            cuadro.delete(s)
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        if check_nulos_value.get()==False:
            a = conexion.execute("""SELECT * FROM stock WHERE mp = ? and stock != ?;""", (combobox.get(),0))        
            b = a.fetchall()
        else:
            a = conexion.execute("""SELECT * FROM stock WHERE mp = ?;""", (combobox.get(),))
            b = a.fetchall()        
        for i in b:
            cuadro.insert("", tk.END, text=i[0],
                                values=(i[2],i[5],round(i[3],3),i[1],i[6]))
        conexion.close()
    if s == "lote":
        for s in cuadro.get_children():
            cuadro.delete(s)
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        if check_nulos_value.get()==False:
            a = conexion.execute("""SELECT * FROM stock WHERE lote = ? and stock !=?;""", (combobox_lote.get(),0))         
            b = a.fetchall()  
        else:
            a = conexion.execute("""SELECT * FROM stock WHERE lote = ?;""", (combobox_lote.get(),))         
            b = a.fetchall() 

        for i in b:
            cuadro.insert("", tk.END, text=i[0],
                               values=(i[2],i[5],round(i[3],3),round(i[4],3),i[1],i[6]))
        conexion.close()
    if s == "deposito":
        for s in cuadro.get_children():
            cuadro.delete(s)
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        if check_nulos_value.get()==False:
            a = conexion.execute("""SELECT * FROM stock WHERE deposito = ? and stock !=?;""", (combobox_deposito.get(),0))         
            b = a.fetchall()
        else:
            a = conexion.execute("""SELECT * FROM stock WHERE deposito = ?;""", (combobox_deposito.get(),))         
            b = a.fetchall()  
        for i in b:
            cuadro.insert("", tk.END, text=i[0],
                                values=(i[2],i[5],round(i[3],3),round(i[4],3),i[1],i[6]))
        conexion.close()
    
def exportar():
    ruta = entrada_ruta_registro.get()    
    with open(ruta + "/" + "reporte.csv", 'w', newline='') as f:       
        writer = csv.writer(f,delimiter=';') 
        guardar = ["MP","Lote","Vto","Cantidad", "Deposito","Estado"]
        writer.writerow(guardar)        
        for i in cuadro.get_children():
            guardar.clear()         
            guardar.append(cuadro.item(i)["text"])       
            for t in cuadro.item(i)["values"]:
                guardar.append(t)
            writer.writerow(guardar)   
    
    
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

def actualizar():
    nuevo_stock = (entrada_stock.get())
    if nuevo_stock == "":
        messagebox.showinfo(message="Ingrese Nuevo Stock", title="Error")
        return
    if responsable.get() == "":
        messagebox.showinfo(message="Ingrese Responsable", title="Error")
        return
    try:
        lote = cuadro.item(cuadro.selection())["values"][0]
        mp =  cuadro.item(cuadro.selection())["text"]    
        deposito = cuadro.item(cuadro.selection())["values"][3]    
        stockant = cuadro.item(cuadro.selection())["values"][2]
    except:
        messagebox.showinfo(message="Seleccione MP", title="Error")
    
    lista = cuadro.item(cuadro.selection())["values"]       
    lista[2]=float(nuevo_stock)          
    cuadro.item(cuadro.selection(),values=lista)  
    fecha = time.strftime("%d/%m/%y")
    hora = time.strftime("%H:%M:%S")
    respon = responsable.get()
    conexion=sqlite3.connect(entrada_ruta_bd.get())    
    
    nuevo_stock = float(nuevo_stock)
    if nuevo_stock == 0:
        conexion.execute("""UPDATE stock SET stock = ?, estado = "agotado"  WHERE mp = ? and lote = ? and deposito = ?;""",(nuevo_stock,mp,lote,deposito))
        conexion.commit()            
    else:                   
        conexion.execute("""UPDATE stock SET stock = ?,estado = "liberado" WHERE mp = ? and lote = ? and deposito = ?;""",(nuevo_stock,mp,lote,deposito))
        conexion.commit()
    conexion.execute("""insert into registro_cambios (fecha,hora,mp,lote,deposito,stockant,nuevostock,responsable, programa)
                VALUES(?,?,?,?,?,?,?,?,?);""",(fecha,hora, mp, lote,deposito,stockant,nuevo_stock,respon, "stock"))
    conexion.commit()
    conexion.close()    

    return

def busqueda_mp(le):
    for s in cuadro.get_children():
            cuadro.delete(s)    
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    if check_nulos_value.get()==False:
        a = conexion.execute("""SELECT * FROM stock where stock != ? ;""",(0,))
        b = a.fetchall()
    else:
        a = conexion.execute("""SELECT * FROM stock;""")
        b = a.fetchall() 
    for i in b:
        if combobox.get() in str(i[0]).lower():
            cuadro.insert("", tk.END, text=i[0],values=(i[2],i[5],round(float(i[3]),3),i[1],i[6]))
    conexion.close()
    return True

def busqueda_lote(letra):
    for s in cuadro.get_children():
            cuadro.delete(s)
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    if check_nulos_value.get()==False:
        a = conexion.execute("""SELECT * FROM stock where stock != ? ;""",(0,))
        b = a.fetchall()
    else:
        a = conexion.execute("""SELECT * FROM stock;""")
        b = a.fetchall() 
    for i in b:
        if combobox_lote.get() in str(i[2]).lower():
            cuadro.insert("", tk.END, text=i[0],values=(i[2],i[5],round(i[3],3),round(i[4],3),i[1],i[6]))
    conexion.close()
    return True

    
def autenticar():
    if(entrada_contraseña.get()=="nutri23"):        
        boton_act_sim["state"] = ["enable"]       
    else:
        messagebox.showinfo(message="Contraseña Incorrecta", title="Contraseña Incorrecta")

def exportar_cambios():
    ruta = entrada_ruta_registro.get()    
    with open(ruta + "/" + "reporte_cambios.csv", 'w', newline='') as f:       
        writer = csv.writer(f,delimiter=';') 
        guardar = ["Id","Fecha","Hora","mp","Lote", "Deposito","Stock Anterior","Stock sim","Nuevo Stock","Responsable","Producto","N de Batch","Cambio","Programa","Codigo Produccion","MP Nueva","Deposito Nuevo","Lote Nuevo"]
        writer.writerow(guardar)
        conexion=sqlite3.connect(entrada_ruta_bd.get())     
        a = conexion.execute("""SELECT * FROM registro_cambios ;""")
        b = a.fetchall()  
         
        for i in b:
            guardar.clear()              
            for t in i:
                guardar.append(t)
            writer.writerow(guardar)   
    
def validar_entrada(numero):
    try:
        float(numero)
        return True
    except:
        if numero == ".":
            return True
        else:
            try:
                int(numero)
                return True
            except:
                return False

ventana = Tk()
ventana.protocol("WM_DELETE_WINDOW", cerrar)
ventana.geometry("1200x700")
ventana.title("Stock")
tab_control = ttk.Notebook(ventana, width=1200, height=650)
tab_control.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_prod = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_prod.place(x=0, y=0, relheight=1, relwidth=1)

pestaña_config = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_config.place(x=0, y=0, relheight=1, relwidth=1)
tab_control.add(pestaña_prod, text="Stock")
tab_control.add(pestaña_config, text="Configuracion")
label_ruta_bd = ttk.Label(pestaña_config, text="Ruta a Base de Datos")
label_ruta_bd.place(relx=0.1, rely=0.14)
entrada_ruta_bd = ttk.Entry(pestaña_config, width=80)
entrada_ruta_bd.place(relx=0.27, rely=0.14)
boton_ruta_bd = ttk.Button(pestaña_config, text="Config. Ruta", command=lambda: selecionar_ruta("bd"))
boton_ruta_bd.place(relx=0.8, rely=0.14)
label_mp = ttk.Label(pestaña_prod, text="Materia Prima")
label_mp.place(relx=0.01, rely=0.08)
label_lote = ttk.Label(pestaña_prod, text="Lote")
label_lote.place(relx=0.01, rely=0.22)
label_deposito = ttk.Label(pestaña_prod, text="Deposito")
label_deposito.place(relx=0.01, rely=0.36)

combobox = ttk.Combobox(pestaña_prod, width=40)
combobox.place(relx=0.11, rely=0.08)
combobox.bind("<<ComboboxSelected>>", partial(buscar,"mp"))
combobox.bind("<Return>", partial(busqueda_mp))
combobox_lote = ttk.Combobox(pestaña_prod, width=40)
combobox_lote.place(relx=0.11, rely=0.22)
combobox_lote.bind("<<ComboboxSelected>>", partial(buscar,"lote"))
combobox_lote.bind("<Return>", partial(busqueda_lote))
combobox_deposito = ttk.Combobox(pestaña_prod, width=40)
combobox_deposito.place(relx=0.11, rely=0.36)
combobox_deposito.bind("<<ComboboxSelected>>", partial(buscar,"deposito"))
cuadro = ttk.Treeview(pestaña_prod, columns=("Lote","Vto","Stock", "Deposito","Estado"))
cuadro.column("#0", width=80, anchor="center")
cuadro.column("Lote", width=30, anchor="center")
cuadro.column("Vto", width=10, anchor="center")
cuadro.column("Stock", width=10, anchor="center")

cuadro.column("Deposito", width=10, anchor="center")
cuadro.column("Estado", width=10, anchor="center")

cuadro.heading("#0", text="MP")
cuadro.heading("Lote", text="Lote")
cuadro.heading("Vto", text="Vto")
cuadro.heading("Stock", text="Stock")

cuadro.heading("Deposito", text="Deposito")
cuadro.heading("Estado", text="Estado")
barra = ttk.Scrollbar(cuadro,orient=tk.VERTICAL)
check_nulos_value = tk.BooleanVar()
check_nulos = ttk.Checkbutton(pestaña_prod, text="Mostrar Stock Cero",variable=check_nulos_value)


check_nulos.place(relx=0.4, rely=0.1)
cuadro.config(yscrollcommand=barra.set)
barra.config(command=cuadro.yview)
cuadro.place(relx=0.01, rely=0.5, relwidth=0.98, relheight=0.5)
barra.pack(fill=tk.Y, side=RIGHT)

boton_exportar = ttk.Button(pestaña_prod, text="Exportar", command= exportar)
boton_exportar.place(relx=0.4, rely=0.2, relheight=0.07)
label_ruta_registro = ttk.Label(pestaña_config, text="Ruta a Carpeta de Registros")
label_ruta_registro.place(relx=0.1, rely=0.3)
entrada_ruta_registro = ttk.Entry(pestaña_config, width= 60)
entrada_ruta_registro.place(relx=0.27, rely=0.3)
configurar_ruta_registro = ttk.Button(pestaña_config,command = partial(selecionar_ruta,"registro"),text="Conf. Ruta")
configurar_ruta_registro.place(relx=0.8, rely=0.3)
boton_act = ttk.Button(pestaña_prod,text="Actualizar Stock", command= actualizar)
boton_act.place(relx=0.7, rely=0.2,relheight=0.07)
entrada_stock = ttk.Entry(pestaña_prod, width=10,validate="key",
                           validatecommand=((pestaña_prod.register(validar_entrada)), "%S"))
entrada_stock.place(relx=0.6, rely=0.22)

label_contraseña = ttk.Label(pestaña_config, text="Contraseña")
entrada_contraseña = ttk.Entry(pestaña_config, width= 30,show="*")
label_contraseña.place(relx=0.05, rely=0.01)
entrada_contraseña.place(relx=0.27, rely=0.01)
boto_autenticar = ttk.Button(pestaña_config, text="Autenticar", command=autenticar)
boto_autenticar.place(relx=0.8, rely=0.01)
label_responsable = ttk.Label(pestaña_prod, text="Responsable")
label_responsable.place(relx=0.6, rely=0.15)
responsable = ttk.Entry(pestaña_prod, width=20)
responsable.place(relx=0.68, rely=0.15)
boton_exp_cambio = ttk.Button(pestaña_prod,text="Exportar Cambios", command= exportar_cambios)
boton_exp_cambio.place(relx=0.5, rely=0.4,relheight=0.07)
leer_archivo()
leer_base()
ventana.mainloop()
