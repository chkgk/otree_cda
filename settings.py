from os import environ

SESSION_CONFIGS = [
    dict(
         name="export_test",
         display_name="Export Test",
         app_sequence=["export_test"],
         num_demo_participants=4,
    ),
    dict(
        name="intro",
        display_name="Introduction",
        app_sequence=["intro"],
        num_demo_participants=4,
    ),
    dict(
        name="cda_practice",
        display_name="Asset Market Practice Period",
        app_sequence=['cda_practice'],
        num_demo_participants=4,
        trading_seconds=120,
        trading_summary_seconds=30,
        dividend_high=10,
        dividend_low=2,
        endowment_high_cash=(3000, 20),
        endowment_low_cash=(1000, 60),
    ),
    dict(
        name='stroop',
        display_name="1a Stroop Treatment",
        app_sequence=['stroop'],
        num_demo_participants=4,
    ),
    dict(
        name='movie',
        display_name="1b Movie Treatment",
        app_sequence=['movie'],
        num_demo_participants=4,
    ),
    dict(
        name='cda_rep1',
        display_name="2 Asset Market - Repetition 1",
        app_sequence=['cda_rep1'],
        num_demo_participants=4,
        trading_seconds=120,
        trading_summary_seconds=30,
        dividend_high=10,
        dividend_low=2,
        endowment_high_cash=(3000, 20),
        endowment_low_cash=(1000, 60),
    ),
    dict(
        name='cda_rep2',
        display_name="2 Asset Market - Repetition 2",
        app_sequence=['cda_rep2'],
        num_demo_participants=4,
        trading_seconds=120,
        trading_summary_seconds=30,
        dividend_high=10,
        dividend_low=2,
        endowment_high_cash=(3000, 20),
        endowment_low_cash=(1000, 60),
    ),
    dict(
        name="crt7",
        display_name="3.1 Cognitive Reflection Test",
        app_sequence=["crt7"],
        num_demo_participants=4,
    ),
    dict(
        name="apm",
        display_name="3.2 Advanced Progressive Matrices",
        app_sequence=["apm"],
        num_demo_participants=4,
    ),
    dict(
        name="egt",
        display_name="3.3 Eye Gaze Test",
        app_sequence=["egt"],
        num_demo_participants=4,
    ),
    dict(
        name="demographics",
        display_name="4 Demographics + Payments",
        app_sequence=["demographics"],
        num_demo_participants=4,
    ),
    dict(
        name="complete_stroop",  # needs second round of market
        display_name="Complete Experiment - Stroop",
        app_sequence=["intro", "cda_practice", "stroop", "cda_rep1", "cda_rep2", "crt7", "apm", "egt", "demographics"],
        num_demo_participants=4,
        experiment="stroop",
        trading_seconds=120,
        trading_summary_seconds=30,
        dividend_high=10,
        dividend_low=2,
        endowment_high_cash=(3000, 20),
        endowment_low_cash=(1000, 60),
    ),
    dict(
        name="complete_movie",  # needs second round of market
        display_name="Complete Experiment - Movie",
        app_sequence=["intro", "cda_practice", "movie", "cda_rep1", "cda_rep2", "crt7", "apm", "egt", "demographics"],
        num_demo_participants=4,
        experiment="movie",
        trading_seconds=120,
        trading_summary_seconds=30,
        dividend_high=10,
        dividend_low=2,
        endowment_high_cash=(3000, 20),
        endowment_low_cash=(1000, 60),
    )
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1/160, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '4324687630047'

