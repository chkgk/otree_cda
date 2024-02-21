from otree.api import *
from otree.settings import DEBUG, LANGUAGE_CODE
from common.pages import TranslatedPage, LANGUAGE_MAP

doc = """
Your app description
"""


def _(s):
    LANGUAGE_MAP["de"] = {
        "broken even in the stock market": "weder Geld gewonnen noch verloren",
        "is ahead of where he began": "Geld gewonnen",
        "has lost money": "Geld verloren",
        "Jerry received both the 15th highest and the 15th lowest mark in the class. How many students are in the class? (students)": "Jerry hat sowohl die 15.-höchste als auch die 15.-niedrigste Note in der Klasse erhalten. Wie viele Schüler sind in der Klasse? (Schüler)",
        "If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets? (minutes)": "Wenn 5 Maschinen 5 Minuten brauchen, um 5 Dinge herzustellen, wie lange würden 100 Maschinen brauchen, um 100 Dinge herzustellen? (Minuten)",
        "Simon decided to invest $8,000 in the stock market one day early in 2008. Six months after he invested, on July 17, the stocks he had purchased were down 50%. Fortunately for Simon, from July 17 to October 17, the stocks he had purchased went up 75%. At this point, Simon has:": "Simon hat beschlossen, am Anfang des Jahres 2008 $8.000 in den Aktienmarkt zu investieren. Sechs Monate nach seiner Investition, am 17. Juli, waren die Aktien, die er gekauft hatte, um 50% gefallen. Glücklicherweise stiegen die Aktien, die er gekauft hatte, vom 17. Juli bis zum 17. Oktober um 75%. Zu diesem Zeitpunkt hat Simon:",
        "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost? (dollars)": "Ein Schläger und ein Ball kosten insgesamt $1.10. Der Schläger kostet $1.00 mehr als der Ball. Wie viel kostet der Ball? (Dollar)",
        "In a lake, there is a patch of lily pads. Every day, the patch doubles in size. If it takes 48 days for the patch to cover the entire lake, how long would it take for the patch to cover half of the lake? (days)": "In einem See gibt es ein Fläche von Seerosenblättern. Jeden Tag verdoppelt sich die Fläche. Wenn es 48 Tage dauert, bis die Fläche den gesamten See bedeckt, wie lange würde es dauern, bis die Fläche die Hälfte des Sees bedeckt? (Tage)",
        "A man buys a pig for $60, sells it for $70, buys it back for $80, and sells it finally for $90. How much has he made? (dollars)": "Ein Mann kauft ein Schwein für $60, verkauft es für $70, kauft es für $80 zurück und verkauft es schließlich für $90. Wie viel hat er verdient? (Dollar)",
        "If John can drink one barrel of water in 6 days, and Mary can drink one barrel of water in 12 days, how long would it take them to drink one barrel of water together? (days)": "Wenn John ein Fass Wasser in 6 Tagen trinken kann und Mary ein Fass Wasser in 12 Tagen trinken kann, wie lange würde es dauern, bis sie zusammen ein Fass Wasser getrunken hätten? (Tage)"
    }
    if LANGUAGE_CODE in LANGUAGE_MAP.keys():
        return LANGUAGE_MAP[LANGUAGE_CODE][s]
    return s

class C(BaseConstants):
    NAME_IN_URL = 'crt7'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    crt7_jerry = models.IntegerField(min=0, max=50, label=_("Jerry received both the 15th highest and the 15th lowest mark in the class. How many students are in the class? (students)"))
    crt7_machines = models.IntegerField(min=0, max=500, label=_("If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets? (minutes)"))
    crt7_stocks = models.IntegerField(choices=[(0, _("broken even in the stock market")), (1, _("is ahead of where he began")), (2, _("has lost money"))], widget=widgets.RadioSelect, label=_("Simon decided to invest $8,000 in the stock market one day early in 2008. Six months after he invested, on July 17, the stocks he had purchased were down 50%. Fortunately for Simon, from July 17 to October 17, the stocks he had purchased went up 75%. At this point, Simon has:"))
    crt7_ball = models.FloatField(label=_("A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost? (dollars)"))
    crt7_lake = models.IntegerField(min=0, max=100, label=_("In a lake, there is a patch of lily pads. Every day, the patch doubles in size. If it takes 48 days for the patch to cover the entire lake, how long would it take for the patch to cover half of the lake? (days)"))
    crt7_pig = models.IntegerField(min=0, max=200, label=_("A man buys a pig for $60, sells it for $70, buys it back for $80, and sells it finally for $90. How much has he made? (dollars)"))
    crt7_barrels = models.IntegerField(min=0, max=100, label=_("If John can drink one barrel of water in 6 days, and Mary can drink one barrel of water in 12 days, how long would it take them to drink one barrel of water together? (days)"))

    crt7_score = models.FloatField()


# PAGES
class Part3Announcement(TranslatedPage):
    pass


class Part3Waitpage(WaitPage):
    def is_displayed(player):
        return not DEBUG

class CRT7(TranslatedPage):
    form_model = 'player'
    form_fields = ['crt7_jerry', 'crt7_machines', 'crt7_stocks', 'crt7_ball', 'crt7_lake', 'crt7_pig', 'crt7_barrels']

    def before_next_page(player, timeout_happened):
        player.crt7_score = sum([
            player.crt7_jerry == 29,
            player.crt7_machines == 5,
            player.crt7_stocks == 2,
            player.crt7_ball == 0.05,
            player.crt7_lake == 47,
            player.crt7_pig == 20,
            player.crt7_barrels == 4
        ])/7


page_sequence = [
    Part3Announcement,
    Part3Waitpage,
    CRT7
]
