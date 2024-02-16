from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import os


author = 'Felix Holzmeister. Adapted by Christian König-Kersting in 2024.'

doc = """
Eye Gaze Test as proposed by Baron-Cohen et al (2001).
"""


# ******************************************************************************************************************** #
# *** CLASS CONSTANTS
# ******************************************************************************************************************** #
class Constants(BaseConstants):
    name_in_url = 'egt'
    players_per_group = None

    # list of lists of choices
    # ----------------------------------------------------------------------------------------------------------------
    choices = [
        # set 1
        ['playful', 'comforting', 'irritated', 'bored'],
        # set 2
        ['terrified', 'upset', 'arrogant', 'annoyed'],
        # set 3
        ['joking', 'flustered', 'desire', 'convinced'],
        # set 4
        ['joking', 'insisting', 'amused', 'relaxed'],
        # set 5
        ['irritated', 'sarcastic', 'worried', 'friendly'],
        # set 6
        ['aghast', 'fantasizing', 'impatient', 'alarmed'],
        # set 7
        ['apologetic', 'friendly', 'uneasy', 'dispirited'],
        # set 8
        ['despondent', 'relieved', 'shy', 'excited'],
        # set 9
        ['annoyed', 'hostile', 'horrified', 'preoccupied'],
        # set 10
        ['cautious', 'insisting', 'bored', 'aghast'],
        # set 11
        ['terrified', 'amused', 'regretful', 'flirtatious'],
        # set 12
        ['indifferent', 'embarrassed', 'sceptical', 'dispirited'],
        # set 13
        ['decisive', 'anticipating', 'threatening', 'shy'],
        # set 14
        ['irritated', 'disappointed', 'depressed', 'accusing'],
        # set 15
        ['contemplative', 'flustered', 'encouraging', 'amused'],
        # set 16
        ['irritated', 'thoughtful', 'encouraging', 'sympathetic'],
        # set 17
        ['doubtful', 'affectionate', 'playful', 'aghast'],
        # set 18
        ['decisive', 'amused', 'aghast', 'bored'],
        # set 19
        ['arrogant', 'grateful', 'sarcastic', 'tentative'],
        # set 20
        ['dominant', 'friendly', 'guilty', 'horrified'],
        # set 21
        ['embarrassed', 'fantasizing', 'confused', 'panicked'],
        # set 22
        ['preoccupied', 'grateful', 'insisting', 'imploring'],
        # set 23
        ['contented', 'apologetic', 'defiant', 'curious'],
        # set 24
        ['pensive', 'irritated', 'excited', 'hostile'],
        # set 25
        ['panicked', 'incredulous', 'despondent', 'interested'],
        # set 26
        ['alarmed', 'shy', 'hostile', 'anxious'],
        # set 27
        ['joking', 'cautious', 'arrogant', 'reassuring'],
        # set 28
        ['interested', 'joking', 'affectionate', 'contented'],
        # set 29
        ['impatient', 'aghast', 'irritated', 'reflective'],
        # set 30
        ['grateful', 'flirtatious', 'hostile', 'disappointed'],
        # set 31
        ['ashamed', 'confident', 'joking', 'dispirited'],
        # set 32
        ['serious', 'ashamed', 'bewildered', 'alarmed'],
        # set 33
        ['embarrassed', 'guilty', 'fantasizing', 'concerned'],
        # set 34
        ['aghast', 'baffled', 'distrustful', 'terrified'],
        # set 35
        ['puzzled', 'nervous', 'insisting', 'contemplative'],
        # set 36
        ['ashamed', 'nervous', 'suspicious', 'indecisive']
    ]

    # list of lists of synonyms
    # ----------------------------------------------------------------------------------------------------------------
    synonyms = [
        # set 1
        [
            # playful
            'full of high spirits and fun',
            # comforting
            'consoling, compassionate<b/><br/>',
            # irritated
            'exasperated, annoyed',
            # bored
            'tired, fatigued'
        ],
        # set 2
        [
            # terrified
            'alarmed, fearful',
            # upset
            'agitated, worried, uneasy',
            # arrogant
            'conceited, self-important, having a big opinion of oneself',
            # annoyed
            'irritated, displeased'
        ],
        # set 3
        [
            # joking
            'being funny, playful',
            # flustered
            'confused, nervous and upset',
            # desire
            'passion, lust, longing for',
            # convinced
            'certain, absolutely positive'
        ],
        # set 4
        [
            # joking
            'being funny, playful',
            # insisting
            'demanding, persisting, maintaining',
            # amused
            'finding something funny',
            # relaxed
            'taking it easy, calm, carefree'
        ],
        # set 5
        [
            # irritated
            'exasperated, annoyed',
            # sarcastic
            'cynical, mocking, scornful',
            # worried
            'anxious, fretful, troubled',
            # friendly
            'sociable, amiable'
        ],
        # set 6
        [
            # aghast
            'horrified, astonished, alarmed',
            # fantasizing
            'daydreaming',
            # impatient
            'restless, wanting something to happen soon',
            # alarmed
            'fearful, worried, filled with anxiety'
        ],
        # set 7
        [
            # apologetic
            'feeling sorry',
            # friendly
            'sociable, amiable',
            # uneasy
            'unsettled, apprehensive, troubled',
            # dispirited
            'glum, miserable, low'
        ],
        # set 8
        [
            # despondent
            'gloomy, despairing, without hope',
            # relieved
            'freed from worry or anxiety',
            # shy
            'coy, sheepish, shortspoken',
            # excited
            'fevered, aroused, nervous'
        ],
        # set 9
        [
            # annoyed
            'irritated, displeased',
            # hostile
            'unfriendly',
            # horrified
            'terrified, appalled',
            # preoccupied
            'absorbed, engrossed in one´s own thoughts',
        ],
        # set 10
        [
            # cautious
            'careful, wary',
            # insisting
            'demanding, persisting, maintaining',
            # bored
            'tired, fatigued',
            # aghast
            'horrified, astonished, alarmed'
        ],
        # set 11
        [
            # terrified
            'alarmed, fearful',
            # amused
            'finding somethin funny',
            # regretful
            'sorry',
            # flirtatious
            'brazen, saucy, teasing, playful'
        ],
        # set 12
        [
            # indifferent
            'disinterested, unresponsive, don´t care',
            # embarrassed
            'ashamed',
            # sceptical
            'doubtful, suspicious, mistrusting',
            # dispirited
            'glum, miserable, low'
        ],
        # set 13
        [
            # decisive
            'already made your mind up',
            # anticipating
            'expecting',
            # threatening
            'menacing, intimidating',
            # shy
            'coy, sheepish, shortspoken'
        ],
        # set 14
        [
            # irritated
            'exasperated, annoyed',
            # disappointed
            'displeased, disgruntled',
            # depressed
            'miserable',
            # accusing
            'blaming'
        ],
        # set 15
        [
            # contemplative
            'reflective, thoughtful, considering',
            # flustered
            'confused, nervous and upset',
            # encouraging
            'hopeful, heartening, supporting',
            # amused
            'finding something funny'
        ],
        # set 16
        [
            # irritated
            'exasperated, annoyed',
            # thoughtful
            'thinking about something',
            # encouraging
            'hopeful, heartening, supporting',
            # sympathetic
            'kind, compassionate'
        ],
        # set 17
        [
            # doubtful
            'dubious, suspicious, not really believing',
            # affectionate
            'showing fondness toward someone',
            # playful
            'fully of high spirits and fun',
            # aghast
            'horrified, astonished, alarmed'
        ],
        # set 18
        [
            # decisive
            'already made your mind up',
            # amused
            'finding something funny',
            # aghast
            'horrified, astonished, alarmed',
            # bored
            'tired, fatigued'
        ],
        # set 19
        [
            # arrogant
            'conceited, self-important, having a big opinion of oneself',
            # grateful
            'thankful',
            # sarcastic
            'cynical, mocking, scornful',
            # tentative
            'hesitant, uncertain, cautious'
        ],
        # set 20
        [
            # dominant
            'commanding, bossy',
            # friendly
            'sociable, amiable',
            # guilty
            'feeling sorry for doing something wrong',
            # horrified
            'terrified, appalled'
        ],
        # set 21
        [
            # embarrassed
            'ashamed',
            # fantasizing
            'daydreaming',
            # confused
            'puzzled, perplexed',
            # panicked
            'distraught, feeling of terror or anxiety'
        ],
        # set 22
        [
            # preoccupied
            'absorbed, engrossed in one´s own thoughts',
            # grateful
            'thankful',
            # insisting
            'demanding, persisting, maintaining',
            # imploring
            'begging, pleading'
        ],
        # set 23
        [
            # contented
            'satisfied',
            # apologetic
            'feeling sorry',
            # defiant
            'insolent, bold, don´t care what anyone ele thinks',
            # curious
            'inquisitive, inquiring, prying'
        ],
        # set 24
        [
            # pensive
            'thinking about something slightly worrying',
            # irritated
            'exasperated, annoyed',
            # excited
            'fevered, aroused, nervous',
            # hostile
            'unfriendly'
        ],
        # set 25
        [
            # panicked
            'distraught, feeling of terror or anxiety',
            # incredulous
            'not believing',
            # despondent
            'gloomy, despairing, without hope',
            # interested
            'inquiring, curious'
        ],
        # set 26
        [
            # alarmed
            'fearful, worried, filled with anxiety',
            # shy
            'coy, sheepish, shortspoken',
            # hostile
            'unfriendly',
            # anxious
            'worried, tense, uneasy'
        ],
        # set 27
        [
            # joking
            'being funny, playful',
            # cautious
            'careful, wary',
            # arrogant
            'conceited, self-important, having a big opinion of oneself',
            # reassuring
            'supporting, encouraging, giving someone confidence'
        ],
        # set 28
        [
            # interested
            'inquiring, curious',
            # joking
            'being funny, playful',
            # affectionate
            'showing fondness toward someone',
            # contented
            'satisfied'
        ],
        # set 29
        [
            # impatient
            'restless, wanting something to happen soon',
            # aghast
            'horrified, astonished, alarmed',
            # irritated
            'exasperated, annoyed',
            # reflective
            'contemplative, thoughtful'
        ],
        # set 30
        [
            # grateful
            'thankful',
            # flirtatious
            'brazen, saucy, teasing, playful',
            # hostile
            'unfriendly',
            # disappointed
            'displeased, disgruntled'
        ],
        # set 31
        [
            # ashamed
            'overcome with shame or guilt',
            # confident
            'self-assured, believing in oneself',
            # joking
            'being funny, playful',
            # dispirited
            'glum, miserable, low'
        ],
        # set 32
        [
            # serious
            'solemn, grave',
            # ashamed
            'overcome with shame or guilt',
            # bewildered
            'utterly confused, puzzled, dazed',
            # alarmed
            'fearful, worried, filled with anxiety'
        ],
        # set 33
        [
            # embarrassed
            'ashamed',
            # guilty
            'feeling sorry for doing something wrong',
            # fantasizing
            'daydreaming',
            # concerned
            'worried, troubled'
        ],
        # set 34
        [
            # aghast
            'horrified, astonished, alarmed',
            # baffled
            'confused, puzzled, dumfounded',
            # distrustful
            'suspicious, doubtful, wary',
            # terrified
            'alarmed, fearful'
        ],
        # set 35
        [
            # puzzled
            'perplexed, bewildered, confused',
            # nervous
            'apprehensive, tense, worried',
            # insisting
            'demanding, persisting, maintaining',
            # contemplative
            'reflective, thoughtful, considering'
        ],
        # set 36
        [
            # ashamed
            'overcome with shame or guilt',
            # nervous
            'apprehensive, tense, worried',
            # suspicious
            'disbelieving, suspecting, doubting',
            # indecisive
            'unsure, hesitant, unable to make your mind up'
        ]
    ]

    # list of lists of example sentences
    # ----------------------------------------------------------------------------------------------------------------
    examples = [
        # set 1
        [
            # playful
            'Neil was feeling <i>playful</i> at his birthday party.',
            # comforting
            'The nurse was <i>comforting</i> the wounded soldier.',
            # irritated
            'Frances was <i>irritated</i> by all the jun mail she received.',
            # bored
            'The long speech <i>bored</i> me.'
        ],
        # set 2
        [
            # terrified
            'The boy was <i>terrified</i> when he though he saw a ghost.',
            # upset
            'The man was very <i>upset</i> when his mother died.',
            # arrogant
            'The <i>arrogant</i> man thought he knew more about politics than everyone else in the room.',
            # annoyed
            'Jack was <i>annoyed</i> by a funny joke someone told me.'
        ],
        # set 3
        [
            # joking
            'Gary was always <i>joking</i> with his friends.',
            # flustered
            'Sarah felt a bit <i>flustered</i> when she realized how late she was for the meeting '
            'and that she had forgotten an important document.',
            # desire
            'Kate had a strong <i>desire</i> for chocolate.',
            # convinced
            'Richard was <i>convinced</i> he had come to the right decision.'
        ],
        # set 4
        [
            # joking
            'Gary was always <i>joking</i> with his friends.',
            # insisting
            'After a work outing, Frank was <i>insisting</i> he paid the bill for everyone.',
            # amused
            'I was <i>amused</i> by a funny joke someone told me.',
            # relaxed
            'On holiday, Pam felt happy and <i>relaxed</i>.'
        ],
        # set 5
        [
            # irritated
            'Frances was <i>irritated</i> by all the junk mail she received.',
            # sarcastic
            'The comedian made a <i>sarcastic</i> comment when someone came into the theatre late.',
            # worried
            'When her cat went missing, the girl was very <i>worried</i>.',
            # friendly
            'The <i>friendly</i> girl showed the tourists the way to the town centre.'
        ],
        # set 6
        [
            # aghast
            'Jane was <i>aghast</i> when she discovered her house had been burgled.',
            # fantasizing
            'Emma was <i>fantasizing</i> about being a film star.',
            # impatient
            'Jane grew increasingly <i>impatient</i> as she waited for her friend who was already 20 minutes late.',
            # alarmed
            'Claire was <i>alarmed</i> when she thought she was being followed home.'
        ],
        # set 7
        [
            # apologetic
            'The waiter was very <i>apologetic</i> when he spilt soup all over the customer.',
            # friendly
            'The <i>friendly</i> girl showed the tourists the way to the town centre.',
            # uneasy
            'Karen felt slightly <i>uneasy</i> about accepting a lift from the man she had only met tat day.',
            # dispirited
            'Adam was <i>dispirited</i> when he failed his exams.'
        ],
        # set 8
        [
            # despondent
            'Gary was <i>despondent</i> when he did not get the job he wanted.',
            # relieved
            'At the restaurant, Ray was <i>relieved</i> to find he had not forgotten his wallet.',
            # shy
            'She was to <i>shy</i> to ask for help.',
            # excited
            'The little girl was very <i>excited</i> in anticipation of her birthday party.'
        ],
        # set 9
        [
            # annoyed
            'Jack was <i>annoyed</i> when he found out he had missed the last bus home.',
            # hostile
            'The two neighbours were <i>hostile</i> towards each other because of an argument about loud music.',
            # horrified
            'The man was <i>horrified</i> to discover that his new wife was already married.',
            # preoccupied
            'Worrying about her mother´s illness made Debbie <i>preoccupied</i> at work.',
        ],
        # set 10
        [
            # cautious
            'Sarah was always a bit <i>cautious</i> when talking to someone she did not know.',
            # insisting
            'After a work outing, Frank was <i>insisting</i> he paid the bill for everyone.',
            # bored
            'The long speech <i>bored</i> me.',
            # aghast
            'Jane was <i>aghast</i> when she discovered her house had been burgled.'
        ],
        # set 11
        [
            # terrified
            'The boy was <i>terrified</i> when he thought he saw a ghost.',
            # amused
            'I was <i>amused</i> by a funny joke someone told me.',
            # regretful
            'Lee was always <i>regretful</i> that he had never travelled when he was younger.',
            # flirtatious
            'Connie was accused of being <i>flirtatious</i> when she winked at a stranger at a party.'
        ],
        # set 12
        [
            # indifferent
            'Terry was completely <i>indifferent</i> as to whether they went to the cinema or the pub.',
            # embarrassed
            'After forgetting a colleague´s name, Jenny felt very <i>embarrassed</i>.',
            # sceptical
            'Patrick looked <i>sceptical</i> as someone read out his horoscope to him.',
            # dispirited
            'Adam was <i>dispirited</i> when he failed his exams.'
        ],
        # set 13
        [
            # decisive
            'Jane looked very <i>decisive</i> as she walked into the polling station.',
            # anticipating
            'At the start of the football match, the fans were <i>anticipating</i> a quiick goal.',
            # threatening
            'The large, drunk man was acting in a very <i>threatening</i> way.',
            # shy
            'She was to <i>shy</i> to ask for help.'
        ],
        # set 14
        [
            # irritated
            'Frances was <i>irritated</i> by all the junk mail she received.',
            # disappointed
            'Manchester United fans were <i>disappointed</i> not to win the Championship.',
            # depressed
            'George was <i>depressed</i> when he did not receive any birthday cards.',
            # accusing
            'The policeman was <i>accusing</i> the man of stealing a wallet.'
        ],
        # set 15
        [
            # contemplative
            'John was in a <i>contemplative</i> mood on the eve of his 60th birthday.',
            # flustered
            'Sarah felt a bit <i>flustered</i> when she realised how late she was for the meeting'
            'and that she had forgotten an important document.',
            # encouraging
            'All the parents were <i>encouraging</i> their children in the school sports day.',
            # amused
            'I was <i>amused</i> by a funny joke someone told me.'
        ],
        # set 16
        [
            # irritated
            'Frances was <i>irritated</i> by all the junk mail she received.',
            # thoughtful
            'Phil looked <i>thoughtful</i> as he sat waiting for the girlfriend he was about to finish with.',
            # encouraging
            'All the parents were <i>encouraging</i> their children in the school sports day.',
            # sympathetic
            'The nurse looked <i>sympathetic</i> as she told the patient the bad news.'
        ],
        # set 17
        [
            # doubtful
            'Mary was <i>doubtful</i> that her son was telling the truth.',
            # affectionate
            'Most mothers are <i>affectionate</i> to their babies by giving them lots of kisses and cuddles.',
            # playful
            'Neil was feeling <i>playful</i> at his birthday party.',
            # aghast
            'Jane was <i>aghast</i> when she discovered her house had been burgled.'
        ],
        # set 18
        [
            # decisive
            'Jane looked very <i>decisive</i> as she walked into the polling station.',
            # amused
            'I was <i>amused</i> by a funny joke someone told me.',
            # aghast
            'Jane was <i>aghast</i> when she discovered her house had been burgled.',
            # bored
            'The long speech <i>bored</i> me.'
        ],
        # set 19
        [
            # arrogant
            'The <i>arrogant</i> man thought he knew more about politics than everyone else in the room.',
            # grateful
            'Kelly was very <i>grateful</i> for the kindness shown by the stranger.',
            # sarcastic
            'The comedian made a <i>sarcastic</i> comment when someone came into the theatre late.',
            # tentative
            'Andrew felt a bit <i>tentative</i> as he went into the room full of strangers.'
        ],
        # set 20
        [
            # dominant
            'The sergeant major looked <i>dominant</i> as he inspected the new recruits.',
            # friendly
            'The <i>friendly</i> girl showed the tourists the way to the town centre.',
            # guilty
            'Charlie felt <i>guilty</i> about having an affair.',
            # horrified
            'The man was <i>horrified</i> to discover that his new wife was already married.'
        ],
        # set 21
        [
            # embarrassed
            'After forgetting a colleague´s name, Jenny felt very <i>embarrassed</i>.',
            # fantasizing
            'Emma was <i>fantasizing</i> about being a film star.',
            # confused
            'Lizzie was so <i>confused</i> by the directions given to her, she got lost.',
            # panicked
            'On walking to find the house on fire, the whole family were <i>panicked</i>.'
        ],
        # set 22
        [
            # preoccupied
            'Worrying about her mother´s illness made Debbie <i>preoccupied</i> at work.',
            # grateful
            'Kelly was very <i>grateful</i> for the kindness shown by the stranger.',
            # insisting
            'After a work outing, Frank was <i>insisting</i> he paid the bill for everyone.',
            # imploring
            'Nicola looked <i>imploring</i> as she tried to persuade her dad to lend her the car.'
        ],
        # set 23
        [
            # contented
            'After a nice walk and a good meal, David felt very <i>contented</i>.',
            # apologetic
            'The waiter was very <i>apologetic</i> when he spilt soup all over the customer.',
            # defiant
            'The animal protester remained <i>defiant</i> even after being sent to prison.',
            # curious
            'Louise was <i>curious</i> about the strange-shaped parcel.'
        ],
        # set 24
        [
            # pensive
            'Susie looked <i>pensive</i> on the way to meeting her boyfriend´s parents for the first time.',
            # irritated
            'Frances was <i>irritated</i> by all the junk mail she received.',
            # excited
            'The little girl was very <i>excited</i> in anticipation of her birthday party.',
            # hostile
            'The two neighbours were <i>hostile</i> towards each other because of an argument about loud music.'
        ],
        # set 25
        [
            # panicked
            'On waking to find the house on fire, the whole family were <i>panicked</i>.',
            # incredulous
            'Simon was <i>incredulous</i> when he heard that he had won the lottery.',
            # despondent
            'Gary was <i>despondent</i> when he did not get the job he wanted.',
            # interested
            'After seeing Jurassic Park, Huge grew very <i>interested</i> in dinosaurs.'
        ],
        # set 26
        [
            # alarmed
            'Claire was <i>alarmed</i> when she thought she was being followed home.',
            # shy
            'She was to <i>shy</i> to ask for help.',
            # hostile
            'The two neighbours were <i>hostile</i> towards each other because of an argument about loud music.',
            # anxious
            'The student was feeling <i>anxious</i> before taking her final exams.'
        ],
        # set 27
        [
            # joking
            'Gary was always <i>joking</i> with his friends.',
            # cautious
            'Sarah was always a bit <i>cautious</i> when talking to someone she did not know.',
            # arrogant
            'The <i>arrogant</i> man thought he knew more about politics than everyone else in the room.',
            # reassuring
            'Andy tried to look <i>reassuring</i> as he told his wife that her new dress did suit her.'
        ],
        # set 28
        [
            # interested
            'After seeing Jurassic Park, Huge grew very <i>interested</i> in dinosaurs.',
            # joking
            'Gary was always <i>joking</i> with his friends.',
            # affectionate
            'Most mothers are <i>affectionate</i> to their babies by giving them lots of kisses and cuddles.',
            # contented
            'After a nice walk and a good meal, David felt very <i>contented</i>.'
        ],
        # set 29
        [
            # impatient
            'Jane grew increasingly <i>impatient</i> as she waited for her friend who was already 20 minutes late.',
            # aghast
            'Jane was <i>aghast</i> when she discovered her house had been burgled.',
            # irritated
            'Frances was <i>irritated</i> by all the junk mail she received.',
            # reflective
            'George was in a <i>reflective</i> mood as he thought about what he had done with his life.'
        ],
        # set 30
        [
            # grateful
            'Kelly was very <i>grateful</i> for the kindness shown by the stranger.',
            # flirtatious
            'Connie was accused of being <i>flirtatious</i> when she winked at a stranger at a party.',
            # hostile
            'The two neighbours were <i>hostile</i> towards each other because of an argument about loud music.',
            # disappointed
            'Manchester United fans were <i>disappointed</i> not to win the Championship.'
        ],
        # set 31
        [
            # ashamed
            'The boy felt <i>ashamed</i> when his mother discovered him stealing money from her purse.',
            # confident
            'The tennis player was feeling very <i>confident</i> about winning his match.',
            # joking
            'Gary was always <i>joking</i> with his friends.',
            # dispirited
            'Adam was <i>dispirited</i> when he failed his exams.'
        ],
        # set 32
        [
            # serious
            'The bank manager looked <i>serious</i> as he refused Nigel an overdraft.',
            # ashamed
            'The boy felt <i>ashamed</i> when his mother discovered him stealing money from her purse.',
            # bewildered
            'The child was <i>bewildered</i> when visiting the big city for the first time.',
            # alarmed
            'Claire was <i>alarmed</i> when she thought she was being followed home.'
        ],
        # set 33
        [
            # embarrassed
            'After forgetting a colleague´s name, Jenny felt very <i>embarrassed</i>.',
            # guilty
            'Charlie felt <i>guilty</i> about having an affair.',
            # fantasizing
            'Emma was <i>fantasizing</i> about being a film star.',
            # concerned
            'The doctor was <i>concerned</i> when his patient took a turn for the worse.'
        ],
        # set 34
        [
            # aghast
            'Jane was <i>aghast</i> when she discovered her house had been burgled.',
            # baffled
            'The detectives were completely <i>baffled</i> by the murder case.',
            # distrustful
            'The old woman was <i>distrustful</i> of the stranger at her door.',
            # terrified
            'The boy was <i>terrified</i> when he thought he saw a ghost.'
        ],
        # set 35
        [
            # puzzled
            'After doing the crossword for an hour, June was still <i>puzzled</i> by one clue.',
            # nervous
            'Just before her job interview, Alice felt very <i>nervous</i>.',
            # insisting
            'After a work outing, Frank was <i>insisting</i> he paid the bill for everyone.',
            # contemplative
            'John was in a <i>contemplative</i> mood on the eve of his 60th birthday.'
        ],
        # set 36
        [
            # ashamed
            'The boy felt <i>ashamed</i> when his mother discovered him stealing money from her purse.',
            # nervous
            'Just before her job interview, Alice felt very <i>nervous</i>.',
            # suspicious
            'After Sam had lost his wallet for the second time at work, '
            'he grew <i>suspicious</i> of one of his colleagues.',
            # indecisive
            'Tammy was so <i>indecisive</i> that she could not even decide what to have for lunch.'
        ]
    ]

    # list of correct answers
    # ----------------------------------------------------------------------------------------------------------------
    correct = [
        'playful',       # set 1
        'upset',         # set 2
        'desire',        # set 3
        'insisting',     # set 4
        'worried',       # set 5
        'fantasizing',   # set 6
        'uneasy',        # set 7
        'despondent',    # set 8
        'preoccupied',   # set 9
        'cautious',      # set 10
        'regretful',     # set 11
        'sceptical',     # set 12
        'anticipating',  # set 13
        'accusing',      # set 14
        'contemplative', # set 15
        'thoughtful',    # set 16
        'doubtful',      # set 17
        'decisive',      # set 18
        'tentative',     # set 19
        'friendly',      # set 20
        'fantasizing',   # set 21
        'preoccupied',   # set 22
        'defiant',       # set 23
        'pensive',       # set 24
        'interested',    # set 25
        'hostile',       # set 26
        'cautious',      # set 27
        'interested',    # set 28
        'reflective',    # set 29
        'flirtatious',   # set 30
        'confident',     # set 31
        'serious',       # set 32
        'concerned',     # set 33
        'distrustful',   # set 34
        'nervous',       # set 35
        'suspicious'     # set 36
    ]

    # dynamically determine list of all images
    # ----------------------------------------------------------------------------------------------------------------
    images = [str(j)+'.png' for j in range(1,37)]

    # commenting this out. Corgnet et al did all 36 in 10 minutes.

    # only keep odd-numbered items
    # ----------------------------------------------------------------------------------------------------------------
    # images = images[::2]
    # choices = choices[::2]
    # synonyms = synonyms[::2]
    # examples = examples[::2]
    # correct = correct[::2]

    # set number of rounds
    # ----------------------------------------------------------------------------------------------------------------
    num_rounds = len(images)

    gto_seconds = 600


# ******************************************************************************************************************** #
# *** CLASS SUBSESSION
# ******************************************************************************************************************** #
class Subsession(BaseSubsession):

    # set correct emotion
    # ----------------------------------------------------------------------------------------------------------------
    def creating_session(self):
        for p in self.get_players():
            p.correct = Constants.correct[self.round_number - 1]


# ******************************************************************************************************************** #
# *** CLASS GROUP
# ******************************************************************************************************************** #
class Group(BaseGroup):
    pass


# ******************************************************************************************************************** #
# *** CLASS PLAYER
# ******************************************************************************************************************** #
class Player(BasePlayer):

    choice = models.CharField()
    correct = models.CharField()
    score = models.IntegerField()

    # verify whether choice has been correct
    # ----------------------------------------------------------------------------------------------------------------
    def verify_if_correct(self):
        if self.choice == self.correct:
            self.score = 1
        else:
            self.score = 0
