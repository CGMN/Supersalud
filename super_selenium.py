from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests
from bs4 import BeautifulSoup
import csv
import traceback
import pandas as pd
import numpy as np
import tkinter.filedialog, re
import time
import dateutil.parser as dparser

starttime =  time.time()

f= open("Archivo_de_error.txt","w")

var=0

#listado con los rut para ir iterand o__________
#root = tkinter.Tk()
#root.withdraw()
#file_path = tkinter.filedialog.askopenfilename()

print('Leyendo archivo de Ruts a consultar')
df = pd.read_csv("Ruts_a_consultar.csv", encoding="latin1", low_memory = False)

print('Creando lista de Rut')
#RUT=[]
#for i in df['RUT_FUNCIONARIO']:
#   RUT.append(str(i))


print('Leyendo las especialidades')
df = pd.read_csv("Especialidades.csv", encoding="latin1", low_memory = False)

print('Creando listas de especialidades')
especialidades=[]
for i in df['Especialidades']:
   especialidades.append(str(i))


browser = webdriver.Chrome()


RUT=["6249403","7335462","15490509"]
print (len(RUT), 'Ruts a consultar')
resultados=[]

#varias especialidades
#2637823-0
#1616681-2

print('Realizando las consultas a la pagina web de la SuperIntendencia de salud')

for i in range(0,len(RUT)):

    try:#___________________________________________________________________________________
        #Paso 1 entrar con el RUT

        #la direccion la obtuve de Ctrl+Mayus+I, luego Network y Headers, ahi se busca entre los movimientos
        browser.get("http://webhosting.superdesalud.gob.cl/bases/prestadoresindividuales.nsf/(searchAll2)/Search?SearchView&Query=(FIELD%20rut_pres="+RUT[i]+")&Start=1&count=10")
        browser.implicitly_wait(0)
        #con esto tengo el nombre, para obtener la clase usé:

        #r = requests.get("http://webhosting.superdesalud.gob.cl/bases/prestadoresindividuales.nsf/(searchAll2)/Search?SearchView&Query=(FIELD%20rut_pres=6249403)&Start=1&count=10")
        #print(r.text) ahi sale la clase

        nombre=browser.find_element_by_class_name("showDoc").text
        browser.implicitly_wait(0)
        #___________________________________________________________________________________
        #Paso 2 click en el NOMBRE

        elm=browser.find_element_by_link_text(str(nombre))
        browser.implicitly_wait(5)
        elm.click()

        #___________________________________________________________________________________
        #Paso 3 capturar la url actual

        url=browser.current_url
        #print(url)

        #___________________________________________________________________________________
        #Paso 4 seleccionar la clave para buscar el certificado

        slice_str=url[85:117]
        #print(slice_str)

        #Paso 5 ingresar a la pagina del certificado
        browser.get('http://webhosting.superdesalud.gob.cl/bases/prestadoresindividuales.nsf/CertificadoRegistro?openform&pid='+str(slice_str))


        #Paso 6 Extraer la información  Ctrl+Mayus+I con eso puedo buscar los elementos, los copié como xpath
        rut=browser.find_element_by_xpath("/html/body/form/table/tbody/tr[2]/td/div/table/tbody/tr[6]/td[2]").text
        rut=rut.replace(".","")
        rut=rut.replace("-","")
        rut_corto_sin_p_g=rut[0:-1]

        titulo=browser.find_element_by_xpath("/html/body/form/table/tbody/tr[2]/td/div/table/tbody/tr[11]/td[2]/b").text

        especialidad=browser.find_element_by_xpath("/html/body/form/table/tbody/tr[2]/td/div/table/tbody/tr[13]/td").text
        espe=especialidad.replace("\n"," ")
        todas_espec=[]

        for i in range(0, len(especialidades)): #busca la especialidad en el texto
            if especialidades[i] in espe:
                todas_espec.append(str(especialidades[i]))


        espec_sin_signos=','.join(todas_espec) #para que me salga en una sola celda al mandarlo al archivo

        #cambiar las fechas
        meses_dic = {" de Enero de ":"/01/", " de Febrero de ":"/02/"," de Marzo de ":"/03/"," de Abril de ":"/04/",
            " de Mayo de ":"/05/", " de Junio de ":"/06/"," de Julio de ":"/07/"," de Agosto de ":"/08/",
            " de Septiembre de ":"/09/", " de Octubre de ":"/10/", " de Noviembre de ":"/11/", " de Diciembre de ":"/12/"}
        dias={' 1/':' 01/',' 2/':' 02/',' 3/':' 03/',' 4/':' 04/',' 5/':' 05/',' 6/':' 06/',' 7/':' 07/',' 8/':' 08/',' 9/':' 09/'}

        for i, j in meses_dic.items(): #cambiamos las fechas al hacer un loop en el diccionario
            espe = espe.replace(i, j)

        for i, j in dias.items(): #cambiamos las fechas al hacer un loop en el diccionario cuando son menores a 10
            espe = espe.replace(i, j)

        espe=espe.replace('°','')
        espe=espe.replace('"','')
        espe=espe.replace('“','')
        espe=espe.replace('     ','')

        #determinar las posiciones de las fechas
        fechas_estandar=["/01/","/02/","/03/","/04/","/05/","/06/","/07/","/08/","/09/","/10/","/11/","/12/"]

        import re
        pos_fechas=[]
        for j in range(0,len(fechas_estandar)):
            for m in re.finditer(fechas_estandar[j], espe):
                pos_fechas.append(m.start())

        print ('pos fechas',pos_fechas)

        #determinar la ubicación de las especialidades
        pos_especial=[]
        for j in range(0,len(especialidades)):
            for m in re.finditer(especialidades[j], espe):
                pos_especial.append(m.start())
        print ('pos especialidades',pos_especial)

        #fechas
        fechas=[]
        print(espe[(pos_fechas[0]-2):(pos_fechas[0]+7)])
        #fecha1=espe[espe[pos_fechas[0]:85]]
        #print (fecha1)


        #agregar las fechas a las especialidades


        resultados.append([rut_corto_sin_p_g,titulo,espe,espec_sin_signos])

    except:
        var = traceback.format_exc()
        resultados.append([RUT[i],"0","0"])
        #print (var)
if var !=0:
    f.write(var)
    f.close()
    #print ("")
    #print (" X X X X X X X X X X X X X X X X X X ")
    #print ("")
    #print ("El programa arroja un error")
    #print ("Se ha creado un archivo llamado 'Archivo_de_error' con el detalle")
    #print ("")
    #print (" X X X X X X X X X X X X X X X X X X ")

f.close()


browser.close()
print ("cantidad de funcionarios consultados:", len(resultados))

#___________________________________________________________________________________

with open("output.csv", "w",newline='') as f:
    writer = csv.writer(f)
    writer.writerows(resultados)

print ("tiempo de ejecucion:", int(time.time()-starttime)," segundos")
print("terminado")


#'http://webhosting.superdesalud.gob.cl/bases/prestadoresindividuales.nsf/(searchAll2)/F14E03A2D6E3930A8425763C006A2A51?OpenDocument'
#'http://webhosting.superdesalud.gob.cl/bases/prestadoresindividuales.nsf/(searchAll2)/858C30EB841BED008425763C006A0771?OpenDocument'
#'http://webhosting.superdesalud.gob.cl/bases/prestadoresindividuales.nsf/(searchAll2)/7FA56805368626AE84257850006F8C3E?OpenDocument'
