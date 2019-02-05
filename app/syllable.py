from collections import defaultdict
from collections import deque
from itertools import islice

from app.char import chars


vowel_repetitions = set([
    'aa', 'ii', 'ee', 'uu', 'oo',
    'ie', 'ei', 'uo', 'ou'])


def parse_syllable(syllable):
    def get_index(i, func):
        while i < len(syllable) and func(syllable[i]):
            i += 1
        return i
    cons_i = get_index(0, lambda char: char not in chars['non-consonant'])
    vowl_i = get_index(cons_i, lambda char: char in chars['vowel'])
    return syllable[:cons_i], syllable[cons_i:vowl_i], syllable[vowl_i:]


class SymbolMap(defaultdict):
    def __missing__(self, key):
        self[key] = key
        return key


symbol_map = SymbolMap()
symbol_map.update({'j': 'D', 'ñ': '~', 'ng': 'N', 'ts': 'C'})
symbol_map.update({'aa': ':', 'ii': '1', 'ee': '2', 'uu': '3', 'oo': '4'})
symbol_map.update({'ie': '5', 'ei': '6', 'uo': '7', 'ou': '8'})
symbol_map.update({'trailing_consonant': '/', 'non_trailing_consonant': '='})
symbol_map.update({'double_syllable': ':'})
symbol_map.update({'syllable_consonant_stop': '-'})
symbol_map.update({'double_syllable_consonant_stop': ';'})
symbol_map.update({'word_doubling': '\\'})


class Syllable:

    def __init__(self, syllable):
        consonant, vowel, modifier = parse_syllable(syllable)
        self._consonant = consonant
        self._vowel = vowel
        self._modifier = modifier

    def __repr__(self):
        return '({},{},{})'.format(self.consonant, self.vowel, self.modifier)

    def __eq__(self, syllable):
        return (self.consonant == syllable.consonant and
                self.vowel == syllable.vowel and
                self.modifier == syllable.modifier)

    def set_modifier(self, modifier_key):
        self.modifier = symbol_map[modifier_key]

    def append_modifier(self, modifier_key):
        self.modifier += symbol_map[modifier_key]

    def is_consonant(self):
        return self.consonant and not self.vowel

    def is_vowel(self):
        return not self.consonant and self.vowel

    def is_syllable(self):
        return self.consonant and self.vowel

    def is_double_syllable(self):
        return self.modifier == symbol_map['double_syllable']

    @property
    def consonant(self):
        return self._consonant

    @property
    def vowel(self):
        return self._vowel

    @property
    def modifier(self):
        return self._modifier

    @vowel.setter
    def vowel(self, vowel):
        self._vowel = vowel

    @modifier.setter
    def modifier(self, modifier):
        self._modifier = modifier


class SyllableSeq(deque):

    def __init__(self, syllables):
        super().__init__(syllables)

    def is_word_doubling(self):
        if len(self) < 4:
            return False
        return ((self[0], self[1]) == (self[2], self[3]) and
                self[0] != self[1])

    def is_vowel_doubling(self):
        if len(self) < 2:
            return False
        return (self[0].is_vowel() and self[1].is_vowel() and
                self[0] == self[1])

    def is_syllable_doubling(self):
        if len(self) < 2:
            return False
        return (self[0].is_syllable() and self[1].is_syllable() and
                self[0].consonant == self[1].consonant and
                self.concat_vowels(2) in vowel_repetitions)

    def is_consonant_stop(self):
        if len(self) < 2:
            return False
        return (self[0].is_syllable() and self[1].is_consonant() and
                self[0].consonant == self[1].consonant)

    def is_trailing_consonant(self):
        if not self[0].is_consonant():
            return False
        return len(self) < 2 or self[1] == Syllable(' ')

    def is_non_trailing_consonant(self):
        if not self[0].is_consonant() or len(self) < 2:
            return False
        return self[1] != Syllable(' ')

    def insert_modifier(self, i, modifier_key):
        self.insert(i, Syllable(symbol_map[modifier_key]))

    def concat_vowels(self, n):
        return ''.join([syllable.vowel for syllable in
                        islice(self, 0, n) if syllable.vowel])

    def pop_nth(self, n):
        self.rotate(-n)
        self.popleft()
        self.rotate(n)
