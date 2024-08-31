from wakeonlan import send_magic_packet

# MAC-адрес вашего сервера (замените на ваш реальный MAC-адрес)
MAC_ADDRESS = '00:11:22:33:44:55'  # Замените на реальный MAC-адрес сервера

def send_wol():
    try:
        # Отправляем WOL пакет
        send_magic_packet(MAC_ADDRESS)
        print(f"WOL пакет отправлен на сервер с MAC-адресом {MAC_ADDRESS}")
    except Exception as e:
        print(f"Ошибка отправки WOL пакета: {e}")

if __name__ == '__main__':
    send_wol()