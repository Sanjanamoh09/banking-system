import os
import hashlib
from datetime import datetime, timedelta

# File paths
ACCOUNTS_FILE = "accounts.txt"
TRANSACTIONS_FILE = "transactions.txt"

def encrypt_password(password):
    #Encrypt the password using SHA-256.
    return hashlib.sha256(password.encode()).hexdigest()

def load_accounts():
    #Load account details from the file.
    accounts = {}
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "r") as file:
            for line in file:
                account_number, name, password, balance, locked, lock_time = line.strip().split(",")
                accounts[account_number] = {
                    "name": name,
                    "password": password,
                    "balance": float(balance),
                    "locked": locked == "True",
                    "lock_time": lock_time if lock_time else ""
                }
    return accounts

def save_account(account_number, name, password, balance, locked=False, lock_time=""):
    #Save a new account to the file.
    with open(ACCOUNTS_FILE, "a") as file:
        file.write(f"{account_number},{name},{password},{balance},{locked},{lock_time}\n")

def update_accounts_file(accounts):
    #Update the accounts file with the current state.
    with open(ACCOUNTS_FILE, "w") as file:
        for acc_num, details in accounts.items():
            file.write(f"{acc_num},{details['name']},{details['password']},{details['balance']},{details['locked']},{details['lock_time']}\n")

def log_transaction(account_number, transaction_type, amount, balance):
    #Log a transaction to the file.
    with open(TRANSACTIONS_FILE, "a") as file:
        file.write(f"{account_number},{transaction_type},{amount},{balance},{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def create_account(accounts):
    #Create a new account.
    name = input("Enter your name: ")
    initial_deposit = float(input("Enter your initial deposit: "))
    password = encrypt_password(input("Enter a password: "))
    account_number = str(len(accounts) + 1).zfill(6)  # Generate a 6-digit account number
    accounts[account_number] = {
        "name": name,
        "password": password,
        "balance": initial_deposit,
        "locked": False,
        "lock_time": ""
    }
    save_account(account_number, name, password, initial_deposit)
    print(f"Account created successfully! Your account number is: {account_number}")

def is_account_locked(account, account_number):
    #Check if an account is locked and unlock it after 5 minutes.
    if account["locked"]:
        if account["lock_time"]:
            lock_time = datetime.strptime(account["lock_time"], '%Y-%m-%d %H:%M:%S')
            time_diff = datetime.now() - lock_time
            if time_diff >= timedelta(minutes=5):
                # Unlock the account after 5 minutes
                account["locked"] = False
                account["lock_time"] = ""  # Clear the lock time
                print(f"Account {account_number} has been unlocked after 5 minutes.")
            else:
                print("Account locked due to too many failed login attempts. Please try again after 5 minutes.")
                return True
        else:
            # No lock time found, reset lock state
            account["locked"] = False
            account["lock_time"] = ""
    return False


def login(accounts):
    #Login to an account.
    account_number = input("Enter your account number: ")

    if account_number in accounts:
        account = accounts[account_number]
        
        # Check if the account is locked
        if is_account_locked(account, account_number):
            return None

        for attempt in range(3):
            password = encrypt_password(input("Enter your password: "))
            if account["password"] == password:
                print("Login successful!")
                return account_number
            else:
                print(f"Incorrect password. {2 - attempt} attempts remaining.")

        print("Account locked due to too many failed login attempts.")
        # Lock account and set lock time
        account["locked"] = True
        account["lock_time"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        update_accounts_file(accounts)
        print("Account locked due to too many failed login attempts. Check again after 5 minutes.")
        return None
    else:
        print("Account number not found.")
        return None


def deposit(accounts, account_number):
    #Deposit money into the account.
    amount = float(input("Enter amount to deposit: "))
    accounts[account_number]["balance"] += amount
    log_transaction(account_number, "Deposit", amount, accounts[account_number]["balance"])
    print(f"Deposit successful! Current balance: {accounts[account_number]['balance']}")
    update_accounts_file(accounts)

def withdraw(accounts, account_number):
    #Withdraw money from the account.
    amount = float(input("Enter amount to withdraw: "))
    if accounts[account_number]["balance"] >= amount:
        accounts[account_number]["balance"] -= amount
        log_transaction(account_number, "Withdrawal", amount, accounts[account_number]["balance"])
        print(f"Withdrawal successful! Current balance: {accounts[account_number]['balance']}")
        update_accounts_file(accounts)
    else:
        print("Insufficient balance!")

def check_balance(accounts, account_number):
    #Check the account balance.
    balance = accounts[account_number]["balance"]
    print(f"Your current balance is: {balance}")

def main():
    accounts = load_accounts()

    while True:
        print("\nWelcome to the Banking System!")
        print("1. Create Account")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            create_account(accounts)
        elif choice == "2":
            account_number = login(accounts)
            if account_number:
                while True:
                    print("\n1. Deposit")
                    print("2. Withdraw")
                    print("3. Check Balance")
                    print("4. Logout")
                    sub_choice = input("Enter your choice: ")

                    if sub_choice == "1":
                        deposit(accounts, account_number)
                    elif sub_choice == "2":
                        withdraw(accounts, account_number)
                    elif sub_choice == "3":
                        check_balance(accounts, account_number)
                    elif sub_choice == "4":
                        break
                    else:
                        print("Invalid choice! Try again.")
        elif choice == "3":
            print("Thank you for using the Banking System. Goodbye!")
            break
        else:
            print("Invalid choice! Try again.")

if __name__ == "__main__":
    main()
