from django import template

register = template.Library()


@register.filter
def naira(value):
    """Format number as Nigerian Naira with comma separators."""
    try:
        return "₦{:,}".format(int(value))
    except (ValueError, TypeError):
        return value


@register.filter
def multiply(value, arg):
    """Multiply two numbers."""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0
