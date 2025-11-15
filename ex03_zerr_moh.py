import random
# List to store all clients in memory
clients = []
# Class Client
class Client:
    def __init__(self, firstName, lastName, tel=""):
        self.__CIN = self.generate_cin()# Each client has a unique CIN (ID)
        self.__firstName = firstName
        self.__lastName = lastName
        self.__tel = tel
        self.__accounts = []# List of accounts for this client

        # Getters and setters for all attributes
    def get_CIN(self): return self.__CIN
    def get_firstName(self): return self.__firstName
    def get_lastName(self): return self.__lastName
    def get_tel(self): return self.__tel
    def get_accounts(self):return self.__accounts

    def set_tel(self, tel): self.__tel = tel

    def add_account(self, account):# Add account to this client
        self.__accounts.append(account)
    def display(self): # Display client information and their accounts
        print(f"CIN: {self.__CIN}, Name: {self.__firstName} {self.__lastName}, Tel: {self.__tel}")
        if not self.__accounts:
            print("No accounts yet.")
        else:
            print("Accounts:")
            for acc in self.__accounts:
                acc.display()
                print("-" * 30)
    @staticmethod
    def generate_cin(): # Generate a unique CIN for each client
        while True:
            CIN = str(random.randint(100000, 999999))
            if all(client.get_CIN() != CIN for client in clients):
                return CIN

# Class Account
class Account:
    __nbAccounts = 0  # static variable for sequential codes

    def __init__(self, owner, password):
        Account.__nbAccounts += 1
        self.__code = Account.__nbAccounts
        self.__balance = 0.0
        self.__owner = owner
        self.__password = password
        self.__transactions = []# Stores transaction history
        owner.add_account(self) # Add this account to the client's account list

    # Access methods
    def get_code(self): return self.__code
    def get_balance(self): return self.__balance
    def get_owner(self): return self.__owner
    def check_password(self, pwd):
        return self.__password == pwd

    # Credit and debit methods
    def credit(self, amount, account=None):
        if amount <= 0: # Input validation: amount must be positive
            print("Amount must be positive.")
            self.__transactions.append(f"Failed credit attempt of {amount} DA (invalid amount)")
            return
        if account is None:# Regular deposit
            self.__balance += amount
            self.__transactions.append(f"Credited {amount} DA")
        else:# If coming from another account (transfer)
            self.__balance += amount
            account.debit(amount)
            self.__transactions.append(f"Received {amount} DA from Account {account.get_code()}")

    def debit(self, amount, account=None):
        if amount <= 0:
            print("Amount must be positive.")
            self.__transactions.append(f"Failed debit attempt of {amount} DA (invalid amount)")
            return
        if self.__balance < amount:# Check for sufficient balance
            print("Insufficient balance.")
            self.__transactions.append(f"Failed debit attempt of {amount} DA (insufficient balance)")
            return
        else:
            self.__balance -= amount
            if account is not None:# Transfer to another account
                if account == self:#Cannot transfer to the same account so we return the amount back
                   self.__balance += amount
                   print("Cannot transfer to the same account.")
                   self.__transactions.append(f"Failed transfer attempt of {amount} DA to self")
                else:
                   account.credit(amount)
                   self.__transactions.append(f"Transferred {amount} DA to Account {account.get_code()}")
            else:# Regular withdrawal
                self.__transactions.append(f"Debited {amount} DA")
    def display(self):# Record all operations (credit, debit, transfer)
        print(f"Account Code: {self.__code}")
        print(f"Owner: {self.__owner.get_firstName()} {self.__owner.get_lastName()}")
        print(f"Balance: {self.__balance} DA")
        if self.__transactions:
            print("Transaction History:")
            for t in self.__transactions:
                print("-", t)
        else:
            print("No transactions yet.")

    @staticmethod
    def displayNbAccounts():
        print("Total accounts created:", Account.__nbAccounts)
def create_account():
    print("=== Sign Up / Create Account ===")
    cin = input("Enter your CIN (leave empty if new client): ").strip()

    client = None
    if cin:
        for c in clients:
            if c.get_CIN() == cin:
                client = c
                break

    if client:
        print(f"Client found: {client.get_firstName()} {client.get_lastName()}")
    else: # Create new client
        first_name = input("Enter First Name: ").strip()
        last_name = input("Enter Last Name: ").strip()
        tel = input("Enter Telephone (optional): ").strip()
        client = Client(first_name, last_name, tel)
        clients.append(client)
        print(f"New client created: {first_name} {last_name}")

    password = input("Set a password for your new account: ")# Set password for the new account
    account = Account(client, password)
    print(f"Account created successfully! Account Code: {account.get_code()}")
    print(f"Client CIN: {client.get_CIN()}\n")
    return account
def login():
    print("=== Log In ===")
    cin = input("Enter your CIN: ")
    try:
        acc_code = int(input("Enter your Account Code: "))
    except ValueError:
        print("Account Code must be a number!")
        return None
    password = input("Enter your account password: ")
    if not cin or not acc_code or not password:
        print("All fields are required!")
        return None

    for client in clients:# Search for client and matching account
        if client.get_CIN() == cin:
            for account in client.get_accounts():
                if account.get_code() == acc_code and account.check_password(password):
                    print(f"Welcome back, {client.get_firstName()}!\n")
                    return account
            print("Account code or password incorrect!")
            return None
    print("CIN not found!")
    return None
def client_menu(acc):
    client = acc.get_owner()
    while True:
        print("\n--- Client Menu ---")
        print("1. Display client info")
        print("2. Credit account (Deposit)")
        print("3. Withdraw from account")
        print("4. Transfer to another account")
        print("5. Logout")
        option = input("Choose an option: ").strip()

        if option == "1":
            client.display()
        elif option == "2":
            try:
                amount = int(input("Enter amount to deposit: "))  # فقط أعداد صحيحة
                acc.credit(amount)
            except ValueError:
                print("Invalid amount! Please enter an integer.")
        elif option == "3":
            try:
                amount = int(input("Enter amount to withdraw: "))
                acc.debit(amount)
            except ValueError:
                print("Invalid amount! Please enter an integer.")
        elif option == "4":
                target_cin = input("Enter target client's CIN: ").strip()
                try:
                    target_code = int(input("Enter target Account Code: "))
                except ValueError:
                    print("Account Code must be a number!")
                    continue

                target_acc = None
                for c in clients:
                    if c.get_CIN() == target_cin:
                        for a in c.get_accounts():
                            if a.get_code() == target_code:
                                target_acc = a
                                break
                        break
                if target_acc:
                    try:
                        amount = int(input("Enter amount to transfer: "))
                        acc.debit(amount, target_acc)
                    except ValueError:
                        print("Invalid amount! Please enter an integer.")
                else:
                    print("Target account not found!")
        elif option == "5":
            print("Logged out.")
            break
        else:
            print("Invalid option!")

while True:
    print("1. Create Account")
    print("2. Log In")
    print("3. Exit")
    choice = input("Choose an option: ")

    if choice == "1":
        accoun = create_account()
        client_menu(accoun)

    elif choice == "2":
        accoun = login()
        if accoun:
            client_menu(accoun)

    elif choice == "3":
        break
    else:
        print("Invalid choice.")
