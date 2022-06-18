from django import template

from storage.models import Lease

register = template.Library()

@register.filter(name="badge_bg")
def badge_bg(value):
    """Get appropriate CSS style for status"""

    if value == Lease.Status.NOT_PAID:
        return "bg-warning"
    if value == Lease.Status.PAID:
        return "bg-success"
    if value == Lease.Status.OVERDUE:
        return "bg-danger"
    if value == Lease.Status.COMPLETED:
        return "bg-dark"
    return "bg-secondary"


@register.filter(name="is_paid")
def is_paid(value):
    return value == Lease.Status.PAID


@register.filter(name="is_not_paid")
def is_not_paid(value):
    return value == Lease.Status.NOT_PAID


@register.filter(name="is_overdue")
def is_overdue(value):
    return value == Lease.Status.OVERDUE


@register.filter(name="is_canceled")
def is_canceled(value):
    return value == Lease.Status.CANCELED


@register.filter(name="is_completed")
def is_completed(value):
    return value == Lease.Status.COMPLETED