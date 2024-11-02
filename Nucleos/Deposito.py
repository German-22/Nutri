import tkinter as tk
from tkinter import *
from tkinter import ttk,messagebox, filedialog
import sqlite3
import os
from csv import reader, writer
from reportlab.pdfgen import canvas
from functools import partial
from datetime import datetime
import time
import random
ruta_bd = ""
ruta_txt = ""

def leer_archivo():
    global ruta_txt
    if "archnucl" in os.listdir("/"):
        ruta_txt = "/archnucl"
    else:
        try:
            os.mkdir("/archnucl")
            ruta_txt = "/archnucl"
        except:
            messagebox.showinfo(message="No se Creo el Dir. del Archivo de Rutas", title="Error al Crear el Directorio")

    if "archivo_bd.txt" in os.listdir(ruta_txt):
        archivo_bd = reader(open(ruta_txt + "/archivo_bd.txt", "r"))
        archivo_bd = (list(archivo_bd)[0])
        entrada_ruta.delete("0", "end")
        entrada_ruta.insert(0, (archivo_bd))
       
    else:
        messagebox.showinfo(message="Configure la Ruta a la Base de Datos", title="Ruta Erronea")

    if "archivo_ruta_registro.txt" in os.listdir(ruta_txt):
        archivo_registro = reader(open(ruta_txt + "/archivo_ruta_registro.txt", "r"))
        archivo_registro = (list(archivo_registro)[0])
        entrada_ruta_registro.delete("0", "end")
        entrada_ruta_registro.insert(0, (archivo_registro))
        
    else:
        messagebox.showinfo(message="Configure la Ruta a la Carpeta de Registros", title="Ruta Erronea")

def selecionar_ruta(s):    
    if  s == "bd":
        ruta_guardar = []
        ruta_bd= filedialog.askopenfilename(initialdir="/", title="Seleccionar Base de Datos")                                        
        entrada_ruta.delete("0", "end")
        entrada_ruta.insert(0, str(ruta_bd))
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

def leer_base():
    try:
        conexion=sqlite3.connect(entrada_ruta.get())
        a = conexion.execute("""SELECT DISTINCT deposito FROM mp ;""")         
        selec_deposito['values'] = list(a)           
        conexion.close()
    except:
        messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")


def crear_pdf():
    #hora = time.strftime("%H:%M:%S")
    vto = entrada_vto.get()
    fecha = (entrada_fecha.get())
    mp = selec_mp.get()
    cantidad = (entrada_cantidad.get())
    
    lote = entrada_lote.get()
    deposito = selec_deposito.get()
    remito = entrada_remito.get()
    marca = entrada_marca.get()
    proveedor = entrada_prov.get()
    protocolo = entrada_prot.get()
    chofer = entrada_chofer.get()
    transporte = entrada_tran.get()
    patente = entrada_patente.get()
    habilitacion = entrada_habilitacion.get()
    estado_transporte = entrada_estadot.get()
    estado_carga = entrada_estadoc.get()
    responsable_deposito = entrada_resp.get()
    observacion = str(entrada_obs.get())
    presentacion = entrada_presentacion.get()
    calidad = str(random.sample(["Maria Eugenia Tillus", "Daniela Poloni", "Veronica Amuchastegui", "Natalia Martinez", "Sofia Pascua", "Mariano Benitez"],k=1)[0])
       
    c = canvas.Canvas(str(entrada_ruta_registro.get()) + "/" + str(fecha) + "-" + str(mp)+ "-" + str(lote)+ "-" + str(remito) + ".pdf")
    x = 50
    y = 50
    d = 40
    dist = y 
    while dist <= 810:         
        c.line(x, dist, x + 500, dist)
        dist = dist + d
    xh = 50
    yh = 50
    dh = 250
    dist = 0
    while dist <= 500:    
        c.line(xh + dist, yh, xh + dist, 810)
        dist = dist + dh
    c.drawString(60, 785, "Fecha: " + fecha)
    c.drawString(60, 745, "Materia Prima: " + mp)
    c.drawString(60, 705, "Vencimiento: " + vto)
    c.drawString(60, 665, "Cantidad: " + cantidad)
    c.drawString(60, 625, "Lote: " + lote)
    c.drawString(60, 585, "Deposito: " + deposito)
    c.drawString(60, 545, "Remito: " + remito)
    c.drawString(60, 505, "Marca: " + marca)
    c.drawString(60, 465, "Proveedor: " + proveedor)
    c.drawString(60, 425, "Protocolo: " + protocolo)
    c.drawString(305, 785, "Cofer: " + chofer)
    c.drawString(305, 745, "Transporte: " + transporte)
    c.drawString(305, 705, "Patente: " + patente)
    c.drawString(305, 665, "Habilitacion: " + habilitacion)
    c.drawString(305, 625, "Estado de Transporte: " + estado_transporte)
    c.drawString(305, 585, "Estado de Carga: " + estado_carga)
    c.drawString(305, 545, "Responsable: " + responsable_deposito)
    c.drawString(305, 505, "Presentacion MP: " + presentacion)
    c.drawString(305, 465, "Observaciones: " + observacion)
    c.drawString(305, 65, "Verifico:  " + calidad)
    c.save()

def seleccionar_deposito(s):
    dep = selec_deposito.get()
    try:
        conexion=sqlite3.connect(entrada_ruta.get())
        a = conexion.execute("""SELECT mp FROM mp WHERE deposito = ?;""", (dep,))         
        selec_mp['values'] = list(a)           
        conexion.close()
    except:
        messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")

def recepcionar():
    for s in cuadro.get_children():
            cuadro.delete(s)
    mp = selec_mp.get()
    cantidad = (entrada_cantidad.get())
    vto = entrada_vto.get()
    lote = entrada_lote.get()
    deposito = selec_deposito.get()
    remito = entrada_remito.get()
    marca = entrada_marca.get()
    proveedor = entrada_prov.get()
    protocolo = entrada_prot.get()
    chofer = entrada_chofer.get()
    transporte = entrada_tran.get()
    patente = entrada_patente.get()
    habilitacion = entrada_habilitacion.get()
    estado_transporte = entrada_estadot.get()
    estado_carga = entrada_estadoc.get()
    responsable_deposito = entrada_resp.get()
    observacion = str(entrada_obs.get())
    presentacion = entrada_presentacion.get()        

    if mp!="" and cantidad != "" and vto != "" and lote!="" and deposito != "" and remito != "" and marca != "" and proveedor != "" and protocolo != "" and chofer != "" and transporte != "" and patente != "" and habilitacion != "" and estado_transporte != "" and estado_carga != "" and responsable_deposito != "" and presentacion != "":
        fecha = (entrada_fecha.get())
        try:
            float(cantidad)
        except:
            messagebox.showinfo(message="Error en Cantidad", title="Error")
            return

        if len(vto)==10 and len(fecha)==10 :
            dia = vto[0:2]
            mes = vto[3:5]
            año = vto[6:10]        
            vto = (año) + "-" + (mes) + "-" + (dia)                  
            try:            
                datetime.strptime(vto, "%Y-%m-%d")            
            except:            
                messagebox.showinfo(message="Error en Fecha de Vto", title="Error de Fecha")
                return                         
            try:            
                datetime.strptime(str(fecha), "%d-%m-%Y")            
            except:            
                messagebox.showinfo(message="Error en Fecha", title="Error de Fecha")
                return
            try:
                conexion=sqlite3.connect(entrada_ruta.get())
                a = conexion.execute("""SELECT * FROM recepcion WHERE mp = ? and lote = ? and nderemito = ?;""",(mp, lote,remito))
                b = a.fetchall()
                if b != []:                    
                    messagebox.showinfo(message="Esta Materia Prima ya Esta Recepcionada", title="Registro Duplicado")
                    for i in b:                        
                        cuadro.insert("", tk.END, text=i[1],
                                values=(i[2],i[3],i[7],i[6],i[8],i[20]))
                    conexion.close()
                    return                   
            except:
                messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")
                return
            try:
                conexion=sqlite3.connect(entrada_ruta.get())
                conexion.execute("""insert into recepcion (fecha,mp,lote,vto,cantidad,deposito,nderemito,presentacion,marca,proveedor,protocolo,chofer,transporte,patente,habilitacion,estado_transporte,estado_carga,observacion,responsabledeposito)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);""",(fecha, mp, lote,vto,float(cantidad),deposito,remito,presentacion,marca,proveedor,protocolo,chofer,transporte, patente,habilitacion,estado_transporte,estado_carga,observacion,responsable_deposito))
                conexion.commit()
                conexion.close()
                cuadro.insert("", tk.END, text=fecha,
                                values=(mp,lote,deposito,cantidad,remito,responsable_deposito))
            except:
                messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")
                return
            try:
                crear_pdf()
                messagebox.showinfo(message="Registrado", title="Registrado")
            except:
                messagebox.showinfo(message="Error al Crear Registro", title="Error de Conexion")
        else:
            messagebox.showinfo(message="Error en Fecha", title="Error de Fecha")
    else:
        messagebox.showinfo(message="Complete todos los Campos", title="Campo Incompleto")

def validar_entrada(numero):  
          
    try:
        int(numero)
        return True
    except:
        if numero == "-":
            return True
        else:
            return False
            
def validar_entrada_cantidad(numero):        
    try:
        int(numero)
        if len(entrada_cantidad.get()) == 0:
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
            if len(entrada_lote.get()) == 0:
                if int(numero) == 0:
                    return False
                else:
                    return True
            return True
        except:
            return True   
    else:
        return False

def seleccionar_mp(s):
    conexion=sqlite3.connect(entrada_ruta.get())
    mp = selec_mp.get()
    a = conexion.execute("""SELECT codmp FROM mp WHERE mp = ? ;""", (mp,))
    mostrar_codigo["state"] = ["enable"]
    mostrar_codigo.delete(0,"end")
    mostrar_codigo.insert(0,a.fetchall())    
    mostrar_codigo["state"] = ["disable"]    
    conexion.close()

ventana = Tk()
ventana.geometry("1000x650")
ventana.title("Deposito")
tab_control = ttk.Notebook(ventana, width=800, height=650)
tab_control.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_recepcion = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_recepcion.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_conf = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_conf.place(x=0, y=0, relheight=1, relwidth=1)
tab_control.add(pestaña_recepcion, text="Recepciones")
tab_control.add(pestaña_conf, text="Configuracion")

label_ruta_registro = ttk.Label(pestaña_conf, text="Ruta a Carpeta de Registros")
label_ruta = ttk.Label(pestaña_conf, text="Ruta a Base de Datos")
label_fecha = ttk.Label(pestaña_recepcion, text="Fecha")
label_mp = ttk.Label(pestaña_recepcion, text="Materia Prima")
label_lote = ttk.Label(pestaña_recepcion, text="Lote")
label_vto = ttk.Label(pestaña_recepcion, text="Vencimiento")
label_cantidad = ttk.Label(pestaña_recepcion, text="Cantidad")
label_deposito = ttk.Label(pestaña_recepcion, text="Deposito")
label_remito = ttk.Label(pestaña_recepcion, text="N° de Remito")

label_ruta_registro.place(relx=0.05, rely=0.3)
label_ruta.place(relx=0.05, rely=0.7)
label_fecha.place(relx=0.01, rely=0.05)
label_mp.place(relx=0.01, rely=0.15)
label_lote.place(relx=0.01, rely=0.25)
label_vto.place(relx=0.01, rely=0.30)
label_cantidad.place(relx=0.01, rely=0.20)
label_deposito.place(relx=0.01, rely=0.1)
label_remito.place(relx=0.01, rely=0.35)

entrada_ruta_registro = ttk.Entry(pestaña_conf, width= 60)
entrada_ruta = ttk.Entry(pestaña_conf, width= 60)
selec_mp = ttk.Combobox(pestaña_recepcion, width=40,state="readonly")
selec_mp.bind("<<ComboboxSelected>>", partial(seleccionar_mp))
entrada_fecha = ttk.Entry(pestaña_recepcion, width= 30,validate="key",
                      validatecommand=((pestaña_recepcion.register(validar_entrada)), "%S"))

entrada_lote = ttk.Entry(pestaña_recepcion, width=30, validate="key",validatecommand=((pestaña_recepcion.register(validar_entrada_lote)),"%S"))
entrada_vto = ttk.Entry(pestaña_recepcion, width=30,validate="key",validatecommand=((pestaña_recepcion.register(validar_entrada)),"%S"))
entrada_cantidad = ttk.Entry(pestaña_recepcion, width=30,validate="key",validatecommand=((pestaña_recepcion.register(validar_entrada_cantidad)),"%S"))
selec_deposito = ttk.Combobox(pestaña_recepcion, width=30,state="readonly")
selec_deposito.bind("<<ComboboxSelected>>", partial(seleccionar_deposito))
entrada_remito = ttk.Entry(pestaña_recepcion, width=30,validate="key",validatecommand=((pestaña_recepcion.register(validar_entrada_lote)),"%S"))

entrada_ruta_registro.place(relx=0.27, rely=0.3)
entrada_ruta.place(relx=0.27, rely=0.7)
entrada_fecha.place(relx=0.15, rely=0.05)
selec_mp.place(relx=0.15, rely=0.15)
mostrar_codigo = ttk.Entry(pestaña_recepcion, width=15)
mostrar_codigo.place(relx=0.42, rely=0.15)
entrada_lote.place(relx=0.15, rely=0.25)
entrada_vto.place(relx=0.15, rely=0.30)
entrada_cantidad.place(relx=0.15, rely=0.20)
selec_deposito.place(relx=0.15, rely=0.1)
entrada_remito.place(relx=0.15, rely=0.35)

label_marca = ttk.Label(pestaña_recepcion, text="Marca")
label_marca.place(relx=0.55, rely=0.05)
label_prov = ttk.Label(pestaña_recepcion, text="Proveedor")
label_prov.place(relx=0.55, rely=0.1)
label_prot = ttk.Label(pestaña_recepcion, text="Protocolo")
label_prot.place(relx=0.55, rely=0.15)
label_chofer = ttk.Label(pestaña_recepcion, text="Chofer")
label_chofer.place(relx=0.55, rely=0.2)
label_tran = ttk.Label(pestaña_recepcion, text="Transporte")
label_tran.place(relx=0.55, rely=0.25)
label_patente = ttk.Label(pestaña_recepcion, text="Patente")
label_patente.place(relx=0.55, rely=0.30)
label_habilitacion = ttk.Label(pestaña_recepcion, text="Hailitacion")
label_habilitacion.place(relx=0.55, rely=0.35)
label_estadot = ttk.Label(pestaña_recepcion, text="Estado del Transporte")
label_estadot.place(relx=0.55, rely=0.40)
label_estadoc = ttk.Label(pestaña_recepcion, text="Estado de Carga")
label_estadoc.place(relx=0.01, rely=0.40)
label_responsable = ttk.Label(pestaña_recepcion, text="Responsable")
label_responsable.place(relx=0.01, rely=0.45)
label_observ = ttk.Label(pestaña_recepcion, text="Observaciones")
label_observ.place(relx=0.55, rely=0.55)
label_presentacion = ttk.Label(pestaña_recepcion, text="Presentacion")
label_presentacion.place(relx=0.55, rely=0.45)

entrada_marca = ttk.Entry(pestaña_recepcion, width=30)
entrada_marca.place(relx=0.70, rely=0.05)
entrada_prov = ttk.Entry(pestaña_recepcion, width=30)
entrada_prov.place(relx=0.7, rely=0.1)
entrada_prot = ttk.Combobox(pestaña_recepcion, width=30,state="readonly",values=["Falta_Protocolo","Papel", "Digital"])
entrada_prot.place(relx=0.7, rely=0.15)
entrada_chofer = ttk.Entry(pestaña_recepcion, width=30)
entrada_chofer.place(relx=0.7, rely=0.20)
entrada_tran = ttk.Entry(pestaña_recepcion, width=30)
entrada_tran.place(relx=0.7, rely=0.25)
entrada_patente = ttk.Entry(pestaña_recepcion, width=30)
entrada_patente.place(relx=0.7, rely=0.30)
entrada_habilitacion = ttk.Entry(pestaña_recepcion, width=30)
entrada_habilitacion.place(relx=0.7, rely=0.35)
entrada_estadot = ttk.Entry(pestaña_recepcion, width=30)
entrada_estadot.place(relx=0.7, rely=0.40)
entrada_estadoc = ttk.Entry(pestaña_recepcion, width=30)
entrada_estadoc.place(relx=0.15, rely=0.4)
entrada_resp = ttk.Entry(pestaña_recepcion, width=30)
entrada_resp.place(relx=0.15, rely=0.45)
entrada_obs = ttk.Entry(pestaña_recepcion, width=30)
entrada_obs.place(relx=0.7, rely=0.55,relheight=0.1)
entrada_presentacion = ttk.Entry(pestaña_recepcion, width=30)
entrada_presentacion.place(relx=0.7, rely=0.45)

configurar_ruta = ttk.Button(pestaña_conf,command = partial(selecionar_ruta,"bd"),text="Conf. Ruta")
configurar_ruta.place(relx=0.8, rely=0.7)
configurar_ruta_registro = ttk.Button(pestaña_conf,command = partial(selecionar_ruta,"registro"),text="Conf. Ruta")
configurar_ruta_registro.place(relx=0.8, rely=0.3)
recepcionar_mp = ttk.Button(pestaña_recepcion,command=recepcionar,text="Recepcionar")
recepcionar_mp.place(relx=0.2, rely=0.55, relheight=0.11,relwidth=0.15)
cuadro = ttk.Treeview(pestaña_recepcion, columns=("MP","Lote","Deposito","Cantidad","N° Remito","Responsable"))
cuadro.column("#0", width=80, anchor="center")
cuadro.column("MP", width=30, anchor="center")
cuadro.column("Lote", width=30, anchor="center")
cuadro.column("Deposito", width=10, anchor="center")
cuadro.column("Cantidad", width=10, anchor="center")
cuadro.column("N° Remito", width=10, anchor="center")
cuadro.column("Responsable", width=10, anchor="center")

cuadro.heading("#0", text="Fecha")
cuadro.heading("MP", text="MP")
cuadro.heading("Lote", text="Lote")
cuadro.heading("Deposito", text="Deposito")
cuadro.heading("Cantidad", text="Cantidad")
cuadro.heading("N° Remito", text="N° de Remito")
cuadro.heading("Responsable", text="Responsable")
cuadro.place(relx=0.01, rely=0.7, relwidth=0.95, relheight=0.2)

leer_archivo()
leer_base()
ventana.mainloop()