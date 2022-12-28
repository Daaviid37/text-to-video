import requests
from requests.structures import CaseInsensitiveDict
from google.cloud import speech_v1 as speech
from moviepy.editor import VideoClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
import base64
import numpy as np
import cv2
import json
import openai
from moviepy.video.fx.all import fadein, fadeout
from moviepy.editor import ImageClip

# Importar la librería para trabajar con texto y la librería para trabajar con tiempos
from moviepy.video.VideoClip import TextClip
import boto3

# Establecer la clave de acceso a la API de GPT-3
openai.api_key = "OPENAIAPI"

# Hacer una petición a la API de GPT-3 para generar el texto
response = openai.Completion.create(
    engine="text-davinci-003",
    prompt="Cuento de caperucita roja",
    max_tokens=100,
    temperature=0.7,
)

# Obtener el texto generado
texto = response["choices"][0]["text"]

# Establecer las claves de acceso y secreta
access_key = "POLLYKEY"
secret_key = "POLLYKEY"

# Crear un objeto de servicio para acceder a la API de Text-to-Speech de AWS
client = boto3.client(
    "polly",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name="us-east-1",
)


# Generar el audio utilizando la API de Text-to-Speech de AWS
response = client.synthesize_speech(
    Text=texto,
    OutputFormat="mp3",
    VoiceId="Enrique",
)

audio = response["AudioStream"].read()

# Guardar el audio generado en un archivo
with open("voz.mp3", "wb") as f:
    f.write(audio)



# Crear un objeto AudioFileClip a partir del archivo de audio generado
audio = AudioFileClip("voz.mp3")

# Dividir el texto en fragmentos de x palabras
palabras = texto.split()
num_palabras = len(palabras)
num_imagenes = num_palabras // 17 + (num_palabras % 17 != 0)
fragmentos = [palabras[i:i+17] for i in range(0, num_palabras, 17)]

# Crea una lista de objetos VideoClip a partir de las imágenes
fps = 30
duration = 5  # Duración de cada imagen en segundos
num_frames = fps * duration
clips = []
for i, fragmento in enumerate(fragmentos):
    
    # Generar imágenes a partir del fragmento de texto
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = "Bearer API OPENAI"
    data = json.dumps({"model": "image-alpha-001", "prompt": ' '.join(fragmento), "num_images":1, "size":"1024x1024"})
    resp = requests.post("https://api.openai.com/v1/images/generations", headers=headers, data=data)
    resp = requests.post("https://api.openai.com/v1/images/generations", headers=headers, data=data)

    # Comprobar si la petición ha tenido éxito
    if resp.status_code != 200:
        print("Error al generar la imagen:", resp.text)
    else:
        # Descargar la imagen y guardarla en un archivo
        image_url = resp.json()["data"][0]["url"]
        resp = requests.get(image_url)
        if resp.status_code == 200:
            with open(f"imagen{i+1}.jpg", "wb") as f:
                f.write(resp.content)

    # Crear un objeto ImageClip a partir de la imagen
    imagen = ImageClip(f"imagen{i+1}.jpg")
    clip = imagen.set_duration(duration)
    clip.fps = 24


    

    # Crear el subtítulo
    subtitulo = TextClip(f"{' '.join(fragmento)}.upper()", font="Arial", align="center", fontsize=25, color="#ff000000", bg_color="black").set_duration(duration)

    # Crear la sombra
    #sombra = TextClip(f"{' '.join(fragmento)}", font="Arial", align="center", fontsize=0, color="black").set_duration(duration)

    # Desplazar la sombra 3 píxeles hacia la derecha y hacia arriba
    #sombra = sombra.set_pos((3, 3))

    # Superponer el subtítulo y la sombra
    #subtitulo_con_sombra = CompositeVideoClip([sombra, subtitulo])
    
    # Establecer la posición del subtítulo debajo de la imagen con un margen lateral de 50 píxeles
    subtitulo = subtitulo.set_pos((5, 1024))

    # Superponer el subtítulo sobre la imagen
    subtitulo_sobre_imagen = CompositeVideoClip([clip, subtitulo])
    
    # Añadir el objeto ImageClip y el objeto TextClip a la lista de clips
    clips.append(CompositeVideoClip([clip, subtitulo]))



    
# Definir el tamaño del vídeo
video_size = (1280, 720)
# Concatenar los clips en un único vídeo
video = concatenate_videoclips(clips)

# Añadir el audio al vídeo
video = video.set_audio(audio)

# Guardar el vídeo resultante en un archivo
video.write_videofile("video.mp4")
