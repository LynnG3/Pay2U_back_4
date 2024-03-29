# from django.shortcuts import render

from push_notifications.models import APNSDevice  # GCMDevice


def send_push_notification(device_id, message):
    """Заготовка для пуш-уведомлений."""
    # Находим устройство пользователя по его идентификатору
    device = APNSDevice.objects.get(device_id=device_id)

    # Отправляем пуш уведомление
    device.send_message(message, badge=1)


# Пример использования
device_id = "номер телефона"
message = "ваша подписка на ___ истекает такогото числа"
send_push_notification(device_id, message)
