from channels.generic.websocket import JsonWebsocketConsumer
#from channels.generic.websockets import JsonWebsocketConsumer
from realefforttask.models import Player
from otree.models import Participant
from otree.models_concrete import ParticipantToPlayerLookup
import logging
#from realefforttask import channels_checker

logger = logging.getLogger(__name__)


class TaskTracker(JsonWebsocketConsumer):
    url_pattern = r'^RETtasktracker/(?P<participant_code>.+)$'

    def clean_kwargs(self):
        participant = Participant.objects.get(code__exact=self.kwargs['participant_code'])
    def set_vars(self):
        participant = Participant.objects.get(code__exact=self.participant_id)
        cur_page_index = participant._index_in_pages
        lookup = ParticipantToPlayerLookup.objects.get(participant=participant, page_index=cur_page_index)
        player_pk = lookup.player_pk
        self.player = Player.objects.get(id=player_pk)

    # def get_player(self):
    #     self.clean_kwargs()
    #     return Player.objects.get(id=self.player_pk)
    def receive_json(self, content, **kwargs):
        answer = content.get('answer')

    # def receive(self, text=None, bytes=None, **kwargs):
    #     player = self.get_player()
    #     answer = text.get('answer')

        # def receive_json(self, content, **kwargs):
        #     answer = content.get('answer')

        if answer:
#            old_task = player.get_or_create_task()
            old_task = self.player.get_or_create_task()
            old_task.answer = answer
            old_task.save()

            if old_task.answer == old_task.correct_answer:
                feedback = "Вы ответили правильно!"
            else:
                feedback = "Ваш предыдущий ответ " + old_task.answer + " был неверен, правильный ответ был " + \
                old_task.correct_answer + ". Будьте внимательны!"

            # new_task = player.get_or_create_task()
            # self.send({'task_body': new_task.html_body,
            #            'num_tasks_correct': player.num_tasks_correct,
            #            'num_tasks_total': player.num_tasks_total,
            #            })
            new_task = self.player.get_or_create_task()
            self.send_json({'task_body': new_task.html_body,
                            'num_tasks_correct': self.player.num_tasks_correct,
                            'num_tasks_total': self.player.num_tasks_total,
                            'feedback': feedback,
                            })

    # def connect(self, message, **kwargs):
    #     logger.info(f'Connected: {self.kwargs["participant_code"]}')


    def connect(self):
        self.participant_id = self.scope['url_route']['kwargs']['participant_code']
        self.set_vars()
        self.accept()
        logger.info(f'Connected: {self.participant_id}')