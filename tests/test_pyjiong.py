import sys
import os
import unittest
sys.path.append(os.path.abspath(".."))
import pyjiong 
from io import StringIO

class PyjiongTest(unittest.TestCase):
    def test_open_unihan(self):
        with open('./textfiles/unihan_test.txt',
                  mode='r',
                  encoding='utf-8') as txt_file:
            expected_output = {
                '糫': {
                    'kHanyuPinyin': ['huán'], 
                    'kMandarin': ['huán']}, 
                '㮏': {
                    'kHanyuPinyin': ['nài', 'nì', 'nà', 'nà', 'nài', 'nì'], 
                    'kMandarin': ['nài']}, 
                '糯': {
                    'kHanyuPinyin': ['nuò'], 
                    'kMandarin': ['nuò'], 
                    'kDefinition': 'glutinous rice; glutinous, sticky'}, 
                '愝': {
                    'kHanyuPinyin': ['yǎn'], 
                    'kMandarin': ['yǎn']}, 
                '愜': {
                    'kHanyuPinyin': ['qiè'], 
                    'kMandarin': ['qiè'], 
                    'kDefinition': 'be satisfied, be comfortable'}, 
                '愞': {'kMandarin': ['nuò'], 
                    'kDefinition': 'timid, apprehensive'}
                }
            real_output = pyjiong.open_unihan(txt_file,
                    ['kHanyuPinyin','kDefinition','kMandarin'])
            self.assertEqual(real_output,expected_output)

    def test_open_save_list(self):
        with open('./textfiles/skritter_test.txt',
                  mode='r',
                  encoding='utf-8') as skritter_file:
            sample_in = skritter_file.read()
            skritter_file.seek(0)
            test_list = pyjiong.ChList('test-list', list_file = skritter_file)
            sample_file_out = StringIO()
            test_list.save_file(sample_file_out,
                    {'attr_order':['simp','pinyin','definition']})
            sample_out = sample_file_out.getvalue() + '\n'
            self.assertEqual(sample_in, sample_out)

    def test_convert_pinyin(self):
        num_pinyin = 'ni3 hao3'
        mark_pinyin = 'nǐ hǎo'

        self.assertEqual(mark_pinyin, pyjiong.pinyin_num_to_mark(num_pinyin))
        self.assertEqual(num_pinyin[:3],
                pyjiong.pinyin_mark_to_num(mark_pinyin[:2]))

    def test_only_hanzi(self):
        hanzi_mix = '1234567890ß!"§$%&/()=? \
                ¹²³¼½½¬¬{{[[]}\ééäöüasdfjkl \
                漢字,.-;:_<>|abcdefghijklmnopqrstuvwxyz'
        only_hanzi = '漢字'
        self.assertEqual(only_hanzi,pyjiong.only_hanzi(hanzi_mix))

if __name__ == '__main__':
    unittest.main()

