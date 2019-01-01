import json

from flask import Flask
import flask

from jrnl_helpers import JournalWrapper, EntryWrapper


app = Flask(__name__)

def load_template(template_name, **kwargs):
    template = app.jinja_env.get_or_select_template(template_name)
    return template.render(**kwargs)

app.config['_hero_template'] = load_template('_hero.html')

journal = JournalWrapper()


@app.route('/')
def index():
    entry_links = journal.get_entry_links()
    return flask.render_template('index.html', entry_links=entry_links)


@app.route('/entry/<path:date>')
def entry(date):
    parsed_entry = EntryWrapper(journal.get_entry(date))
    context = {
        'date': parsed_entry.date,
        'title': parsed_entry.title,
        'body_paragraphs': parsed_entry.body_paragraphs,
        'tags': parsed_entry.html_tags,
        'num_words': parsed_entry.word_count,
    }
    return flask.render_template('entry.html', **context)


@app.route('/stats')
def stats():
    options = {
        'tag_stats': journal.tag_stats,
        'num_entries': len(journal.journal.entries),
        'num_words': journal.word_count(),
        'num_tags': len(journal.tag_stats),
    }
    return flask.render_template('stats.html', **options)

