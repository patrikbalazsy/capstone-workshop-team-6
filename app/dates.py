from datetime import date


def days_left(deadline: date) -> int:
    """Return how many days are left until the deadline.

    0 on the deadline day, 1 the day before, -1 the day after.
    """
    return (deadline - date.today()).days
