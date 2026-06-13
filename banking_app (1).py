import hashlib
import uuid
from datetime import datetime


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def generate_account_number():
    return str(uuid.uuid4().int)[:10]


# ─── In-memory "database" ───────────────────────────────────────────────────
users = {}       # { account_number: user_dict }
sessions = {}    # { account_number: bool } — tracks logged-in user


def get_logged_in_user():
    for acc, logged_in in sessions.items():
        if logged_in:
            return users[acc]
    return None


# ─── Auth ────────────────────────────────────────────────────────────────────
def register():
    print("\n─── Create Account ───")
    name = input("Full name: ").strip()
    if not name:
        print("❌ Name cannot be empty.")
        return

    password = input("Password: ").strip()
    if len(password) < 4:
        print("❌ Password must be at least 4 characters.")
        return

    confirm = input("Confirm password: ").strip()
    if password != confirm:
        print("❌ Passwords do not match.")
        return

    account_number = generate_account_number()
    users[account_number] = {
        "name": name,
        "account_number": account_number,
        "password": hash_password(password),
        "balance": 0.0,
        "transactions": []
    }

    print(f"\n✅ Account created successfully!")
    print(f"   Your account number: {account_number}")
    print("   Keep this safe — you'll need it to log in.")


def login():
    print("\n─── Login ───")
    account_number = input("Account number: ").strip()
    password = input("Password: ").strip()

    user = users.get(account_number)
    if not user or user["password"] != hash_password(password):
        print("❌ Invalid account number or password.")
        return

    # Clear any existing sessions
    sessions.clear()
    sessions[account_number] = True
    print(f"\n✅ Welcome back, {user['name']}!")


def logout():
    user = get_logged_in_user()
    if user:
        sessions.clear()
        print(f"\n👋 Logged out. Goodbye, {user['name']}!")


# ─── Transactions ────────────────────────────────────────────────────────────
def log_transaction(user, t_type, amount, note=""):
    user["transactions"].append({
        "type": t_type,
        "amount": amount,
        "note": note,
        "balance_after": user["balance"],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


def deposit():
    user = get_logged_in_user()
    print("\n─── Deposit ───")
    try:
        amount = float(input("Amount to deposit: ₦"))
    except ValueError:
        print("❌ Invalid amount.")
        return

    if amount <= 0:
        print("❌ Amount must be greater than zero.")
        return

    user["balance"] += amount
    log_transaction(user, "Deposit", amount)
    print(f"✅ ₦{amount:,.2f} deposited. New balance: ₦{user['balance']:,.2f}")


def withdraw():
    user = get_logged_in_user()
    print("\n─── Withdrawal ───")
    try:
        amount = float(input("Amount to withdraw: ₦"))
    except ValueError:
        print("❌ Invalid amount.")
        return

    if amount <= 0:
        print("❌ Amount must be greater than zero.")
        return

    if amount > user["balance"]:
        print(f"❌ Insufficient funds. Your balance is ₦{user['balance']:,.2f}")
        return

    user["balance"] -= amount
    log_transaction(user, "Withdrawal", amount)
    print(f"✅ ₦{amount:,.2f} withdrawn. New balance: ₦{user['balance']:,.2f}")


def transfer():
    user = get_logged_in_user()
    print("\n─── Transfer ───")
    recipient_acc = input("Recipient account number: ").strip()

    if recipient_acc == user["account_number"]:
        print("❌ You cannot transfer to your own account.")
        return

    recipient = users.get(recipient_acc)
    if not recipient:
        print("❌ Recipient account not found.")
        return

    try:
        amount = float(input(f"Amount to transfer to {recipient['name']}: ₦"))
    except ValueError:
        print("❌ Invalid amount.")
        return

    if amount <= 0:
        print("❌ Amount must be greater than zero.")
        return

    if amount > user["balance"]:
        print(f"❌ Insufficient funds. Your balance is ₦{user['balance']:,.2f}")
        return

    user["balance"] -= amount
    recipient["balance"] += amount

    log_transaction(user, "Transfer Out", amount, note=f"To {recipient['name']} ({recipient_acc})")
    log_transaction(recipient, "Transfer In", amount, note=f"From {user['name']} ({user['account_number']})")

    print(f"✅ ₦{amount:,.2f} transferred to {recipient['name']}. New balance: ₦{user['balance']:,.2f}")


def change_password():
    user = get_logged_in_user()
    print("\n─── Change Password ───")
    current = input("Current password: ").strip()

    if user["password"] != hash_password(current):
        print("❌ Incorrect current password.")
        return

    new_password = input("New password: ").strip()
    if len(new_password) < 4:
        print("❌ Password must be at least 4 characters.")
        return

    confirm = input("Confirm new password: ").strip()
    if new_password != confirm:
        print("❌ Passwords do not match.")
        return

    user["password"] = hash_password(new_password)
    print("✅ Password changed successfully.")


def transaction_history():
    user = get_logged_in_user()
    print("\n─── Transaction History ───")

    if not user["transactions"]:
        print("No transactions yet.")
        return

    print(f"{'#':<4} {'Date':<20} {'Type':<15} {'Amount':>12} {'Balance After':>14} {'Note'}")
    print("─" * 80)

    for i, t in enumerate(user["transactions"], 1):
        note = t.get("note", "")
        print(f"{i:<4} {t['date']:<20} {t['type']:<15} ₦{t['amount']:>10,.2f} ₦{t['balance_after']:>12,.2f}  {note}")


def check_balance():
    user = get_logged_in_user()
    print(f"\n💰 Current Balance: ₦{user['balance']:,.2f}")


# ─── Menus ───────────────────────────────────────────────────────────────────
def dashboard_menu():
    user = get_logged_in_user()
    while user:
        print(f"\n═══ Dashboard — {user['name']} (Acc: {user['account_number']}) ═══")
        print("  1. Check Balance")
        print("  2. Deposit")
        print("  3. Withdraw")
        print("  4. Transfer")
        print("  5. Transaction History")
        print("  6. Change Password")
        print("  7. Logout")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            check_balance()
        elif choice == "2":
            deposit()
        elif choice == "3":
            withdraw()
        elif choice == "4":
            transfer()
        elif choice == "5":
            transaction_history()
        elif choice == "6":
            change_password()
        elif choice == "7":
            logout()
            break
        else:
            print("❌ Invalid option. Please choose 1–7.")

        user = get_logged_in_user()


def main_menu():
    print("\n╔══════════════════════════════╗")
    print("║      🏦 BANK OF NIGERIA      ║")
    print("╚══════════════════════════════╝")

    while True:
        print("\n  1. Create Account")
        print("  2. Login")
        print("  3. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            register()
        elif choice == "2":
            login()
            if get_logged_in_user():
                dashboard_menu()
        elif choice == "3":
            print("\n👋 Thanks for using Hustla Bank. Bye!\n")
            break
        else:
            print("❌ Invalid option. Please choose 1–3.")


if __name__ == "__main__":
    main_menu()
