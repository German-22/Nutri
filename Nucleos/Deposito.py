from tkinter import *
from tkinter import ttk,messagebox, filedialog
import sqlite3
import os
from csv import reader, writer
from reportlab.pdfgen import canvas
from functools import partial
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
    
    c = canvas.Canvas(str(entrada_ruta_registro.get()) + "/" + str(entrada_fecha.get()) + str(selec_mp.get()) + ".pdf")
    c.drawString(100, 750, "Fecha: " + entrada_fecha.get())
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
    fecha = entrada_fecha.get()
    mp = selec_mp.get()
    cantidad = entrada_cantidad.get()
    vto = entrada_vto.get()
    lote = entrada_lote.get()
    deposito = selec_deposito.get()
    remito = entrada_remito.get()
    #try:
    conexion=sqlite3.connect(entrada_ruta.get())
    conexion.execute("""insert into recepcion (fecha,mp,lote,vto,cantidad,deposito,nderemito)
    VALUES(?,?,?,?,?,?,?);""",(fecha, mp, lote,vto,cantidad,deposito,remito))
    a = conexion.execute("""SELECT stock FROM stock WHERE mp = ? and lote = ?;""",(mp, lote))
    b = a.fetchone()
    
    if len(b) == 0:
        stock = cantidad
        print(stock)
    else:       
        stock = (float((b)[0])) + float(cantidad)   
           
    conexion.execute("""UPDATE stock SET stock = ? WHERE mp = ? and lote = ?;""",(stock,mp,lote))
    conexion.commit()                  
    conexion.close()
    #except:
     #   messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")

    try:
        crear_pdf()
    except:
        messagebox.showinfo(message="Error al Crear Registro", title="Error de Conexion")

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
ventana.geometry("800x650")
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
label_fecha.place(relx=0.05, rely=0.05)
label_mp.place(relx=0.05, rely=0.14)
label_lote.place(relx=0.05, rely=0.42)
label_vto.place(relx=0.05, rely=0.55)
label_cantidad.place(relx=0.05, rely=0.28)
label_deposito.place(relx=0.05, rely=0.7)
label_remito.place(relx=0.05, rely=0.8)

entrada_ruta_registro = ttk.Entry(pestaña_conf, width= 60)
entrada_ruta = ttk.Entry(pestaña_conf, width= 60)
selec_mp = ttk.Combobox(pestaña_recepcion, width=30)
entrada_fecha = ttk.Entry(pestaña_recepcion, width= 30,validate="key",
                      validatecommand=((pestaña_recepcion.register(validar_entrada)), "%S"))
selec_mp = ttk.Combobox(pestaña_recepcion, width=30)
entrada_lote = ttk.Entry(pestaña_recepcion, width=30)
entrada_vto = ttk.Entry(pestaña_recepcion, width=30,validate="key",validatecommand=((pestaña_recepcion.register(validar_entrada)),"%S"))
entrada_cantidad = ttk.Entry(pestaña_recepcion, width=30)
selec_deposito = ttk.Combobox(pestaña_recepcion, width=30)
selec_deposito.bind("<<ComboboxSelected>>", partial(seleccionar_deposito))
entrada_remito = ttk.Entry(pestaña_recepcion, width=30)

entrada_ruta_registro.place(relx=0.27, rely=0.3)
entrada_ruta.place(relx=0.27, rely=0.7)
entrada_fecha.place(relx=0.27, rely=0.05)
selec_mp.place(relx=0.27, rely=0.14)
entrada_lote.place(relx=0.27, rely=0.42)
entrada_vto.place(relx=0.27, rely=0.55)
entrada_cantidad.place(relx=0.27, rely=0.28)
selec_deposito.place(relx=0.27, rely=0.7)
entrada_remito.place(relx=0.27, rely=0.8)
configurar_ruta = ttk.Button(pestaña_conf,command = partial(selecionar_ruta,"bd"),text="Conf. Ruta")
configurar_ruta.place(relx=0.8, rely=0.7)
configurar_ruta_registro = ttk.Button(pestaña_conf,command = partial(selecionar_ruta,"registro"),text="Conf. Ruta")
configurar_ruta_registro.place(relx=0.8, rely=0.3)

recepcionar_mp = ttk.Button(pestaña_recepcion,command=recepcionar,text="Recepcionar")
recepcionar_mp.place(relx=0.7, rely=0.5)

leer_archivo()
leer_base()
ventana.mainloop()