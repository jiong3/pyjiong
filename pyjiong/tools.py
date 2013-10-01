#from __future__ import unicode_literals
#from __future__ import print_function
import sys
import re
from collections import Counter

TONE_MARKS = {
     'a': ('ā','á','ǎ','à','a'),
     'A': ('Ā','Á','Ǎ','À','A'),
     'e': ('ē','é','ě','è','e'),
     'E': ('Ē','É','Ě','È','E'),
     'i': ('ī','í','ǐ','ì','i'),
     'I': ('Ī','Í','Ǐ','Ì','I'),
     'o': ('ō','ó','ǒ','ò','o'),
     'O': ('Ō','Ó','Ǒ','Ò','O'),
     'u': ('ū','ú','ǔ','ù','u'),
     'U': ('Ū','Ú','Ǔ','Ù','U'),
     'ü': ('ǖ','ǘ','ǚ','ǜ','ü'),
     'Ü': ('Ǖ','Ǘ','Ǚ','Ǜ','U')
     }

def pinyin_normalize(pinyin_num):
    """ Return the pinyin with u:/v converted to ü. """

    pattern = re.compile('(n|N|l|L)(v|V|u:|U:)(e|E)?([1-5])?')
    to_replace = (('v','ü'),('V','Ü'),('u:','ü'),('U:','Ü'))
    colons_removed = 0
    pinyin_num_copy = pinyin_num
    for match in pattern.finditer(pinyin_num_copy):
        s = match.group()
        for this, with_this in to_replace:
            s = s.replace(this,with_this)
        cut_start = match.start() - colons_removed
        cut_end = match.end() - colons_removed
        pinyin_num = pinyin_num[:cut_start] + s + pinyin_num[cut_end:]
        if ':' in match.group(2):
            colons_removed += 1

    return pinyin_num

def pinyin_split(pinyin_num):
    """ Return a tuple (inital, final, tone) for one syllable. """

    INITIALS = set(("b","p","m","n","f","d",
        "t","l","g","k","h","j","q","x",
        "zh","ch","sh","r","z","c","s"))
    EXCEPTIONS = {'you': 'iu', 'wei': 'ui',
            'wu': 'u', 'wen': 'un'}
    STRANGERS = set(('m', 'n', 'hm', 'ng', 'hng'))

    pinyin = pinyin_normalize(pinyin_num)
    pinyin = pinyin.lower()
    initial = ''
    final = ''
    tone = 5
    if pinyin[-1].isdigit():
        tone = int(pinyin[-1])
        pinyin = pinyin[:-1]

    if pinyin in STRANGERS:
        initial = pinyin
    elif pinyin[:2] in INITIALS:
        initial = pinyin[:2]
        final = pinyin[2:]
    elif pinyin[0] in INITIALS:
        initial = pinyin[0]
        final = pinyin[1:]
        if initial in set(('j', 'q', 'x')):
            final = final.replace('u', 'ü')
    else:  # no initial
        if pinyin in EXCEPTIONS:
            final = EXCEPTIONS[pinyin]
        elif pinyin.startswith('yi'):
            final = pinyin[1:]
        elif pinyin.startswith('yu'):
            final = pinyin.replace('yu', 'ü')
        elif pinyin.startswith('y'):
            final = pinyin.replace('y', 'i')
        elif pinyin.startswith('w'):
            final = pinyin.replace('w', 'u')

    return (initial, final, tone)

def pinyin_are_similar(pinyin1, pinyin2, margins=None,
                      in_groups=None, fin_groups=None):
    """
    Determine if two syllables are similar.

    Args:
        pinyin1 (str): First syllable
        pinyin2 (str): Second syllable
        margins (list): A list with "similarity margins" for
            intial, final, tone. Default = [1, 1, 3]
            Following numbers are possible:
            0: equal
            1: similar
            2: similar, empty string being similar to everything
            3: anything
        in_groups ([(group)]): A list of tuples, each tuple representing
            a group of initial sounds which are considered similar. For
            the default, see below.
        fin_groups: See in_groups, same thing for final sounds.

    Returns:
        True/False
    """

    # not included: f, l, h
    IN_GROUPS = (
            ('b', 'p'),
            ('m', 'n'),
            ('d', 't'),
            ('g', 'k'),
            ('j', 'q', 'x'),
            ('zh', 'ch', 'sh', 'r'),
            ('z', 'c', 's'))
    # not included: i, iu, ie
    FIN_GROUPS = (
        ('a', 'ao'),
        ('ai', 'ei'),
        ('an', 'ang'),
        ('o', 'ou'),
        ('ong', 'iong', 'eng', 'en'),
        ('e', 'er'),
        ('ia', 'iao'),
        ('ian', 'in', 'iang', 'ing'),
        ('u', 'ua', 'uo'),
        ('ui', 'uai'),
        ('un', 'uan', 'uang', 'ueng'),
        ('ü', 'üe'),
        ('üan', 'ün'))
    
    if not margins:
        margins = [1,1,3]
    if not in_groups:
        in_groups = IN_GROUPS
    if not fin_groups:
        fin_groups = FIN_GROUPS

    # build dictionary
    similar_dic = {}
    for groups in (in_groups, fin_groups):
        for group in groups:
            for sound in group:
                if sound in similar_dic:
                    similar_dic[sound].update(set(group))
                else:
                    similar_dic[sound] = set(group)

    pinyin1 = pinyin_split(pinyin1)
    pinyin2 = pinyin_split(pinyin2)

    result = True
    for pin1, pin2, margin in zip(pinyin1, pinyin2, margins):
        if margin == 0 and pin1 != pin2:
            result = False
        if margin == 3:
            continue
        if not isinstance(pin1, int):  # not the tone number
            if margin == 2 and (pin1 == '' or pin2 == ''):
                continue
            else:
                if pin1 in similar_dic:
                    if pin1 not in similar_dic[pin2]:
                        result = False
                else:
                    if pin1 != pin2:
                        result = False

    return result

def pinyin_num_to_mark(pinyin_num):
    """ Convert a string of pinyin with numbers to a string of pinyin with
    tonemarks.
    """
    
    pinyin_num = pinyin_normalize(pinyin_num)
            
    # replace the tone numbers
    pinyin_mark = pinyin_num
    pattern = re.compile('([a-zA-ZüÜ]{1,6})([1-5])') # could be more strict if necessary
    replaced_letters = 0
    for match in pattern.finditer(pinyin_num):
        pin = match.group(1)
        pin_low = pin.lower()
        tone = int(match.group(2))
        marked = None
        for mark_letter, replace_letter in (
            ('a','a'),
            ('e','e'),
            ('o','o'),
            ('ui','i'),
            ('iu','u'),
            ('u','u'),
            ('ü','ü'),
            ('i','i')):
            if not marked:
                if mark_letter in pin_low:
                    pos = pin_low.find(replace_letter)
                    letter = pin[pos:pos + 1]  
                    pin = pin.replace(letter, TONE_MARKS[letter][tone-1])
                    marked = True
        if marked:
            # after each replacement, the string gets 1 shorter (number is gone)
            cut_start = match.start() - replaced_letters
            cut_end = match.end() - replaced_letters
            pinyin_mark = pinyin_mark[:cut_start] + pin + pinyin_mark[cut_end:]
            replaced_letters += 1
    return pinyin_mark

def pinyin_mark_to_num(pinyin_mark):
    """ Return one syllable of pinyin with numbers from one with marks. """

    if len(pinyin_mark) > 6:
        pass
    for key_char, mark_chars in TONE_MARKS.items():
        for tone, tone_char in enumerate(mark_chars[:4]):
            if tone_char in pinyin_mark:
                return (pinyin_mark.replace(tone_char,key_char) + str(tone+1))
    return (pinyin_mark.replace(tone_char,key_char) + str(5))

def char_frequency(string):
    """
    Return a sorted list of tuples (char, count).
    
    The list is sorted from highest to lowest count, 
    with count being the number of appearances of
    the character in the string.
    """

    string = only_hanzi(string)
    freq_cnt = Counter()
    for char in string:
        freq_cnt[char] += 1
    return freq_cnt.most_common()

def only_hanzi(word):
    """ Return the string minus everything which is not a hanzi. """

    # taken from stackoverflow.com !!
    if word.strip() == '':
        return ''
    LHan = [[0x2E80, 0x2E99],    # Han # So  [26] CJK RADICAL REPEAT, CJK RADICAL RAP
            [0x2E9B, 0x2EF3],    # Han # So  [89] CJK RADICAL CHOKE, CJK RADICAL C-SIMPLIFIED TURTLE
            [0x2F00, 0x2FD5],    # Han # So [214] KANGXI RADICAL ONE, KANGXI RADICAL FLUTE
            0x3005,              # Han # Lm       IDEOGRAPHIC ITERATION MARK
            0x3007,              # Han # Nl       IDEOGRAPHIC NUMBER ZERO
            [0x3021, 0x3029],    # Han # Nl   [9] HANGZHOU NUMERAL ONE, HANGZHOU NUMERAL NINE
            [0x3038, 0x303A],    # Han # Nl   [3] HANGZHOU NUMERAL TEN, HANGZHOU NUMERAL THIRTY
            0x303B,              # Han # Lm       VERTICAL IDEOGRAPHIC ITERATION MARK
            [0x3400, 0x4DB5],    # Han # Lo [6582] CJK UNIFIED IDEOGRAPH-3400, CJK UNIFIED IDEOGRAPH-4DB5
            [0x4E00, 0x9FC3],    # Han # Lo [20932] CJK UNIFIED IDEOGRAPH-4E00, CJK UNIFIED IDEOGRAPH-9FC3
            [0xF900, 0xFA2D],    # Han # Lo [302] CJK COMPATIBILITY IDEOGRAPH-F900, CJK COMPATIBILITY IDEOGRAPH-FA2D
            [0xFA30, 0xFA6A],    # Han # Lo  [59] CJK COMPATIBILITY IDEOGRAPH-FA30, CJK COMPATIBILITY IDEOGRAPH-FA6A
            [0xFA70, 0xFAD9],    # Han # Lo [106] CJK COMPATIBILITY IDEOGRAPH-FA70, CJK COMPATIBILITY IDEOGRAPH-FAD9
            [0x20000, 0x2A6D6],  # Han # Lo [42711] CJK UNIFIED IDEOGRAPH-20000, CJK UNIFIED IDEOGRAPH-2A6D6
            [0x2F800, 0x2FA1D]]  # Han # Lo [542] CJK COMPATIBILITY IDEOGRAPH-2F800, CJK COMPATIBILITY IDEOGRAPH-2FA1D

    def build_re():
        pattern_list = []
        for char_range in LHan:
            if isinstance(char_range, list):
                from_char, to_char = char_range
                try: 
                    from_char = chr(from_char)
                    to_char = chr(to_char)
                    pattern_list.append('%s-%s' % (from_char, to_char))
                except: 
                    pass # A narrow python build, so can't use chars > 65535 without surrogate pairs!
            else:
                try:
                    pattern_list.append(chr(char_range))
                except:
                    pass

        pattern = '[%s]' % ''.join(pattern_list)
        return re.compile(pattern)

    pattern = build_re()
    hanzi_only = ''.join([c for c in word if pattern.match(c)])

    return hanzi_only
