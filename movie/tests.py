from otree.api import Currency as c, currency_range, expect, Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Instructions
        yield Movie

        # set up the evaluation context
        eval_context = {
            'movie_feeling': random.randint(1, 2),
            'movie_filler_task': random.choice([True, False]),
        }
        if eval_context['movie_feeling'] == 1:
            eval_context['movie_intensity_anxiety'] = random.randint(1, 9)
        else:
            eval_context['movie_intensity_excitement'] = random.randint(1, 9)

        # yield the page
        yield Evaluation, eval_context
        yield Part2Announcement
