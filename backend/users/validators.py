import re
from django.core.exceptions import ValidationError


def validate_username(username):
    if username.lower() == 'me':
        raise ValidationError('Выберите другое имя пользователя')
    return username


def validate_mobile(number):
    phone = re.compile(r"^\+?[7-8]?[0-9]{10}$")

    if not phone.search(number):
        raise ValidationError("Неверный мобильный номер.")
    return number
