import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    cur_year = datetime.datetime.today()
    return {
        'year': cur_year.year
    }
