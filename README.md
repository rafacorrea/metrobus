# metrobus

## Pasos

1. GET https://datos.cdmx.gob.mx/api/records/1.0/download/?dataset=alcaldias
  * Parse
  * Guardar informacion y area de cada alcaldia para poder saber en cual se encuentran los metrobuses

2. GET https://datos.cdmx.gob.mx/api/records/1.0/download/?dataset=prueba_fetchdata_metrobus
  * Parse
  * Cada hora hacer un query y guardar historico de la ubicacion de cada metrobus.

## API
### Modelos / Recursos
  * Metrobus
  * Alcaldia
  * Historico

### Endpoints
  * metrobuses
    * filtro por alcaldia y por unidad
  * historial
    * filtro por unidad
  * alcaldias
  * unidades que hayan estado dentro de una alcaldia
