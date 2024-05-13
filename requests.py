import random

from datetime import timedelta

def generate_static_requests(radio, time_from, time_to, sec_gen_from, sec_gen_to):
        # создание статичного потока заявок 
        while True:
            sec_gen = random.randint(sec_gen_from, sec_gen_to)
            time_add = time_from + timedelta(seconds=sec_gen)

            if time_add < time_to:
                song_request = SongRequest(
                    song=random.choice(radio.song_library.songs_list),  # случайная песня
                    time_add=time_add
                )
                radio.requests_list.append(song_request) # сохранение в список песен
                time_from = time_add
            else:
                break

class SongRequest:
    """
    Класс для представления заявки на песню.
    
    Атрибуты:
        time_add (datetime): Время добавления/исполнения заявки.
        song (Song): Песня, на которую сделана заявка.
    """
    def __init__(self, song, time_add):
        self.time_add = time_add
        self.song = song
        self.song.rating += 1