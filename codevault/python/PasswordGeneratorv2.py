# Auto-generated Code Vault for 'PasswordGenerator_v2' [Python]

import string
import secrets

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
        characters = string.ascii_letters + string.digits + string.punctuation
        while True:
            self.password = ''.join(secrets.choice(characters) for _ in range(self.length))
            if (any(c.islower() for c in self.password)
                    and any(c.isupper() for c in self.password)
                    and any(c.isdigit() for c in self.password)
                    and any(c in string.punctuation for c in self.password)):
                break

    def print_password(self):
        print(f"Generated password: {self.password}")


def main():
    password_generator = PasswordGenerator()
    password_generator.get_length_from_user()
    password_generator.generate_password()
    password_generator.print_password()


if __name__ == "__main__":
    main()
