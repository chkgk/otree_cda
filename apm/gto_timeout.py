
from . import models, pages
from ._builtin import Page
from .models import Constants
import time
from otree.models_concrete import PageTimeout


# setting default values if they are missing in Constants
if hasattr(Constants, 'gto_seconds'):
    gto_seconds = Constants.gto_seconds
else:
    gto_seconds = 600

if hasattr(Constants, 'overallrounds'):
    overallrounds = Constants.overallrounds
else:
    overallrounds = False

def now():
    return int(time.time())


class GTOPage(Page):

    timeout_seconds = gto_seconds

    def get_sequence(self):
        from .pages import page_sequence
        p_in_gen_timeout = [p for p in page_sequence if hasattr(p,'general_timeout')]
        p_in_gen_timeout = [p for p in p_in_gen_timeout if p.general_timeout]
        return p_in_gen_timeout

    def get_index_in_sequence(self):
        p_in_gen_timeout = self.get_sequence()
        if type(self) in p_in_gen_timeout:
            index_in_gto = p_in_gen_timeout.index(type(self))
            seqlen = len(p_in_gen_timeout)
            return index_in_gto

    def is_first(self):
        if self.get_index_in_sequence() == 0:
            return True
        return False

    def is_last(self):
        if self.get_index_in_sequence() == len(self.get_sequence()) - 1:
            return True
        return False


    def is_displayed(self):
        if self.is_first() and 'gto_time_stamp' not in self.player.participant.vars:
            self.player.participant.vars['gto_time_stamp'] = now()
        expiration_time = self.player.participant.vars['gto_time_stamp'] + gto_seconds
        timeout, created = PageTimeout.objects.get_or_create(
            participant=self.participant,
            page_index=self.participant._index_in_pages,
            defaults={'expiration_time': expiration_time})
        to_display = expiration_time > now()
        return to_display and self.gto_is_displayed()

    def before_next_page(self):
        if not overallrounds and self.is_last():
            del self.player.participant.vars['gto_time_stamp']

    def vars_for_template(self):
        if self.general_timeout:
            gto_dict = {'gto': self.general_timeout,
                        'overallrounds':overallrounds}
            if self.gto_vars_for_template():
                gto_dict.update(self.gto_vars_for_template())
            return gto_dict

    def gto_is_displayed(self):
        return True

    def gto_before_next_page(self):
        ...

    def gto_vars_for_template(self):
        ...