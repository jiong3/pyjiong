import os
import sys
sys.path.append(os.path.abspath("../.."))
import pyjiong

# open list files
with open('chars-simp.txt', mode='r', encoding='utf-8') as txt_file:
    freq = pyjiong.ChList('freq')
    freq.open_file(txt_file)
with open('hsk_plecodict.txt', mode='r', encoding='utf-8') as txt_file:
    hsk = pyjiong.ChList('hsk')
    hsk.open_file(txt_file)


# freq.mix_with(...)[0] contains characters which are only in the
# frequency list, [1] contains words/characters which only consist
# of characters which are in both hsk and freq and [2] contains
# words which characters which are not in the frequency list

# insert hsk words in the right place in freq
order_to_freq = freq.mix_with(hsk, 'simp', iterate=True)[1]
# subtract all those single characters which are not words on their own
only_hsk_words = order_to_freq.mix_with(hsk, 'simp')[1]
result = only_hsk_words
result.name = 'result'

# since the frequency file doesn't contain any pinyin or definitions,
# we have to add those from the hsk file
hsk.create_index('simp')
for i, word in enumerate(result.words):
    if word.simp in hsk.simp_i:
        new_word = hsk.words[hsk.simp_i[word.simp][0]]
        result.words[i].pinyin = new_word.pinyin
        result.words[i].definition = new_word.definition

# write the result list
with open('result.txt', mode='w', encoding='utf-8') as txt_file:
    result.save_file(txt_file)
