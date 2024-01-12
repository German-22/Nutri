import tkinter as tk
from tkinter import *
from tkinter import ttk,messagebox, filedialog
import sqlite3
from datetime import datetime
from csv import reader, writer
from reportlab.pdfgen import canvas
from functools import partial
import Leer_archivo as la 
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

def leer_base():
    try:
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT nombre FROM formulas;""")         
        combobox['values'] = list(a)           
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

def calcular():
    global sector
    for s in cuadro.get_children():
            cuadro.delete(s)
    formula = combobox.get()
    ndebatch = int(entrada_ndebatch.get())
    mp = []
    dep = []
    
    cantidad = []
    reg = []
    dic_vto = {}
    dic_stock = {}    
    dic_lote = {}
    dic_deposito = {}
    
    
    vto = []
    stock = []
    mp_stock = []
    lote = []
    deposito = []
    lotes_agotados = []       
    dep_agotados = []
    try:
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT * FROM %s;""" %formula)         
        b = a.fetchall()
        for i in b:
            mp.append(i[0])        
            dep.append(i[1])
            cantidad.append(i[2])
            sector = (i[3])
            reg.append(i[4])
        conexion.close()        
    except:
        messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")   
    try:
        conexion=sqlite3.connect(entrada_ruta_bd.get())   
        for i in mp:   
            vto.clear()
            stock.clear()
            mp_stock.clear()
            lote.clear()
            deposito.clear()             
            a = conexion.execute("""SELECT * FROM stock WHERE mp = ? and estado = "Liberado" and stocksim > ? ORDER BY vto;""",(i,0))         
            b = a.fetchall()     
                   
            for p in b:            
                if datetime.strptime(str(p[5]), "%Y/%m/%d") > (datetime.strptime(str(datetime.now().date()),"%Y-%m-%d")):
                    vto.append(p[5])
                    stock.append(p[4])                
                    lote.append(p[2])
                    deposito.append(p[1])

            dic_vto[i] = vto[0::] 
            dic_stock[i] = stock[0::]               
            dic_lote[i] = lote[0::]     
            dic_deposito[i] = deposito[0::]         
        conexion.close()
    except:
           messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")   
    k = 0
    res =0      
    for i in dic_stock:#Recorro las MP en stock
        lotes_agotados.clear()
        dep_agotados.clear()
        n =0
        m = 0
        parcial = False
        entero = False
        #Recorro los lotes en stock   
        cant = float(dic_stock[i][m])
        conexion=sqlite3.connect(entrada_ruta_bd.get())   
        while n<ndebatch:                    
            if entero == False:                        
                cant = float(dic_stock[i][m])                             
            while cant < cantidad[k]:                              
                if len(dic_stock[i]) > m:  
                    lotes_agotados.append(dic_lote[i][m]) 
                    dep_agotados.append(dic_deposito[i][m])
                    if entero == False:         
                        cant = float(dic_stock[i][m])     
                    entero = False               
                    if parcial == False:    
                        n = n + 1                
                        res = cant - cantidad[k]                              
                        cuadro.insert("", tk.END, text=entrada_cod_produccion.get(),
                            values=(i,"",n,cant,dic_deposito[i][m],dic_lote[i][m],dic_vto[i][m]))
                        
                        conexion.execute("""insert into simulacion (codprod,formula, mp,deposito, lote, cantidad, vto, ndebatch)
                            VALUES(?,?,?,?,?,?,?,?);""",(entrada_cod_produccion.get(), combobox.get(), i,dic_deposito[i][m],dic_lote[i][m],cant,dic_vto[i][m] ,n))
                        conexion.commit() 
                        
                        parcial = True
                        m = m + 1
                    else:
                        res = cant + res
                        if res < 0:
                            cuadro.insert("", tk.END, text=entrada_cod_produccion.get(),
                            values=(i,"",n, cant,dic_deposito[i][m],dic_lote[i][m],dic_vto[i][m]))
                            conexion.execute("""insert into simulacion (codprod,formula, mp, deposito, lote, cantidad, vto, ndebatch)
                            VALUES(?,?,?,?,?,?,?,?);""",(entrada_cod_produccion.get(), combobox.get(), i,dic_deposito[i][m],dic_lote[i][m],cant,dic_vto[i][m] ,n))
                            conexion.commit() 
                            m = m + 1
                        else:
                            cuadro.insert("", tk.END, text=entrada_cod_produccion.get(),
                            values=(i,"",n,-(res-cant),dic_deposito[i][m],dic_lote[i][m],dic_vto[i][m]))
                            conexion.execute("""insert into simulacion (codprod,formula, mp, deposito, lote, cantidad, vto, ndebatch)
                            VALUES(?,?,?,?,?,?,?,?);""",(entrada_cod_produccion.get(), combobox.get(), i,dic_deposito[i][m],dic_lote[i][m],-(res-cant),dic_vto[i][m] ,n))
                            conexion.commit() 
                            cant = res
                            if cant == 0:
                                m = m + 1
                            else:
                                parcial = False
                                entero = True                 
                else:
                    cant = cantidad[k]
                    messagebox.showinfo(message="No Hay suficiente stock de" , title="Stock Insuficiente")
                    n = ndebatch
                    dic_res_stock[i] = [lotes_agotados[0::],dep_agotados[0::]]

            if len (dic_stock[i])>m:
                entero = True
                if parcial == True:
                    cuadro.insert("", tk.END, text=entrada_cod_produccion.get(),
                        values=(i,"",n,-res,dic_deposito[i][m],dic_lote[i][m],dic_vto[i][m]))
                    conexion.execute("""insert into simulacion (codprod,formula, mp, deposito,lote, cantidad, vto, ndebatch)
                            VALUES(?,?,?,?,?,?,?,?);""",(entrada_cod_produccion.get(), combobox.get(), i,dic_deposito[i][m],dic_lote[i][m],-res,dic_vto[i][m] ,n))
                    conexion.commit() 
                else:
                    n = n + 1
                    cuadro.insert("", tk.END, text=entrada_cod_produccion.get(),
                        values=(i,"",n,cantidad[k],dic_deposito[i][m],dic_lote[i][m],dic_vto[i][m]))
                    conexion.execute("""insert into simulacion (codprod,formula, mp, deposito, lote, cantidad, vto, ndebatch)
                            VALUES(?,?,?,?,?,?,?,?);""",(entrada_cod_produccion.get(), combobox.get(), i,dic_deposito[i][m],dic_lote[i][m],cantidad[k],dic_vto[i][m] ,n))
                    conexion.commit() 
                    cant = cant - cantidad[k]
        k = k + 1               
    conexion.close()      

def nuevo():
    global sector       
    codprod = entrada_cod_produccion.get()
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    conexion.execute("""insert into producciones (codprod,formula,sector,ndebatch,estado)
        VALUES(?,?,?,?,?);""",(codprod, combobox.get(), sector, entrada_ndebatch.get(),"programado"))
    conexion.commit() 
    a = conexion.execute("""SELECT * FROM simulacion WHERE codprod = ? ;""",(entrada_cod_produccion.get(),))         
    b = a.fetchall()  
    for i in b:  
        r = conexion.execute("""SELECT * FROM stock WHERE mp = ? and lote = ? and deposito = ? ;""",(i[3],i[5],i[4]))         
        f = r.fetchall()
                 
        conexion.execute("""UPDATE stock SET stocksim = ? WHERE mp = ? and lote = ? and deposito = ?;""",(f[0][4]-i[6],f[0][0],f[0][2],f[0][1]))
        conexion.commit() 
            
    conexion.close()      
      
def buscar():
    for s in cuadro.get_children():
            cuadro.delete(s)
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    a = conexion.execute("""SELECT * FROM simulacion;""")         
    b = a.fetchall()  
    for i in b:
        cuadro.insert("", tk.END, text=i[1],
                            values=(i[3],i[2],i[8],i[6],i[4],i[5],i[7]))

def eliminar():
    codprod = cuadro.item(cuadro.selection())["text"]   
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    conexion.execute("""DELETE FROM producciones WHERE codprod = ?;""", (codprod,))
    conexion.commit()
    a = conexion.execute("""SELECT * FROM simulacion WHERE codprod = ?;""",(codprod,))         
    b = a.fetchall()  
          
    for i in b:
        r = conexion.execute("""SELECT * FROM stock WHERE mp = ? and lote = ? and deposito = ?  and estado = "Liberado";""", (i[3],i[5],i[4]))         
        f = r.fetchall()    
    
        conexion.execute("""UPDATE stock SET stocksim = ? WHERE mp = ? and lote = ? and deposito = ?;""",(f[0][4]+i[6],i[3],i[5],i[4]))
        conexion.commit()
    conexion.execute("""DELETE FROM simulacion WHERE codprod = ?;""", (codprod,))
    conexion.commit()
    conexion.close()
    
    buscar()
    
def cerrar():
    ventana.destroy
    sys.exit()

ventana = Tk()
ventana.protocol("WM_DELETE_WINDOW", cerrar)
ventana.geometry("1400x650")
ventana.title("Produccion")
tab_control = ttk.Notebook(ventana, width=1000, height=650)
tab_control.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_prod = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_prod.place(x=0, y=0, relheight=1, relwidth=1)

pestaña_config = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_config.place(x=0, y=0, relheight=1, relwidth=1)
tab_control.add(pestaña_prod, text="Produccion")
tab_control.add(pestaña_config, text="Configuracion")
label_ruta_bd = ttk.Label(pestaña_config, text="Ruta al Archivo de Lotes             ")
entrada_ruta_bd = ttk.Entry(pestaña_config, width=80)
entrada_ruta_bd.place(relx=0.27, rely=0.14)
boton_ruta_bd = ttk.Button(pestaña_config, text="Config. Ruta", command=lambda: selecionar_ruta("lote"))
boton_ruta_bd.place(relx=0.8, rely=0.14)
label_codigo = ttk.Label(pestaña_prod, text="Codigo de Produccion")
label_codigo.place(relx=0.01, y=10)
label_formula = ttk.Label(pestaña_prod, text="Seleccionar Formula")
label_formula.place(relx=0.3, y=10)

label_ndebatch = ttk.Label(pestaña_prod, text="N° de Batch")
label_ndebatch.place(relx=0.75, y=10)
entrada_cod_produccion = ttk.Entry(pestaña_prod, width=20)
entrada_cod_produccion.place(relx=0.11, y=10)
combobox = ttk.Combobox(pestaña_prod, width=40)
combobox.place(relx=0.45, y=10)

entrada_ndebatch= ttk.Entry(pestaña_prod, width=10)
entrada_ndebatch.place(relx=0.81, y=10)

cuadro = ttk.Treeview(pestaña_prod, columns=("MP","Formula","N° de Batch","Cantidad", "Deposito", "Lote", "Vto","Estado"))
barra = ttk.Scrollbar(cuadro)
cuadro.column("#0", width=20, anchor="center")
cuadro.column("MP", width=80, anchor="center")
cuadro.column("Formula", width=80, anchor="center")
cuadro.column("N° de Batch", width=10, anchor="center")
cuadro.column("Cantidad", width=20, anchor="center")
cuadro.column("Deposito", width=10, anchor="center")
cuadro.column("Lote", width=40, anchor="center")
cuadro.column("Vto", width=20, anchor="center")
cuadro.column("Estado", width=20, anchor="center")
cuadro.heading("#0", text="Codigo de Produccion")
cuadro.heading("MP", text="MP")
cuadro.heading("Formula", text="Formula")
cuadro.heading("N° de Batch", text="N° de Batch")
cuadro.heading("Cantidad", text="Cantidad")
cuadro.heading("Deposito", text="Deposito")
cuadro.heading("Lote", text="Lote")
cuadro.heading("Vto", text="Vto")
cuadro.heading("Estado", text="Estado")
cuadro.config(yscrollcommand=barra.set)
barra.config(command=cuadro.yview)
cuadro.place(relx=0.01, rely=0.3, relwidth=0.98, relheight=0.6)
barra.place(relx=0.98, rely=0.1, relheight=0.85)
boton_calcular = ttk.Button(pestaña_prod, text="Calcular", command = calcular)
boton_calcular.place(relx=0.2, rely=0.15)
boton_nuevo = ttk.Button(pestaña_prod, text="Nuevo", command = nuevo)
boton_nuevo.place(relx=0.4, rely=0.15)
boton_buscar = ttk.Button(pestaña_prod, text="Buscar", command= buscar)
boton_buscar.place(relx=0.6, rely=0.15)
boton_eliminar = ttk.Button(pestaña_prod, text="Eliminar", command=eliminar)
boton_eliminar.place(relx=0.8, rely=0.15)

leer_archivo()
leer_base()
ventana.mainloop()
