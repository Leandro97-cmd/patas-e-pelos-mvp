"""Validação de texto compartilhada pelos cadastros."""

import unicodedata


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
