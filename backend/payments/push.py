from push_notifications.models import APNSDevice


def send_push_notification(device_id, message):
    """Заготовка для пуш-уведомлений."""
    device = APNSDevice.objects.get(device_id=device_id)
    device.send_message(message, badge=1)


device_id = "номер телефона"
message = "ваша подписка на ___ истекает такогото числа"
send_push_notification(device_id, message)
