import sys
sys.path.append(r"c:\users\germa\appdata\local\programs\python\python311\lib\site-packages" )
from pandas import read_excel
from datetime import datetime
import serial
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import *
import os
import time
from csv import reader, writer
from functools import partial
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
    global rutas, ruta_txt, ruta_lote, ruta_receta, ruta_receta_macro, ruta_registro,recetas, recetas_macro, lotes
    

    if "archnucl" in os.listdir("/"):
        ruta_txt = "/archnucl"
    else:
        try:
            os.mkdir("/archnucl")
            ruta_txt = "/archnucl"
        except:
            messagebox.showinfo(message="No se Creo el Dir. del Archivo de Rutas", title="Error al Crear el Directorio")

    if "archivo_rutas.txt" in os.listdir(ruta_txt):
        archivo_rutas = reader(open(ruta_txt + "/archivo_rutas.txt", "r"))

        for i in archivo_rutas:
            rutas.append(i)
        if len(rutas) > 0:
            rutas = rutas[0]
            if len(rutas) == 6:
                ruta_lote = rutas[0]
                ruta_receta = rutas[1]
                ruta_receta_macro = rutas[2]
                ruta_registro = rutas[3]
                puerto_balanza_chica = rutas[4]
                puerto_balanza_grande = rutas[5]
                recetas = os.listdir(ruta_receta)
                recetas_macro = os.listdir(ruta_receta_macro)
                lotes = os.listdir(ruta_lote)
                entrada_ruta_lote.insert(0, str(ruta_lote))
                entrada_ruta_receta.insert(0, str(ruta_receta))
                entrada_ruta_receta_macro.insert(0, str(ruta_receta_macro))
                entrada_ruta_registro.insert(0, str(ruta_registro))
                if puerto_balanza_chica != "":
                    entrada_puerto_chico.insert(0, str(puerto_balanza_chica))
                    balanza_chica.port = str(puerto_balanza_chica)
                if puerto_balanza_grande != "":
                    entrada_puerto_grande.insert(0, str(puerto_balanza_grande))
                    balanza_grande.port = str(puerto_balanza_grande)
                entrada_ruta_lote["state"] = ["disable"]
                entrada_ruta_receta["state"] = ["disable"]
                entrada_ruta_receta_macro["state"] = ["disable"]
                entrada_ruta_registro["state"] = ["disable"]
                entrada_puerto_grande["state"] = ["disable"]
                entrada_puerto_chico["state"] = ["disable"]
                boton_ruta_lote["state"] = ["disable"]
                boton_ruta_receta["state"] = ["disable"]
                boton_ruta_registro["state"] = ["disable"]
                boton_ruta_receta_macro["state"] = ["disable"]
                des_balanza_grande["state"] = ["disable"]
                desactivar_balanza_chica["state"] = ["disable"]
            else:
                archivo = open(ruta_txt + "/archivo_rutas.txt", "w")
                archivo.close()
                rutas.clear()
                messagebox.showinfo(message="Configure las Rutas", title="Ruta Erronea")
        else:
            messagebox.showinfo(message="Configure las Rutas", title="Ruta Erronea")
    else:
        messagebox.showinfo(message="Configure las Rutas", title="Ruta Erronea")

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

def selecionar_ruta(ruta):
    if ruta == "lote":
        ruta_lote = filedialog.askdirectory(initialdir="/", title="Seleccionar el Archivo de Ingreso de MP")                                        
        entrada_ruta_lote.delete("0", "end")
        entrada_ruta_lote.insert(0, str(ruta_lote))
        ruta_guardar.append(ruta_lote)
    if ruta == "receta":
        ruta_receta = filedialog.askdirectory(initialdir="/", title="Seleccionar Carpeta de Recetas")
        entrada_ruta_receta.delete("0", "end")
        entrada_ruta_receta.insert(0, str(ruta_receta))
        ruta_guardar.append(ruta_receta)
    if ruta == "receta macro":
        ruta_receta_macro = filedialog.askdirectory(initialdir="/", title="Seleccionar Carpeta de Recetas")
        entrada_ruta_receta_macro.delete("0", "end")
        entrada_ruta_receta_macro.insert(0, str(ruta_receta_macro))
        ruta_guardar.append(ruta_receta_macro)
    if ruta == "registro":
        ruta_registro = filedialog.askdirectory(initialdir="/", title="Seleccionar Carpeta Registros")
        entrada_ruta_registro.delete("0", "end")
        entrada_ruta_registro.insert(0, str(ruta_registro))
        ruta_guardar.append(ruta_registro)
        ruta_guardar.append("COM4")
        ruta_guardar.append("COM5")
    try:
        archivo = open(ruta_txt + "/archivo_rutas.txt", "w")
        archivo_csv = writer(archivo)
        archivo_csv.writerow(ruta_guardar)
        archivo.close()
    except:
        None

def formula_seleccionada(event, sl):
    global receta_seleccionada
    global receta_seleccionada_macro
    global df
    global df_lote
    global df_mp
    global df_deposito
    global peso_batch
    global df_vto
    global MP
    global cantidades
    global Deposito
    global MP_macro
    global cantidades_macro
    global Deposito_macro
    
    
    ti_m = time.ctime(os.path.getmtime(ruta_lote + "/"+ lotes[0]))
    m_ti = lotes.index(lotes[0])
    
    for i in lotes:
        if ti_m < time.ctime(os.path.getmtime(ruta_lote + "/"+ i)):
            ti_m = time.ctime(os.path.getmtime(ruta_lote + "/"+ i))
            m_ti = lotes.index(i)
    
       
    try:
        df = read_excel(io=ruta_lote + "/" + lotes[m_ti], sheet_name="REGISTRO", header=5)
        
        df_lote = df["LOTE"].tolist()
        df_mp = df["MATERIA PRIMA"].tolist()
        df_deposito = df["DEPOSITO"].tolist()
        df_vto = df["FECHA VTO"]
        j = 0

        for i in (df_lote):
            df_lote[j] = str(df_lote[j]).lower()
            df_mp[j] = str(df_mp[j]).lower()
            df_deposito[j] = str(df_deposito[j]).lower()
            df_vto[j] = str(df_vto[j]).lower()[0:10]
            j = j + 1
    except:
            messagebox.showinfo(message="Error en el Formato del Archivo de Lotes", title="Error")
     
    if (event == "nucleos"):
        MP.clear()
        Deposito = []
        nde_bulto = []
        receta_seleccionada = combobox.get()
        df_receta = read_excel(io=(ruta_receta + "/" + receta_seleccionada), sheet_name="Hoja1", header=0)
        MP = df_receta["Materia Prima"].tolist()
        cantidades = df_receta["Cantidad"].tolist()
        nde_bulto = df_receta["Bulto"].tolist()
        Deposito = df_receta["Deposito"].tolist()
        j = 0
        peso_batch = 0
        for s in cuadro.get_children():
            cuadro.delete(s)

        for mp in (MP):
            cantidades[j] = float(cantidades[j])
            nde_bulto[j] = int(nde_bulto[j])
            Deposito[j] = str(Deposito[j].lower())
            cuadro.insert("", j, text=mp, values=(cantidades[j], int(nde_bulto[j]), Deposito[j]))
            peso_batch = peso_batch + float(cantidades[j])
            j = j + 1

    if (event == "macro"):
        MP_macro.clear()
        Deposito_macro = []
        receta_seleccionada_macro = combobox_macro.get()
        df_receta = read_excel(io=(ruta_receta_macro + "/" + receta_seleccionada_macro), sheet_name="Hoja1", header=0)
        MP_macro = df_receta["Materia Prima"].tolist()
        cantidades_macro = df_receta["Cantidad"].tolist()
        Deposito_macro = df_receta["Deposito"].tolist()
        peso_batch = 0
        j =0
        for s in cuadro_macro.get_children():
            cuadro_macro.delete(s)

        for mp in (MP_macro):
            cantidades_macro[j] = float(cantidades_macro[j])
            Deposito_macro[j] = str(Deposito_macro[j].lower())
            cuadro_macro.insert("", j, text=mp, values=(cantidades_macro[j], Deposito_macro[j]))
            peso_batch = peso_batch + float(cantidades_macro[j])
            j = j + 1

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
    global lista_lote
    global lista_vto
    global lista_lote_macro
    global lista_vto_macro

    if(w == "nucleos"):
        if (inicio == True):
            MP_seleccionada = cuadro.item(cuadro.selection())["text"]
            if MP_seleccionada != mp_selec.get():
                lista_vto.clear()
                lista_lote.clear()
                i = 0
                for o in df_mp:
                    if str(o).lower() == str(MP_seleccionada).lower():
                        if (df_deposito[i]==cuadro.item(cuadro.selection())["values"][2]):
                            lista_lote.append(df_lote[i])
                            lista_vto.append(df_vto[i])
                    i = i + 1
                mp_selec.delete(0, "end")
                combobox_lote.delete(0, "end")
                combobox_lote.set("")
                mp_selec.insert(0, MP_seleccionada)
                combobox_lote["values"] = lista_lote
                cantidad_pesar.delete("0", "end")
                cantidad_pesar.insert(0, float(cantidades[MP.index(MP_seleccionada)]))
                n_batch=0
                n_debatch.delete("0", "end")
                try:
                    if (str(receta_seleccionada).lower() + str(time.strftime("%d-%m-%y")) + ".txt") in str(
                            os.listdir(ruta_registro)).lower():
                        registro = open(str(ruta_registro) + "/" + str(
                            (receta_seleccionada).lower() + str(time.strftime("%d-%m-%y")) + ".txt"), "r")
                        leer_reg_nucleos = reader(registro)
                        lista = (list(leer_reg_nucleos))
                        lote = []
                        for f in lista:
                            if len(f) != 0 and f[9] != "Eliminado":
                                if str(f[3])==str(MP_seleccionada):
                                   n_batch+=1
                                   lote = f[5][2:len(f[5])-2]
                            combobox_lote.set(str(lote))
                except:
                    None
                if n_batch == 0:
                    n_debatch.insert(0, 1)
                    n_batch = 1
                else:
                    n_debatch.delete("0", "end")
                    n_debatch.insert(0, n_batch+1)
        else:
             messagebox.showinfo(message="Debe Iniciar el Proceso", title="Error")

    if(w == "macro"):
        if (inicio_macro == True):
            MP_seleccionada_macro = cuadro_macro.item(cuadro_macro.selection())["text"]
            if MP_seleccionada_macro != mp_selec_macro.get():
                lista_vto_macro.clear()
                lista_lote_macro.clear()
                i = 0
                for o in df_mp:
                    if str(o).lower() == str(MP_seleccionada_macro).lower():
                        if (df_deposito[i] == cuadro_macro.item(cuadro_macro.selection())["values"][1]):
                            lista_lote_macro.append(df_lote[i])
                            lista_vto_macro.append(df_vto[i])
                    i = i + 1
                mp_selec_macro.delete(0, "end")
                combobox_lote_macro.delete(0, "end")
                combobox_lote_macro.set("")
                mp_selec_macro.insert(0,MP_seleccionada_macro)
                combobox_lote_macro["values"]=lista_lote_macro
                cantidad_pesar_macro.delete("0", "end")
                cantidad_pesar_macro.insert(0, float(cantidades_macro[MP_macro.index(MP_seleccionada_macro)]))
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
        if len(MP) != 0:
            inicio = True
            for s in cuadro2.get_children():
                cuadro2.delete(s)
            boton1["state"] = ["disable"]
            combobox["state"] = ["disable"]
            n_debatch.delete(0, "end")
            combobox_lote.delete(0, "end")
            cantidad_pesar.delete(0, "end")
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
        cantidad = cantidad_pesar.get()
        cuadro2.insert("", tk.END, text=time.strftime("%d/%m/%y"),
                       values=(time.strftime("%H:%M:%S"), n_batch, MP_seleccionada, cantidad, lote,str(lista_vto[lista_lote.index(lote)]), Deposito[MP.index(MP_seleccionada)]))
        registro = open(ruta_registro + "/" +str(receta_seleccionada).lower() + str(time.strftime("%d-%m-%y")) + ".txt", "a", newline="")
        registro_csv = writer(registro)
        registro_csv.writerow([n_batch,time.strftime("%d/%m/%y"),time.strftime("%H:%M:%S"), MP_seleccionada,[cantidad],[lote],[Deposito[MP.index(MP_seleccionada)]],[str(lista_vto[lista_lote.index(lote)])],[str(responsable.get())],[]])
        n_debatch.delete("0", "end")
        n_debatch.insert(0, int(n_batch) + 1)

    if (sec == "macro"):
        cantidad = cantidad_pesar_macro.get()
        cuadro_macro2.insert("", tk.END, text=time.strftime("%d/%m/%y"),
                       values=(time.strftime("%H:%M:%S"),int(item),MP_seleccionada_macro, cantidad, lote_macro,
                               str(lista_vto_macro[lista_lote_macro.index(lote_macro)]), Deposito_macro[MP_macro.index(MP_seleccionada_macro)]))
        registro_macro = open(
            ruta_registro + "/" + str((receta_seleccionada_macro).lower() + str(time.strftime("%d-%m-%y")) + ".txt"),
            "a",newline="")
        registro_macro_csv = writer(registro_macro)
        registro_macro_csv.writerow([item, time.strftime("%d/%m/%y"), time.strftime("%H:%M:%S"), MP_seleccionada_macro, [cantidad], [lote_macro], Deposito_macro[MP_macro.index(MP_seleccionada_macro)],str(lista_vto_macro[lista_lote_macro.index(lote_macro)]),[str(responsable_macro.get())],[]])
        item = item + 1

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

                cuadro2.insert("", tk.END, text=time.strftime("%d/%m/%y"),
                               values=(time.strftime("%H:%M:%S"), n_batch, MP_seleccionada, peso_mostrar, lote,str(lista_vto[lista_lote.index(lote)]),Deposito[MP.index(MP_seleccionada)]))
                registro = open(
                    ruta_registro + "/" + str(receta_seleccionada).lower() + str(time.strftime("%d-%m-%y")) + ".txt",
                    "a", newline="")
                registro_csv = writer(registro)
                registro_csv.writerow(
                    [n_batch, time.strftime("%d/%m/%y"), time.strftime("%H:%M:%S"), MP_seleccionada, [peso_mostrar],
                     [lote], [Deposito[MP.index(MP_seleccionada)]], [str(lista_vto[lista_lote.index(lote)])],
                     [str(responsable.get())], []])
                registro.close()
                n_fila = n_fila + 1
                n_debatch.delete("0", "end")
                n_debatch.insert(0, int(n_batch) + 1)
            else:
                messagebox.showinfo(message="El Peso en la Balanza no es Estable", title="Error en Balanza")
        else:
            cuadro2.insert("", tk.END, text=time.strftime("%d/%m/%y"),
                           values=(time.strftime("%H:%M:%S"), n_batch, MP_seleccionada, peso_balanza[1:7], lote,
                                   str(lista_vto[lista_lote.index(lote)]), Deposito[MP.index(MP_seleccionada)]))
            registro = open(
                ruta_registro + "/" + str(receta_seleccionada).lower() + str(time.strftime("%d-%m-%y")) + ".txt",
                "a", newline="")
            registro_csv = writer(registro)
            registro_csv.writerow(
                [n_batch, time.strftime("%d/%m/%y"), time.strftime("%H:%M:%S"), MP_seleccionada, [peso_balanza[1:7]],
                 [lote], [Deposito[MP.index(MP_seleccionada)]], [str(lista_vto[lista_lote.index(lote)])],
                 [str(responsable.get())], []])
            registro.close()
            n_fila = n_fila + 1
            n_debatch.delete("0", "end")
            n_debatch.insert(0, int(n_batch) + 1)

    else:
        messagebox.showinfo(message="Balanza no Conectada", title="Error en Balanza")

def pesar(sector):
    global n_mp
    global n_batch
    global hs
    global lote
    global vto
    global lote_macro
    n_batch = n_debatch.get()
    venc = ""
    if (sector == "nucleos"):
        lote = combobox_lote.get()
        try:
            venc = datetime.strptime(str(lista_vto[lista_lote.index(lote)]), "%Y-%m-%d")
        except:
            try:
                venc = datetime.strptime(str(lista_vto[lista_lote.index(lote)]), "%d-%m-%Y")
            except:
                messagebox.showinfo(message="Error en Fecha de Vencimiento", title=  "Error en el formato del Archivo de lotes")
        if lote in lista_lote and venc!= "":
            if venc > (datetime.strptime(str(datetime.now().date()),"%Y-%m-%d")):
                if responsable.get() != "":

                    if float(cantidades[MP.index(MP_seleccionada)]) < 3:
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
        else:
            messagebox.showinfo(message="Lote Incorrecto", title="Error en el Lote")

    if (sector == "macro"):
        lote_macro = combobox_lote_macro.get()
        try:
            venc = datetime.strptime(str(lista_vto_macro[lista_lote_macro.index(lote_macro)]), "%Y-%m-%d")
        except:
            try:
                    venc = datetime.strptime(str(lista_vto_macro[lista_lote_macro.index(lote_macro)]), "%d-%m-%Y")
            except:
                messagebox.showinfo(message="Error en el formato del Archivo de lotes",
                                    title="Error en Fecha de Vencimiento")
        if lote_macro in lista_lote_macro and venc!="":
            if venc > (datetime.strptime(str(datetime.now().date()),"%Y-%m-%d")):
                    if responsable_macro.get() != "":
                        presiono = time.time()
                        sin_balanza("macro")
                    else:
                        messagebox.showinfo(message="INGRESE EL RESPONSABLE", title="ERROR")

            else:
                    messagebox.showinfo(message="La Materia Prima Esta Vencida", title="Materia Prima Vencida")
        else:
                messagebox.showinfo(message="Lote Incorrecto", title="Error en el Lote")

def eliminar(sect):
    if(sect == "nucleos"):
        elemento_seleccionado = cuadro2.selection()
        if (str(elemento_seleccionado)) == "()":
            messagebox.showinfo(message="Seleccione Elemento a Eliminar", title="Error")
        else:
            elemento_mp = cuadro2.item(elemento_seleccionado)["values"]
            elemento_batch = elemento_mp[1]

            registro = open(str(ruta_registro) + "/" + str(
                (receta_seleccionada).lower() + str(time.strftime("%d-%m-%y")) + ".txt"), "r")
            leer_reg = reader(registro)
            reg = list(leer_reg)
            registro = open(
                ruta_registro + "/" + str(
                    (receta_seleccionada).lower() + str(time.strftime("%d-%m-%y")) + ".txt"),
                "w")
            for f in list(reg):
                if len(f) != 0:

                    if str(f[0]) == str(elemento_batch):
                        if str(f[3]) == str(elemento_mp[2]):
                            registro_csv = writer(registro)
                            registro_csv.writerow([f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], "Eliminado"])
                        else:
                            registro_csv = writer(registro)
                            registro_csv.writerow([f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9]])
                    else:
                        registro_csv = writer(registro)
                        registro_csv.writerow([f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9]])
            cuadro2.delete(elemento_seleccionado)
            registro.close()

    if(sect == "macro"):
        elemento_seleccionado = cuadro_macro2.selection()
        if (str(elemento_seleccionado)) == "()":
            messagebox.showinfo(message="Seleccione Elemento a Eliminar", title="Error")
        else:
            elemento_mp = cuadro_macro2.item(elemento_seleccionado)["values"]
            elemento_batch = elemento_mp[1]

            registro_macro = open(str(ruta_registro) + "/" + str(
                (receta_seleccionada_macro).lower() + str(time.strftime("%d-%m-%y")) + ".txt"), "r")
            leer_reg = reader(registro_macro)
            reg = list(leer_reg)
            registro_macro = open(
                ruta_registro + "/" + str(
                    (receta_seleccionada_macro).lower() + str(time.strftime("%d-%m-%y")) + ".txt"),
                "w")

            for f in list(reg):
                if len(f) != 0:
                    if str(f[0])==str(elemento_batch):
                        if str(f[3]) == str(elemento_mp[2]):
                            registro_macro_csv = writer(registro_macro)
                            registro_macro_csv.writerow([f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7],f[8],"Eliminado"])
                        else:
                            registro_macro_csv = writer(registro_macro)
                            registro_macro_csv.writerow([f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7],f[8],f[9]])
                    else:
                        registro_macro_csv = writer(registro_macro)
                        registro_macro_csv.writerow([f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9]])

            cuadro_macro2.delete(elemento_seleccionado)
            registro_macro.close()

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
        probar_balanza()
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
        entrada_ruta_lote["state"] = ["enable"]
        entrada_ruta_receta["state"] = ["enable"]
        entrada_ruta_receta_macro["state"] = ["enable"]
        entrada_ruta_registro["state"] = ["enable"]
        entrada_puerto_grande["state"] = ["enable"]
        entrada_puerto_chico["state"] = ["enable"]
        boton_ruta_lote["state"] = ["enable"]
        boton_ruta_receta["state"] = ["enable"]
        boton_ruta_registro["state"] = ["enable"]
        boton_ruta_receta_macro["state"] = ["enable"]
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


label_ruta_lote = ttk.Label(frame_config, text="Ruta al Archivo de Lotes             ")
label_ruta_receta = ttk.Label(frame_config, text="Ruta a la Carpeta de Recetas       ")
label_ruta_registro = ttk.Label(frame_config, text="Ruta a la Carpeta de Registros")
label_ruta_receta_macro = ttk.Label(frame_config, text="Ruta a la Carpeta de Recetas de Macro      ")
label_ruta_lote.place(relx=0.05, rely=0.14)
label_ruta_receta.place(relx=0.05, rely=0.28)
label_ruta_receta_macro.place(relx=0.05, rely=0.42)
label_ruta_registro.place(relx=0.05, rely=0.55)
label_puerto_chico = ttk.Label(frame_config, text="Puerto Balanza Chica             ")
label_puerto_chico.place(relx=0.05, rely=0.7)
label_puerto_grande = ttk.Label(frame_config, text="Puerto Balanza Grande             ")
label_puerto_grande.place(relx=0.05, rely=0.8)

entrada_ruta_lote = ttk.Entry(frame_config, width=80)
entrada_ruta_receta = ttk.Entry(frame_config, width=80)
entrada_ruta_receta_macro = ttk.Entry(frame_config, width=80)
entrada_ruta_registro = ttk.Entry(frame_config, width=80)
entrada_puerto_chico = ttk.Entry(frame_config, width=20)
entrada_puerto_grande = ttk.Entry(frame_config, width=20)
entrada_ruta_lote.place(relx=0.27, rely=0.14)
entrada_ruta_receta.place(relx=0.27, rely=0.28)
entrada_ruta_receta_macro.place(relx=0.27, rely=0.42)
entrada_ruta_registro.place(relx=0.27, rely=0.55)
entrada_puerto_chico.place(relx=0.27, rely=0.7)
entrada_puerto_grande.place(relx=0.27, rely=0.8)
boton_ruta_lote = ttk.Button(frame_config, text="Config. Ruta", command=lambda: selecionar_ruta("lote"))
boton_ruta_receta = ttk.Button(frame_config, text="Config. Ruta", command=lambda: selecionar_ruta("receta"))
boton_ruta_receta_macro = ttk.Button(frame_config, text="Config. Ruta", command=lambda: selecionar_ruta("receta macro"))
boton_ruta_registro = ttk.Button(frame_config, text="Config. Ruta", command=lambda: selecionar_ruta("registro"))

boton_ruta_lote.place(relx=0.8, rely=0.14)
boton_ruta_receta.place(relx=0.8, rely=0.28)
boton_ruta_receta_macro.place(relx=0.8, rely=0.42)
boton_ruta_registro.place(relx=0.8, rely=0.55)
desactivar_balanza_chica = Button(frame_config, text="Act./Desc. Balaza",command=lambda: des_balanza("chica"),bg="green")
desactivar_balanza_chica.place(relx=0.5, rely=0.7)
des_balanza_grande = Button(frame_config, text="Act./Desc. Balaza", command=lambda: des_balanza("grande"),bg="green")
des_balanza_grande.place(relx=0.5, rely=0.8)
entrada_puerto_chico.bind("<Return>", lambda y: conf_puerto("chico"))
entrada_puerto_grande.bind("<Return>", lambda y: conf_puerto("grande"))

label_formula = ttk.Label(frame, text="Seleccionar Formula")
label_formula.place(relx=0.15, y=10)
leer_archivo()
combobox = ttk.Combobox(frame, values=recetas, width=50, state="disable")
combobox.place(relx=0.35, y=10)
combobox.bind("<<ComboboxSelected>>", partial(formula_seleccionada,"nucleos"))
cuadro = ttk.Treeview(frame, columns=("Cantidad", "N° de Bulto", "Deposito"))
barra = ttk.Scrollbar(cuadro)
cuadro.column("#0", width=400, anchor="center")
cuadro.column("Cantidad", width=100, anchor="center")
cuadro.column("Deposito", width=200, anchor="center")
cuadro.column("N° de Bulto", width=100, anchor="center")
cuadro.heading("#0", text="MP")
cuadro.heading("Cantidad", text="Cantidad")
cuadro.heading("Deposito", text="Deposito")
cuadro.heading("N° de Bulto", text="N° de Bulto")
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
ventana.mainloop()
