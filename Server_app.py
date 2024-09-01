import tkinter as tk
from datetime import datetime
from tkinter import messagebox
import paramiko
from wakeonlan import send_magic_packet
import time
import threading
import os
import logging


# Настройки сервера
MAC_ADDRESS = '00:11:22:33:44:55'  # Замените на реальный MAC-адрес сервера
HOSTNAME = '192.168.1.100'  # IP-адрес сервера
USERNAME = 'user'  # Имя пользователя сервера
PASSWORD = 'password'  # Пароль от сервера
LOGFILE = 'app.log'





# Проверяем, существует ли файл, если нет — создаем его
if not os.path.exists(LOGFILE):
    with open(LOGFILE, 'w') as file:
        file.write('')  # Создаем пустой файл

# Настраиваем логирование
logging.basicConfig(
    filename=LOGFILE,  # Имя файла для логов
    level=logging.INFO,  # Уровень логирования
    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат логов
)
# Пример записи лога
#logging.info('Программа запущена.')
#logging.warning('Это предупреждение.')
#logging.error('Произошла ошибка.')


# Функция отправки WOL пакета
def send_wol():
    try:
        send_magic_packet(MAC_ADDRESS)
        messagebox.showinfo("Успех", "WOL пакет отправлен!")
        check_server_status()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось отправить WOL пакет: {e}")
        logging.error(f"Не удалось отправить WOL пакет: {e}")


# Функция выключения сервера
def shutdown_server():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)

        stdin, stdout, stderr = ssh.exec_command('sudo shutdown now')
        stdin.write(PASSWORD + '\n')  # Отправляем пароль для выполнения sudo
        stdin.flush()

        stdout.channel.recv_exit_status()  # Ожидаем завершения команды
        ssh.close()

        messagebox.showinfo("Успех", "Сервер выключен!")
        check_server_status()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось выключить сервер: {e}")
        logging.error(f"Не удалось выключить сервер: {e}")


# Функция сканирования документа (эмуляция)
def scan_doc():
    time.sleep(10)  # Эмуляция времени сканирования
    messagebox.showinfo("Сканирование", "Документ отсканирован!")


# Обновление состояния сервера
def check_server_status():
    response = os.system(f"ping {HOSTNAME} -n 1")
    if response == 0:
        status_label.config(text="Сервер включен", fg="green")
        btn_wake.config(state=tk.DISABLED)
        btn_shutdown.config(state=tk.NORMAL)
    else:
        status_label.config(text="Сервер выключен", fg="red")
        btn_wake.config(state=tk.NORMAL)
        btn_shutdown.config(state=tk.DISABLED)

# Функция запуска сканирования с блокировкой кнопки
def start_scan():
    btn_scan.config(state=tk.DISABLED)
    threading.Thread(target=run_scan).start()

def run_scan():
    try:
        scanner_script()
    except Exception as e:
        logging.error(f"Не удалось отcканировать: {e}")
    btn_scan.config(state=tk.NORMAL)


def cur_date_time():
    current_datetime = datetime.now().strftime("%d-%m-%Y___%H-%M-%S")
    return current_datetime


cur_dt = cur_date_time()
scan_path = f"/Scans/scan-{cur_dt}.png"


# Функция для выполнения команды и получения устройства
def get_scan_device():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Подключаемся к серверу
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)

        # Выполняем команду 'scanimage -L'
        stdin, stdout, stderr = client.exec_command('scanimage -L')

        output = stdout.read().decode('utf-8')
        errors = stderr.read().decode('utf-8')

        if errors:
            raise Exception(f"Error occurred: {errors}")

        # Используем регулярное выражение для извлечения устройства из вывода
        print(output)
        start = output.find("`") + 1
        end = output.find("'", start)

        if start > 0 and end > start:
            device_temp = output[start:end]
            return device_temp

        else:
            raise Exception("No device found in scanimage output.")

    finally:
        client.close()


# Функция для выполнения команды сканирования
def scan_image(device_temp):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Подключаемся к серверу
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)

        # Формируем команду сканирования
        command = f'scanimage --device="{device_temp}" --resolution=200 --format=png > "{scan_path}"'

        stdin, stdout, stderr = client.exec_command(command)

        output = stdout.read().decode('utf-8')
        errors = stderr.read().decode('utf-8')

        if errors:
            raise Exception(f"Error occurred during scanning: {errors}")

        print(f"Scan completed successfully. File saved to {scan_path}")

    finally:
        client.close()


def scanner_script():
    try:
        device_temp = get_scan_device()  # Получаем устройство
        scan_image(device_temp)  # Выполняем сканирование
    except Exception as e:
        print(str(e))






#_____________________________TKINTER__________________________
# Основное окно
root = tk.Tk()
root.title("Домашний сервер")

# Метка состояния сервера
status_label = tk.Label(root, text="Проверка состояния сервера...", font=("Arial", 14))
status_label.pack(pady=10)

# Кнопка включения сервера
btn_wake = tk.Button(root, text="Включить сервер", command=send_wol, font=("Arial", 12))
btn_wake.pack(pady=10)

# Кнопка выключения сервера
btn_shutdown = tk.Button(root, text="Выключить сервер", command=shutdown_server, font=("Arial", 12), state=tk.DISABLED)
btn_shutdown.pack(pady=10)

# Кнопка сканирования документа
btn_scan = tk.Button(root, text="Сканировать документ", command=start_scan, font=("Arial", 12))
btn_scan.pack(pady=10)

# Первоначальная проверка состояния сервера
check_server_status()

# Запуск основного цикла приложения
root.mainloop()