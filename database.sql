CREATE DATABASE IF NOT EXISTS fasAPImovies;
USE fasAPImovies;

# Corregimos los tipos de algunas columnas en las tablas creadas recientemente
ALTER TABLE cast
MODIFY idShow INT,
MODIFY cast VARCHAR(100);

ALTER TABLE genre
MODIFY idShow INT,
MODIFY listed_in VARCHAR(30);

ALTER TABLE movieTVShow
MODIFY idShow INT,
MODIFY type VARCHAR(10),
MODIFY title VARCHAR(120),
MODIFY director VARCHAR(280),
MODIFY country VARCHAR(140),
MODIFY date_added VARCHAR(20),
MODIFY release_year INT,
MODIFY rating VARCHAR(20),
MODIFY duration INT,
MODIFY description VARCHAR(1900),
MODIFY platform VARCHAR(8);

ALTER TABLE genre ADD INDEX idShow_index (idshow);
ALTER TABLE cast ADD INDEX idShow_index (idshow);

#********************************************#
#1 Max Duration: 2018, hulu, min
SELECT title, duration
FROM movieTVShow
WHERE release_year = 2018 AND platform = "hulu" AND type = "Movie"
ORDER BY duration DESC;
# Loro
# The House That Jack Built

#2  Count Platform: netflix
SELECT type, count(*)
FROM movieTVShow
WHERE platform = "netflix"
GROUP BY type;
# Movie = 6131; TV Show = 2676

#3 Listedin: comedy
SELECT s.platform, COUNT(s.platform) as cantidad
FROM genre g
JOIN movieTVShow s ON (s.idShow = g.idShow)
WHERE g.listed_in = "Comedy"
GROUP BY s.platform
ORDER BY cantidad DESC;
# amazon: 2099

#4 Actor: netflix, 2018
SELECT count(c.cast) AS cantidad, c.cast
FROM cast c
JOIN movieTVShow s ON (s.idShow = c.idShow)
WHERE s.platform = "netflix" AND s.release_year = 2018 AND c.cast != "Sin Datos"
GROUP BY c.cast
ORDER BY cantidad DESC;
# Andrea Libman


