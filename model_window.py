import sys

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import  QWidget, QVBoxLayout, QLabel, QPushButton,  QScrollBar, QListWidgetItem, QListWidget, QDialog, QLineEdit, QHBoxLayout, QGroupBox, QFileDialog, QAbstractItemView
from PyQt6 import QtCore

from radio import *
from param_window import *
from final_report_window import *


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.widget_items = []

        self.setup_window()
        result, dialog_data = self.run_start_dialog()
        if result != QDialog.DialogCode.Accepted:
            self.close()
            sys.exit()
            
        self.init_radio_station(dialog_data)
        self.setup_layout()

        self.start_modeling()

        self.show()

    def setup_window(self):
        # основные параметры окна
        self.title = "Моделирование работы радиостанции"
        self.setWindowTitle(self.title)
        self.setGeometry(10, 60, 1200, 500)

    def run_start_dialog(self):
        # запуск окна ввода параметров моделирования
        dialog = FirstParams()
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            return result, dialog.get_data()
        else:
            return result, {}
        
    def init_radio_station(self, dialog_data):
        # установка параметров моделирвоания
        self.radio = RadioStation(
            programs_in_day=dialog_data.get("programs_in_day", 0),
            modeling_days=dialog_data.get("modeling_days", 0),
            duration_time=dialog_data.get("duration_time", 0),
            modeling_step=dialog_data.get("modeling_step", 0),
            sec_gen_from=dialog_data.get("sec_gen_from", 0),
            sec_gen_to=dialog_data.get("sec_gen_to", 0),
        )
        self.modeling_step = dialog_data.get('modeling_step', 0)

    def setup_layout(self):
        # макет основного окна
        main_layout = QHBoxLayout()
        self.program_widget = self.create_widget(500)  # Метод виджета программ
        self.request_widget = self.create_widget(200)  # Метод для создания виджета заявок
        self.executed_widget = self.create_widget(200)  # Метод для создания выполненных заявок
        # расположение макета кнопок и параметров
        buttons_layout = self.setup_buttons()

        # добавление виджетов в основной макет
        main_layout.addWidget(self.program_widget)
        main_layout.addWidget(self.request_widget)
        main_layout.addWidget(self.executed_widget)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

    def setup_buttons(self):
        # настройка кнопок управления
        buttons_layout = QVBoxLayout()
        self.step_buttons = []
        self.final_buttons = []
        
        params_group = QGroupBox("Заданные параметры моделирования")
        params_layout = QVBoxLayout(params_group)
        
        self.params_label = QLabel(f"Число программ в день: {self.radio.programs_in_day}\n"
                                    f"Количество дней моделирования: {self.radio.modeling_days}\n"
                                    f"Длительность программы в часах: {self.radio.duration_time//3600}\n"
                                    f"Промежуток генерации заявок в секундах: {self.radio.sec_gen_from} до {self.radio.sec_gen_to}\n")
        self.params_label.setStyleSheet("QLabel { color: black; }")
        params_layout.addWidget(self.params_label)

        input_layout = QHBoxLayout()
        label = QLabel("Изменить шаг моделирования:")
        input_layout.addWidget(label)
        
        modeling_step_edit = QLineEdit(str(self.modeling_step), self)
        modeling_step_edit.textChanged.connect(self.change_modeling_step)
        input_layout.addWidget(modeling_step_edit)
        params_layout.addLayout(input_layout)

        buttons_layout.addWidget(params_group)

        buttons_group = QGroupBox("Управление моделированием")
        control_layout = QVBoxLayout(buttons_group)

        step_button = QPushButton('Сделать шаг моделирования')
        step_button.clicked.connect(self.step_model)
        control_layout.addWidget(step_button)
        self.step_buttons.append(step_button)
        step_button.setFixedSize(300, 35)
        
        full_step_button = QPushButton("Промоделировать полностью")
        full_step_button.clicked.connect(self.all_model)
        control_layout.addWidget(full_step_button)
        self.step_buttons.append(full_step_button)
        full_step_button.setFixedSize(300, 35)
        
        report_button = QPushButton('Показать финальный отчёт')
        report_button.clicked.connect(self.show_final_report)
        control_layout.addWidget(report_button)
        self.final_buttons.append(report_button)
        report_button.setFixedSize(300, 35)
        for btn in self.final_buttons:
                btn.setEnabled(False)
        
        begin_button = QPushButton('Начать моделирование сначала')
        begin_button.clicked.connect(self.begin_click)
        begin_button.setFixedSize(300, 35)
        control_layout.addWidget(begin_button)
        
        exit_button = QPushButton('Закрыть программу')
        exit_button.clicked.connect(self.exit_click)
        exit_button.setFixedSize(300, 35)
        control_layout.addWidget(exit_button)
        
        save_button = QPushButton('Сохранить моделирование')
        save_button.clicked.connect(self.save_program)
        control_layout.addWidget(save_button)
        save_button.setFixedSize(300, 35)
        self.final_buttons.append(save_button)
        for btn in self.final_buttons:
                btn.setEnabled(False)

        # стиль кнопочек
        button_style = "QPushButton { background-color: #add8e6; color: black; margin: 5px; }" \
                    "QPushButton:disabled { background-color: #e0e0e0; color: #a0a0a0; }"
        step_button.setStyleSheet(button_style)
        full_step_button.setStyleSheet(button_style)
        report_button.setStyleSheet(button_style)
        begin_button.setStyleSheet(button_style)
        exit_button.setStyleSheet(button_style)
        save_button.setStyleSheet(button_style)
        
        buttons_layout.addWidget(buttons_group)

        return buttons_layout
    def start_modeling(self):
        # запуск работы рдиостанции
        self.radio.modeling()
        self.current_time = self.radio.start_time
        self.end_time = self.current_time + timedelta(days=self.radio.modeling_days)
        self.generate_program_widget_items()
        
    def generate_program_widget_items(self):
        # генерация виджета программ
        self.program_widget.clear()
        program_date = None
        for song_program in self.radio.programs_list:
            first_song_time = song_program.songs_list[0][0]
            if not program_date or first_song_time.date() != program_date:
                program_date = first_song_time.date()
                self.add_date_item(program_date)

            self.add_program_item(song_program)

            for i, song_record in enumerate(song_program.songs_list):
                self.add_song_item(song_record, song_program)

    def add_date_item(self, program_date):
        # добавление нового дня
        item = QListWidgetItem(program_date.strftime("%d/%m/%Y"))
        item.setBackground(QColor('#ADD8E6' ))
        item.start_time = datetime(year=program_date.year, month=program_date.month, day=program_date.day)
        self.widget_items.append(item)

    def add_program_item(self, song_program):
        # элемент наименования программы
        if song_program.type_program == 1:
            item_text = f"Хит-парад по жанру {song_program.genre}"
        else:
            item_text = "Программа по заявкам"
        color = '#A9D08E'
        item = QListWidgetItem(item_text)
        item.setBackground(QColor(color))
        item.start_time = song_program.start_time
        self.widget_items.append(item)

    def add_song_item(self, song_record, song_program):
        # элемент песни внутри программы
        t_start, song = song_record
        t_end = t_start + timedelta(seconds=song.playing_time)
        item_text = self.format_song_text(t_start, t_end, song, song_program)
        item = QListWidgetItem(item_text)
        item.song = song
        item.start_time = t_start
        self.widget_items.append(item)

    def format_song_text(self, t_start, t_end, song, song_program):
        # форматирование времени и названия песни
        if song_program.type_program == 1:
            return f"{t_start.strftime('%X')} - {t_end.strftime('%X')}  ---- {song.song_title} by {song.author} rating: {song_program.song_rating_dict[song]}"
        else:
            return f"{t_start.strftime('%X')} - {t_end.strftime('%X')}  ---- {song.song_title} by {song.author}"

    def create_widget(self, width):
        # создание виджета на главном экране моделирования
        widget = QListWidget(self)
        scroll_bar = QScrollBar(self)
        widget.setVerticalScrollBar(scroll_bar)
        widget.setFixedWidth(width)

        return widget

    def get_widgets(self, time_from, time_to):
        # удовлетворение временному интервала
        return [widget for widget in self.widget_items if time_from <= widget.start_time < time_to]

    def step_model(self):
        # метод выполнения одного шага моделирования
        time_from = self.current_time
        time_to = min(self.current_time + timedelta(minutes=self.modeling_step), self.end_time)
        widgets = self.get_widgets(time_from, time_to)
        self.update_executed_widget(time_to) 
        self.update_request_widget(time_to) 

        for w in widgets:
            self.program_widget.addItem(w)
            self.program_widget.scrollToItem(w, QAbstractItemView.ScrollHint.EnsureVisible)

        self.current_time = time_to
        if self.current_time >= self.end_time:
            for btn in self.step_buttons:
                btn.setEnabled(False)
            for btn in self.final_buttons:
                btn.setEnabled(True)
            item = QListWidgetItem(f"Моделирование закончено. Всего программ: {len(self.radio.programs_list)}")
            item.setBackground(QColor('#add8e6'))
            self.program_widget.addItem(item) 
            self.program_widget.scrollToItem(item, QAbstractItemView.ScrollHint.EnsureVisible)

    def all_model(self):
        # метод выполнения полное моделирование
        time_from = self.current_time
        time_to = self.end_time
        widgets = self.get_widgets(time_from, time_to)
        self.update_executed_widget(time_to)
        self.update_request_widget(time_to) 
        self.current_time = time_to

        for w in widgets:
            self.program_widget.addItem(w)
            self.program_widget.scrollToItem(w, QAbstractItemView.ScrollHint.EnsureVisible)

        if self.current_time >= self.end_time:
            for btn in self.step_buttons:
                btn.setEnabled(False)
            for btn in self.final_buttons:
                btn.setEnabled(True)
            item = QListWidgetItem(f"Моделирование закончено. Всего программ: {len(self.radio.programs_list)}")
            item.setBackground(QColor('#add8e6'))
            self.program_widget.addItem(item) 
        self.program_widget.addItem(item)
        self.program_widget.scrollToItem(item, QAbstractItemView.ScrollHint.EnsureVisible)
        
    def update_executed_widget(self, time_to):
        # виджет выполненных заявок
        self.executed_widget.clear() 
        item = QListWidgetItem(f"Выполненные \n к текущему шагу \n заявки")
        item.setBackground(QColor('#add8e6'))
        self.executed_widget.addItem(item) 

        for request in self.radio.executed_requests:
            if request.time_add <= time_to:
                self.executed_widget.addItem(f" {request.song.song_title} by {request.song.artist}    Время: {request.time_add}")
                
    def update_request_widget(self, time_to):
        # виджет всех заявок
        self.request_widget.clear() 
        item = QListWidgetItem(f"Полученные \n к текущему шагу \n заявки")
        item.setBackground(QColor('#add8e6'))
        self.request_widget.addItem(item) 

        for request in self.radio.requests_list:
            if request.time_add <= time_to:
                self.request_widget.addItem(f" {request.song.song_title} by {request.song.artist}    Время: {request.time_add}")

    def show_final_report(self):
        # метод для показа всплывающего окна с финальным отчётом
        text = ""
        sorted_songs_list = sorted(self.radio.song_library.songs_list, key=lambda song: song.rating, reverse=True)

        for i, song in enumerate(sorted_songs_list):
            text += f"{i+1}. {song.song_title} by {song.artist} Rating: {song.rating}\n\n"
        all_requests = len(self.radio.requests_list) + len(self.radio.executed_requests )
        ex_requests = len(self.radio.executed_requests )
        dialog = FinalReportDialog(text, all_requests, ex_requests, self)

        dialog.exec()
        
    def begin_click(self):
        # начать сначала
        QtCore.QCoreApplication.quit()
        QtCore.QProcess.startDetached(sys.executable, sys.argv)
    
    def change_modeling_step(self, text):
        # измнеить шаг моделирования
        if text.isdigit():
            self.modeling_step = int(text)
        
    def exit_click(self):
        # закрыть программц
        self.close()
    
    def save_program(self):
        # программа в файл
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить программу", "", "Текстовые файлы (*.txt)")
        if filename:
            self.save_program_widget_text(filename)
            
    def save_program_widget_text(self, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            for index in range(self.program_widget.count()):
                item = self.program_widget.item(index)
                text = item.text()
                file.write(text + '\n')
                
