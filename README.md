# prueba-analitica-modelo-opciones-de-pago
 Prueba Analítica: Modelo Opciones de Pago

## Creacíon del archivo .gitignore
Se creó un archivo `.gitignore` para evitar que ciertos archivos y carpetas innecesarios se suban 
al repositorio. Esto incluye la carpeta `.venv/`, que contiene el ambiente virtual de Python 
y también la carpeta `data/`, que contiene los datos con los que se debe desarrollar el modelo.

## Creación y preparación del ambiente virtual en CMD
Se creó el ambiente virtual con: python -m venv .venv
Se activó el ambiente virtual con: .venv\Scripts\activate
Se actualizó el pip con: python -m pip install --upgrade pip
Se instalaron las librerías de pandas, scikit-learn con: pip install pandas kaggle scikit-learn

## Creación del archivo requirements.txt
Se creó el archvio requirements.txt con: pip freeze > requirements.txt

## Creación de carpeta data 
Se creó la carpeta data donde se colocó la carpeta comprimida con los datos con los que se 
desarrollará el modelo.

## Descomprimir los archivos en la carpeta data
Se accedió a git bash y se activó el ambiente virtual con: source .venv/Scripts/activate
Se descomprimió la carpeta prueba-analitica-modelo-opciones-de-pago.zip con: 
unzip data/prueba-analitica-modelo-opciones-de-pago.zip -d data/
