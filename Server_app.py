import tkinter as tk
from tkinter import messagebox

import paramiko
from wakeonlan import send_magic_packet
import time
import threading
import os
from Scanner_script import scanner_script


# Настройки сервера
MAC_ADDRESS = '00:11:22:33:44:55'  # Замените на реальный MAC-адрес сервера
SERVER_IP = '192.168.1.100'  # IP-адрес сервера
SERVER_USER = 'user'  # Имя пользователя сервера
SERVER_PASSWORD = 'password'  # Пароль от сервера

# Функция отправки WOL пакета
def send_wol():
    try:
        send_magic_packet(MAC_ADDRESS)
        messagebox.showinfo("Успех", "WOL пакет отправлен!")
        check_server_status()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось отправить WOL пакет: {e}")

# Функция выключения сервера
def shutdown_server():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD)

        stdin, stdout, stderr = ssh.exec_command('sudo shutdown now')
        stdin.write(SERVER_PASSWORD + '\n')  # Отправляем пароль для выполнения sudo
        stdin.flush()

        stdout.channel.recv_exit_status()  # Ожидаем завершения команды
        ssh.close()

        messagebox.showinfo("Успех", "Сервер выключен!")
        check_server_status()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось выключить сервер: {e}")

# Функция сканирования документа (эмуляция)
def scan_doc():
    time.sleep(10)  # Эмуляция времени сканирования
    messagebox.showinfo("Сканирование", "Документ отсканирован!")

# Обновление состояния сервера
def check_server_status():
    response = os.system(f"ping -c 1 {SERVER_IP} > /dev/null 2>&1")
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
    scanner_script()
    btn_scan.config(state=tk.NORMAL)

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