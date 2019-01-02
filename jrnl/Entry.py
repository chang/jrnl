#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
import logging
import re
import textwrap
from datetime import datetime

import crayons


class Entry:
    # Number of spaces to use for indenting journal entries.
    INDENTATION_LEVEL = 2

    def __init__(self, journal, date=None, title="", body="", starred=False):
        self.journal = journal  # Reference to journal mainly to access it's config
        self.date = date or datetime.now()
        self.title = title.rstrip("\n ")
        self.body = body.rstrip("\n ")
        self.tags = self.parse_tags()
        self.starred = starred
        self.modified = False

    @staticmethod
    def tag_regex(tagsymbols):
        pattern = r'(?u)\s([{tags}][-+*#/\w]+)'.format(tags=tagsymbols)
        return re.compile( pattern, re.UNICODE )

    def parse_tags(self):
        fulltext =  " " + " ".join([self.title, self.body]).lower()
        tagsymbols = self.journal.config['tagsymbols']
        tags = re.findall( Entry.tag_regex(tagsymbols), fulltext )
        self.tags = tags
        return set(tags)

    def __unicode__(self):
        """Returns a string representation of the entry to be written into a journal file."""
        date_str = self.date.strftime(self.journal.config['timeformat'])
        title = date_str + " " + self.title.rstrip("\n ")
        if self.starred:
            title += " *"
        return "{title}{sep}{body}\n".format(
            title=title,
            sep="\n" if self.body.rstrip("\n ") else "",
            body=self.body.rstrip("\n ")
        )

    @property
    def date_format_string(self):
        if 'prettytimeformat' in self.journal.config:
            return self.journal.config['prettytimeformat']
        else:
            logging.debug("'prettytimeformat' not found in .jrnl_config. Defaulting to 'timeformat'.")
            return self.journal.config['timeformat']

    @property
    def pretty_title(self):
        return crayons.red(self.title.strip())

    @property
    def formatted_date(self):
        return self.date.strftime(self.date_format_string)

    @property
    def pretty_date(self):
        return crayons.green(self.formatted_date, bold=True)

    def _wrap_line(self, line):
        if not line:
            return " "

        initial_indent = self.INDENTATION_LEVEL * " "
        is_bullet_point = line.startswith("- ")
        if is_bullet_point:
            subsequent_indent = "  " + initial_indent
        else:
            subsequent_indent = initial_indent

        wrapped_line = textwrap.fill(
            line,
            initial_indent=initial_indent,
            subsequent_indent=subsequent_indent,
            drop_whitespace=True,
        )
        return wrapped_line

    def pprint(self, short=False):
        """Return a pretty-printed version of the entry.

        Args:
            short (bool): If True, only print the title.
        """
        if not short and self.journal.config['linewrap']:
            title = textwrap.fill(self.pretty_date + " " + self.pretty_title, self.journal.config['linewrap'])
            lines = self.body.rstrip(" \n").splitlines()
            # Remove newline between title and body.
            if lines and not lines[0]:
                lines = lines[1:]
            wrapped_lines = [self._wrap_line(l) for l in lines]
            body = "\n".join(wrapped_lines)
        else:
            title = "{date} {title}".format(date=self.pretty_date, title=self.pretty_title)
            body = self.body.rstrip("\n ")

        # Suppress bodies that are just blanks and new lines.
        has_body = len(self.body) > 20 or not all(char in (" ", "\n") for char in self.body)

        if short:
            return title
        else:
            return "{title}{sep}{body}\n".format(
                title=title,
                sep="\n" if has_body else "",
                body=body if has_body else "",
            )

    def __repr__(self):
        return "<Entry '{0}' on {1}>".format(self.title.strip(), self.date.strftime("%Y-%m-%d %H:%M"))

    def __eq__(self, other):
        if not isinstance(other, Entry) \
           or self.title.strip() != other.title.strip() \
           or self.body.rstrip() != other.body.rstrip() \
           or self.date != other.date \
           or self.starred != other.starred:
           return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_dict(self):
        return {
            'title': self.title,
            'body': self.body,
            'date': self.date.strftime("%Y-%m-%d"),
            'time': self.date.strftime("%H:%M"),
            'starred': self.starred
        }

    def to_md(self):
        date_str = self.date.strftime(self.journal.config['timeformat'])
        body_wrapper = "\n\n" if self.body else ""
        body = body_wrapper + self.body
        space = "\n"
        md_head = "###"

        return "{md} {date}, {title} {body} {space}".format(
            md=md_head,
            date=date_str,
            title=self.title,
            body=body,
            space=space
        )
