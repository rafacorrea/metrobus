# metrobus

## Pasos / Metodologia

1. GET https://datos.cdmx.gob.mx/api/records/1.0/download/?dataset=alcaldias
  * Parsear
  * Guardar informacion y area de cada alcaldia para poder saber en cual se encuentran los metrobuses

2. GET https://datos.cdmx.gob.mx/api/records/1.0/download/?dataset=prueba_fetchdata_metrobus
  * Parsear
  * Cada hora hacer un query y guardar historico de la ubicacion de cada metrobus.

## Arquitectura
  * App en flask
  * worker / extraccion de datos con celery
  * DB con postgres + postgis
  * redis

  Diagrama en docs/diagrama.pdf

  * Para mas informacion sobre postgis consultar documentacion: http://postgis.net/docs/

## Setup
  Necesitaras lo siguiente:
  * `docker`
  * `docker-compose`

  Para migrar la base de datos es necesario correr `flask db migrate` y `flask db upgrade`.
  Para actualizar las alcaldias se hizo un comando de cli de flask llamado `update_zones`. Para ejecutarlo solo llamar `flask update_zones`.

  (Nada de esto es necesario si se usa la carpeta postgres-data como volumen compartido con docker.)

  Para correr la aplicacion en modo desarrollo, unicamente basta con correr `docker-compose up -d --build`. Despues se debe correr `docker-compose up` y la aplicacion estara sirviendo en el puerto 5000.

  ### Puntos a considerar:
  * La base de datos esta montada en la raiz del proyecto para poder utilizar una base de datos pre-poblada (se encuentra en la carpeta postgres-data).
  * Actualmente los datos sobre la posicion de los metrobuses se actualiza cada hora (ver `CELERY_BEAT_SCHEDULE` en la configuracion de la aplicacion)

## Endpoints
  * `/api/alcaldias` - Listado de todas las alcaldias en la base de datos abiertos de CDMX.
  * `api/alcaldias/$id` - Ver una alcaldia en especifico
  * `api/metrobuses` - Ver todas las unidades con su `label` (Numero de metrobus)
    - Recibe parametro `zone_id` e.g. `/api/metrobuses?zone_id=44`
  * `api/metrobuses/$id` - Ver el historial de ubicaciones de un metrous en especifico
