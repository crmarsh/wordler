#!/usr/bin/env python3

import sys
import collections
from enum import Enum

from word_lists import possible_answers, acceptable_guesses


## not quite working:
# guesses with 3 letters the same are broken, eg:
# racer ends up guessing rarer then getting stuck

"""
fails on delve
The answer is billy in 7 guesses
The answer is catch in 8 guesses
The answer is tatty in 7 guesses
The answer is boxer in 8 guesses
The answer is foyer in 7 guesses
The answer is found in 7 guesses
The answer is taste in 7 guesses
The answer is bound in 8 guesses
The answer is fight in 7 guesses
fails on racer
The answer is shade in 7 guesses
The answer is hatch in 7 guesses
The answer is purer in 7 guesses
The answer is daunt in 7 guesses

Counter({4: 974, 3: 905, 5: 233, 2: 146, 6: 41, 7: 10, 8: 3, 1: 1})
fails: {'racer', 'delve'}
./wordler.py  332.96s user 2.80s system 98% cpu 5:40.71 total

"""


def is_letter(c):
    if c is None or len(c) != 1:
        return False
    return ord("a") <= ord(c) <= ord("z")


def print_counter(c: collections.Counter) -> None:
    arr = sorted([(k, c[k]) for k in c])
    for thing in arr:
        guesses, count = thing
        print(f"{guesses}: {count}")


class GuessState(Enum):
    Empty = 0
    Correct = 1
    Misplaced = 2


class GuessLetter(object):
    def __init__(self, guess=None):
        if is_letter(guess):
            self.letter = guess
            self.state = GuessState.Correct
        else:
            self.letter = "."
            self.state = GuessState.Empty
        self.exclusions = set()

    def __str__(self):
        if self.state == GuessState.Empty:
            return "[ ]"
        elif self.state == GuessState.Correct:
            return f"({self.letter})"
        elif self.state == GuessState.Misplaced:
            return f"<{self.letter}>"

    def is_correct(self):
        return self.state == GuessState.Correct

    def set_correct(self, letter):
        self.letter = letter
        self.state = GuessState.Correct

    def is_misplaced(self):
        return self.state == GuessState.Misplaced

    def set_misplaced(self, letter):
        self.letter = letter
        self.state = GuessState.Misplaced
        self.exclusions.add(letter)

    def clear_guess(self):
        self.letter = "."
        self.state = GuessState.Empty

    def matches(self, letter: str) -> bool:
        if self.is_correct():
            return letter == self.letter
        return letter not in self.exclusions


class Guesser(object):
    def __init__(self, word=None):
        self.exclusions = set()  # known not letters
        self.inclusions = set()  # known letters, not known locations
        if word and len(word) == 5:
            self.letters = [GuessLetter(c) for c in word]
        else:
            self.letters = [GuessLetter() for _ in range(5)]

    def __str__(self):
        base = "".join([str(x) for x in self.letters])
        if self.exclusions:
            return base + f" [exc: {self.exclusions}]"
        return base

    def matches(self, word: str):
        for need in self.inclusions:
            if not need in word:
                return False
        for i, letter in enumerate(word):
            if letter in self.exclusions:
                return False
            if not self.letters[i].matches(letter):
                return False
            if (letter in word[:i] or letter in word[i + 1 :]) and (
                "2" + letter
            ) in self.exclusions:
                return False
        return True

    def filter_set(self, word_set):
        result = set()
        for word in word_set:
            if self.matches(word):
                result.add(word)
        return result

    def stats_set(self, word_set):
        counters = [collections.Counter() for _ in range(6)]
        any_letter = counters[5]
        for i, letter in enumerate(self.letters):
            counter = counters[i]
            if letter.is_correct():
                counter.update([letter.letter])
                continue
            for word in word_set:
                c = word[i]
                if c in word[:i]:
                    c = "2" + c
                counter.update([c])
                any_letter.update([c])
        return counters


possible_answer_multiplier = 1.125
in_column_weight = 6.28
in_word_weight = 0.25


def weight_guess(stats, possible, word):
    score = 0.0
    any_letter_stats = stats[5]
    for i, letter in enumerate(word):
        if letter in word[:i]:
            letter = "2" + letter
        score += in_word_weight * any_letter_stats[letter]
        this_letter_stats = stats[i]
        score += in_column_weight * this_letter_stats[letter]
    if word in possible:
        score *= possible_answer_multiplier
    return score


def apply_guess(real_word, guesser, guess) -> bool:
    num_correct = 0
    for letter in guesser.letters:
        letter.clear_guess()
    guesser.inclusions = set()

    for i, (real_letter, letter) in enumerate(zip(real_word, guess)):
        if letter == real_letter:
            guesser.letters[i].set_correct(letter)
            num_correct += 1

    if num_correct == 5:
        return True

    for i, (real_letter, letter) in enumerate(zip(real_word, guess)):
        if letter == real_letter:
            continue
        unguessed = [c for c in real_word]
        for c in guesser.letters:
            if c.is_correct():
                unguessed.remove(c.letter)
        if letter in unguessed:
            guesser.letters[i].set_misplaced(letter)
            guesser.inclusions.add(letter)
            continue

        if letter in real_word:
            guesser.exclusions.add("2" + letter)
        else:
            guesser.exclusions.add(letter)
    return False


def run_solver(real_word, guess=None, exclusions=None, verbose=False):
    guesser = Guesser(guess)

    if exclusions:
        guesser.exclusions.update(exclusions)

    possible = possible_answers
    guesses = acceptable_guesses

    for try_number in range(10):
        if verbose:
            print(try_number, guesser)
        possible = guesser.filter_set(possible)
        guesses = guesser.filter_set(guesses)
        n = len(possible)
        m = len(guesses)
        if verbose:
            print(f"there are {n} possible answers, {m} guesses")

        assert n > 0, f"no guess for {guesser}, {real_word}"

        if verbose:
            if n < 40:
                print(possible)
            if m < 40:
                print(guesses)

        if n == 1:
            next_guess = possible.pop()
        else:
            stats = guesser.stats_set(possible)
            # print('stats\n\t', '\n\t'.join([str(s) for s in stats]), sep='')
            rated = []
            for g in guesses:
                score = weight_guess(stats, possible, g)
                rated.append((score, g))
            rated.sort()
            # print(rated[-15:])
            next_guess = rated[-1][1]
            if verbose:
                print("next guess:", next_guess)

        if real_word:
            correct = apply_guess(real_word, guesser, next_guess)
            if correct:
                try_number += 1
                if verbose or try_number > 6:
                    print(f"The answer is {next_guess} in {try_number} guesses")
                return next_guess, try_number
        else:
            return
    raise Exception(f"no solution {real_word}, {guesser}")


def solver():
    if len(sys.argv) > 1:
        exclusions = set()
        guess = sys.argv[1]

        if len(sys.argv) == 3 and len(sys.argv[2]) == 5:
            real_word = sys.argv[2]
        else:
            real_word = None
            for arg in sys.argv[2:]:
                for letter in arg:
                    letter = letter.lower()
                    if not is_letter(letter):
                        continue
                    exclusions.add(letter)

        run_solver(real_word, guess, exclusions=exclusions, verbose=True)
    else:
        fails = set()
        tries = collections.Counter()
        for i, real_word in enumerate(possible_answers):
            try:
                answer, try_number = run_solver(real_word)
                assert answer == real_word
            except:
                fails.add(real_word)
                print("fails on", real_word)
                continue
            tries.update([try_number])
            if i > 0 and i % 100 == 0:
                print(i, "so far", tries)
        print_counter(tries)
        print("fails:", fails)


if __name__ == "__main__":
    solver()
