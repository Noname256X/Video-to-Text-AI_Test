from moviepy.editor import *
from pydub import AudioSegment
import os
import vosk
import wave
import json

while True:
    preferences = int(input("Введите 1 если ваша ОС - Windows\nВведите 2 если ваша ОС - MacOS\n"))
    if preferences == 1:
        originalVideoPath = input("Введите путь к видео: ")  # "C:\Users\fodea\Downloads\Как читать код.mp4"
        originalVideoPath = originalVideoPath.replace("\\", "/").replace('"', '')
        if not os.path.exists(originalVideoPath):
            raise FileNotFoundError(f"Файл не найден: {originalVideoPath}")
        break
    elif preferences == 2:
        print("MacOS пока недоступна")
    else:
        print("Вы ввели несуществующий пункт (",preferences,"). Попробуйте заново")


print("Преобразование видео в аудио...")
pathVideo = VideoFileClip(originalVideoPath)
pathAudiofolder = "Project Data/Audio/"
filenameVideo = os.path.basename(originalVideoPath).strip('"') # filename
audioFileMP3 = os.path.join(pathAudiofolder, filenameVideo).replace('.mp4', '.mp3')
pathVideo.audio.write_audiofile(audioFileMP3)


print("Преобразование аудиофайла из mp3 в wav...")
os.environ["PATH"] += os.pathsep + "dependencies for libraries/ffmpeg-2024-08-11-git-43cde54fc1-essentials_build/ffmpeg-2024-08-11-git-43cde54fc1-essentials_build/bin" # Абсолютное имя для ffmpeg
sound = AudioSegment.from_mp3(audioFileMP3)
sound = sound.set_channels(1).set_frame_rate(16000).set_sample_width(2) # Моно | 16kHZ | 16 бит
audioFileWAV = audioFileMP3.replace('.mp3', '.wav')
sound.export(audioFileWAV, format="wav")
if os.path.exists(audioFileMP3):
    os.remove(audioFileMP3)
else:
    print(f"Файл {audioFileMP3} не найден. Удаление невозможно!")


print("Создание объекта распознавания (model-rus-0.42)...")
model = vosk.Model("dependencies for libraries/vosk/model/vosk-model-ru-0.42") # Загрузка русской модели
wf = wave.open(audioFileWAV) # Открытие аудиофайла
if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000: # Проверка соответствия параметров аудиофайла
    raise ValueError("Аудиофайл должен быть моно, 16 бит, 16kHz")
rec = vosk.KaldiRecognizer(model, wf.getframerate()) # Создание объекта распознавания


pathTextfolder = os.path.join("Project Data/TextFiles/", filenameVideo.replace('.mp4', '') + " (model-rus-0.42)" + ".txt")
with open(pathTextfolder, 'w', encoding="utf-8") as TextFile:
    print("Чтение файлов и распознавание...")
    print('Модель распознавания: model-rus-0.42\n', file=TextFile)
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            print(result['text'])
            print(result['text'], file=TextFile)


# if os.path.exists(audioFileWAV):
#     os.remove(audioFileWAV)
# else:
#     print(f"Файл {audioFileWAV} не найден. Удаление невозможно!")