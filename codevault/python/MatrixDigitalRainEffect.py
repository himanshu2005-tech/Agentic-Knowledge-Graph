# Auto-generated Code Vault for 'MatrixDigitalRainEffect' [Python]

import random
import time
import os
from colorama import init, Fore, Back, Style

init()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def matrix_digital_rain_effect():
    clear_screen()
    columns = os.get_terminal_size().columns
    lines = os.get_terminal_size().lines
    rain = [[' ' for _ in range(columns)] for _ in range(lines)]

    while True:
        clear_screen()
        for y, row in enumerate(rain):
            for x, char in enumerate(row):
                if random.random() < 0.05:
                    rain[y][x] = random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                elif y < lines - 1:
                    rain[y][x] = rain[y + 1][x]
                else:
                    rain[y][x] = ' '
        for y, row in enumerate(rain):
            for x, char in enumerate(row):
                if char != ' ':
                    print(f"{Back.BLACK}{Fore.GREEN}{char}", end='')
                else:
                    print(f"{Back.BLACK}{Fore.BLACK} ", end='')
            print()
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        matrix_digital_rain_effect()
    except KeyboardInterrupt:
        print(f"{Style.RESET_ALL}")
