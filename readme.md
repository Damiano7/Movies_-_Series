![1670467172910](image/readme/1670467172910.png)

# PROYECTO: ANÁLISIS DE SERVICIOS DE STREAMINGS

### Propuesta de trabajo

> El proyecto consiste en realizar una ingesta de datos desde diversas fuentes, posteriormente aplicar las transformaciones pertinentes, y luego disponibilizar los datos limpios para su consulta a través de una API. Esta API se encuentra en un entorno virtual dockerizado.

### Consultas a realizar en la API

* Máxima duración según tipo de film (película o serie), por plataforma y por año: El request será:

```
get_max_duration(anio, plataforma, [min o season])
```

* Cantidad de películas y series (separado) por plataforma. El request será:

```
get_count_plataform(plataforma)
```

* Cantidad de veces que se repite un género y plataforma con mayor frecuencia del mismo. El request será:

```
get_listedin(genero)
```

* Actor que más se repite según plataforma y año. El request será:

```
get_actor(plataforma, año)
```

### Tecnologías

* ***Python*** - Lenguaje con el cual realizaremos la limpieza de datos utilizando entre otros las librerias Pandas, NumPy,  sqlAlchemy
* ***MySQL*** - Sistema de gestión de bases de datos relacionales
* ***Uvicorn*** - Librería de Python que funciona como servidor, permite que cualquier computadora se convierta en servidor
* ***FastAPI*** - Web framework moderno y rápido (de alto rendimiento) para construir APIs con Python
* ***Docker*** - Contenedores ligeros y portables para las aplicaciones de software que pueden ejecutarse en cualquier máquina con Docker instalado
  * **`Container`** es una abstracción de la capa de software que permite *empaquetar* código, con librerías y dependencias en un entorno parcialmente aislado.
  * **`Image`** es un ejecutable Docker que tiene todo lo necesario para correr aplicaciones, lo que incluye un archivo de configuración, variables -de entorno y runtime- y librerías.
  * **`Dockerfile`** archivo de texto con instrucciones para construir una imagen. Puede considerarse la automatización de creación de imágenes.

### Pasos del Proyecto

##### 1. Ingesta y normalización de datos

![1670470392235](image/readme/1670470392235.png)

El primer paso, la etapa "**Extract**", consistió en unificar toda la información en un solo Dataframe, para esto tomamos cada uno de los archivos y gracias a la función "importData(list)" los fuimos concatenando en el mismo Dataframe. Para esto se hizo uso de la librería 'os' de Python para obtener los nombres y extensiones de los archivos que allí se eencontraban

```python
# Directorio origen
dirPath = r"./datasets"

# Lista donde guardaremos el nombre de cada archivo
listPlatforms=[]

# Recorremos la carpeta datasets para cargar todos los archivos que hay en su interior
for f in os.listdir(dirPath):
    if os.path.isfile(os.path.join(dirPath, f)):
        listPlatforms.append(f)
```

```python
def importData(list):
  
    # Dataframe donde se almacenaran todas las peliculas y series
    data = pd.DataFrame()  

    for path in list:  

        dirPath = r"./datasets"
        path = os.path.join(dirPath, path) 
  
        # Importa los archivos csv
        if Path(path).suffix == ".csv":
            name = Path(path).stem
            f = open(path,"rb")
            result= chardet.detect(f.read())
            dataCSV = pd.read_csv(path, encoding=result["encoding"], engine='python', decimal=".")
  
            # Crea la columna platform donde se indica la plataforma original
            dataCSV["platform"] = name.split("_", 1)[0]
  
            # Carga de datos en el Dataframe data
            data = pd.concat([data, dataCSV])
  
        # Importa los archivos json
        if Path(path).suffix == ".json":
            name = Path(path).stem
            dataJson= pd.read_json(path, precise_float=True)

            # Crea la columna platform donde se indica la plataforma original
            dataJson["platform"] = name.split("_", 1)[0]
  
            # Carga de datos en el Dataframe data
            data = pd.concat([data, dataJson])
  
    return data
```

![1670477859399](image/readme/1670477859399.png)

Ahora que ya contamos con toda la información en un mismo lugar vamos a comenzar con la limpieza de los datos, es decir la etapa "**Transform**".
Aquí podemos ver las columnas que tenemos. Tal como se puede apreciar hay valores faltantes en varias de ellas que procederemos a limpiar

![1670480066148](image/readme/1670480066148.png)

Empezamos eliminando el "show_id" y lo reemplazamos con un nuevo índice númerico que nos facilita la búsqueda en las filas del Dataframe

```python
data.drop(['show_id'], axis=1, inplace=True)
data = data.reset_index(drop=True)
data.insert(0, "idShow", data.index)
```

Para obtener un pantallazo general contamos la cantidad de nulos por columna

```python
counts = data.isna().sum()
percentages = round(data.isna().mean() * 100, 1)
nullValues = pd.concat([counts, percentages], axis=1, keys=["count", "%"])
```

![1670480487501](image/readme/1670480487501.png)

Haciendo una revisión de los campos se encontró con que algunas filas tenian el valor de la columna "duration" almacenado en la columna "rating"

```python
# Para hacer esta transformación utilizamos una función lambda que chequea que la columna duration sea nula y que en la columna rating este el formato de "duration" (min o Season)
data['duration'] = data.apply(lambda row: row['rating'] if (pd.isnull(row['duration']) & ("min" in str(row['rating']))) else row['duration'], axis=1)
data['duration'] = data.apply(lambda row: row['rating'] if (pd.isnull(row['duration']) & ("Season" in str(row['rating']))) else row['duration'], axis=1)

# Eliminamos esos valores de la columna rating
data['rating'] = data.apply(lambda row: np.nan if ("min" in str(row['rating'])) else row['rating'], axis=1)
data['rating'] = data.apply(lambda row: np.nan if ("Season" in str(row['rating'])) else row['rating'], axis=1)
```

Ahora que ya tenemos todos los valores en la columna "duration" procedemos a convertirla a un valor numérico, ya que después usaremos este campo para buscar aquellas películas de mayor duración. La información de "min" o "season" en este caso es redundante ya que tenemos una columna "type" donde se detalla si se trata de una película o una serie

```python
# Realizamos un split sobre la columna "duration" y nos quedamos con el primer término
# Si la duración no está especificada se reemplazará con 0
duracion = data["duration"].str.split(" ", n = 1, expand = True)
data["duration"] = duracion[0]
data["duration"] = data["duration"].fillna(0)
data["duration"] = pd.to_numeric(data["duration"])
```

Como ya tenemos corregida la información de la columna "duration" vamos a reemplazar todos los valores faltantes de las demas columnas por un "Sin Datos"

```python
data = data.fillna("Sin Datos")
```

Realizamos una inspección minusiosa de los géneros (ubicados en la columna "listed_in") y vemos que podemos reemplazar los géneros "and Culture" por "Culture" y "Dramas" por "Drama"

```python
# Generamos un array con la lista los géneros únicos
listAllGenres = data['listed_in'].str.split(", ").dropna().to_numpy()
listUniqueGenres = np.unique(sum(listAllGenres, []))
```

```python
data['listed_in'] = data['listed_in'].str.replace('and Culture','Culture')
data['listed_in'] = data['listed_in'].str.replace('Dramas','Drama')
```

Hacemos lo mismo con los directores y nos encontramos que hay uno con mas de 1.000 caracteres de longitud, procedemos a reemplazarlo

```python
listAllDir = data['director'].str.split(", ").dropna().to_numpy()
listAllDir = np.unique(sum(listAllDir, []))
listAllDir = np.array(sorted(listAllDir, key=len, reverse=True))
```

```python
data.at[9224,'director']='CAPI ValidCAPI'
```

Volvemos a hacer lo mismo pero con los actores esta vez y nos encontramos que no todos vienen separados por comas, por lo cual hacemos una conversión manual de algunos de estos errores.
Es importante que los actores esten separados por comas ya que despúes para que nuestro set de datos cumpla con la Primera Forma Normal queremos quitar esta columna del Dataframe principal y guardarlos en uno secundario donde cada actor este separado de los demas

```python
listAllCast = data['cast'].str.split(", ").dropna().to_numpy()
listAllCast = np.unique(sum(listAllCast, []))
listAllCast = np.array(sorted(listAllCast, key=len, reverse=True))
```

```python
data["cast"] = data["cast"].replace('\|', ',', regex=True)
data["cast"] = data["cast"].replace('IKPONMWOSA AIK ODIASE ONAH CHINYERE OKORIE PREACH BASSEY SUNNY WILLIAMS', 'IKPONMWOSA AIK ODIASE, ONAH CHINYERE OKORIE, PREACH BASSEY, SUNNY WILLIAMS')
data["cast"] = data["cast"].replace('Phillipe Torreton Sophie-Charlotte Husson  Julie Gayet', 'Phillipe Torreton, Sophie-Charlotte Husson, Julie Gayet')
data["cast"] = data["cast"].replace('Ray Emodi mike uchegbu Ray Ighodaro chinelo enemchukwu', 'Ray Emodi, mike uchegbu, Ray Ighodaro, chinelo enemchukwu')
data["cast"] = data["cast"].replace('Denis Podalydes Isabelle Candalier Phillipe Uchan', 'Denis Podalydes, Isabelle Candalier, Phillipe Uchan')
data["cast"] = data["cast"].replace('Helene de Fourgorelles Tcheky Karyo Pierre Arditi', 'Helene de Fourgorelles, Tcheky Karyo, Pierre Arditi')
data["cast"] = data["cast"].replace('John Dumelo Van Vicker Moses Efret Fatima Koroma', 'John Dumelo, Van Vicker, Moses Efret, Fatima Koroma')
data["cast"] = data["cast"].replace('COURAGE AKPANIKAN LAMIROSE ALI EBILOMA EMMANUEL', 'COURAGE AKPANIKAN, LAMIROSE ALI, EBILOMA EMMANUEL')
data["cast"] = data["cast"].replace('Xavier Beauvois Chiara Mastroianni  Roschdy Zem', 'Xavier Beauvois, Chiara Mastroianni, Roschdy Zem')
data["cast"] = data["cast"].replace('Laetitia Casta Jean Paul Rouve Stefano Accorsi', 'Laetitia Casta, Jean Paul Rouve, Stefano Accorsi')
data["cast"] = data["cast"].replace('PAUL SAMBO EMPRESS NJAMA IKPONMWOSA AIK ODIASE', 'PAUL SAMBO, EMPRESS NJAMA, IKPONMWOSA AIK ODIASE')
data["cast"] = data["cast"].replace('Fiona Gordon Lucy Tulugarjuk Dominique Abel', 'Fiona Gordon, Lucy Tulugarjuk, Dominique Abel')
data["cast"] = data["cast"].replace('Nizhalgal Ravi Anupama Kumar Meera Krishnan', 'Nizhalgal Ravi, Anupama Kumar, Meera Krishnan')
data["cast"] = data["cast"].replace('Adaeze Eluke Stephen Odimgbe Domben Chisom', 'Adaeze Eluke, Stephen Odimgbe, Domben Chisom')
data["cast"] = data["cast"].replace('Tana Adelana Martha Ankomah Seun Akindele', 'Tana Adelana, Martha Ankomah, Seun Akindele')
data["cast"] = data["cast"].replace('Iyke Ogbonna George Clinting Ngozi Achms', 'Iyke Ogbonna, George Clinting, Ngozi Achms')
data["cast"] = data["cast"].replace('Salim Sahid Kamara Phebean Swill Ram Dee', 'Salim Sahid, Kamara Phebean, Swill Ram Dee')
data["cast"] = data["cast"].replace('Frank Artus Qwasi Blay Jessica Williams', 'Frank Artus, Qwasi Blay, Jessica Williams')
data["cast"] = data["cast"].replace('Kalu Ikeagwu Scarlet Gomez Bukky Thomas', 'Kalu Ikeagwu, Scarlet Gomez, Bukky Thomas')
```

Ahora si, generamos estos nuevos Dataframes con la información de los géneros y de los actores

```python
dataGenre = data[['idShow', 'listed_in']].drop_duplicates()
dataGenre['listed_in'] = dataGenre['listed_in'].str.split(',')
dataGenre = dataGenre.explode('listed_in')
dataGenre['listed_in'] = dataGenre['listed_in'].str.strip()
```

```python
dataCast = data[['idShow', 'cast']].drop_duplicates()
dataCast['cast'] = dataCast['cast'].str.split(',')
dataCast = dataCast.explode('cast')
dataCast['cast'] = dataCast['cast'].str.strip()
```

Borramos estas columnas del Dataframe principal

```python
data.drop(['cast', 'listed_in'], axis=1, inplace=True)
```

##### 2. Relacionar el conjunto de datos y crear las tablas necesarias para realizar las consultas

Ahora comenzamos con la etapa "**Load**" donde guardaremos todos nuestros datos limpios en una base de datos en MySQL. Para esto se hizo uso de la libreria "SQLAlchemy"

```python
engine = create_engine("mysql+pymysql://root:Discoteca$7@localhost:3306/fasAPImovies")

data.to_sql('movieTVShow', engine, index=False)
dataGenre.to_sql('genre', engine, index=False)
dataCast.to_sql('cast', engine, index=False)
```

![1670482200114](image/readme/1670482200114.png)

##### 3. Crear la API en un entorno Docker

![1670484843159](image/readme/1670484843159.png)

Para esto utlizamos la guía provista en:

* [https://hub.docker.com/r/tiangolo/uvicorn-gunicorn-fastapi/](https://hub.docker.com/r/tiangolo/uvicorn-gunicorn-fastapi/)

Para empezar creamos un archivo Dockerfile con lo siguiente

```python
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11
 
COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app /app
```

Creamos un directorio app y en su interior creamos el archivo main.py donde va a estar funcionando nuestra api. Tambien se crearon los archivos necesarios para establecer la conexión con nuestra base de datos: "config/db.py" y "models/user.py", quedandonos la siguiente estructura de archivos:

.
├── app
│   └── main.py
│   └── config
│   │   └── __ init __.py
│   │   └── db.py
│   └── models
│   │   └── __ init __.py
│   │   └── user.py
└── Dockerfile
└── requirements.txt

Construimos nuestra api

```python
docker build -t myimage .
```

Ejecturamos un contenedor basado en la imagen que acabamos de crear

```python
docker run -d --name mycontainer -p 80:80 myimage
```

##### 4. Realizar consultas a la API

* Máxima duración según tipo de film (película o serie), por plataforma y por año

```python
# Nos pasan por parametro las variables: year, platform, [min or season]
@app.get('/get_max_duration/', tags=["Consultas"])
def get_max_duration(year: int, platform: str, type:str):
    tipo = type
    if (type == "min"): type = "Movie"
    else: type = "Tv Show"
    s = select(movieTVShows.c.title, func.concat(movieTVShows.c.duration, ' ', tipo).label("duracion"))
		.where(movieTVShows.c.release_year == year)
		.where(movieTVShows.c.platform == platform)
		.where(movieTVShows.c.type == type)
		.order_by(movieTVShows.c.duration.desc())
    return (conn.execute(s).first())
```

* Cantidad de películas y series (separado) por plataforma

```python
# Nos pasan por parametro la variable: platform
@app.get('/get_count_plataform/', tags=["Consultas"])
def get_count_plataform(platform: str):
    s = select(movieTVShows.c.type, func.count(movieTVShows.c.type).label("cantidad"))
		.where(movieTVShows.c.platform == platform)
		.group_by(movieTVShows.c.type)
    return (conn.execute(s).fetchall())
```

* Cantidad de veces que se repite un género y plataforma con mayor frecuencia del mismo

```python
# Nos pasan por parametro la variable: genre
@app.get('/get_listedin/', tags=["Consultas"])
def get_listedin(genre: str):
    s = select(movieTVShows.c.platform, func.count(movieTVShows.c.platform).label("cantidad"))
		.join(genres, genres.c.idShow==movieTVShows.c.idShow)
		.where(genres.c.listed_in == genre)
		.group_by(movieTVShows.c.platform)
		.order_by(func.count(movieTVShows.c.platform).desc())
    return (conn.execute(s).first())
```

* Actor que más se repite según plataforma y año

```python
# Nos pasan por parametro las variables: year, platform
@app.get('/get_actor/', tags=["Consultas"])
def get_actor(year: int, platform: str):
    s = select(func.count(casts.c.cast).label("cantidad"), casts.c.cast)
		.join(movieTVShows, casts.c.idShow==movieTVShows.c.idShow)
		.where(movieTVShows.c.platform == platform)
		.where(movieTVShows.c.release_year == year)
		.where(casts.c.cast != "Sin Datos")
		.group_by(casts.c.cast)
		.order_by(func.count(casts.c.cast).desc())
    return (conn.execute(s).first())  
```

![1670509295895](image/readme/1670509295895.png)

### Video Explicativo

[![VIDEO](http://img.youtube.com/vi/UgJRnhlPj9M/0.jpg)](http://www.youtube.com/watch?v=UgJRnhlPj9M "Proyecto: FastAPI + Entorno Virtual Dockerizado")
