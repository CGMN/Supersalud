
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

#rut=["1.616.681-2"]
#rut=["14.285.470-8"]
#rut=["13.450.412-9"]

# rut=["6.249.403-4","1.616.681-2","14.285.470-8","15.312.391-8",
#     "15.341.395-9","14.048.954-9","8.744.345-0","24.050.211-9","7.475.384-1","26.246.649-3"]

print('\nLeyendo archivo de Ruts a consultar')
df = pd.read_csv("Ruts_a_consultar_f.csv", encoding="latin1", low_memory = False)

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

resultados=[['RUT',"Nacionalidad","nuevo_textocompleto","Eunacom","N de Profesiones","Profesion","N de Especialidades","Especialidades"]]

print("\nConectandose a la pagina de la SuperIntendencia de Salud")

from progress.bar import Bar

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
        #14.285.470-8 mas de una profesion
        #6.249.403-4
        #7.335.462-5
        #1.616.681-2  mas de una especialidad
        #13.450.412-9
        #16.609.710-K
        #17.028.841-6

        #</editor-fold>


        #<editor-fold # Profesion

        #profesion
        browser.implicitly_wait(espera)
        prof=browser.find_element_by_css_selector("#main > div > div.fill.ng-scope > div > table > tbody > tr > td:nth-child(5)").text
        profesion=texto_a_lista(prof)

        pos_eunacom=[i for i,x in enumerate(profesion) if x=='(EUNACOM)']

        #si eunacom es >0
        prof_eunacom=[]
        if len(pos_eunacom)>0 and len(profesion)==2:
            prof_eunacom.append(profesion[pos_eunacom[0]-1])
        nuevo_prof_eunacom=','.join(prof_eunacom)

        if len(pos_eunacom)>0:
            profesion.pop(pos_eunacom[0])
            profesion.pop((pos_eunacom[0]-1))

        prof_limpia=[]
        for i in range(0,len(profesion)):
            if i%2==0:
                prof_limpia.append(profesion[i])


        #</editor-fold>#


        #<editor-fold #especialidades
        #especialidad
        browser.implicitly_wait(espera)
        espe=browser.find_element_by_css_selector("#main > div > div.fill.ng-scope > div > table > tbody > tr > td:nth-child(6)").text
        especialidades=texto_a_lista(espe)
        espe_limpia=[]
        for i in range(0,len(especialidades)):
            if i%2==0:
                espe_limpia.append(especialidades[i])

        #print (espe_limpia)
        #</editor-fold>#


        #<editor-fold # copiar texto del certificado

        browser.implicitly_wait(espera)
        bb=browser.find_element_by_css_selector("#main > div > div.fill.ng-scope > div > table > tbody > tr > td:nth-child(2) > h4 > a") #para abrir el certificado
        bb.send_keys('\n')

        #Esperar texto visible para copiar_______________________________________

        sin_observaciones=[]
        con_observaciones=[]

        wait = WebDriverWait(browser, 1)

        try:
            if wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#main > div > div.fill.ng-scope > div > div > div.x_panel.col-12 > div > div:nth-child(2) > table > tbody > tr:nth-child(2) > td'),"Posee"))==True:
                sin_observaciones.append("1")
        except:
            con_observaciones.append("1")

        #________________________________________________________________________

        #copio el texto de la pagina web con el teclado
        textocompleto=browser.find_element_by_css_selector("body").text
        #print(textocompleto)

        #para separar el str en una lista
        nuevo_textocompleto=texto_a_lista(textocompleto)

        #print("\n",nuevo_textocompleto)

        nuevo_textocompleto2=','.join(nuevo_textocompleto)

        #</editor-fold>#


        #<editor-fold # depuracion de profesiones y fechas

        #posiciones de las profesiones en el texto grande para poder encontrar las fechas
        anterior_pos_prof=[i for i,x in enumerate(nuevo_textocompleto) if x=='Antecedente del Título o habilitación profesional']

        examen_en_texto = [s for s in nuevo_textocompleto if "Examen Único Nacional de Conocimientos de Medicina" in s]

        pos_texto_examen=[]
        if len(examen_en_texto)>0:
            for i in range(0,len(examen_en_texto)):
                pos_texto_examen.append(nuevo_textocompleto.index(examen_en_texto[i]))

        import re
        from datetime import datetime

        fecha_eunacom=[]
        if len(examen_en_texto)>0:
            for i in range(0,len(pos_texto_examen)):
                text = nuevo_textocompleto[pos_texto_examen[i]]
                match = re.search(r'\d{2}-\d{2}-\d{4}', text)
                date = datetime.strptime(match.group(), '%d-%m-%Y').date()
                fecha_eunacom.append(str(date))
        else:
            fecha_eunacom.append("0")
        fecha_eunacom2=','.join(fecha_eunacom)

        #obteniendo año de la profesión en el extranjero
        pos_agno_tit_prof=[]
        if len(examen_en_texto)>0:
            examen_en_texto_str=examen_en_texto[0]
            pos_agno_tit_prof.append(examen_en_texto_str.index("Año"))

        agno_tit_prof=[]
        if len(examen_en_texto)>0:
            agno_tit_prof.append(examen_en_texto_str[pos_agno_tit_prof[0]:pos_agno_tit_prof[0]+8])
            #print (agno_tit_prof)


        #quitando de la pos anterior prof el eunacom
        if len(pos_texto_examen)>0:
            o=anterior_pos_prof.index(pos_texto_examen[0]-1)
            anterior_pos_prof.pop(o)

        pos_prof=[]
        for i in range(0,len(anterior_pos_prof)):
            pos_prof.append((anterior_pos_prof[i]+1))

        fechas_prof=[]

        for i in range(0,len(pos_prof)):
            text = nuevo_textocompleto[pos_prof[i]]
            match = re.search(r'\d{2}-\d{2}-\d{4}', text)
            date = datetime.strptime(match.group(), '%d-%m-%Y').date()
            fechas_prof.append(str(date))


        prof_fecha=[]
        for i in range(0, len(prof_limpia)):
            prof_fecha.append((str(prof_limpia[i])+";"+str(fechas_prof[i])))

        nueva_prof_fecha=','.join(prof_fecha)

        #</editor-fold>#

        #me falta el año cuando son titulos extranjeros

        #<editor-fold #depuracion de especialidades y fechas

        anterior_pos_espe=[i for i,x in enumerate(nuevo_textocompleto) if x=='Antecedente de la Especialidad']


        pos_espe=[]
        for l in range(0,len(anterior_pos_espe)):
            pos_espe.append((anterior_pos_espe[l]+1))


        fechas_espe=[]

        for i in range(0,len(pos_espe)):
            text = nuevo_textocompleto[pos_espe[i]]
            match = re.search(r'\d{2}-\d{2}-\d{4}', text)
            date = datetime.strptime(match.group(), '%d-%m-%Y').date()
            fechas_espe.append(str(date))


        espe_fecha=[]
        for i in range(0, len(espe_limpia)):
            espe_fecha.append((str(espe_limpia[i])+"/"+str(fechas_espe[i])))
        espe_fecha2=','.join(espe_fecha)

        #</editor-fold>#


        #<editor-fold #Nacionalidad

        browser.implicitly_wait(espera)
        nacion=browser.find_element_by_css_selector("#main > div > div.fill.ng-scope > div > div > div.x_panel.col-12 > div > table > tbody > tr:nth-child(7) > td.ng-binding").text

        #</editor-fold>#

        if len(prof_eunacom)>0:
            resultados.append([rut[n],nacion,nuevo_textocompleto2,fecha_eunacom2,
                len(prof_eunacom),nuevo_prof_eunacom,len(espe_limpia),espe_fecha2])
        else:
            resultados.append([rut[n],nacion,nuevo_textocompleto2,fecha_eunacom2,
                len(prof_limpia),nueva_prof_fecha,len(espe_limpia),espe_fecha2])
        #bar.next()

    except:

        var = traceback.format_exc()
        resultados.append([rut[n],"0","0","0","0","0","0","0"])
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
with open("output_f.csv", "w",newline='') as f:
    writer = csv.writer(f)
    writer.writerows(resultados)
print("\nArchivo listo")

print ("\nTiempo de ejecucion:", int(time.time()-starttime)," segundos")
print ("Ejecutado a las:",time.strftime("%H:%M"),"\n")
print ("Proceso Terminado")
