# Auto-generated Code Vault for 'TextRPG' [Python]

import random
import time

class Player:
    def __init__(self):
        self.hp = 100
        self.weapon = "Basic Sword"
        self.gold = 0

    def is_alive(self):
        return self.hp > 0

    def __str__(self):
        return f"HP: {self.hp}, Weapon: {self.weapon}, Gold: {self.gold}"

class Enemy:
    def __init__(self, name, hp):
        self.name = name
        self.hp = hp

    def is_alive(self):
        return self.hp > 0

    def __str__(self):
        return f"{self.name} - HP: {self.hp}"

def print_colorful(text, color_code):
    print(f"\033[{color_code}m{text}\033[0m")

def roll_dice(sides):
    return random.randint(1, sides)

def combat(player, enemy):
    while player.is_alive() and enemy.is_alive():
        print_colorful(f"\n{player}", 32)
        print_colorful(f"{enemy}", 31)
        action = input("What do you want to do? (A)ttack or (R)un: ")
        if action.lower() == "a":
            player_roll = roll_dice(6)
            enemy_roll = roll_dice(6)
            print_colorful(f"\nYou rolled a {player_roll}", 32)
            print_colorful(f"{enemy.name} rolled a {enemy_roll}", 31)
            if player_roll > enemy_roll:
                damage = player_roll - enemy_roll
                enemy.hp -= damage
                print_colorful(f"You hit {enemy.name} for {damage} damage!", 32)
            elif player_roll < enemy_roll:
                damage = enemy_roll - player_roll
                player.hp -= damage
                print_colorful(f"{enemy.name} hit you for {damage} damage!", 31)
            else:
                print_colorful("It's a tie!", 33)
        elif action.lower() == "r":
            print_colorful("You ran away!", 33)
            break
        else:
            print_colorful("Invalid action!", 31)
        time.sleep(1)
    if not player.is_alive():
        print_colorful("You died! Game over.", 31)
    elif not enemy.is_alive():
        print_colorful(f"You killed {enemy.name}! You earned 10 gold.", 32)
        player.gold += 10

def game_loop():
    player = Player()
    while True:
        print_colorful("\nTextRPG", 34)
        print_colorful("---------", 34)
        print_colorful("1. Explore", 32)
        print_colorful("2. Check Stats", 33)
        print_colorful("3. Quit", 31)
        choice = input("What do you want to do? ")
        if choice == "1":
            encounter = random.randint(1, 2)
            if encounter == 1:
                enemy = Enemy("Goblin", 20)
                print_colorful(f"\nYou encountered a {enemy.name}!", 31)
                combat(player, enemy)
            elif encounter == 2:
                treasure = random.randint(1, 10)
                print_colorful(f"\nYou found a treasure chest with {treasure} gold!", 32)
                player.gold += treasure
        elif choice == "2":
            print_colorful(f"\n{player}", 32)
        elif choice == "3":
            print_colorful("Goodbye!", 33)
            break
        else:
            print_colorful("Invalid choice!", 31)
        time.sleep(1)

if __name__ == "__main__":
    game_loop()
