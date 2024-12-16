import os
import sqlite3
from pfa_main import check_login, check_password, validate_date, check_goal_title, check_goal_amount, check_goal_date, check_sums_transaction_valid, check_transaction_amount_is_not_digit, check_transaction_amount_another_symbols
import pytest
import unittest

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

class Test_transaction_Checks(unittest.TestCase):
    def test_check_transaction_valid(self):
        self.assertTrue(check_sums_transaction_valid("100", testing=True))
    
    def test_check_transaction_invalid(self):
        with self.assertRaises(ValueError, msg="Сумма не может быть пустой"):
            check_sums_transaction_valid("", testing=True)
    
    def test_check_transaction_is_negative(self):
        with self.assertRaises(ValueError, msg="Сумма транзакции должна быть больше нуля"):
            check_transaction_amount_is_not_digit("-10000", testing=True)
    
    def test_check_transaction_is_not_digit(self):
        self.assertTrue(check_transaction_amount_is_not_digit("100", testing=True))

    def test_check_transaction_is_digit(self):
        with self.assertRaises(ValueError, msg="Сумма транзакции не может быть буквой"):
            check_transaction_amount_is_not_digit("abcd", testing=True)

    def test_check_transaction_amount_another_symbols(self):
        with self.assertRaises(ValueError, msg="Сумма транзакции не может включать в себя спецаильные символы"):
            check_transaction_amount_another_symbols("$", testing=True)
    
class TestGoalChecks(unittest.TestCase):
    def test_check_goal_title_valid(self):
        self.assertTrue(check_goal_title("Моя цель", testing=True))

    def test_check_goal_title_invalid(self):
        with self.assertRaises(ValueError, msg="Название цели не может быть пустым"):
            check_goal_title("", testing=True)

    def test_check_goal_amount_valid(self):
        self.assertTrue(check_goal_amount("10000", testing=True))

    def test_check_goal_amount_invalid_empty(self):
        with self.assertRaises(ValueError, msg="Сумма цели не может быть пустой"):
            check_goal_amount("", testing=True)

    def test_check_goal_amount_invalid_negative(self):
        with self.assertRaises(ValueError, msg="Сумма цели должна быть положительным числом"):
            check_goal_amount("-500", testing=True)

    def test_check_goal_date_valid(self):
        self.assertTrue(check_goal_date("2025-12-31", testing=True))

    def test_check_goal_date_invalid_format(self):
        with self.assertRaises(ValueError, msg="Некорректный формат даты! Ожидается формат ГГГГ-ММ-ДД."):
            check_goal_date("31-12-2025", testing=True)

if __name__ == "__main__":
    unittest.main()
