import numpy as np
import cv2 as cv
import sounddevice as sd
import time
import telebot
import os



def calculate_decibels(data):
    rms = np.sqrt(np.mean(data ** 2))
    if rms > 0:
        return 25* np.log10(rms)
    else:
        return -np.inf


def monitor_sound(threshold_db):
    sample_rate = 44100
    duration = 1  # время записи в секундах

    while True:
        # Запись звука
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float64')
        sd.wait()  # Ждем завершения записи

        # Расчет громкости в децибелах
        decibels = calculate_decibels(recording)

        print(f"Громкость: {decibels:.2f} дБ")

        # Если громкость превышает порог, сохраняем видео
        if decibels > threshold_db:
            video_file_path = save_video()  # Запускаем запись видео на 1 минуту
            print("Видео сохранено.")
            send_video(video_file_path)  # Отправляем видео через Telegram-бота

        time.sleep(0.5)  # Задержка перед следующей проверкой


def save_video():
    cap = cv.VideoCapture(0)
    fourcc = cv.VideoWriter_fourcc(*'XVID')

    # Создание папки для сохранения видео, если она не существует
    output_dir = 'videos'
    os.makedirs(output_dir, exist_ok=True)

    video_file_path = os.path.join(output_dir, 'output.avi')
    out = cv.VideoWriter(video_file_path, fourcc, 20.0, (640, 480))

    start_time = time.time()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        cv.imshow('frame', frame)

        # Проверяем, прошло ли 60 секунд
        if time.time() - start_time > 60:
            break

        if cv.waitKey(1) == ord('q'):
            break

    cap.release()
    out.release()
    cv.destroyAllWindows()  # Закрыть окно
    print("Сохранение видео завершено.")
    return video_file_path  # Возвращаем путь к сохраненному видео


# Установите порог громкости в децибелах
threshold = -20

# Создаем бота
bot = telebot.TeleBot("7950100509:AAGyWn3Fyk_4V9hTqvVGz80qh1zPMrgf_y8")  # Замените на свой токен
chat_id = 1128015826

def send_video(video_file_path):
    with open(video_file_path, 'rb') as video:
        bot.send_video(chat_id, video, caption="Смотрите видео!")


monitor_sound(threshold)
