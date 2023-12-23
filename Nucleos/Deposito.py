from tkinter import *
from tkinter import ttk,messagebox, filedialog
import sqlite3
import os
from csv import reader, writer
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
        print(archivo_bd)
        entrada_ruta.delete("0", "end")
        entrada_ruta.insert(0, (archivo_bd))
        
    else:
        messagebox.showinfo(message="Configure las Rutas", title="Ruta Erronea")

def selecionar_ruta():
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

def recepcionar():
    fecha = entrada_fecha.get()
    mp = selec_mp.get()
    cantidad = entrada_cantidad.get()
    vto = entrada_vto.get()
    lote = entrada_lote.get()
    deposito = selec_deposito.get()
    remito = entrada_remito.get()
    try:
        conexion=sqlite3.connect(entrada_ruta.get())
        conexion.execute("""insert into recepcion (fecha,mp,lote,vto,cantidad,deposito,nderemito)
        VALUES(?,?,?,?,?,?,?);""",(fecha, mp, lote,vto,cantidad,deposito,remito))
        conexion.commit()                  
        conexion.close()
    except:
        messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")
           
ventana = Tk()
ventana.geometry("800x650")
ventana.title("Deposito")
tab_control = ttk.Notebook(ventana, width=800, height=650)
tab_control.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_recepcion = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_recepcion.place(x=0, y=0, relheight=1, relwidth=1)
tab_control.add(pestaña_recepcion, text="Recepciones")

label_ruta = ttk.Label(pestaña_recepcion, text="Ruta a Base de Dato")
label_fecha = ttk.Label(pestaña_recepcion, text="Fecha")
label_mp = ttk.Label(pestaña_recepcion, text="Materia Prima")
label_lote = ttk.Label(pestaña_recepcion, text="Lote")
label_vto = ttk.Label(pestaña_recepcion, text="Vencimiento")
label_cantidad = ttk.Label(pestaña_recepcion, text="Cantidad")
label_deposito = ttk.Label(pestaña_recepcion, text="Deposito")
label_remito = ttk.Label(pestaña_recepcion, text="N° de Remito")


label_ruta.place(relx=0.05, rely=0.9)
label_fecha.place(relx=0.05, rely=0.05)
label_mp.place(relx=0.05, rely=0.14)
label_lote.place(relx=0.05, rely=0.42)
label_vto.place(relx=0.05, rely=0.55)
label_cantidad.place(relx=0.05, rely=0.28)
label_deposito.place(relx=0.05, rely=0.7)
label_remito.place(relx=0.05, rely=0.8)

entrada_ruta = ttk.Entry(pestaña_recepcion, width= 60)
selec_mp = ttk.Combobox(pestaña_recepcion, width=30)
entrada_fecha = ttk.Entry(pestaña_recepcion, width= 30)
selec_mp = ttk.Combobox(pestaña_recepcion, width=30)
entrada_lote = ttk.Entry(pestaña_recepcion, width=30)
entrada_vto = ttk.Entry(pestaña_recepcion, width=30)
entrada_cantidad = ttk.Entry(pestaña_recepcion, width=30)
selec_deposito = ttk.Combobox(pestaña_recepcion, width=30)
entrada_remito = ttk.Entry(pestaña_recepcion, width=30)

entrada_ruta.place(relx=0.27, rely=0.9)
entrada_fecha.place(relx=0.27, rely=0.05)
selec_mp.place(relx=0.27, rely=0.14)
entrada_lote.place(relx=0.27, rely=0.28)
entrada_vto.place(relx=0.27, rely=0.42)
entrada_cantidad.place(relx=0.27, rely=0.55)
selec_deposito.place(relx=0.27, rely=0.7)
entrada_remito.place(relx=0.27, rely=0.8)
configurar_ruta = ttk.Button(command=selecionar_ruta,text="Conf. Ruta")
configurar_ruta.place(relx=0.8, rely=0.89)
recepcionar = ttk.Button(command=recepcionar,text="Recepcionar")
recepcionar.place(relx=0.7, rely=0.5)

selec_mp['values'] = "Azucar"
selec_deposito['values'] = "ntc"
leer_archivo()
ventana.mainloop()