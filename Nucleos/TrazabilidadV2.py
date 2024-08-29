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
        a = conexion.execute("""SELECT nombre FROM formulas;""")         
        formula['values'] = list(a)   
        a = conexion.execute("""SELECT mp FROM mp;""")         
        mp['values'] = list(a)         
        conexion.close()      
    except:
        messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")
         
def buscar(s):   
    if s == "formula":
        try:      
            sector = cuadro2.item(cuadro2.selection())["values"][1]
            codprod = cuadro2.item(cuadro2.selection())["text"]
            if sector == "Carga_Comasa" or sector == "Carga_Cereales" or sector == "Carga_jarabe":
                sector = "registro_carga"
        except:
            messagebox.showinfo(message="Seleccione una Produccion", title="Error")
            return
        
        conexion=sqlite3.connect(entrada_ruta_bd.get())          
        
        a = conexion.execute("""SELECT * FROM %s WHERE codprod = ? ; """ %sector, (codprod,))         
        b = a.fetchall()  
        for s in cuadro.get_children():
                cuadro.delete(s)  
        if sector == "Macro_Comasa":    
            for i in b:
                kg = ""
                for u in str(i[8]):
                    if u != ".":
                        kg = kg + u  
                    else:
                        kg = kg + ","  
                cuadro.insert("", tk.END, text=i[1],
                                    values=(i[11],i[2],i[3],"-",i[4],i[6],i[7],i[5],kg,i[9],i[12],"-","-"))
            conexion.close()
            
        elif sector == "registro_carga": 
            for i in b:
                
                cuadro.insert("", tk.END, text=i[3],
                                    values=(i[6],i[1],i[2],i[4],"-","-","-","-","-","-",i[9],i[5],i[8]))
            conexion.close()
        else:
            for i in b:
                kg = ""
                for u in str(i[8]):
                    if u != ".":
                        kg = kg + u  
                    else:
                        kg = kg + ","  
                cuadro.insert("", tk.END, text=i[0],
                                    values=(i[11],i[2],i[3],i[1],i[4],i[6],i[7],i[5],kg,i[9],i[12],"-","-"))
            conexion.close()
    if s == "mp":

        try:      
            lote = cuadro_mp.item(cuadro_mp.selection())["values"][0]
            mp = cuadro_mp.item(cuadro_mp.selection())["text"]
        except:
            messagebox.showinfo(message="Seleccione una Materia Prima", title="Error")
            return
        
        conexion=sqlite3.connect(entrada_ruta_bd.get())          
        a = conexion.execute("""SELECT * FROM Macro_Cereales WHERE mp = ? and lote = ? ; """,(mp,lote))         
        b = a.fetchall()  
        a = conexion.execute("""SELECT * FROM Nucleos_Cereales WHERE mp = ? and lote = ? ; """,(mp,lote))         
        b.append(a.fetchall())
        a = conexion.execute("""SELECT * FROM Macro_Comasa WHERE mp = ? and lote = ? ; """,(mp,lote))         
        b.append(a.fetchall())
        a = conexion.execute("""SELECT * FROM Nucleos_Comasa WHERE mp = ? and lote = ? ; """,(mp,lote))         
        b.append(a.fetchall())
        a = conexion.execute("""SELECT * FROM Macro_Jarabe WHERE mp = ? and lote = ? ; """,(mp,lote))         
        b.append(a.fetchall())
        a = conexion.execute("""SELECT * FROM Nucleos_Jarabe WHERE mp = ? and lote = ? ; """,(mp,lote))         
        b.append(a.fetchall())
        conexion.close()
        for s in cuadro2_mp.get_children():
            cuadro2_mp.delete(s)  
        
        for e in b:
            if e != []:  
                for i in e:
                    kg = ""
                    for u in str(i[8]):
                        if u != ".":
                            kg = kg + u  
                        else:
                            kg = kg + ","
                    if i[10]!="Macro_Comasa":  
                                      
                        cuadro2_mp.insert("", tk.END, text=i[0],
                                        values=(i[11],i[2],i[3],i[1],i[4],i[6],i[7],i[5],kg,i[9],i[12]))
                    else:
                        
                        cuadro2_mp.insert("", tk.END, text=i[0],
                                        values=(i[11],i[2],i[3],"-",i[4],i[6],i[7],i[5],kg,i[9],i[12]))
    if s == "fecha":
        fecha = entrada_fecha.get()
        if len(fecha)==10 :
            dia = fecha[0:2]
            mes = fecha[3:5]
            año = fecha[8:10]        
            fecha = (dia) + "/" + (mes) + "/" + (año)                  
            try:            
                datetime.strptime(fecha, "%d/%m/%y")            
            except:            
                messagebox.showinfo(message="Error en Fecha", title="Error de Fecha")
                return                         
        else:
            messagebox.showinfo(message="Error en Fecha", title="Error de Fecha")
            return                         
        conexion=sqlite3.connect(entrada_ruta_bd.get())          
        a = conexion.execute("""SELECT * FROM Macro_Cereales WHERE fecha = ?; """,(fecha,))         
        b = a.fetchall()  
        a = conexion.execute("""SELECT * FROM Nucleos_Cereales WHERE fecha = ?; """,(fecha,))         
        b.append(a.fetchall())
        a = conexion.execute("""SELECT * FROM Macro_Comasa WHERE fecha = ?; """,(fecha,))         
        b.append(a.fetchall())
        a = conexion.execute("""SELECT * FROM Nucleos_Comasa WHERE fecha = ?; """,(fecha,))         
        b.append(a.fetchall())
        a = conexion.execute("""SELECT * FROM Macro_Jarabe WHERE fecha = ?; """,(fecha,))         
        b.append(a.fetchall())
        a = conexion.execute("""SELECT * FROM Nucleos_Jarabe WHERE fecha = ?; """,(fecha,))         
        b.append(a.fetchall())
        a = conexion.execute("""SELECT * FROM registro_carga WHERE fecha = ?; """,(fecha,))         
        b.append(a.fetchall())
        conexion.close()
        for s in cuadro2_fecha.get_children():
            cuadro2_fecha.delete(s)  
        
        for e in b:
            if e != []:  
                for i in e:
                    kg = ""
                    for u in str(i[8]):
                        if u != ".":
                            kg = kg + u  
                        else:
                            kg = kg + ","
                    if i[10]!="Macro_Comasa":              
                        cuadro2_fecha.insert("", tk.END, text=i[0],
                                        values=(i[11],i[2],i[3],i[1],i[4],i[6],i[7],i[5],kg,i[9],i[12]))
                        
                    else:
                        cuadro2_fecha.insert("", tk.END, text=i[0],
                                        values=(i[11],i[2],i[3],"-",i[4],i[6],i[7],i[5],kg,i[9],i[12]))

              
def exportar(s):    
    if s == "formula":        
        try:   
            ruta = entrada_ruta_registro.get()
            codprod = cuadro2.item(cuadro2.selection())["text"]             
            form = formula.get()
            with open(ruta + "/" + 'reporte' + str(form)+ str(codprod) + '.csv', 'w', newline='') as f:       
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

    if s == "mp":
        try:   
            lote = cuadro_mp.item(cuadro_mp.selection())["values"][0]    
            ruta = entrada_ruta_registro.get()
            mp1 = mp.get()
            with open(ruta + "/" + 'reporte'+ str(mp1) + str(lote) +'.csv', 'w', newline='') as f:       
                writer = csv.writer(f,delimiter=';') 
                guardar = ["Codigo de Produccion","Formula","Fecha","Hora","N° de Batch","MP","Lote","Vto","Deposito", "Cantida", "Responsable","Comentario"]
                writer.writerow(guardar)        
                for i in cuadro2_mp.get_children():
                    guardar.clear()            
                    guardar.append((cuadro2_mp.item(i)["text"]))    
                    for t in cuadro2_mp.item(i)["values"]:
                        guardar.append(t)
                    writer.writerow(guardar)    
        except:
            messagebox.showinfo(message="Error al Exportar Datos", title="Error")
    if s == "fecha":
        try:       
            ruta = entrada_ruta_registro.get()
            fecha = entrada_fecha.get()
            with open(ruta + "/" + 'reporte' +str(fecha)+ '.csv', 'w', newline='') as f:       
                writer = csv.writer(f,delimiter=';') 
                guardar = ["Codigo de Produccion","Formula","Fecha","Hora","N° de Batch","MP","Lote","Vto","Deposito", "Cantida", "Responsable","Comentario"]
                writer.writerow(guardar)        
                for i in cuadro2_fecha.get_children():
                    guardar.clear()            
                    guardar.append((cuadro2_fecha.item(i)["text"]))    
                    for t in cuadro2_fecha.item(i)["values"]:
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

def buscar_formula(f):
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    a = conexion.execute("""SELECT * FROM producciones WHERE formula = ? ;""",(formula.get(),))         
    b = a.fetchall()  
    for s in cuadro2.get_children():
            cuadro2.delete(s)   
    for i in b:
        cuadro2.insert("", tk.END, text=i[0],
                            values=(i[1],i[2],i[3],i[4]))
    conexion.close()

def buscar_mp(f):
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    a = conexion.execute("""SELECT * FROM recepcion WHERE mp = ? ;""",(mp.get(),))         
    b = a.fetchall()  
    for s in cuadro_mp.get_children():
            cuadro_mp.delete(s)   
    for i in b:
        cuadro_mp.insert("", tk.END, text=i[2],
                            values=(i[3],i[7]))
    conexion.close()

def validar_entrada(numero):        
    try:
        int(numero)
        return True
    except:
        if numero == "-":
            return True
        else:
            return False
    
ventana = Tk()
ventana.protocol("WM_DELETE_WINDOW", cerrar)
ventana.geometry("1200x600")
ventana.title("Trazabilidad")
tab_control = ttk.Notebook(ventana, width=1200, height=700)
tab_control.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_prod = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_prod.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_mp = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_mp.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_fecha = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_fecha.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_config = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_config.place(x=0, y=0, relheight=1, relwidth=1)
tab_control.add(pestaña_prod, text="Producciones")
tab_control.add(pestaña_mp, text="MP")
tab_control.add(pestaña_fecha, text="Fecha")
tab_control.add(pestaña_config, text="Configuracion")
label_ruta_bd = ttk.Label(pestaña_config, text="Ruta a Base de Datos")
label_ruta_bd.place(relx=0.1, rely=0.14)
entrada_ruta_bd = ttk.Entry(pestaña_config, width=80)
entrada_ruta_bd.place(relx=0.27, rely=0.14)
boton_ruta_bd = ttk.Button(pestaña_config, text="Config. Ruta", command = lambda: selecionar_ruta("bd"))
boton_ruta_bd.place(relx=0.8, rely=0.14)
label_formula = ttk.Label(pestaña_prod, text="Formula")
label_formula.place(relx=0.01, rely=0.01)
label_mp = ttk.Label(pestaña_mp, text="MP")
label_mp.place(relx=0.01, rely=0.01)
label_fecha = ttk.Label(pestaña_fecha, text="FECHA")
label_fecha.place(relx=0.01, rely=0.01)

formula = ttk.Combobox(pestaña_prod, width=40)
formula.place(relx=0.07, rely=0.01)
formula.bind("<<ComboboxSelected>>", partial(buscar_formula))

cuadro = ttk.Treeview(pestaña_prod, columns=("Formula","Fecha","Hora","N° de Batch","MP","Lote","Vto","Deposito","Cantidad","Responsable","Comentario","N° Nucleo","Cod_Nucleo"))
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
cuadro.column("N° Nucleo", width=30, anchor="center")
cuadro.column("Cod_Nucleo", width=30, anchor="center")
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
cuadro.heading("N° Nucleo", text="N° Nucleo")
cuadro.heading("Cod_Nucleo", text="Cod_Nucleo")

barra = ttk.Scrollbar(cuadro)
cuadro.config(yscrollcommand=barra.set)
barra.config(command=cuadro.yview)
cuadro.place(relx=0.01, rely=0.4, relwidth=0.98, relheight=0.5)
barra.place(relx=0.98, rely=0.11, relheight=0.85)

cuadro2 = ttk.Treeview(pestaña_prod, columns=("Formula","Sector","N° de Batch","Estado"))
cuadro2.column("#0", width=20, anchor="center")
cuadro2.column("Formula", width=20, anchor="center")
cuadro2.column("Sector", width=20, anchor="center")
cuadro2.column("N° de Batch", width=20, anchor="center")
cuadro2.column("Estado", width=30, anchor="center")
cuadro2.heading("#0", text="CodigoProd")
cuadro2.heading("Formula", text="Formula")
cuadro2.heading("Sector", text="Sector")
cuadro2.heading("N° de Batch", text="N° de Batch")
cuadro2.heading("Estado", text="Estado")
barra2 = ttk.Scrollbar(cuadro2)
cuadro2.config(yscrollcommand=barra2.set)
barra2.config(command=cuadro2.yview)

barra2.place(relx=0.965, rely=0.11, relheight=0.85)
cuadro2.place(relx=0.45, rely=0.01, relwidth=0.5, relheight=0.3)
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

mp = ttk.Combobox(pestaña_mp, width=40)
mp.place(relx=0.07, rely=0.01)
mp.bind("<<ComboboxSelected>>", partial(buscar_mp))

cuadro_mp = ttk.Treeview(pestaña_mp, columns=("Lote","Deposito"))
cuadro_mp.column("#0", width=20, anchor="center")
cuadro_mp.column("Lote", width=20, anchor="center")
cuadro_mp.column("Deposito", width=20, anchor="center")

cuadro_mp.heading("#0", text="MP")
cuadro_mp.heading("Lote", text="Lote")
cuadro_mp.heading("Deposito", text="Deposito")
cuadro_mp.place(relx=0.45, rely=0.01, relwidth=0.5, relheight=0.3)
barra_mp = ttk.Scrollbar(cuadro_mp)
cuadro_mp.config(yscrollcommand=barra_mp.set)
barra_mp.config(command=cuadro_mp.yview)
barra_mp.place(relx=0.965, rely=0.11, relheight=0.85)

boton_buscar = ttk.Button(pestaña_prod, text="Buscar", command=partial(buscar,"formula"))
boton_buscar.place(relx=0.3, rely=0.01, relheight=0.07)
boton_exportar = ttk.Button(pestaña_prod, text="Exportar", command=partial(exportar,"formula"))
boton_exportar.place(relx=0.3, rely=0.11, relheight=0.07)
cuadro2_mp = ttk.Treeview(pestaña_mp, columns=("Formula","Fecha","Hora","N° de Batch","MP","Lote","Vto","Deposito","Cantidad","Responsable","Comentario"))
cuadro2_mp.column("#0", width=20, anchor="center")
cuadro2_mp.column("Formula", width=20, anchor="center")
cuadro2_mp.column("Fecha", width=20, anchor="center")
cuadro2_mp.column("Hora", width=20, anchor="center")
cuadro2_mp.column("N° de Batch", width=20, anchor="center")
cuadro2_mp.column("MP", width=80, anchor="center")
cuadro2_mp.column("Lote", width=30, anchor="center")
cuadro2_mp.column("Vto", width=30, anchor="center")
cuadro2_mp.column("Deposito", width=30, anchor="center")
cuadro2_mp.column("Cantidad", width=30, anchor="center")
cuadro2_mp.column("Responsable", width=30, anchor="center")
cuadro2_mp.column("Comentario", width=30, anchor="center")
cuadro2_mp.heading("#0", text="CodigoProd")
cuadro2_mp.heading("Formula", text="Formula")
cuadro2_mp.heading("Fecha", text="Fecha")
cuadro2_mp.heading("Hora", text="Hora")
cuadro2_mp.heading("N° de Batch", text="N° de Batch")
cuadro2_mp.heading("MP", text="MP")
cuadro2_mp.heading("Lote", text="Lote")
cuadro2_mp.heading("Vto", text="Vto")
cuadro2_mp.heading("Deposito", text="Deposito")
cuadro2_mp.heading("Cantidad", text="Cantidad")
cuadro2_mp.heading("Responsable", text="Responsable")
cuadro2_mp.heading("Comentario", text="Comentario")
cuadro2_mp.place(relx=0.01, rely=0.4, relwidth=0.98, relheight=0.5)

barra2_mp = ttk.Scrollbar(cuadro2_mp)
cuadro2_mp.config(yscrollcommand=barra2_mp.set)
barra2_mp.config(command=cuadro2_mp.yview)
cuadro2_mp.place(relx=0.01, rely=0.4, relwidth=0.98, relheight=0.5)
barra2_mp.place(relx=0.98, rely=0.11, relheight=0.85)
boton_buscar_mp = ttk.Button(pestaña_mp, text="Buscar", command=partial(buscar,"mp"))
boton_buscar_mp.place(relx=0.3, rely=0.01, relheight=0.07)
boton_exportar_mp = ttk.Button(pestaña_mp, text="Exportar", command=partial(exportar,"mp"))
boton_exportar_mp.place(relx=0.3, rely=0.11, relheight=0.07)

entrada_fecha = ttk.Entry(pestaña_fecha, width=30,validate="key",
                      validatecommand=((pestaña_fecha.register(validar_entrada)), "%S"))
entrada_fecha.place(relx=0.07, rely=0.01)


boton_buscar_fecha = ttk.Button(pestaña_fecha, text="Buscar", command=partial(buscar,"fecha"))
boton_buscar_fecha.place(relx=0.3, rely=0.01, relheight=0.07)
boton_exportar_fecha = ttk.Button(pestaña_fecha, text="Exportar", command=partial(exportar,"fecha"))
boton_exportar_fecha.place(relx=0.3, rely=0.11, relheight=0.07)
cuadro2_fecha = ttk.Treeview(pestaña_fecha, columns=("Formula","Fecha","Hora","N° de Batch","MP","Lote","Vto","Deposito","Cantidad","Responsable","Comentario"))
cuadro2_fecha.column("#0", width=20, anchor="center")
cuadro2_fecha.column("Formula", width=20, anchor="center")
cuadro2_fecha.column("Fecha", width=20, anchor="center")
cuadro2_fecha.column("Hora", width=20, anchor="center")
cuadro2_fecha.column("N° de Batch", width=20, anchor="center")
cuadro2_fecha.column("MP", width=80, anchor="center")
cuadro2_fecha.column("Lote", width=30, anchor="center")
cuadro2_fecha.column("Vto", width=30, anchor="center")
cuadro2_fecha.column("Deposito", width=30, anchor="center")
cuadro2_fecha.column("Cantidad", width=30, anchor="center")
cuadro2_fecha.column("Responsable", width=30, anchor="center")
cuadro2_fecha.column("Comentario", width=30, anchor="center")
cuadro2_fecha.heading("#0", text="CodigoProd")
cuadro2_fecha.heading("Formula", text="Formula")
cuadro2_fecha.heading("Fecha", text="Fecha")
cuadro2_fecha.heading("Hora", text="Hora")
cuadro2_fecha.heading("N° de Batch", text="N° de Batch")
cuadro2_fecha.heading("MP", text="MP")
cuadro2_fecha.heading("Lote", text="Lote")
cuadro2_fecha.heading("Vto", text="Vto")
cuadro2_fecha.heading("Deposito", text="Deposito")
cuadro2_fecha.heading("Cantidad", text="Cantidad")
cuadro2_fecha.heading("Responsable", text="Responsable")
cuadro2_fecha.heading("Comentario", text="Comentario")
cuadro2_fecha.place(relx=0.01, rely=0.4, relwidth=0.98, relheight=0.5)

barra2_fecha = ttk.Scrollbar(cuadro2_fecha)
cuadro2_fecha.config(yscrollcommand=barra2_fecha.set)
barra2_fecha.config(command=cuadro2_fecha.yview)
cuadro2_fecha.place(relx=0.01, rely=0.4, relwidth=0.98, relheight=0.5)
barra2_fecha.place(relx=0.98, rely=0.11, relheight=0.85)


leer_archivo()
leer_base()
ventana.mainloop()
