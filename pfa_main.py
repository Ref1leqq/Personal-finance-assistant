import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import sqlite3
from datetime import datetime, timedelta
import threading
import re
import pandas as pd
import matplotlib.pyplot as plt 
import time   




class FinanceAssistantApp(tk.Tk): #Эта строка объявляет класс FinanceAssistantApp, который наследуется от класса tk.Tk. Класс Tk является основным окном приложения в библиотеке Tkinter.
    def __init__(self, user): #Определение конструктора класса __init__, который вызывается при создании экземпляра класса. Конструктор принимает параметр user.
        super().__init__() #Этот вызов инициализирует родительский класс Tk, что необходимо для корректной работы окна Tkinter.
        self.title("Финансовый помощник")
        self.geometry("800x600")
        self.user = user #Сохраняет переданный объект пользователя (user) как атрибут объекта класса. Это может быть полезно для хранения информации о пользователе внутри приложения.
        icon = PhotoImage(file="logo.png")
        self.iconphoto(False, icon) #Устанавливает иконку окна приложения. Первый аргумент False указывает, что иконка будет использоваться только для главного окна (не для дочерних окон). Второй аргумент – это само изображение.

        # Создание интерфейса
        self.create_main_interface()



    def create_main_interface(self):
        # Верхний фрейм с приветствием и значком пользователя
        top_frame = tk.Frame(self, bg="lightblue") #Здесь создается новый экземпляр класса Frame (фрейма) с именем top_frame. Фрейм используется для группировки виджетов. Аргумент bg="lightblue" устанавливает синий цвет фона для этого фрейма.
        top_frame.pack(fill=tk.X) #Метод pack() размещает фрейм в окне приложения. Параметр fill=tk.X означает, что фрейм будет растягиваться по горизонтали, заполняя все доступное пространство по оси X.

        user_icon = tk.Label(top_frame, text="👤", font=("Arial", 24), bg="lightblue") #Создается метка (виджет Label), которая отображает символ пользователя (👤). Метка помещается внутрь верхнего фрейма top_frame. Также устанавливаются шрифт (font=("Arial", 24) — Arial размером 24 пункта) и фон (bg="lightblue").
        user_icon.pack(side=tk.LEFT, padx=15) #Метка с символом пользователя размещается внутри фрейма с выравниванием слева (side=tk.LEFT) и отступом по горизонтали в 15 пикселей (padx=15).

        user_label = tk.Label(top_frame, text=f"Добро пожаловать, {self.user[1]}!", font=("Arial", 16), bg="lightblue") #Еще одна метка создается для приветствия пользователя. Текст метки включает имя пользователя, которое берется из атрибута self.user[1] (предположительно это список, где индекс [1] содержит имя пользователя). Шрифт установлен как Arial размером 16 пунктов, а фон совпадает с цветом фрейма.
        user_label.pack(side=tk.LEFT) #Метка с текстом приветствия также размещается внутри фрейма с выравниванием слева.


        # Основной интерфейс с вкладками
        notebook = ttk.Notebook(self) #Создается экземпляр класса Notebook из модуля ttk, который представляет собой контейнер для вкладок. Он добавляется к основному окну приложения.
        notebook.pack(fill=tk.BOTH, expand=True) #Контейнер с вкладками размещается таким образом, чтобы он занимал всё доступное пространство по обеим осям (горизонтальной и вертикальной) благодаря параметрам fill=tk.BOTH и expand=True.

        # Вкладки
        self.home_page = tk.Frame(notebook) #Для каждой вкладки создаются отдельные фреймы, которые будут содержать контент этих вкладок. Эти фреймы добавляются к контейнеру notebook.
        self.diagrams_page = tk.Frame(notebook)
        self.transactions_page = tk.Frame(notebook)
        self.goals_page = tk.Frame(notebook)
        self.reminders_page = tk.Frame(notebook)

        notebook.add(self.home_page, text="Главная") #Каждая вкладка добавляется в контейнер notebook с соответствующим текстовым названием. Например, первая вкладка называется "Главная", вторая — "Диаграммы" и так далее.
        notebook.add(self.diagrams_page, text="Диаграммы")
        notebook.add(self.transactions_page, text="Транзакции")
        notebook.add(self.goals_page, text="Цели")
        notebook.add(self.reminders_page, text="Напоминания")

        # Настройка вкладок
        self.setup_home_page()
        self.setup_diagrams_page()
        self.setup_transactions_page()
        self.setup_goals_page()
        self.setup_reminders_page()

#        self.check_reminders()

    def setup_home_page(self):
        tk.Label(self.home_page, text="Общая информация", font=("Arial", 16)).pack(pady=10) #Создание метки (Label) с текстом "Общая информация". Метка размещается на главной странице (self.home_page) с использованием шрифта Arial размером 16 пунктов. Метод .pack(pady=10) размещает метку с отступами сверху и снизу по 10 пикселей.

        self.balance_label = tk.Label(self.home_page, text="Текущий баланс: 0.00 RUB", font=("Arial", 14)) #Создание метки для отображения текущего баланса. Изначально значение баланса установлено как "0.00 RUB". Метка имеет шрифт Arial размером 14 пунктов и размещается с отступами сверху и снизу по 10 пикселей.
        self.balance_label.pack(pady=10)

        self.earnings_label = tk.Label(self.home_page, text="Заработано: 0.00 RUB", font=("Arial", 12)) #Аналогично предыдущему шагу, создается метка для отображения заработанных средств. Значение по умолчанию "0.00 RUB". Размер шрифта здесь уменьшен до 12 пунктов, а отступы составляют 5 пикселей.
        self.earnings_label.pack(pady=5)

        self.expenses_label = tk.Label(self.home_page, text="Потрачено: 0.00 RUB", font=("Arial", 12))
        self.expenses_label.pack(pady=5)

        tk.Button(self.home_page, text="Добавить транзакцию", command=self.add_transaction_window).pack(pady=10) #Создается кнопка с надписью "Добавить транзакцию". При нажатии на эту кнопку вызывается метод add_transaction_window, который, предположительно, открывает окно для добавления новой транзакции. Кнопка размещается с отступами по 10 пикселей.

        self.update_balance()

    def update_balance(self):
        conn = sqlite3.connect('users.db') #Открывается соединение с базой данных SQLite под названием users.db.
        cursor = conn.cursor() #Создаётся курсор для выполнения SQL-запросов.
        cursor.execute('''
            SELECT SUM(CASE WHEN type = "Доход" THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN type = "Расход" THEN amount ELSE 0 END) as total_expense
            FROM transactions
            WHERE user_id = ?
        ''', (self.user[0],)) #Выполняется SQL-запрос, который выбирает сумму всех доходов и расходов пользователя из таблицы transactions. Для каждого типа транзакций ("Доход" или "Расход") вычисляется сумма значений поля amount. Запрос фильтруется по полю user_id, используя идентификатор пользователя, хранящийся в self.user[0].
        result = cursor.fetchone() #Извлекаются результаты запроса. Метод fetchone() возвращает одну строку результата (или None, если результатов нет).
        conn.close() #Закрывается соединение с базой данных.

        total_income = result[0] if result[0] is not None else 0.0 #Проверяется наличие значений в результате запроса. Если результат не равен None, то берутся соответствующие суммы дохода и расхода; иначе присваиваются нулевые значения.
        total_expense = result[1] if result[1] is not None else 0.0
        current_balance = total_income - total_expense

        self.balance_label.config(text=f"Текущий баланс: {current_balance:.2f} RUB") #Обновляются тексты меток (balance_label, earnings_label, expenses_label) с новыми значениями баланса, общего дохода и общих расходов соответственно. Форматирование чисел производится с двумя знаками после запятой (:.2f).
                                                                                        #Этот метод выполняет запрос к базе данных для получения сумм доходов и расходов, затем рассчитывает баланс и обновляет соответствующие метки на главной странице приложения.
        self.earnings_label.config(text=f"Заработано: {total_income:.2f} RUB")
        self.expenses_label.config(text=f"Потрачено: {total_expense:.2f} RUB")

    def setup_diagrams_page(self):
        tk.Label(self.diagrams_page, text="Диаграммы расходов и доходов", font=("Arial", 16)).pack(pady=10)

        # Кнопка для открытия нового окна
        tk.Button(
            self.diagrams_page,
            text="Создать диаграммы",
            command=self.open_diagrams_window
        ).pack(pady=10)

    def open_diagrams_window(self):
        diagrams_window = tk.Toplevel(self) #Создание нового окна типа Toplevel, которое будет дочерним окном основного окна приложения.
        diagrams_window.title("Настройка диаграмм")
        diagrams_window.geometry("400x400")

        # Выбор типа данных
        tk.Label(diagrams_window, text="Тип данных:").pack(pady=5)
        data_type = tk.StringVar(value="Все") #Создание переменной типа StringVar для хранения выбранного типа данных. По умолчанию устанавливается значение "Все".
        ttk.Combobox( #Создание выпадающего списка (Combobox) с тремя вариантами выбора: "Все", "Только доходы", "Только расходы". Выбранное значение сохраняется в переменную data_type. Список размещен с отступами по 5 пикселей.
            diagrams_window,
            textvariable=data_type,
            values=["Все", "Только доходы", "Только расходы"]
        ).pack(pady=5)

        # Выбор типа диаграммы
        tk.Label(diagrams_window, text="Тип визуализации:").pack(pady=5)
        chart_type = tk.StringVar(value="Круговая диаграмма") #Создание переменной типа StringVar для хранения выбранного типа диаграммы. По умолчанию устанавливается значение "Круговая диаграмма".
        ttk.Combobox( #Создание выпадающего списка (Combobox) с тремя типами диаграмм: "Круговая диаграмма", "Гистограмма", "Гистограмма(Цвета)". Выбранное значение сохраняется в переменную chart_type. Список размещен с отступами по 5 пикселей.
            diagrams_window,
            textvariable=chart_type,
            values=["Круговая диаграмма", "Гистограмма", "Гистограмма(Цвета)"]
        ).pack(pady=5)

        # Кнопка для генерации диаграммы
        tk.Button( #Создание кнопки с текстом "Построить диаграмму". При нажатии на нее вызывается метод generate_chart с передачей выбранных типов данных и диаграммы. Кнопка размещена с отступами по 10 пикселей.
            diagrams_window,
            text="Построить диаграмму",
            command=lambda: self.generate_chart(data_type.get(), chart_type.get())
        ).pack(pady=10)

    def generate_chart(self, data_type, chart_type):
        # Получение данных из базы
        conn = sqlite3.connect('users.db') #Открытие соединения с базой данных SQLite под названием users.db.
        cursor = conn.cursor() #Создание курсора для выполнения SQL-запросов.
        query = "SELECT category, amount, type FROM transactions WHERE user_id = ?"
        cursor.execute(query, (self.user[0],)) #Формирование и выполнение SQL-запроса для выборки категорий, сумм и типов транзакций для конкретного пользователя (идентификатор которого хранится в self.user[0]).
        data = cursor.fetchall() #Получение всех записей, возвращаемых запросом, и сохранение их в переменной data.
        conn.close()

        # Преобразование в DataFrame
        df = pd.DataFrame(data, columns=["Category", "Amount", "Type"]) #Преобразование полученных данных в pandas DataFrame с колонками "Category", "Amount" и "Type".

        # Фильтрация данных
        if data_type == "Только доходы": #Фильтрация данных в зависимости от выбранного типа данных. Если выбраны только доходы, остаются записи с типом "Доход"; если только расходы — с типом "Расход".
            df = df[df["Type"] == "Доход"]
        elif data_type == "Только расходы":
            df = df[df["Type"] == "Расход"]

        # Построение диаграммы
        if chart_type == "Круговая диаграмма": #Выбор типа диаграммы для построения. В зависимости от того, какой тип диаграммы был выбран, вызываются соответствующие методы для построения круговой диаграммы, гистограммы или цветной гистограммы.
            self.plot_pie_chart(df)
        elif chart_type == "Гистограмма":
            self.plot_bar_chart(df)
        elif chart_type == "Гистограмма(Цвета)":
            self.plot_gisto_chart(df)

    def plot_pie_chart(self, df): #Определение функции plot_pie_chart, которая принимает объект DataFrame (таблицу данных) в качестве параметра.
        plt.figure(figsize=(8, 8)) #Создание фигуры (графика) с размерами 8x8 дюймов.
        df.groupby("Category")["Amount"].sum().plot.pie(autopct='%1.1f%%', startangle=90) #Группация данных по столбцу "Category" и суммирование значений в столбце "Amount". Затем строится круговая диаграмма с указанием процента для каждого сектора (autopct='%1.1f%%') и начального угла в 90 градусов (startangle=90).
        plt.title("Круговая диаграмма") #Задание названия графика.
        plt.ylabel("") #Удаление подписи у оси Y (установка пустой строки).
        plt.show() #Отображение построенного графика.

    def plot_bar_chart(self, df): #Определение функции plot_bar_chart, которая также принимает DataFrame в качестве параметра.
        plt.figure(figsize=(10, 6)) #Создание фигуры с размерами 10x6 дюймов.
        df.groupby("Category")["Amount"].sum().plot(kind="bar") #Группация данных по столбцу "Category" и суммирование значений в столбце "Amount". Затем строится гистограмма.
        plt.title("Гистограмма") #Задание названия графика.
        plt.xlabel("Категория") #Подпись оси X.
        plt.ylabel("Сумма") #Подпись оси Y.
        plt.show()

    def plot_gisto_chart(self, df): #Определение функции plot_gisto_chart, принимающей DataFrame.
        plt.figure(figsize=(8, 8)) #Создание фигуры с размерами 8x8 дюймов.

        grouped = df.groupby("Category")["Amount"].sum() #Группация данных по столбцу "Category" и суммирование значений в столбце "Amount".
        colors = ["red", "green", "blue", "purple", "orange"] #Список цветов для окрашивания столбцов гистограммы.
        grouped.plot(kind="bar", color=colors[:len(grouped)]) #Построение гистограммы с использованием первых len(grouped) цветов из списка colors.

        plt.title("Гистограмма(Цвета)") #Задание названия графика.
        plt.xlabel("Категория") #Подпись оси X.
        plt.ylabel("Сумма") #Подпись оси Y.
        plt.show() #Отображение построенного графика.

    def setup_transactions_page(self): #Эта строка объявляет метод setup_transactions_page внутри класса. Метод предназначен для настройки страницы истории транзакций.
        tk.Label(self.transactions_page, text="История транзакций", font=("Arial", 16)).pack(pady=10) #Здесь создается метка (Label) с текстом "История транзакций". Она размещается на странице транзакций (self.transactions_page), используется шрифт Arial размером 16 пикселей. Метку упаковывают с отступами сверху и снизу по 10 пикселей.
        self.transactions_tree = ttk.Treeview(self.transactions_page, columns=("category", "amount","type", "date"), show="headings") #Создается объект TreeView, который будет отображать таблицу с историей транзакций. У таблицы есть четыре столбца: категория, сумма, тип и дата. Параметр show="headings" указывает, что нужно показывать только заголовки столбцов без первого пустого столбца, который обычно присутствует в TreeView.
        self.transactions_tree.heading("category", text="Категория") #Эти строки настраивают заголовки каждого столбца таблицы. Заголовок передается через параметр text.
        self.transactions_tree.heading("amount", text="Сумма")
        self.transactions_tree.heading("type", text="Тип")
        self.transactions_tree.heading("date", text="Дата")
        self.transactions_tree.pack(fill=tk.BOTH, expand=True) #Таблица упаковывается так, чтобы она занимала все доступное пространство по горизонтали и вертикали на странице.
        self.update_transactions_list()

    def update_transactions_list(self): #Объявляется метод update_transactions_list, который отвечает за обновление списка транзакций.
        conn = sqlite3.connect('users.db') 
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, amount, type, date FROM transactions WHERE user_id = ?
        """, (self.user[0],)) #Выполняется запрос к базе данных, выбирающий категорию, сумму, тип и дату всех транзакций текущего пользователя (идентификатор которого хранится в self.user[0]).
        transactions = cursor.fetchall() #Все результаты запроса сохраняются в переменной transactions. После этого соединение с базой данных закрывается.
        conn.close()

        for row in self.transactions_tree.get_children(): #Очищаются все существующие записи в таблице TreeView перед добавлением новых данных.
            self.transactions_tree.delete(row)

        for transaction in transactions: #ля каждой транзакции из результата запроса добавляется новая запись в таблицу TreeView. Значения для новой строки берутся прямо из кортежа transaction.
            self.transactions_tree.insert("", tk.END, values=transaction)

    def add_transaction_window(self): #Это объявление метода add_transaction_window внутри класса. Этот метод отвечает за создание окна для добавления новой транзакции
        add_window = tk.Toplevel(self) #Создание нового окна верхнего уровня (Toplevel), которое будет дочерним окном основного окна приложения.
        add_window.title("Добавить транзакцию")
        add_window.geometry("300x400")  # Увеличиваем высоту окна для радиокнопок

        tk.Label(add_window, text="Тип транзакции:").pack(pady=5)

        transaction_type = tk.StringVar(value="Расход")  # Значение по умолчанию - "Расход"

        # Радиокнопки для выбора типа транзакции
        def update_categories(): #Определение функции update_categories, которая изменяет доступные варианты категорий в зависимости от выбранного типа транзакции ("Доход" или "Расход").
            if transaction_type.get() == "Доход":
                combobox["values"] = ["Зарплата", "Переводы", "Инвестиции"]  # Убираем значения для выбора
            else:
                combobox["values"] = ["Продукты", "Одежда", "Такси"]  # Категории для расхода

        income_radiobutton = tk.Radiobutton(add_window, text="Доход", variable=transaction_type, value="Доход", 
                                            command=update_categories)#Создание радиокнопки для выбора типа транзакции "Доход". При изменении состояния этой кнопки вызывается функция update_categories.
        income_radiobutton.pack()
        expense_radiobutton = tk.Radiobutton(add_window, text="Расход", variable=transaction_type, value="Расход",
                                             command=update_categories) #Создание радиокнопки для выбора типа транзакции "Расход". Аналогично кнопке "Доход", при изменении состояния вызывается функция update_categories.
        expense_radiobutton.pack()

        tk.Label(add_window, text="Категория:").pack(pady=5)

        # Поле выбора или ввода категории
        combobox = ttk.Combobox(add_window, state="readonly") #Создание выпадающего списка (комбобокс) для выбора категории. Список доступен только для чтения, то есть пользователь может выбирать только из предложенных вариантов.
        combobox.pack(padx=6, pady=6)

        #category_entry = tk.Entry(add_window, state=tk.DISABLED)  # Поле для пользовательского ввода категории дохода
        #category_entry.pack(padx=6, pady=6)

        tk.Label(add_window, text="Сумма:").pack(pady=5) #Создание метки с текстом "Сумма:" и текстового поля для ввода суммы транзакции.
        amount_entry = tk.Entry(add_window)
        amount_entry.pack(pady=5)

        def save_transaction(): #Функция save_transaction извлекает введенную пользователем информацию: категорию, сумму и тип транзакции.
            category = combobox.get() #if transaction_type.get() == "Доход" else combobox.get()
            amount = amount_entry.get()
            transaction_type_value = transaction_type.get()

            if not amount: #Проверяется, введена ли сумма. Если нет, выводится сообщение об ошибке, и выполнение функции прерывается.
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return

            try: #Пытаемся преобразовать введенное значение суммы в число с плавающей точкой. Если это невозможно, выводится ошибка.
                amount = float(amount)
            except ValueError:
                messagebox.showerror("Ошибка", "Сумма должна быть числом!")
                return

            conn = sqlite3.connect('users.db') #Открывается соединение с базой данных, выполняется вставка новой транзакции в таблицу transactions, после чего соединение закрывается.
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (user_id, category, amount, date, type) VALUES (?, ?, ?, ?, ?)
            """, (self.user[0], category, amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), transaction_type_value))
            conn.commit()
            conn.close()

            if transaction_type_value == "Доход": #Если транзакция является доходом, вызывается метод update_goal_progress для обновления прогресса достижения финансовой цели.
                self.update_goal_progress(amount)

            messagebox.showinfo("Успех", "Транзакция добавлена!") #Выводится сообщение об успешном добавлении транзакции, окно добавления транзакции закрывается, а затем обновляются списки транзакций и баланс.
            add_window.destroy()
            self.update_transactions_list()
            self.update_balance()

        tk.Button(add_window, text="Сохранить", command=save_transaction).pack(pady=10) #Создание кнопки "Сохранить", которая вызывает функцию save_transaction при нажатии.

    def setup_goals_page(self): #Объявление метода setup_goals_page внутри класса. Этот метод отвечает за настройку страницы финансовых целей.
        tk.Label(self.goals_page, text="Финансовые цели", font=("Arial", 16)).pack(pady=10)

        # Создаем таблицу для отображения целей
        #Создание таблицы для отображения финансовых целей с четырьмя столбцами: название, целевая сумма, текущая сумма и оставшееся время. Таблица занимает всё доступное пространство по ширине и высоте с отступами сверху и снизу по 10 пикселей.
        self.goals_tree = ttk.Treeview(self.goals_page, columns=("title", "target_amount", "current_amount", "remaining"), show="headings")
        self.goals_tree.heading("title", text="Название")
        self.goals_tree.heading("target_amount", text="Цель (₽)")
        self.goals_tree.heading("current_amount", text="Текущая сумма (₽)")
        self.goals_tree.heading("remaining", text="Осталось времени")
        self.goals_tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # Кнопки для добавления и пополнения цели
        tk.Button(self.goals_page, text="Добавить цель", command=self.add_goal_window).pack(pady=10)
        #tk.Button(self.goals_page, text="Пополнить цель", command=self.top_up_goal).pack(pady=10)
        tk.Button(self.goals_page, text="Удалить цель", command=self.delete_completed_goal).pack(pady=10)

        # Обновляем список целей
        self.update_goals_list()  # Вставляем вызов метода для обновления списка целей

    def top_up_goal(self): #Эта строка объявляет метод top_up_goal внутри класса. Данный метод отвечает за пополнение финансовой цели.
        selected_item = self.goals_tree.selection() #Получение выделенного элемента в дереве целей (goals_tree). Метод selection() возвращает идентификаторы выбранных строк.
        if not selected_item: #Проверяем, выбрана ли какая-то цель. Если ничего не выбрано, показываем предупреждение и прекращаем выполнение метода.
            messagebox.showwarning("Ошибка", "Выберите цель для пополнения.")
            return

        item_values = self.goals_tree.item(selected_item)['values'] #Извлекаем значения полей для выбранной строки дерева целей. Метод item() возвращает словарь с информацией о строке, где ключ 'values' содержит список значений колонок.
        goal_id = item_values[0]  # Получаем ID выбранной цели
        current_amount = float(item_values[1])  # Текущая сумма цели

        top_up_window = tk.Toplevel(self)
        top_up_window.title("Пополнение цели")
        top_up_window.geometry("300x200")

        tk.Label(top_up_window, text="Введите сумму для пополнения:").pack(pady=10)
        amount_entry = tk.Entry(top_up_window)
        amount_entry.pack(pady=10)

        #def save_top_up():
        #    try:
        #        amount = float(amount_entry.get())
        #        if amount <= 0:
        #            raise ValueError("Сумма должна быть положительной!")

        #        # Проверка баланса пользователя перед пополнением
        #        conn = sqlite3.connect('users.db')
        #        cursor = conn.cursor()

        #        # Получаем текущий баланс пользователя
        #        cursor.execute('SELECT balance FROM users WHERE id = ?', (self.user[0],))
        #        user_balance = cursor.fetchone()[0]

        #        print(f"Текущий баланс: {user_balance}")  # Отладочный вывод

        #        # Проверяем, что тип данных баланса правильный
        #        if isinstance(user_balance, str):
        #            user_balance = float(user_balance)  # Преобразуем в число, если это строка

        #        # Проверяем, хватает ли средств на балансе
        #        if amount > user_balance:
        #            messagebox.showerror("Ошибка", f"Недостаточно средств на балансе! Баланс: {user_balance}")
        #            conn.close()
        #            return

                # Обновляем текущую сумму цели в базе данных
        #        cursor.execute('''
        #            UPDATE goals SET current_amount = current_amount + ? WHERE id = ?
        #        ''', (amount, goal_id))
        #        conn.commit()

                # Обновляем баланс пользователя (сумма списывается с баланса)
        #        cursor.execute('''
        #            UPDATE users
        #            SET balance = balance - ?
        #            WHERE id = ?
        #        ''', (amount, self.user[0]))
        #        conn.commit()

        #        conn.close()

                # Обновляем данные в интерфейсе
        #        self.update_balance()  # Обновляем баланс
        #        self.update_goals_list()  # Обновляем список целей

        #       messagebox.showinfo("Успех", f"Цель пополнена на {amount}₽.")
        #        top_up_window.destroy()

        #    except ValueError as e:
        #        messagebox.showerror("Ошибка", str(e))

        # Используем lambda, чтобы передать self в метод save_top_up
        #tk.Button(top_up_window, text="Подтвердить", command=lambda: save_top_up()).pack(pady=10)

    def update_goals_list(self): #Объявление метода update_goals_list внутри класса. Этот метод отвечает за обновление списка финансовых целей.
        # Очищаем таблицу
        for row in self.goals_tree.get_children(): #Цикл проходит по всем строкам дерева целей (self.goals_tree) и удаляет их одну за другой, очищая таблицу перед добавлением новых данных.
            self.goals_tree.delete(row)

        # Получаем данные о целях из базы данных
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, target_amount, current_amount, target_date
            FROM goals
            WHERE user_id = ?
        ''', (self.user[0],))  # Получаем цели для текущего пользователя
        goals = cursor.fetchall()
        conn.close()

        # Используем словарь для отслеживания добавленных кнопок
        #added_buttons = {}

        for goal_id, title, target_amount, current_amount, target_date in goals: #Цикл перебирает все цели, полученные из базы данных. Для каждой цели извлекаются следующие параметры: идентификатор цели, название, целевая сумма, текущая сумма и срок завершения.
            # Вычисляем количество оставшихся дней
            remaining_days = (datetime.strptime(target_date, "%Y-%m-%d") - datetime.now()).days #Вычисление количества оставшихся дней до срока завершения цели. Если осталось меньше одного дня, то отображается сообщение "Срок истёк".
            remaining_text = f"{remaining_days + 1} дн." if remaining_days >= 0 else "Срок истёк"

            if current_amount >= target_amount: #Если текущая сумма достигла целевой, добавляем новую строку в дерево целей с соответствующими значениями и помечаем её тегом "completed".
                self.goals_tree.insert(
                    "",
                    tk.END,
                    values=(title, f"{current_amount}/{target_amount}", "Цель достигнута!"),
                    tags=("completed",)
                )
                # Добавляем кнопку "Удалить", если она еще не добавлена
                #if goal_id not in added_buttons:
                #    delete_button = tk.Button(
                #        self.goals_page,
                #        text="Удалить",
                #        command=lambda gid=goal_id: self.delete_completed_goal(gid)
                #    )
                #    delete_button.pack(pady=5)
                #    added_buttons[goal_id] = delete_button
            else:
                self.goals_tree.insert( #Если цель ещё не завершена, добавляем новую строку в дерево целей с указанием названия, целевой суммы, текущей суммы и оставшегося времени.
                    "",
                    tk.END,
                    values=(
                        title,  # Название цели
                        f"{target_amount}",  # Цель
                        f"{current_amount}",  # Текущая сумма
                        remaining_text  # Осталось времени
                    )
                )

    def add_goal_window(self):
        add_goal_window = tk.Toplevel(self)
        add_goal_window.title("Добавить цель")
        add_goal_window.geometry("300x300")
        add_goal_window.resizable(False, False)

        tk.Label(add_goal_window, text="Название цели:").pack(pady=10)
        title_entry = tk.Entry(add_goal_window)
        title_entry.pack(pady=5)

        tk.Label(add_goal_window, text="Сумма цели (₽):").pack(pady=10)
        target_amount_entry = tk.Entry(add_goal_window)
        target_amount_entry.pack(pady=5)

        tk.Label(add_goal_window, text="Дата достижения цели (ГГГГ-ММ-ДД):").pack(pady=10)
        target_date_entry = tk.Entry(add_goal_window)
        target_date_entry.pack(pady=5)


        #if not validate_date(targetdate):
        #    messagebox.showerror("Ошибка", "Некорректный формат даты! Используйте ГГГГ-ММ-ДД.")
        #    return


        def save_goal():
            title = title_entry.get()
            target_amount = target_amount_entry.get()
            target_date = target_date_entry.get()

            if not title or not target_amount or not target_date:
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return
            if not validate_date(target_date):
                messagebox.showerror("Ошибка", "Некорректный формат даты! Используйте ГГГГ-ММ-ДД.")
                return

            try:
                target_amount = float(target_amount)
            except ValueError:
                messagebox.showerror("Ошибка", "Сумма цели должна быть числом!")
                return

            # Добавляем текущую дату для поля creation_date
            creation_date = datetime.now().strftime("%Y-%m-%d")  # Получаем текущую дату в формате "ГГГГ-ММ-ДД"

            # Добавляем цель в базу данных
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO goals (user_id, title, target_amount, current_amount, target_date, creation_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.user[0], title, target_amount, 0, target_date, creation_date))  # Текущая сумма = 0
            conn.commit()
            conn.close()

            messagebox.showinfo("Успех", "Цель добавлена!")
            add_goal_window.destroy()

            self.update_goals_list()  # Обновляем список целей

        tk.Button(add_goal_window, text="Сохранить цель", command=save_goal).pack(pady=10)

    def setup_reminders_page(self):
        tk.Label(self.reminders_page, text="Напоминания", font=("Arial", 16)).pack(pady=10)

        # Создание объекта TreeView для отображения таблицы напоминаний. У таблицы есть четыре столбца: название, дата, время и описание. Параметр show="headings" указывает, что нужно показывать только заголовки столбцов без первого пустого столбца, который обычно присутствует в TreeView.
        self.reminders_tree = ttk.Treeview(self.reminders_page, columns=("Title", "Date", "Time", "Description"), show="headings")
        self.reminders_tree.heading("Title", text="Название")
        self.reminders_tree.heading("Date", text="Дата")
        self.reminders_tree.heading("Time", text="Время")
        self.reminders_tree.heading("Description", text="Описание")
        self.reminders_tree.pack(fill=tk.BOTH, expand=True) #Упаковка таблицы таким образом, чтобы она занимала все доступное пространство по горизонтали и вертикали на странице.
        self.reminders_tree.column("Time", stretch=False, width=100 ) #Настройка ширины столбца "Время" на 100 пикселей и отключение автоматического растяжения содержимого.



        tk.Button(self.reminders_page, text="Добавить напоминание", command=self.add_reminder_window).pack(pady=10)

        tk.Button(self.reminders_page, text="Удалить напоминание", command=self.delete_reminder).pack(pady=5)

        self.load_reminders() #Вызов метода load_reminders, который загружает и отображает имеющиеся напоминания в таблице.

    def load_reminders(self): #Объявление метода load_reminders внутри класса. Этот метод отвечает за загрузку напоминаний из базы данных и отображение их в таблице.
        # Очистка текущего содержимого
        for item in self.reminders_tree.get_children(): #Перед загрузкой новых данных очищаем таблицу напоминаний, удаляя все существующие элементы.
            self.reminders_tree.delete(item)

        # Загрузка напоминаний из базы данных
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT title, date, time, description_reminder FROM reminders WHERE user_id = ?', (self.user[0],))
        for row in cursor.fetchall(): #Проходим циклом по результатам запроса и добавляем каждое напоминание в таблицу.
            self.reminders_tree.insert("", tk.END, values=row)
        conn.close()

    def delete_reminder(self):
        selected_item = self.reminders_tree.selection() #Получаем идентификатор выбранного элемента в дереве напоминаний
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите напоминание для удаления.")
            return

        # Получаем значения из выбранной строки
        item_values = self.reminders_tree.item(selected_item)['values'] #Извлекаем значения из выбранной строки: название, дату и время напоминания.
        title = item_values[0]
        date = item_values[1]
        time = item_values[2]

        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить напоминание '{title}'?"): #Эта строка показывает диалоговое окно с вопросом подтверждения удаления напоминания. Пользователь видит название напоминания и может подтвердить или отменить операцию.
            try:
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM reminders WHERE user_id=? AND title=? AND date=? AND time=?",
                               (self.user[0], title, date, time)) #Выполняет SQL-запрос для удаления напоминания из базы данных. Условием для удаления являются совпадение идентификатора пользователя, названия, даты и времени напоминания.
                conn.commit()
                conn.close()

                # Удаляем строку из Treeview
                self.reminders_tree.delete(selected_item)

                messagebox.showinfo("Успех", "Напоминание удалено.")
            except Exception as e: #Начинает блок обработки исключений. Если возникает любая ошибка при выполнении кода в блоке try, управление переходит сюда.
                messagebox.showerror("Ошибка", f"Не удалось удалить напоминание: {e}")

    def add_reminder_window(self):
        add_window = tk.Toplevel(self)
        add_window.title("Добавить напоминание")
        add_window.geometry("300x400")
        add_window.resizable(False, False)

        tk.Label(add_window, text="Название:").pack(pady=5)
        title_entry = tk.Entry(add_window)
        title_entry.pack(pady=5)

        tk.Label(add_window, text="Дата (ГГГГ-ММ-ДД):").pack(pady=5)
        date_entry = tk.Entry(add_window)
        date_entry.pack(pady=5)

        tk.Label(add_window, text="Время (ЧЧ:ММ):").pack(pady=5)
        time_entry = tk.Entry(add_window)
        time_entry.pack(pady=5)

        tk.Label(add_window, text="Описание:").pack(pady=5)
        description_entry = tk.Entry(add_window)
        description_entry.pack(pady=5)


        #def validate_date(date_str):
        #    try:
        #        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        #        return date >= datetime.now().date()
        #    except ValueError:
        #        return False

        def validate_time(time_str):
            try:
                datetime.strptime(time_str, "%H:%M")
                return True
            except ValueError:
                return False


        def save_reminder():
            title = title_entry.get()
            date = date_entry.get()
            time = time_entry.get()
            description = description_entry.get()

            # Проверка на пустые поля
            if not title or not date or not time:
                messagebox.showerror("Ошибка", "Заполните все обязательные поля!")
                return

            # Проверка формата даты
            if not validate_date(date):
                messagebox.showerror("Ошибка", "Некорректный формат даты! Используйте ГГГГ-ММ-ДД.")
                return

            # Проверка формата времени
            if not validate_time(time):
                messagebox.showerror("Ошибка", "Некорректный формат времени! Используйте ЧЧ:ММ.")
                return


            # Сохранение данных в базу данных
            try: #Открытие соединения с базой данных, выполнение SQL-запроса для вставки данных о новом напоминании и закрытие соединения. Данные вставляются в таблицу reminders: идентификатор пользователя, название, дата, время и описание.
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO reminders (user_id, title, date, time, description_reminder) 
                    VALUES (?, ?, ?, ?, ?)
                """, (self.user[0], title, date, time, description))
                conn.commit()
                conn.close()
                #После успешного сохранения данных в базу данных выводится сообщение об успехе, окно добавления напоминания закрывается, и происходит перезагрузка списка напоминаний. Если произошла ошибка, выводится соответствующее сообщение с описанием исключения.

                messagebox.showinfo("Успех", "Напоминание добавлено!")
                add_window.destroy()
                self.load_reminders()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить напоминание: {e}")

        tk.Button(add_window, text="Сохранить", command=save_reminder).pack(pady=10)

        def check_reminders_db(self):
            def check_db():
                now = datetime.now()
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute('SELECT title, date, time FROM reminders WHERE user_id = ?', (self.user[0],))
                reminders = cursor.fetchall()
                conn.close()

                for title, date_str, time_str in reminders:
                    reminder_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                    if now <= reminder_time <= now + timedelta(minutes=1):
                        messagebox.showinfo("Напоминание", f"Напоминание: {title}")

                # Проверять каждую минуту
                self.after(60000, check_db)

            check_db()


        def check_db():
            now = datetime.now()
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT title, date, time FROM reminders WHERE user_id = ?', (self.user[0],))
            reminders = cursor.fetchall()
            conn.close()

            for title, date_str, time_str in reminders:
                reminder_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                if now <= reminder_time <= now + timedelta(minutes=1):
                    messagebox.showinfo("Напоминание", f"Напоминание: {title}")

            # Проверять каждую минуту
            self.after(60000, check_db)
            check_db()


            def check_reminders():
                print("Запуск проверки напоминаний...")  # Проверка, что поток запущен
                while True:
                    now = datetime.now()
                    print(f"Текущее время: {now.strftime('%Y-%m-%d %H:%M')}")  # Вывод времени для отладки

                    try:
                        conn = sqlite3.connect('users.db')
                        cursor = conn.cursor()
                        cursor.execute('''
                            SELECT title, date, time
                            FROM reminders
                            WHERE user_id = ? AND date = ? AND time = ?
                        ''', (self.user[0], now.strftime("%Y-%m-%d"), "18:25"))
                        
                        reminders = cursor.fetchall()
                        conn.close()

                        if reminders:
                            for reminder in reminders:
                                print(f"Напоминание найдено: {reminder[0]}")  # Печать напоминания
                                messagebox.showinfo("Напоминание", f"{reminder[0]} наступило!")  # Показываем уведомление

                    except Exception as e:
                        print(f"Ошибка при проверке напоминаний: {e}")

                    time.sleep(60)  # Проверяем каждую минуту

            # Запускаем поток в фоновом режиме
            print("Запуск потока для уведомлений...")
            threading.Thread(target=check_reminders, daemon=True).start()  # Создаём и запускаем поток




    def update_goal_progress(self, amount):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, current_amount, target_amount FROM goals WHERE user_id = ?
        ''', (self.user[0],))
        goals = cursor.fetchall()

        #if not goals:
        #    messagebox.showinfo("Информация", "У вас нет активных целей.")
        #    conn.close()
        #    return

        for goal_id, current_amount, target_amount in goals:
            new_amount = current_amount + amount

            if new_amount >= target_amount:
                cursor.execute('''
                    UPDATE goals SET current_amount = ?, target_amount = 0 WHERE id = ?
                ''', (target_amount, goal_id))
                messagebox.showinfo("Поздравляем!", f"Цель достигнута!")
            else:
                cursor.execute('''
                    UPDATE goals SET current_amount = ? WHERE id = ?
                ''', (new_amount, goal_id))

        conn.commit()
        conn.close()

        self.update_goals_list()

    def delete_completed_goal(self):
        # Получаем выбранный элемент
        selected_item = self.goals_tree.selection() #Получение идентификаторов выбранных строк в дереве целей (goals_tree).
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите цель для удаления.")
            return

        # Получаем данные из выбранного элемента
        item_values = self.goals_tree.item(selected_item)['values'] #Извлечение данных из выбранной строки дерева целей. Извлекается название цели, которое находится в первой позиции списка значений.
        title = item_values[0]

        # Отображение диалогового окна с подтверждением удаления цели. Пользователю предлагается подтвердить удаление цели с указанным названием.
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить цель '{title}'?"):
            try:
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()

                # Выполнение SQL-запроса для удаления цели из базы данных по её названию и идентификатору пользователя. Изменения фиксируются, и соединение с базой данных закрывается.
                cursor.execute("""
                    DELETE FROM goals 
                    WHERE user_id = ? AND title = ?
                """, (self.user[0], title))
                conn.commit()
                conn.close()

                # Удаляем элемент из Treeview
                self.goals_tree.delete(selected_item)

                messagebox.showinfo("Успех", "Цель удалена.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить цель: {e}")

def validate_date(date_str):
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        return date >= datetime.now().date()
    except ValueError:
        return False

def clear_text():
    login_entry.delete(0, 'end')
    password_entry.delete(0, 'end')
    confirm_password_entry.delete(0, 'end')

def register():
    login = login_entry.get()
    password = password_entry.get()
    confirm_password = confirm_password_entry.get()

    if not login or not password or not confirm_password:
        messagebox.showerror("Ошибка", "Заполните все поля!")
        return

    if password != confirm_password:
        messagebox.showerror("Ошибка", "Пароли не совпадают!")
        return

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (login, password) VALUES (?, ?)", (login, password))
        conn.commit()
        messagebox.showinfo("Успех", "Регистрация прошла успешно!")
        clear_text()
    except sqlite3.IntegrityError:
        messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует!")
    finally:
        conn.close()


def login():
    login = login_entry.get()
    password = password_entry.get()
    confirm_password = confirm_password_entry.get()
    if not login or not password or not confirm_password:
        messagebox.showerror("Ошибка", "Заполните все поля!")
        return
    if password != confirm_password:
        messagebox.showerror("Ошибка", "Пароли не совпадают")
        return


    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE login = ? AND password = ?", (login, password))
    user = cursor.fetchone()
    conn.close()


    if user and password == confirm_password:
        messagebox.showinfo("Успех", "Вход выполнен успешно!")
        window.destroy()
        app = FinanceAssistantApp(user)
        app.mainloop()
    else:
        messagebox.showerror("Ошибка", "Проверьте корректность введённых данных!")


#create_db()

window = tk.Tk()
window.resizable(width=False, height=False)
window.title("Вход/Регистрация")
window.geometry("800x600")

icon = PhotoImage(file= "logo.png")
window.iconphoto(False, icon)

app_label = tk.Label(window, text = "Финансовый помощник",fg="#57a1f8", font=('Microsoft Yahei UI Light',23,'bold'), pady=40)
app_label.place(relx=.5,anchor="n")
login_label = tk.Label(window, text="Логин:")
login_label.place(x=370,y=100)
login_entry = tk.Entry(window)
login_entry.place(x=300,y=130)

password_label = tk.Label(window, text="Пароль:")
password_label.place(x=367,y=180)
password_entry = tk.Entry(window, show="*")
password_entry.place(x=300, y = 210)

confirm_password_label = tk.Label(window, text="Подтверждение пароля:")
confirm_password_label.place(x=315, y = 260)
confirm_password_entry = tk.Entry(window, show="*")
confirm_password_entry.place(x=300, y = 290)

login_button = tk.Button(window, text="Вход", command=login)
login_button.place(x=300,y=320)

register_button = tk.Button(window, text="Регистрация", command=register)
register_button.place(x=375,y=320)

window.mainloop()