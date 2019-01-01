from conf import TAG_COLORS


class HTMLTag:
    def __init__(self, tag):
        self.tag = tag

    def _render(self, template, **kwargs):
        if self.tag in TAG_COLORS:
            color = TAG_COLORS[self.tag]
        else:
            color = 'light'
        return template.format(color=color, tag=self.tag, **kwargs)

    def pill(self):
        return self._render('<span class="tag is-rounded is-{color}">{tag}</span>')

    def text(self):
        return self._render('<span class="has-text-{color} has-text-weight-semibold">{tag}</span>')

    def count_pill(self, n):
        return self._render(
            """
            <div class="tags has-addons">
                <a class="tag is-{color} is-medium">{tag}</a>
                <a class="tag is-dark is-medium">{n}</a>
            </div>
            """,
            n=n
        )
