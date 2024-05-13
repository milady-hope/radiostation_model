import random

from datetime import datetime, timedelta
from library import *
from requests import *

class RadioStation:
    """Класс для моделирования работы радиостанции.

    Attributes:
        programs_in_day (int): Количество программ в день.
        modeling_days (int): Общее количество дней для моделирования.
        duration_time (int): Длительность каждой программы в секундах.
        modeling_step (int): Шаг моделирования в минутах.
        sec_gen_from (int), sec_gen_to (int): Частота генерации заявок на песни в секундах.
        start_time (datetime): Начальная дата и время моделирования.
        current_time (datetime): Текущее время в процессе моделирования.
        requests_list (list): Список заявок на песни.
        programs_list (list): Список сгенерированных программ.
        executed_requests (list): Список исполненных заявок.
        song_library (SongLibrary): Библиотека песен.

    Methods:
        generate_program_by_requests: Создает программу на основе заявок.
        generate_hit_parade: Создает хит-парад на основе жанра.
        modeling: Запускает моделирование радиостанции.
    """

    def __init__(self, programs_in_day, modeling_days, duration_time, modeling_step, sec_gen_from, sec_gen_to):
        self.programs_in_day = programs_in_day
        self.modeling_days = modeling_days
        self.duration_time = duration_time * 60 * 60  # перевод часов в секунды
        self.modeling_step = modeling_step * 60  # перевод минут в секунды
        self.sec_gen_from = sec_gen_from
        self.sec_gen_to = sec_gen_to

        self.start_time = datetime(year=2024, month=4, day=17)
        self.current_time = self.start_time
        self.requests_list = []
        self.programs_list = []
        self.executed_requests = []
        self.song_library = SongLibrary()


    def generate_program_by_requests(self):
        # создание программы по заявкам
        prog_start_time = self.current_time
        prog_end_time = self.current_time + timedelta(seconds=self.duration_time)
        songs_list = []
        # артисты предыдущих песен для разнообразия, чтобы в программе, по возможности, артисты разные
        prev_artist = []
        artist_list = []
        for song in self.song_library.songs_list:
            if song.artist not in artist_list:
                artist_list.append(song.artist)
                
        current_list = [] # не исполненные заявки
        executed_songs = []
        current_artists = []
        for request in self.executed_requests:
            executed_songs.append(request.song)

        current_list = [request for request in self.requests_list if request.song not in executed_songs] 
        for request in current_list:
            if (request.time_add <= self.current_time + timedelta(seconds=request.song.playing_time) ):
                if (self.current_time + timedelta(seconds=request.song.playing_time) <= prog_end_time):
                    if (request.song.artist not in prev_artist) :
                        start_time = self.current_time
                        self.current_time = start_time + timedelta(seconds=request.song.playing_time)

                        current_artists = [artist for artist in artist_list if artist not in prev_artist]
                        if len(current_artists) == 2: 
                            prev_artist =  prev_artist [2:]
                        
                        prev_artist.append(request.song.artist) # учет артистов сыгранных песен
                        
                        songs_list.append((start_time, request.song))
                        executed_request = SongRequest( # исполненная заявка с временем исполнения
                            song=request.song,  
                            time_add=start_time
                        )
                        self.executed_requests.append(executed_request)
            else:
                break

        # создание программы по заявкам
        program_by_req = MusicProgram(
            songs_list=songs_list,
            start_time=prog_start_time,
            song_rating_dict={song: 0 for song in songs_list},
            genre=None,
            type_program=0  # программа по заявкам
        )

        return program_by_req

    def generate_hit_parade(self):
        # создание хит-парада определенного жанра
        prog_start_time = self.current_time
        prog_end_time = prog_start_time + timedelta(seconds=self.duration_time)

        # выбор случайного жанра и подготовка списка песен по рейтингу НА ТЕКУЩИЙ МОМЕНТ для этого жанра
        chosen_genre = random.choice(list(self.song_library.genres))
        ranked_songs = [song for song in self.song_library.songs_list if song.genre == chosen_genre]
        song_rating_dict = {song: random.randint(1,4) for song in ranked_songs} # изначально НЕ нулевой рейтинг для реалистичности

        for song in ranked_songs:
            for request in self.requests_list:
                if song == request.song and prog_start_time >= request.time_add:
                    song_rating_dict[song] += 1
        ranked_songs.sort(key=lambda song: song_rating_dict[song], reverse=True)

        parade_songs = []
        for song in ranked_songs:
            if self.current_time + timedelta(seconds=song.playing_time) >= prog_end_time:
                break
            parade_songs.append((self.current_time, song))
            self.current_time += timedelta(seconds=song.playing_time)

        # создание  хит-парада 
        hit_parade_program = MusicProgram(
            songs_list=parade_songs,
            start_time=prog_start_time,
            song_rating_dict=song_rating_dict,  # для хранения рейтинга на текущий момент
            genre=chosen_genre,
            type_program=1  # программа хит-парад
        )

        return hit_parade_program

    def modeling(self):
        # запуск для генерации программ радиостанции во всем времени моделирования по дням
        for day in range(1, self.modeling_days + 1):
            while len(self.programs_list) < self.programs_in_day * day:
                if len(self.programs_list) % 2 == 1:  # чередуем программы через одну, первая по заявкам
                    program = self.generate_hit_parade()
                else:
                    generate_static_requests(self, self.current_time, self.current_time + timedelta(seconds=self.duration_time),
                                                   self.sec_gen_from, self.sec_gen_to)
                    program = self.generate_program_by_requests()
                self.programs_list.append(program)
            self.current_time += timedelta(days=1)
            self.current_time = datetime(self.current_time.year, self.current_time.month, self.current_time.day)


class MusicProgram:
    """
    Класс для представления музыкальной программы радиостанции.
    
    Атрибуты:
        start_time (datetime): Время начала программы.
        songs_list (list): Список песен в программе.
        song_rating_dict (dict): Словарь с рейтингами песен на текущий момент (для хит-парадов).
        genre (str): Жанр программы (для хит-парада).
        type_program (int): Тип программы (1 - хит-парад, 0 - по заявкам).
    """
    def __init__(self, songs_list, start_time, song_rating_dict, genre, type_program):
        self.start_time = start_time
        self.songs_list = songs_list
        self.song_rating_dict = song_rating_dict
        self.genre = genre
        self.type_program = type_program 


