import sys

from datetime import datetime
import serial
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import *
import os
import time
from csv import reader, writer
from functools import partial
import Leer_archivo as la
import sqlite3
MP_macro= []
lista_lote = []
lista_vto = []
lista_lote_macro = []
lista_vto_macro = []
indice_lote = 0
MP_seleccionada = "a"
MP_seleccionada_macro = "a"
lote = "a"
lote_macro = "a"
n_mp = 1
n_batch = 1
item = 1
rutas = []
ruta_txt = ""
ruta_lote = "C:/"
ruta_receta = "C:/"
ruta_receta_macro = "C:/"
ruta_registro = "C:/"
recetas = os.listdir(ruta_receta)
recetas_macro = os.listdir(ruta_receta_macro)
lotes = os.listdir(ruta_lote)
MP = []
cantidades = []
n_fila = 1
n_fila_macro = 1
ruta_guardar = []
act_bal_chica = True
act_bal_grande = True
peso_batch = 0
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
    archivo_bd = bd.leer()
    if archivo_bd!= False:
        entrada_ruta_bd.delete("0", "end")
        entrada_ruta_bd.insert(0, (archivo_bd))
    else:
        messagebox.showinfo(message="Configure la Ruta a la Base de Datos", title="Ruta Erronea")

def leer_base():
    try:
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT nombre FROM formulas ;""")         
        combobox['values'] = list(a)           
        conexion.close()
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
        balanza_chica.port = str(entrada_puerto_chico.get()).upper()
        rutas[4] = str(entrada_puerto_chico.get()).upper()
        archivo = open(ruta_txt + "/archivo_rutas.txt", "w")
        archivo_csv = writer(archivo)
        archivo_csv.writerow(rutas)
        archivo.close()
        try:
            balanza_chica.open()
        except serial.SerialException:
            messagebox.showinfo(message="Puerto de Balanza Incorrecto", title="Error")
        else:
            balanza_chica.close()
    if y == "grande":
        balanza_grande.port = str(entrada_puerto_grande.get()).upper()
        rutas[5] = str(entrada_puerto_grande.get()).upper()
        archivo = open(ruta_txt + "/archivo_rutas.txt", "w")
        archivo_csv = writer(archivo)
        archivo_csv.writerow(rutas)
        archivo.close()
        try:
            balanza_grande.open()
        except serial.SerialException:
            messagebox.showinfo(message="Puerto de Balanza Incorrecto", title="Error")
        else:
            balanza_grande.close()

def selecionar_ruta(s):        
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

def formula_seleccionada(event,sector):
    if event == "nucleos":
        try:
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            a = conexion.execute("""SELECT * FROM %s WHERE sector = "Nucleos_Comasa";""" % combobox.get())         
            j = 0
            for s in cuadro.get_children():
                cuadro.delete(s)
            for i in a:
                cuadro.insert("", j, text=i[0], values=(i[2],i[1]))
                j +=1               
                
            conexion.close()
        except:
              messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")
    if event == "macro":
        try:
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            a = conexion.execute("""SELECT * FROM %s WHERE sector = "Macro_Comasa";""" % combobox_macro.get())         
            j = 0
            for s in cuadro_macro.get_children():
                cuadro_macro.delete(s)
            for i in a:
                cuadro_macro.insert("", j, text=i[0], values=(i[2],i[1]))
                j +=1               
                 
            conexion.close()
        except:
            messagebox.showinfo(message="Error al Conectar con Base de Datos", title="Error de Conexion")
            
    
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
    global lista_lote_macro
    global lista_vto_macro

    if(w == "nucleos"):
        if (inicio == True):
            MP_seleccionada = cuadro.item(cuadro.selection())["text"] 
                                
            lista_lote.clear()           
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            a = conexion.execute("""SELECT * FROM stock WHERE  mp = ? and estado = "Liberado";""", (MP_seleccionada,))         
            for i in list(a):
                lista_lote.append(i[2])                              
            mp_selec.delete(0, "end")
            combobox_lote.delete(0, "end")
            combobox_lote.set("")
            mp_selec.insert(0, MP_seleccionada)
            combobox_lote["values"] = lista_lote
            cantidad_pesar.delete("0", "end")
            cantidad_pesar.insert(0, "w")                
            n_debatch.delete("0", "end")
            
            cod = 1
            a = conexion.execute("""SELECT * FROM registro_fraccionado_comasa WHERE codprod = ? and mp = ? and ndebatch = (SELECT MAX(ndebatch) from registro_fraccionado_comasa) ;""", (cod, MP_seleccionada))         
            b = a.fetchone()[0]

            if b !=None:
                n_debatch.delete("0", "end")
                n_debatch.insert(0, int(b)+1)                
            else: 
                n_debatch.insert(0, 1)                 
            conexion.close()
        else:
             messagebox.showinfo(message="Debe Iniciar el Proceso", title="Error")

    if(w == "macro"):
        if (inicio_macro == True):
            MP_seleccionada_macro = cuadro_macro.item(cuadro_macro.selection())["text"]
            lista_lote_macro.clear()          
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            a = conexion.execute("""SELECT * FROM stock WHERE  mp = ? and estado = "Liberado";""", (MP_seleccionada_macro,))         
            for i in list(a):
                lista_lote.append(i[2])                              
            mp_selec_macro.delete(0, "end")
            combobox_lote_macro.delete(0, "end")
            combobox_lote_macro.set("")
            mp_selec_macro.insert(0, MP_seleccionada_macro)
            combobox_lote_macro["values"] = lista_lote_macro
            cantidad_pesar_macro.delete("0", "end")
            cantidad_pesar_macro.insert(0, "w")                
            n_debatch.delete("0", "end")          
            
        else:
             messagebox.showinfo(message="Debe Iniciar el Proceso", title="Error")

                
def ordenar(col):

    if col == "mp":
        elem = []
        elem_ordenado = []
        for t in cuadro2.get_children():
            elem.append((cuadro2.item(t)["values"]))
        elem_ordenado = sorted(elem, key=lambda x: x[2])
        for s in cuadro2.get_children():
            cuadro2.delete(s)
        for s in elem_ordenado:
            cuadro2.insert("", tk.END, text=time.strftime("%d/%m/%y"), values=(s))

def iniciar(sl):
    global inicio
    global inicio_macro
    global item
    if (sl == "nucleos"):
        
        if combobox.get() != "":
            inicio = True
            for s in cuadro2.get_children():
                cuadro2.delete(s)
            boton1["state"] = ["disable"]
            combobox["state"] = ["disable"]
            n_debatch.delete(0, "end")
            combobox_lote.delete(0, "end")
            cantidad_pesar.delete(0, "end")
            receta_seleccionada = combobox.get()
            try:
                if (str(receta_seleccionada).lower() + str(time.strftime("%d-%m-%y")) + ".txt") in str(
                        os.listdir(ruta_registro)).lower():
                    registro = open(str(ruta_registro) + "/" + str(
                        (receta_seleccionada).lower() + str(time.strftime("%d-%m-%y")) + ".txt"), "r")
                    leer_reg_nucleos = reader(registro)

                    for f in list(leer_reg_nucleos):

                        if len(f) != 0:
                            if f[9] != "Eliminado":
                                 cuadro2.insert("", tk.END, text=f[1], values=(f[2], f[0], f[3], f[4], f[5], f[7], f[6]))
            except:
                None
            combobox_lote["state"] = ["readonly"]
            mp_selec["state"] = ["enable"]
            boton_pesar["state"] = ["enable"]
            n_debatch["state"] = ["enable"]
            responsable["state"] = ["enable"]
        else:
            messagebox.showinfo(message="Seleccione una Receta", title="Error")

    if (sl == "macro"):
        if len(MP_macro) != 0:
            inicio_macro = True
            global n_fila_macro
            for s in cuadro_macro2.get_children():
                cuadro_macro2.delete(s)
            boton_iniciar_macro["state"] = ["disable"]
            combobox_macro["state"] = ["disable"]
            combobox_lote_macro.delete(0, "end")
            cantidad_pesar_macro.delete(0, "end")
            try:
                if (str(receta_seleccionada_macro).lower() + str(time.strftime("%d-%m-%y")) + ".txt") in str(
                        os.listdir(ruta_registro)).lower():
                    registro_macro = open(str(ruta_registro) + "/" + str(
                        (receta_seleccionada_macro).lower() + str(time.strftime("%d-%m-%y")) + ".txt"), "r")
                    leer_reg = reader(registro_macro)

                    for f in list(leer_reg):
                        if len(f)!=0:
                            if f[9] != "Eliminado":
                                 cuadro_macro2.insert("", tk.END, text=f[1],values=(f[2], f[0],f[3], f[4],f[5],f[7],f[6]))
            except:
                None
            combobox_lote_macro["state"] = ["readonly"]
            mp_selec_macro["state"] = ["enable"]
            boton_pesar_macro["state"] = ["enable"]
            cantidad_pesar_macro["state"] = ["enable"]
            responsable_macro["state"] = ["enable"]
            item = n_fila_macro-1
        else:
            messagebox.showinfo(message="Seleccione una Receta", title="Error")

def sin_balanza(sec):
    global item
    if(sec == "nucleos"):                
        cantidad = float(cantidad_pesar.get())
        nuevo_stock = stock - cantidad
        codprod = 1
        fecha = time.strftime("%d/%m/%y")
        hora = time.strftime("%H:%M:%S")
        Deposito = cuadro.item(cuadro.selection())["text"]        
        formula = combobox.get()        
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        conexion.execute("""insert into registro_fraccionado_comasa (codprod,ndebatch,fecha,hora,mp,deposito,lote,vto,cantidad,responsable,sector,formula)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?);""",(codprod, n_debatch.get(),fecha, hora, MP_seleccionada, Deposito, lote,vto,cantidad,responsable.get(),"nucleos_comasa",formula))
        conexion.commit()
        conexion.execute("""UPDATE stock SET stock = ? WHERE mp = ? and lote = ?;""",(nuevo_stock,MP_seleccionada,lote))
        conexion.commit()
        conexion.close()
        cuadro2.insert("", tk.END, text=fecha,
                    values=(hora, n_batch, MP_seleccionada, cantidad, lote, vto, Deposito))        
        n_debatch.delete("0", "end")
        n_debatch.insert(0, int(n_batch) + 1)
        
    if (sec == "macro"):
        codprod = 1
        fecha = time.strftime("%d/%m/%y")
        hora = time.strftime("%H:%M:%S")
        Deposito = cuadro_macro.item(cuadro_macro.selection())["text"]
        cantidad = cantidad_pesar_macro.get()
        formula = combobox_macro.get()
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        conexion.execute("""insert into registro_fraccionado_comasa (codprod,fecha,hora,mp,deposito,lote,vto,cantidad,responsable,sector,formula)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?);""",(codprod,fecha, hora, MP_seleccionada, Deposito, lote,vto,cantidad,responsable_macro.get(),"macro_comasa",formula))
        conexion.commit()
        conexion.execute("""UPDATE stock SET stock = ? WHERE mp = ? and lote = ?;""",(nuevo_stock,MP_seleccionada_macro,lote_macro))
        conexion.commit()
        conexion.close()

        cuadro_macro2.insert("", tk.END, text=fecha,
                       values=(hora,int(item),MP_seleccionada_macro, cantidad, lote_macro,
                               str(vto, Deposito)))       
        item = item + 1

def con_balanza(t):
    global peso_balanza
    peso_balanza = ""
    codprod = 1
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
                    conexion.execute("""insert into registro_fraccionado_comasa (codprod,ndebatch,fecha,hora,mp,deposito,lote,vto,cantidad,responsable,sector,formula)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?);""",(codprod, n_debatch.get(),fecha, hora, MP_seleccionada, Deposito, lote,vto,cantidad,responsable.get(),"nucleos_comasa",formula))
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
                conexion.execute("""insert into registro_fraccionado_comasa (codprod,ndebatch,fecha,hora,mp,deposito,lote,vto,cantidad,responsable,sector,formula)
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
    global n_mp
    global n_batch
    global stock
    global lote
    global vto
    global lote_macro
    n_batch = n_debatch.get()
    venc = ""
    if (sector == "nucleos"):
        lote = combobox_lote.get()
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT * FROM stock WHERE  mp = ? and lote = ? and estado = "Liberado" ;""", (MP_seleccionada,lote))         
        b = a.fetchall()[0]
        vto = b[4]
        stock = float(b[3])
        conexion.close()       
        
        try:
            venc = datetime.strptime(str(vto), "%d/%m/%Y")
        except:
            messagebox.showinfo(message="Error en Fecha de Vencimiento", title=  "Error en el formato del Archivo de lotes")
        if venc > (datetime.strptime(str(datetime.now().date()),"%Y-%m-%d")):
            if responsable.get() != "":
                
                if float(cuadro.item(cuadro.selection())["values"][0]) < 3:
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
        
    if (sector == "macro"):
        lote_macro = combobox_lote_macro.get()
        conexion=sqlite3.connect(entrada_ruta_bd.get())
        a = conexion.execute("""SELECT * FROM stock WHERE  mp = ? and lote = ? and estado = "Liberado" ;""", (MP_seleccionada,lote))         
        b = a.fetchall()[0]
        vto = b[4]
        stock = float(b[3])
        conexion.close()
        cantidad = float(cantidad_pesar_macro.get())
        nuevo_stock = stock - cantidad
        
        try:
            venc = datetime.strptime(str(vto), "%d/%m/%Y")
        except:
            messagebox.showinfo(message="Error en Fecha de Vencimiento", title=  "Error en el formato del Archivo de lotes")

        if venc > (datetime.strptime(str(datetime.now().date()),"%Y-%m-%d")):
            if responsable.get() != "":
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
            codprod=1
            ndebatch = elemento_mp[1]
            mp = elemento_mp[2]
            lote = elemento_mp[4]

            conexion=sqlite3.connect(entrada_ruta_bd.get())
            conexion.execute("""DELETE FROM registro_fraccionado_comasa WHERE codprod = ? and ndebatch = ? and mp = ? and lote = ?;""", (codprod,ndebatch,mp,lote))
            conexion.commit()
            conexion.close()
            cuadro2.delete(elemento_seleccionado)
            

    if(sect == "macro"):
        elemento_seleccionado = cuadro_macro2.selection()
        if (str(elemento_seleccionado)) == "()":
            messagebox.showinfo(message="Seleccione Elemento a Eliminar", title="Error")
        else:
            elemento_mp = cuadro_macro2.item(elemento_seleccionado)["values"]                      
            codprod=1
            ndebatch = elemento_mp[1]
            mp = elemento_mp[2]
            lote = elemento_mp[4]
            conexion=sqlite3.connect(entrada_ruta_bd.get())
            conexion.execute("""DELETE FROM registro_macro_comasa WHERE codprod = ? and ndebatch = ? and mp = ? and lote = ?;""", (codprod,ndebatch,mp,lote))
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

def autenticar():
    if(entrada_contraseña.get()=="nutri17"):
        
        entrada_puerto_grande["state"] = ["enable"]
        entrada_puerto_chico["state"] = ["enable"]
        
        boton_ruta_registro["state"] = ["enable"]
        
        des_balanza_grande["state"] = ["normal"]
        desactivar_balanza_chica["state"] = ["normal"]
    else:
        messagebox.showinfo(message="Contraseña Incorrecta", title="Contraseña Incorrecta")

ventana = Tk()
ventana.protocol("WM_DELETE_WINDOW", cerrar)
ventana.geometry("1300x650")
ventana.title("Preparacion de Nucleos")
tab_control = ttk.Notebook(ventana, width=1000, height=650)
tab_control.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_nucleos = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_nucleos.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_macro = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_macro.place(x=0, y=0, relheight=1, relwidth=1)
pestaña_config = ttk.Frame(tab_control, borderwidth=10, relief="solid")
pestaña_config.place(x=0, y=0, relheight=1, relwidth=1)
tab_control.add(pestaña_nucleos, text="Preparacion de Nucleos")
tab_control.add(pestaña_macro, text="Carga de Macro")
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
boton_ruta_bd = ttk.Button(frame_config, text="Config. Ruta", command=lambda: selecionar_ruta("lote"))
boton_ruta_registro = ttk.Button(frame_config, text="Config. Ruta", command=lambda: selecionar_ruta("registro"))

boton_ruta_bd.place(relx=0.8, rely=0.14)

boton_ruta_registro.place(relx=0.8, rely=0.55)
desactivar_balanza_chica = Button(frame_config, text="Act./Desc. Balaza",command=lambda: des_balanza("chica"),bg="green")
desactivar_balanza_chica.place(relx=0.5, rely=0.7)
des_balanza_grande = Button(frame_config, text="Act./Desc. Balaza", command=lambda: des_balanza("grande"),bg="green")
des_balanza_grande.place(relx=0.5, rely=0.8)
entrada_puerto_chico.bind("<Return>", lambda y: conf_puerto("chico"))
entrada_puerto_grande.bind("<Return>", lambda y: conf_puerto("grande"))

label_formula = ttk.Label(frame, text="Seleccionar Formula")
label_formula.place(relx=0.15, y=10)

combobox = ttk.Combobox(frame, values=recetas, width=50, state="disable")
combobox.place(relx=0.35, y=10)
combobox.bind("<<ComboboxSelected>>", partial(formula_seleccionada,"nucleos"))
cuadro = ttk.Treeview(frame, columns=("Cantidad", "Deposito"))
barra = ttk.Scrollbar(cuadro)
cuadro.column("#0", width=400, anchor="center")
cuadro.column("Cantidad", width=100, anchor="center")
cuadro.column("Deposito", width=200, anchor="center")

cuadro.heading("#0", text="MP")
cuadro.heading("Cantidad", text="Cantidad")
cuadro.heading("Deposito", text="Deposito")

cuadro.config(yscrollcommand=barra.set)
barra.config(command=cuadro.yview)
cuadro.place(x=60, y=60, relwidth=0.9, relheight=0.6)
cuadro.bind("<<TreeviewSelect>>",partial(mp_seleccionada,"nucleos"))
barra.place(relx=0.97, rely=0.17, relheight=0.81)
#Pestaña carga de macro
label_formula_macro = ttk.Label(frame_macro, text="Seleccionar Formula")
label_formula_macro.place(relx=0.15, y=10)
combobox_macro = ttk.Combobox(frame_macro, values=recetas_macro, width=50, state="disable")
combobox_macro.place(relx=0.35, y=10)
combobox_macro.bind("<<ComboboxSelected>>", partial(formula_seleccionada,"macro"))
cuadro_macro = ttk.Treeview(frame_macro, columns=("Cantidad", "N° de Bulto", "Deposito"))
barra_macro = ttk.Scrollbar(cuadro_macro)
cuadro_macro.column("#0", width=400, anchor="center")
cuadro_macro.column("Cantidad", width=100, anchor="center")
cuadro_macro.column("Deposito", width=200, anchor="center")
cuadro_macro.heading("#0", text="MP")
cuadro_macro.heading("Cantidad", text="Cantidad")
cuadro_macro.heading("Deposito", text="Deposito")
cuadro_macro.config(yscrollcommand=barra.set)
barra_macro.config(command=cuadro_macro.yview)
cuadro_macro.place(x=60, y=60, relwidth=0.9, relheight=0.6)
cuadro_macro.bind("<<TreeviewSelect>>",partial(mp_seleccionada,"macro"))
barra_macro.place(relx=0.97, rely=0.17, relheight=0.81)
label_mp_macro = ttk.Label(frame_macro2, text="Matera Prima")
label_mp_macro.place(relx=0.01, rely=0.35)
combobox_lote_macro = ttk.Combobox(frame_macro2, width=30, state="disabled")
combobox_lote_macro.place(relx=0.4, rely=0.35)
label_cantidad_macro = ttk.Label(frame_macro2, text="Kg")
cantidad_pesar_macro = ttk.Entry(frame_macro2, width=15, state="disabled", validate="key",
                           validatecommand=((frame_macro2.register(validar_entrada)), "%S"))
label_lote_macro = ttk.Label(frame_macro2, text="Lote MP")
mp_selec_macro = ttk.Entry(frame_macro2, width=30, state="disabled")
label_cantidad_macro.place(relx=0.24, rely=0.35)
cantidad_pesar_macro.place(relx=0.26, rely=0.35)
label_lote_macro.place(relx=0.35, rely=0.35)
mp_selec_macro.place(relx=0.08, rely=0.35)
label_ndebatch = ttk.Label(frame2, text="N° de Batch")
label_ndebatch.place(relx=0, rely=0.35)
n_debatch = ttk.Entry(frame2, width=7, state="disabled", validate="key",
                      validatecommand=((frame2.register(validar_entrada)), "%S"))
n_debatch.place(relx=0.07, rely=0.35)
label_mp = ttk.Label(frame2, text="Matera Prima")
label_mp.place(relx=0.12, rely=0.35)
combobox_lote = ttk.Combobox(frame2, width=20, state="disabled")
combobox_lote.place(relx=0.45, rely=0.35)
label_cantidad = ttk.Label(frame2, text="kg")
cantidad_pesar = ttk.Entry(frame2, width=10, state="disabled", validate="key",
                           validatecommand=((frame2.register(validar_entrada)), "%S"))
label_lote = ttk.Label(frame2, text="Lote MP")
mp_selec = ttk.Entry(frame2, width=20, state="disabled")
label_cantidad.place(relx=0.3, rely=0.35)
cantidad_pesar.place(relx=0.32, rely=0.35)
label_lote.place(relx=0.4, rely=0.35)
mp_selec.place(relx=0.19, rely=0.35)
label_responsable = ttk.Label(frame2, text= "Responsable")
label_responsable.place(relx=0.6, rely=0.35)
responsable = ttk.Entry(frame2, width=25, state="disabled")
responsable.place(relx=0.66, rely=0.35)
label_responsable_macro = ttk.Label(frame_macro2, text= "Responsable")
label_responsable_macro.place(relx=0.6, rely=0.35)
responsable_macro = ttk.Entry(frame_macro2, width=25, state="disabled")
responsable_macro.place(relx=0.66, rely=0.35)

#Pestaña macro
cuadro_macro2 = ttk.Treeview(frame_macro3, columns=( "Hora","Item", "MP", "Cantidad", "Lote","Vencimiento","Deposito"))
barra_macro2 = ttk.Scrollbar(cuadro_macro2)
cuadro_macro2.column("#0", width=70, anchor="w")
cuadro_macro2.column("Hora", width=70, anchor="center")
cuadro_macro2.column("Item", width=50, anchor="center")
cuadro_macro2.column("MP", width=180, anchor="center")
cuadro_macro2.column("Cantidad", width=60, anchor="center")
cuadro_macro2.column("Lote", width=150, anchor="center")
cuadro_macro2.column("Vencimiento", width=100, anchor="center")
cuadro_macro2.column("Deposito", width=100, anchor="center")
cuadro_macro2.heading("#0", text="Fecha")
cuadro_macro2.heading("Item", text="Item", command=lambda: ordenar("batch"))
cuadro_macro2.heading("Hora", text="Hora")
cuadro_macro2.heading("MP", text="MP", command=lambda: ordenar("mp"))
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
boton_eliminar_macro.place(relx=0.91, rely=0.3)
boton_nuevo_macro = ttk.Button(frame_macro, text="Nuevo", command = partial(nuevo, "macro"))
boton_nuevo_macro.place(relx=0.85, y=10)
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
cuadro2.heading("N° de Batch", text="N° de Batch", command=lambda: ordenar("batch"))
cuadro2.heading("Hora", text="Hora")
cuadro2.heading("MP", text="MP", command=lambda: ordenar("mp"))
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
boton_pesar.place(relx=0.9, rely=0.35)
boton_eliminar = ttk.Button(frame3, text="Eliminar", command = partial(eliminar, "nucleos"))
boton_eliminar.place(relx=0.91, rely=0.3)

boton_nuevo = ttk.Button(frame, text="Nuevo", command = partial(nuevo, "nucleos"))
boton_nuevo.place(relx=0.85, y=10)

leer_archivo()
leer_base()
ventana.mainloop()
