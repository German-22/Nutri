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

def leer_base():
    global  opciones_formula
    global  opciones_mp
    print(entrada_ruta_bd.get())
    try:
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT nombre FROM formulas;""")   
        opciones_formula =  a.fetchall()       
        combobox['values'] = opciones_formula      
        a = conexion.execute("""SELECT * FROM depositos;""")           
        combobox_depo["values"] = list(a)    
        a = conexion.execute("""SELECT nombre FROM formulas WHERE sector = "Nucleos_Cereales" or sector = "Nucleos_Comasa" or sector = "Nucleos_Jarabe" ;""")         
        combobox_carga['values'] = list(a)                        
        a = conexion.execute("""SELECT DISTINCT formula FROM simulacion WHERE estado != "finalizado";""")         
        filtro['values'] = list(a)   
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

def calcular(x):
    eliminar("calcular")
    formula = str(combobox.get())
   
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    a = conexion.execute("""SELECT sector FROM formulas WHERE nombre = ?;""",(formula,))         
    sector_for = a.fetchall()[0][0]        

    a = conexion.execute("""SELECT codprod FROM producciones WHERE codprod = ? and estado = "programado";""", (entrada_cod_produccion.get(),))
    b = a.fetchall()    
        
    if x == "agregar":
        if b == []:
            messagebox.showinfo(message="ESTA PRODUCCION NO ESTA PROGRAMADA", title="Error")
            return
        else:            
            a = conexion.execute("""SELECT ndebatch FROM simulacion WHERE codprod = ? and estado != "finalizado" ORDER BY ndebatch desc;""",(entrada_cod_produccion.get(),))  
            b = a.fetchall()
            ndebatch_anterior = b[0][0]
            conexion.close()            
    else:
        if b == []:
            a = conexion.execute("""SELECT * FROM producciones WHERE formula = ? and estado = "programado" and sector != "Carga_Comasa";""", (formula,))
            b = a.fetchall()
            
            if b != []:           
                messagebox.showinfo(message="ESTA PRODUCCION YA ESTA PROGRAMADA", title="Error")
                conexion.close()
                return
        else:
            messagebox.showinfo(message="ESTA PRODUCCION YA ESTA PROGRAMADA", title="Error")
            conexion.close()
            return

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
        messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")   
    try:
        conexion=sqlite3.connect(entrada_ruta_bd.get())   
        for i in mp:   #Para cada materia prima de la formula busco que lotes hay en stock.
            vto.clear()
            stock.clear()
            mp_stock.clear()
            lote.clear()
            deposito.clear()             
            a = conexion.execute("""SELECT * FROM stock WHERE mp = ? and estado = "liberado" and stocksim > ? and stock > ? ORDER BY vto;""",(i,0.0001,0.0001))         
            b = a.fetchall()                              
            for p in b:        
                    
                if datetime.strptime(str(p[5]), "%Y-%m-%d") > (datetime.strptime(str(datetime.now().date()),"%Y-%m-%d")):
                    vto.append(p[5])
                    stock.append(round(p[4],3))                
                    lote.append(p[2])
                    deposito.append(p[1])
            dic_vto[i] = vto[0::] 
            dic_stock[i] = stock[0::]               
            dic_lote[i] = lote[0::]     
            dic_deposito[i] = deposito[0::]         
        conexion.close()
    except:
           
           messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")   
    try:     
        k = 0                 
        for i in dic_stock:#Recorro las MP en stock   
            m = 0                    
            if dic_stock[i]==[]:
                messagebox.showinfo(message="No Hay stock de" + " " + i , title="Stock Insuficiente") 
                k += 1
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
                        break
                    cant = float(dic_stock[i][m])
                else:
                    messagebox.showinfo(message="No Hay stock de" + " " + i , title="Stock Insuficiente")
                    break  
            if len(dic_deposito[i])>m:
                dic_calculo[dic_lote[i][m]] = [entrada_cod_produccion.get(),round(cant_usar,3),i,formula,dic_deposito[i][m],dic_lote[i][m],dic_vto[i][m]]
            
            m = m + 1   
            k = k + 1         
        
        s = []    
        for e in dic_calculo:  
            s.append((dic_calculo[e][0],dic_calculo[e][3], dic_calculo[e][2],dic_calculo[e][4],dic_calculo[e][5],(dic_calculo[e][1]),dic_calculo[e][6],1))
        conexion=sqlite3.connect(entrada_ruta_bd.get())    
        conexion.executemany("""insert into simulacion (codprod,formula, mp, deposito, lote, cantidad, vto, ndebatch)
                VALUES(?,?,?,?,?,?,?,?);""",(s))
        conexion.commit()        
        conexion.close()          
    except:           
           messagebox.showinfo(message="Error de calculo", title="Error de Conexion")     
    buscar("nucleos")
    return


def nuevo(sec):     
    fecha = time.strftime("%d/%m/%y")
    hora = time.strftime("%H:%M:%S")
    respon = responsable.get()       
    if respon == "":
        messagebox.showinfo(message="Ingrese Responsable", title="Error")
        return
    producto = combobox.get()
    if  sec == "nucleos":        
        codprod = entrada_cod_produccion.get()        
        ndebatch = entrada_ndebatch.get()
        if codprod == "" or ndebatch=="":
            messagebox.showinfo(message="Complete los Campos", title="Error")
            return
        conexion=sqlite3.connect(entrada_ruta_bd.get())       
        a = conexion.execute("""SELECT * FROM simulacion WHERE codprod = ? and estado = "simulado";""",(entrada_cod_produccion.get(),))         
        b = a.fetchall()  
        if b == []:
            return
       
        formula = b[0][2]        
        for i in b:  
            r = conexion.execute("""SELECT * FROM stock WHERE mp = ? and lote = ? and deposito = ? ;""",(i[3],i[5],i[4]))         
            f = r.fetchall()                 
            conexion.execute("""UPDATE stock SET stocksim = ? WHERE mp = ? and lote = ? and deposito = ?;""",(f[0][4]-i[6],f[0][0],f[0][2],f[0][1]))
            conexion.commit()             
        c = conexion.execute("""SELECT sector FROM formulas WHERE nombre = ?;""",(formula,))
        d = c.fetchall() 
        sector = d[0][0]
        e = conexion.execute("""SELECT ndebatch FROM producciones WHERE codprod = ?;""",(codprod,))
        f = e.fetchall()    
        if f == []:
            conexion.execute("""insert into producciones (codprod,formula,sector,ndebatch,estado)
                VALUES(?,?,?,?,?);""",(codprod, formula, sector, entrada_ndebatch.get(),"programado"))
            conexion.commit() 
        else:
            conexion.execute("""UPDATE producciones set ndebatch = ? WHERE codprod = ?;""",(float(f[0][0])+ float(entrada_ndebatch.get()), codprod))
            conexion.commit() 
        
        for i in b:  
            
            m = conexion.execute("""SELECT * FROM simulacion WHERE codprod = ? and mp = ? and lote = ? and estado = "programado";""",(entrada_cod_produccion.get(),i[3],i[5]))         
            n = m.fetchall() 
            
            if n !=[]:
                conexion.execute("""UPDATE simulacion SET cantidad = ? WHERE codprod = ? and mp = ? and lote = ? and estado = "programado";""" ,(round(float(n[0][6])+float(i[6]),3),entrada_cod_produccion.get(),i[3],i[5]))         
                conexion.commit()
                conexion.execute("""DELETE FROM simulacion WHERE codprod = ? and mp = ? and lote = ? and estado = "simulado";""",(entrada_cod_produccion.get(),i[3],i[5]))         
                conexion.commit()
            else:
                conexion.execute("""UPDATE simulacion SET estado = "programado" WHERE codprod = ? and mp = ? and lote = ?;""",(entrada_cod_produccion.get(),i[3],i[5]))
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
                    VALUES(?,?,?,?,?,?,?,?);""",(fecha,hora,respon, producto, ndebatch, "Programar", "Produccion",codprod))
    conexion.commit()
    conexion.close()

def buscar(sec, formula = "todas"):       
    if sec == "nucleos":        
        for s in cuadro.get_children():
                cuadro.delete(s)
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        if formula == "todas":                     
            a = conexion.execute("""SELECT * FROM simulacion WHERE estado != "finalizado";""")         
            b = a.fetchall()  
        else:
            a = conexion.execute("""SELECT * FROM simulacion WHERE estado != "finalizado" and formula = ?;""",(formula,))         
            b = a.fetchall() 
        
        for i in b:
            cuadro.insert("", tk.END, text=i[1],
                                values=(i[3],i[2],i[6],i[4],i[5],i[7],i[9],i[0]))
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

def eliminar(sec):
    if sec == "nucleos":
        codprod = cuadro.item(cuadro.selection())["text"]   
        conexion=sqlite3.connect(entrada_ruta_bd.get())       
        conexion.execute("""DELETE FROM simulacion WHERE codprod = ? and estado = "simulado";""", (codprod,))
        conexion.commit()               
        conexion.close()    
        buscar("nucleos")
    if sec == "calcular":          
        conexion=sqlite3.connect(entrada_ruta_bd.get())       
        conexion.execute("""DELETE FROM simulacion WHERE estado = "simulado";""")
        conexion.commit()               
        conexion.close()    
        buscar("nucleos")
    

def actualizar():
    codprod = entrada_cod_produccion.get()
    fecha = time.strftime("%d/%m/%y")
    hora = time.strftime("%H:%M:%S")
    respon = responsable.get()
    if respon == "":
        messagebox.showinfo(message="Ingrese Responsable", title="Error")
        return
    
    id = cuadro.item(cuadro.selection())["values"][7]  
    mp2 = cuadro.item(cuadro.selection())["values"][0]  
    dep = cuadro.item(cuadro.selection())["values"][3]  
    lot = cuadro.item(cuadro.selection())["values"][4]     
    can = cuadro.item(cuadro.selection())["values"][2] 
    formula = cuadro.item(cuadro.selection())["values"][1] 
    mp = combobox_mp.get()
    deposito = combobox_depo.get()
    cantidad = entrada_cantidad.get()
    lote = combobox_lote.get()

    conexion=sqlite3.connect(entrada_ruta_bd.get())
    a = conexion.execute("""SELECT vto , stocksim from stock WHERE mp = ? and deposito = ? and lote = ?;""", (mp,deposito,lote))
    b = a.fetchall()  
    
    if float(b[0][1]) >= float(cantidad):  
        
        conexion.execute("""UPDATE stock SET stocksim = ? WHERE mp = ? and lote = ? and deposito = ?;""",(float(b[0][1])-float(cantidad),mp,lote,deposito))
        conexion.commit()
        conexion.execute("""UPDATE stock SET stocksim = (stocksim+?) WHERE mp = ? and lote = ? and deposito = ?;""",(float(can),mp2,lot,dep))
        conexion.commit()
        conexion.execute("""UPDATE simulacion SET mp = ?, deposito = ?, lote = ?, cantidad = ? WHERE id = ?;""", (mp,deposito,lote,cantidad,id))
        conexion.commit()
        conexion.execute("""insert into registro_cambios (fecha,hora,responsable, producto, accion, programa, codprod,depnuevo,deposito,mp,mpnueva,lote,lotenuevo,stockant,nuevostock)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);""",(fecha,hora,respon, formula, "Actualizar MP", "Produccion", codprod, deposito, dep, mp2, mp,lot,lote,can,cantidad))
        conexion.commit()
        conexion.close()
    else:
        messagebox.showinfo(message="No hay suficiente stock", title="Error")
    conexion.close()
    buscar("nucleos", formula)
    

def agrear_mp():
    codprod = entrada_cod_produccion.get()
    fecha = time.strftime("%d/%m/%y")
    hora = time.strftime("%H:%M:%S")
    respon = responsable.get()    
    if respon == "":
        messagebox.showinfo(message="Ingrese Responsable", title="Error")
        return
    
    if codprod == "":
        messagebox.showinfo(message="Seleccione una Produccion", title="Error")
        return
    #ndebatch = entrada_ndeba.get()
    mp = combobox_mp.get()
    deposito = combobox_depo.get()
    cantidad = entrada_cantidad.get()
    lote = combobox_lote.get()
    formula = combobox.get()
    conexion=sqlite3.connect(entrada_ruta_bd.get())     
    a = conexion.execute("""SELECT vto , stocksim from stock WHERE mp = ? and deposito = ? and lote = ?;""", (mp,deposito,lote))
    b = a.fetchall()  
    
    if float(b[0][1]) >= float(cantidad):          
        conexion.execute("""INSERT INTO simulacion (codprod,formula, mp, deposito, lote, cantidad, vto, ndebatch) VALUES(?,?,?,?,?,?,?,?);""", (codprod,formula,mp,deposito,lote,cantidad,b[0][0],1))
        conexion.commit()
        conexion.execute("""insert into registro_cambios (fecha,hora,responsable, producto, accion, programa, codprod, deposito, mp, nuevostock,lote)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?);""",(fecha,hora,respon, formula, "Agregar MP", "Produccion", codprod, deposito, mp, cantidad,lote))
        conexion.commit()
        conexion.close()
        
    else:
        messagebox.showinfo(message="No hay suficiente stock", title="Error")
        conexion.close()
    buscar("nucleos", formula)

def deposito_seleccionado(e):    
    mp = []              
    deposito = combobox_depo.get()      
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    a = conexion.execute("""SELECT DISTINCT mp FROM stock WHERE  deposito = ? and estado = "liberado";""", (deposito,))         
    b = a.fetchall()
    for i in b:
        mp.append(i[0])       
    combobox_mp.delete(0, "end")        
    combobox_mp["values"] = mp
    conexion.close()

def selec_materiaprima(e):    
    lote = []   
    mp = combobox_mp.get()
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    a = conexion.execute("""SELECT lote FROM stock WHERE  mp = ? and estado = "liberado" and stock > ?;""", (mp,0.0001))         
    b = a.fetchall()
    for i in b:
        lote.append(i[0])     
    combobox_lote.delete(0, "end")
    combobox_lote.set("")
    combobox_lote["values"] = lote
    conexion.close()

def seleccion(g,h):    
    try:        
        codprod = cuadro.item(cuadro.selection())["text"]
        formula = cuadro.item(cuadro.selection())["values"][1]
        entrada_cod_produccion.delete(0,"end")
        entrada_ndebatch.delete(0,"end")
        combobox.delete(0,"end")
        combobox.set("")
        combobox.set(formula)
        entrada_cod_produccion.insert(0,str(codprod))
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT ndebatch FROM simulacion WHERE codprod = ? and estado = "simulado" ORDER BY ndebatch desc;""",(codprod,))  
        b = a.fetchall() 
        if b != []:       
            ndebatch_sim = b[0][0]   
        else:
            return
        a = conexion.execute("""SELECT ndebatch FROM simulacion WHERE codprod = ? and estado = "programado" ORDER BY ndebatch desc;""",(codprod,))
        b = a.fetchall()
        if b != []:
            ndebatch_prog=b[0][0]
        else:
            return         
        entrada_ndebatch.insert(0,int(ndebatch_sim)-int(ndebatch_prog))
        conexion.close()
    except:
        None

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
        a = conexion.execute("""SELECT * FROM simulacion WHERE codprod = ? and estado != "simulado" and estado != "finalizado";""",(codprod,))         
        b = a.fetchall()         
              
        if b != []:
            for i in b:            
                r = conexion.execute("""SELECT * FROM stock WHERE mp = ? and lote = ? and deposito = ?;""", (i[3],i[5],i[4]))         
                f = r.fetchall()                
                if f == []:   
                    messagebox.showinfo(message="Hay un Error en BD", title="Error")
                    conexion.close()
                    return
                if f[0][3] <= 0:      
                    estado = "agotado"
                    conexion.execute("""UPDATE stock SET stocksim = ? WHERE mp = ? and lote = ? and deposito = ?;""",(0,i[3],i[5],i[4]))
                    conexion.commit()
                    conexion.execute("""UPDATE stock SET estado = ? WHERE mp = ? and lote = ? and deposito = ?;""",(estado,i[3],i[5],i[4]))
                    conexion.commit()
                else:
                    estado = "liberado" 
                    
                    if f[0][3] >= (i[6] + f[0][4]):                                                     
                        conexion.execute("""UPDATE stock SET stocksim = (stocksim + ?) WHERE mp = ? and lote = ? and deposito = ?;""",(i[6],i[3],i[5],i[4]))
                        conexion.commit()       
                    else:
                        conexion.execute("""UPDATE stock SET stocksim = ? WHERE mp = ? and lote = ? and deposito = ?;""",(f[0][3],i[3],i[5],i[4]))
                        conexion.commit()         
        
            conexion.execute("""DELETE FROM simulacion WHERE codprod = ?;""", (codprod,))
            conexion.commit()
            #conexion.close()
            for s in cuadro.get_children():
                cuadro.delete(s)
        else:
            messagebox.showinfo(message="ESTA PRODUCCION NO ESTA PROGRAMADA", title="Error")
            conexion.close()
            return 
        
    if sec == "carga":
        codprod = cuadro_carga.item(cuadro_carga.selection())["text"]   
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        conexion.execute("""UPDATE producciones SET estado = "finalizado" WHERE codprod = ?;""", (codprod,))
        conexion.commit()        
        buscar("carga")
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
        codprod = cuadro.item(cuadro.selection())["text"]
        if codprod != "":
            entrada_cod_produccion["state"] = ["enable"]
            entrada_cod_produccion.delete(0,"end")
            entrada_cod_produccion.insert(0,codprod)
            entrada_cod_produccion["state"] = ["readonly"]
            return
        lote = entrada_lote_juliano.get()
        if lote == "":
            messagebox.showinfo(message="Ingrese el Lote", title="Error")
            return
        formula = combobox.get()
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT * FROM formulas WHERE nombre = ?;""", (formula,))         
        b = a.fetchall()
        entrada_cod_produccion["state"] = ["enable"]
        entrada_cod_produccion.delete(0,"end")
        entrada_cod_produccion.insert(0,str(b[0][2]) + lote + str(b[0][1][0]) + str(b[0][1][-1]))
        entrada_cod_produccion["state"] = ["readonly"]
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

def filtrar_formula(s):
    prod = str(filtro.get())
    for s in cuadro.get_children():
                cuadro.delete(s)
    conexion=sqlite3.connect(entrada_ruta_bd.get())
       
    a = conexion.execute("""SELECT * FROM simulacion WHERE formula = ? and estado != "finalizado";""", (prod,))         
    b = a.fetchall()  
    for i in b:
        cuadro.insert("", tk.END, text=i[1],
                                values=(i[3],i[2],round(i[6],3),i[4],i[5],i[7],i[9],i[0]))
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
boton_ruta_bd = ttk.Button(pestaña_config, text="Config. Ruta", command=selecionar_ruta)
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
label_cant = ttk.Label(pestaña_prod, text="Cantidad")
label_cant.place(relx=0.4, rely=0.19)
label_mp = ttk.Label(pestaña_prod, text="Materia Prima")
label_mp.place(relx=0.4, rely=0.01)
label_deposito = ttk.Label(pestaña_prod, text="Deposito")
label_deposito.place(relx=0.4, rely=0.07)
label_lote = ttk.Label(pestaña_prod, text="Lote")
label_lote.place(relx=0.4, rely=0.13)
combobox_mp = ttk.Combobox(pestaña_prod, width=30)
combobox_mp.place(relx=0.5, rely=0.01)
combobox_depo = ttk.Combobox(pestaña_prod, width=30)
combobox_depo.place(relx=0.5, rely=0.07)
combobox_lote = ttk.Combobox(pestaña_prod, width=30)
combobox_depo.bind("<<ComboboxSelected>>", partial(deposito_seleccionado))
combobox_lote.place(relx=0.5, rely=0.13)
combobox_mp.bind("<<ComboboxSelected>>", partial(selec_materiaprima))
entrada_cantidad = ttk.Entry(pestaña_prod, width=20,validate="key",
                           validatecommand=((pestaña_prod.register(validar_entrada)), "%S"))
entrada_cantidad.place(relx=0.5, rely=0.19)
entrada_cod_produccion = ttk.Entry(pestaña_prod, width=20)
entrada_cod_produccion.place(relx=0.1, rely=0.19)
entrada_lote_juliano = ttk.Entry(pestaña_prod, width=20,validate="key",
                           validatecommand=((pestaña_prod.register(validar_entrada_cod)), "%S"))
entrada_lote_juliano.place(relx=0.1, rely=0.01)
entrada_lote_juliano_carga = ttk.Entry(pestaña_carga, width=20,validate="key",
                           validatecommand=((pestaña_prod.register(validar_entrada_cod_c)), "%S"))
entrada_lote_juliano_carga.place(relx=0.1, rely=0.01)
combo_var = tk.StringVar()


combobox = ttk.Combobox(pestaña_prod, width=30,textvariable=combo_var)
combobox.place(relx=0.1, rely=0.07)
combobox.bind("<<ComboboxSelected>>", partial(selec_formula,"prod"))
combobox.bind('<Return>', partial(filtrar_opciones,combobox,"formula"))
entrada_ndebatch= ttk.Entry(pestaña_prod, width=10,validate="key",
                           validatecommand=((pestaña_prod.register(validar_entrada)), "%S"))
entrada_ndebatch.place(relx=0.1, rely=0.13)

label_filtro = ttk.Label(pestaña_prod, text="Filtro")
label_filtro.place(relx=0.01, rely=0.25)
filtro = ttk.Combobox(pestaña_prod, width=30)
filtro.place(relx=0.1, rely=0.25)
filtro.bind("<<ComboboxSelected>>", partial(filtrar_formula))
cuadro = ttk.Treeview(pestaña_prod, columns=("MP","Formula","Cantidad", "Deposito", "Lote", "Vto","Estado","id"))
barra = ttk.Scrollbar(cuadro)
cuadro.column("#0", width=20, anchor="center")
cuadro.column("MP", width=80, anchor="center")
cuadro.column("Formula", width=80, anchor="center")
#cuadro.column("N° de Batch", width=10, anchor="center")
cuadro.column("Cantidad", width=20, anchor="center")
cuadro.column("Deposito", width=10, anchor="center")
cuadro.column("Lote", width=40, anchor="center")
cuadro.column("Vto", width=20, anchor="center")
cuadro.column("Estado", width=20, anchor="center")
cuadro.column("id", width=5, anchor="center")
cuadro.heading("#0", text="Codigo de Produccion")
cuadro.heading("MP", text="MP")
cuadro.heading("Formula", text="Formula")
#cuadro.heading("N° de Batch", text="N° de Batch")
cuadro.heading("Cantidad", text="Cantidad")
cuadro.heading("Deposito", text="Deposito")
cuadro.heading("Lote", text="Lote")
cuadro.heading("Vto", text="Vto")
cuadro.heading("Estado", text="Estado")
cuadro.heading("id", text="id")
cuadro.config(yscrollcommand=barra.set)
barra.config(command=cuadro.yview)
cuadro.place(relx=0.01, rely=0.3, relwidth=0.98, relheight=0.6)
cuadro.bind("<<TreeviewSelect>>",partial(seleccion,""))
barra.place(relx=0.98, rely=0.1, relheight=0.85)
boton_calcular = ttk.Button(pestaña_prod, text="Simular", command = partial(calcular,""))
boton_calcular.place(relx=0.27, rely=0.01)
boton_nuevo = ttk.Button(pestaña_prod, text="Programar", command = partial (nuevo,"nucleos"))
boton_nuevo.place(relx=0.8, rely=0.04,relheight = 0.1)

boton_eliminar = ttk.Button(pestaña_prod, text="Eliminar", command = partial (eliminar,"nucleos"))
boton_eliminar.place(relx=0.27, rely=0.07)
boton_actualizar = ttk.Button(pestaña_prod, text="Actualizar", command=actualizar)
boton_actualizar.place(relx=0.67, rely=0.07)
boton_agregar = ttk.Button(pestaña_prod, text="Agregar", command=partial(calcular,"agregar"))
boton_agregar.place(relx=0.27, rely=0.13)
boton_finalizar = ttk.Button(pestaña_prod, text="Finalizar", command = partial (finalizar,"nucleos"))
boton_finalizar.place(relx=0.9, rely=0.04,relheight = 0.1)
cuadro_carga = ttk.Treeview(pestaña_carga, columns=("Formula","N° de Batch"))

cuadro_carga.column("#0", width=20, anchor="center")
cuadro_carga.column("Formula", width=80, anchor="center")
cuadro_carga.column("N° de Batch", width=10, anchor="center")
cuadro_carga.heading("#0", text="Codigo de Produccion")
cuadro_carga.heading("Formula", text="Formula")
cuadro_carga.heading("N° de Batch", text="N° de Batch")
cuadro_carga.place(relx=0.26, rely=0.4, relwidth=0.5, relheight=0.5)
cuadro_carga.bind("<<TreeviewSelect>>",partial(seleccion,""))
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
boton_agregar_mp = ttk.Button(pestaña_prod, text="Agregar MP", command= agrear_mp)
boton_agregar_mp.place(relx=0.67, rely=0.12)
#label_ndeba = ttk.Label(pestaña_prod, text="N° de Batch")
#label_ndeba.place(relx=0.4, rely=0.25)
#entrada_ndeba= ttk.Entry(pestaña_prod, width=10,validate="key",
#                           validatecommand=((pestaña_carga.register(validar_entrada)), "%S"))
#entrada_ndeba.place(relx=0.5, rely=0.25)
label_responsable = ttk.Label(pestaña_prod, text="Responsable")
label_responsable.place(relx=0.4, rely=0.25)
responsable = ttk.Entry(pestaña_prod, width=20)
responsable.place(relx=0.5, rely=0.25)
leer_archivo()
leer_base()
ventana.mainloop()
