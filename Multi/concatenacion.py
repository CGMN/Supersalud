import pandas as pd

archivos_outputs=["output_a.csv","output_b.csv","output_c.csv","output_d.csv","output_e.csv","output_f.csv",
    "output_g.csv","output_h.csv","output_i.csv","output_j.csv"]
archivos_correlativos=[]
for i in archivos_outputs:
	archivos_correlativos.append(pd.read_csv(i,encoding='latin1',low_memory=False))

consolidado=pd.concat(archivos_correlativos)
consolidado=pd.concat(archivos_correlativos).reset_index(drop = True)
consolidado.to_csv('consolidado_base_especialistas.csv', encoding='latin1',index=False)
