class recomendacion:
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
def recomen(userId):
    movie=int(select_movie(userId))
    table=caracteristicas_pelicula.reset_index()
    filtro=table["movieId"]==movie
    pelicula=table[filtro]
    indice=pelicula.index.tolist()[0]
    return make_recommendation(caracteristicas_pelicula,4,indice)
    
def make_recommendation( data, n_recommendations,movie_data):
    idlis=[]
    query_index = movie_data
    distances, indices = model_knn.kneighbors(data.iloc[query_index,:].values.reshape(1, -1), n_neighbors =n_recommendations )
    idlis.append(data.index[query_index])
    for i in range(1, len(distances.flatten())):
        idlis.append(indices.flatten()[i])
    return idlis
def select_movie (userId):
    df_for_user=pd.DataFrame()
    df_for_user["clasificacion"]=caracteristicas_pelicula[userId]
    df_mayor_clas=pd.DataFrame(columns=["index","clasificacion"])
    filtro=df_for_user["clasificacion"]>=4.0
    
    df_ranking=df_for_user[filtro]
    df_ranking=df_ranking.reset_index()
    aleatorio = df_ranking.sample()
    indice=aleatorio.index.tolist()[0]
    return df_ranking["movieId"][indice]
   
def foundMovie(inuser):
    recomend=recomen(inuser)
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
    movies = foundMovie(userId)
    while(movies ==0):
        movies = foundMovie(userId)
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
            replaces1=stringJson.replace("'s",'s')
            replaces2=replaces1.replace("None",'"None"')
            replaces=replaces2.replace("'",'"')
            jsonpelicula=loads(replaces)
            imagen="https://image.tmdb.org/t/p/w500/"+jsonpelicula["poster_path"]
            datset_recomendacion=datset_recomendacion.append({"title":pelicula["original_title"].tolist()[0],"imdb":pelicula["imdb_id"].tolist()[0],"sinopsis":pelicula["tagline"].tolist()[0],"date":pelicula["release_date"].tolist()[0],"image":imagen},ignore_index=True)
    return datset_recomendacion
predice=recomendation_movie(83)
predice
