import tkinter as tk
from tkinter import *
from tkinter import ttk,messagebox, filedialog
import sqlite3
from datetime import datetime, timedelta
from csv import reader, writer
from reportlab.pdfgen import canvas
from functools import partial
import Leer_archivo as la 
import csv
ruta_txt = "/archnucl"
import sys
import time
sector = ""
dic_res_stock = {}
copia = 0
ancho1 = 30
ancho2 = 20
sep = 0.25
sep2 = 0.37
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
        a = conexion.execute("""SELECT DISTINCT mp FROM recepcion;""")
        b = a.fetchall()
        mp['values'] = list(b)
        entrada_mp_corr['values'] = list(b)
        a = conexion.execute("""SELECT DISTINCT fecha FROM recepcion;""")
        fecha['values'] = list(a)
        a = conexion.execute("""SELECT DISTINCT nderemito FROM recepcion;""") 
        nderemito['values'] = list(a)
        a = conexion.execute("""SELECT DISTINCT lote FROM recepcion;""") 
        lote['values'] = list(a)
        a = conexion.execute("""SELECT DISTINCT proveedor FROM recepcion;""") 
        proveedor['values'] = list(a)  
        a = conexion.execute("""SELECT DISTINCT deposito FROM recepcion;""") 
        entrada_dep_corr['values'] = list(a) 
        a = conexion.execute("""SELECT * FROM stock WHERE stock != ? and estado != ?;""",(0,"retenido")) 
        b = a.fetchall()         
        
        for i in b:            
            if datetime.strptime(str(i[5]), "%Y-%m-%d") < datetime.strptime(str(datetime.now().date() + timedelta(7)),"%Y-%m-%d"):
                
                boton_vencimiento.config(bg="red")
                break
            elif datetime.strptime(str(i[5]), "%Y-%m-%d") < datetime.strptime(str(datetime.now().date() + timedelta(30)),"%Y-%m-%d"):
                boton_vencimiento.config(bg="yellow")
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
     
def buscar(r,e):    
    if r == "fecha":
        b = fecha.get()
    if r == "nderemito":
        b = nderemito.get()            
    elif r == "mp":
        b = mp.get()
    elif r == "lote":
        b = lote.get()
    elif r == "proveedor":
        b = proveedor.get()
    elif r == "protocolo":
        b = protocolo.get()   
    elif r == "id":
        b = e    
    elif r == "estado":
        b = estado.get()
    for s in cuadro.get_children():
            cuadro.delete(s)
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    a = conexion.execute("""SELECT * FROM recepcion WHERE %s = ?;""" %r, (b,))         
    b = a.fetchall()  
    for i in b:
        cuadro.insert("", tk.END, text=i[0],
                            values=(i[1],i[2],i[3],i[5],i[6],i[7],i[8],i[9],i[10],i[11],i[13],i[14],i[15],i[16],i[17],i[18],i[19],i[20],i[12],i[4], i[21],i[22],i[23],i[24],i[25],i[26],i[27],i[28],i[30],i[29],i[31],i[32]))
    conexion.close()

def liberar():
    id = cuadro.item(cuadro.selection())["text"]
    mp = cuadro.item(cuadro.selection())["values"][1]
    deposito = cuadro.item(cuadro.selection())["values"][5]
    lote = cuadro.item(cuadro.selection())["values"][2]
    respon = entrada_responsable.get()
    cantidad = cuadro.item(cuadro.selection())["values"][4]
    vto = cuadro.item(cuadro.selection())["values"][3]
    estado = cuadro.item(cuadro.selection())["values"][29]
    
    if respon == "":
        messagebox.showinfo(message="Ingrese Responsable", title="Error")
        return   
    if estado != "pendiente":
        messagebox.showinfo(message="Esta MP ya esta Liberada", title="Error")
        return   
    try:
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        conexion.execute("""UPDATE recepcion SET estado = "liberado" , responsablecalidad = ? WHERE id = ?;""",(respon, id))
        conexion.commit()
        a = conexion.execute("""SELECT * FROM stock WHERE mp = ? and lote = ?;""",(mp, lote))
        b = a.fetchone()                
        if b == None:
            conexion.execute("""insert into stock (mp,deposito,lote,stock,stocksim,vto,estado)
            VALUES(?,?,?,?,?,?,?);""",(mp,deposito,lote,float(cantidad),float(cantidad),vto,"liberado"))
            conexion.commit()         
        else:                  
            stock = (float(b[3])) + float(cantidad)
            stocksim = (float(b[4])) + float(cantidad) 
            conexion.execute("""UPDATE stock SET stock = ?,stocksim = ?, estado = "liberado"  WHERE mp = ? and lote = ? and deposito = ?;""",(stock,stocksim,mp,lote,deposito))
            conexion.commit()     
        conexion.close()     
        lista = cuadro.item(cuadro.selection())["values"]
        lista[29]="liberado"
        lista[20]=str(entrada_responsable.get())
        cuadro.item(cuadro.selection(),values=lista)
    except:
        messagebox.showinfo(message="Error al Conectar BD", title="Error")
        conexion.close()
        return

def verificar():
    id = cuadro.item(cuadro.selection())["text"]
    respon = entrada_responsable.get()
    estado = cuadro.item(cuadro.selection())["values"][29]
    if respon == "":
        messagebox.showinfo(message="Ingrese Responsable", title="Error")
        return   
    if estado == "pendiente":
        messagebox.showinfo(message="Esta MP no esta Liberada", title="Error")
        return   
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    conexion.execute("""UPDATE recepcion SET estado = "verificado", resver = ? WHERE id = ?;""",(respon,id))
    conexion.commit()
    conexion.close()     
    lista = cuadro.item(cuadro.selection())["values"]
    lista[30]=str(entrada_responsable.get())
    lista[29]="verificado"
    cuadro.item(cuadro.selection(),values=lista)

def cargar():
    id = cuadro.item(cuadro.selection())["text"]
    if id != "":
        lista = [entrada_pro.get(),entrada_fechaelb.get(),entrada_responsable.get(),entrada_revision.get(),entrada_rotulo.get(),entrada_organ.get(),entrada_fisic.get(),entrada_confis.get(),
                entrada_conqui.get(),entrada_micro.get(),entrada_otros.get()]
        lista2 = ["protocolo","fechaelaboracion","responsablecalidad","etrevision","rotulo","organolep","fisicoqui","contfisico","contquimico","contmicro","otros"]
        
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        e = 0        
        for i in lista2:           
            if lista[e] != "":                
                conexion.execute("""UPDATE recepcion SET %s = ? WHERE id = ?;""" %i,(lista[e],id))
                conexion.commit()
            e = e + 1
        conexion.close()   
        lista3 = cuadro.item(cuadro.selection())["values"]
        e = 18
        for i in lista:           
            if i!= "":
               lista3[e]=i 
            e = e + 1                   
        cuadro.item(cuadro.selection(),values=lista3)         
    else:
        messagebox.showinfo(message="Seleccione un Elemento", title="Error")        

def exportar():       
    global copia
    ruta = entrada_ruta_registro.get()
    with open(ruta + "/" + "reporte" + str(copia) +".csv", 'w', newline='') as f:       
        writer = csv.writer(f,delimiter=';') 
        guardar = ["Fecha","MP","Lote","Fecha de Elaboracion","Vto","Cantidad", "Deposito", "N° de Remito","Presentacion" ,"Marca","Proveedor","Protocolo","Chofer","Transporte","Patente","Habilitacion","Estado del Transporte","Estado de Carga","Observacion","Responsable Deposito","Responsable Calidad","ET Revision","Rotulo","Caracteristicas Organolepticas", "Fisicoquimicas","Contaminantes Fisicos","Contaminantes Quimicos","Contaminantes Micro", "Estado","Otros Datos","Responsable Verificacion","Correccion"]
        writer.writerow(guardar)        
        for i in cuadro.get_children():
            guardar.clear()                   
            for t in cuadro.item(i)["values"]:
                guardar.append(t)
            writer.writerow(guardar)    
        copia +=1
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

def eliminar():
    estado = cuadro.item(cuadro.selection())["values"][29]
    fecha = time.strftime("%d/%m/%y")
    hora = time.strftime("%H:%M:%S")
    if estado == "pendiente":
        id = cuadro.item(cuadro.selection())["text"]
        mp = cuadro.item(cuadro.selection())["values"][1]
        deposito = cuadro.item(cuadro.selection())["values"][6]
        lote = cuadro.item(cuadro.selection())["values"][2]
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        conexion.execute("""DELETE FROM recepcion WHERE id = ?;""",(id,))
        conexion.commit()
        ##conexion.execute("""DELETE FROM stock WHERE mp = ? and deposito = ? and lote = ?;""",(mp,deposito,lote))
        #conexion.commit()          
        cuadro.delete(cuadro.selection())   
        conexion.execute("""insert into registro_cambios (fecha,hora,mp,lote,deposito,stockant,stocksim,nuevostock,responsable, programa)
                    VALUES(?,?,?,?,?,?,?,?,?,?);""",(fecha,hora, mp, lote,deposito,stockant,stocksim,nuevo_stock,respon, "stock"))
        conexion.commit()
        conexion.close()
    else:
        messagebox.showinfo(message="No se puede Eliminar porque ya esta Liberado", title="Error")

def retener():
    id = cuadro.item(cuadro.selection())["text"]
    respon = entrada_responsable.get()
    if respon == "":
        messagebox.showinfo(message="Ingrese Responsable", title="Error")
        return   
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    conexion.execute("""UPDATE recepcion SET estado = "retenido", resver = ? WHERE id = ?;""",(respon,id))
    conexion.commit()
    a = conexion.execute("""SELECT * FROM recepcion WHERE id = ?;""",(id,))
    b = a.fetchall()
    conexion.execute("""UPDATE stock SET estado = "retenido" WHERE mp = ? and lote = ?;""",(b[0][2],b[0][3]))
    conexion.commit()
    conexion.close()     
    lista = cuadro.item(cuadro.selection())["values"]
    lista[29]="retener"
    lista[20]=str(entrada_responsable.get())
    cuadro.item(cuadro.selection(),values=lista)

def revalidar():
    id = cuadro.item(cuadro.selection())["text"]
    rev = entrada_revalida.get()
    if len(rev)==10:
        dia = rev[0:2]
        mes = rev[3:5]
        año = rev[6:10]        
        rev = (año) + "-" + (mes) + "-" + (dia)                  
        try:            
            datetime.strptime(rev, "%Y-%m-%d")            
        except:            
            messagebox.showinfo(message="Error en Fecha de Vto", title="Error de Fecha")
            return    
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        conexion.execute("""UPDATE recepcion SET vto = ? WHERE id = ?;""",(rev +" revalidado",id))
        conexion.commit()
        a = conexion.execute("""SELECT * FROM recepcion WHERE id = ?;""",(id,))
        b = a.fetchall()
        conexion.execute("""UPDATE stock SET vto = ?, estado = "liberado" WHERE mp = ? and lote = ?;""",(rev,b[0][2],b[0][3]))
        conexion.commit()
        conexion.close()     
        lista = cuadro.item(cuadro.selection())["values"]
        lista[29]=str(rev +" revalidado")
        lista[20]=str(entrada_responsable.get())
        cuadro.item(cuadro.selection(),values=lista) 
    else:
        messagebox.showinfo(message="Error en Fecha de Vto", title="Error de Fecha")
        return    


def validar_entrada(numero):        
    try:
        int(numero)
        return True
    except:
        if numero == "-":
            return True
        else:
            return False

def busqueda_mp(letra):
    for s in cuadro.get_children():
            cuadro.delete(s)
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    a = conexion.execute("""SELECT * FROM recepcion;""")
    b = a.fetchall() 
    for i in b:
        if mp.get() in str(i[2]).lower():
            if datetime.strptime(str(i[5][0:10]), "%Y-%m-%d") < datetime.strptime(str(datetime.now().date()),"%Y-%m-%d"):
                cuadro.insert("", tk.END, text=i[0],tags=i[0],
                            values=(i[1],i[2],i[3],i[5],i[6],i[7],i[8],i[9],i[10],i[11],i[13],i[14],i[15],i[16],i[17],i[18],i[19],i[20],i[12],i[4], i[21],i[22],i[23],i[24],i[25],i[26],i[27],i[28],i[30],i[29],i[31],i[32]))
                cuadro.tag_configure(i[0],background = 'red')
            else:
                cuadro.insert("", tk.END, text=i[0],tags=i[0],
                            values=(i[1],i[2],i[3],i[5],i[6],i[7],i[8],i[9],i[10],i[11],i[13],i[14],i[15],i[16],i[17],i[18],i[19],i[20],i[12],i[4], i[21],i[22],i[23],i[24],i[25],i[26],i[27],i[28],i[30],i[29],i[31],i[32]))
    conexion.close()
    return True

def busqueda_lote(letra):
    for s in cuadro.get_children():
            cuadro.delete(s)
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    a = conexion.execute("""SELECT * FROM recepcion;""")
    b = a.fetchall() 
    for i in b:
        if lote.get() in str(i[3]).lower():
            if datetime.strptime(str(i[5][0:10]), "%Y-%m-%d") < datetime.strptime(str(datetime.now().date()),"%Y-%m-%d"):
                cuadro.insert("", tk.END, text=i[0],tags=i[0],
                            values=(i[1],i[2],i[3],i[5],i[6],i[7],i[8],i[9],i[10],i[11],i[13],i[14],i[15],i[16],i[17],i[18],i[19],i[20],i[12],i[4], i[21],i[22],i[23],i[24],i[25],i[26],i[27],i[28],i[30],i[29],i[31],i[32]))
                cuadro.tag_configure(i[0],background = 'red')
            else:
                cuadro.insert("", tk.END, text=i[0],tags=i[0],
                            values=(i[1],i[2],i[3],i[5],i[6],i[7],i[8],i[9],i[10],i[11],i[13],i[14],i[15],i[16],i[17],i[18],i[19],i[20],i[12],i[4], i[21],i[22],i[23],i[24],i[25],i[26],i[27],i[28],i[30],i[29],i[31],i[32]))
                conexion.close()
    return True

def busqueda_remito(letra):
    for s in cuadro.get_children():
            cuadro.delete(s)
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    a = conexion.execute("""SELECT * FROM recepcion;""")
    b = a.fetchall() 
    for i in b:
        if nderemito.get() in str(i[8]).lower():
            if datetime.strptime(str(i[5][0:10]), "%Y-%m-%d") < datetime.strptime(str(datetime.now().date()),"%Y-%m-%d"):
                cuadro.insert("", tk.END, text=i[0],tags=i[0],
                            values=(i[1],i[2],i[3],i[5],i[6],i[7],i[8],i[9],i[10],i[11],i[13],i[14],i[15],i[16],i[17],i[18],i[19],i[20],i[12],i[4], i[21],i[22],i[23],i[24],i[25],i[26],i[27],i[28],i[30],i[29],i[31],i[32]))
                cuadro.tag_configure(i[0],background = 'red')
            else:
                cuadro.insert("", tk.END, text=i[0],tags=i[0],
                            values=(i[1],i[2],i[3],i[5],i[6],i[7],i[8],i[9],i[10],i[11],i[13],i[14],i[15],i[16],i[17],i[18],i[19],i[20],i[12],i[4], i[21],i[22],i[23],i[24],i[25],i[26],i[27],i[28],i[30],i[29],i[31],i[32]))                    
    conexion.close()
    return True

def vencimiento():
    for s in cuadro.get_children():
            cuadro.delete(s)
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    a = conexion.execute("""SELECT * FROM stock WHERE stock != ? and estado != ?;""",(0,"retenido")) 
    b = a.fetchall()        
    for e in b:                    
        if datetime.strptime(str(e[5]), "%Y-%m-%d") < datetime.strptime(str(datetime.now().date() + timedelta(30)),"%Y-%m-%d"):
            c = conexion.execute("""SELECT * FROM recepcion WHERE mp = ? and lote = ?;""",(str(e[0]), str(e[2])))
            d = c.fetchall()             
            for i in d:   
                if datetime.strptime(str(e[5]), "%Y-%m-%d") < datetime.strptime(str(datetime.now().date() + timedelta(7)),"%Y-%m-%d"):
                    cuadro.insert("", tk.END, text=i[0], tags=i[0],
                            values=(i[1],i[2],i[3],i[5],i[6],i[7],i[8],i[9],i[10],i[11],i[13],i[14],i[15],i[16],i[17],i[18],i[19],i[20],i[12],i[4], i[21],i[22],i[23],i[24],i[25],i[26],i[27],i[28],i[30],i[29],i[31]))
                    cuadro.tag_configure(i[0],background = 'red')
                else:
                    cuadro.insert("", tk.END, text=i[0], tags=i[0],
                            values=(i[1],i[2],i[3],i[5],i[6],i[7],i[8],i[9],i[10],i[11],i[13],i[14],i[15],i[16],i[17],i[18],i[19],i[20],i[12],i[4], i[21],i[22],i[23],i[24],i[25],i[26],i[27],i[28],i[30],i[29],i[31]))
    conexion.close()

def correccion():
    estado = cuadro.item(cuadro.selection())["values"][29]

    if estado == "pendiente":
        messagebox.showinfo(message="Esta MP no esta Liberada", title="Error")
        return 
    id = cuadro.item(cuadro.selection())["text"]
    mp = cuadro.item(cuadro.selection())["values"][1]
    deposito = cuadro.item(cuadro.selection())["values"][5]
    lote = cuadro.item(cuadro.selection())["values"][2]    
    cantidad = cuadro.item(cuadro.selection())["values"][4]
    vto = cuadro.item(cuadro.selection())["values"][3]
    fecha = cuadro.item(cuadro.selection())["values"][0]
    remito = cuadro.item(cuadro.selection())["values"][6]
    mpc = entrada_mp_corr.get()
    depositoc = entrada_dep_corr.get()
    lotec = entrada_lote_corr.get()
    cantidadc = entrada_cantidad_corr.get()
    vtoc = entrada_vto_corr.get()
    fechac = entrada_fecha_corr.get()
    remitoc = entrada_remito_corr.get()
    
    correccion = []
    original = []
    lista = []
    corr = ""
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    lista2 = cuadro.item(cuadro.selection())["values"]   
    if fechac!="":   
        lista2[0] = fechac
        conexion.execute("""UPDATE recepcion SET fecha = ? WHERE id = ?;""" ,(fechac,id))
        conexion.commit()
        original.append(fecha)
        correccion.append(fechac)
        lista.append("Fecha")
    else:
        fechac = fecha    
    if mpc!="":          
        lista2[1] = mpc
        conexion.execute("""UPDATE recepcion SET mp = ? WHERE id = ?;""" ,(mpc,id))
        conexion.commit()
        original.append(mp)
        correccion.append(mpc)
        lista.append("MP")
    else:
        mpc = mp
    if lotec!="":      
        lista2[2] = lotec    
        conexion.execute("""UPDATE recepcion SET lote = ? WHERE id = ?;""" ,(lotec,id))
        conexion.commit()
        original.append(lote)
        correccion.append(lotec)
        lista.append("Lote")
    else:
        lotec = lote
    if vtoc!="":  
        lista2[3] = vtoc 
        if len(vtoc)==10:
            dia = vtoc[0:2]
            mes = vtoc[3:5]
            año = vtoc[6:10]        
            rev = (año) + "-" + (mes) + "-" + (dia)                  
            try:            
                datetime.strptime(rev, "%Y-%m-%d")            
            except:            
                messagebox.showinfo(message="Error en Fecha de Vto", title="Error de Fecha")
                return           
        conexion.execute("""UPDATE recepcion SET vto = ? WHERE id = ?;""" ,(rev,id))
        conexion.commit()
        original.append(vto)
        correccion.append(rev)
        lista.append("Vto")
    else:
        vtoc = vto
    if cantidadc!="":          
        lista2[4] = cantidadc
        conexion.execute("""UPDATE recepcion SET cantidad = ? WHERE id = ?;""" ,(cantidadc,id))
        conexion.commit()
        original.append(cantidad)
        correccion.append(cantidadc)
        lista.append("Cantidad")
    else:
        cantidadc = cantidad
    if depositoc!="":        
        lista2[5] = depositoc
        conexion.execute("""UPDATE recepcion SET deposito = ? WHERE id = ?;""" ,(depositoc,id))
        conexion.commit()
        original.append(deposito)
        correccion.append(depositoc)
        lista.append("Deposito")
    else:
        depositoc = deposito

    if remitoc!="":    
        lista2[6] = remitoc          
        conexion.execute("""UPDATE recepcion SET nderemito = ? WHERE id = ?;""" ,(remitoc,id))
        conexion.commit()
        original.append(remito)
        correccion.append(remitoc)
        lista.append("Remito")
    else:
        remitoc = remito
    
    f = 0    
 
    corr = ""
    for i in original:        
        corr = corr + " Cambio" + " " + lista[f] +" "+ str(i) +" "+ " por " + correccion[f]
        f+=1
 
    a = conexion.execute("""SELECT correccion FROM recepcion where id = ?;""",(id,))
    b = a.fetchall()
    if b[0][0]!= None:
        conexion.execute("""UPDATE recepcion SET correccion = ? WHERE id = ?;""" ,((corr+b[0][0]),id))
        conexion.commit()
    else:
        conexion.execute("""UPDATE recepcion SET correccion = ? WHERE id = ?;""" ,((corr),id))
        conexion.commit()
    conexion.close()   
    
      
    try:
        conexion=sqlite3.connect(entrada_ruta_bd.get())        
        a = conexion.execute("""SELECT * FROM stock WHERE mp = ? and lote = ?;""",(mpc, lotec))
        b = a.fetchone()                
        if b == None:
            conexion.execute("""insert into stock (mp,deposito,lote,stock,stocksim,vto,estado)
            VALUES(?,?,?,?,?,?,?);""",(mpc,depositoc,lotec,float(cantidadc),float(cantidadc),vtoc,"liberado"))
            conexion.commit()         
        else:                  
            stock = (float(b[3])) + float(cantidadc)
            stocksim = (float(b[4])) + float(cantidadc) 
            conexion.execute("""UPDATE stock SET stock = ?,stocksim = ?, estado = "liberado"  WHERE mp = ? and lote = ? and deposito = ?;""",(stock,stocksim,mpc,lotec,depositoc))
            conexion.commit()     
        conexion.close()     
        cuadro.item(cuadro.selection(),values=lista2)
    except:
        messagebox.showinfo(message="Error al Conectar BD", title="Error")
        conexion.close()
        return


def validar_entrada_cantidad(numero):        
    try:
        int(numero)
        if len(entrada_cantidad_corr.get()) == 0:
            if int(numero) == 0:
                return False
            else:
                return True        
        else:
            return True
    except:
        if numero == ".":
            return True
        else:
            return False   

def validar_entrada_lote(numero):
    if len(numero) == 1:
        try:
            if numero == " " or numero == "/":
                return False
            if len(entrada_lote_corr.get()) == 0:
                if int(numero) == 0:
                    return False
                else:
                    return True
            return True
        except:
            return True   
    else:
        return False

        
ventana = Tk()
ventana.protocol("WM_DELETE_WINDOW", cerrar)
ventana.geometry("1500x800")
ventana.title("Calidad")
tab_control = ttk.Notebook(ventana, width=1000, height=650)
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
boton_ruta_bd = ttk.Button(pestaña_config, text="Config. Ruta", command=lambda: selecionar_ruta("bd"))
boton_ruta_bd.place(relx=0.8, rely=0.14)

label_fecha = ttk.Label(pestaña_prod, text="Fecha")
label_fecha.place(relx=0.005, rely=0.01)
label_mp = ttk.Label(pestaña_prod, text="Materia Prima")
label_mp.place(relx=0.005, rely=0.08)
label_nremito = ttk.Label(pestaña_prod, text="N° de Remito")
label_nremito.place(relx=0.005, rely=0.15)
label_lote = ttk.Label(pestaña_prod, text="Lote")
label_lote.place(relx=0.005, rely=0.22)
label_prov = ttk.Label(pestaña_prod, text="Proveedor")
label_prov.place(relx=0.005, rely=0.29)
label_protocolo = ttk.Label(pestaña_prod, text="Protocolo")
label_protocolo.place(relx=0.005, rely=0.36)
label_fechaelab = ttk.Label(pestaña_prod, text="Fecha de Elaboracion")
label_fechaelab.place(relx=sep, rely=0.01)
label_revision = ttk.Label(pestaña_prod, text="ET/Revision")
label_revision.place(relx=sep, rely=0.06)
label_rotulo = ttk.Label(pestaña_prod, text="Rotulo")
label_rotulo.place(relx=sep, rely=0.11)
label_organ = ttk.Label(pestaña_prod, text="Carcateristias Organolepticas")
label_organ.place(relx=sep, rely=0.16)
label_fisic = ttk.Label(pestaña_prod, text="Carcateristias Fisicas")
label_fisic.place(relx=sep, rely=0.21)
label_confis = ttk.Label(pestaña_prod, text="Contaminaantes Fisicos")
label_confis.place(relx=sep, rely=0.26)
label_conqui = ttk.Label(pestaña_prod, text="Contamientes Quimicos")
label_conqui.place(relx=sep, rely=0.31)
label_conmicro = ttk.Label(pestaña_prod, text="Contamientes Microbiologicos")
label_conmicro.place(relx=sep, rely=0.36)
label_responsable = ttk.Label(pestaña_prod, text="Responsable")
label_responsable.place(relx=sep, rely=0.41)
label_otros = ttk.Label(pestaña_prod, text="Otros Datos")
label_otros.place(relx=0.47, rely=0.01)
entrada_otros= ttk.Entry(pestaña_prod, width=20)
entrada_otros.place(relx=0.47, rely=0.04,height=60)
label_revalida = ttk.Label(pestaña_prod, text="Vto.Revalida")
label_revalida.place(relx=0.85, rely=0.2)
label_pro = ttk.Label(pestaña_prod, text="Protocolo")
label_pro.place(relx=sep, rely=0.46)

#Todos estos son para correccion
label_fecha_corr = ttk.Label(pestaña_prod, text="Fecha")
label_fecha_corr.place(relx=0.57, rely=0.01)
label_mp_corr = ttk.Label(pestaña_prod, text="Materia Prima")
label_mp_corr.place(relx=0.57, rely=0.08)
label_nremito_corr = ttk.Label(pestaña_prod, text="N° de Remito")
label_nremito_corr.place(relx=0.57, rely=0.15)
label_lote_corr = ttk.Label(pestaña_prod, text="Lote")
label_lote_corr.place(relx=0.57, rely=0.22)
label_prov_corr = ttk.Label(pestaña_prod, text="Deposito")
label_prov_corr.place(relx=0.57, rely=0.29)
label_protocolo_corr = ttk.Label(pestaña_prod, text="Cantidad")
label_protocolo_corr.place(relx=0.57, rely=0.36)
label_protocolo_corr = ttk.Label(pestaña_prod, text="Vencimiento")
label_protocolo_corr.place(relx=0.57, rely=0.43)

entrada_fecha_corr= ttk.Entry(pestaña_prod, width=ancho2)
entrada_fecha_corr.place(relx=0.63, rely=0.01)
entrada_mp_corr = ttk.Combobox(pestaña_prod, width=ancho2)
entrada_mp_corr.place(relx=0.63, rely=0.08)
entrada_remito_corr = ttk.Entry(pestaña_prod, width=ancho2)
entrada_remito_corr.place(relx=0.63, rely=0.15)
entrada_lote_corr = ttk.Entry(pestaña_prod, width=ancho2,validate="key",validatecommand=((pestaña_prod.register(validar_entrada_lote)),"%S"))
entrada_lote_corr.place(relx=0.63, rely=0.22)
entrada_dep_corr = ttk.Combobox(pestaña_prod, width=ancho2)
entrada_dep_corr.place(relx=0.63, rely=0.29)
entrada_cantidad_corr = ttk.Entry(pestaña_prod, width=ancho2,validate="key",validatecommand=((pestaña_prod.register(validar_entrada_cantidad)),"%S"))
entrada_cantidad_corr.place(relx=0.63, rely=0.36)
entrada_vto_corr = ttk.Entry(pestaña_prod, width=ancho2,validate="key",validatecommand=((pestaña_prod.register(validar_entrada)),"%S"))
entrada_vto_corr.place(relx=0.63, rely=0.43)


entrada_revalida= ttk.Entry(pestaña_prod, width=ancho2,validate="key",validatecommand=((pestaña_prod.register(validar_entrada)),"%S"))
entrada_revalida.place(relx=0.9, rely=0.2)
entrada_fechaelb= ttk.Entry(pestaña_prod, width=ancho2)
entrada_fechaelb.place(relx=sep2, rely=0.01)
entrada_revision = ttk.Entry(pestaña_prod, width=ancho2)
entrada_revision.place(relx=sep2, rely=0.06)
entrada_rotulo = ttk.Entry(pestaña_prod, width=ancho2)
entrada_rotulo.place(relx=sep2, rely=0.11)
entrada_organ = ttk.Entry(pestaña_prod, width=ancho2)
entrada_organ.place(relx=sep2, rely=0.16)
entrada_fisic = ttk.Entry(pestaña_prod, width=ancho2)
entrada_fisic.place(relx=sep2, rely=0.21)
entrada_confis = ttk.Entry(pestaña_prod, width=ancho2)
entrada_confis.place(relx=sep2, rely=0.26)
entrada_conqui = ttk.Entry(pestaña_prod, width=ancho2)
entrada_conqui.place(relx=sep2, rely=0.31)
entrada_micro = ttk.Entry(pestaña_prod, width=ancho2)
entrada_micro.place(relx=sep2, rely=0.36)
entrada_pro = ttk.Combobox(pestaña_prod,state="readonly",values=["Falta_Protocolo","Papel", "Digital"])
entrada_pro.place(relx=sep2, rely=0.46)
entrada_responsable = ttk.Entry(pestaña_prod, width=ancho2)
entrada_responsable.place(relx=sep2, rely=0.41)

fecha = ttk.Combobox(pestaña_prod, width=ancho1, state="readonly")
fecha.place(relx=0.07, y=10)
fecha.bind("<<ComboboxSelected>>", partial(buscar,"fecha"))
mp = ttk.Combobox(pestaña_prod, width=ancho1)
mp.place(relx=0.07, rely=0.08)
mp.bind("<<ComboboxSelected>>", partial(buscar,"mp"))
mp.bind("<Return>", partial(busqueda_mp))
nderemito = ttk.Combobox(pestaña_prod, width=ancho1)
nderemito.place(relx=0.07, rely=0.15)
nderemito.bind("<<ComboboxSelected>>", partial(buscar,"nderemito"))
nderemito.bind("<Return>", partial(busqueda_remito))
lote = ttk.Combobox(pestaña_prod, width=ancho1)
lote.place(relx=0.07, rely=0.22)
lote.bind("<<ComboboxSelected>>", partial(buscar,"lote"))
lote.bind("<Return>", partial(busqueda_lote))
proveedor = ttk.Combobox(pestaña_prod, width=ancho1,state="readonly")
proveedor.place(relx=0.07, rely=0.29)
proveedor.bind("<<ComboboxSelected>>", partial(buscar,"proveedor"))
protocolo = ttk.Combobox(pestaña_prod, width=ancho1,state="readonly",values=["Falta_Protocolo","Papel", "Digital"])
protocolo.place(relx=0.07, rely=0.36)
protocolo.bind("<<ComboboxSelected>>", partial(buscar,"protocolo"))
estado = ttk.Combobox(pestaña_prod, width=ancho1,state="readonly" ,values=["pendiente","liberado","verificado","retenido"])
estado.place(relx=0.07, rely=0.42)
estado.bind("<<ComboboxSelected>>", partial(buscar,"estado"))
label_estado = ttk.Label(pestaña_prod, text="Estado")
label_estado.place(relx=0.005, rely=0.42)

cuadro = ttk.Treeview(pestaña_prod, columns=("Fecha","MP","Lote","Vto","Cantidad", "Deposito", "N° de Remito","Presentacion" , "Marca","Proveedor","Chofer","Transporte","Patente","Habilitacion","Estado del Transporte","Estado de Carga","Observacion","Responsable Deposito","Protocolo","Fecha de Elaboracion","Responsable Calidad","ET Revision","Rotulo","Caracteristicas Organolepticas", "Fisicoquimicas","Contaminantes Fisicos","Contaminantes Quimicos","Contaminantes Micro","Otros", "Estado","Responsable Verificacion","Correccion"))
cuadro.column("#0",anchor="center",minwidth=50,width=50,stretch=NO)
cuadro.column("Fecha",anchor="center",minwidth=70,width=70,stretch=NO)
cuadro.column("MP", anchor="center",minwidth=200,width=200,stretch=NO)
cuadro.column("Lote", anchor="center",minwidth=90,width=90,stretch=NO)

cuadro.column("Vto", anchor="center",minwidth=70,width=70,stretch=NO)
cuadro.column("Cantidad",anchor="center",minwidth=50,width=50,stretch=NO)
cuadro.column("Deposito",anchor="center",minwidth=80,width=80,stretch=NO)
cuadro.column("N° de Remito", anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.column("Presentacion",  anchor="center",minwidth=100,width=100,stretch=NO)
cuadro.column("Marca", anchor="center",minwidth=90,width=90,stretch=NO)
cuadro.column("Proveedor", anchor="center",minwidth=90,width=90,stretch=NO)

cuadro.column("Chofer", anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.column("Transporte",  anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.column("Patente", anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.column("Habilitacion",  anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.column("Estado del Transporte",  anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.column("Estado de Carga" ,anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.column("Observacion",  anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.column("Responsable Deposito",  anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.column("Protocolo", anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.column("Fecha de Elaboracion", anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.column("Responsable Calidad",  anchor="center",minwidth=120,width=120,stretch=NO)

cuadro.column("ET Revision",anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.column("Rotulo",anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.column("Caracteristicas Organolepticas", anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.column("Fisicoquimicas",  anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.column("Contaminantes Fisicos", anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.column("Contaminantes Quimicos", anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.column("Contaminantes Micro",  anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.column("Otros", anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.column("Estado", anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.column("Responsable Verificacion", anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.column("Correccion", anchor="center",minwidth=120,width=120,stretch=NO)
cuadro.heading("#0", text="Id")
cuadro.heading("Fecha", text="Fecha")
cuadro.heading("MP", text="MP")
cuadro.heading("Lote", text="Lote")

cuadro.heading("Vto", text="Vto")
cuadro.heading("Cantidad", text="Cantidad")
cuadro.heading("Deposito", text="Deposito")
cuadro.heading("N° de Remito", text="N° de Remito")
cuadro.heading("Presentacion", text="Presentacion")
cuadro.heading("Marca", text="Marca")
cuadro.heading("Proveedor", text="Proveedor")

cuadro.heading("Chofer", text="Chofer")
cuadro.heading("Transporte", text="Transporte")
cuadro.heading("Patente", text="Patente")
cuadro.heading("Habilitacion", text="Habilitacion")
cuadro.heading("Estado del Transporte", text="Estado del Transporte")
cuadro.heading("Estado de Carga", text="Estado de Carga")
cuadro.heading("Observacion", text="Observacion")
cuadro.heading("Responsable Deposito", text="Responsable Deposito")
cuadro.heading("Protocolo", text="Protocolo")
cuadro.heading("Fecha de Elaboracion", text="Fecha de Elaboracion")
cuadro.heading("Responsable Calidad", text="Responsable Calidad")
cuadro.heading("ET Revision", text="ET Revision")
cuadro.heading("Rotulo", text="Rotulo")
cuadro.heading("Caracteristicas Organolepticas", text="Caracteristicas Organolepticas")
cuadro.heading("Fisicoquimicas", text="Fisicoquimicas")
cuadro.heading("Contaminantes Fisicos", text="Contaminantes Fisicos")
cuadro.heading("Contaminantes Quimicos", text="Contaminantes Quimicos")
cuadro.heading("Contaminantes Micro", text="Contaminantes Micro")
cuadro.heading("Otros", text="Otros")
cuadro.heading("Estado", text="Estado")

cuadro.heading("Responsable Verificacion", text="Responsable Verificacion")
cuadro.heading("Correccion", text="Correccion")

barra = ttk.Scrollbar(pestaña_prod,orient=tk.HORIZONTAL)
barra2 = ttk.Scrollbar(cuadro,orient=tk.VERTICAL)
cuadro.config(yscrollcommand=barra2.set)
barra2.config(command=cuadro.yview)
cuadro.config(xscrollcommand=barra.set)
barra.config(command=cuadro.xview)
cuadro.place(relx=0.01, rely=0.5, relwidth=0.95, relheight=0.47)
barra.place(relx=0.01, rely=0.97,relwidth=0.95)
barra2.pack(fill=tk.Y, side=RIGHT)

boton_cargar = ttk.Button(pestaña_prod, text="Cargar", command= cargar)
boton_cargar.place(relx=0.49, rely=0.14, relheight=0.07)
boton_liberar = ttk.Button(pestaña_prod, text="Liberar", command=liberar)
boton_liberar.place(relx=0.49, rely=0.21, relheight=0.07)
boton_verificar = ttk.Button(pestaña_prod, text="verificar", command=verificar)
boton_verificar.place(relx=0.49, rely=0.28, relheight=0.07)
boton_exportar = ttk.Button(pestaña_prod, text="Exportar", command= exportar)
boton_exportar.place(relx=0.964, rely=0.7, relheight=0.07,relwidth=0.04)
label_ruta_registro = ttk.Label(pestaña_config, text="Ruta a Carpeta de Registros")
label_ruta_registro.place(relx=0.1, rely=0.3)
entrada_ruta_registro = ttk.Entry(pestaña_config, width= 60)
entrada_ruta_registro.place(relx=0.27, rely=0.3)
configurar_ruta_registro = ttk.Button(pestaña_config,command = partial(selecionar_ruta,"registro"),text="Conf. Ruta")
configurar_ruta_registro.place(relx=0.8, rely=0.3)
boton_eliminar = ttk.Button(pestaña_prod, text="Eliminar", command=eliminar)
boton_eliminar.place(relx=0.49, rely=0.42, relheight=0.07)
boton_retener= ttk.Button(pestaña_prod, text="Retener", command=retener)
boton_retener.place(relx=0.49, rely=0.35, relheight=0.07)
boton_revalidar= ttk.Button(pestaña_prod, text="Revalidar", command=revalidar)
boton_revalidar.place(relx=0.92, rely=0.25, relheight=0.07)
boton_vencimiento= Button(pestaña_prod, text="MP Vencida", command=vencimiento)
boton_vencimiento.place(relx=0.92, rely=0.1, relheight=0.07)
boton_corregir= Button(pestaña_prod, text="Corregir",command=correccion)
boton_corregir.place(relx=0.75, rely=0.2, relheight=0.07)
leer_archivo()
leer_base()
ventana.mainloop()
