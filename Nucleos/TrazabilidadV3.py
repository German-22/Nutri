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
opciones_formula = []
opciones_mp = []
opciones_formulapt = []

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
    global  opciones_formula, opciones_formulapt
    global  opciones_mp
    try:
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT nombre FROM formulas;""")                
        opciones_formula =  a.fetchall()         
        formula['values'] = opciones_formula        
        a = conexion.execute("""SELECT mp FROM mp;""")  
        opciones_mp =  a.fetchall()        
        mp['values'] = opciones_mp  
        a = conexion.execute("""SELECT nombre from formulas where (sector = ? or sector = ? or nombre = ? or nombre = ?) ORDER BY nombre;""",("Nucleos_Comasa","Nucleos_Cereales","Leche_en_Polvo_Abanderadox800g","Pellet_Maiz_y_Arroz_PMI"))               
        opciones_formulapt =  a.fetchall()         
        formula_pt['values'] = opciones_formulapt     
        formula_pl['values'] = opciones_formulapt    
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
        b = []
        conexion=sqlite3.connect(entrada_ruta_bd.get())          
        a = conexion.execute("""SELECT * FROM Macro_Cereales WHERE mp = ? and lote = ? ; """,(mp,lote))         
        c = a.fetchall()  
        b.append(c)
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
        
        for i in b:                       
            if i != []:        
                             
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
    if s == "pt":
        try:      
            producto = tree2.item(tree2.selection())["values"][1]
            lote = tree2.item(tree2.selection())["values"][2]

            if producto == "":       
                messagebox.showinfo(message="Seleccione una Produccion", title="Error")
                return
        
            conexion=sqlite3.connect(entrada_ruta_bd.get())          
            
            a = conexion.execute("""SELECT fecha,producto,pallet,cantidad,lote,destino,remito,oc,chofer,estado_trans,patente,comentario,responsable,transporte FROM planillas WHERE producto = ? and lote =?; """, (producto,lote))         
            b = a.fetchall()  
            for s in tree.get_children():
                    tree.delete(s)  
            for i in b:
                tree.insert("", tk.END, values=i)
            conexion.close()
        except:
            messagebox.showinfo(message="Error en Busqueda", title="Error")
            conexion.close()   
    if s == "formula2":
        cod = tree2.item(tree2.selection())["values"][0]
        
        if cod == "":
            messagebox.showinfo(message="Seleccione una Produccion", title="Error")
            return
        b = []
        conexion=sqlite3.connect(entrada_ruta_bd.get())          
        a = conexion.execute("""SELECT * FROM Macro_Cereales WHERE codprod = ? ; """,(cod,))         
        c = a.fetchall()  
        b.append(c)
        a = conexion.execute("""SELECT * FROM Nucleos_Cereales WHERE codprod = ? ; """,(cod,))         
        b.append(a.fetchall())
        
        a = conexion.execute("""SELECT * FROM Macro_Comasa WHERE codprod = ? ; """,(cod,))         
        b.append(a.fetchall())
        
        a = conexion.execute("""SELECT * FROM Nucleos_Comasa WHERE codprod = ? ; """,(cod,))         
        b.append(a.fetchall())
      
        a = conexion.execute("""SELECT * FROM Macro_Jarabe WHERE codprod = ? ; """,(cod,))         
        b.append(a.fetchall())
       
        a = conexion.execute("""SELECT * FROM Nucleos_Jarabe WHERE codprod = ? ; """,(cod,))         
        b.append(a.fetchall())
        
        conexion.close()
        for s in tree3.get_children():
            tree3.delete(s)  
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
                        tree3.insert("", tk.END,
                                        values=(i[0],i[11],i[2],i[3],i[1],i[4],i[6],i[7],i[5],kg,i[9],i[12],i[10]))
                    else:                        
                        tree3.insert("", tk.END,
                                        values=(i[0],i[11],i[2],i[3],"-",i[4],i[6],i[7],i[5],kg,i[9],i[12],i[10]))
    if s == "pl":
        formula = tree2l.item(tree2l.selection())["values"][1]
        lote = tree2l.item(tree2l.selection())["values"][2]
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT hora,producto,pallet,cantidadorg,lote,vto,comentario,responsable,envasadora FROM despacho WHERE producto = ? and lote = ?;""",(formula,lote))         
        b = a.fetchall()  
        for s in treel.get_children():
                treel.delete(s)   
        for i in b:
            treel.insert("", tk.END, values=i)
        a = conexion.execute("""SELECT SUM(cantidad) FROM despacho WHERE producto = ? and lote = ? group by producto,lote;""",(formula,lote))         
        b = a.fetchall()
        entrada_total.delete("0", "end")  
        entrada_total.insert(0,b)   
        conexion.close()
    
def exportar(s):    
    if s == "formula":        
        try:   
            ruta = entrada_ruta_registro.get()                    
            form = formula.get()            
            with open(ruta + "/" + 'reporte' + str(form) + '.csv', 'w', newline='') as f:       
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
    if s == "formula2":        
        try:   
            ruta = entrada_ruta_registro.get()                    
            form = formula.get()            
            with open(ruta + "/" + 'reporte' + str(form) + '.csv', 'w', newline='') as f:       
                writer = csv.writer(f,delimiter=';') 
                guardar = ["CodProd","Formula","Fecha","Hora","N° de Batch","MP","Lote","Vto","Deposito","Cantidad","Responsable","Comentario","Sector"]
                writer.writerow(guardar)        
                for i in tree3.get_children():
                    guardar.clear()                     
                    for t in tree3.item(i)["values"]:
                        guardar.append(t)
                    writer.writerow(guardar)    
        except:
            messagebox.showinfo(message="Error al Exportar Datos", title="Error")
    if s == "pl":
        try:   
            ruta = entrada_ruta_registro.get()                    
            form = formula.get()            
            with open(ruta + "/" + 'reporte' + str(form) + '.csv', 'w', newline='') as f:       
                writer = csv.writer(f,delimiter=';') 
                guardar = ["Fecha","Producto","Pallet","Cantidad","Lote","Vto","Comentario","Responsable","Envasadora"]
                writer.writerow(guardar)        
                for i in treel.get_children():
                    guardar.clear()                     
                    for t in treel.item(i)["values"]:
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

def buscar_pt(f,s):
    if f == "pt":
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT DISTINCT codprod,producto,lote FROM despacho WHERE producto = ? ;""",(formula_pt.get(),))         
        b = a.fetchall()  
        for s in tree2.get_children():
                tree2.delete(s)   
        for i in b:
            tree2.insert("", tk.END,values=(i[0],i[1],i[2]))
        conexion.close()
    if f == "pl":
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT DISTINCT codprod,producto,lote FROM despacho WHERE producto = ? ;""",(formula_pl.get(),))         
        b = a.fetchall()  
        for s in tree2l.get_children():
                tree2l.delete(s)   
        for i in b:
            tree2l.insert("", tk.END,values=(i[0],i[1],i[2]))
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

def filtrar_opciones(formula,opciones,s):    
    if opciones == "mp":
        opcion = opciones_mp
        ent = combo_var6.get()
        entrada = combo_var6.get().lower()
    elif opciones == "formula":
        opcion = opciones_formula
        entrada = combo_var.get().lower()
        ent = combo_var.get()
    elif opciones == "pl":
        opcion = opciones_formulapt
        entrada = combo_var4.get().lower()
        ent = combo_var4.get()
    elif opciones == "pt":
        opcion = opciones_formulapt
        entrada = combo_var2.get().lower()
        ent = combo_var2.get()
    
        
    # Filtrar opciones que contengan el texto
    filtradas = [op for op in opcion if entrada in op[0].lower()]
    
    # Guardar posición del cursor y texto actual
    cursor_pos = formula.index(tk.INSERT)
    
    # Actualizar valores del Combobox
    formula['values'] = filtradas if filtradas else opcion
    
    # Restaurar el texto y la posición del cursor
    formula.delete(0, tk.END)
    formula.insert(0, ent)
    formula.icursor(cursor_pos)
    
    # Autocompletar si hay una sola opción
    if len(filtradas) == 1:
        formula.delete(0, tk.END)
        formula.insert(0, filtradas[0])
        formula.icursor(tk.END)

    # Mostrar menú desplegable
    formula.event_generate('<Down>')    

ventana = Tk()
ventana.protocol("WM_DELETE_WINDOW", cerrar)
ventana.geometry("1200x800")
ventana.title("Trazabilidad")
tab_control = ttk.Notebook(ventana, width=1200, height=800)
tab_control.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_prod = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_prod.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_mp = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_mp.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_fecha = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_fecha.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_pt = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_pt.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_pl= ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_pl.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_config = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_config.place(x=0, y=0, relheight=1, relwidth=1)
tab_control.add(pestaña_prod, text="Producciones")
tab_control.add(pestaña_mp, text="MP")
tab_control.add(pestaña_fecha, text="Fecha")
tab_control.add(pestaña_pt, text="Despachos")
tab_control.add(pestaña_pl, text="Planilla")
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
combo_var = tk.StringVar()

formula = ttk.Combobox(pestaña_prod, width=40,textvariable=combo_var)
formula.place(relx=0.07, rely=0.01)
formula.bind("<<ComboboxSelected>>", partial(buscar_formula))
formula.bind('<Return>', partial(filtrar_opciones,formula,"formula"))


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


label_ruta_registro = ttk.Label(pestaña_config, text="Ruta a Carpeta de Registros")
label_ruta_registro.place(relx=0.1, rely=0.3)
entrada_ruta_registro = ttk.Entry(pestaña_config, width= 60)
entrada_ruta_registro.place(relx=0.27, rely=0.3)
configurar_ruta_registro = ttk.Button(pestaña_config,command = partial(selecionar_ruta,"registro"),text="Conf. Ruta")
configurar_ruta_registro.place(relx=0.8, rely=0.3)
combo_var6=tk.StringVar()

mp = ttk.Combobox(pestaña_mp, width=40,textvariable=combo_var6)
mp.place(relx=0.07, rely=0.01)
mp.bind("<<ComboboxSelected>>", partial(buscar_mp))
mp.bind('<Return>', partial(filtrar_opciones,mp,"mp"))

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

label_formula_pt = ttk.Label(pestaña_pt, text="Formula")
label_formula_pt.place(relx=0.01, rely=0.01)
combo_var2 = tk.StringVar()
formula_pt = ttk.Combobox(pestaña_pt, width=40,textvariable=combo_var2)
formula_pt.place(relx=0.07, rely=0.01)
formula_pt.bind("<<ComboboxSelected>>", partial(buscar_pt,"pt"))
formula_pt.bind('<Return>', partial(filtrar_opciones,formula_pt,"pt"))




contenedor_tree = ttk.Frame(pestaña_pt)
contenedor_tree.place(relx=0.01, rely=0.25, relwidth=0.85, relheight=0.35)  # Ajusta si es necesario
ttk.Label(contenedor_tree, text="Despachos:").place(relx=0,rely=0)
# Scrollbars
scrollbar_y = ttk.Scrollbar(contenedor_tree, orient="vertical")
scrollbar_x = ttk.Scrollbar(contenedor_tree, orient="horizontal")

# Treeview con scrollbars
tree = ttk.Treeview(
    contenedor_tree,
    columns=("Fecha","Producto","Pallet","Cantidad","Lote","Destino","Remito","OC","Chofer","Estado Transporte","Patente","Comentario","Responsable","Transporte"), show='headings', 
    yscrollcommand=scrollbar_y.set,
    xscrollcommand=scrollbar_x.set,
    height=10
)

scrollbar_y.config(command=tree.yview)
scrollbar_x.config(command=tree.xview)
for col in tree["columns"]:
    tree.heading(col, text=col)
    if col == "id":
        tree.column(col, width=0, stretch=False)  
    else:
        tree.column(col, anchor="center", width=100)

# Empaquetar widgets
tree.place(relx=0,rely=0.08, relheight=0.85,relwidth=0.96)
scrollbar_y.place(relx=0.95,rely=0.08, relheight=0.85,relwidth=0.05)
scrollbar_x.place(relx=0,rely=0.9, relheight=0.1,relwidth=0.98)



contenedor_tree3 = ttk.Frame(pestaña_pt)
contenedor_tree3.place(relx=0.01, rely=0.6, relwidth=0.85, relheight=0.35)  # Ajusta si es necesario
ttk.Label(contenedor_tree3, text="Materia Prima:").place(relx=0,rely=0)
# Scrollbars
scrollbar_y = ttk.Scrollbar(contenedor_tree3, orient="vertical")
scrollbar_x = ttk.Scrollbar(contenedor_tree3, orient="horizontal")

# Treeview con scrollbars
tree3 = ttk.Treeview(
    contenedor_tree3,
    columns=("CodProd","Formula","Fecha","Hora","N° de Batch","MP","Lote","Vto","Deposito","Cantidad","Responsable","Comentario","Sector"), show='headings', 
    yscrollcommand=scrollbar_y.set,
    xscrollcommand=scrollbar_x.set,
    height=10
)

scrollbar_y.config(command=tree3.yview)
scrollbar_x.config(command=tree3.xview)
for col in tree3["columns"]:
    tree3.heading(col, text=col)
    if col == "CodProd":
        tree3.column(col, width=0, stretch=False)  
    else:
        tree3.column(col, anchor="center", width=100)

# Empaquetar widgets
tree3.place(relx=0,rely=0.08, relheight=0.85,relwidth=0.96)
scrollbar_y.place(relx=0.95,rely=0.08, relheight=0.85,relwidth=0.05)
scrollbar_x.place(relx=0,rely=0.9, relheight=0.1,relwidth=0.98)


contenedor_tree2 = ttk.Frame(pestaña_pt)
contenedor_tree2.place(relx=0.45, rely=0, relwidth=0.5, relheight=0.25)  # Ajusta si es necesario

# Scrollbars
scrollbar_y = ttk.Scrollbar(contenedor_tree2, orient="vertical")
scrollbar_x = ttk.Scrollbar(contenedor_tree2, orient="horizontal")

# Treeview con scrollbars
tree2 = ttk.Treeview(
    contenedor_tree2,
    columns=("CodigoProd","Formula","Lote"), show='headings', 
    yscrollcommand=scrollbar_y.set,
    xscrollcommand=scrollbar_x.set,
    height=10
)

scrollbar_y.config(command=tree2.yview)
scrollbar_x.config(command=tree2.xview)
for col in tree2["columns"]:
    tree2.heading(col, text=col)
    tree2.column(col, anchor="center", width=100)

# Empaquetar widgets
tree2.place(relx=0,rely=0.08, relheight=0.85,relwidth=0.96)
scrollbar_y.place(relx=0.95,rely=0.08, relheight=0.85,relwidth=0.05)
scrollbar_x.place(relx=0,rely=0.9, relheight=0.1,relwidth=0.98)

boton_buscar_pt = ttk.Button(pestaña_pt, text="Buscar", command=partial(buscar,"pt"))
boton_buscar_pt.place(relx=0.87, rely=0.35, relheight=0.07)
boton_exportar_pt = ttk.Button(pestaña_pt, text="Exportar", command=partial(exportar,"pt"))
boton_exportar_pt.place(relx=0.87, rely=0.45, relheight=0.07)

boton_buscar_pt_mp = ttk.Button(pestaña_pt, text="Buscar", command=partial(buscar,"formula2"))
boton_buscar_pt_mp.place(relx=0.87, rely=0.7, relheight=0.07)
boton_exportar_pt_mp = ttk.Button(pestaña_pt, text="Exportar", command=partial(exportar,"formula2"))
boton_exportar_pt_mp.place(relx=0.87, rely=0.8, relheight=0.07)


#todo esto es para buscar las planillas
#############################################
#############################################
#############################################

ttk.Label(pestaña_pl, text="Formula").place(relx=0.01, rely=0.01)
combo_var4 = tk.StringVar()
formula_pl = ttk.Combobox(pestaña_pl, width=40,textvariable=combo_var4)
formula_pl.place(relx=0.07, rely=0.01)
formula_pl.bind("<<ComboboxSelected>>", partial(buscar_pt,"pl"))
formula_pl.bind('<Return>', partial(filtrar_opciones,formula_pl,"pl"))
ttk.Label(pestaña_pl, text="Total de Cajas:").place(relx=0.05,rely=0.2)
entrada_total = ttk.Entry(pestaña_pl, width=15)
entrada_total.place(relx=0.12, rely=0.2)
contenedor_treel = ttk.Frame(pestaña_pl)
contenedor_treel.place(relx=0.01, rely=0.25, relwidth=0.85, relheight=0.7)  # Ajusta si es necesario

# Scrollbars
scrollbar_y = ttk.Scrollbar(contenedor_treel, orient="vertical")
scrollbar_x = ttk.Scrollbar(contenedor_treel, orient="horizontal")

# Treeview con scrollbars
treel = ttk.Treeview(
    contenedor_treel,
    columns=("Fecha","Producto","Pallet","Cantidad","Lote","Vto","Comentario","Responsable","Envasadora"), show='headings', 
    yscrollcommand=scrollbar_y.set,
    xscrollcommand=scrollbar_x.set,
    height=10
)

scrollbar_y.config(command=treel.yview)
scrollbar_x.config(command=treel.xview)
for col in treel["columns"]:
    treel.heading(col, text=col)
    if col == "id":
        treel.column(col, width=0, stretch=False)  
    else:
        treel.column(col, anchor="center", width=100)

# Empaquetar widgets
treel.place(relx=0,rely=0.08, relheight=0.85,relwidth=0.96)
scrollbar_y.place(relx=0.95,rely=0.08, relheight=0.85,relwidth=0.05)
scrollbar_x.place(relx=0,rely=0.9, relheight=0.1,relwidth=0.98)

contenedor_tree2l = ttk.Frame(pestaña_pl)
contenedor_tree2l.place(relx=0.45, rely=0, relwidth=0.5, relheight=0.25)  # Ajusta si es necesario

# Scrollbars
scrollbar_y = ttk.Scrollbar(contenedor_tree2l, orient="vertical")
scrollbar_x = ttk.Scrollbar(contenedor_tree2l, orient="horizontal")

# Treeview con scrollbars
tree2l = ttk.Treeview(
    contenedor_tree2l,
    columns=("CodigoProd","Formula","Lote"), show='headings', 
    yscrollcommand=scrollbar_y.set,
    xscrollcommand=scrollbar_x.set,
    height=10
)

scrollbar_y.config(command=tree2l.yview)
scrollbar_x.config(command=tree2l.xview)
for col in tree2l["columns"]:
    tree2l.heading(col, text=col)
    tree2l.column(col, anchor="center", width=100)

# Empaquetar widgets
tree2l.place(relx=0,rely=0.08, relheight=0.85,relwidth=0.96)
scrollbar_y.place(relx=0.95,rely=0.08, relheight=0.85,relwidth=0.05)
scrollbar_x.place(relx=0,rely=0.9, relheight=0.1,relwidth=0.98)

boton_buscar_ptl = ttk.Button(pestaña_pl, text="Buscar", command=partial(buscar,"pl"))
boton_buscar_ptl.place(relx=0.87, rely=0.35, relheight=0.07)
boton_exportar_ptl = ttk.Button(pestaña_pl, text="Exportar", command=partial(exportar,"pl"))
boton_exportar_ptl.place(relx=0.87, rely=0.45, relheight=0.07)


leer_archivo()
leer_base()
ventana.mainloop()
