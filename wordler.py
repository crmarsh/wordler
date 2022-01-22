#!/usr/bin/env python3

import sys

from wordler_solver import *
from word_lists import possible_answers, acceptable_guesses


CSI = "\033["
OSC = "\033]"
BEL = "\a"
FORMAT_CODE = "m"

GREEN_RGB = (83, 141, 78)
YELLOW_RGB = (181, 159, 59)
GREY_RGB = (58, 58, 60)
LTGREY_RGB = (215, 218, 220)


def clear_screen():
    sys.stdout.write(f"{CSI}2J")


def set_fg_color(rgb):
    r, g, b = rgb
    sys.stdout.write(f"{CSI}38;2;{r};{g};{b}m")


def clear_color():
    sys.stdout.write(f"{CSI}0m")


def set_bg_color(rgb):
    r, g, b = rgb
    sys.stdout.write(f"{CSI}48;2;{r};{g};{b}m")


def print_guess(guesser: Guesser, guess: str):
    bg_colors = []
    letters = []
    for i, letter in enumerate(guesser.letters):
        if letter.is_correct():
            bg_colors.append(GREEN_RGB)
            letters.append(letter.letter.upper())
        elif letter.is_misplaced():
            bg_colors.append(YELLOW_RGB)
            letters.append(letter.letter.upper())
        else:
            bg_colors.append(GREY_RGB)
            letters.append(guess[i].upper())

    print()

    for i in range(5):
        set_bg_color(bg_colors[i])
        print("   ", end="")

        clear_color()
        print(" ", end="")

    print()

    for i in range(5):
        set_bg_color(bg_colors[i])
        set_fg_color(LTGREY_RGB)
        print(f" {letters[i]} ", end="")

        clear_color()
        print(" ", end="")

    print()

    for i in range(5):
        set_bg_color(bg_colors[i])
        print("   ", end="")

        clear_color()
        print(" ", end="")

    print("\n")


def game():
    import random

    real_word = random.choice(list(possible_answers))
    guess_number = 0
    possible = possible_answers
    guesser = Guesser(None)
    while guess_number < 6:
        clear_color()
        next_guess = None
        while next_guess not in acceptable_guesses:
            next_guess = input("guess: ")
        guess_number += 1
        correct = apply_guess(real_word, guesser, next_guess)
        print_guess(guesser, next_guess)
        if correct:
            print("you got it!")
            return
        else:
            possible = guesser.filter_set(possible)
            # print(f"There are {len(possible)} possibles left")

    set_bg_color((18, 18, 19))
    set_fg_color((241, 11, 4))
    print(f"Nope, it was {real_word}")


if __name__ == "__main__":
    clear_screen()

    set_bg_color((18, 18, 19))
    set_fg_color(LTGREY_RGB)
    print(" W O R D L E \n")

    # guesser = Guesser(None)
    # apply_guess("prick", guesser, "crimp")
    # print_guess(guesser, "crimp")
    game()

    clear_color()
