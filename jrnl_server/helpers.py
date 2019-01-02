import jrnl

from conf import CONFIG_PATH, JRNL_CONFIG, JOURNAL_NAME


def load_journal():
    journal = jrnl.Journal.Journal(journal_name=JOURNAL_NAME, **JRNL_CONFIG)
    journal.open()
    return journal


def get_day_with_suffix(day):
    """
    Returns:
        (day, suffix): (TUPLE[STR, STR])
    """
    assert isinstance(day, int) and 0 < day <= 31
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
            suffix = SUFFIXES[suffix_day]
            return (str(day), suffix)
        suffix_day -= 1
