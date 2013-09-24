#from __future__ import unicode_literals
#from __future__ import print_function
#from __future__ import division
from pyjiong.filesupport import open_text_list, save_text_list
import copy

PLECO_NL = '\ueab1'     # new line
PLECO_BO = '\ueab2'     # bold opening tag
PLECO_BC = '\ueab3'     # bold closing tag
PLECO_IO = '\ueab4'     # italic opening tag
PLECO_IC = '\ueab5'     # italic closing tag
""" other pleco stuff:
EAB8/EABB = "copy-whatever's-in-this-to-the-Input-Field hyperlinks"

colored text:
EAC1 followed by two characters with the highest-order bit 1 and the
lowest-order 12 bits representing the first/second halves of a 24-bit RGB color
value to start the range, EAC2 to end. So to render a character in green, for
example, you'd want EAC1 800F 8F00, then the character, then EAC2."
"""


class ChWord(object):
    def __init__(self, attributes={}):

        for name, value in attributes.items():
            setattr(self, name, value)

        # some defaults
        for name in ['simp', 'trad', 'pinyin', 'definition']:
            if not hasattr(self, name):
                setattr(self, name, '')

        for name in ['section', 'number']:
            if not hasattr(self, name):
                setattr(self, name, -1)


class ChList(object):
    def __init__(self, name, list_file=None,
                 sections=None, words=None, custom=None):

        self.name = name
        if not sections:
            sections = []
        self.sections = sections
        if not words:
            words = []
        self.words = words

        if list_file:
            self.open_file(list_file, custom)

    def open_file(self, list_file, custom=None):
        self.sections, temp_words = open_text_list(list_file, custom)
        self.words = [ChWord(attr_dic) for attr_dic in temp_words]

    def save_file(self, list_file, custom=None):
        temp_words = [word.__dict__ for word in self.words]
        save_text_list(list_file, self.sections, temp_words, custom)

    def create_index(self, attribute_name, iterate=False):
        """
        Create an index for an attribute or items of an attribute.

        If you have a list of words (self) and you want to find those with
        word.pinyin == 'hao3' or those with word.trad == '中國‘ you
        can create an index using 'pinyin' or 'trad' and attribute_name.

        If you want to find all words containing a character like '國',
        you can use iterate = True, so the method will iterate over all
        items in word.attribute_name and create an index for each of those
        items.

        Args:
            attribute_name (string): the name of the attribute you want to
                create an index for.
            iterate (bool): should the index be for the value of the attribute
                as a whole or for each item of the attribute, for strings that
                would be the individual characters, for lists the items.

        The script will add a new attribute to self (the list), called:
        attribute_name + '_i' (iterate == False)   or
        attribute_name + '_ii' (iterate == True)
        attribute_name is obviously the string provided as argument.

        The new attribute is a python dictionary, using the different values
        of word.attribute_name or the values of the items as keys and a list of
        the words having the value in word.attribute_name as values. This list
        only contains the index of the word in self.words, not the word object
        itself. Also, the list is sorted in order of self.words.
        """
        new_index = {}
        if iterate:
            suffix = '_ii'
        else:
            suffix = '_i'
        for no, word in enumerate(self.words):
            # skip words which don't have this attribute
            if hasattr(word, attribute_name):
                content = getattr(word, attribute_name)
            else:
                continue
            # create list of items of this attribute if itereate == True,
            # e.g. for 你好 -> ['你','好']
            if iterate:
                items = list(content)
            else:
                items = [content]
            for item in items:
                if item in new_index:
                    new_index[item].append(no)
                else:
                    new_index[item] = [no]
        setattr(self, attribute_name + suffix, new_index)

    def mix_with(self, list2, attribute, iterate=False):
        """ Mix self with another list while the order of self is kept.

        Args:
            list2 (ChList): another list for comparison
            attribute (string): the name of the attribute which should
                be used for comparisons. Two words are considered the same
                if word.attribute is the same.
            iterate (bool): False if only whole words should be compared,
                True if each character/item of word.attribute should be
                considered
        Returns:
            A tuple with three lists (ChList), the first one contains only
            words which are (according to comparisons with word.attribute) only
            in self, the second one only words which are both in self and in
            list2 and the third one contains words which are only in list2 """
        # characters = iterated items of word, could also be something
        # different
        only_self = []
        both_lists = []
        only_list2 = []
        if not iterate:
            # only complete words are compared
            list2.create_index(attribute, False)
            list2_i = getattr(list2, attribute + '_i')
            only_list2 = list(list2.words)

            for word_o in self.words:
                word = copy.copy(word_o)
                content = getattr(word, attribute)
                if content in list2_i:
                    both_lists.append(word)
                    for number in list2_i[content]:
                        only_list2[number] = None  # leaving only in list2
                else:
                    only_self.append(word)
            only_list2 = [copy.copy(word) for word in only_list2 if word]
        else:
            # look at each character as part of a word

            # create indices
            self.create_index(attribute, False)
            self_i = getattr(self, attribute + '_i')
            self.create_index(attribute, True)
            list2.create_index(attribute, True)
            self_ii = getattr(self, attribute + '_ii')
            list2_ii = getattr(list2, attribute + '_ii')

            # check for words with characters only in self
            for word_o in self.words:
                word = copy.copy(word_o)
                content = getattr(word, attribute)
                items = list(content)
                in_list2 = True
                # only if all items are in list2, the word is also list2
                for item in items:
                    if item in list2_ii:
                        pass
                    else:
                        in_list2 = False
                if in_list2:
                    both_lists.append(word)
                else:
                    only_self.append(word)

            for word_o in list2.words:
                word = copy.copy(word_o)
                content = getattr(word, attribute)
                items = list(content)
                in_self_pos = 0

                for item in items:
                    if item in self_ii:
                        pos = self_ii[item][0]
                        # to get the order of self.words
                        if in_self_pos > -1 and pos > in_self_pos:
                            in_self_pos = pos
                    else:
                        in_self_pos = -1

                if in_self_pos > -1:
                    # if the word itself (and not just all characters) is
                    # is already in self.words, this word was already handled
                    # by the previous loop
                    if content not in self_i:
                        # just to make sure the order of list2 is kept
                        word.number = in_self_pos +\
                            (word.number / len(list2.words))
                        word.section = self.words[in_self_pos].section
                        both_lists.append(word)
                else:
                    only_list2.append(word)

        # bring those new items from the second loop into order with the
        # ones of the first loop
        both_lists.sort(key=lambda w: w.number)

        # create new word.numbers and delete unused sections
        def organize(o_sections, words):
            orig_sections = list(o_sections)  # creating a copy
            used_sections = set()
            new_sections = []
            # new_words = [] what is this?

            # find used sections and create new word numbers
            for number, w in enumerate(words):
                w.number = number
                used_sections.add(w.section)
            new_index = 0

            # remove unused sections
            for i, section in enumerate(orig_sections):
                if i in used_sections:
                    # replace list with integer pointing to
                    # position in new list
                    new_sections.append(section)
                    # replace section name with index in new_sections
                    orig_sections[i] = new_index
                    new_index += 1

            # update section number in words
            for w in words:
                if w.section > -1:
                    w.section = orig_sections[w.section]
            return (new_sections, words)

        # clean up the lists
        only_self = organize(self.sections, only_self)
        both_lists = organize(self.sections, both_lists)
        only_list2 = organize(list2.sections, only_list2)

        # new names
        only_self_name = self.name + '_minus_' + list2.name
        both_lists_name = self.name + '_intersecting_' + list2.name
        only_list2_name = list2.name + '_minus_' + self.name

        # done!
        only_self = ChList(only_self_name,
                           sections=only_self[0],
                           words=only_self[1])
        both_lists = ChList(both_lists_name,
                            sections=both_lists[0],
                            words=both_lists[1])
        only_list2 = ChList(only_list2_name,
                            sections=only_list2[0],
                            words=only_list2[1])

        return (only_self, both_lists, only_list2)
