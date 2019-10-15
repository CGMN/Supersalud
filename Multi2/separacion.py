import pandas as pd
import tkinter.filedialog, re

#Permite seleccionar el archivo, abre el explorador y guarda la seleccion en la variable file_path
#______________________________________________________________________________
root = tkinter.Tk()
root.withdraw()
file_path = tkinter.filedialog.askopenfilename()

df = pd.read_csv(str(file_path), encoding="latin1", low_memory = False)

print("Cantidad de filas del archivo",len(df))
print("")

df_rut_unico = df.drop_duplicates(subset="Rut Funcionario", keep="first")

listado_rut_unico = df_rut_unico["Rut Funcionario"].tolist()
print ("Cantidad de rut unicos",len(listado_rut_unico))
print("")

partes=10

n_por_archivo=(len(listado_rut_unico)/partes)

#print(n_por_archivo)

redondeo=round(n_por_archivo)

#print(redondeo)

indices=[redondeo, redondeo*2, redondeo*3,redondeo*4,redondeo*5,redondeo*6,redondeo*7,redondeo*8,redondeo*9]

def partition(listado_rut_unico, indices):
    return [listado_rut_unico[i:j] for i, j in zip([0]+indices, indices+[None])]

#print(len(partition(listado_rut_unico,indices)))

para_nombre=['a','b','c','d','e','f','g','h','i','j']

dfa = pd.DataFrame(listado_rut_unico, columns=["RUT_FUNCIONARIO"])
dfa.to_csv('listado_rut_unico.csv', index=False)


dfs_para_grabar=[]

for i in range(0,len(partition(listado_rut_unico,indices))):
    dfs_para_grabar.append(pd.DataFrame(partition(listado_rut_unico,indices)[i], columns=["RUT_FUNCIONARIO"]))
#print(len(dfs_para_grabar))


for i in range(0,len(dfs_para_grabar)):
    dfs_para_grabar[i].to_csv('Ruts_a_consultar_'+para_nombre[i]+'.csv', index=False)


print ("Proceso terminado")
