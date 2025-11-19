import random
from datetime import datetime

# Dictionary to store all clients in memory {CIN: Client}
clients = {}


# ============== Transaction Classes (Using Inheritance) ==============

class Transaction:
    # Base class for all transactions
    def __init__(self, amount):
        self.amount = amount
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def display(self):
        # To be overridden by subclasses
        pass


class Credit(Transaction):
    # Regular deposit transaction
    def display(self):
        return f"[{self.timestamp}] CREDIT: +{self.amount} DA (Deposit)"


class Debit(Transaction):
    # Regular withdrawal transaction
    def display(self):
        return f"[{self.timestamp}] DEBIT: -{self.amount} DA (Withdrawal)"


class TransferOut(Transaction):
    # Money sent to another account
    def __init__(self, amount, target_account_code):
        super().__init__(amount)
        self.target_account_code = target_account_code

    def display(self):
        return f"[{self.timestamp}] TRANSFER OUT: -{self.amount} DA → Account #{self.target_account_code}"


class TransferIn(Transaction):
    # Money received from another account
    def __init__(self, amount, source_account_code):
        super().__init__(amount)
        self.source_account_code = source_account_code

    def display(self):
        return f"[{self.timestamp}] TRANSFER IN: +{self.amount} DA ← Account #{self.source_account_code}"


class FailedTransaction(Transaction):
    # Failed transaction with reason
    def __init__(self, amount, reason, transaction_type):
        super().__init__(amount)
        self.reason = reason
        self.transaction_type = transaction_type

    def display(self):
        return f"[{self.timestamp}] FAILED {self.transaction_type}: {self.amount} DA - {self.reason}"


# ============== Client Class ==============

class Client:
    def __init__(self, firstName, lastName, tel=""):
        self.__CIN = self.generate_cin()
        self.__firstName = firstName
        self.__lastName = lastName
        self.__tel = tel
        self.__account_codes = []  # Store only account codes, not objects

    # Getters
    def get_CIN(self):
        return self.__CIN

    def get_firstName(self):
        return self.__firstName

    def get_lastName(self):
        return self.__lastName

    def get_tel(self):
        return self.__tel

    def get_account_codes(self):
        return self.__account_codes.copy()  # Return a copy to prevent external modification

    # Setters
    def set_tel(self, tel):
        self.__tel = tel

    def add_account_code(self, account_code):
        # Add account code to client's list
        if account_code not in self.__account_codes:
            self.__account_codes.append(account_code)

    def get_accounts(self):
        # Retrieve actual account objects from account codes
        return [Account.get_account_by_code(code) for code in self.__account_codes
                if Account.get_account_by_code(code) is not None]

    def display(self):
        # Display client information and all their accounts
        print(f"\n{'=' * 50}")
        print(f"CLIENT INFORMATION")
        print(f"{'=' * 50}")
        print(f"CIN: {self.__CIN}")
        print(f"Name: {self.__firstName} {self.__lastName}")
        print(f"Tel: {self.__tel if self.__tel else 'N/A'}")
        print(f"{'=' * 50}")

        accounts = self.get_accounts()
        if not accounts:
            print("No accounts yet.")
        else:
            print(f"\nTotal Accounts: {len(accounts)}")
            print("-" * 50)
            for acc in accounts:
                acc.display()
                print("-" * 50)

    @staticmethod
    def generate_cin():
        # Generate a unique CIN for each client
        while True:
            CIN = str(random.randint(100000, 999999))
            if CIN not in clients:
                return CIN


# ============== Account Class ==============

class Account:
    __nbAccounts = 0
    __all_accounts = {}  # Dictionary to store all accounts by code

    def __init__(self, owner_cin, password):
        # Validate client exists before creating account
        if owner_cin not in clients:
            raise ValueError(f"Cannot create account: Client with CIN '{owner_cin}' does not exist!")

        Account.__nbAccounts += 1
        self.__code = Account.__nbAccounts
        self.__balance = 0.0
        self.__owner_cin = owner_cin  # Store only CIN, not the object
        self.__password = password
        self.__transactions = []  # List of Transaction objects

        # Register this account
        Account.__all_accounts[self.__code] = self

        # Add this account code to the client
        owner = self.get_owner()
        owner.add_account_code(self.__code)

    # Getters
    def get_code(self):
        return self.__code

    def get_balance(self):
        return self.__balance

    def get_owner_cin(self):
        return self.__owner_cin

    def get_owner(self):
        # Retrieve the owner object from CIN
        return clients.get(self.__owner_cin)

    def check_password(self, pwd):
        return self.__password == pwd

    # Credit method
    def credit(self, amount):
        # Deposit money into account
        if amount <= 0:
            print("Amount must be positive.")
            self.__transactions.append(FailedTransaction(amount, "Invalid amount", "CREDIT"))
            return False

        self.__balance += amount
        self.__transactions.append(Credit(amount))
        print(f"Successfully credited {amount} DA. New balance: {self.__balance} DA")
        return True

    # Debit method
    def debit(self, amount):
        # Withdraw money from account
        if amount <= 0:
            print("Amount must be positive.")
            self.__transactions.append(FailedTransaction(amount, "Invalid amount", "DEBIT"))
            return False

        if self.__balance < amount:
            print("Insufficient balance.")
            self.__transactions.append(FailedTransaction(amount, "Insufficient balance", "DEBIT"))
            return False

        self.__balance -= amount
        self.__transactions.append(Debit(amount))
        print(f"Successfully debited {amount} DA. New balance: {self.__balance} DA")
        return True

    # Transfer method
    def transfer(self, amount, target_account):
        # Transfer money to another account
        if amount <= 0:
            print("Amount must be positive.")
            self.__transactions.append(FailedTransaction(amount, "Invalid amount", "TRANSFER"))
            return False

        if target_account == self:
            print("Cannot transfer to the same account.")
            self.__transactions.append(FailedTransaction(amount, "Transfer to self", "TRANSFER"))
            return False

        if self.__balance < amount:
            print("Insufficient balance.")
            self.__transactions.append(FailedTransaction(amount, "Insufficient balance", "TRANSFER"))
            return False

        # Perform transfer
        self.__balance -= amount
        target_account.__balance += amount

        # Record transactions
        self.__transactions.append(TransferOut(amount, target_account.get_code()))
        target_account.__transactions.append(TransferIn(amount, self.__code))

        print(f"Successfully transferred {amount} DA to Account #{target_account.get_code()}")
        print(f"   New balance: {self.__balance} DA")
        return True

    def display(self):
        # Display account information and transaction history
        owner = self.get_owner()
        owner_name = f"{owner.get_firstName()} {owner.get_lastName()}"

        print(f"\nAccount Code: {self.__code}")
        print(f"Owner: {owner_name} (CIN: {self.__owner_cin})")
        print(f"Balance: {self.__balance} DA")

        if self.__transactions:
            print(f"\nTransaction History ({len(self.__transactions)} transactions):")
            for transaction in self.__transactions:
                print(f"  {transaction.display()}")
        else:
            print("\nNo transactions yet.")

    @staticmethod
    def get_account_by_code(code):
        # Retrieve account by code
        return Account.__all_accounts.get(code)

    @staticmethod
    def displayNbAccounts():
        print(f"Total accounts created: {Account.__nbAccounts}")


# ============== User Interface Functions ==============

def create_account():
    print("\n" + "=" * 50)
    print("CREATE NEW ACCOUNT")
    print("=" * 50)

    cin = input("Enter your CIN (leave empty if new client): ").strip()

    client = None
    if cin:
        client = clients.get(cin)

    if client:
        print(f"Client found: {client.get_firstName()} {client.get_lastName()}")
    else:
        print("\n--- New Client Registration ---")
        first_name = input("Enter First Name: ").strip()
        last_name = input("Enter Last Name: ").strip()
        tel = input("Enter Telephone (optional): ").strip()

        if not first_name or not last_name:
            print("First name and last name are required!")
            return None

        client = Client(first_name, last_name, tel)
        clients[client.get_CIN()] = client
        print(f"New client created: {first_name} {last_name}")
        print(f"   Your CIN: {client.get_CIN()}")

    password = input("Set a password for your new account: ").strip()
    if not password:
        print("Password cannot be empty!")
        return None

    account = Account(client.get_CIN(), password)
    print(f"\nAccount created successfully!")
    print(f"   Account Code: {account.get_code()}")
    print(f"   Client CIN: {client.get_CIN()}")
    print("   Please save these credentials for login.\n")

    return account


def login():
    print("\n" + "=" * 50)
    print("LOGIN")
    print("=" * 50)

    cin = input("Enter your CIN: ").strip()

    try:
        acc_code = int(input("Enter your Account Code: "))
    except ValueError:
        print("Account Code must be a number!")
        return None

    password = input("Enter your account password: ").strip()

    if not cin or not password:
        print("All fields are required!")
        return None

    # Find client
    client = clients.get(cin)

    if not client:
        print("CIN not found!")
        return None

    # Find account
    account = Account.get_account_by_code(acc_code)
    if not account:
        print("Account not found!")
        return None

    # Check if account belongs to client
    if account.get_owner_cin() != cin:
        print("This account does not belong to you!")
        return None

    # Check password
    if not account.check_password(password):
        print("Incorrect password!")
        return None

    print(f"\nWelcome back, {client.get_firstName()}!\n")
    return account


def client_menu(acc):
    client = acc.get_owner()

    while True:
        print("\n" + "=" * 50)
        print("CLIENT MENU")
        print("=" * 50)
        print("1. Display my information & all accounts")
        print("2. Deposit money (Credit)")
        print("3. Withdraw money (Debit)")
        print("4. Transfer to another account")
        print("5. View transaction history")
        print("6. Logout")
        print("=" * 50)

        option = input("Choose an option: ").strip()

        if option == "1":
            client.display()

        elif option == "2":
            try:
                amount = int(input("Enter amount to deposit: "))
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

            # Find target account
            target_acc = Account.get_account_by_code(target_code)

            if not target_acc:
                print("Target account not found!")
                continue

            # Verify target account belongs to the specified CIN
            if target_acc.get_owner_cin() != target_cin:
                print("Account does not belong to the specified CIN!")
                continue

            try:
                amount = int(input("Enter amount to transfer: "))
                acc.transfer(amount, target_acc)
            except ValueError:
                print("Invalid amount! Please enter an integer.")

        elif option == "5":
            print("\n" + "=" * 50)
            print("TRANSACTION HISTORY")
            print("=" * 50)
            acc.display()

        elif option == "6":
            print("\nLogged out successfully.")
            break

        else:
            print("Invalid option!")


# ============== Main Program ==============

def main():
    print("\n" + "=" * 50)
    print("WELCOME TO BANK MANAGEMENT SYSTEM")
    print("=" * 50)

    while True:
        print("\n--- Main Menu ---")
        print("1. Create Account")
        print("2. Log In")
        print("3. Display Total Accounts")
        print("4. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            account = create_account()
            if account:
                client_menu(account)

        elif choice == "2":
            account = login()
            if account:
                client_menu(account)

        elif choice == "3":
            Account.displayNbAccounts()

        elif choice == "4":
            print("\nThank you for using our bank system. Goodbye!")
            break

        else:
            print("Invalid choice!")

main()