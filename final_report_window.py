from PyQt6.QtWidgets import  QWidget, QVBoxLayout, QLabel, QDialog, QDialogButtonBox, QScrollArea


class FinalReportDialog(QDialog):
    def __init__(self, text, all_requests, ex_requests, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Финальный отчёт")
        self.setStyleSheet("background-color: '#F5F5F5'")
        self.resize(500, 400)

        layout = QVBoxLayout(self)
        
        label = QLabel("Рейтинг каждой из песен по окончании моделирования:")
        layout.addWidget(label)
        # прокрутка списка песен
        scroll_area = QScrollArea(self)  
        scroll_area.setWidgetResizable(True) 

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)  

        label = QLabel(text, content_widget)
        label.setWordWrap(True)
        content_layout.addWidget(label)

        scroll_area.setWidget(content_widget)

        layout.addWidget(scroll_area)

        label = QLabel(f"Всего заявок: {all_requests}")
        layout.addWidget(label)
        
        label = QLabel(f"Выполнено заявок: {ex_requests}")
        layout.addWidget(label)
        # кнопка закрытия отчета
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, self)
        ok_button = buttonBox.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Закрыть отчет")
        ok_button.setStyleSheet("background-color: #add8e6;")
        buttonBox.accepted.connect(self.accept)

        layout.addWidget(buttonBox)

        self.setLayout(layout)