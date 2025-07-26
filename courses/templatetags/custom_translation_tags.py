from django import template
import os

register = template.Library()


@register.filter
def translate_number(value):
    value = str(value)
    english_to_persian_table = value.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
    return value.translate(english_to_persian_table)


@register.filter
def filename(value):
        return os.path.basename(value.file.name)


@register.filter
def multiply_by(value, arg):
    """Multiplies the input value by the given argument."""
    return arg * int(value)

@register.filter
def convert_to_int(value):
    return int(value)

@register.filter
def total_stars(value):
    return sum(i.star for i in value.all())
