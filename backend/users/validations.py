import re

from django.core.exceptions import ValidationError

from . import settings

REGULAR_SYMBOLS = re.compile(settings.REGULAR_USERNAME, re.I)


def validate_username(value):
    if value == 'me':
        raise ValidationError('Использовать имя "me" в'
                              ' качестве username запрещено.')
    valid_symbol = " ".join(REGULAR_SYMBOLS.findall(value))
    invalid_symbol = " ".join([
        symbol for symbol in value if symbol not in valid_symbol
    ])
    if len(invalid_symbol) > 0:
        raise ValidationError(
            f'Имя пользователя содержит недопустимые символы: {invalid_symbol}'
        )
    return value
