from otree import settings
from otree.api import *
import os
import json

LANGUAGE_MAP = dict(de=dict())


# FUNCTIONS
def manual_advance_admin_vars(subsession, advance_pages):
    s = subsession.session
    advance_pages = {f"advance_{page}": s.vars.get(f"advance_{page}", False) for page in advance_pages}
    return {
        "rest_key": os.getenv('OTREE_REST_KEY', ''),
        "session_code": s.code,
        "advance_pages": json.dumps(advance_pages)
    }


# PAGES
class TranslatedPage(Page):
    def get_template_name(self):
        if self.template_name is not None:
            return f"{self.template_name[:-5]}_{settings.LANGUAGE_CODE}.html"
        return f'{self.__module__}/{self.__class__.__name__}_{settings.LANGUAGE_CODE}.html'

    def get_context_data(self, **context):
        context = super().get_context_data(**context)
        context["LANGUAGE_CODE"] = settings.LANGUAGE_CODE
        return context


class ManualAdvancePage(Page):
    @staticmethod
    def live_method(player, data):
        current_page_name = player.participant._current_page_name
        if player.session.vars.get(f"advance_{current_page_name}", False):
            return {0: {'advance': current_page_name}}

    @staticmethod
    def js_vars(player):
        return {
            "player_id": player.id_in_group,
            "current_page_name": player.participant._current_page_name
        }

    @staticmethod
    def before_next_page(player, timeout_happened):
        # make sure that if the first player leaves the page in debug, the others do not have to wait either.
        if player.id_in_group == 1:
            player.session.vars[f"advance_{player.participant._current_page_name}"] = True
