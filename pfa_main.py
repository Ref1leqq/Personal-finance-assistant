import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import sqlite3
from datetime import datetime, timedelta
import threading
import re
import pandas as pd
import matplotlib.pyplot as plt 
import time   

def create_db():
    conn = sqlite3.connect('users.db') #подключение к базе данных
    cursor = conn.cursor() #создание курсора

    # Создание таблицы пользователей
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Таблица финансовых целей
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

    # Таблица напоминаний
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

    # Таблица транзакций
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
    def __init__(self, user):
        super().__init__()
        self.title("Финансовый помощник")
        self.geometry("800x600")
        self.user = user
        icon = PhotoImage(file="logo.png")
        self.iconphoto(False, icon)

        # Создание интерфейса
        self.create_main_interface()



    def create_main_interface(self):
        # Верхний фрейм с приветствием и значком пользователя
        top_frame = tk.Frame(self, bg="lightblue")
        top_frame.pack(fill=tk.X)

        user_icon = tk.Label(top_frame, text="👤", font=("Arial", 24), bg="lightblue")
        user_icon.pack(side=tk.LEFT, padx=15)

        user_label = tk.Label(top_frame, text=f"Добро пожаловать, {self.user[1]}!", font=("Arial", 16), bg="lightblue")
        user_label.pack(side=tk.LEFT)


        # Основной интерфейс с вкладками
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладки
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

        # Настройка вкладок
        self.setup_home_page()
        self.setup_diagrams_page()
        self.setup_transactions_page()
        self.setup_goals_page()
        self.setup_reminders_page()

#        self.check_reminders()

    def setup_home_page(self):
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

        self.balance_label.config(text=f"Текущий баланс: {current_balance:.2f} RUB")
        self.earnings_label.config(text=f"Заработано: {total_income:.2f} RUB")
        self.expenses_label.config(text=f"Потрачено: {total_expense:.2f} RUB")
    
    def setup_diagrams_page(self):
        tk.Label(self.diagrams_page, text="Диаграммы расходов и доходов", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.diagrams_page, text="Показать диаграммы", command=self.create_diagrams).pack(pady=10)

    def create_diagrams(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Извлечение данных о доходах и расходах
        cursor.execute('''
            SELECT category, amount, type
            FROM transactions
            WHERE user_id = ?
        ''', (self.user[0],))
        data = cursor.fetchall()
        conn.close()

        # Преобразование в DataFrame
        df = pd.DataFrame(data, columns=['Category', 'Amount', 'Type'])

        # Построение круговых диаграмм
        income_df = df[df['Type'] == "Доход"]
        expense_df = df[df['Type'] == "Расход"]

        # Гистограмма доходов
        plt.figure(figsize=(10, 6))
        income_df.groupby('Category').sum()['Amount'].plot(kind='bar', title="Доходы по категориям")
        plt.xlabel("Категория")
        plt.ylabel("Сумма (₽)")
        plt.show()

        # Гистограмма расходов
        plt.figure(figsize=(10, 6))
        expense_df.groupby('Category').sum()['Amount'].plot(kind='bar', title="Расходы по категориям")
        plt.xlabel("Категория")
        plt.ylabel("Сумма (₽)")
        plt.show()

        # Круговая диаграмма доходов
        plt.figure(figsize=(8, 8))
        income_df.groupby('Category').sum()['Amount'].plot.pie(autopct='%1.1f%%', title="Доходы по категориям")
        plt.ylabel('')
        plt.show()

        # Круговая диаграмма расходов
        plt.figure(figsize=(8, 8))
        expense_df.groupby('Category').sum()['Amount'].plot.pie(autopct='%1.1f%%', title="Расходы по категориям")
        plt.ylabel('')
        plt.show()

    def setup_transactions_page(self):
        tk.Label(self.transactions_page, text="История транзакций", font=("Arial", 16)).pack(pady=10)
        self.transactions_tree = ttk.Treeview(self.transactions_page, columns=("category", "amount","type", "date"), show="headings")
        self.transactions_tree.heading("category", text="Категория")
        self.transactions_tree.heading("amount", text="Сумма")
        self.transactions_tree.heading("type", text="Тип")
        self.transactions_tree.heading("date", text="Дата")
        self.transactions_tree.pack(fill=tk.BOTH, expand=True)
        self.update_transactions_list()

    def update_transactions_list(self):
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
        add_window = tk.Toplevel(self)
        add_window.title("Добавить транзакцию")
        add_window.geometry("300x400")  # Увеличиваем высоту окна для радиокнопок

        tk.Label(add_window, text="Тип транзакции:").pack(pady=5)

        transaction_type = tk.StringVar(value="Расход")  # Значение по умолчанию - "Расход"

        # Радиокнопки для выбора типа транзакции
        def update_categories():
            if transaction_type.get() == "Доход":
                combobox["values"] = ["Зарплата", "Переводы", "Инвестиции"]  # Убираем значения для выбора
            else:
                combobox["values"] = ["Продукты", "Одежда", "Такси"]  # Категории для расхода

        income_radiobutton = tk.Radiobutton(add_window, text="Доход", variable=transaction_type, value="Доход",
                                            command=update_categories)
        income_radiobutton.pack()
        expense_radiobutton = tk.Radiobutton(add_window, text="Расход", variable=transaction_type, value="Расход",
                                             command=update_categories)
        expense_radiobutton.pack()

        tk.Label(add_window, text="Категория:").pack(pady=5)

        # Поле выбора или ввода категории
        combobox = ttk.Combobox(add_window, state="readonly")
        combobox.pack(padx=6, pady=6)

        #category_entry = tk.Entry(add_window, state=tk.DISABLED)  # Поле для пользовательского ввода категории дохода
        #category_entry.pack(padx=6, pady=6)

        tk.Label(add_window, text="Сумма:").pack(pady=5)
        amount_entry = tk.Entry(add_window)
        amount_entry.pack(pady=5)

        def save_transaction():
            category = combobox.get() #if transaction_type.get() == "Доход" else combobox.get()
            amount = amount_entry.get()
            transaction_type_value = transaction_type.get()

            if not amount:
                messagebox.showerror("Ошибка", "Заполните все поля!")
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
        tk.Label(self.goals_page, text="Финансовые цели", font=("Arial", 16)).pack(pady=10)

        # Создаем таблицу для отображения целей
        self.goals_tree = ttk.Treeview(self.goals_page, columns=("title", "target_amount", "current_amount", "remaining"), show="headings")
        self.goals_tree.heading("title", text="Название")
        self.goals_tree.heading("target_amount", text="Цель (₽)")
        self.goals_tree.heading("current_amount", text="Текущая сумма (₽)")
        self.goals_tree.heading("remaining", text="Осталось времени")
        self.goals_tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # Кнопки для добавления и пополнения цели
        tk.Button(self.goals_page, text="Добавить цель", command=self.add_goal_window).pack(pady=10)
        tk.Button(self.goals_page, text="Пополнить цель", command=self.top_up_goal).pack(pady=10)

        # Обновляем список целей
        self.update_goals_list()  # Вставляем вызов метода для обновления списка целей

    def top_up_goal(self):
        selected_item = self.goals_tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите цель для пополнения.")
            return

        item_values = self.goals_tree.item(selected_item)['values']
        goal_id = item_values[0]  # Получаем ID выбранной цели
        current_amount = float(item_values[1])  # Текущая сумма цели

        top_up_window = tk.Toplevel(self)
        top_up_window.title("Пополнение цели")
        top_up_window.geometry("300x200")

        tk.Label(top_up_window, text="Введите сумму для пополнения:").pack(pady=10)
        amount_entry = tk.Entry(top_up_window)
        amount_entry.pack(pady=10)

        def save_top_up():
            try:
                amount = float(amount_entry.get())
                if amount <= 0:
                    raise ValueError("Сумма должна быть положительной!")

                # Проверка баланса пользователя перед пополнением
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()

                # Получаем текущий баланс пользователя
                cursor.execute('SELECT balance FROM users WHERE id = ?', (self.user[0],))
                user_balance = cursor.fetchone()[0]

                print(f"Текущий баланс: {user_balance}")  # Отладочный вывод

                # Проверяем, что тип данных баланса правильный
                if isinstance(user_balance, str):
                    user_balance = float(user_balance)  # Преобразуем в число, если это строка

                # Проверяем, хватает ли средств на балансе
                if amount > user_balance:
                    messagebox.showerror("Ошибка", f"Недостаточно средств на балансе! Баланс: {user_balance}")
                    conn.close()
                    return

                # Обновляем текущую сумму цели в базе данных
                cursor.execute('''
                    UPDATE goals SET current_amount = current_amount + ? WHERE id = ?
                ''', (amount, goal_id))
                conn.commit()

                # Обновляем баланс пользователя (сумма списывается с баланса)
                cursor.execute('''
                    UPDATE users
                    SET balance = balance - ?
                    WHERE id = ?
                ''', (amount, self.user[0]))
                conn.commit()

                conn.close()

                # Обновляем данные в интерфейсе
                self.update_balance()  # Обновляем баланс
                self.update_goals_list()  # Обновляем список целей

                messagebox.showinfo("Успех", f"Цель пополнена на {amount}₽.")
                top_up_window.destroy()

            except ValueError as e:
                messagebox.showerror("Ошибка", str(e))

        # Используем lambda, чтобы передать self в метод save_top_up
        tk.Button(top_up_window, text="Подтвердить", command=lambda: save_top_up()).pack(pady=10)

    def update_goals_list(self):
        # Очищаем таблицу
        for row in self.goals_tree.get_children():
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

        # Добавляем данные о целях в таблицу
        for goal_id, title, target_amount, current_amount, target_date in goals:
            # Вычисляем количество оставшихся дней
            remaining_days = (datetime.strptime(target_date, "%Y-%m-%d") - datetime.now()).days
            remaining_text = f"{remaining_days + 1} дн." if remaining_days >= 0 else "Срок истёк"

            # Заполняем таблицу
            if current_amount >= target_amount:
                self.goals_tree.insert(
                    "",
                    tk.END,
                    values=(title, f"{current_amount}/{target_amount}", "Цель достигнута!"),
                    tags=("completed",)
                )
                delete_button = tk.Button(self.goals_page, text="Удалить",
                                          command=lambda gid=goal_id: self.delete_completed_goal(gid))
                delete_button.pack(pady=5)
            else:
                self.goals_tree.insert(
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

        # Таблица для отображения напоминаний
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
        # Очистка текущего содержимого
        for item in self.reminders_tree.get_children():
            self.reminders_tree.delete(item)

        # Загрузка напоминаний из базы данных
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT title, date, time, description_reminder FROM reminders WHERE user_id = ?', (self.user[0],))
        for row in cursor.fetchall():
            self.reminders_tree.insert("", tk.END, values=row)
        conn.close()

    def delete_reminder(self):
        selected_item = self.reminders_tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите напоминание для удаления.")
            return

        # Получаем значения из выбранной строки
        item_values = self.reminders_tree.item(selected_item)['values']
        title = item_values[0]
        date = item_values[1]
        time = item_values[2]

        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить напоминание '{title}'?"):
            try:
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM reminders WHERE user_id=? AND title=? AND date=? AND time=?",
                               (self.user[0], title, date, time))
                conn.commit()
                conn.close()

                # Удаляем строку из Treeview
                self.reminders_tree.delete(selected_item)

                messagebox.showinfo("Успех", "Напоминание удалено.")
            except Exception as e:
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

            # Проверка на допустимость символов в названии и описании
            if not re.match(r"^[a-zA-Zа-яА-Я0-9\s\-.,!?]+$", title):
                messagebox.showerror("Ошибка", "Название содержит недопустимые символы!")
                return

            if description and not re.match(r"^[a-zA-Zа-яА-Я0-9\s\-.,!?]+$", description):
                messagebox.showerror("Ошибка", "Описание содержит недопустимые символы!")
                return

            # Сохранение данных в базу данных
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

        if not goals:
            messagebox.showinfo("Информация", "У вас нет активных целей.")
            conn.close()
            return

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

    def delete_completed_goal(self, goal_id):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Цель удалена.")
        self.update_goals_list()

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