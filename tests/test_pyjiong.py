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
        test_list = [
                ('ni3', 'nǐ'),
                ('hao3', 'hǎo'),
                ('nu:5', 'nü'),
                ('nve5', 'nüe')
                ]
        for test in test_list:
            self.assertEqual(test[1], pyjiong.pinyin_num_to_mark(test[0]))
            self.assertEqual(pyjiong.pinyin_normalize(test[0]),
                             pyjiong.pinyin_mark_to_num(test[1]))
    
    def test_split_pinyin(self):
        test_list1 = [
                ('yi1', 'i'),
                ('ya2', 'ia'),
                ('yao3', 'iao'),
                ('ye4', 'ie'),
                ('you1', 'iu'),
                ('yan2', 'ian'),
                ('yang3', 'iang'),
                ('yin4', 'in'),
                ('ying5', 'ing'),
                ('yong1', 'iong'),
                ('wu2', 'u'),
                ('wa3', 'ua'),
                ('wo', 'uo'),
                ('wei4', 'ui'),
                ('wai2', 'uai'),
                ('wan3', 'uan'),
                ('wen', 'un'),
                ('wang3', 'uang'),
                ('weng1', 'ueng'),
                ('yu1', 'ü'),
                ('yue3', 'üe'),
                ('yuan2', 'üan'),
                ('yun4', 'ün')
                ]
        test_list2 = [
                ('Que4', ('q', 'üe', 4)),
                ('Hm2', ('hm', '', 2)),
                ('shuang1', ('sh', 'uang', 1)),
                ('you2', ('', 'iu', 2)),
                ('yo', ('', 'io', 5))
                ]
        for test in test_list1:
            self.assertEqual(pyjiong.pinyin_split(test[0])[1], test[1])
        for test in test_list2:
            self.assertEqual(pyjiong.pinyin_split(test[0]), test[1])


    def test_similar_pinyin(self):
        test_list = [
                ('feng1', 'fen'),
                ('ding3', 'ting2'),
                ('bang3', 'pan2')
                ]
        for test in test_list:
            self.assertTrue(pyjiong.pinyin_are_similar(test[0], test[1]))

    def test_only_hanzi(self):
        hanzi_mix = '1234567890ß!"§$%&/()=? \
                ¹²³¼½½¬¬{{[[]}\ééäöüasdfjkl \
                漢字,.-;:_<>|abcdefghijklmnopqrstuvwxyz'
        only_hanzi = '漢字'
        self.assertEqual(only_hanzi,pyjiong.only_hanzi(hanzi_mix))

if __name__ == '__main__':
    unittest.main()

