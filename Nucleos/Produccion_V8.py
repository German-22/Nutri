import tkinter as tk
from tkinter import *
from tkinter import ttk,messagebox, filedialog
import sqlite3
from datetime import datetime
from csv import reader, writer
#from reportlab.pdfgen import canvas
from functools import partial
import Leer_archivo as la 
ruta_txt = "/archnucl"
import sys
import time
import csv
sector = ""

dic_res_stock = {}
opciones_formula = []
opciones_mp = []
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
    global  opciones_formula
    global  opciones_mp
    
    try:
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT nombre FROM formulas;""")   
        opciones_formula =  a.fetchall()       
        combobox['values'] = opciones_formula          
        a = conexion.execute("""SELECT nombre FROM formulas WHERE sector = "Nucleos_Cereales" or sector = "Nucleos_Comasa" or sector = "Nucleos_Jarabe" ;""")         
        combobox_carga['values'] = list(a)                        
        conexion.close() 
        buscar("nucleos")       
    except:
        messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")
    
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


def calcular(x):    
    correcto = True 
    formula = str(combobox.get())   
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    a = conexion.execute("""SELECT sector FROM formulas WHERE nombre = ?;""",(formula,))         
    sector_for = a.fetchall()[0][0]        
    global sector    
    for s in cuadro.get_children():
            cuadro.delete(s)    
    if str(combobox.get()) == "" or entrada_ndebatch.get() == "" or entrada_cod_produccion.get() == "":
        messagebox.showinfo(message="COMPLETE LOS CAMPOS", title="Error")
        return   
    ndebatch = float(entrada_ndebatch.get())

    mp = []
    dep = []    
    cantidad = []
    reg = []
    dic_vto = {}
    dic_stock = {}    
    dic_lote = {}
    dic_deposito = {}       
    dic_calculo = {}
    vto = []
    stock = []
    mp_stock = []
    lote = []
    deposito = []
  
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
        conexion.close()   
        messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")   
    try:
        conexion=sqlite3.connect(entrada_ruta_bd.get())   
        for i in mp:   #Para cada materia prima de la formula busco que lotes hay en stock.
            vto.clear()
            stock.clear()
            mp_stock.clear()
            lote.clear()
            deposito.clear()             
            a = conexion.execute("""SELECT * FROM stock WHERE mp = ? and estado = "liberado" and stock > ? ORDER BY vto;""",(i,0.0001))         
            b = a.fetchall()                              
            for p in b:        
                    
                if datetime.strptime(str(p[5]), "%Y-%m-%d") > (datetime.strptime(str(datetime.now().date()),"%Y-%m-%d")):
                    vto.append(p[5])
                    stock.append(round(p[3],3))                
                    lote.append(p[2])
                    deposito.append(p[1])
            dic_vto[i] = vto[0::] 
            dic_stock[i] = stock[0::]               
            dic_lote[i] = lote[0::]     
            dic_deposito[i] = deposito[0::]         
        conexion.close()
    except:
           conexion.close()   
           messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")   
   
    try:     
        k = 0
                        
        for i in dic_stock:#Recorro las MP en stock   
            m = 0                    
            if dic_stock[i]==[]:
                messagebox.showinfo(message="No Hay stock de" + " " + i , title="Stock Insuficiente") 
                k += 1
                correcto = False
                continue            
                                       
            cant = float(dic_stock[i][m])
            cant_usar = round(cantidad[k] * ndebatch,3)                    
            while cant - cant_usar < 0:                                                                     
                if len(dic_deposito[i])>m:                                           
                    dic_calculo[dic_lote[i][m]] = [entrada_cod_produccion.get(),round(cant,3),i,formula,dic_deposito[i][m],dic_lote[i][m],dic_vto[i][m]]
                    m = m + 1                                   
                    cant_usar = cant_usar - cant                
                    if len(dic_deposito[i])<=m:
                        messagebox.showinfo(message="No Hay stock de" + " " + i , title="Stock Insuficiente")
                        correcto = False
                        
                        break
                    cant = float(dic_stock[i][m])
                else:
                    messagebox.showinfo(message="No Hay stock de" + " " + i , title="Stock Insuficiente")
                    correcto = False
                    
                    break  
            if len(dic_deposito[i])>m:
                dic_calculo[dic_lote[i][m]] = [entrada_cod_produccion.get(),round(cant_usar,3),i,formula,dic_deposito[i][m],dic_lote[i][m],dic_vto[i][m]]
            m = m + 1   
            k = k + 1
                                 
    except:           
           messagebox.showinfo(message="Error de calculo", title="Error de Conexion")
           conexion.close()        
    if correcto == True:
        messagebox.showinfo(message="Hay Stock de todas Las MP", title="")  
    return

def nuevo(sec):     
    fecha = time.strftime("%d/%m/%y")
    hora = time.strftime("%H:%M:%S")
    respon = responsable.get()       
    if respon == "":
        messagebox.showinfo(message="Ingrese Responsable", title="Error")
        return
    
    if  sec == "nucleos":        
        codprod = entrada_cod_produccion.get()        
        ndebatch = entrada_ndebatch.get()
        formula = combobox.get()

        if codprod == "" or ndebatch=="":
            messagebox.showinfo(message="Complete los Campos", title="Error")
            return
        conexion=sqlite3.connect(entrada_ruta_bd.get())   
        e = conexion.execute("""SELECT sector FROM formulas WHERE nombre = ?;""",(formula,))        
        sector = e.fetchall()[0][0]           
        e = conexion.execute("""SELECT ndebatch FROM producciones WHERE codprod = ?;""",(codprod,))
        f = e.fetchall()    
        if f == []:
            
            conexion.execute("""insert into producciones (codprod,formula,sector,ndebatch,estado)
                VALUES(?,?,?,?,?);""",(codprod, formula, sector, entrada_ndebatch.get(),"programado"))
            conexion.commit() 
        else:
            
            conexion.execute("""UPDATE producciones set ndebatch = ? WHERE codprod = ?;""",(float(f[0][0])+ float(entrada_ndebatch.get()), codprod))
            conexion.commit()      
        conexion.close()
        buscar("nucleos")


    if sec == "carga":
        codprod = entrada_cod_prod_car.get()
        formula = combobox_carga.get()
        sector = combobox_sector.get()
        if codprod == "" or formula =="" or sector=="":
            messagebox.showinfo(message="Complete los Campos", title="Error")
            return
        conexion=sqlite3.connect(entrada_ruta_bd.get())        
        a = conexion.execute("""SELECT ndebatch FROM producciones WHERE codprod = ?;""",(codprod,))
        b = a.fetchall()        
        if b == []:            
            conexion.execute("""insert into producciones (codprod,formula,sector,ndebatch,estado)
                VALUES(?,?,?,?,?);""",(codprod, formula, sector, entrada_ndebatch_carga.get(),"programado"))
            conexion.commit() 
        else:            
            conexion.execute("""UPDATE producciones set ndebatch = ? WHERE codprod = ?;""",(int(b[0][0])+ int(entrada_ndebatch_carga.get()), codprod))
            conexion.commit()             
        conexion.close()      
        buscar("carga")
    conexion=sqlite3.connect(entrada_ruta_bd.get()) 
    conexion.execute("""insert into registro_cambios (fecha,hora,responsable, producto, ndeb, accion, programa, codprod)
                    VALUES(?,?,?,?,?,?,?,?);""",(fecha,hora,respon,formula, ndebatch, "Programar", "Produccion",codprod))
    conexion.commit()
    conexion.close()

def buscar(sec):       
    if sec == "nucleos":        
        for s in cuadro.get_children():
                cuadro.delete(s)
        conexion=sqlite3.connect(entrada_ruta_bd.get())                           
        a = conexion.execute("""SELECT * FROM producciones WHERE estado != "finalizado";""")         
        b = a.fetchall()             
        for i in b:
            cuadro.insert("", tk.END, text=i[0],
                                values=(i[1],i[3]))
        conexion.close()
    if sec == "carga":
        for s in cuadro_carga.get_children():
                cuadro_carga.delete(s)
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT * FROM producciones WHERE sector = "Carga_Cereales" or sector = "Carga_Comasa" or sector = "Carga_jarabe";""")         
        b = a.fetchall()  
        for i in b:
            if i[4]=="programado": 
                cuadro_carga.insert("", tk.END, text=i[0],
                                values=(i[1],i[3]))
        conexion.close()


def finalizar(sec):
    fecha = time.strftime("%d/%m/%y")
    hora = time.strftime("%H:%M:%S")
    respon = responsable.get()       
    if respon == "":
        messagebox.showinfo(message="Ingrese Responsable", title="Error")
        return
    producto = combobox.get()
    if sec == "nucleos":        
        codprod = cuadro.item(cuadro.selection())["text"]   
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        conexion.execute("""UPDATE producciones SET estado = "finalizado" WHERE codprod = ?;""", (codprod,))
        conexion.commit()   
        conexion.close()
        buscar("nucleos")
               
    if sec == "carga":
        codprod = cuadro_carga.item(cuadro_carga.selection())["text"]   
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        conexion.execute("""UPDATE producciones SET estado = "finalizado" WHERE codprod = ?;""", (codprod,))
        conexion.commit()        
        buscar("carga")
        conexion.close()
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    conexion.execute("""insert into registro_cambios (fecha,hora,responsable, producto, accion, programa, codprod)
                    VALUES(?,?,?,?,?,?,?);""",(fecha,hora,respon, producto, "Finalizar", "Produccion", codprod))
    conexion.commit()
    conexion.close()
    

def agregar():
    
    respon = responsable.get()    
    codprod = entrada_cod_prod_car.get()
    ndebatch = entrada_ndebatch_carga.get()
    if respon == "":
        messagebox.showinfo(message="Ingrese Responsable", title="Error")
        return
    producto = combobox.get()
    if codprod =="" or ndebatch == "" :
        messagebox.showinfo(message="Ingrese el Codigo de Produccion", title="Error")
        return
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    a = conexion.execute("""SELECT ndebatch FROM producciones WHERE codprod = ?;""",(codprod,))         
    b = a.fetchall()
    if b == []:
            messagebox.showinfo(message="Esta Produccion no esta Programada", title="Error")
            conexion.close()
            return
    else:
            conexion.execute("""UPDATE producciones set ndebatch = ? WHERE codprod = ?;""",(int(b[0][0])+ int(ndebatch), codprod))
            conexion.commit()     
            conexion.close()

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

def validar_entrada_cod(numero):
    try:
        int(numero)
        if len(entrada_lote_juliano.get()) == 0:
            if int(numero) == 0:
                return False
            else:
                return True
        else:
            return True
    except:
        return True   

def validar_entrada_cod_c(numero):
    try:
        int(numero)
        if len(entrada_lote_juliano_carga.get()) == 0:
            if int(numero) == 0:
                return False
            else:
                return True
        else:
            return True
    except:
        return True       
    
def selec_formula(s,sector):
    if s=="prod":        
        lote = entrada_lote_juliano.get()
        if lote == "":
            messagebox.showinfo(message="Ingrese el Lote", title="Error")
            return
        formula = combobox.get()
        try:
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            a = conexion.execute("""SELECT * FROM formulas WHERE nombre = ?;""", (formula,))         
            b = a.fetchall()
            entrada_cod_produccion["state"] = ["enable"]
            entrada_cod_produccion.delete(0,"end")
            entrada_cod_produccion.insert(0,str(b[0][2]) + lote + str(b[0][1][0]) + str(b[0][1][-1]))
            entrada_cod_produccion["state"] = ["readonly"]
            conexion.close()
        except:
            messagebox.showinfo(message="Error en BD", title="Error")
            conexion.close()
    if s == "carga":
        lote = entrada_lote_juliano_carga.get()
        if lote == "":
            messagebox.showinfo(message="Ingrese el Lote", title="Error")
            return
        formula = combobox_carga.get()
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT codfor FROM formulas WHERE nombre = ?;""", (formula,))         
        b = a.fetchall()
        entrada_cod_prod_car["state"] = ["enable"]
        entrada_cod_prod_car.delete(0,"end")
        entrada_cod_prod_car.insert(0,str(b[0][0]) + lote + "C" )
        entrada_cod_prod_car["state"] = ["readonly"]
        conexion.close()


def filtrar_opciones(formula,opciones,s):    
    if opciones == "mp":
        opcion = opciones_mp
    else:
        opcion = opciones_formula
    
    entrada = combo_var.get().lower()
 
    # Filtrar opciones que contengan el texto
    filtradas = [op for op in opcion if entrada in op[0].lower()]
    
    # Guardar posición del cursor y texto actual
    cursor_pos = formula.index(tk.INSERT)
    
    # Actualizar valores del Combobox
    formula['values'] = filtradas if filtradas else opcion
    
    # Restaurar el texto y la posición del cursor
    formula.delete(0, tk.END)
    formula.insert(0, combo_var.get())
    formula.icursor(cursor_pos)
    
    # Autocompletar si hay una sola opción
    if len(filtradas) == 1:
        formula.delete(0, tk.END)
        formula.insert(0, filtradas[0])
        formula.icursor(tk.END)

    # Mostrar menú desplegable
    formula.event_generate('<Down>')

def mostrar_formula():
    formula = cuadro.item(cuadro.selection())["values"][0] 
    batch = cuadro.item(cuadro.selection())["values"][1] 

    for s in cuadro2.get_children():
                cuadro2.delete(s)
    try:
        conexion=sqlite3.connect(entrada_ruta_bd.get())

        a = conexion.execute("""SELECT mp,cantidad FROM %s ;"""%formula)         
        b = a.fetchall()
        for i in b:
                cuadro2.insert("", tk.END, text=i[0],
                                    values=(float(i[1])*float(batch)))
        conexion.close()
    except:
        messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")
        conexion.close()  
    return

def exportar():
    try:   
        ruta = entrada_ruta_registro.get()     
        form = cuadro.item(cuadro.selection())["values"][0]
        with open(ruta + "/" + 'reporte' + str(form) + '.csv', 'w', newline='') as f:       
            writer = csv.writer(f,delimiter=';') 
            guardar = ["MP","Cantida"]
            writer.writerow(guardar)        
            for i in cuadro2.get_children():
                guardar.clear()            
                guardar.append((cuadro2.item(i)["text"]))    
                for t in cuadro2.item(i)["values"]:
                    guardar.append(t)
                writer.writerow(guardar)    
    except:
            messagebox.showinfo(message="Error al Exportar Datos", title="Error")


def cerrar():
    ventana.destroy
    sys.exit()

ventana = Tk()
ventana.protocol("WM_DELETE_WINDOW", cerrar)
ventana.geometry("1200x600")
ventana.title("Produccion")
tab_control = ttk.Notebook(ventana, width=1200, height=600)
tab_control.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_prod = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_prod.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_carga = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_carga.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_config = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_config.place(x=0, y=0, relheight=1, relwidth=1)
tab_control.add(pestaña_prod, text="Nucleos")
tab_control.add(pestaña_carga, text="Carga de Batch")
tab_control.add(pestaña_config, text="Configuracion")
label_ruta_bd = ttk.Label(pestaña_config, text="Ruta al Archivo de Lotes             ")
entrada_ruta_bd = ttk.Entry(pestaña_config, width=80)
entrada_ruta_bd.place(relx=0.27, rely=0.14)
boton_ruta_bd = ttk.Button(pestaña_config, text="Config. Ruta", command=partial(selecionar_ruta,"bd"))
boton_ruta_bd.place(relx=0.8, rely=0.14)
label_codigo = ttk.Label(pestaña_prod, text="Codigo de Produccion")
label_codigo.place(relx=0.01, rely=0.19)
label_lote_juliano = ttk.Label(pestaña_prod, text="Lote Juliano")
label_lote_juliano.place(relx=0.01, rely=0.01)
label_lote_juliano_carga = ttk.Label(pestaña_carga, text="Lote Juliano")
label_lote_juliano_carga.place(relx=0.01, rely=0.01)
label_formula = ttk.Label(pestaña_prod, text="Seleccionar Formula")
label_formula.place(relx=0.01, rely=0.07)
label_ndebatch = ttk.Label(pestaña_prod, text="N° de Batch")
label_ndebatch.place(relx=0.01, rely=0.13)

entrada_cod_produccion = ttk.Entry(pestaña_prod, width=20)
entrada_cod_produccion.place(relx=0.18, rely=0.19)
entrada_lote_juliano = ttk.Entry(pestaña_prod, width=20,validate="key",
                           validatecommand=((pestaña_prod.register(validar_entrada_cod)), "%S"))
entrada_lote_juliano.place(relx=0.18, rely=0.01)
entrada_lote_juliano_carga = ttk.Entry(pestaña_carga, width=20,validate="key",
                           validatecommand=((pestaña_prod.register(validar_entrada_cod_c)), "%S"))
entrada_lote_juliano_carga.place(relx=0.1, rely=0.01)

combo_var = tk.StringVar()


combobox = ttk.Combobox(pestaña_prod, width=30,textvariable=combo_var)
combobox.place(relx=0.18, rely=0.07)
combobox.bind("<<ComboboxSelected>>", partial(selec_formula,"prod"))
combobox.bind('<Return>', partial(filtrar_opciones,combobox,"formula"))
entrada_ndebatch= ttk.Entry(pestaña_prod, width=10,validate="key",
                           validatecommand=((pestaña_prod.register(validar_entrada)), "%S"))
entrada_ndebatch.place(relx=0.18, rely=0.13)


label_responsable = ttk.Label(pestaña_prod, text="Responsable")
label_responsable.place(relx=0.01, rely=0.25)
responsable = ttk.Entry(pestaña_prod, width=20)
responsable.place(relx=0.18, rely=0.25)

cuadro = ttk.Treeview(pestaña_prod, columns=("Formula","N° de Batch"))
barra = ttk.Scrollbar(cuadro)
cuadro.column("#0", width=20, anchor="center")
cuadro.column("Formula", width=80, anchor="center")
cuadro.column("N° de Batch", width=10, anchor="center")
cuadro.heading("#0", text="Codigo de Produccion")
cuadro.heading("Formula", text="Formula")
cuadro.heading("N° de Batch", text="N° de Batch")


cuadro.config(yscrollcommand=barra.set)
barra.config(command=cuadro.yview)
cuadro.place(relx=0.01, rely=0.3, relwidth=0.5, relheight=0.6)

barra.place(relx=0.97, rely=0.08, relheight=0.9)

cuadro2 = ttk.Treeview(pestaña_prod, columns=("Cantidad"))
barra2 = ttk.Scrollbar(cuadro2)
cuadro2.column("#0", width=20, anchor="center")
cuadro2.column("Cantidad", width=80, anchor="center")

cuadro2.heading("#0", text="MP")
cuadro2.heading("Cantidad", text="Cantidad")
cuadro2.config(yscrollcommand=barra2.set)
barra2.config(command=cuadro2.yview)
cuadro2.place(relx=0.65, rely=0.3, relwidth=0.3, relheight=0.6)
barra2.place(relx=0.95, rely=0.08, relheight=0.9)


boton_calcular = ttk.Button(pestaña_prod, text="Simular", command = partial(calcular,""))
boton_calcular.place(relx=0.4, rely=0.005,relheight = 0.08)
boton_finalizar = ttk.Button(pestaña_prod, text="Finalizar", command = partial (finalizar,"nucleos"))
boton_finalizar.place(relx=0.4, rely=0.198,relheight = 0.08)
boton_programar = ttk.Button(pestaña_prod, text="Programar", command = partial (nuevo,"nucleos"))
boton_programar.place(relx=0.4, rely=0.1,relheight = 0.08)
boton_mostrar = ttk.Button(pestaña_prod, text="Mostrar Formula", command = mostrar_formula)
boton_mostrar.place(relx=0.55, rely=0.5,relheight = 0.08)
boton_exp = ttk.Button(pestaña_prod, text="Exportar", command = exportar)
boton_exp.place(relx=0.55, rely=0.6,relheight = 0.08)

cuadro_carga = ttk.Treeview(pestaña_carga, columns=("Formula","N° de Batch"))

cuadro_carga.column("#0", width=20, anchor="center")
cuadro_carga.column("Formula", width=80, anchor="center")
cuadro_carga.column("N° de Batch", width=10, anchor="center")
cuadro_carga.heading("#0", text="Codigo de Produccion")
cuadro_carga.heading("Formula", text="Formula")
cuadro_carga.heading("N° de Batch", text="N° de Batch")
cuadro_carga.place(relx=0.26, rely=0.4, relwidth=0.5, relheight=0.5)

boton_nuevo_carga = ttk.Button(pestaña_carga, text="Nuevo", command = partial(nuevo,"carga"))
boton_nuevo_carga.place(relx=0.35, rely=0.01,relheight = 0.07)
boton_buscar_carga = ttk.Button(pestaña_carga, text="Buscar", command= partial(buscar,"carga"))
boton_buscar_carga.place(relx=0.27, rely=0.01)


boton_agregar_carga = ttk.Button(pestaña_carga, text="Agregar", command=agregar)
boton_agregar_carga.place(relx=0.27, rely=0.07)
boton_finalizar_carga = ttk.Button(pestaña_carga, text="Finalizar", command= partial(finalizar,"carga"))
boton_finalizar_carga.place(relx=0.35, rely=0.1,relheight = 0.07)
label_codigo_carga = ttk.Label(pestaña_carga, text="Codigo de Produccion")
label_codigo_carga.place(relx=0.01, rely=0.25)
label_formula_carga = ttk.Label(pestaña_carga, text="Seleccionar Formula")
label_formula_carga.place(relx=0.01, rely=0.07)
label_ndebatch_carga = ttk.Label(pestaña_carga, text="N° de Batch")
label_ndebatch_carga.place(relx=0.01, rely=0.13)
entrada_cod_prod_car = ttk.Entry(pestaña_carga, width=20)
entrada_cod_prod_car.place(relx=0.1, rely=0.25)
combobox_carga = ttk.Combobox(pestaña_carga, width=30)
combobox_carga.place(relx=0.1, rely=0.07)
combobox_carga.bind("<<ComboboxSelected>>", partial(selec_formula,"carga"))
entrada_ndebatch_carga= ttk.Entry(pestaña_carga, width=10,validate="key",
                           validatecommand=((pestaña_carga.register(validar_entrada)), "%S"))
entrada_ndebatch_carga.place(relx=0.1, rely=0.13)
label_sector = ttk.Label(pestaña_carga, text="Sector")
label_sector.place(relx=0.01, rely=0.19)
combobox_sector = ttk.Combobox(pestaña_carga, width=30, values=["Carga_Cereales","Carga_Comasa","Carga_Jarabe"])
combobox_sector.place(relx=0.1, rely=0.19)

label_ruta_registro = ttk.Label(pestaña_config, text="Ruta a Carpeta de Registros")
label_ruta_registro.place(relx=0.1, rely=0.3)
entrada_ruta_registro = ttk.Entry(pestaña_config, width= 60)
entrada_ruta_registro.place(relx=0.27, rely=0.3)
configurar_ruta_registro = ttk.Button(pestaña_config,command = partial(selecionar_ruta,"registro"),text="Conf. Ruta")
configurar_ruta_registro.place(relx=0.8, rely=0.3)

leer_archivo()
leer_base()
ventana.mainloop()
