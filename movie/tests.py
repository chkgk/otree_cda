from otree.api import Currency as c, currency_range, expect, Bot, Submission
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Part1Announcement
        yield Instructions
        yield Submission(Movie, check_html=False)

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
        if self.player.clip == 'intense':
            yield EvaluationIntense, eval_context
        else:
            yield EvaluationCalm, {
                'movie_pleasant': random.choice([True, False]),
                'movie_calm_to_excited': random.randint(1, 9),
            }
        yield Part2Announcement
