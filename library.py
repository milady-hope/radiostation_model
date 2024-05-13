import csv
from collections import defaultdict

class SongLibrary:
    """
    Класс для управления библиотекой песен.
    
    Атрибуты:
        songs_list (list): Список всех песен в библиотеке.
        genres (set): Множество всех жанров, представленных в библиотеке.
    
    Загружает песни из файла CSV и фильтрует их по популярности жанров.
    """
    def __init__(self):
        songs_list = []
        genres = set()
        genre_counter = defaultdict(int)

        with open('songs.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                song_obj = Song(
                    genre=row['genre'],
                    song_title=row['song_title'],
                    author=row['author'],
                    artist=row['artist'],
                    album=row['album'],
                    release_year=int(row['release_year']),
                    playing_time=int(row['playing_time'])
                )
                songs_list.append(song_obj)
                genres.add(row['genre'])
                genre_counter[row['genre']] += 1

        top_genres = set(genre for genre, count in genre_counter.items() if count >= 20) # избегаем жанров с малым числом песен
        self.songs_list = [song for song in songs_list if song.genre in top_genres]
        self.genres = genres


class Song:
    """
    Класс для представления песни.
    
    Атрибуты:
        genre (str): Жанр песни.
        song_title (str): Название песни.
        author (str): Автор песни.
        artist (str): Исполнитель песни.
        album (str): Альбом, в который входит песня.
        release_year (int): Год выпуска песни.
        playing_time (int): Длительность песни в секундах.
        rating (int): Рейтинг песни на основе всех поступивших заявок.
    """
    def __init__(self, genre, song_title, author, artist, album, release_year, playing_time):
        self.genre = genre
        self.song_title = song_title
        self.author = author
        self.artist = artist
        self.album = album
        self.release_year = release_year
        self.playing_time = playing_time
        self.rating = 0
