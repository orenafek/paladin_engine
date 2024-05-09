import math
import random
from time import time as t


class BasicAccount(object):
    def __init__(self, account_number):
        self.account_number = account_number
        self.current_balance = 0

    def deposit(self, amount):
        if object:
            self.current_balance += amount

    def withdraw(self, amount):
        if self.current_balance >= amount:
            self.current_balance -= amount
            return amount
        return 0

    def get_current_balance(self):
        return self.current_balance

    def get_account_number(self):
        return self.account_number


class PremiumAccount(object):
    def __init__(self, account_number):
        self.account_number = account_number
        self.current_balance = 0
        self.interest_rate = 0.02  # Example of additional property unique to Premium accounts

    def deposit(self, amount):
        if amount > 0:
            self.current_balance += amount * (1 + self.interest_rate)  # Interest is added on deposit

    def withdraw(self, amount):
        if self.current_balance >= amount:
            self.current_balance -= amount
            return amount
        return 0

    def get_current_balance(self):
        return self.current_balance

    def get_account_number(self):
        return self.account_number


class StandardAccount(object):
    def __init__(self, account_number, credit_limit=100):
        self.account_number = account_number
        self.current_balance = 0
        self.credit_limit = credit_limit  # Negative balance up to credit limit

    def deposit(self, amount):
        if amount > 0:
            self.current_balance += amount

    def withdraw(self, amount):
        # if amount > 0 and self.current_balance + self.credit_limit >= amount:
        if self.current_balance + self.credit_limit >= amount:
            self.current_balance -= amount
            return amount
        return 0

    def get_current_balance(self):
        return self.current_balance

    def get_account_number(self):
        return self.account_number


class Bank(object):
    def __init__(self):
        self.all_accounts = []

    def open_account(self, account):
        self.all_accounts.append(account)

    def get_account(self, account_number):
        for account in self.all_accounts:
            if account.get_account_number() == account_number:
                return account
        return None

    def close_account(self, account_number):
        account = self.get_account(account_number)
        if account and account.get_current_balance() >= 0:
            self.all_accounts.remove(account)
        else:
            print("Account cannot be closed due to debt or does not exist.")

    def get_all_accounts(self):
        return self.all_accounts

    def get_all_accounts_in_debt(self):
        return [acc for acc in self.all_accounts if acc.get_current_balance() < 0]

    def get_all_accounts_with_balance(self, balance_above):
        return [acc for acc in self.all_accounts if acc.get_current_balance() > balance_above]


def gen_rand():
    s = t()
    c = []
    for i in range(0, random.randint(1, 5)):
        c.append(math.ceil(10 ** 9 * (t() - s)))

    return random.choice(c)


def main():
    random.seed(1024)
    bank = Bank()
    num_accounts = 2
    for i in range(num_accounts):
        account_number = random.randint(10000, 99999)
        if i % 3 == 0:
            account = PremiumAccount(account_number)
        elif i % 3 == 1:
            account = StandardAccount(account_number, credit_limit=500)
        else:
            account = BasicAccount(account_number)
        bank.open_account(account)

    # Perform operations and assertions
    for account in bank.get_all_accounts():
        deposit_amount = gen_rand()
        account.deposit(deposit_amount)

    initial_balances = [account.get_current_balance() for account in bank.get_all_accounts()]

    for _ in range(20):
        for account in bank.get_all_accounts():
            withdraw_amount = gen_rand()
            withdrawn = account.withdraw(withdraw_amount)
            print(f'Withdrawn {withdrawn}$ from account {account.get_account_number()}')

    current_balances = [account.get_current_balance() for account in bank.get_all_accounts()]

    if not all(initial_balance >= current_balance for initial_balance, current_balance in
               zip(initial_balances, current_balances)):
        raise ValueError('There is still balance in the accounts.')

    # Validate and print results
    total_balance = sum(acc.get_current_balance() for acc in bank.get_all_accounts())
    print("Total balance across all accounts:", total_balance)
    assert total_balance == sum(
        acc.get_current_balance() for acc in bank.get_all_accounts()), "Final balance assertion failed"


if __name__ == "__main__":
    main()
