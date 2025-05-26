import sys
from datetime import datetime
import serial
import tkinter as tk
from tkinter import messagebox, filedialog
import time
from csv import  writer
import Leer_archivo as la
import sqlite3
 
sector_nucleos = ""
sector_macro = ""
sector_carga = "registro_carga"
reg_carga = ""

ruta_txt = "/archnucl"
act_bal_chica = False
act_bal_grande = False
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

def leer_archivo(base,sector,entrada_ruta_bd,sele_sector):
    bd = la.Leer_archivo(base)
    sec = la.Leer_archivo(sector)
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

def leer_base(entrada_ruta_bd,sele_sector,combobox,combobox_carga,combobox_macro,entrada_puerto_chico,entrada_puerto_grande,des_balanza_grande,desactivar_balanza_chica,boton_ruta_bd):
    global sector_nucleos,sector_macro,sector_carga,reg_carga
    try:
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        
        sec = sele_sector.get()
        if sec == "Cereales":
            sector_nucleos = "Nucleos_Cereales"
            sector_macro = "Macro_Cereales"
            reg_carga = "Carga_Cereales"
        if sec == "Jarabe":
            sector_nucleos = "Nucleos_Jarabe"
            sector_macro = "Macro_Jarabe"
            reg_carga = "Carga_Jarabe"
        if sec == "Comasa":
            sector_nucleos = "Nucleos_Comasa"
            sector_macro = "Macro_Comasa"
            reg_carga = "Carga_Comasa"
        
        a = conexion.execute("""SELECT formula FROM producciones WHERE sector = ? and estado = "programado" ;""" ,(sector_nucleos,))  
        combobox['values'] = list(a) 
        a = conexion.execute("""SELECT formula FROM producciones WHERE sector = ? and estado = "programado" ;""" ,(reg_carga,))
        combobox_carga['values'] = list(a)    
        a = conexion.execute("""SELECT formula FROM producciones WHERE sector = ? and estado = "programado";""" ,(sector_macro,))
        combobox_macro['values'] = list(a) 
        a = conexion.execute("""SELECT puerto FROM puerto WHERE balanza = "chica" and sector = ? ;""",(sector_nucleos,))
        b = a.fetchall()
      
        entrada_puerto_chico.insert(0,b[0][0]) 
        a = conexion.execute("""SELECT puerto FROM puerto WHERE balanza = "grande" and sector = ?;""",(sector_nucleos,))
        b = a.fetchall()
        entrada_puerto_grande.insert(0,b[0][0])   
        conexion.close()
        entrada_puerto_grande["state"] = ["disable"] 
        entrada_puerto_chico["state"] = ["disable"]           
        des_balanza_grande["state"] = ["disable"]
        desactivar_balanza_chica["state"] = ["disable"]  
        boton_ruta_bd["state"] = ["disable"] 
        sele_sector["state"] = ["disable"]
        balanza_chica.port = str(entrada_puerto_chico.get()).upper()
        balanza_grande.port = str(entrada_puerto_grande.get()).upper()
               
    except:
       messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")

def des_balanza(r,desactivar_balanza_chica,des_balanza_grande,cantidad_pesar):
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

def conf_puerto(y,entrada_puerto_chico,entrada_ruta_bd,entrada_puerto_grande):
    if y == "chico":        
        balanza_chica.port = str(entrada_puerto_chico.get()).upper()
        puerto = str(entrada_puerto_chico.get()).upper()
        try:
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            conexion.execute("""UPDATE puerto SET puerto = ?  WHERE sector = ? and balanza = ?;""",(puerto,sector_nucleos,"chica"))
            conexion.commit()
            conexion.close()
        except:
            messagebox.showinfo(message="Error al Configurar Puerto", title="Error")
            conexion.close()
        try:
            balanza_chica.open()
        except serial.SerialException:
            messagebox.showinfo(message="Puerto de Balanza Chica Incorrecto", title="Error")
        else:
            balanza_chica.close()
    if y == "grande":
       
        balanza_grande.port = str(entrada_puerto_grande.get()).upper()
        puerto = str(entrada_puerto_grande.get()).upper()
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        try:
            conexion.execute("""UPDATE puerto SET puerto = ? WHERE sector = ? and balanza = ?;""",(puerto,sector_nucleos,"grande"))
            conexion.commit()
            conexion.close()
        except:
            messagebox.showinfo(message="Error al Configurar Puerto", title="Error")
            conexion.close()
        try:
            balanza_grande.open()
        except serial.SerialException:
            messagebox.showinfo(message="Puerto de Balanza Grande Incorrecto", title="Error")
        else:
            balanza_grande.close()

def selecionar_ruta(entrada_ruta_bd,base,sector,sele_sector):        
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
        leer_archivo(base,sector,entrada_ruta_bd,sele_sector)
    except:
        messagebox.showinfo(message="Error al Configurar la Ruta", title="Ruta Erronea")

def seleccionar_sector(sele_sector,base,sector,entrada_ruta_bd,s):
    ruta_guardar = []
    sec = sele_sector.get()
    ruta_guardar.append(sec)
    try: 
        archivo = open(ruta_txt +"/"+ sector,"w")
        archivo_csv = writer(archivo)
        archivo_csv.writerow(ruta_guardar)
        archivo.close()
        leer_archivo(base,sector,entrada_ruta_bd,sele_sector)
    except:
        messagebox.showinfo(message="Error al Configurar la Ruta", title="Ruta Erronea")

def formula_seleccionada(event,entrada_ruta_bd,cod,cuadro,cod_macro,cuadro_macro,ndebatch_carga,cuadro_carga2,combobox,combobox_macro,combobox_carga,h):
    if event == "nucleos":
        try:
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            a = conexion.execute("""SELECT codprod FROM producciones WHERE formula = ? and estado != "finalizado";""" ,(combobox.get(),))         
            b = a.fetchall()                        
            cod['state'] = ['enable']
            cod.delete(0,"end")
            cod.insert(0,b[0][0])
            cod['state'] = ['disable']            
            a = conexion.execute("""SELECT * FROM %s;"""% combobox.get())         
            b = a.fetchall()               
            conexion.close()         
            for s in cuadro.get_children():
                cuadro.delete(s)
            for i in b:                
                cuadro.insert("", tk.END, text=i[0], values=(i[1],i[2]))                  
        except:
              messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")
              conexion.close()  
    if event == "macro":
        try:
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            a = conexion.execute("""SELECT codprod FROM producciones WHERE formula = ? and estado != "finalizado";""" ,(combobox_macro.get(),))         
            b = a.fetchall() 
                    
            cod_macro['state'] = ['enable']
            cod_macro.delete(0,"end")
            cod_macro.insert(0,b[0][0])
            cod_macro['state'] = ['disable']            
            a = conexion.execute("""SELECT * FROM %s;"""% combobox_macro.get())         
            b = a.fetchall()         
            conexion.close()           
            for s in cuadro_macro.get_children():
                cuadro_macro.delete(s)
            for i in b:
                cuadro_macro.insert("", tk.END, text=i[0], values=(i[1],i[2]))                                              
           
        except:
            messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")
            conexion.close()
    if event == "carga":
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT * FROM producciones WHERE formula = ? and sector = ? and estado = "programado" ;""" , (combobox_carga.get(),reg_carga))         
        b = a.fetchall()     
        ndebatch_carga['state'] = "enable"
        ndebatch_carga.delete(0,"end")
        ndebatch_carga.insert(0,b[0][3])
        ndebatch_carga['state'] = "disable"
        codprod = b[0][0]
        a = conexion.execute("""SELECT * FROM registro_carga WHERE codprod = ? ;""" , (codprod,))         
        b = a.fetchall()
        conexion.close()
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

def mp_seleccionada(w,cuadro,entrada_ruta_bd,deposito_selec,mp_selec,combobox_lote,cantidad_pesar,n_debatch,cuadro_macro,deposito_macro_selec,mp_selec_macro,combobox_lote_macro,cantidad_pesar_macro,ndebatch_macro,mostrar_stock,mostrar_stock_macro,s):
    global MP_seleccionada_macro
    global MP_seleccionada  
    
    if(w == "nucleos"):             
        if (inicio == True):                           
            try:
                MP_seleccionada = cuadro.item(cuadro.selection())["text"]                      
                deposito = cuadro.item(cuadro.selection())["values"][0]                   
                cant = cuadro.item(cuadro.selection())["values"][1]                         
            except:
                return
            lista_lote = []           
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            a = conexion.execute("""SELECT * FROM stock WHERE  mp = ? and stock > ? and estado = "liberado" ORDER BY vto;""", (MP_seleccionada, 0.0001))         
            b = a.fetchall()
            for i in b:
                lista_lote.append(i[2])
            a = conexion.execute("""SELECT * FROM depositos;""")           
            deposito_selec["values"] = list(a)
            deposito_selec.set(deposito)
            mp_selec.delete(0, "end")                   
            combobox_lote.delete(0, "end")            
            mp_selec.set(MP_seleccionada)            
            combobox_lote["values"] = lista_lote   
            combobox_lote.set(lista_lote[0])         
            cantidad_pesar["state"] = "enable"
            cantidad_pesar.delete("0", "end")
            cantidad_pesar.insert(0,cant)   
            #cantidad_pesar["state"] = "disable"             
            n_debatch.delete("0", "end") 
            mostrar_stock.delete(0, tk.END)  
            mostrar_stock.insert(0,round(b[0][3],4)) 

            conexion.close()
            
        else:
             messagebox.showinfo(message="Debe Iniciar el Proceso", title="Error")

    if(w == "macro"):
        if (inicio_macro == True):
            try:                
                MP_seleccionada_macro = cuadro_macro.item(cuadro_macro.selection())["text"]
                lista_lote_macro=[]    
                cantidad = cuadro_macro.item(cuadro_macro.selection())["values"][1]
                deposito = cuadro_macro.item(cuadro_macro.selection())["values"][0]                     
            except:                 
                messagebox.showinfo(message="Seleccione una Materia Prima", title="ERROR") 
                return            
            
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            a = conexion.execute("""SELECT * FROM stock WHERE  mp = ? and estado = "liberado" ORDER BY vto;""", (MP_seleccionada_macro,))         
            b = a.fetchall()
            for i in list(b):
                lista_lote_macro.append(i[2])   
            a = conexion.execute("""SELECT * FROM depositos;""")        
            deposito_macro_selec.delete(0, "end")   
            deposito_macro_selec["values"] = list(a)
            deposito_macro_selec.set(deposito)                           
            mp_selec_macro.delete(0, "end")
            combobox_lote_macro.delete(0, "end")            
            combobox_lote_macro.set(lista_lote_macro[0])
            mp_selec_macro.set(MP_seleccionada_macro)
            combobox_lote_macro["values"] = lista_lote_macro     
            
            cantidad_pesar_macro["state"] = "enable"                    
            cantidad_pesar_macro.delete("0", "end")            
            ndebatch_macro.delete("0", "end")     
            mostrar_stock_macro.delete(0, tk.END)  
            mostrar_stock_macro.insert(0,round(b[0][3],2))              
            conexion.close()      
                            
        else:
             messagebox.showinfo(message="Debe Iniciar el Proceso", title="Error")
                
def iniciar(sl,boton1,combobox,entrada_ruta_bd,cuadro2,cod,n_debatch,combobox_lote,cantidad_pesar,boton_pesar,responsable,combobox_macro,cuadro_macro2,boton_iniciar_macro,combobox_lote_macro,cantidad_pesar_macro,boton_pesar_macro,responsable_macro,cod_macro):
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
                cuadro2.insert("", tk.END, text=i[2], values=(i[3],i[1],i[4],i[8],i[6],i[7],i[5]))
            conexion.close
            boton1["state"] = ["disable"]
            combobox["state"] = ["disable"]
            n_debatch.delete(0, "end")
            combobox_lote.delete(0, "end")
            cantidad_pesar.delete(0, "end")                      
            combobox_lote["state"] = ["enable"]
            #mp_selec["state"] = ["enable"]
            boton_pesar["state"] = ["enable"]
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
            if sector_macro == "Macro_Comasa":
                  for i in b:
                        cuadro_macro2.insert("", tk.END, text=i[2], values=(i[3],i[0],i[4],i[8],i[6],i[7],i[5]))
            else:
                for i in b:
                    cuadro_macro2.insert("", tk.END, text=i[2], values=(i[3],i[1],i[4],i[8],i[6],i[7],i[5]))
           
            boton_iniciar_macro["state"] = ["disable"]
            combobox_macro["state"] = ["disable"]
            combobox_lote_macro.delete(0, "end")
            cantidad_pesar_macro.delete(0, "end")           
            #combobox_lote_macro["state"] = ["readonly"]
            #mp_selec_macro["state"] = ["enable"]
            boton_pesar_macro["state"] = ["enable"]
            cantidad_pesar_macro["state"] = ["enable"]
            responsable_macro["state"] = ["enable"]
           
        else:
            messagebox.showinfo(message="Seleccione una Receta", title="Error")

def actualizar_nucleos(combobox_lote,entrada_ruta_bd,cod):
    try:
        lote = combobox_lote.get()
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        codprod = cod.get()         
        a = conexion.execute("""SELECT * FROM %s WHERE codprod = ? and ndebatch = ?;"""%sector_nucleos,(codprod,n_batch))         
        b = a.fetchall()          
        suma = 0        
        for i in b:                    
            suma = suma + i[8]  
        a = conexion.execute("""SELECT formula FROM simulacion WHERE codprod = ?;""",(codprod,))         
        b = a.fetchall()        
        
        formula = b[0][0]          
        p = conexion.execute("""SELECT cantidad FROM %s;""" % formula)  
        o = p.fetchall()
        total_batch = 0
        for e in o:
            total_batch = total_batch + e[0]
        a = conexion.execute("""SELECT distinct ndebatch FROM producciones WHERE codprod = ?;""",(codprod,))         
        b = a.fetchall()  
        decimal = b[0][0] - int(b[0][0])      
        
        if total_batch*1.01 >= suma and  total_batch*0.99 <= suma:                   
            conexion.execute("""insert into stock_nucleos (codprod,formula,ndebatch)
                VALUES(?,?,?);""", (codprod,formula,n_batch))
            conexion.commit()                         
            conexion.close()     
        else:            
            if decimal*total_batch*1.01 >= suma and  decimal*total_batch*0.99 <= suma:                   
                conexion.execute("""insert into stock_nucleos (codprod,formula,ndebatch)
                    VALUES(?,?,?);""", (codprod,formula,n_batch))
                conexion.commit()                         
                conexion.close()  
            conexion.close() 
    except:
        conexion.close()
        messagebox.showinfo(message="Error de Conexion", title="Error")
    return

def registrar(cantidad,nuevo_stock,cuadro,mp_selec,cod,combobox_lote,deposito_selec,combobox,entrada_ruta_bd,n_debatch,cuadro2,responsable,comentario_nucleo):
    try:        
        MP_seleccionada = mp_selec.get()
        codprod = cod.get()
        lote = combobox_lote.get()
        fecha = time.strftime("%d/%m/%y")
        hora = time.strftime("%H:%M:%S")
        Deposito = deposito_selec.get()    
        formula = combobox.get()
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        conexion.execute("""insert into %s (codprod,ndebatch,fecha,hora,mp,deposito,lote,vto,cantidad,responsable,sector,formula,comentario)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?);""" %sector_nucleos,(codprod, n_debatch.get(),fecha, hora, MP_seleccionada, Deposito, lote,vto,cantidad,responsable.get(),sector_nucleos,formula,comentario_nucleo.get()))
        conexion.commit()
        conexion.execute("""UPDATE stock SET stock = ? WHERE mp = ? and lote = ?;""",(nuevo_stock,MP_seleccionada,lote))
        conexion.commit()        
        cuadro2.insert("", tk.END, text= fecha,
                values=(hora, n_batch, MP_seleccionada,cantidad, lote, vto,Deposito))
        conexion.commit()          
        conexion.close()
        #actualizar_nucleos(combobox_lote,entrada_ruta_bd,cod)     
    except:
        conexion.close()
        messagebox.showinfo(message="Error al Conectar con BD", title="ERROR")                        
        return

def sin_balanza(sec,cuadro_macro2,comentario_macro,responsable_macro,ndebatch_macro,cuadro_macro,entrada_ruta_bd,cuadro,cantidad_pesar,mp_selec_macro,combobox_lote_macro,cod_macro,cantidad_pesar_macro,deposito_macro_selec,combobox_macro,mp_selec,cod,combobox_lote,deposito_selec,combobox,n_debatch,cuadro2,responsable,comentario_nucleo):    
    if(sec == "nucleos"):  
        cant_sim = cuadro.item(cuadro.selection())["values"][1]                  
        cantidad = float(cantidad_pesar.get())
        nuevo_stock = stock - cantidad                  
        if nuevo_stock>=0:             
            if float(cant_sim) - cantidad>=0 :
                registrar(cantidad,nuevo_stock,cuadro,mp_selec,cod,combobox_lote,deposito_selec,combobox,entrada_ruta_bd,n_debatch,cuadro2,responsable,comentario_nucleo) 
            else:
                messagebox.showinfo(message="Esta Registrando mas de lo Necesario", title="ERROR")
        else:
            messagebox.showinfo(message="No hay stock de este lote", title="ERROR")

    if (sec == "macro"):
               
        MP_seleccionada_macro = mp_selec_macro.get()
        lote = combobox_lote_macro.get()
        codprod = cod_macro.get()
        cantidad = float(cantidad_pesar_macro.get())       
        fecha = time.strftime("%d/%m/%y")
        hora = time.strftime("%H:%M:%S")
        Deposito = deposito_macro_selec.get()       
        formula = combobox_macro.get()      
        nuevo_stock = stock - cantidad
        
        try:
            conexion=sqlite3.connect(entrada_ruta_bd.get())            
            cant_sim = cuadro_macro.item(cuadro_macro.selection())["values"]            
            if sector_macro == "Macro_Comasa":
                conexion.execute("""insert into %s (codprod,fecha,hora,mp,deposito,lote,vto,cantidad,responsable,sector,formula,comentario)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?);"""%sector_macro,(codprod,fecha, hora, MP_seleccionada_macro, Deposito, lote,vto,cantidad,responsable_macro.get(),sector_macro,formula,comentario_macro.get()))
                conexion.commit()                  
                cuadro_macro2.insert("", tk.END, text=fecha,
                values=(hora,id,MP_seleccionada_macro, cantidad, lote,vto, Deposito))     
            else:
                if ndebatch_macro.get()=="":
                    messagebox.showinfo(message="Ingrese el Numero de Batch", title="ERROR")
                    return
                conexion.execute("""insert into %s (codprod,ndebatch,fecha,hora,mp,deposito,lote,vto,cantidad,responsable,sector,formula,comentario)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?);"""%sector_macro,(codprod,ndebatch_macro.get(),fecha, hora, MP_seleccionada_macro, Deposito, lote,vto,cantidad,responsable_macro.get(),sector_macro,formula,comentario_macro.get()))
                conexion.commit()
                cuadro_macro2.insert("", tk.END, text=fecha,
                    values=(hora,ndebatch_macro.get(),MP_seleccionada_macro, cantidad, lote,vto, Deposito))
                                
                         
            conexion.execute("""UPDATE stock SET stock = ? WHERE mp = ? and lote = ?;""",(nuevo_stock,MP_seleccionada_macro,lote))
            conexion.commit()
            conexion.close()
        except:
            messagebox.showinfo(message="Error al Conectar con BD", title="Error")  
            conexion.close()        
    return


def con_balanza(t):
    global peso_balanza
    peso_balanza = ""   
    if t == "chica":
        try:
            balanza_chica.open()
            balanza_chica.write("P".encode('ASCII'))
            peso_balanza = (balanza_chica.readline()).decode("ASCII")
            balanza_chica.close()
        except serial.SerialException:
            messagebox.showinfo(message="Balanza Chica no Conetada", title="Error")
            balanza_chica.close()
            return
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
            messagebox.showinfo(message="Balanza Grande no Conetada", title="Error")
            balanza_grande.close()
            return
        else:
            balanza_grande.close()
    if peso_balanza != "":
        if len(peso_balanza)>8:
            if "NET" in peso_balanza:
                peso_balanza = [c for c in peso_balanza if c.strip()]
                peso_mostrar = peso_balanza[4] + peso_balanza[5] + peso_balanza[6] + peso_balanza[7] + peso_balanza[8] + peso_balanza[9]  
                cantidad = float(peso_mostrar)
                nuevo_stock = stock - cantidad
                if nuevo_stock >= 0:
                    registrar(cantidad,nuevo_stock)                                               
                else:    
                    messagebox.showinfo(message="No hay stock de este lote", title="ERROR")
                    return        
            else:
                messagebox.showinfo(message="El Peso en la Balanza no es Estable", title="Error en Balanza")
        else:
            cantidad = float(peso_balanza[1:7])
            nuevo_stock = stock - cantidad
            if nuevo_stock >= 0:                
                registrar(cantidad, nuevo_stock)              
                             
            else:    
                messagebox.showinfo(message="No hay stock de este lote", title="ERROR")
                
                return
    else:
        messagebox.showinfo(message="Balanza no Conectada", title="Error en Balanza")
    return

def pesar(sector,combobox_lote,responsable_macro,combobox_lote_macro,mp_selec_macro,cantidad_pesar_macro,cuadro_macro,responsable,n_debatch,cuadro,mp_selec,entrada_ruta_bd,cuadro_macro2,comentario_macro,ndebatch_macro,cantidad_pesar,cod_macro,deposito_macro_selec,combobox_macro,cod,deposito_selec,combobox,comentario_nucleo,cuadro2):   
    global n_batch
    global stock    
    global vto    
    venc = ""    
    
    if (sector == "nucleos"):
        
        lote = combobox_lote.get()
        n_batch = n_debatch.get()
        if n_batch == "":
            messagebox.showinfo(message="Ingrese el Numero de Batch", title="ERROR")
            return
        if lote == "":
            messagebox.showinfo(message="Ingrese el Lote", title="ERROR")
            return
        seleccion = cuadro.item(cuadro.selection())["values"]        
        if seleccion == "":
            messagebox.showinfo(message="Seleccione una Materia Prima", title="ERROR") 
            return        
        MP_seleccionada = mp_selec.get()
        try:    
            conexion=sqlite3.connect(entrada_ruta_bd.get())            
            a = conexion.execute("""SELECT * FROM stock WHERE  mp = ? and lote = ? and estado = "liberado" ;""", (MP_seleccionada,lote))         
            b = a.fetchall()[0]
            vto = b[5]
            stock = float(b[3])
            conexion.close()         
        except:
            messagebox.showinfo(message="ERROR EN BD", title="ERROR")
            return
        try:
            venc = datetime.strptime(str(vto), "%Y-%m-%d")           
        except:
            messagebox.showinfo(message="Error en Fecha de Vencimiento", title=  "Error en el formato del Archivo de lotes")
            return
        if venc > (datetime.strptime(str(datetime.now().date()),"%Y-%m-%d")):
            if responsable.get() != "":                
                if float(cuadro.item(cuadro.selection())["values"][1]) < 3:
                        if act_bal_chica == True:
                            con_balanza("chica")
                        else:
                            sin_balanza("nucleos",cuadro_macro2,comentario_macro,responsable_macro,ndebatch_macro,cuadro_macro,entrada_ruta_bd,cuadro,cantidad_pesar,mp_selec_macro,combobox_lote_macro,cod_macro,cantidad_pesar_macro,deposito_macro_selec,combobox_macro,mp_selec,cod,combobox_lote,deposito_selec,combobox,n_debatch,cuadro2,responsable,comentario_nucleo)
                else:
                    if act_bal_grande == True:
                        con_balanza("grande")
                    else:
                        sin_balanza("nucleos",cuadro_macro2,comentario_macro,responsable_macro,ndebatch_macro,cuadro_macro,entrada_ruta_bd,cuadro,cantidad_pesar,mp_selec_macro,combobox_lote_macro,cod_macro,cantidad_pesar_macro,deposito_macro_selec,combobox_macro,mp_selec,cod,combobox_lote,deposito_selec,combobox,n_debatch,cuadro2,responsable,comentario_nucleo)                
            else:
                    messagebox.showinfo(message="INGRESE EL RESPONSABLE", title="ERROR")
        else:
            messagebox.showinfo(message="La Materia Prima Esta Vencida", title="Materia Prima Vencida")
                
    if (sector == "macro"):
        seleccion = cuadro_macro.item(cuadro_macro.selection())["values"]        
        if seleccion == "":
            messagebox.showinfo(message="Seleccione una Materia Prima", title="ERROR") 
            return
        
        if cantidad_pesar_macro.get() == "":
            messagebox.showinfo(message="Ingrese la Cantidad ", title="ERROR") 
            return

        MP_seleccionada_macro = mp_selec_macro.get()
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
            return       
        if venc > (datetime.strptime(str(datetime.now().date()),"%Y-%m-%d")):
            if responsable_macro.get() != "":
                if nuevo_stock >= 0: 
                        sin_balanza("macro",cuadro_macro2,comentario_macro,responsable_macro,ndebatch_macro,cuadro_macro,entrada_ruta_bd,cuadro,cantidad_pesar,mp_selec_macro,combobox_lote_macro,cod_macro,cantidad_pesar_macro,deposito_macro_selec,combobox_macro,mp_selec,cod,combobox_lote,deposito_selec,combobox,n_debatch,cuadro2,responsable,comentario_nucleo)            
                else:
                  messagebox.showinfo(message="No hay stock de este lote", title="ERROR")                     
            else:
                messagebox.showinfo(message="INGRESE EL RESPONSABLE", title="ERROR")
        else:
            messagebox.showinfo(message="La Materia Prima Esta Vencida", title="Materia Prima Vencida")
    return

def eliminar(sect,cuadro2,cod,cuadro,cuadro_macro,entrada_ruta_bd,cuadro_macro2,cod_macro):
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
            conexion.execute("""UPDATE stock SET stock = (stock + ?) WHERE mp = ? and deposito = ? and lote = ?;""",(cantidad,mp,deposito,lote))       
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
            conexion.execute("""UPDATE stock SET stock = (stock + ?)  WHERE mp = ? and deposito = ? and lote = ?;""",(cantidad,mp,deposito,lote))       
            conexion.commit()                       
               
            if sector_macro == "Macro_Comasa":
                conexion.execute("""DELETE FROM %s WHERE id = ?;"""%sector_macro, (batch,))
                conexion.commit()
            else:
                conexion.execute("""DELETE FROM %s WHERE codprod = ? and ndebatch = ? and mp = ? and lote = ?;"""%sector_macro, (codprod,batch,mp,lote))
                conexion.commit()
            conexion.close()                                                                  
            cuadro_macro2.delete(elemento_seleccionado)            

def cerrar(ventana):
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

def nuevo(sec,cuadro2,cuadro,boton1,combobox,cuadro_macro2,cuadro_macro,boton_iniciar_macro,combobox_macro):
    global inicio
    global inicio_macro
    if(sec == "nucleos"):
        for s in cuadro2.get_children():
            cuadro2.delete(s)
        for s in cuadro.get_children():
            cuadro.delete(s)
        boton1["state"] = ["enable"]
        combobox["state"] = ["readonly"]
        
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
    return        

def actualizar(entrada_ruta_bd,cuadro_carga):
    
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    c = conexion.execute("""SELECT * FROM stock_nucleos WHERE estado = "completo";""" )  
    d = c.fetchall()   
    
    for s in cuadro_carga.get_children():
        cuadro_carga.delete(s)  
    for i in d:
        cuadro_carga.insert("", tk.END, text=i[2],
                    values=(i[1],i[0]))                
    conexion.close()  
    return
def cargar(combobox_carga,cuadro_carga,comentario_carga,entrada_ruta_bd,cuadro_carga2):
    if combobox_carga.get() == "":
        messagebox.showinfo(message="Seleccione una Formula", title="Error")
        return

    ndenucleo = cuadro_carga.item(cuadro_carga.selection())["text"]
    codnucleo= cuadro_carga.item(cuadro_carga.selection())["values"][1]    
    comentario = comentario_carga.get()
    fecha = time.strftime("%d/%m/%y")
    hora = time.strftime("%H:%M:%S")
    conexion=sqlite3.connect(entrada_ruta_bd.get())    
    c = conexion.execute("""SELECT codprod FROM producciones WHERE formula = ? and estado = "programado" and sector = ?;""" ,(combobox_carga.get(),reg_carga))  
    d = c.fetchall()  
    a = conexion.execute("""SELECT ndebatch FROM registro_carga WHERE codprod = ? ORDER BY ndebatch desc;""",(d[0][0],))
    b = a.fetchall() 
    if b == []:
        b = [[0]]
    conexion.execute("""insert into registro_carga (fecha,hora,codprod,ndebatch,ndenucleo,formula,sector, codnucleo, comentario)
                    VALUES(?,?,?,?,?,?,?,?,?);""" ,(fecha,hora,d[0][0],b[0][0]+1,ndenucleo,combobox_carga.get(),sector_carga,codnucleo,comentario))
    conexion.commit()
    conexion.execute("""UPDATE stock_nucleos SET estado = "utilizado" WHERE codprod = ? and ndebatch = ?;""" ,(codnucleo, ndenucleo))
    conexion.commit()
    cuadro_carga2.insert("", tk.END, text=fecha,
                    values=(hora,b[0][0]+1,ndenucleo,combobox_carga.get(),d[0][0], codnucleo)) 

    conexion.close()   
    actualizar(entrada_ruta_bd,cuadro_carga)
    return
def eliminar_carga(cuadro_carga2,entrada_ruta_bd,cuadro_carga):
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
    actualizar(entrada_ruta_bd,cuadro_carga)
    
def autenticar(entrada_contraseña,boton_pesar,deposito_selec,deposito_macro_selec,mp_selec,combobox_lote,boton_pesar_macro,mp_selec_macro,combobox_lote_macro,sele_sector,boton_ruta_bd,entrada_ruta_bd,entrada_puerto_grande,entrada_puerto_chico):
    if(entrada_contraseña.get()=="ntc25"):
        entrada_ruta_bd["state"] = ["enable"]        
        entrada_puerto_grande["state"] = ["enable"]
        entrada_puerto_chico["state"] = ["enable"]        
        boton_ruta_bd["state"] = ["normal"] 
        sele_sector["state"] = ["enable"]
        combobox_lote_macro["state"] = ["readonly"]
        mp_selec_macro["state"] = ["enable"]
        boton_pesar_macro["state"] = ["enable"]
        #cantidad_pesar_macro["state"] = ["enable"]
        combobox_lote["state"] = ["readonly"]
        mp_selec["state"] = ["enable"]
        boton_pesar["state"] = ["enable"]
        deposito_macro_selec["state"] = "readonly"
        deposito_selec["state"] = "readonly"
        #cantidad_pesar["state"] = ["enable"]
    else:
        messagebox.showinfo(message="Contraseña Incorrecta", title="Contraseña Incorrecta")

def autenticar_balanza(entrada_contraseña_bal,des_balanza_grande,desactivar_balanza_chica):
    if(entrada_contraseña_bal.get()=="nutri23"):
        des_balanza_grande["state"] = ["normal"]
        desactivar_balanza_chica["state"] = ["normal"]        
    else:
        messagebox.showinfo(message="Contraseña Incorrecta", title="Contraseña Incorrecta")

def deposito_seleccionado(sector,deposito_selec,entrada_ruta_bd,mp_selec,deposito_macro_selec,mp_selec_macro,e):    
    mp = []    
    if sector == "nucleos":  
        deposito = deposito_selec.get()      
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
       
def selec_lote(sector,mp_selec,combobox_lote_macro,mp_selec_macro,entrada_ruta_bd,combobox_lote,mostrar_stock,mostrar_stock_macro,e):
    
    if sector == "nucleos":
        lote = combobox_lote.get()
        mp = mp_selec.get()
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT stock FROM stock WHERE  mp = ? and lote = ? and estado = "liberado";""", (mp,lote))         
        b = a.fetchall()
        
        mostrar_stock.delete(0, tk.END)  
        mostrar_stock.insert(0,round(b[0][0],2))     
        
        conexion.close()
    if sector == "macro":
        lote = combobox_lote_macro.get()
        mp = mp_selec_macro.get()
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        
        a = conexion.execute("""SELECT stock FROM stock WHERE  mp = ? and lote = ? and estado = "liberado";""", (mp,lote))         
        b = a.fetchall()
        
        mostrar_stock_macro.delete(0, tk.END)  
        mostrar_stock_macro.insert(0,round(b[0][0],2)) 
         
        conexion.close()

def selec_materiaprima(sector,mp_selec,combobox_lote_macro,mp_selec_macro,entrada_ruta_bd,combobox_lote,e):
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

def ordenar(col,cuadro,cuadro_macro,cuadro2,cuadro_macro2):
    if col == "batch":
        elem = []
        elem_ordenado = []
        for t in cuadro.get_children():
            elem.append((cuadro.item(t)))       
        elem_ordenado = sorted(elem, key=lambda x: x["text"])        
        for s in cuadro.get_children():
            cuadro.delete(s)
        for s in elem_ordenado:
            cuadro.insert("", tk.END, text=s["text"], values=(s["values"]))
    if col == "batch_macro":
        elem = []
        elem_ordenado = []
        for t in cuadro_macro.get_children():
            elem.append((cuadro_macro.item(t)))       
        elem_ordenado = sorted(elem, key=lambda x: x["text"])        
        for s in cuadro_macro.get_children():
            cuadro_macro.delete(s)
        for s in elem_ordenado:
            cuadro_macro.insert("", tk.END, text=s["text"], values=(s["values"]))

    if col == "batch_reg":
        elem = []
        elem_ordenado = []
        for t in cuadro2.get_children():
            elem.append(cuadro2.item(t))       
        elem_ordenado = sorted(elem, key=lambda x: x["values"][1])        
        for s in cuadro2.get_children():
            cuadro2.delete(s)
        for s in elem_ordenado:
            cuadro2.insert("", tk.END, text=s["text"], values=(s["values"]))

    if col == "mp":
        elem = []
        elem_ordenado = []
        for t in cuadro.get_children():
            elem.append((cuadro.item(t)))
        elem_ordenado = sorted(elem, key=lambda x: x["values"][0])
        for s in cuadro.get_children():
            cuadro.delete(s)
        for s in elem_ordenado:
            cuadro.insert("", tk.END, text=s["text"], values=(s["values"]))

    if col == "mp_reg":
        elem = []
        elem_ordenado = []
        for t in cuadro2.get_children():
            elem.append((cuadro2.item(t)))
        elem_ordenado = sorted(elem, key=lambda x: x["values"][2])
        for s in cuadro2.get_children():
            cuadro2.delete(s)
        for s in elem_ordenado:
            cuadro2.insert("", tk.END, text=s["text"], values=(s["values"]))
        
    if col == "mp_macro_reg":
        elem = []
        elem_ordenado = []
        for t in cuadro_macro2.get_children():
            elem.append((cuadro_macro2.item(t)))
        elem_ordenado = sorted(elem, key=lambda x: x["values"][2])
        for s in cuadro_macro2.get_children():
            cuadro_macro2.delete(s)
        for s in elem_ordenado:
            cuadro_macro2.insert("", tk.END, text=s["text"], values=(s["values"]))
    
    if col == "mp_macro":
        elem = []
        elem_ordenado = []
        for t in cuadro_macro.get_children():
            elem.append((cuadro_macro.item(t)))
        elem_ordenado = sorted(elem, key=lambda x: x["values"][0])
        for s in cuadro_macro.get_children():
            cuadro_macro.delete(s)
        for s in elem_ordenado:
            cuadro_macro.insert("", tk.END, text=s["text"], values=(s["values"]))        
        
    if col == "batch_reg_macro":
        elem = []
        elem_ordenado = []
        for t in cuadro_macro2.get_children():
            elem.append(cuadro_macro2.item(t))       
        elem_ordenado = sorted(elem, key=lambda x: x["values"][1])        
        for s in cuadro_macro2.get_children():
            cuadro_macro2.delete(s)
        for s in elem_ordenado:
            cuadro_macro2.insert("", tk.END, text=s["text"], values=(s["values"]))     


