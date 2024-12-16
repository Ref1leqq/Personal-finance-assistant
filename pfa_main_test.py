import os
import sqlite3
from pfa_main import check_login, check_password, validate_date, check_sum_goal_entry
import pytest

def test_check_login():
    assert (check_login('Pavel') == True)

def test_check_login_negative():
    with pytest.raises(ValueError):
        check_login('Pb')

def test_check_password():
    assert (check_password('abcdefgh') == True)

def test_check_password_negative():
    with pytest.raises(ValueError):
        check_password('123')

def test_validate_date():
    assert (validate_date("2024-12-28") == True)

def test_validate_date_negative():
    with pytest.raises(ValueError):
        validate_date("2023-12-12")

def test_check_sum_goal_entry():
    assert (check_sum_goal_entry('100') == True)

def test_check_sum_goal_entry_negative():
    with pytest.raises(ValueError):
        check_sum_goal_entry("-100")

@pytest.fixture(scope="module")
def test_db():
    # Создаем тестовую базу данных
    test_db_path = 'test_users.db'
    conn = sqlite3.connect(test_db_path)
    # Обновляем путь в create_db
    def create_test_db():
        conn_test = sqlite3.connect(test_db_path)
        cursor = conn_test.cursor()

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

        conn_test.commit()
        conn_test.close()

    create_test_db()  # Инициализируем таблицы для тестов
    yield conn  # Передаем соединение для тестов
    conn.close()
    os.remove(test_db_path)  # Удаляем тестовую базу данных после тестов

@pytest.fixture()
def db_cursor(test_db):
    return test_db.cursor()

# Положительные тесты
def test_add_transaction_positive(db_cursor):
    user_id = 1
    db_cursor.execute("INSERT INTO users (login, password) VALUES (?, ?)", ("test_user", "password"))
    db_cursor.execute("INSERT INTO transactions (user_id, category, amount, date, type) VALUES (?, ?, ?, ?, ?)",
                      (user_id, "Food", 100.0, "2024-01-01", "Expense"))
    db_cursor.connection.commit()

    db_cursor.execute("SELECT category, amount, type FROM transactions WHERE user_id=?", (user_id,))
    result = db_cursor.fetchone()
    assert result == ("Food", 100.0, "Expense")

def test_balance_calculation_positive(db_cursor):
    user_id = 1
    db_cursor.execute("INSERT INTO transactions (user_id, category, amount, date, type) VALUES (?, ?, ?, ?, ?)",
                      (user_id, "Salary", 1000.0, "2024-01-02", "Income"))
    db_cursor.connection.commit()

    db_cursor.execute('''
        SELECT SUM(CASE WHEN type = "Income" THEN amount ELSE 0 END) as total_income,
               SUM(CASE WHEN type = "Expense" THEN amount ELSE 0 END) as total_expense
        FROM transactions
        WHERE user_id = ?
    ''', (user_id,))
    total_income, total_expense = db_cursor.fetchone()
    current_balance = total_income - total_expense

    assert total_income == 1000.0
    assert total_expense == 100.0
    assert current_balance == 900.0

def test_delete_transaction_positive(db_cursor):
    user_id = 1
    db_cursor.execute("DELETE FROM transactions WHERE user_id=?", (user_id,))
    db_cursor.connection.commit()

    db_cursor.execute("SELECT COUNT(*) FROM transactions WHERE user_id=?", (user_id,))
    count = db_cursor.fetchone()[0]
    assert count == 0

# Отрицательные тесты

def test_add_transaction_negative(db_cursor):
    with pytest.raises(sqlite3.IntegrityError):
        db_cursor.execute("INSERT INTO transactions (user_id, category, amount, date, type) VALUES (?, ?, ?, ?, ?)",
                          (None, "Food", 100.0, "2024-01-01", "Expense"))

def test_balance_calculation_negative(db_cursor):
    user_id = 1
    db_cursor.execute("INSERT INTO transactions (user_id, category, amount, date, type) VALUES (?, ?, ?, ?, ?)",
                      (user_id, "Invalid", -300.0, "2024-01-04", "Income"))
    db_cursor.connection.commit()

    db_cursor.execute('''
        SELECT SUM(CASE WHEN type = "Income" THEN amount ELSE 0 END) as total_income,
               SUM(CASE WHEN type = "Expense" THEN amount ELSE 0 END) as total_expense
        FROM transactions
        WHERE user_id = ?
    ''', (user_id,))
    total_income, total_expense = db_cursor.fetchone()
    current_balance = total_income - total_expense

    assert total_income != 1000.0  # Проверка на неверный итоговый доход
    assert total_expense == 0.0  # Расходов быть не должно
    assert current_balance != 700.0  # Неверный баланс

def test_delete_transaction_negative(db_cursor):
    with pytest.raises(sqlite3.OperationalError):
        db_cursor.execute("DELETE FROM non_existent_table WHERE id=?", (1,))