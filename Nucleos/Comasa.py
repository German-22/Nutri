import sys
from datetime import datetime
import serial
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import *
import time
from csv import  writer
from functools import partial
import Leer_archivo as la
import sqlite3

sector_nucleos = ""
sector_macro = ""
sector_carga = ""

ruta_txt = "/archnucl"
act_bal_chica = True
act_bal_grande = True
inicio = False
inicio_macro = False
balanza_grande = serial.Serial()
balanza_grande.baudrate = 9600
balanza_grande.timeout = 1
balanza_grande.write_timeout = 1
balanza_chica = serial.Serial()
balanza_chica.baudrate = 9600
balanza_chica.timeout = 1
balanza_chica.write_timeout = 1

def leer_archivo():
    bd = la.Leer_archivo("archivo_bd.txt")
    sec = la.Leer_archivo("archivo_sector.txt")
    archivo_bd = bd.leer()
    archivo_sec = (sec.leer())
    if archivo_bd!= False:
        
        entrada_ruta_bd.delete("0", "end")
        entrada_ruta_bd.insert(0, archivo_bd)
        entrada_ruta_bd["state"] = ["disable"]        
        
    else:
        messagebox.showinfo(message="Configure la Ruta a la Base de Datos", title="Ruta Erronea")

    if archivo_sec!= False:
        
        sele_sector.delete("0", "end")
        sele_sector.set((archivo_sec))           
        
    else:
        messagebox.showinfo(message="Seleccione el Sector", title="Error")

def leer_base():
    global sector_nucleos,sector_macro,sector_carga
    try:
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        
        sec = sele_sector.get()
        if sec == "Cereales":
            sector_nucleos = "Nucleos_Cereales"
            sector_macro = "Macro_Cereales"
            sector_carga = "registro_carga"
        if sec == "Jarabe":
            sector_nucleos = "Nucleos_Jarabe"
            sector_macro = "Macro_Jarabe"
            sector_carga = "registro_carga"
        if sec == "Comasa":
            sector_nucleos = "Nucleos_Comasa"
            sector_macro = "Macro_Comasa"
            sector_carga = "registro_carga"
       
        a = conexion.execute("""SELECT formula FROM producciones WHERE sector = ? and estado = "programado" ;""" ,(sector_nucleos,))  
        combobox['values'] = list(a) 
        a = conexion.execute("""SELECT formula FROM producciones WHERE sector = ? ;""" ,(sector_carga,))
        combobox_carga['values'] = list(a)    
        a = conexion.execute("""SELECT formula FROM producciones WHERE sector = ? ;""" ,(sector_macro,))
        combobox_macro['values'] = list(a) 
        a = conexion.execute("""SELECT puerto FROM puerto WHERE balanza = "chica" ;""")
        b = a.fetchall()
        entrada_puerto_chico.insert(0,b[0][0]) 
        a = conexion.execute("""SELECT puerto FROM puerto WHERE balanza = "grande" ;""")
        b = a.fetchall()
        entrada_puerto_grande.insert(0,b[0][0])   
        conexion.close()
        entrada_puerto_grande["state"] = ["disable"] 
        entrada_puerto_chico["state"] = ["disable"]           
        des_balanza_grande["state"] = ["disable"]
        desactivar_balanza_chica["state"] = ["disable"]  
        boton_ruta_bd["state"] = ["disable"] 
        sele_sector["state"] = ["disable"]
               
    except:
       messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")

def des_balanza(r):
    global act_bal_chica
    global act_bal_grande
    if r == "chica":
        if act_bal_chica == True:
            act_bal_chica = False
            desactivar_balanza_chica.config(bg="white")
        else:
            act_bal_chica = True
            desactivar_balanza_chica.config(bg="green")
    if r == "grande":
        if act_bal_grande == True:
            act_bal_grande = False
            des_balanza_grande.config(bg="white")
        else:
            act_bal_grande = True
            des_balanza_grande.config(bg="green")

    if act_bal_chica == False or act_bal_grande == False:
        cantidad_pesar["state"] = ["enable"]
    else:
        cantidad_pesar["state"] = ["disabled"]

def conf_puerto(y):
    if y == "chico":
        sec = sele_sector.get()
        balanza_chica.port = str(entrada_puerto_chico.get()).upper()
        puerto = str(entrada_puerto_chico.get()).upper()
        try:
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            conexion.execute("""UPDATE puerto SET puerto = ?  WHERE sector = ? and balanza = ?;""",(puerto,sec,"chica"))
            conexion.commit()
            conexion.close()
        except:
            messagebox.showinfo(message="Error al Configurar Puerto", title="Error")
            conexion.close()
        try:
            balanza_chica.open()
        except serial.SerialException:
            messagebox.showinfo(message="Puerto de Balanza Incorrecto", title="Error")
        else:
            balanza_chica.close()
    if y == "grande":
        sec = sele_sector.get()
        balanza_grande.port = str(entrada_puerto_grande.get()).upper()
        puerto = str(entrada_puerto_grande.get()).upper()
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        try:
            conexion.execute("""UPDATE puerto SET puerto = ? WHERE sector = ? and balanza = ?;""",(puerto,sec,"grande"))
            conexion.commit()
            conexion.close()
        except:
            messagebox.showinfo(message="Error al Configurar Puerto", title="Error")
            conexion.close()
        try:
            balanza_grande.open()
        except serial.SerialException:
            messagebox.showinfo(message="Puerto de Balanza Incorrecto", title="Error")
        else:
            balanza_grande.close()

def selecionar_ruta():        
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

def seleccionar_sector(s):
    ruta_guardar = []
    sec = sele_sector.get()
    ruta_guardar.append(sec)
    try: 
        archivo = open(ruta_txt + "/archivo_sector.txt", "w")
        archivo_csv = writer(archivo)
        archivo_csv.writerow(ruta_guardar)
        archivo.close()
        leer_archivo()
    except:
        messagebox.showinfo(message="Error al Configurar la Ruta", title="Ruta Erronea")

def formula_seleccionada(event,sector):
    if event == "nucleos":
        try:
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            a = conexion.execute("""SELECT * FROM simulacion WHERE formula = ? and estado != "finalizado";""" ,(combobox.get(),))         
            b = a.fetchall()
            cod['state'] = ['enable']
            cod.delete(0,"end")
            cod.insert(0,b[0][1])
            cod['state'] = ['disable']
            a = conexion.execute("""SELECT * FROM simulacion WHERE codprod = ? and estado != "finalizado";""" ,(b[0][1],))         
            b = a.fetchall()
            for s in cuadro.get_children():
                cuadro.delete(s)
            for i in b:
                cuadro.insert("", tk.END, text=i[8], values=(i[3],i[5],i[6],i[4]))
                                               
            conexion.close()
        except:
              messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")
    if event == "macro":
        try:
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            a = conexion.execute("""SELECT * FROM simulacion WHERE formula = ?;""" , (combobox_macro.get(),))         
            b = a.fetchall()     
            
            cod_macro['state'] = ['enable']
            cod_macro.delete(0,"end")
            cod_macro.insert(0,b[0][1])
            cod_macro['state'] = ['disable']
            a = conexion.execute("""SELECT * FROM simulacion WHERE codprod = ? and estado != "finalizado";""" ,(b[0][1],))         
            b = a.fetchall()
            for s in cuadro_macro.get_children():
                cuadro_macro.delete(s)
            for i in b:
                cuadro_macro.insert("", tk.END, text=i[8], values=(i[3],i[6],i[5],i[4]))                                              
            conexion.close()
        except:
            messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")
    if event == "carga":
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT * FROM producciones WHERE formula = ? and sector = ? and estado = "programado" ;""" , (combobox_carga.get(),sector_carga))         
        b = a.fetchall()     
        ndebatch_carga['state'] = "enable"
        ndebatch_carga.delete(0,"end")
        ndebatch_carga.insert(0,b[0][3])
        ndebatch_carga['state'] = "disable"
        codprod = b[0][0]
        a = conexion.execute("""SELECT * FROM registro_carga WHERE codprod = ? ;""" , (codprod,))         
        b = a.fetchall()
        for i in b:
            cuadro_carga2.insert("", tk.END, text=i[1],
                        values=(i[2],i[4],i[5],i[6],i[3],i[8]))       
   
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
def mp_seleccionada(w,e):
    global MP_seleccionada_macro
    global MP_seleccionada  

    if(w == "nucleos"):
        if (inicio == True):
            MP_seleccionada = cuadro.item(cuadro.selection())["values"][0]            
            deposito = cuadro.item(cuadro.selection())["values"][3]
            ndebatch =  cuadro.item(cuadro.selection())["text"]  
            lote = cuadro.item(cuadro.selection())["values"][1]    
            cant = cuadro.item(cuadro.selection())["values"][2]                         
            lista_lote = []           
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            a = conexion.execute("""SELECT * FROM stock WHERE  mp = ? and estado = "liberado";""", (MP_seleccionada,))         
            for i in list(a):
                lista_lote.append(i[2])
            a = conexion.execute("""SELECT * FROM depositos;""")           
            deposito_selec["values"] = list(a)
            deposito_selec.set(deposito)
            mp_selec.delete(0, "end")
            combobox_lote.delete(0, "end")            
            mp_selec.set(MP_seleccionada)
            combobox_lote["values"] = lista_lote
            combobox_lote.set(lote)
            cantidad_pesar["state"] = "enable"
            cantidad_pesar.delete("0", "end")
            cantidad_pesar.insert(0,cant)   
            cantidad_pesar["state"] = "disable"             
            n_debatch.delete("0", "end")                   
            n_debatch.insert(0, ndebatch)                                  
            conexion.close()
        else:
             messagebox.showinfo(message="Debe Iniciar el Proceso", title="Error")

    if(w == "macro"):
        if (inicio_macro == True):
            ndebatch =  cuadro_macro.item(cuadro_macro.selection())["text"] 
            MP_seleccionada_macro = cuadro_macro.item(cuadro_macro.selection())["values"][0] 
            lista_lote_macro=[]    
            cantidad = cuadro_macro.item(cuadro_macro.selection())["values"][1]
            deposito = cuadro_macro.item(cuadro_macro.selection())["values"][3] 
            lote = cuadro_macro.item(cuadro_macro.selection())["values"][2]       
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            a = conexion.execute("""SELECT * FROM stock WHERE  mp = ? and estado = "liberado";""", (MP_seleccionada_macro,))         
            for i in list(a):
                lista_lote_macro.append(i[2])   
            a = conexion.execute("""SELECT * FROM depositos;""")        
            deposito_macro_selec.delete(0, "end")   
            deposito_macro_selec["values"] = list(a)
            deposito_macro_selec.set(deposito)                           
            mp_selec_macro.delete(0, "end")
            combobox_lote_macro.delete(0, "end")
            combobox_lote_macro.set("")
            mp_selec_macro.insert(0, MP_seleccionada_macro)
            combobox_lote_macro["values"] = lista_lote_macro            
            combobox_lote_macro.set(lote)
            cantidad_pesar_macro["state"] = "enable"            
            
            cantidad_pesar_macro.delete("0", "end")
            cantidad_pesar_macro.insert(0, cantidad) 
            cantidad_pesar_macro["state"] = "disable"   
            ndebatch_macro.delete("0", "end")                   
            ndebatch_macro.insert(0, ndebatch)                         
        else:
             messagebox.showinfo(message="Debe Iniciar el Proceso", title="Error")
                
def iniciar(sl):
    global inicio
    global inicio_macro
   
    if (sl == "nucleos"):
        if combobox.get() != "":
            inicio = True
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            a = conexion.execute("""SELECT * FROM %s WHERE codprod = ?;"""% sector_nucleos, (cod.get(),))
            b = a.fetchall()
            for s in cuadro2.get_children():
                cuadro2.delete(s)
            
            for i in b:
                cuadro2.insert("", tk.END, text=i[3], values=(i[3],i[1],i[4],i[8],i[6],i[7],i[5]))
            conexion.close
            boton1["state"] = ["disable"]
            combobox["state"] = ["disable"]
            n_debatch.delete(0, "end")
            combobox_lote.delete(0, "end")
            cantidad_pesar.delete(0, "end")                      
            #combobox_lote["state"] = ["readonly"]
            #mp_selec["state"] = ["enable"]
            #boton_pesar["state"] = ["enable"]
            n_debatch["state"] = ["enable"]
            responsable["state"] = ["enable"]
        else:
            messagebox.showinfo(message="Seleccione una Receta", title="Error")

    if (sl == "macro"):
        receta_seleccionada_macro = combobox_macro.get()
        if receta_seleccionada_macro != "":
            inicio_macro = True
           
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            a = conexion.execute("""SELECT * FROM %s WHERE codprod = ?;""" %sector_macro, (cod_macro.get(),))
            b = a.fetchall()
         
            for s in cuadro_macro2.get_children():
                cuadro_macro2.delete(s)
            
            for i in b:
                cuadro_macro2.insert("", tk.END, text=i[2], values=(i[3],i[1],i[4],i[8],i[6],i[7],i[5]))
           
            boton_iniciar_macro["state"] = ["disable"]
            combobox_macro["state"] = ["disable"]
            combobox_lote_macro.delete(0, "end")
            cantidad_pesar_macro.delete(0, "end")           
            #combobox_lote_macro["state"] = ["readonly"]
            #mp_selec_macro["state"] = ["enable"]
            #boton_pesar_macro["state"] = ["enable"]
            #cantidad_pesar_macro["state"] = ["enable"]
            responsable_macro["state"] = ["enable"]
           
        else:
            messagebox.showinfo(message="Seleccione una Receta", title="Error")

def sin_balanza(sec):
    
    if(sec == "nucleos"):     
        lote = combobox_lote.get()           
        cantidad = float(cantidad_pesar.get())
        nuevo_stock = stock - cantidad
        codprod = cod.get()
        fecha = time.strftime("%d/%m/%y")
        hora = time.strftime("%H:%M:%S")
        Deposito = cuadro.item(cuadro.selection())["values"][3]        
        formula = combobox.get()        
        try:
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            conexion.execute("""insert into %s (codprod,ndebatch,fecha,hora,mp,deposito,lote,vto,cantidad,responsable,sector,formula,comentario)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?);""" %sector_nucleos,(codprod, n_debatch.get(),fecha, hora, MP_seleccionada, Deposito, lote,vto,cantidad,responsable.get(),sector_nucleos,formula, comentario_nucleo.get()))
            conexion.commit()
            conexion.execute("""UPDATE stock SET stock = ? WHERE mp = ? and lote = ?;""",(nuevo_stock,MP_seleccionada,lote))
            conexion.commit()
            conexion.close()
            cuadro2.insert("", tk.END, text=fecha,
                        values=(hora, n_batch, MP_seleccionada, cantidad, lote, vto, Deposito))        
            n_debatch.delete("0", "end")
            n_debatch.insert(0, int(n_batch) + 1)
        except:
             messagebox.showinfo(message="Error al Conectar con BD", title="Error")  
        
    if (sec == "macro"):
        MP_seleccionada_macro = cuadro_macro.item(cuadro_macro.selection())["values"][0]
        lote = combobox_lote_macro.get()
        codprod = cod_macro.get()
        cantidad = float(cantidad_pesar_macro.get())       
        fecha = time.strftime("%d/%m/%y")
        hora = time.strftime("%H:%M:%S")
        Deposito = cuadro_macro.item(cuadro_macro.selection())["values"][3]        
        formula = combobox_macro.get()      
        nuevo_stock = stock - cantidad
        try:
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            conexion.execute("""insert into %s (codprod,ndebatch,fecha,hora,mp,deposito,lote,vto,cantidad,responsable,sector,formula,comentario)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?);"""%sector_macro,(codprod,ndebatch_macro.get(),fecha, hora, MP_seleccionada_macro, Deposito, lote,vto,cantidad,responsable_macro.get(),sector_macro,formula,comentario_macro.get()))
            conexion.commit()
            conexion.execute("""UPDATE stock SET stock = ? WHERE mp = ? and lote = ?;""",(nuevo_stock,MP_seleccionada_macro,lote))
            conexion.commit()
            conexion.close()
            cuadro_macro2.insert("", tk.END, text=fecha,
                        values=(hora,ndebatch_macro.get(),MP_seleccionada_macro, cantidad, lote,vto, Deposito))       
        except:
             messagebox.showinfo(message="Error al Conectar con BD", title="Error")  
        
def con_balanza(t):
    global peso_balanza
    peso_balanza = ""
    codprod = cod.get()
    lote = combobox_lote.get()
    fecha = time.strftime("%d/%m/%y")
    hora = time.strftime("%H:%M:%S")
    Deposito = cuadro.item(cuadro.selection())["text"]    
    formula = combobox.get()
    if t == "chica":
        try:
            balanza_chica.open()
            balanza_chica.write("P".encode('ASCII'))
            peso_balanza = (balanza_chica.readline()).decode("ASCII")
            balanza_chica.close()
        except serial.SerialException:
            messagebox.showinfo(message="Balanza no Conetada", title="Error")
        else:
            balanza_chica.close()
        global n_fila
    if t == "grande":
        try:
            balanza_grande.open()
            balanza_grande.write("P".encode('ASCII'))
            peso_balanza = (balanza_grande.readline()).decode("ASCII")
            balanza_grande.close()
        except serial.SerialException:
            messagebox.showinfo(message="Balanza no Conetada", title="Error")
        else:
            balanza_grande.close()
    if peso_balanza != "":
        if len(peso_balanza)>8:
            if "NET" in peso_balanza:
                peso_balanza = [c for c in peso_balanza if c.strip()]
                peso_mostrar = peso_balanza[4] + peso_balanza[5] + peso_balanza[6] + peso_balanza[7] + peso_balanza[8] + \
                               peso_balanza[9]  
                cantidad = float(peso_mostrar)
                nuevo_stock = stock - cantidad
                if nuevo_stock > 0:
                    conexion=sqlite3.connect(entrada_ruta_bd.get())
                    conexion.execute("""insert into registro_finos_cereales (codprod,ndebatch,fecha,hora,mp,deposito,lote,vto,cantidad,responsable,sector,formula,comentario)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?);""",(codprod, n_debatch.get(),fecha, hora, MP_seleccionada, Deposito, lote,vto,cantidad,responsable.get(),"nucleos_comasa",formula,comentario_nucleo.get()))
                    conexion.commit()
                    conexion.execute("""UPDATE stock SET stock = ? WHERE mp = ? and lote = ?;""",(nuevo_stock,MP_seleccionada,lote))
                    conexion.commit()
                    conexion.close()
                    cuadro2.insert("", tk.END, text= fecha,
                                values=(hora, n_batch, MP_seleccionada,cantidad, lote, vto,Deposito))
                    
                    n_fila = n_fila + 1
                    n_debatch.delete("0", "end")
                    n_debatch.insert(0, int(n_batch) + 1)
                else:    
                    messagebox.showinfo(message="No hay stock de este lote", title="ERROR")
                    conexion=sqlite3.connect(entrada_ruta_bd.get())
                    conexion.execute("""UPDATE stock SET estado = ? WHERE mp = ? and lote = ?;""",("agotado",MP_seleccionada,lote))
                    conexion.commit()
                    conexion.close()

            else:
                messagebox.showinfo(message="El Peso en la Balanza no es Estable", title="Error en Balanza")
        else:
            cantidad = float(peso_balanza[1:7])
            nuevo_stock = stock - cantidad
            if nuevo_stock > 0:
                conexion=sqlite3.connect(entrada_ruta_bd.get())
                conexion.execute("""insert into registro_finos_cereales (codprod,ndebatch,fecha,hora,mp,deposito,lote,vto,cantidad,responsable,sector,formula)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?);""",(codprod, n_debatch.get(),fecha, hora, MP_seleccionada, Deposito, lote,vto,cantidad,responsable.get(),"nucleos_comasa",formula))
                conexion.commit()
                conexion.execute("""UPDATE stock SET stock = ? WHERE mp = ? and lote = ?;""",(nuevo_stock,MP_seleccionada,lote))
                conexion.commit()
                conexion.close()
                cuadro2.insert("", tk.END, text= fecha,
                            values=(hora, n_batch, MP_seleccionada, peso_mostrar, lote, vto,Deposito))
                           
                n_fila = n_fila + 1
                n_debatch.delete("0", "end")
                n_debatch.insert(0, int(n_batch) + 1)
            else:    
                messagebox.showinfo(message="No hay stock de este lote", title="ERROR")
                conexion=sqlite3.connect(entrada_ruta_bd.get())
                conexion.execute("""UPDATE stock SET estado = ? WHERE mp = ? and lote = ?;""",("agotado",MP_seleccionada,lote))
                conexion.commit()
                conexion.close()
    else:
        messagebox.showinfo(message="Balanza no Conectada", title="Error en Balanza")

def pesar(sector):   
    global n_batch
    global stock    
    global vto
    lote = combobox_lote.get()
    n_batch = n_debatch.get()
    venc = ""
    if (sector == "nucleos"):       
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT * FROM stock WHERE  mp = ? and lote = ? and estado = "liberado" ;""", (MP_seleccionada,lote))         
        b = a.fetchall()[0]
        vto = b[5]
        stock = float(b[3])
        conexion.close()                    
        try:
            venc = datetime.strptime(str(vto), "%Y-%m-%d")           
        except:
            messagebox.showinfo(message="Error en Fecha de Vencimiento", title=  "Error en el formato del Archivo de lotes")
        if venc > (datetime.strptime(str(datetime.now().date()),"%Y-%m-%d")):
            if responsable.get() != "":                
                if float(cuadro.item(cuadro.selection())["values"][2]) < 3:
                        if act_bal_chica == True:
                            con_balanza("chica")
                        else:
                            sin_balanza("nucleos")
                else:
                    if act_bal_grande == True:
                        con_balanza("grande")
                    else:
                        sin_balanza("nucleos")                
            else:
                    messagebox.showinfo(message="INGRESE EL RESPONSABLE", title="ERROR")
        else:
            messagebox.showinfo(message="La Materia Prima Esta Vencida", title="Materia Prima Vencida")
        
        try:
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            codprod = cod.get()         
            a = conexion.execute("""SELECT * FROM %s WHERE codprod = ? and ndebatch = ?;"""%sector_nucleos,(codprod,n_batch))         
            b = a.fetchall()          
            suma = 0        
            for i in b:                    
                suma = suma + i[8]  
            a = conexion.execute("""SELECT formula FROM simulacion WHERE codprod = ? and ndebatch = ?;""",(codprod,n_batch))         
            b = a.fetchall()  
            formula = b[0][0]          
            p = conexion.execute("""SELECT cantidad FROM %s;""" % formula)  
            o = p.fetchall()
            total_batch = 0
            for e in o:
                total_batch = total_batch + e[0]
            if total_batch*1.01 >= suma and  total_batch*0.99 <= suma:                   
                conexion.execute("""insert into stock_nucleos (codprod,formula,ndebatch)
                    VALUES(?,?,?);""", (codprod,formula,n_batch))
                conexion.commit()                         
            conexion.close()
        except:
            messagebox.showinfo(message="Error de Conexion", title="Error")
        

    if (sector == "macro"):
        lote_macro = combobox_lote_macro.get()
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT * FROM stock WHERE  mp = ? and lote = ? and estado = "liberado" ;""", (MP_seleccionada_macro,lote_macro))         
        b = a.fetchall()[0]
        vto = b[5]
        stock = float(b[3])
        conexion.close()
        cantidad = float(cantidad_pesar_macro.get())
        nuevo_stock = stock - cantidad        
        try:
            venc = datetime.strptime(str(vto), "%Y-%m-%d")
        except:
            messagebox.showinfo(message="Error en Fecha de Vencimiento", title=  "Error en el formato del Archivo de lotes")
        
        if venc > (datetime.strptime(str(datetime.now().date()),"%Y-%m-%d")):
            if responsable_macro.get() != "":
                if nuevo_stock > 0: 
                        sin_balanza("macro")            
                else:
                  messagebox.showinfo(message="No hay stock de este lote", title="ERROR") 
                  conexion=sqlite3.connect(entrada_ruta_bd.get())
                  conexion.execute("""UPDATE stock SET estado = ? WHERE mp = ? and lote = ?;""",("agotado",MP_seleccionada,lote))
                  conexion.commit()
                  conexion.close()         
            else:
                messagebox.showinfo(message="INGRESE EL RESPONSABLE", title="ERROR")
        else:
            messagebox.showinfo(message="La Materia Prima Esta Vencida", title="Materia Prima Vencida")
      

def eliminar(sect):
    if(sect == "nucleos"):
        elemento_seleccionado = cuadro2.selection()
        if (str(elemento_seleccionado)) == "()":
            messagebox.showinfo(message="Seleccione Elemento a Eliminar", title="Error")
        else:
            elemento_mp = cuadro2.item(elemento_seleccionado)["values"]
            conexion=sqlite3.connect(entrada_ruta_bd.get())            
            codprod = cod.get()   
                    
            ndebatch = elemento_mp[1]
            mp = elemento_mp[2]
            cantidad = float(elemento_mp[3])
            lote = elemento_mp[4]   
            deposito = elemento_mp[6]
            a = conexion.execute("""SELECT stock FROM stock  WHERE mp = ? and deposito = ? and lote = ?;""",(mp,deposito,lote))  
            c = a.fetchall()  
            conexion.execute("""UPDATE stock SET stock = ? WHERE mp = ? and deposito = ? and lote = ?;""",(float(c[0][0])+cantidad,mp,deposito,lote))       
            conexion.commit()
            conexion.execute("""DELETE FROM %s WHERE codprod = ? and ndebatch = ? and mp = ? and lote = ?;""" %sector_nucleos, (codprod,ndebatch,mp,lote))
            conexion.commit()                 
            a = conexion.execute("""SELECT codprod, ndebatch FROM stock_nucleos LEFT OUTER JOIN %s USING(codprod, ndebatch) WHERE ndebatch = ? and codprod = ?;"""%sector_nucleos,(ndebatch,codprod))  
            c = a.fetchall()
            if c != []:
                conexion.execute("""DELETE FROM stock_nucleos WHERE codprod = ? and ndebatch = ?;""", (codprod,ndebatch))
                conexion.commit() 
            conexion.close()
            cuadro2.delete(elemento_seleccionado)
            

    if(sect == "macro"):
        elemento_seleccionado = cuadro_macro2.selection()
        if (str(elemento_seleccionado)) == "()":
            messagebox.showinfo(message="Seleccione Elemento a Eliminar", title="Error")
        else:
            elemento_mp = cuadro_macro2.item(elemento_seleccionado)["values"]                      
            codprod = cod_macro.get()
            batch = elemento_mp[1]
            mp = elemento_mp[2]
            lote = elemento_mp[4]
            cantidad = float(elemento_mp[3])           
            deposito = elemento_mp[6]
            
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            a = conexion.execute("""SELECT stock FROM stock  WHERE mp = ? and deposito = ? and lote = ?;""",(mp,deposito,lote))  
            c = a.fetchall() 
             
            conexion.execute("""UPDATE stock SET stock = ? WHERE mp = ? and deposito = ? and lote = ?;""",(float(c[0][0])+cantidad,mp,deposito,lote))       
            conexion.commit()
            conexion.execute("""DELETE FROM %s WHERE codprod = ? and ndebatch = ? and mp = ? and lote = ?;"""%sector_nucleos, (codprod,batch,mp,lote))
            conexion.commit()
            conexion.close()                       
            cuadro_macro2.delete(elemento_seleccionado)            

def cerrar():
    ventana.destroy
    sys.exit()

def probar_balanza():
    try:
        balanza_chica.open()
    except serial.SerialException:
        messagebox.showinfo(message="Balanza Chica no Conetada", title="Error")
    else:
        balanza_chica.close()
    try:
        balanza_grande.open()
    except serial.SerialException:
        messagebox.showinfo(message="Balanza Grande no Conetada", title="Error")
    else:
        balanza_grande.close()

def nuevo(sec):
    global inicio
    global inicio_macro
    if(sec == "nucleos"):
        for s in cuadro2.get_children():
            cuadro2.delete(s)
        for s in cuadro.get_children():
            cuadro.delete(s)
        boton1 ["state"] = ["enable"]
        combobox ["state"] = ["readonly"]
        
        if(inicio == True):
            inicio = False

    if (sec == "macro"):
        for s in cuadro_macro2.get_children():
            cuadro_macro2.delete(s)
        for s in cuadro_macro.get_children():
            cuadro_macro.delete(s)
        boton_iniciar_macro["state"] = ["enable"]
        combobox_macro["state"] = ["readonly"]
        if (inicio_macro == True):
            inicio_macro = False

def actualizar():
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    c = conexion.execute("""SELECT * FROM stock_nucleos WHERE estado = "completo";""" )  
    d = c.fetchall()   
    
    for s in cuadro_carga.get_children():
        cuadro_carga.delete(s)  
    for i in d:
        cuadro_carga.insert("", tk.END, text=i[2],
                    values=(i[1],i[0]))    
                
    conexion.close()  
def cargar():
    ndenucleo = cuadro_carga.item(cuadro_carga.selection())["text"]
    codnucleo= cuadro_carga.item(cuadro_carga.selection())["values"][1]    
      
    fecha = time.strftime("%d/%m/%y")
    hora = time.strftime("%H:%M:%S")
    conexion=sqlite3.connect(entrada_ruta_bd.get())    
    c = conexion.execute("""SELECT codprod FROM producciones WHERE formula = ? and estado = "programado" and sector = ?;""" ,(combobox_carga.get(),sector_carga))  
    d = c.fetchall()  
    a = conexion.execute("""SELECT ndebatch FROM registro_carga WHERE codprod = ? ORDER BY ndebatch desc;""",(d[0][0],))
    b = a.fetchall() 
    if b == []:
        b = [[0]]
    conexion.execute("""insert into registro_carga (fecha,hora,codprod,ndebatch,ndenucleo,formula,sector, codnucleo)
                    VALUES(?,?,?,?,?,?,?,?);""" ,(fecha,hora,d[0][0],b[0][0]+1,ndenucleo,combobox_carga.get(),sector_carga,codnucleo))
    conexion.commit()
    conexion.execute("""UPDATE stock_nucleos SET estado = "utilizado" WHERE codprod = ? and ndebatch = ?;""" ,(codnucleo, ndenucleo))
    conexion.commit()
    cuadro_carga2.insert("", tk.END, text=fecha,
                    values=(hora,b[0][0]+1,ndenucleo,combobox_carga.get(),d[0][0], codnucleo)) 

    conexion.close()   
    actualizar()

def eliminar_carga():
    ndenucleo = cuadro_carga2.item(cuadro_carga2.selection())["values"][2]
    codnucleo= cuadro_carga2.item(cuadro_carga2.selection())["values"][5]  
    ndebatch = cuadro_carga2.item(cuadro_carga2.selection())["values"][1]  
    codprodu = cuadro_carga2.item(cuadro_carga2.selection())["values"][4]  
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    conexion.execute("""UPDATE stock_nucleos SET estado = ? WHERE codprod = ? and ndebatch = ?;""" ,("completo",codnucleo, ndenucleo))
    conexion.commit()
    conexion.execute("""DELETE FROM registro_carga WHERE codprod = ? and ndebatch = ?;""" ,(codprodu, ndebatch))
    conexion.commit()
    cuadro_carga2.delete(cuadro_carga2.selection())
    conexion.close()
    actualizar()
    
def autenticar():
    if(entrada_contraseña.get()=="nutri17"):
        entrada_ruta_bd["state"] = ["enable"]        
        entrada_puerto_grande["state"] = ["enable"]
        entrada_puerto_chico["state"] = ["enable"]        
        des_balanza_grande["state"] = ["normal"]
        desactivar_balanza_chica["state"] = ["normal"]
        boton_ruta_bd["state"] = ["normal"] 
        sele_sector["state"] = ["enable"]
        combobox_lote_macro["state"] = ["readonly"]
        mp_selec_macro["state"] = ["enable"]
        boton_pesar_macro["state"] = ["enable"]
        cantidad_pesar_macro["state"] = ["enable"]
        combobox_lote["state"] = ["readonly"]
        mp_selec["state"] = ["enable"]
        boton_pesar["state"] = ["enable"]
        deposito_macro_selec["state"] = "readonly"
        deposito_selec["state"] = "readonly"
        cantidad_pesar["state"] = ["enable"]


    else:
        messagebox.showinfo(message="Contraseña Incorrecta", title="Contraseña Incorrecta")

def deposito_seleccionado(sector,e):
    
    mp = []    
    if sector == "nucleos":  
        deposito = deposito.get()      
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT DISTINCT mp FROM stock WHERE  deposito = ? and estado = "liberado";""", (deposito,))         
        b = a.fetchall()
        for i in b:
            mp.append(i[0])       
        mp_selec.delete(0, "end")        
        mp_selec["values"] = mp
        conexion.close()
    if sector == "macro":  
        deposito = deposito_macro_selec.get()      
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT DISTINCT mp FROM stock WHERE  deposito = ? and estado = "liberado";""", (deposito,))         
        b = a.fetchall()
        for i in b:
            mp.append(i[0])       
        mp_selec_macro.delete(0, "end")        
        mp_selec_macro["values"] = mp
        conexion.close()
       

def selec_materiaprima(sector,e):
    
    lote = []
    if sector == "nucleos":
        mp = mp_selec.get()
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT lote FROM stock WHERE  mp = ? and estado = "liberado";""", (mp,))         
        b = a.fetchall()
        for i in b:
            lote.append(i[0])   
        
        combobox_lote.delete(0, "end")
        combobox_lote.set("")
        combobox_lote["values"] = lote
        conexion.close()
    if sector == "macro":
        mp = mp_selec_macro.get()
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT lote FROM stock WHERE  mp = ? and estado = "liberado";""", (mp,))         
        b = a.fetchall()
        for i in b:
            lote.append(i[0])   
        
        combobox_lote_macro.delete(0, "end")
        combobox_lote_macro.set("")
        combobox_lote_macro["values"] = lote
        conexion.close()

ventana = Tk()
ventana.protocol("WM_DELETE_WINDOW", cerrar)
ventana.geometry("1300x650")
tab_control = ttk.Notebook(ventana, width=1000, height=650)
tab_control.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_nucleos = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_nucleos.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_macro = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_macro.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_carga = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_carga.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_config = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_config.place(x=0, y=0, relheight=1, relwidth=1)
tab_control.add(pestaña_nucleos, text="Preparacion de Nucleos")
tab_control.add(pestaña_macro, text="Carga de Macro")
tab_control.add(pestaña_carga, text="Carga de Batch")
tab_control.add(pestaña_config, text="Configuracion")
frame = ttk.Frame(pestaña_nucleos, borderwidth=10, relief="solid")
frame.place(x=0, y=0, relheight=0.45, relwidth=1)
frame2 = ttk.Frame(pestaña_nucleos, relief="solid", borderwidth=10)
frame2.place(x=0, rely=0.45, relheight=0.1, relwidth=1)
frame3 = ttk.Frame(pestaña_nucleos, relief="solid", borderwidth=10)
frame3.place(x=0, rely=0.55, relheight=0.45, relwidth=1)
frame_macro = ttk.Frame(pestaña_macro, borderwidth=10, relief="solid")
frame_macro.place(x=0, y=0, relheight=0.45, relwidth=1)
frame_macro2 = ttk.Frame(pestaña_macro, relief="solid", borderwidth=10)
frame_macro2.place(x=0, rely=0.45, relheight=0.1, relwidth=1)
frame_macro3 = ttk.Frame(pestaña_macro, relief="solid", borderwidth=10)
frame_macro3.place(x=0, rely=0.55, relheight=0.45, relwidth=1)
frame_config = ttk.Frame(pestaña_config, borderwidth=10)
frame_config.place(relheight=1, relwidth=1)

label_contraseña = ttk.Label(frame_config, text="Contraseña")
entrada_contraseña = ttk.Entry(frame_config, width= 30,show="*")
boto_autenticar = ttk.Button(frame_config, text="Autenticar", command=autenticar)
boto_autenticar.place(relx=0.8, rely=0.01)
label_contraseña.place(relx=0.05, rely=0.01)
entrada_contraseña.place(relx=0.27, rely=0.01)

label_ruta_bd = ttk.Label(frame_config, text="Ruta al Archivo de Lotes             ")
entrada_ruta_bd = ttk.Entry(frame_config, width=80)
label_puerto_chico = ttk.Label(frame_config, text="Puerto Balanza Chica             ")
label_puerto_chico.place(relx=0.05, rely=0.7)
label_puerto_grande = ttk.Label(frame_config, text="Puerto Balanza Grande             ")
label_puerto_grande.place(relx=0.05, rely=0.8)
entrada_puerto_chico = ttk.Entry(frame_config, width=20)
entrada_puerto_grande = ttk.Entry(frame_config, width=20)
entrada_ruta_bd.place(relx=0.27, rely=0.14)
entrada_puerto_chico.place(relx=0.27, rely=0.7)
entrada_puerto_grande.place(relx=0.27, rely=0.8)
boton_ruta_bd = ttk.Button(frame_config, text="Config. Ruta", command=selecionar_ruta)
boton_ruta_bd.place(relx=0.8, rely=0.14)
desactivar_balanza_chica = Button(frame_config, text="Act./Desc. Balaza",command=lambda: des_balanza("chica"),bg="green")
desactivar_balanza_chica.place(relx=0.5, rely=0.7)
des_balanza_grande = Button(frame_config, text="Act./Desc. Balaza", command=lambda: des_balanza("grande"),bg="green")
des_balanza_grande.place(relx=0.5, rely=0.8)
entrada_puerto_chico.bind("<Return>", lambda y: conf_puerto("chico"))
entrada_puerto_grande.bind("<Return>", lambda y: conf_puerto("grande"))
label_formula = ttk.Label(frame, text="Seleccionar Formula")
label_formula.place(relx=0.15, y=10)
cod = ttk.Entry(frame, width=15)
cod.place(relx=0.7, y=10)
cod_macro = ttk.Entry(frame_macro, width=15)
cod_macro.place(relx=0.7, y=10)

combobox = ttk.Combobox(frame, width=50, state="disable")
combobox.place(relx=0.35, y=10)
combobox.bind("<<ComboboxSelected>>", partial(formula_seleccionada,"nucleos"))
cuadro = ttk.Treeview(frame, columns=("MP","Lote","Cantidad", "Deposito"))
barra = ttk.Scrollbar(cuadro)
cuadro.column("#0", width=20, anchor="center")
cuadro.column("MP", width=100, anchor="center")
cuadro.column("Cantidad", width=30, anchor="center")
cuadro.column("Lote", width=30, anchor="center")
cuadro.column("Deposito", width=200, anchor="center")
cuadro.heading("#0", text="N° de Batch")
cuadro.heading("MP", text="MP")
cuadro.heading("Lote", text="Lote")
cuadro.heading("Cantidad", text="Cantidad")
cuadro.heading("Deposito", text="Deposito")

cuadro.config(yscrollcommand=barra.set)
barra.config(command=cuadro.yview)
cuadro.place(x=60, y=60, relwidth=0.9, relheight=0.6)
cuadro.bind("<<TreeviewSelect>>",partial(mp_seleccionada,"nucleos"))
barra.place(relx=0.97, rely=0.17, relheight=0.81)

label_formula_macro = ttk.Label(frame_macro, text="Seleccionar Formula")
label_formula_macro.place(relx=0.15, y=10)
combobox_macro = ttk.Combobox(frame_macro, width=50, state="disable")
combobox_macro.place(relx=0.35, y=10)
combobox_macro.bind("<<ComboboxSelected>>", partial(formula_seleccionada,"macro"))
cuadro_macro = ttk.Treeview(frame_macro, columns=("MP","Cantidad", "Lote", "Deposito"))
barra_macro = ttk.Scrollbar(cuadro_macro)
cuadro_macro.column("#0", width=20, anchor="center")
cuadro_macro.column("MP", width=100, anchor="center")
cuadro_macro.column("Cantidad", width=100, anchor="center")
cuadro_macro.column("Lote", width=200, anchor="center")
cuadro_macro.column("Deposito", width=200, anchor="center")
cuadro_macro.heading("#0", text="N° de Batch")
cuadro_macro.heading("MP", text="MP")
cuadro_macro.heading("Cantidad", text="Cantidad")
cuadro_macro.heading("Lote", text="Lote")
cuadro_macro.heading("Deposito", text="Deposito")
cuadro_macro.config(yscrollcommand=barra.set)
barra_macro.config(command=cuadro_macro.yview)
cuadro_macro.place(x=60, y=60, relwidth=0.75, relheight=0.6)
cuadro_macro.bind("<<TreeviewSelect>>",partial(mp_seleccionada,"macro"))
barra_macro.place(relx=0.97, rely=0.17, relheight=0.81)
label_mp_macro = ttk.Label(frame_macro2, text="Matera Prima")
label_mp_macro.place(relx=0.12, rely=0.35)
combobox_lote_macro = ttk.Combobox(frame_macro2, width=20, state="disabled")
combobox_lote_macro.place(relx=0.57, rely=0.35)

label_cantidad_macro = ttk.Label(frame_macro2, text="Kg")
cantidad_pesar_macro = ttk.Entry(frame_macro2, width=10, state="disabled", validate="key",
                           validatecommand=((frame_macro2.register(validar_entrada)), "%S"))
label_lote_macro = ttk.Label(frame_macro2, text="Lote MP")
mp_selec_macro = ttk.Combobox(frame_macro2, width=20, state="disabled")
mp_selec_macro.bind("<<ComboboxSelected>>", partial(selec_materiaprima,"macro"))

label_cantidad_macro.place(relx=0.44, rely=0.35)
cantidad_pesar_macro.place(relx=0.46, rely=0.35)
label_lote_macro.place(relx=0.52, rely=0.35)
mp_selec_macro.place(relx=0.19, rely=0.35)

deposito_macro_selec = ttk.Combobox(frame_macro2, width=10, state="disable")
deposito_macro_selec.bind("<<ComboboxSelected>>", partial(deposito_seleccionado,"macro"))
deposito_macro_selec.place(relx=0.36, rely=0.35)
label_deposito_macro = ttk.Label(frame_macro2, text= "Deposito")
label_deposito_macro.place(relx=0.31, rely=0.35)
label_ndebatch = ttk.Label(frame2, text="N° de Batch")
label_ndebatch.place(relx=0, rely=0.35)
n_debatch = ttk.Entry(frame2, width=7, state="disabled", validate="key",
                      validatecommand=((frame2.register(validar_entrada)), "%S"))
n_debatch.place(relx=0.07, rely=0.35)
label_mp = ttk.Label(frame2, text="Matera Prima")
label_mp.place(relx=0.12, rely=0.35)
combobox_lote = ttk.Combobox(frame2, width=20, state="disabled")
combobox_lote.place(relx=0.61, rely=0.35)
label_cantidad = ttk.Label(frame2, text="kg")
cantidad_pesar = ttk.Entry(frame2, width=10, state="disabled", validate="key",
                           validatecommand=((frame2.register(validar_entrada)), "%S"))
label_lote = ttk.Label(frame2, text="Lote MP")
mp_selec = ttk.Combobox(frame2, width=20, state="disabled")
deposito_selec = ttk.Combobox(frame2, width=10, state="disable")
deposito_selec.bind("<<ComboboxSelected>>", partial(deposito_seleccionado,"nucleos"))

label_cantidad.place(relx=0.47, rely=0.35)
cantidad_pesar.place(relx=0.49, rely=0.35)
label_lote.place(relx=0.57, rely=0.35)
mp_selec.place(relx=0.19, rely=0.35)
mp_selec.bind("<<ComboboxSelected>>", partial(selec_materiaprima,"nucleos"))
deposito_selec.place(relx=0.4, rely=0.35)
label_deposito = ttk.Label(frame2, text= "Deposito")
label_deposito.place(relx=0.35, rely=0.35)
label_responsable = ttk.Label(frame2, text= "Responsable")
label_responsable.place(relx=0.75, rely=0.35)
responsable = ttk.Entry(frame2, width=20, state="disabled")
responsable.place(relx=0.81, rely=0.35)

#Pestaña macro
label_responsable_macro = ttk.Label(frame_macro2, text= "Responsable")
label_responsable_macro.place(relx=0.7, rely=0.35)
responsable_macro = ttk.Entry(frame_macro2, width=25, state="disabled")
responsable_macro.place(relx=0.77, rely=0.35)
label_ndebatch_macro = ttk.Label(frame_macro2, text= "N° de Batch")
label_ndebatch_macro.place(relx=0, rely=0.35)
ndebatch_macro = ttk.Entry(frame_macro2, width=5)
ndebatch_macro.place(relx=0.07, rely=0.35)
cuadro_macro2 = ttk.Treeview(frame_macro3, columns=( "Hora","N° de Batch", "MP", "Cantidad", "Lote","Vencimiento","Deposito"))
barra_macro2 = ttk.Scrollbar(cuadro_macro2)
cuadro_macro2.column("#0", width=70, anchor="w")
cuadro_macro2.column("Hora", width=70, anchor="center")
cuadro_macro2.column("N° de Batch", width=70, anchor="center")
cuadro_macro2.column("MP", width=180, anchor="center")
cuadro_macro2.column("Cantidad", width=60, anchor="center")
cuadro_macro2.column("Lote", width=150, anchor="center")
cuadro_macro2.column("Vencimiento", width=100, anchor="center")
cuadro_macro2.column("Deposito", width=100, anchor="center")
cuadro_macro2.heading("#0", text="Fecha")
cuadro_macro2.heading("Hora", text="Hora")
cuadro_macro2.heading("N° de Batch", text="N° de Batch")
cuadro_macro2.heading("MP", text="MP")
cuadro_macro2.heading("Cantidad", text="Cantidad")
cuadro_macro2.heading("Lote", text="lote", )
cuadro_macro2.heading("Vencimiento", text="Vencimiento", )
cuadro_macro2.heading("Deposito", text="Deposito", )
cuadro_macro2.config(yscrollcommand=barra_macro2.set)
barra_macro2.config(command=cuadro_macro2.yview)
cuadro_macro2.place(relx=0, rely=0, relwidth=0.88, relheight=1)
barra_macro2.place(relx=0.97, rely=0.11, relheight=0.85)
boton_pesar_macro = ttk.Button(frame_macro2, text="Ingresar", command=partial(pesar,"macro"), state="disabled")
boton_pesar_macro.place(relx=0.9, rely=0.35)
boton_eliminar_macro = ttk.Button(frame_macro3, text="Eliminar", command=partial(eliminar,"macro"))
boton_eliminar_macro.place(relx=0.91, rely=0.6)
boton_nuevo_macro = ttk.Button(frame_macro, text="Nuevo", command = partial(nuevo, "macro"))
boton_nuevo_macro.place(relx=0.85, rely=0.4,relheight=0.2,relwidth=0.1)
cuadro2 = ttk.Treeview(frame3, columns=("Hora", "N° de Batch", "MP", "Cantidad", "Lote","Vencimiento","Deposito"))
barra2 = ttk.Scrollbar(cuadro2)
cuadro2.column("#0", width=70, anchor="w")
cuadro2.column("N° de Batch", width=50, anchor="center")
cuadro2.column("Hora", width=70, anchor="center")
cuadro2.column("MP", width=180, anchor="center")
cuadro2.column("Cantidad", width=60, anchor="center")
cuadro2.column("Lote", width=150, anchor="center")
cuadro2.column("Vencimiento", width=100, anchor="center")
cuadro2.column("Deposito", width=100, anchor="center")
cuadro2.heading("#0", text="Fecha")
cuadro2.heading("N° de Batch", text="N° de Batch")
cuadro2.heading("Hora", text="Hora")
cuadro2.heading("MP", text="MP")
cuadro2.heading("Cantidad", text="Cantidad")
cuadro2.heading("Lote", text="lote", )
cuadro2.heading("Vencimiento", text="Vencimiento", )
cuadro2.heading("Deposito", text="Deposito", )
cuadro2.config(yscrollcommand=barra2.set)
barra2.config(command=cuadro2.yview)
cuadro2.place(relx=0, rely=0, relwidth=0.88, relheight=1)
barra2.place(relx=0.97, rely=0.11, relheight=0.85)
boton1 = ttk.Button(frame, text="Iniciar", command = partial(iniciar, "nucleos"), state="disable")
boton1.place(relx=0.45, rely=0.9)
boton_iniciar_macro = ttk.Button(frame_macro, text="Iniciar", command = partial(iniciar, "macro"), state="disable")
boton_iniciar_macro.place(relx=0.45, rely=0.9)
boton_pesar = ttk.Button(frame2, text="Pesar", command=partial(pesar,"nucleos"), state="disabled")
boton_pesar.place(relx=0.93, rely=0.35)
boton_eliminar = ttk.Button(frame3, text="Eliminar", command = partial(eliminar, "nucleos"))
boton_eliminar.place(relx=0.91, rely=0.6)

boton_nuevo = ttk.Button(frame, text="Nuevo", command = partial(nuevo, "nucleos"))
boton_nuevo.place(relx=0.85, y=10)

#Pestaña Carga

cuadro_carga = ttk.Treeview(pestaña_carga, columns=("Formula", "CodigoProduccion"))
barra_carga = ttk.Scrollbar(cuadro_carga)
cuadro_carga.column("#0", width=70, anchor="w")
cuadro_carga.column("Formula", width=50, anchor="center")
cuadro_carga.column("CodigoProduccion", width=50, anchor="center")
cuadro_carga.heading("#0", text="N° de Nucleo")
cuadro_carga.heading("Formula", text="Furmula")
cuadro_carga.heading("CodigoProduccion", text="CodigoProduccion")
cuadro_carga.config(yscrollcommand=barra_carga.set)
barra_carga.config(command=cuadro_carga.yview)
cuadro_carga.place(relx=0.2, rely=0.1, relwidth=0.3, relheight=0.3)
barra_carga.place(relx=0.945, rely=0.13, relheight=0.85)
cuadro_carga2 = ttk.Treeview(pestaña_carga, columns=("Hora", "N° de Batch","N° de Nucleo", "Formula", "CodigoProduccion","CodNucleo"))
barra_carga2 = ttk.Scrollbar(cuadro_carga2)
cuadro_carga2.column("#0", width=70, anchor="w")
cuadro_carga2.column("Hora", width=70, anchor="center")
cuadro_carga2.column("N° de Batch", width=50, anchor="center")
cuadro_carga2.column("N° de Nucleo", width=50, anchor="center")
cuadro_carga2.column("Formula", width=180, anchor="center")
cuadro_carga2.column("CodigoProduccion", width=50, anchor="center")
cuadro_carga2.column("CodNucleo", width=50, anchor="center")
cuadro_carga2.heading("#0", text="Fecha")
cuadro_carga2.heading("Hora", text="Hora")
cuadro_carga2.heading("N° de Batch", text="N° de Batch")
cuadro_carga2.heading("N° de Nucleo", text="N° de Nucleo")
cuadro_carga2.heading("Formula", text="Formula")
cuadro_carga2.heading("CodigoProduccion", text="CodigoProduccion" )
cuadro_carga2.heading("CodNucleo", text="CodNucleo", )
cuadro_carga2.config(yscrollcommand=barra_carga2.set)
barra_carga2.config(command=cuadro_carga2.yview)
cuadro_carga2.place(relx=0.05, rely=0.5, relwidth=0.8, relheight=0.5)
barra_carga2.place(relx=0.98, rely=0.11, relheight=0.85)
boton_actualizar = ttk.Button(pestaña_carga, text="Actualizar", command= actualizar)
boton_actualizar.place(relx=0.8, rely=0.12, relheight=0.1, relwidth=0.1)
boton_cargar = ttk.Button(pestaña_carga, text="Cargar", command= cargar)
boton_cargar.place(relx=0.8, rely=0.27, relheight=0.1, relwidth=0.1)
boton_eliminarcarga = ttk.Button(pestaña_carga, text="Eliminar", command=eliminar_carga)
boton_eliminarcarga.place(relx=0.87, rely=0.7, relheight=0.1, relwidth=0.1)
label_formula_carga = ttk.Label(pestaña_carga, text="Seleccionar Formula")
label_formula_carga.place(relx=0.2, rely=0.02)
combobox_carga = ttk.Combobox(pestaña_carga, width=50)
combobox_carga.place(relx=0.3, rely=0.02)
combobox_carga.bind("<<ComboboxSelected>>", partial(formula_seleccionada,"carga"))

label_carga_ndebatch = ttk.Label(pestaña_carga, text="N° de Batch")
label_carga_ndebatch.place(relx=0.72, rely=0.02)
ndebatch_carga= ttk.Entry(pestaña_carga,width=5)
ndebatch_carga.place(relx=0.8, rely=0.02)
label_comentario_nucleos= ttk.Label(frame3,text="Comentario")
label_comentario_nucleos.place(relx=0.91, rely=0.01)
comentario_nucleo = ttk.Entry(frame3, width=20)
comentario_nucleo.place(relx=0.9, rely=0.1, height=80)
label_comentario_macro= ttk.Label(frame_macro3,text="Comentario")
label_comentario_macro.place(relx=0.91, rely=0.01)
comentario_macro = ttk.Entry(frame_macro3, width=20)
comentario_macro.place(relx=0.9, rely=0.1, height=80)
label_comentario_carga= ttk.Label(pestaña_carga,text="Comentario")
label_comentario_carga.place(relx=0.62, rely=0.15)
comentario_carga = ttk.Entry(pestaña_carga, width=40)
comentario_carga.place(relx=0.55, rely=0.19, height=80)
label_sector= ttk.Label(pestaña_config,text="Sector")
label_sector.place(relx=0.06, rely=0.6)
sele_sector = ttk.Combobox(pestaña_config, width=20,values=["Cereales","Jarabe","Comasa"])
sele_sector.place(relx=0.27, rely=0.6)
sele_sector.bind("<<ComboboxSelected>>", partial(seleccionar_sector))

leer_archivo()
leer_base()
ventana.title(sector_nucleos)
ventana.mainloop()
