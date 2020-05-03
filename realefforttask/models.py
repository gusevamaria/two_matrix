import random
from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range,
)

from django.db import models as djmodels
from django.db.models import F
from otree.models import player

from . import ret_functions
import pandas as pd
import logging

logger = logging.getLogger(__name__)

author = ' Guseva Maria '

doc = """
    multi-round real effort task
"""


class Constants(BaseConstants):
    name_in_url = 'realefforttask'
    players_per_group = 8
    num_rounds = 5
    # this parameter defines how much time a user will stay on a RET page per round (in seconds)
    task_time = 180
    training_answer_All_correct = c(192)
    # Эта минимальная обязательная сумма выплачивается за участие в эксперименте всем участникам
    participation_fee = 0
    # Эта сумма должна быть выплачена победителю раунда или разделена среди n победителей
    total_round_payoff = 400

class Subsession(BaseSubsession):
    def creating_session(self):

        # we look for a corresponding Task Generator in our library (ret_functions.py) that contain all task-generating
        # functions. So the name of the generator in 'task_fun' parameter from settings.py should coincide with an
        # actual task-generating class from ret_functions.
        self.session.vars['task_fun'] = getattr(ret_functions, self.session.config['task'])
        # If a task generator gets some parameters (like a level of difficulty, or number of rows in a matrix etc.)
        # these parameters should be set in 'task_params' settings of an app, in a form of dictionary. For instance:
        # 'task_params': {'difficulty': 5}
        self.session.vars['task_params'] = self.session.config.get('task_params', {})

        # for each player we call a function (defined in Player's model) called get_or_create_task
        # this is done so that when a RET page is shown to a player for the first time they would already have a task
        # to work on
        for p in self.get_players():
            p.get_or_create_task()



class Group(BaseGroup):
    def set_ranking(self):
        players = self.get_players()
        values = [p.num_tasks_correct for p in players]
        data = dict(player=players, value=values)
        df = pd.DataFrame(data)
        df['rank'] = df['value'].rank(method='min', ascending=False)

        num_winners = 0
        for index, row in df.iterrows():
            row['player'].rank = int(row['rank'])
            if row['player'].rank == 1:
                row['player'].round_win = 1
                num_winners += 1
            else:
                row['player'].round_win = 0
        payout_per_round = int(Constants.total_round_payoff / num_winners)

        for p in players:
            if p.round_win == 1:
                p.participant.payoff = payout_per_round
                p.pay = p.participant.payoff
                p.win_per_round = num_winners
            else:
                p.pay = 0



#final_payoff = p.pay + Constants.participation_fee
#cycle for round control(in Players??)
# for round in self.player.in_all_rounds():



class Player(BasePlayer):
    rank = models.IntegerField()
    round_win = models.IntegerField()
    pay = models.CurrencyField()
    final_payoff = models.CurrencyField()


    # here we store all tasks solved in this specific round - for further analysis
    tasks_dump = models.LongStringField(doc='to store all tasks with answers, diff level and feedback')
    training_answer_All = models.IntegerField(verbose_name='This training_answer')

    # this method returns number of correct tasks solved in this round
    @property
    def num_tasks_correct(self):
        return self.tasks.filter(correct_answer=F('answer')).count()
    # logger.info(f'Правильных answer: {num_tasks_correct}')

    # this method returns total number of tasks to which a player provided an answer
    @property
    def num_tasks_total(self):
        return self.tasks.filter(answer__isnull=False).count()
    # logger.info(f'Всего answer: {num_tasks_total}')

    # The following method checks if there are any unfinished (with no answer) tasks. If yes, we return the unfinished
    # task. If there are no uncompleted tasks we create a new one using a task-generating function from session settings
    def get_or_create_task(self):
        unfinished_tasks = self.tasks.filter(answer__isnull=True)
        if unfinished_tasks.exists():
            return unfinished_tasks.first()
        else:
            task = Task.create(self, self.session.vars['task_fun'], **self.session.vars['task_params'])
            task.save()
            return task

    fname = models.StringField()
    lname = models.StringField()
    otchestvo = models.StringField()
    age = models.IntegerField(min=14, max=60)
    phone = models.StringField()
    city = models.StringField()
    sex = models.StringField(
        choices=[
            ['Мужской', 'Мужской'],
            ['Женский', 'Женский'],
        ],
        widget=widgets.RadioSelect
    )
    # вопрос про разглашение своего места (rank_disclosure) сразу после таблицы с результатами
    rank_disclosure = models.CharField(
        choices=['Да, было бы лучше, если бы никто не увидел мой результат',
                 'Нет, хочу, чтоб все увидели мой результат', 'Не знаю'],
        widget=widgets.RadioSelect()
    )

    # вопросы между раундами
    expected_result = models.IntegerField(min=1, max=8)
    inter_question_1 = models.CharField(
        choices=['Больше', 'Не знаю', 'Меньше', 'Предыдущего раунда ещё не было'],
        widget=widgets.RadioSelect()
    )
    inter_question_2 = models.CharField(
        choices=['Полностью соглашусь', 'Скорее соглашусь, чем нет', 'Не знаю', 'Скорее не соглашусь, чем соглашусь',
                 'Полностью не соглашусь'],
        widget=widgets.RadioSelect()
    )

    inter_question_3 = models.CharField(
        choices=['Полностью соглашусь', 'Скорее соглашусь, чем нет', 'Не знаю', 'Скорее не соглашусь, чем соглашусь',
                 'Полностью не соглашусь'],
        widget=widgets.RadioSelect()
    )

    inter_question_4 = models.CharField(
        choices=['Полностью соглашусь', 'Скорее соглашусь, чем нет', 'Не знаю', 'Скорее не соглашусь, чем соглашусь',
                 'Полностью не соглашусь'],
        widget=widgets.RadioSelect()
    )


    # вопросы после эксперимента
    end_question_1 = models.CharField(
        choices=['Да, меня устраивает перевод на телефон', 'Нет, я хочу получить перевод только на банковскую карту'],
        widget=widgets.RadioSelect()
    )
    end_question_2 = models.CharField(
        choices=[
            'А что получили остальные ученики в классе?',
            'Как мы можем тебе помочь, чтобы ты понял материал этой контрольной?',
            'Много ли времени ты уделил подготовке к этой контрольной?',
            'А учитель хорошо объяснил(а) тему этой контрольной?',
        ],
        widget=widgets.RadioSelect()
    )
    end_question_3 = models.CharField(
        choices=['Среднеобразовательная школа', 'Гимназия с физ.мат/гуманитарным уклоном', 'Лицей при университете','Колледж'],
        widget=widgets.RadioSelect()
    )
    end_question_4 = models.CharField(
        choices=['Личная (я знаю только своё место в общем рейтинге и не вижу тех, кто выше меня и кто ниже меня)','Публичная ( таблица общего рейтинга, где я могу посмотреть место, занимаемое мною и места других студентов)'],
        widget=widgets.RadioSelect()
    )
    end_question_5 = models.CharField(
        choices=['Я сраниваю свою текущую позицию в общем рейтинге со своей предыдущей позицией', 'Я сраниваю свою текущую позицию в общем рейтинге с позицями других студентов','Я вообще не смотрю рейтинг'],
        widget=widgets.RadioSelect()
    )
    end_question_6 = models.CharField(
        choices=['Да', 'Нет'],
        widget=widgets.RadioSelect()
    )
    end_question_7 = models.CharField(
        choices=['Правдиво', 'Наобум'],
        widget=widgets.RadioSelect()
    )
    end_question_8 = models.CharField(
        choices=['1', '2', '3', '4', '5'],
        widget=widgets.RadioSelect(),
    )
    interruption = models.CharField(
        choices=['Да', 'Нет'],
        widget=widgets.RadioSelect()
    )
    rules_understanding = models.CharField(
        choices=['0', '1', '2', '3', '4', '5'],
        widget=widgets.RadioSelect()
    )
    # hidden_correct_input = models.IntegerField()
    hidden_total_answer = models.IntegerField()
    hidden_correct_answer = models.IntegerField()

    total_score = models.IntegerField(initial=0)
    win_per_round = models.IntegerField(initial=0)


# This is a custom model that contains information about individual tasks. In each round, each player can have as many
# tasks as they tried to solve (we can call for the set of all tasks solved by a player by calling for instance
# player.tasks.all()
# Each task has a body field, html_body - actual html code shown at each page, correct answer and an answer provided by
# a player. In addition there are two automatically updated/created fields that track time of creation and of an update
# These fields can be used to track how long each player works on each task
class Task(djmodels.Model):
    class Meta:
        ordering = ['-created_at']

    player = djmodels.ForeignKey(to=Player, related_name='tasks', on_delete=djmodels.CASCADE)
    round_number = models.IntegerField(null=True)
    body = models.LongStringField()
    html_body = models.LongStringField()
    correct_answer = models.StringField()
    answer = models.StringField(null=True)
    created_at = djmodels.DateTimeField(auto_now_add=True)
    updated_at = djmodels.DateTimeField(auto_now=True)
    task_name = models.StringField()
    # the following method creates a new task, and requires as an input a task-generating function and (if any) some
    # parameters fed into task-generating function.
    @classmethod
    def create(cls, player, fun, **params):
        proto_task = fun(**params)
        task = cls(player=player,
                   body=proto_task.body,
                   html_body=proto_task.html_body,
                   correct_answer=proto_task.correct_answer,
                   task_name = proto_task.name)
        return task
