from PyQt6.QtWidgets import QFormLayout, QDialog, QDialogButtonBox, QLineEdit

class FirstParams(QDialog):
    # класс для получения параметров моделирования от пользователя
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Параметры моделирования радиостанции")

        self.programs_in_day = QLineEdit(self)
        self.programs_in_day.setText("5")
        self.modeling_days = QLineEdit(self)
        self.modeling_days.setText("1")
        self.duration_time = QLineEdit(self)
        self.duration_time.setText("1")
        self.modeling_step = QLineEdit(self)
        self.modeling_step.setText("10")
        self.sec_gen_text= QLineEdit(self)
        self.sec_gen_text.setText("От 5 до 45")

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        ok_button = buttonBox.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Ок")
        cancel_button = buttonBox.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setText("Отмена")
        
        layout = QFormLayout(self)
        layout.addRow("Число программ в день (5 - 8)", self.programs_in_day)
        layout.addRow("Количество дней моделирования (1 - 7)", self.modeling_days)
        layout.addRow("Длительность программы в часах (1 - 3)", self.duration_time)
        layout.addRow("Шаг моделирования в минутах (10 - 30)", self.modeling_step)
        layout.addRow("Промежуток генерации заявок в секундах", self.sec_gen_text)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)  # подтвердить ввод данных
        buttonBox.rejected.connect(self.reject)  # отменить ввод и закрыть окно
        
    def get_data(self):  # данные в нужный формат
        sec_gen_text = self.sec_gen_text.text()

        parts = sec_gen_text.split()

        sec_gen_from = int(parts[1])  
        sec_gen_to = int(parts[3]) 
        return {
            'programs_in_day': int(self.programs_in_day.text()),
            'modeling_days': int(self.modeling_days.text()),
            'duration_time': int(self.duration_time.text()),
            'modeling_step': int(self.modeling_step.text()),
            'sec_gen_from': int(sec_gen_from),
            'sec_gen_to': int(sec_gen_to),
        }