from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests
from bs4 import BeautifulSoup
import csv
import traceback
import pandas as pd
import numpy as np
import time

starttime =  time.time()

f= open("Archivo_de_error.txt","w")

var=0

print('Leyendo archivo de Ruts a consultar')
df = pd.read_csv("Ruts_a_consultar.csv", encoding="latin1", low_memory = False)

print('Creando lista de Rut')
RUT=[]
for i in df['RUT_FUNCIONARIO']:
   RUT.append(str(i))

#RUT=["16609710","14285470","6249403","7335462","15490509","5509946","12486951","7813596","15745523",
#    "2637823","1616681","13450412","17028841"]

#6249403-4
#7335462-5
#1616681-2
#13450412-9
#16609710-K
#17028841-6
#14285470-8 tec med - med

#ignorando errores de certificacion
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

browser = webdriver.Chrome(chrome_options=options)
browser.set_window_size(780, 520)

print (len(RUT), 'Ruts a consultar')
resultados=[['RUT',"Profesion","Espe"]]

print('Realizando las consultas a la pagina web de la SuperIntendencia de salud')
for j in range(0,len(RUT)):

    try:#___________________________________________________________________________________
        #Paso 1 entrar con el RUT

        #la direccion la obtuve de Ctrl+Mayus+I, luego Network y Headers, ahi se busca entre los movimientos
        browser.get("http://webhosting.superdesalud.gob.cl/bases/prestadoresindividuales.nsf/(searchAll2)/Search?SearchView&Query=(FIELD%20rut_pres="+RUT[j]+")&Start=1&count=10")
        browser.implicitly_wait(0)

        #con esto tengo el nombre, para obtener la clase usé:
        #r = requests.get("http://webhosting.superdesalud.gob.cl/bases/prestadoresindividuales.nsf/(searchAll2)/Search?SearchView&Query=(FIELD%20rut_pres=6249403)&Start=1&count=10")
        #print(r.text) ahi sale la clase

        nombre=browser.find_element_by_class_name("showDoc").text
        browser.implicitly_wait(0)
        #___________________________________________________________________________________
        #Paso 2 click en el NOMBRE
        elm=browser.find_element_by_link_text(str(nombre))
        browser.implicitly_wait(0)
        elm.click()

        #para saber la cantidad de filas de la tabla_______________________________________________________________________________
        primer_cuadro=browser.find_elements_by_xpath("//table[@class = 'antecedente']/tbody/tr")

        profesion=[]
        profesion.append(browser.find_element_by_xpath('//*[@id="ficha"]/div/table/tbody/tr[2]/td/table/tbody/tr[1]/td[1]').text)
        profesion_limpio=','.join(profesion)
        profesion_limpio=profesion_limpio.replace("Título o habilitación profesional : ","")


        espec_lista=[]
        for i in range(2,len(primer_cuadro)+1):
            espec_lista.append(browser.find_element_by_xpath('//*[@id="ficha"]/div/table/tbody/tr[2]/td/table/tbody/tr['+str(i)+']/td[1]').text)

        espec_lista=espec_lista[::-1] #invierte el orden

        espec_lista_limpia=[]
        for i in range(0, len(espec_lista)):
            b=espec_lista[i].replace("Especialidad : ","") #quita la palabra especialidad
            espec_lista_limpia.append(b)

        #obtener las fechas desde el bloque de texto

        #Paso 3 capturar la url actual
        url=browser.current_url
        #print(url)

        #___________________________________________________________________________________
        #Paso 4 seleccionar la clave para buscar el certificado
        slice_str=url[85:117]

        #Paso 5 ingresar a la pagina del certificado
        browser.get('http://webhosting.superdesalud.gob.cl/bases/prestadoresindividuales.nsf/CertificadoRegistro?openform&pid='+str(slice_str))

        especialidad=browser.find_element_by_xpath("/html/body/form/table/tbody/tr[2]/td/div/table/tbody/tr[13]/td").text
        espe=especialidad.replace("\n"," ")
        espe=espe.replace('°','')
        espe=espe.replace('"','')
        espe=espe.replace('“','')
        espe=espe.replace('     ','')

        #cambiar las fechas
        meses_dic = {" de Enero de ":"/01/", " de Febrero de ":"/02/"," de Marzo de ":"/03/"," de Abril de ":"/04/",
            " de Mayo de ":"/05/", " de Junio de ":"/06/"," de Julio de ":"/07/"," de Agosto de ":"/08/",
            " de Septiembre de ":"/09/", " de Octubre de ":"/10/", " de Noviembre de ":"/11/", " de Diciembre de ":"/12/"}
        dias={' 1/':' 01/',' 2/':' 02/',' 3/':' 03/',' 4/':' 04/',' 5/':' 05/',' 6/':' 06/',' 7/':' 07/',' 8/':' 08/',' 9/':' 09/'}

        for n, m in meses_dic.items(): #cambiamos las fechas al hacer un loop en el diccionario
            espe = espe.replace(n, m)

        for p, t in dias.items(): #cambiamos las fechas al hacer un loop en el diccionario cuando son menores a 10
            espe = espe.replace(p, t)

        #determinar las posiciones de las fechas
        fechas_estandar=["/01/","/02/","/03/","/04/","/05/","/06/","/07/","/08/","/09/","/10/","/11/","/12/"]

        import re
        #lista con la posición de las fechas
        pos_fechas=[]   #esta mal el orden
        for r in range(0,len(fechas_estandar)):
            for m in re.finditer(fechas_estandar[r], espe):
                pos_fechas.append(m.start())
        pos_fecha_prof=pos_fechas[0]
        pos_fechas.pop(0)

        #lista con las fechas
        fechas=[]  #esta mal el orden
        for i in range(0, len(pos_fechas)):
            fechas.append(espe[(pos_fechas[i]-2):(pos_fechas[i]+8)])

        #tupla de fecha y posicion para ordenarla
        pareo_pos_fecha=[]
        for d in range(0, len(fechas)):
            pareo_pos_fecha.append((pos_fechas[d],fechas[d]))

        orden_pareo=sorted(pareo_pos_fecha) #orden de el pareo entre posicion y fechas

        #lista con las fechas ordenadas obtenidas del pareo
        fechas_ordenadas=[]
        for i in range(0,len(orden_pareo)):
            fechas_ordenadas.append(orden_pareo[i][-1])

        #unir las fechas con las Especialidades
        espec_con_fecha=[]
        for i in range(0, len(fechas_ordenadas)):
            espec_con_fecha.append([espec_lista_limpia[i],fechas_ordenadas[i]])

        espec_con_fecha_junto=[]
        for i in range(0,len(espec_con_fecha)):
            an=';'.join(espec_con_fecha[i])
            espec_con_fecha_junto.append(an)
        print (espec_con_fecha_junto)

        resultados.append([RUT[j],profesion_limpio,espe,fechas_ordenadas,espec_lista_limpia,espec_con_fecha_junto])

    except:
        var = traceback.format_exc()
        resultados.append([RUT[j],"0","0","0","0"])
        #print (var)
if var !=0:
    f.write(var)
    f.close()

f.close()


browser.close()
print ("cantidad de funcionarios consultados:", len(resultados)-1)

#___________________________________________________________________________________
with open("output.csv", "w",newline='') as f:
    writer = csv.writer(f)
    writer.writerows(resultados)

print ("")
print ("Tiempo de ejecucion:", int(time.time()-starttime)," segundos")
print ("Ejecutado a las:",time.strftime("%H:%M"))
print ("")
print ("Proceso Terminado")


#'http://webhosting.superdesalud.gob.cl/bases/prestadoresindividuales.nsf/(searchAll2)/F14E03A2D6E3930A8425763C006A2A51?OpenDocument'
#'http://webhosting.superdesalud.gob.cl/bases/prestadoresindividuales.nsf/(searchAll2)/858C30EB841BED008425763C006A0771?OpenDocument'
#'http://webhosting.superdesalud.gob.cl/bases/prestadoresindividuales.nsf/(searchAll2)/7FA56805368626AE84257850006F8C3E?OpenDocument'
