import flask

import jrnl

from conf import CONFIG_PATH, JOURNAL_NAME
from elements import HTMLTag


def load_journal():
    config = jrnl.util.load_and_fix_json(CONFIG_PATH)
    journal_config = config['journals'].get(JOURNAL_NAME)
    config.update(journal_config)
    journal = jrnl.Journal.Journal(journal_name=JOURNAL_NAME, **config)
    journal.open()
    return journal


def _get_day_with_suffix(day):
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


class JournalWrapper:

    def __init__(self):
        self.journal = load_journal()
        self.journal_dict = self.make_journal_dict(self.journal)

    def get_entry(self, date):
        # TODO: Do some input validation here.
        return self.journal_dict[date]

    @property
    def entries(self):
        return self.journal.entries

    def word_count(self):
        return sum([EntryWrapper(e).word_count for e in self.journal.entries])

    def make_journal_dict(self, journal):
        journal_dict = {}
        for entry in journal.entries:
            dt = entry.date
            date_str = f'{dt.year}/{dt.month}/{dt.day}'
            journal_dict[date_str] = entry
        return journal_dict

    def get_entry_links(self):
        entry_links = []
        for date_str, entry in self.journal_dict.items():
            entry_name = f'{date_str}: {entry.title}'
            entry_link = f'entry/{date_str}'
            el = (entry_name, entry_link)
            entry_links.append(el)
        # Do we need to sort this first? No guarantee of ordering in a dict...
        return reversed(entry_links)

    @property
    def tag_stats(self):
        """A list of tuples with the form: [(tag, n)]."""
        tag_list_count_first = list(jrnl.exporters.get_tags_count(self.journal))
        tag_list_count_first = sorted(tag_list_count_first, reverse=True)
        tag_list = [HTMLTag(tag).count_pill(n) for n, tag in tag_list_count_first]
        return tag_list


class EntryWrapper:
    def __init__(self, entry):
        self.entry = entry

    @property
    def title(self):
        return self.entry.title

    @property
    def tags(self):
        unique_tags = list(set(self.entry.tags))
        return sorted(unique_tags)

    @property
    def html_tags(self):
        return [HTMLTag(t).pill() for t in self.tags]

    @property
    def date(self):
        raw_date = self.entry.date
        day, suffix = _get_day_with_suffix(raw_date.day)
        date_str = raw_date.strftime(f'%A, %B {day}{suffix} %Y')
        return date_str

    @property
    def word_count(self):
        return len(self.entry.body.split(" "))

    def _render_lists(self, paragraphs):
        def is_list_item(p):
            return p.strip().startswith('- ')

        rendered, unordered_list = [], []
        for i, p in enumerate(paragraphs):
            if is_list_item(p):
                unordered_list.append(p.lstrip('- '))
            else:
                rendered.append(p)
            end_of_list = (i == len(paragraphs) - 1) or not is_list_item(paragraphs[i + 1])
            if end_of_list:
                html_list = flask.render_template('_unordered_list.html', items=unordered_list)
                rendered.append(html_list)
                unordered_list = []

        return rendered

    def _render_tags(self, paragraphs):
        # Render tags in the body of the journal entry.
        rendered = []
        for p in paragraphs:
            for tag in self.tags:
                p = p.replace(tag, HTMLTag(tag).text())
            rendered.append(p)
        return rendered

    @property
    def body_paragraphs(self):
        paragraphs = self.entry.body.split('\n')
        paragraphs = self._render_lists(paragraphs)
        paragraphs = self._render_tags(paragraphs)
        return paragraphs
