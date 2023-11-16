# Cognitive Services - Alessandro

## Descripcion
Asistente utilizando Cognitive Services de Azure Ai, orientado a realizar una unica tarea, brindar informacion de figuras públicas.

## Tareas que ejecuta

- Reconocimiento de instruccion/pregunta utilizando el microfono del dispositivo.
- Detección de contenido ofensivo, evaluando la instruccion.
- Verificacion de entidad si la instruccion se refiere a un invividuo.
- Obtener informacion de la figura publica utilizando la API de google.
- Respuesta de voz con la informacion a la instruccion.

## SDKs

- SDK de Azure speech-to-text para transformar la consulta hablada a texto.
- SDK de Azure Content Safety para filtrar aquellas preguntas que presentan contenido ofensivo.
- SDK de Azure Language para resumir y extraer la entidad de la que habla el usuario (usando el SDK de Entity Recognition).
- Utiliza la API de Google Knowledge Graph Search para obtener información sobre la entidad.
-  SDK de Azure text-to speech para transformar la respuesta en texto de Alessandro a speech.


## Archivos

- env.txt: que contiene las keys y endpoinds para consumir los servicios de Azure y google
- allesandro.py : archivo con las funciones y logica para nuestro asistente

## Interaccion/Ejecucion

- La aplicacion escucha por 15 segundos.
- Identifica si "alessander" fuer invocado para escuchar la instruccion.
- Responde dependiendo al escenario consultado.