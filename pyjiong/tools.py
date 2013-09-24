#from __future__ import unicode_literals
#from __future__ import print_function
import sys
import re

def pinyin_num_to_mark(pinyin_num):
    tone_marks = {
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
         'ü': ('ǖ','ǘ','ǚ','ǜ','u'),
         'Ü': ('Ǖ','Ǘ','Ǚ','Ǜ','U')
         }
    
    # replace ü workarounds
    pattern = re.compile('(n|N|l|L)(v|V|u:|U:)(e|E)?([1-5])')
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
                    pin = pin.replace(letter, tone_marks[letter][tone-1])
                    marked = True
        if marked:
            # after each replacement, the string gets 1 shorter (number is gone)
            cut_start = match.start() - replaced_letters
            cut_end = match.end() - replaced_letters
            pinyin_mark = pinyin_mark[:cut_start] + pin + pinyin_mark[cut_end:]
            replaced_letters += 1
    return pinyin_mark

def pinyin_mark_to_num(pinyin_mark):
    tone_marks = {
         'a': ('ā','á','ǎ','à'),
         'A': ('Ā','Á','Ǎ','À'),
         'e': ('ē','é','ě','è'),
         'E': ('Ē','É','Ě','È'),
         'i': ('ī','í','ǐ','ì'),
         'I': ('Ī','Í','Ǐ','Ì'),
         'o': ('ō','ó','ǒ','ò'),
         'O': ('Ō','Ó','Ǒ','Ò'),
         'u': ('ū','ú','ǔ','ù'),
         'U': ('Ū','Ú','Ǔ','Ù'),
         'ü': ('ǖ','ǘ','ǚ','ǜ'),
         'Ü': ('Ǖ','Ǘ','Ǚ','Ǜ')
         }
    if len(pinyin_mark) > 6:
        pass
    for key_char, mark_chars in tone_marks.items():
        for tone, tone_char in enumerate(mark_chars):
            if tone_char in pinyin_mark:
                return (pinyin_mark.replace(tone_char,key_char) + str(tone+1))
    return (pinyin_mark.replace(tone_char,key_char) + str(5))

def to_zhuyin(pron):
    pass

def only_hanzi(word):
    # taken from stackoverflow.com !!
    if word.strip() == '':
        return False
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
