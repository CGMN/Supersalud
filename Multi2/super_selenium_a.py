
#<editor-fold #modulos
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import traceback
import csv
import pandas as pd
import numpy as np
import time
from selenium.webdriver.support import expected_conditions as EC
#</editor-fold>#

#ctrl+/ para comentarios

starttime =  time.time()

f= open("Archivo_de_error.txt","w")

var=0
#ignorando errores de certificacion
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

browser = webdriver.Chrome(chrome_options=options)
browser.set_window_size(980, 720)


# rut=["6.249.403-4","1.616.681-2","14.285.470-8","15.312.391-8",
#    "15.341.395-9","15.490.509-K","14.048.954-9","8.744.345-0","24.050.211-9","7.475.384-1","26.246.649-3","26.200.561-5"]

#rut=["26.200.561-5"]

#"6.249.403-4", 1 prof 2 espec
#"1.616.681-2", 1 prof 3 espec
#"14.285.470-8", 2 prof 1 espec
#"15.312.391-8", 3 prof 1 espec
#"15.341.395-9", 2 prof eunc 1 espec
#"15.490.509-K", no se encontraron resultados
#"14.048.954-9", 1 prof eunacom 1 espec
#"8.744.345-0",
#"24.050.211-9",
#"7.475.384-1",
#"26.246.649-3",
#"26.200.561-5"


print('\nLeyendo archivo de Ruts a consultar')
df = pd.read_csv("Ruts_a_consultar_a.csv", encoding="latin1", low_memory = False)

print('\nCreando lista de Rut')

rut=[]
for i in df['RUT_FUNCIONARIO']:
 rut.append(str(i))

print("")
print (len(rut), 'Ruts a consultar')

espera=1

#Funcion que cambia de str a list
def texto_a_lista(texto):
    out = []
    buff = []
    for c in texto:
        if c == '\n':
            out.append(''.join(buff))
            buff = []
        else:
            buff.append(c)
    else:
        if buff:
           out.append(''.join(buff))
    return out

resultados=[['RUT',"N de Profesiones","Profesion","N de Especialidades","Especialidades"]]

print("\nConectandose a la pagina de la SuperIntendencia de Salud")

#from progress.bar import Bar

print("")
#bar = Bar('Procesando', fill="*",max=len(rut))

for n in range(0, len(rut)):

    try:

        #<editor-fold #Conexion

        browser.implicitly_wait(espera)
        browser.get("https://rnpi.superdesalud.gob.cl/?openForm")

        browser.implicitly_wait(espera)
        ingresar_rut=browser.find_element_by_xpath("/html/body/div[1]/div/div/div[3]/form/div/input")#la cajita donde se pone el rut
        ingresar_rut.send_keys(rut[n])

        browser.implicitly_wait(espera)
        buscar=browser.find_element_by_xpath("/html/body/div[1]/div/div/div[3]/form/div/span/button")#el boton de buscar
        buscar.send_keys('\n')  #como si fuera un click

        #</editor-fold>



        #<editor-fold # Profesion

        #profesion
        browser.implicitly_wait(espera)
        prof=browser.find_element_by_css_selector("#main > div > div.fill.ng-scope > div > table > tbody > tr > td:nth-child(5)").text
        profesion=texto_a_lista(prof)

        cant_profesiones=[]
        if len(profesion)>0:
            cant_profesiones.append(str(int(len(profesion)/2)))
        cant_profesiones=','.join(cant_profesiones)

        profesion=','.join(profesion)

        #print(profesion)

        #</editor-fold>#


        #<editor-fold #especialidades
        #especialidad
        browser.implicitly_wait(espera)
        espe=browser.find_element_by_css_selector("#main > div > div.fill.ng-scope > div > table > tbody > tr > td:nth-child(6)").text
        especialidades=texto_a_lista(espe)

        cant_especialidades=[]
        if len(especialidades)>0:
            cant_especialidades.append(str(int(len(especialidades)/2)))
        cant_especialidades=','.join(cant_especialidades)
        #print (especialidades)

        especialidades=','.join(especialidades)


        #</editor-fold>#


        resultados.append([rut[n],cant_profesiones,profesion,cant_especialidades,especialidades])
        #bar.next()

    except:
        sin_elementos=browser.find_element_by_css_selector("#main > div > div.atras-siguiente.row > div.content-mostrar.center.col-4 > span > label").text
        resultados.append([rut[n],sin_elementos,"0","0","0"])
    # except:
    #
    #     var = traceback.format_exc()
    #     resultados.append([rut[n],"0","0","0","0"])
        #bar.next()
#bar.finish()



if var !=0:
    f.write(var)
    f.close()
f.close()

browser.close()
#print ("cantidad de funcionarios consultados:", len(resultados)-1)

#escribir el archivo
print("\nEscribiendo el archivo")
with open("output_a.csv", "w",newline='') as f:
    writer = csv.writer(f)
    writer.writerows(resultados)
print("\nArchivo listo")

print ("\nTiempo de ejecucion:", int(time.time()-starttime)," segundos")
print ("Ejecutado a las:",time.strftime("%H:%M"),"\n")
print ("Proceso Terminado")
