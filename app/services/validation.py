"""Validação de entradas compartilhada pelos serviços."""

import unicodedata

SQLITE_MAX_INTEGER = 2**63 - 1


class ValidationError(ValueError):
    def __init__(self, errors):
        self.errors = errors
        super().__init__("Revise os campos indicados.")


def clean_text(value, field, label, limit, errors, required=False):
    if value is None:
        value = ""
    if not isinstance(value, str):
        errors[field] = f"Informe um valor válido para {label.lower()}."
        return ""
    value = unicodedata.normalize("NFC", value).strip()
    if required and not value:
        errors[field] = f"O campo {label.lower()} é obrigatório."
    elif len(value) > limit:
        errors[field] = f"O campo {label.lower()} deve ter no máximo {limit} caracteres."
    elif "\x00" in value:
        errors[field] = f"Informe um valor válido para {label.lower()}."
    return value


def clean_id(value, field, errors, message):
    """Valida um identificador positivo antes de vinculá-lo a uma consulta."""
    try:
        if isinstance(value, bool) or not isinstance(value, (str, int)):
            raise ValueError
        identifier = int(value)
        if not 1 <= identifier <= SQLITE_MAX_INTEGER:
            raise ValueError
    except ValueError:
        errors[field] = message
        return None
    return identifier
