def _format_day_of_month(day):
    SUFFIXES = {
        1: 'st',
        2: 'nd',
        3: 'rd',
        4: 'th',
        21: 'st',
        22: 'nd',
        23: 'rd',
        24: 'th',
        31: 'st',
    }
    suffix_day = day
    while True:
        if suffix_day in SUFFIXES:
            return f'{day}{SUFFIXES[suffix_day]}'
        suffix_day -= 1



for i in range(1, 32):
    print(_format_day_of_month(i))
