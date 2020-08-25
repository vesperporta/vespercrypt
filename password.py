"""
Copyright 2019 (c) GlibGlob Ltd.
Author: Laurence Psychic
Email: vesper.porta@protonmail.com

Generate passwords on the command line or import this module and use Password
as a self contained class.
"""

from random import choice
from math import ceil


class CharacterRange:
    """Model to define the number values used within an encoding format."""
    name = ''
    min = -1
    max = -1
    bytes = -1
    range = None
    encoding = 'utf-8'

    def represent(self):
        """
        Represent all characters of this character range in a list of byte
        strings.

        :return: list
        """
        try:
            if type(self.range) in [list, tuple, ]:
                return [chr(i) for i in self.range]
            else:
                return [chr(i) for i in range(self.min, self.max)]
        except OverflowError as e:
            print(e)
        except UnicodeDecodeError as e:
            print('{} unable to decode due to UnicodeDecodeError: {}'.format(
                self.name, e.reason,
            ))
        return []

    def __init__(self, name, min, max):
        if min < 0:
            raise Exception('Value for min is below 0: min = {}.'.format(min))
        if max <= min:
            raise Exception('Max is below min: max = {}.'.format(max))
        self.name = name
        self.min = min
        self.max = max
        self.bytes = ceil(int(max).bit_length() / 8)
        self.range = range(min, max)


filename_safe = CharacterRange('Filename Safe', 65, 91)
filename_safe.range = (
    list(range(49, 60)) + list(range(65, 91)) + list(range(97, 123)))


class Alphabet:
    """A Model to maintain a listing of all aplphabets bound within number
    ranges known to this class, currently all of the unicode system in provided
    without Emoji support.

    TODO: Have Emojis represented in this model.
    """
    EXTENDED_ALPHABETS = [
        'Basic Latin', 'Greek and Coptic', 'Cyrillic', 'Armenian',
        'Hebrew', 'Arabic', 'Syriac', 'Thaana', 'Devanagari', 'Bengali',
        'Gurmukhi', 'Oriya', 'Tamil', 'Telugu', 'Kannada', 'Malayalam',
        'Sinhala', 'Thai', 'Lao', 'Tibetan', 'Myanmar', 'Georgian',
        'Hangul Jamo', 'Ethiopic', 'Cherokee', 'Ogham', 'Runic',
        'Tagalog', 'Hanunoo', 'Buhid', 'Tagbanwa', 'Khmer', 'Mongolian',
        'Limbu', 'TaiLe', 'CJK Radicals Supplement', 'Hiragana',
        'Katakana', 'CJK Unified Ideographs',
    ]
    DEFAULT_ALPHABETS = [
        'Basic Latin', 'Hiragana', 'Katakana', 'CJK Unified Ideographs'
    ]

    _alphabet = None

    character_ranges = [
        CharacterRange('ASCII', 33, 122),
        filename_safe,
        CharacterRange('Basic Latin', 32, 127),
        CharacterRange('Latin-1 Supplement', 160, 255),
        CharacterRange('Latin Extended-A', 256, 383),
        CharacterRange('Latin Extended-B', 384, 591),
        CharacterRange('IPA Extensions', 592, 687),
        CharacterRange('Spacing Modifier Letters', 688, 767),
        CharacterRange('Combining Diacritical Marks', 768, 879),
        CharacterRange('Greek and Coptic', 880, 1023),
        CharacterRange('Cyrillic', 1024, 1279),
        CharacterRange('Cyrillic Supplementary', 1280, 1327),
        CharacterRange('Armenian', 1328, 1423),
        CharacterRange('Hebrew', 1424, 1535),
        CharacterRange('Arabic', 1536, 1791),
        CharacterRange('Syriac', 1792, 1871),
        CharacterRange('Thaana', 1920, 1983),
        CharacterRange('Devanagari', 2304, 2431),
        CharacterRange('Bengali', 2432, 2559),
        CharacterRange('Gurmukhi', 2560, 2687),
        CharacterRange('Gujarati', 2688, 2815),
        CharacterRange('Oriya', 2816, 2943),
        CharacterRange('Tamil', 2944, 3071),
        CharacterRange('Telugu', 3072, 3199),
        CharacterRange('Kannada', 3200, 3327),
        CharacterRange('Malayalam', 3328, 3455),
        CharacterRange('Sinhala', 3456, 3583),
        CharacterRange('Thai', 3584, 3711),
        CharacterRange('Lao', 3712, 3839),
        CharacterRange('Tibetan', 3840, 4095),
        CharacterRange('Myanmar', 4096, 4255),
        CharacterRange('Georgian', 4256, 4351),
        CharacterRange('Hangul Jamo', 4352, 4607),
        CharacterRange('Ethiopic', 4608, 4991),
        CharacterRange('Cherokee', 5024, 5119),
        CharacterRange('Unified Canadian Aboriginal Syllabics', 5120, 5759),
        CharacterRange('Ogham', 5760, 5791),
        CharacterRange('Runic', 5792, 5887),
        CharacterRange('Tagalog', 5888, 5919),
        CharacterRange('Hanunoo', 5920, 5951),
        CharacterRange('Buhid', 5952, 5983),
        CharacterRange('Tagbanwa', 5984, 6015),
        CharacterRange('Khmer', 6016, 6143),
        CharacterRange('Mongolian', 6144, 6319),
        CharacterRange('Limbu', 6400, 6479),
        CharacterRange('TaiLe', 6480, 6527),
        CharacterRange('Khmer Symbols', 6624, 6655),
        CharacterRange('Phonetic Extensions', 7424, 7551),
        CharacterRange('Latin Extended Additional', 7680, 7935),
        CharacterRange('Greek Extended', 7936, 8191),
        CharacterRange('General Punctuation', 8192, 8303),
        CharacterRange('Superscripts and Subscripts', 8304, 8351),
        CharacterRange('Currency Symbols', 8352, 8399),
        CharacterRange('Combining Diacritical Marks for Symbols', 8400, 8447),
        CharacterRange('Letterlike Symbols', 8448, 8527),
        CharacterRange('Number Forms', 8528, 8591),
        CharacterRange('Arrows', 8592, 8703),
        CharacterRange('Mathematical Operators', 8704, 8959),
        CharacterRange('Miscellaneous Technical', 8960, 9215),
        CharacterRange('Control Pictures', 9216, 9279),
        CharacterRange('Optical Character Recognition', 9280, 9311),
        CharacterRange('Enclosed Alphanumerics', 9312, 9471),
        CharacterRange('Box Drawing', 9472, 9599),
        CharacterRange('Block Elements', 9600, 9631),
        CharacterRange('Geometric Shapes', 9632, 9727),
        CharacterRange('Miscellaneous Symbols', 9728, 9983),
        CharacterRange('Dingbats', 9984, 10175),
        CharacterRange('Miscellaneous Mathematical Symbols-A', 10176, 10223),
        CharacterRange('Supplemental Arrows-A', 10224, 10239),
        CharacterRange('Braille Patterns', 10240, 10495),
        CharacterRange('Supplemental Arrows-B', 10496, 10623),
        CharacterRange('Miscellaneous Mathematical Symbols-B', 10624, 10751),
        CharacterRange('Supplemental Mathematical Operators', 10752, 11007),
        CharacterRange('Miscellaneous Symbols and Arrows', 11008, 11263),
        CharacterRange('CJK Radicals Supplement', 11904, 12031),
        CharacterRange('Kangxi Radicals', 12032, 12255),
        CharacterRange('Ideographic Description Characters', 12272, 12287),
        CharacterRange('CJK Symbols and Punctuation', 12288, 12351),
        CharacterRange('Hiragana', 12352, 12447),
        CharacterRange('Katakana', 12448, 12543),
        CharacterRange('Bopomofo', 12544, 12591),
        CharacterRange('Hangul Compatibility Jamo', 12592, 12687),
        CharacterRange('Kanbun', 12688, 12703),
        CharacterRange('Bopomofo Extended', 12704, 12735),
        CharacterRange('Katakana Phonetic Extensions', 12784, 12799),
        CharacterRange('Enclosed CJK Letters and Months', 12800, 13055),
        CharacterRange('CJK Compatibility', 13056, 13311),
        CharacterRange('CJK Unified Ideographs Extension A', 13312, 19903),
        CharacterRange('Yijing Hexagram Symbols', 19904, 19967),
        CharacterRange('CJK Unified Ideographs', 19968, 40959),
        CharacterRange('Yi Syllables', 40960, 42127),
        CharacterRange('Yi Radicals', 42128, 42191),
        CharacterRange('Hangul Syllables', 44032, 55215),
        CharacterRange('High Surrogates', 55296, 56191),
        CharacterRange('High Private Use Surrogates', 56192, 56319),
        CharacterRange('Low Surrogates', 56320, 57343),
        CharacterRange('Private Use Area', 57344, 63743),
        CharacterRange('CJK Compatibility Ideographs', 63744, 64255),
        CharacterRange('Alphabetic Presentation Forms', 64256, 64335),
        CharacterRange('Arabic Presentation Forms-A', 64336, 65023),
        CharacterRange('Variation Selectors', 65024, 65039),
        CharacterRange('Combining Half Marks', 65056, 65071),
        CharacterRange('CJK Compatibility Forms', 65072, 65103),
        CharacterRange('Small Form Variants', 65104, 65135),
        CharacterRange('Arabic Presentation Forms-B', 65136, 65279),
        CharacterRange('Halfwidth and Fullwidth Forms', 65280, 65519),
        CharacterRange('Specials', 65520, 65535),
        CharacterRange('Linear B Syllabary', 65536, 65663),
        CharacterRange('Linear B Ideograms', 65664, 65791),
        CharacterRange('Aegean Numbers', 65792, 65855),
        CharacterRange('Old Italic', 66304, 66351),
        CharacterRange('Gothic', 66352, 66383),
        CharacterRange('Ugaritic', 66432, 66463),
        CharacterRange('Deseret', 66560, 66639),
        CharacterRange('Shavian', 66640, 66687),
        CharacterRange('Osmanya', 66688, 66735),
        CharacterRange('Cypriot Syllabary', 67584, 67647),
        CharacterRange('Byzantine Musical Symbols', 118784, 119039),
        CharacterRange('Musical Symbols', 119040, 119295),
        CharacterRange('Tai Xuan Jing Symbols', 119552, 119647),
        CharacterRange('Mathematical Alphanumeric Symbols', 119808, 120831),
        CharacterRange('CJK Unified Ideographs Extension B', 131072, 173791),
        CharacterRange(
            'CJK Compatibility Ideographs Supplement', 194560, 195103),
        CharacterRange('Tags', 917504, 917631),
    ]

    def detail(self, alphabets=None):
        """
        Detail all characters from selected alphabets passed or defaulted to
        full list known to this model, as this is tightly coupled with password
        generation all alphabets are returned represented with each character
        in the returned list object.

        :param alphabets: list, names as strings limiting the alphabets
        :return: list
        """
        if self._alphabet:
            return self._alphabet
        if not alphabets:
            alphabets = self._alphabet
        alphabets_lower = [a.lower() for a in alphabets]
        alphabets = [
            a for a in self.character_ranges
            if a.name.lower() in alphabets_lower]
        rtn = []
        for alphabet in alphabets:
            rtn += alphabet.represent()
        return rtn

    def __init__(self, alphabets=None):
        if not alphabets:
            alphabets = Alphabet.DEFAULT_ALPHABETS
        arg_type = type(alphabets)
        if arg_type not in [list, tuple, ]:
            if arg_type is str and arg_type.index(',') > -1:
                alphabets = arg_type.split(',')
            else:
                alphabets = [alphabets]
        self._alphabet = self.detail(alphabets=alphabets)

    def __str__(self):
        return self._alphabet


class Password:
    """
    Representation of a password with default security to define a character
    length of 64 and use the 'Basic Latin' alphabet. Changing the alphabet
    used when creating this password supply the list of characters at the time
    of creation or generation.

    Example use: `password = Password()`
    """
    complexity = 0
    _value = None

    def generate(self, length=64, alphabet=None):
        """
        Create a new password determined by the alphabet supplied, if no
        alphabet is supplied then a large proportion of the Unicode standard
        will be used.

        :param length: the character length of the password required,
                        default 64
        :param alphabet: optional list of characters to use as characters
        """
        character_details = None
        if not alphabet:
            character_details = Alphabet().detail()
        elif type(alphabet) is Alphabet:
            character_details = alphabet.detail()
        elif type(alphabet) is list:
            character_details = Alphabet(alphabets=alphabet).detail()
        self.complexity = len(character_details)
        if not self.complexity:
            raise Exception('No complexity to alphabet.')
        count = 0
        err_count = 0
        rtn = ''
        while count < length:
            try:
                rtn += choice(character_details)
                count += 1
            except TypeError:
                pass
            except IndexError as e:
                err_count += 1
                if err_count > length:
                    raise e
        self._value = rtn
        return rtn

    def __init__(self, length=64, alphabet=None):
        self.generate(length=length, alphabet=alphabet)

    def __str__(self):
        return self._value or 'Password: Not generated'
