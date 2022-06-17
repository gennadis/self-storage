from django import template

register = template.Library()

@register.filter(name="badge_bg")
def badge_bg(value):
    """Get appropriate CSS style for status"""

    if value == "Не оплачено":
        return "bg-warning"
    if value == "Оплачено":
        return "bg-success"
    if value == "Просрочено":
        return "bg-danger"
    if value == "Завершено":
        return "bg-dark"
    return "bg-secondary"