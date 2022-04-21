import json
from flask import Flask, request
from flask_ngrok import run_with_ngrok
import pandas as pd
from flask_cors import CORS
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import NearestNeighbors
from json import loads
import warnings
warnings.filterwarnings('ignore')

#Para escritorio
calificaciones_peliculas= pd.read_csv('ratings_small.csv')
conjunto_enlaces=pd.read_csv('links.csv')
informacion_peliculas=pd.read_csv('movies_metadata.csv')

caracteristicas_pelicula = calificaciones_peliculas.pivot(
   index='movieId',
    columns='userId',
    values='rating'
).fillna(0)
sparse_movies = csr_matrix(caracteristicas_pelicula.values)
model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=13, n_jobs=-1)
model_knn.fit(sparse_movies)  
def recomendar(userId):
    pelicula_seleccionada=int(escoger_pelicula_mas_punteada(userId))
    tabla_indice=caracteristicas_pelicula.reset_index()
    filtro=tabla_indice["movieId"]==pelicula_seleccionada
    pelicula=tabla_indice[filtro]
    indice=pelicula.index.tolist()[0]
    return hacer_recomendadion(caracteristicas_pelicula,4,indice)
    
def hacer_recomendadion(caracteristicas_pelicula, numero_recomendaciones,info_pelicula):
    recomedaciones=[]
    respuesta_indice = info_pelicula
    distancias, indices = model_knn.kneighbors(caracteristicas_pelicula.iloc[respuesta_indice,:].values.reshape(1, -1), n_neighbors =numero_recomendaciones )
    recomedaciones.append(caracteristicas_pelicula.index[respuesta_indice])
    for i in range(1, len(distancias.flatten())):
        recomedaciones.append(indices.flatten()[i])
    return recomedaciones
def escoger_pelicula_mas_punteada (userId):
    usuarios_data_fame=pd.DataFrame()
    usuarios_data_fame["clasificacion"]=caracteristicas_pelicula[userId]
    filtro=usuarios_data_fame["clasificacion"]>=4.0
    
    df_ranking=usuarios_data_fame[filtro]
    df_ranking=df_ranking.reset_index()
    aleatorio = df_ranking.sample()
    indice=aleatorio.index.tolist()[0]
    return df_ranking["movieId"][indice]
   
def buscar_pelicula(inuser):
    recomend=recomendar(inuser)
    arreglo_tmdbId=[]
    for inrt in recomend:
        filtro=conjunto_enlaces["movieId"]==inrt
        link=conjunto_enlaces[filtro]
        if(link.empty): 
            return 0
            
        else:
            copy=link.copy(deep=True)
            copy.dropna(subset = ["tmdbId"], inplace=True)
            if copy.empty == True: 
                return 0
            else:  
                arreglo_tmdbId.append(str(int(link["tmdbId"].tolist()[0])))
           

    return arreglo_tmdbId
def recomendation_movie(userId):   
    movies = buscar_pelicula(userId)
    while(movies ==0):
        movies = buscar_pelicula(userId)
    datset_recomendacion=pd.DataFrame(columns=["title","imdb","sinopsis","date","image"])

    for mov in movies:
        filtro=informacion_peliculas["id"]==mov
        pelicula=informacion_peliculas[filtro]
        copy=pelicula.copy(deep=True)
        copy.dropna(subset = ["belongs_to_collection"], inplace=True)
        if copy.empty == True:  
            url_imagen="https://www.initcoms.com/wp-content/uploads/2020/07/404-error-not-found-1.png"
            datset_recomendacion=datset_recomendacion.append({"title":pelicula["original_title"].tolist()[0],"imdb":pelicula["imdb_id"].tolist()[0],"sinopsis":pelicula["tagline"].tolist()[0],"date":pelicula["release_date"].tolist()[0],"image":url_imagen},ignore_index=True)
        else:
            stringJson=pelicula["belongs_to_collection"].tolist()[0]
            replaces1=stringJson.replace("'s",'s').replace("None",'"None"').replace("'",'"')
            #replaces2=replaces1.replace("None",'"None"')
            #replaces=replaces2.replace("'",'"')
            jsonpelicula=loads(replaces1)
            imagen="https://image.tmdb.org/t/p/w500/"+jsonpelicula["poster_path"]
            datset_recomendacion=datset_recomendacion.append({"title":pelicula["original_title"].tolist()[0],"imdb":pelicula["imdb_id"].tolist()[0],"sinopsis":pelicula["tagline"].tolist()[0],"date":pelicula["release_date"].tolist()[0],"image":imagen},ignore_index=True)
    return datset_recomendacion

app = Flask(__name__)
CORS(app)
run_with_ngrok(app)

usuariosDataSet = list(set(calificaciones_peliculas["userId"].tolist()))

jsonPrueba ={
    "name":"David",
    "lastname":"Quintero"
}

@app.route("/usuarios")
def usuarios():
    return json.dumps(usuariosDataSet)


@app.route('/peliculasRecomendadas')
def peliculasRecomendadas():
    parametros = request.args.get('UserId','no esta pana')
    predice=recomendation_movie(int(parametros))
    pruebaPelis = list()
    cont = len(predice.values) -2
    for n in predice:
        pruebaPelis.append(list(predice.values[cont]))    
        cont -=1
    return json.dumps(pruebaPelis)  

app.run()