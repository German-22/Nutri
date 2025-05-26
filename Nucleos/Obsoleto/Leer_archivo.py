import os
from csv import reader

class Leer_archivo:

    def __init__(self, archivo):
        self.archivo = archivo
    
    def leer(self):    
        if "archnucl" in os.listdir("/"):
            ruta_txt = "/archnucl"
        else:
            try:
                os.mkdir("/archnucl")
                ruta_txt = "/archnucl"
            except:
                return False   
        if self.archivo in os.listdir(ruta_txt):
            archivo = reader(open(ruta_txt + "/" + self.archivo, "r"))
            archivo = (list(archivo)[0])
            return archivo                
        else:
            return False
        