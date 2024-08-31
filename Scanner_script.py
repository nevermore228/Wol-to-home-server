import paramiko
from datetime import datetime

# Данные для подключения
hostname = "192.168.1.100"
username = "root"
password = "root"

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
        client.connect(hostname, username=username, password=password)

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
        client.connect(hostname, username=username, password=password)

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

# Основная программа


def scanner_script():
    try:
        device_temp = get_scan_device()  # Получаем устройство
        scan_image(device_temp)  # Выполняем сканирование
    except Exception as e:
        print(str(e))