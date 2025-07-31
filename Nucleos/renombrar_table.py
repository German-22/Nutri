import sqlite3
import re

def eliminar_foreign_key(conexion, tabla, columna_fk):
    cursor = conexion.cursor()

    # 1. Obtener SQL original de creación
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?;", (tabla,))
    row = cursor.fetchone()
    if row is None:
        print(f"❌ No se encontró la tabla '{tabla}'.")
        return

    sql_original = row[0]
    print(f"📄 SQL original:\n{sql_original}\n")

    # 2. Quitar líneas con la clave foránea especificada
    lineas = sql_original.splitlines()
    nuevas_lineas = []
    for linea in lineas:        
        if 'FOREIGN KEY("codfor")' in linea:
            print(f"🧹 Eliminando línea: {linea}")
            continue
        nuevas_lineas.append(linea)

    nueva_sql = "\n".join(nuevas_lineas)
    nueva_sql = re.sub(r",\s*\)", "\n)", nueva_sql)  # Quitar coma final inválida
    print(f"✅ CREATE TABLE nuevo:\n{nueva_sql}\n")

    # 3. Obtener las columnas existentes
    cursor.execute(f"PRAGMA table_info('{tabla}')")
    columnas = [fila[1] for fila in cursor.fetchall()]
    columnas_str = ", ".join([f'"{col}"' for col in columnas])

    # 4. Armar script SQL completo
    temp_tabla = f"{tabla}_old"

    script_sql = f"""
    PRAGMA foreign_keys=off;

    ALTER TABLE "{tabla}" RENAME TO "{temp_tabla}";

    {nueva_sql};

    INSERT INTO "{tabla}" ({columnas_str})
    SELECT {columnas_str} FROM "{temp_tabla}";

    DROP TABLE "{temp_tabla}";

    PRAGMA foreign_keys=on;
    """

    try:
        cursor.executescript(script_sql)
        conexion.commit()
        print(f"✅ Clave foránea en '{columna_fk}' eliminada de la tabla '{tabla}'.")
    except sqlite3.Error as e:
        print(f"❌ Error ejecutando el script: {e}")
        print("❗ Script generado:\n", script_sql)

  

#a = conexion.execute("""SELECT nombre FROM formulas; """)         
#b = a.fetchall()
#eliminar_foreign_key(conexion,b[9][0],columna_fk="codfor")

#for tabla in b:
#    #print(f"\n--- Procesando tabla: {tabla[0]} ---\n")
#    eliminar_foreign_key(conexion,tabla[0],columna_fk="codfor")
import pandas as pd
import sqlite3

# Ruta del archivo Excel
archivo_excel = r'C:\Users\germa\Documents\VScode\Nutri\Nucleos\despacho.xlsx'

# Leer la hoja de Excel (puede especificar el nombre o número de hoja con sheet_name)
df = pd.read_excel(archivo_excel, sheet_name=0)

# Verificar que se lea correctamente
print(df.head())

# Conexión a la base de datos SQLite
conexion = sqlite3.connect(r"C:\Users\germa\Documents\BD\nutri.db")
cursor = conexion.cursor()

# Nombre de la tabla destino
nombre_tabla = 'despacho'

# Crear tabla si no existe (ajustá los nombres/tipos de columnas según tu archivo)

# Insertar datos fila por fila
for _, fila in df.iterrows():
    cursor.execute(f'''
        INSERT INTO {nombre_tabla} (hora,producto ,vto, pallet,lote,cantidad,codprod,responsable)
        VALUES (?, ?, ?,?,?,?,?,?)
    ''', (str(fila['fecha']),"Copitas_de_Chocolate_Abanderado_600_kg",str(fila['vto']), int(fila['pallet']),str(fila['lote']),float(fila['cajas']),str(fila['cod']),"GP"))

# Confirmar cambios y cerrar conexión
conexion.commit()
conexion.close()

print("Datos insertados correctamente en la base de datos.")