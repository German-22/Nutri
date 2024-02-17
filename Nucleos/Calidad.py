import tkinter as tk
from tkinter import *
from tkinter import ttk,messagebox, filedialog
import sqlite3
from datetime import datetime
from csv import reader, writer
from reportlab.pdfgen import canvas
from functools import partial
import Leer_archivo as la 
import csv
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
        mp['values'] = list(a)
        a = conexion.execute("""SELECT DISTINCT fecha FROM recepcion;""")
        fecha['values'] = list(a)
        a = conexion.execute("""SELECT DISTINCT nderemito FROM recepcion;""") 
        nderemito['values'] = list(a)
        a = conexion.execute("""SELECT DISTINCT lote FROM recepcion;""") 
        lote['values'] = list(a)
        a = conexion.execute("""SELECT DISTINCT proveedor FROM recepcion;""") 
        proveedor['values'] = list(a)
        a = conexion.execute("""SELECT DISTINCT marca FROM recepcion;""") 
        marca['values'] = list(a)
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
    elif r == "marca":
        b = marca.get()   
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
                            values=(i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8],i[9],i[10],i[11],i[12],i[13],i[14],i[15],i[16],i[17],i[18],i[19],i[20],i[21],i[22],i[23],i[24],i[25],i[26],i[27],i[28],i[29],i[30],i[31]))
    conexion.close()

def liberar():
    id = cuadro.item(cuadro.selection())["text"]
    mp = cuadro.item(cuadro.selection())["values"][1]
    deposito = cuadro.item(cuadro.selection())["values"][6]
    lote = cuadro.item(cuadro.selection())["values"][2]
    respon = entrada_responsable.get()
    if respon == "":
        messagebox.showinfo(message="Ingrese Responsable", title="Error")
        return   
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    conexion.execute("""UPDATE recepcion SET estado = "liberado" , responsablecalidad = ? WHERE id = ?;""",(respon, id))
    conexion.commit()
    conexion.execute("""UPDATE stock SET estado = "liberado" WHERE mp = ? and deposito = ? and lote = ?;""",(mp,deposito,lote))
    conexion.commit()
    conexion.close()     
    buscar("id",id) 

def verificar():
    id = cuadro.item(cuadro.selection())["text"]
    respon = entrada_responsable.get()
    if respon == "":
        messagebox.showinfo(message="Ingrese Responsable", title="Error")
        return   
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    conexion.execute("""UPDATE recepcion SET estado = "verificado", resver = ? WHERE id = ?;""",(respon,id))
    conexion.commit()
    conexion.close()     
    buscar("id",id) 

def cargar():
    id = cuadro.item(cuadro.selection())["text"]
    fecha_elab = entrada_fechaelb.get()
    revision = entrada_revision.get()
    organo = entrada_organ.get()
    fis = entrada_fisic.get()
    confisic = entrada_confis.get()
    qui = entrada_conqui.get()
    micro = entrada_micro.get()
    responsable = entrada_responsable.get()  
    rotulo = entrada_rotulo.get()
    otro = entrada_otros.get()
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    conexion.execute("""UPDATE recepcion SET fechaelaboracion=?,etrevision=?,rotulo=?,organolep=?,fisicoqui=?,contfisico=?,contquimico=?,contmicro=?,responsablecalidad=?, otros = ? WHERE id = ?;""",(fecha_elab,revision,rotulo,organo,fis,confisic,qui,micro,responsable,otro,id))
    conexion.commit()
    conexion.close()     
    buscar("id",id) 

def exportar():       
    ruta = entrada_ruta_registro.get()
    with open(ruta + "/" + 'reporte.csv', 'w', newline='') as f:       
        writer = csv.writer(f,delimiter=';') 
        guardar = ["Fecha","MP","Lote","Fecha de Elaboracion","Vto","Cantidad", "Deposito", "N° de Remito","Presentacion" ,"Marca","Proveedor","Protocolo","Chofer","Transporte","Patente","Habilitacion","Estado del Transporte","Estado de Carga","Observacion","Responsable Deposito","Responsable Calidad","ET Revision","Rotulo","Caracteristicas Organolepticas", "Fisicoquimicas","Contaminantes Fisicos","Contaminantes Quimicos","Contaminantes Micro", "Estado","Otros Datos","Responsable Verificacion"]
        writer.writerow(guardar)        
        for i in cuadro.get_children():
            guardar.clear()           
              
            for t in cuadro.item(i)["values"]:
                guardar.append(t)
            writer.writerow(guardar)    
    
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
    id = cuadro.item(cuadro.selection())["text"]
    mp = cuadro.item(cuadro.selection())["values"][1]
    deposito = cuadro.item(cuadro.selection())["values"][6]
    lote = cuadro.item(cuadro.selection())["values"][2]
    conexion=sqlite3.connect(entrada_ruta_bd.get())
    conexion.execute("""DELETE FROM recepcion WHERE id = ?;""",(id,))
    conexion.commit()
    conexion.execute("""DELETE FROM stock WHERE mp = ? and deposito = ? and lote = ?;""",(mp,deposito,lote))
    conexion.commit()
    conexion.close()  
    cuadro.delete(cuadro.selection())   

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
    buscar("id",id) 

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
    conexion.execute("""UPDATE stock SET vto = ? WHERE mp = ? and lote = ?;""",(rev,b[0][2],b[0][3]))
    conexion.commit()
    conexion.close()     
    buscar("id",id) 

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
label_fecha.place(relx=0.01, rely=0.01)
label_mp = ttk.Label(pestaña_prod, text="Materia Prima")
label_mp.place(relx=0.01, rely=0.08)
label_nremito = ttk.Label(pestaña_prod, text="N° de Remito")
label_nremito.place(relx=0.01, rely=0.15)
label_lote = ttk.Label(pestaña_prod, text="Lote")
label_lote.place(relx=0.01, rely=0.22)
label_prov = ttk.Label(pestaña_prod, text="Proveedor")
label_prov.place(relx=0.01, rely=0.29)
label_marca = ttk.Label(pestaña_prod, text="Marca")
label_marca.place(relx=0.01, rely=0.36)
label_fechaelab = ttk.Label(pestaña_prod, text="Fecha de Elaboracion")
label_fechaelab.place(relx=0.4, rely=0.01)
label_revision = ttk.Label(pestaña_prod, text="ET/Revision")
label_revision.place(relx=0.4, rely=0.06)
label_rotulo = ttk.Label(pestaña_prod, text="Rotulo")
label_rotulo.place(relx=0.4, rely=0.11)
label_organ = ttk.Label(pestaña_prod, text="Carcateristias Organolepticas")
label_organ.place(relx=0.4, rely=0.16)
label_fisic = ttk.Label(pestaña_prod, text="Carcateristias Fisicas")
label_fisic.place(relx=0.4, rely=0.21)
label_confis = ttk.Label(pestaña_prod, text="Contaminaantes Fisicos")
label_confis.place(relx=0.4, rely=0.26)
label_conqui = ttk.Label(pestaña_prod, text="Contamientes Quimicos")
label_conqui.place(relx=0.4, rely=0.31)
label_conmicro = ttk.Label(pestaña_prod, text="Contamientes Microbiologicos")
label_conmicro.place(relx=0.4, rely=0.36)
label_responsable = ttk.Label(pestaña_prod, text="Responsable")
label_responsable.place(relx=0.4, rely=0.41)
label_otros = ttk.Label(pestaña_prod, text="Otros Datos")
label_otros.place(relx=0.7, rely=0.04)
entrada_otros= ttk.Entry(pestaña_prod, width=20)
entrada_otros.place(relx=0.75, rely=0.02,height=60)
label_revalida = ttk.Label(pestaña_prod, text="Vto.Revalida")
label_revalida.place(relx=0.85, rely=0.2)

entrada_revalida= ttk.Entry(pestaña_prod, width=20,validate="key",validatecommand=((pestaña_prod.register(validar_entrada)),"%S"))
entrada_revalida.place(relx=0.9, rely=0.2)
entrada_fechaelb= ttk.Entry(pestaña_prod, width=30)
entrada_fechaelb.place(relx=0.55, rely=0.01)
entrada_revision = ttk.Entry(pestaña_prod, width=30)
entrada_revision.place(relx=0.55, rely=0.06)
entrada_rotulo = ttk.Entry(pestaña_prod, width=30)
entrada_rotulo.place(relx=0.55, rely=0.11)
entrada_organ = ttk.Entry(pestaña_prod, width=30)
entrada_organ.place(relx=0.55, rely=0.16)
entrada_fisic = ttk.Entry(pestaña_prod, width=30)
entrada_fisic.place(relx=0.55, rely=0.21)
entrada_confis = ttk.Entry(pestaña_prod, width=30)
entrada_confis.place(relx=0.55, rely=0.26)
entrada_conqui = ttk.Entry(pestaña_prod, width=30)
entrada_conqui.place(relx=0.55, rely=0.31)
entrada_micro = ttk.Entry(pestaña_prod, width=30)
entrada_micro.place(relx=0.55, rely=0.36)
entrada_responsable = ttk.Entry(pestaña_prod, width=30)
entrada_responsable.place(relx=0.55, rely=0.41)

fecha = ttk.Combobox(pestaña_prod, width=40, state="readonly")
fecha.place(relx=0.11, y=10)
fecha.bind("<<ComboboxSelected>>", partial(buscar,"fecha"))
mp = ttk.Combobox(pestaña_prod, width=40,state="readonly")
mp.place(relx=0.11, rely=0.08)
mp.bind("<<ComboboxSelected>>", partial(buscar,"mp"))
nderemito = ttk.Combobox(pestaña_prod, width=40,state="readonly")
nderemito.place(relx=0.11, rely=0.15)
nderemito.bind("<<ComboboxSelected>>", partial(buscar,"nderemito"))
lote = ttk.Combobox(pestaña_prod, width=40, state="readonly")
lote.place(relx=0.11, rely=0.22)
lote.bind("<<ComboboxSelected>>", partial(buscar,"lote"))
proveedor = ttk.Combobox(pestaña_prod, width=40,state="readonly")
proveedor.place(relx=0.11, rely=0.29)
proveedor.bind("<<ComboboxSelected>>", partial(buscar,"proveedor"))
marca = ttk.Combobox(pestaña_prod, width=40,state="readonly")
marca.place(relx=0.11, rely=0.36)
marca.bind("<<ComboboxSelected>>", partial(buscar,"marca"))
estado = ttk.Combobox(pestaña_prod, width=40,state="readonly" ,values=["pendiente","liberado","verificado","retenido"])
estado.place(relx=0.11, rely=0.42)
estado.bind("<<ComboboxSelected>>", partial(buscar,"estado"))
label_estado = ttk.Label(pestaña_prod, text="Estado")
label_estado.place(relx=0.01, rely=0.42)
cuadro = ttk.Treeview(pestaña_prod, columns=("Fecha","MP","Lote","Fecha de Elaboracion","Vto","Cantidad", "Deposito", "N° de Remito","Presentacion" , "Marca","Proveedor","Protocolo","Chofer","Transporte","Patente","Habilitacion","Estado del Transporte","Estado de Carga","Observacion","Responsable Deposito","Responsable Calidad","ET Revision","Rotulo","Caracteristicas Organolepticas", "Fisicoquimicas","Contaminantes Fisicos","Contaminantes Quimicos","Contaminantes Micro", "Estado","Otros","Responsable Verificacion"))
cuadro.column("#0",anchor="center")
cuadro.column("Fecha",anchor="center")
cuadro.column("MP", anchor="center")
cuadro.column("Lote", anchor="center")
cuadro.column("Fecha de Elaboracion", width=100, anchor="center")
cuadro.column("Vto", anchor="center")
cuadro.column("Cantidad",anchor="center")
cuadro.column("Deposito",anchor="center")
cuadro.column("N° de Remito", anchor="center")
cuadro.column("Presentacion",  anchor="center")
cuadro.column("Marca", anchor="center")
cuadro.column("Proveedor", anchor="center")
cuadro.column("Protocolo", anchor="center")
cuadro.column("Chofer", anchor="center")
cuadro.column("Transporte",  anchor="center")
cuadro.column("Patente", anchor="center")
cuadro.column("Habilitacion",  anchor="center")
cuadro.column("Estado del Transporte",  anchor="center")
cuadro.column("Estado de Carga" ,anchor="center")
cuadro.column("Observacion",  anchor="center")
cuadro.column("Responsable Deposito",  anchor="center")
cuadro.column("Responsable Calidad",  anchor="center")

cuadro.column("Observacion", anchor="center")
cuadro.column("ET Revision",anchor="center")
cuadro.column("Rotulo",anchor="center")
cuadro.column("Caracteristicas Organolepticas", anchor="center")
cuadro.column("Fisicoquimicas",  anchor="center")
cuadro.column("Contaminantes Fisicos", anchor="center")
cuadro.column("Contaminantes Quimicos", anchor="center")
cuadro.column("Contaminantes Micro",  anchor="center")
cuadro.column("Estado", anchor="center")
cuadro.column("Otros", anchor="center")
cuadro.column("Responsable Verificacion", anchor="center")
cuadro.heading("#0", text="Id")
cuadro.heading("Fecha", text="Fecha")
cuadro.heading("MP", text="MP")
cuadro.heading("Lote", text="Lote")
cuadro.heading("Fecha de Elaboracion", text="Fecha de Elaboracion")
cuadro.heading("Vto", text="Vto")
cuadro.heading("Cantidad", text="Cantidad")
cuadro.heading("Deposito", text="Deposito")
cuadro.heading("N° de Remito", text="N° de Remito")
cuadro.heading("Presentacion", text="Presentacion")
cuadro.heading("Marca", text="Marca")
cuadro.heading("Proveedor", text="Proveedor")
cuadro.heading("Protocolo", text="Protocolo")
cuadro.heading("Chofer", text="Chofer")
cuadro.heading("Transporte", text="Transporte")
cuadro.heading("Patente", text="Patente")
cuadro.heading("Habilitacion", text="Habilitacion")
cuadro.heading("Estado del Transporte", text="Estado del Transporte")
cuadro.heading("Estado de Carga", text="Estado de Carga")
cuadro.heading("Observacion", text="Observacion")
cuadro.heading("Responsable Deposito", text="Responsable Deposito")
cuadro.heading("Responsable Calidad", text="Responsable Calidad")
cuadro.heading("ET Revision", text="ET Revision")
cuadro.heading("Rotulo", text="Rotulo")
cuadro.heading("Caracteristicas Organolepticas", text="Caracteristicas Organolepticas")
cuadro.heading("Fisicoquimicas", text="Fisicoquimicas")
cuadro.heading("Contaminantes Fisicos", text="Contaminantes Fisicos")
cuadro.heading("Contaminantes Quimicos", text="Contaminantes Quimicos")
cuadro.heading("Contaminantes Micro", text="Contaminantes Micro")
cuadro.heading("Estado", text="Estado")
cuadro.heading("Otros", text="Otros")
cuadro.heading("Responsable Verificacion", text="Responsable Verificacion")


barra = ttk.Scrollbar(cuadro,orient=tk.HORIZONTAL)
barra2 = ttk.Scrollbar(cuadro,orient=tk.VERTICAL)
cuadro.config(yscrollcommand=barra2.set)
barra2.config(command=cuadro.yview)
cuadro.config(xscrollcommand=barra.set)
barra.config(command=cuadro.xview)
cuadro.place(relx=0.01, rely=0.5, relwidth=0.95, relheight=0.47)
barra.pack(fill=tk.X, side=BOTTOM)
barra2.pack(fill=tk.Y, side=RIGHT)

boton_cargar = ttk.Button(pestaña_prod, text="Cargar", command= cargar)
boton_cargar.place(relx=0.7, rely=0.2, relheight=0.07)
boton_liberar = ttk.Button(pestaña_prod, text="Liberar", command=liberar)
boton_liberar.place(relx=0.76, rely=0.2, relheight=0.07)
boton_verificar = ttk.Button(pestaña_prod, text="verificar", command=verificar)
boton_verificar.place(relx=0.7, rely=0.27, relheight=0.07)
boton_exportar = ttk.Button(pestaña_prod, text="Exportar", command= exportar)
boton_exportar.place(relx=0.33, rely=0.15, relheight=0.07)
label_ruta_registro = ttk.Label(pestaña_config, text="Ruta a Carpeta de Registros")
label_ruta_registro.place(relx=0.1, rely=0.3)
entrada_ruta_registro = ttk.Entry(pestaña_config, width= 60)
entrada_ruta_registro.place(relx=0.27, rely=0.3)
configurar_ruta_registro = ttk.Button(pestaña_config,command = partial(selecionar_ruta,"registro"),text="Conf. Ruta")
configurar_ruta_registro.place(relx=0.8, rely=0.3)
boton_eliminar = ttk.Button(pestaña_prod, text="Eliminar", command=eliminar)
boton_eliminar.place(relx=0.73, rely=0.35, relheight=0.07)
boton_retener= ttk.Button(pestaña_prod, text="Retener", command=retener)
boton_retener.place(relx=0.76, rely=0.27, relheight=0.07)
boton_revalidar= ttk.Button(pestaña_prod, text="Revalidar", command=revalidar)
boton_revalidar.place(relx=0.92, rely=0.25, relheight=0.07)
leer_archivo()
leer_base()
ventana.mainloop()
