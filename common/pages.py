from otree import settings
from otree.api import *

LANGUAGE_MAP = dict(de=dict())


class TranslatedPage(Page):
    def get_template_name(self):
        if self.template_name is not None:
            return f"{self.template_name[:-5]}_{settings.LANGUAGE_CODE}.html"
        return f'{self.__module__}/{self.__class__.__name__}_{settings.LANGUAGE_CODE}.html'

    def get_context_data(self, **context):
        context = super().get_context_data(**context)
        context["LANGUAGE_CODE"] = settings.LANGUAGE_CODE
        return context
