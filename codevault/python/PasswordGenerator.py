# Auto-generated Code Vault for 'PasswordGenerator' [Python]

import random
import string

class PasswordGenerator:
    def __init__(self):
        self.length = 0
        self.password = ""

    def get_length_from_user(self):
        while True:
            try:
                self.length = int(input("Enter the length of the password: "))
                if self.length < 8:
                    print("Password length should be at least 8 characters.")
                else:
                    break
            except ValueError:
                print("Invalid input. Please enter a number.")

    def generate_password(self):
        all_characters = string.ascii_letters + string.digits + string.punctuation
        if self.length < 8:
            print("Password length should be at least 8 characters.")
            return
        self.password = ''.join(random.choice(all_characters) for i in range(self.length))
        return self.password

    def print_password(self):
        print(f"Generated Password : {self.password}")

def main():
    password_generator = PasswordGenerator()
    password_generator.get_length_from_user()
    password_generator.generate_password()
    password_generator.print_password()

if __name__ == "__main__":
    main()
