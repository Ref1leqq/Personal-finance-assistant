import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import sqlite3
from datetime import datetime, timedelta
import re
import pandas as pd
import matplotlib.pyplot as plt
import os
os.chdir(os.path.dirname(__file__))

def create_db():
    """
    Создает базу данных и таблицы, если они еще не существуют.

    Таблицы:
    - users: Хранит данные пользователей.
    - goals: Хранит финансовые цели пользователей.
    - reminders: Хранит напоминания пользователей.
    - transactions: Хранит транзакции (доходы и расходы).
    """
    conn = sqlite3.connect('users.db') 
    cursor = conn.cursor() 

    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            target_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0,
            creation_date TEXT NOT NULL,
            target_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            description_reminder TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

create_db()

class FinanceAssistantApp(tk.Tk):
    """
    Главное окно приложения "Финансовый помощник".

    Атрибуты:
        user (tuple): Текущий пользователь (ID и логин).

    Методы:
        create_main_interface(): Создает основной интерфейс приложения.
        update_balance(): Обновляет данные баланса, доходов и расходов.
        generate_chart(data_type, chart_type): Генерирует диаграмму на основе данных пользователя.
        add_transaction_window(): Открывает окно для добавления транзакции.
        setup_diagrams_page(): Настраивает вкладку диаграмм.
        plot_pie_chart(df): Строит круговую диаграмму.
        plot_bar_chart(df): Строит гистограмму.
        plot_gisto_chart(df): Строит гистограмму с цветами.
        setup_transactions_page(): Настраивает вкладку для управления транзакциями.
        update_transactions_list(): Обновляет список транзакций.
        setup_goals_page(): Настраивает вкладку для управления финансовыми целями.
        update_goals_list(): Обновляет список финансовых целей.
        add_goal_window(): Открывает окно для добавления новой финансовой цели.
        delete_completed_goal(): Удаляет выполненную финансовую цель.
        setup_reminders_page(): Настраивает вкладку для работы с напоминаниями.
        load_reminders(): Загружает напоминания из базы данных.
        add_reminder_window(): Открывает окно для добавления напоминания.
        delete_reminder(): Удаляет выбранное напоминание.
        check_reminders(): Проверяет напоминания на актуальность.
        check_reminders_loop(): Запускает цикл проверки напоминаний.
    """
    def __init__(self, user):
        """
        Инициализирует главное окно приложения.

        Args:
            user (tuple): Кортеж (ID пользователя, логин пользователя).
        """
        super().__init__()
        self.title("Финансовый помощник")
        self.geometry("800x600")
        self.user = user
        icon = PhotoImage(file="logo.png")
        self.iconphoto(False, icon)
        self.create_main_interface()
        self.check_reminders_loop()




    def create_main_interface(self):
        """
        Создает основной интерфейс с вкладками и информацией о пользователе.
        """
        # Верхняя панель
        top_frame = tk.Frame(self, bg="lightblue")
        top_frame.pack(fill=tk.X)

        user_icon = tk.Label(top_frame, text="👤", font=("Arial", 24), bg="lightblue")
        user_icon.pack(side=tk.LEFT, padx=15)

        user_label = tk.Label(top_frame, text=f"Добро пожаловать, {self.user[1]}!", font=("Arial", 16), bg="lightblue")
        user_label.pack(side=tk.LEFT)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.home_page = tk.Frame(notebook)
        self.diagrams_page = tk.Frame(notebook)
        self.transactions_page = tk.Frame(notebook)
        self.goals_page = tk.Frame(notebook)
        self.reminders_page = tk.Frame(notebook)

        notebook.add(self.home_page, text="Главная")
        notebook.add(self.diagrams_page, text="Диаграммы")
        notebook.add(self.transactions_page, text="Транзакции")
        notebook.add(self.goals_page, text="Цели")
        notebook.add(self.reminders_page, text="Напоминания")

        self.setup_home_page()
        self.setup_diagrams_page()
        self.setup_transactions_page()
        self.setup_goals_page()
        self.setup_reminders_page()


    def setup_home_page(self):
        """
        Настраивает вкладку "Главная" с отображением баланса и кнопкой добавления транзакции.
        """
        tk.Label(self.home_page, text="Общая информация", font=("Arial", 16)).pack(pady=10)

        self.balance_label = tk.Label(self.home_page, text="Текущий баланс: 0.00 RUB", font=("Arial", 14))
        self.balance_label.pack(pady=10)

        self.earnings_label = tk.Label(self.home_page, text="Заработано: 0.00 RUB", font=("Arial", 12))
        self.earnings_label.pack(pady=5)

        self.expenses_label = tk.Label(self.home_page, text="Потрачено: 0.00 RUB", font=("Arial", 12))
        self.expenses_label.pack(pady=5)

        tk.Button(self.home_page, text="Добавить транзакцию", command=self.add_transaction_window).pack(pady=10)

        self.update_balance()

    def update_balance(self):
        """
        Обновляет текущий баланс пользователя, суммируя доходы и расходы из базы данных.
        """
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(CASE WHEN type = "Доход" THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN type = "Расход" THEN amount ELSE 0 END) as total_expense
            FROM transactions
            WHERE user_id = ?
        ''', (self.user[0],))
        result = cursor.fetchone()
        conn.close()

        total_income = result[0] if result[0] is not None else 0.0
        total_expense = result[1] if result[1] is not None else 0.0
        current_balance = total_income - total_expense

        self.balance_label.config(text=f"Текущий баланс: {current_balance} RUB")
        self.earnings_label.config(text=f"Заработано: {total_income} RUB")
        self.expenses_label.config(text=f"Потрачено: {total_expense} RUB")

    def setup_diagrams_page(self):
        """
        Настраивает вкладку для работы с диаграммами.
        """
        tk.Label(self.diagrams_page, text="Диаграммы расходов и доходов", font=("Arial", 16)).pack(pady=10)

        tk.Button(
            self.diagrams_page,
            text="Создать диаграммы",
            command=self.open_diagrams_window
        ).pack(pady=10)

    def open_diagrams_window(self):
        """
        Открывает окно настройки и генерации диаграмм.
        """
        diagrams_window = tk.Toplevel(self)
        diagrams_window.title("Настройка диаграмм")
        diagrams_window.geometry("400x400")
        diagrams_window.resizable(False, False)

        tk.Label(diagrams_window, text="Тип данных:").pack(pady=5)
        data_type = tk.StringVar(value="Выберите тип транзакций")
        ttk.Combobox(
            diagrams_window,
            textvariable=data_type,
            state="readonly",
            values=["Только доходы", "Только расходы"]
        ).pack(pady=5)

        tk.Label(diagrams_window, text="Тип визуализации:").pack(pady=5)
        chart_type = tk.StringVar(value="Круговая диаграмма")
        ttk.Combobox(
            diagrams_window,
            textvariable=chart_type,
            state="readonly",
            values=["Круговая диаграмма", "Гистограмма", "Гистограмма(Цвета)"]
        ).pack(pady=5)

        tk.Button(
            diagrams_window,
            text="Построить диаграмму",
            command=lambda: (
                messagebox.showerror("Ошибка", "Пожалуйста, выберите тип данных!")
                if data_type.get() == "Выберите тип транзакций" else self.generate_chart(data_type.get(),
                                                                                         chart_type.get())
            )
        ).pack(pady=15)

    def generate_chart(self, data_type, chart_type):
        """
        Генерирует и отображает диаграмму на основе данных пользователя.

        Args:
            data_type (str): Тип данных ("Только доходы" или "Только расходы").
            chart_type (str): Тип диаграммы ("Круговая диаграмма" и др.).
        """
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT category, amount, type FROM transactions WHERE user_id = ?''', (self.user[0],))
        data = cursor.fetchall()
        conn.close()

        # Преобразование в DataFrame
        df = pd.DataFrame(data, columns=["Category", "Amount", "Type"])

        # Фильтрация данных
        if data_type == "Только доходы":
            df = df[df["Type"] == "Доход"]
        elif data_type == "Только расходы":
            df = df[df["Type"] == "Расход"]

        if chart_type == "Круговая диаграмма":
            self.plot_pie_chart(df)
        elif chart_type == "Гистограмма":
            self.plot_bar_chart(df)
        elif chart_type == "Гистограмма(Цвета)":
            self.plot_gisto_chart(df)

    def plot_pie_chart(self, df):
        """
        Строит круговую диаграмму на основе данных.

        Args:
            df (pd.DataFrame): Данные с колонками "Category" и "Amount".
        """
        plt.figure(figsize=(8, 8))
        df.groupby("Category")["Amount"].sum().plot.pie(autopct='%1.1f%%', startangle=90)
        plt.title("Круговая диаграмма")
        plt.ylabel("")
        plt.tight_layout()
        plt.show()

    def plot_bar_chart(self, df):
        """
        Строит гистограмму на основе данных.

        Args:
            df (pd.DataFrame): Данные с колонками "Category" и "Amount".
        """
        plt.figure(figsize=(10, 10))
        df.groupby("Category")["Amount"].sum().plot(kind="bar")
        plt.title("Гистограмма")
        plt.xlabel("Категория")
        plt.ylabel("Сумма")
        plt.show()

    def plot_gisto_chart(self, df):
        """
        Строит гистограмму с использованием различных цветов для категорий.

        Args:
            df (pd.DataFrame): Данные с колонками "Category" и "Amount".
        """
        plt.figure(figsize=(10, 10))

        grouped = df.groupby("Category")["Amount"].sum()
        colors = ["red", "green", "blue", "purple", "orange"]
        grouped.plot(kind="bar", color=colors[:len(grouped)])

        plt.title("Гистограмма(Цвета)")
        plt.xlabel("Категория")
        plt.ylabel("Сумма")
        plt.show()

    def setup_transactions_page(self):
        """
        Настраивает вкладку для отображения и управления транзакциями.
        """
        tk.Label(self.transactions_page, text="История транзакций", font=("Arial", 16)).pack(pady=10)
        self.transactions_tree = ttk.Treeview(self.transactions_page, columns=("category", "amount","type", "date"), show="headings")
        self.transactions_tree.heading("category", text="Категория")
        self.transactions_tree.heading("amount", text="Сумма")
        self.transactions_tree.heading("type", text="Тип")
        self.transactions_tree.heading("date", text="Дата")
        self.transactions_tree.pack(fill=tk.BOTH, expand=True)
        self.update_transactions_list()

    def update_transactions_list(self):
        """
        Обновляет список транзакций из базы данных.
        """
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, amount, type, date FROM transactions WHERE user_id = ?
        """, (self.user[0],))
        transactions = cursor.fetchall()
        conn.close()

        for row in self.transactions_tree.get_children():
            self.transactions_tree.delete(row)

        for transaction in transactions:
            self.transactions_tree.insert("", tk.END, values=transaction)

    def add_transaction_window(self):
        """
        Открывает окно для добавления новой транзакции.
        """
        add_window = tk.Toplevel(self)
        add_window.title("Добавить транзакцию")
        add_window.geometry("300x400")  

        tk.Label(add_window, text="Тип транзакции:").pack(pady=15)

        transaction_type = tk.StringVar(value="Расход")  

        category_type = tk.StringVar(value="Выберите категорию")
        combobox = ttk.Combobox(add_window, textvariable=category_type, state="readonly")
        combobox.pack(padx=6, pady=6)

        def update_categories():
            """
            Устанавливает начальные значения категорий
            """
            if transaction_type.get() == "Доход":
                combobox["values"] = ["Зарплата", "Переводы", "Инвестиции"]
            else:
                combobox["values"] = ["Продукты", "Одежда", "Такси"]

            category_type.set("Выберите категорию")

        income_radiobutton = tk.Radiobutton(add_window, text="Доход", variable=transaction_type, value="Доход",
                                            command=update_categories, pady=20)
        income_radiobutton.pack()
        expense_radiobutton = tk.Radiobutton(add_window, text="Расход", variable=transaction_type, value="Расход",
                                            command=update_categories, pady=5)
        expense_radiobutton.pack()


        combobox["values"] = ["Продукты", "Одежда", "Такси"]
        category_type.set("Выберите категорию")

        tk.Label(add_window, text="Сумма:").pack(pady=15)
        amount_entry = tk.Entry(add_window)
        amount_entry.pack(pady=2)

        def save_transaction():
            """
            Сохраняет новую транзакцию в базу данных.
            """
            category = category_type.get()  
            amount = amount_entry.get()
            transaction_type_value = transaction_type.get()

            if category == "Выберите категорию":
                messagebox.showerror("Ошибка", "Пожалуйста, выберите категорию!")
                return

            if not amount:
                messagebox.showerror("Ошибка", "Введите сумму!")
                return

            try:
                amount = float(amount)
            except ValueError:
                messagebox.showerror("Ошибка", "Сумма должна быть числом!")
                return

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (user_id, category, amount, date, type) VALUES (?, ?, ?, ?, ?)
            """, (self.user[0], category, amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), transaction_type_value))
            conn.commit()
            conn.close()

            if transaction_type_value == "Доход":
                self.update_goal_progress(amount)

            messagebox.showinfo("Успех", "Транзакция добавлена!")
            add_window.destroy()
            self.update_transactions_list()
            self.update_balance()

        tk.Button(add_window, text="Сохранить", command=save_transaction).pack(pady=10)


    def setup_goals_page(self):
        """
        Настраивает вкладку для управления финансовыми целями.
        """
        tk.Label(self.goals_page, text="Финансовые цели", font=("Arial", 16)).pack(pady=10)

        self.goals_tree = ttk.Treeview(self.goals_page, columns=("title", "target_amount", "current_amount", "remaining"), show="headings")
        self.goals_tree.heading("title", text="Название")
        self.goals_tree.heading("target_amount", text="Цель (₽)")
        self.goals_tree.heading("current_amount", text="Текущая сумма (₽)")
        self.goals_tree.heading("remaining", text="Осталось времени")
        self.goals_tree.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Button(self.goals_page, text="Добавить цель", command=self.add_goal_window).pack(pady=10)
        tk.Button(self.goals_page, text="Удалить цель", command=self.delete_completed_goal).pack(pady=10)

        self.update_goals_list()


    def update_goals_list(self):
        """
        Обновляет список финансовых целей из базы данных.
        """
        # Очищаем таблицу
        for row in self.goals_tree.get_children():
            self.goals_tree.delete(row)

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, target_amount, current_amount, target_date
            FROM goals
            WHERE user_id = ?
        ''', (self.user[0],))
        goals = cursor.fetchall()
        conn.close()


        for goal_id, title, target_amount, current_amount, target_date in goals:
            remaining_days = (datetime.strptime(target_date, "%Y-%m-%d") - datetime.now()).days
            remaining_text = f"{remaining_days + 1} дн." if remaining_days >= 0 else "Срок истёк"

            if current_amount >= target_amount:
                self.goals_tree.insert(
                    "",
                    tk.END,
                    values=(title, f"{current_amount}/{target_amount}", "Цель достигнута!"),
                    tags=("completed",)
                )
            else:
                self.goals_tree.insert(
                    "",
                    tk.END,
                    values=(
                        title, 
                        f"{target_amount}",  
                        f"{current_amount}",  
                        remaining_text  
                    )
                )

    def add_goal_window(self):
        """
        Открывает окно для добавления новой финансовой цели.
        """
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


        def save_goal():
            """
            Сохраняет новую финансовую цель в базе данных.
            """
            title = title_entry.get()
            target_amount = target_amount_entry.get()
            target_date = target_date_entry.get()

            try:
                check_goal_title(title)
                check_goal_amount(target_amount)
                check_goal_date(target_date)
            except ValueError:
                return  

            creation_date = datetime.now().strftime("%Y-%m-%d")

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO goals (user_id, title, target_amount, current_amount, target_date, creation_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.user[0], title, target_amount, 0, target_date, creation_date))
            conn.commit()
            conn.close()

            messagebox.showinfo("Успех", "Цель добавлена!")
            add_goal_window.destroy()

            self.update_goals_list()  

        tk.Button(add_goal_window, text="Сохранить цель", command=save_goal).pack(pady=10)

    def setup_reminders_page(self):
        """
        Настраивает вкладку для управления напоминаниями.
        """
        tk.Label(self.reminders_page, text="Напоминания", font=("Arial", 16)).pack(pady=10)

        self.reminders_tree = ttk.Treeview(self.reminders_page, columns=("Title", "Date", "Time", "Description"), show="headings")
        self.reminders_tree.heading("Title", text="Название")
        self.reminders_tree.heading("Date", text="Дата")
        self.reminders_tree.heading("Time", text="Время")
        self.reminders_tree.heading("Description", text="Описание")
        self.reminders_tree.pack(fill=tk.BOTH, expand=True)
        self.reminders_tree.column("Time", stretch=False, width=100 )

        tk.Button(self.reminders_page, text="Добавить напоминание", command=self.add_reminder_window).pack(pady=10)

        tk.Button(self.reminders_page, text="Удалить напоминание", command=self.delete_reminder).pack(pady=5)

        self.load_reminders()

    def load_reminders(self):
        """
        Загружает все напоминания пользователя из базы данных и отображает их в интерфейсе.
        """
        # Очистка текущего содержимого
        for item in self.reminders_tree.get_children():
            self.reminders_tree.delete(item)

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT title, date, time, description_reminder FROM reminders WHERE user_id = ?', (self.user[0],))
        for row in cursor.fetchall():
            self.reminders_tree.insert("", tk.END, values=row)
        conn.close()

    def delete_reminder(self):
        """
        Удаляет выбранное пользователем напоминание.
        """
        selected_item = self.reminders_tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите напоминание для удаления.")
            return

        item_values = self.reminders_tree.item(selected_item)['values']
        title = item_values[0]
        date = item_values[1]
        time = item_values[2]

        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить напоминание '{title}'?"):
            try:
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM reminders WHERE user_id=? AND title=? AND date=? AND time=?",
                               (self.user[0], title, date, time))
                conn.commit()
                conn.close()

                self.reminders_tree.delete(selected_item)

                messagebox.showinfo("Успех", "Напоминание удалено.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить напоминание: {e}")

    def add_reminder_window(self):
        """
        Открывает окно для добавления нового напоминания.
        """
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

        def validate_time(time_str):
            """
            Проверяет корректность формата времени.

            Args:
                time_str (str): Время в формате "ЧЧ:ММ".

            Returns:
                bool: True, если время корректно, иначе False.
            """
            try:
                datetime.strptime(time_str, "%H:%M")
                return True
            except ValueError:
                return False


        def save_reminder():
            """
            Сохраняет новое напоминание в базе данных.
            """
            title = title_entry.get()
            date = date_entry.get()
            time = time_entry.get()
            description = description_entry.get()

            if not title or not date or not time:
                messagebox.showerror("Ошибка", "Заполните все обязательные поля!")
                return

            if not validate_date(date):
                messagebox.showerror("Ошибка", "Некорректный формат даты! Используйте ГГГГ-ММ-ДД.")
                return

            if not validate_time(time):
                messagebox.showerror("Ошибка", "Некорректный формат времени! Используйте ЧЧ:ММ.")
                return

            if not re.match(r"^[a-zA-Zа-яА-Я0-9\s\-.,!?]+$", title):
                messagebox.showerror("Ошибка", "Название содержит недопустимые символы!")
                return

            if description and not re.match(r"^[a-zA-Zа-яА-Я0-9\s\-.,!?]+$", description):
                messagebox.showerror("Ошибка", "Описание содержит недопустимые символы!")
                return

            try:
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO reminders (user_id, title, date, time, description_reminder) 
                    VALUES (?, ?, ?, ?, ?)
                """, (self.user[0], title, date, time, description))
                conn.commit()
                conn.close()

                messagebox.showinfo("Успех", "Напоминание добавлено!")
                add_window.destroy()
                self.load_reminders()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить напоминание: {e}")

        tk.Button(add_window, text="Сохранить", command=save_reminder).pack(pady=10)

    def check_reminders(self):
        """
        Проверяет напоминания в базе данных на устаревшие или близкие к текущему времени.
        """
        now = datetime.now()
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute('SELECT id, title, date, time FROM reminders WHERE user_id = ?', (self.user[0],))
        reminders = cursor.fetchall()

        for reminder_id, title, date_str, time_str in reminders:
            if not date_str.strip() or not time_str.strip():
                continue

            try:
                reminder_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

                if reminder_datetime < now:
                    cursor.execute('''
                        UPDATE reminders 
                        SET description_reminder = ?, date = '', time = '' 
                        WHERE id = ?''',
                                   ("Напоминание устарело.", reminder_id))

                if now <= reminder_datetime <= now + timedelta(minutes=30):
                    messagebox.showinfo("Напоминание", f"Напоминание скоро истечет!\n\nНапоминание: {title}")

            except ValueError as e:
                print(f"Ошибка обработки напоминания ID {reminder_id}: {e}")

        conn.commit()
        conn.close()

    def check_reminders_loop(self):
        """
        Запускает проверку напоминаний в фоне каждые 1 минут.
        """

        def delayed_check():
            self.check_reminders()
            self.after(600000, delayed_check)

        self.after(1000, delayed_check)



    def update_goal_progress(self, amount):
        """
        Обновляет прогресс всех финансовых целей пользователя на основании внесённой суммы.

        Args:
            amount (float): Сумма для обновления прогресса целей.
        """
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, current_amount, target_amount FROM goals WHERE user_id = ?
        ''', (self.user[0],))
        goals = cursor.fetchall()

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
        """
        Удаляет завершённую финансовую цель из базы данных и интерфейса.
        """

        selected_item = self.goals_tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите цель для удаления.")
            return


        item_values = self.goals_tree.item(selected_item)['values']
        title = item_values[0]


        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить цель '{title}'?"):
            try:
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()

                # Удаляем цель из базы данных по её названию и пользователю
                cursor.execute("""
                    DELETE FROM goals 
                    WHERE user_id = ? AND title = ?
                """, (self.user[0], title))
                conn.commit()
                conn.close()

                self.goals_tree.delete(selected_item)

                messagebox.showinfo("Успех", "Цель удалена.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить цель: {e}")


def validate_date(date_str):
    '''
    Проверяет, является ли введенная дата допустимой.

    :param date_str: Строка, представляющая дату в формате '%Y-%m-%d'
    :type date_str: string
    :returns: Истина, если дата валидна, иначе поднимается исключение `ValueError`.
    :rtype: bool
    :raises ValueError: if date < datetime.now().date()
    '''
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    if date < datetime.now().date():
        messagebox.showerror("Ошибка","Дата должна быть больше указанной")
        raise ValueError("Дата должна быть больше указанной")
    return True

def clear_text():
    """
    Очищает текст
    """
    login_entry.delete(0, 'end')
    password_entry.delete(0, 'end')
    confirm_password_entry.delete(0, 'end')

def register():
    """
    Обрабатывает регистрацию нового пользователя.
    """
    login = login_entry.get()
    password = password_entry.get()
    confirm_password = confirm_password_entry.get()

    check_login(login)
    check_password(password)
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

def check_sums_transaction_valid(summ, testing=False):
    """
    Проверяет валидность суммы транзакции.
    
    Args:
        summ (int): Сумма транзакции
        testing (bool): Если True, ошибки только через исключения (для тестов).
    Raises:
        ValueError: Если вместо суммы пустое поле
    """
    if not summ.strip():
        if testing:
            raise ValueError("Cумма не может быть пустой")
        else:
            messagebox.showerror("Ошибка", "Сумма не может быть пустой!")
            raise ValueError("Сумма не может быть пустой")
    return True 

def check_transaction_amount_is_not_digit(amount, testing=False):
    """
    Проверяет валидность суммы цели.

    Args:
        amount (str): Сумма траназкции.
        testing (bool): Если True, ошибки только через исключения (для тестов).
    Raises:
        ValueError: Если сумма транзакции некорректна или отрицательна.
    """
    if not amount.isdigit() or int(amount) <= 0: 
        if testing:
            raise ValueError("Сумма транзакции должна быть больше нуля")
        else:
            messagebox.showerror("Ошибка", "Сумма транзакции должна быть больше нуля!")
            raise ValueError("Сумма транзакции должна быть больше нуля")
    return True 

def check_transaction_amount_another_symbols(amount, testing=False):
    """
    Проверяет нет ли посторонних символов в сумме транзакции.

    Args:
        amount (str): Сумма траназкции.
        testing (bool): Если True, ошибки только через исключения (для тестов).
    Raises:
        ValueError: Если сумма транзакции имеет посторонние символы.
    """
    if amount in "$+*|":
        if testing:
            raise ValueError("Сумма транзакции не должна иметь посторонних символов")
        else:
            messagebox.showerror("Ошибка", "Сумма транзакции не должна иметь посторонних символов")
            raise ValueError("Сумма транзакции не должна иметь посторонних символов")
    return True 

def check_goal_title(title, testing=False):
    """
    Проверяет валидность названия цели.

    Args:
        title (str): Название цели.
        testing (bool): Если True, ошибки только через исключения (для тестов).
    Raises:
        ValueError: Если название цели пустое.
    """
    if not title.strip():
        if testing:
            raise ValueError("Название цели не может быть пустым")
        else:
            messagebox.showerror("Ошибка", "Название цели не может быть пустым!")
            raise ValueError("Название цели не может быть пустым")
    return True  


def check_goal_amount(target_amount, testing=False):
    """
    Проверяет валидность суммы цели.

    Args:
        target_amount (str): Сумма цели.
        testing (bool): Если True, ошибки только через исключения (для тестов).
    Raises:
        ValueError: Если сумма цели пуста, некорректна или отрицательна.
    """
    if not target_amount.strip():
        if testing:
            raise ValueError("Сумма цели не может быть пустой")
        else:
            messagebox.showerror("Ошибка", "Сумма цели не может быть пустой!")
            raise ValueError("Сумма цели не может быть пустой")

    if not target_amount.isdigit() or int(target_amount) <= 0:
        if testing:
            raise ValueError("Сумма цели должна быть положительным числом")
        else:
            messagebox.showerror("Ошибка", "Сумма цели должна быть положительным числом!")
            raise ValueError("Сумма цели должна быть положительным числом")
    return True  


def check_goal_date(target_date, testing=False):
    """
    Проверяет валидность даты достижения цели.

    Args:
        target_date (str): Дата достижения цели.
        testing (bool): Если True, ошибки только через исключения (для тестов).
    Raises:
        ValueError: Если дата пуста или формат даты некорректен.
    """
    if not target_date.strip():
        if testing:
            raise ValueError("Дата достижения цели не может быть пустой")
        else:
            messagebox.showerror("Ошибка", "Дата достижения цели не может быть пустой!")
            raise ValueError("Дата достижения цели не может быть пустой")

    try:
        datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        if testing:
            raise ValueError("Некорректный формат даты! Ожидается формат ГГГГ-ММ-ДД.")
        else:
            messagebox.showerror("Ошибка", "Некорректный формат даты! Используйте ГГГГ-ММ-ДД.")
            raise ValueError("Некорректный формат даты! Ожидается формат ГГГГ-ММ-ДД.")
    return True  # Дата валидна


def check_login(entryLogin):
    """
    Проверяет длину введенного логина.

    :param entryPassword: Введенный пользователем логин.
    :type entryPassword: string
    :returns: Истина, если логин удовлетворяет условиям длины.
    :rtype: bool
    :raises ValueError: if len(entryPassword) < 8
    """
    if len(entryLogin) < 3:
        messagebox.showerror("Ошибка!", "Логин слишком короткий! Должен содержать минимум 3 символов.")
        raise ValueError("Логин слишком короткий!")
    return True


def check_password(entryPassword):
    """
    Проверяет длину введенного пароля.

    :param entryPassword: Введенный пользователем пароль.
    :type entryPassword: string
    :returns: Истина, если пароль удовлетворяет условиям длины.
    :rtype: bool
    :raises ValueError: if len(entryPassword) < 8
    """
    if len(entryPassword) < 8:
        messagebox.showerror("Ошибка!", "Пароль слишком короткий! Должен содержать минимум 8 символов.")
        raise ValueError("Пароль слишком короткий!")
    else:
        return True

def login():
    """
    Обрабатывает вход пользователя в систему.
    """
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


if __name__ == "__main__":
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


