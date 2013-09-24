#from __future__ import unicode_literals
#from __future__ import print_function
#from MaWord import *
#from tools import *
import re

TEXT_FILE_DEFAULT = {
    'entry_delimiter': '\n',
    'attr_delimiter': '\t',
    'sec_start': '//',
    'sec_delimiter': '/',
    'comment_start': '#',
    # use 'simp[trad]' for a pleco-like format: simp[trad]
    'attr_order': ['simp[trad]', 'pinyin', 'definition']
    }


def open_text_list(word_file, custom=None):
    """
    Open a list in the format used by skritter/pleco.

    Empty sections are skipped!

    Args:
        word_file (file object): a file object opened to read the file
    Returns:
        sections (list): a list of lists which contain the complete section
            name, e.g.
            [['Book 1', 'Chapter 1', 'Listing 1'],
            ['Book 1', 'Chapter 1', Listing 2']]
        word_list (list): a list of dictionaries, reach representing a word
        using the keys 'simp','trad','pinyin','definition','section_no',
        'entry_no'. The default value for each key is ''.
        section_no is index of the section for this word in the section list
        entry_no the index of this word in word_list
    """

    if not custom:
        custom = TEXT_FILE_DEFAULT
    else:
        for k, v in TEXT_FILE_DEFAULT.items():
            if k not in custom:
                custom[k] = v

    raw_text = word_file.read().strip()
    entries = [entry.strip() for entry in
               raw_text.split(custom['entry_delimiter'])]

    words = []
    current_section_no = -1
    sections = []
    current_entry_no = -1
    previous_line_section = False

    for entry in entries:
        if entry == '' or entry.startswith(custom['comment_start']):
            pass
        elif entry.startswith(custom['sec_start']):  # section heading
            current_section = entry[len(custom['sec_start']):]
            current_section = current_section.split(custom['sec_delimiter'])
            if previous_line_section:  # overwrite empty section
                sections[-1] = current_section
            else:
                current_section_no += 1
                sections.append(current_section)
            previous_line_section = True
        else:                       # an entry
            previous_line_section = False
            current_entry_no += 1

            attributes = entry.split(custom['attr_delimiter'])
            new_word = {}
            for (name, attribute) in zip(custom['attr_order'], attributes):
                # special treatment for pleco files with simp[trad]
                if name == 'simp[trad]':
                    if '[' in attribute:
                        if attribute.startswith('['):
                            new_word['trad'] = attribute[1:-1]
                        else:
                            new_word['simp'] = attribute[:attribute.find('[')]
                            new_word['trad'] =\
                                    attribute[attribute.find('[') + 1:-1]
                    else:
                        new_word['simp'] = attribute
                else:
                    new_word[name] = attribute

            new_word['section'] = current_section_no
            new_word['number'] = current_entry_no
            words.append(new_word)

    return (sections, words)


def save_text_list(word_file, sections, words, custom=None):
    """
    Save a list as a text file.

    Args:
        word_file (file object): a file object opened to read the file
        sections (list): a list of lists which contain the complete section
            name, e.g.
            [['Book 1', 'Chapter 1', 'Listing 1'],
            ['Book 1', 'Chapter 1', Listing 2']]
        words (list): a list of dictionaries, reach representing a word
            using the keys 'simp','trad','pinyin','definition','section_no',
            'entry_no' plus others. The default value for each key is ''.
            section_no is index of the section for this word in
                the section list
            entry_no the index of this word in word_list
            custom (dict): used to specify the file format,
                same as in open_text_list
    """

    if not custom:
        custom = TEXT_FILE_DEFAULT
    else:
        for k, v in TEXT_FILE_DEFAULT.items():
            if k not in custom:
                custom[k] = v

    output_lines = []
    current_section_no = -1
    for word in words:
        current_line = []
        # add new section
        if word['section'] != current_section_no:
            if word['section'] < len(sections):
                output_lines.append(
                    custom['sec_start'] + custom['sec_delimiter'].join(
                        sections[word['section']]))
            else:
                output_lines.append('')
            current_section_no = word['section']

        # add word
        for name in custom['attr_order']:
            if name == 'simp[trad]':
                simp = word['simp'] if 'simp' in word else ''
                trad = word['trad'] if 'trad' in word else ''
                current_line.append(simp + '[' + trad + ']')
            else:
                attr = word[name] if name in word else ''
                current_line.append(attr)

        output_lines.append(custom['attr_delimiter'].join(current_line))

    word_file.write(custom['entry_delimiter'].join(output_lines))


def open_cedict(cedict_file, key='trad'):
    """
    output format:
    { '囧': (
        ('simp/trad', 'jiong1', (meaning1, meaning2), {}),
        ('simp/trad', 'hao3', (meaningA), {'tw': 'hao2', 'cl':'char[piny]')}),
        ('simp/trad', 'la4', (meaningX, meaningY), {})
        )
    }
    """
    cedict = {}
    line_pattern = re.compile("^(.*?)\s{1}(.*?)\s{1}(\[.*?\])\s{1}(\/.*\/)$")
    for line in cedict_file:
        line = line.strip()
        if line[0] == '#':
            continue

        items = line_pattern.match(line)
        items = items.groups()
        trad = items[0]
        simp = items[1]
        pinyin = items[2][1:-1]
        definitions = items[3][1:-1].split('/')

        extra = {}
        for i, definition in enumerate(definitions):
            if definition.startswith('Taiwan pr.'):
                extra['tw'] = definition[11:].strip('[]')
                definitions[i] = ''
            if definition.startswith('CL:'):
                extra['cl'] = definition[3:]
                definitions[i] = ''
        definitions = tuple([d for d in definitions if not d == ''])

        if key == 'trad':
            char_key = trad
            simp_trad = simp
        else:
            char_key = simp
            simp_trad = trad
        entry = (simp_trad, pinyin, definitions, extra)
        if char_key in cedict:
            cedict[char_key].append(entry)
        else:
            cedict[char_key] = [entry]
    return cedict


def open_unihan(unihan_file, kvalues):
    """
    Open one unihan file and read the indicated values for all characters.

    Args:
        word_file (file object): the unihan file
        kvalues (list): a list of values that should be extracted,
            e.g. ['kMandarin','kDefinition']
    Returns:
        unihan_dic (dictionary): a dictionary with the chinese characters as
            key, each having a dictionary with the requested kvalues.
            e.g. {'中‘： {'kMandarin': 'zhong', 'kDefinition': 'middle'}, ...}
    """

    unihan_dic = {}

    for word_line in unihan_file:
        word_line = word_line.strip()
        items = word_line.split('\t')
        if len(items) == 3:
            kvalue = items[1].strip()
        else:
            continue

        if kvalue in kvalues:
            hanzi = chr(int(items[0][2:], 16))

            if kvalue == 'kMandarin':
                content = items[2].split(',')
            elif kvalue == 'kHanyuPinyin':
                content = [y for x in items[2].split(' ')
                           for y in x[x.find(':') + 1:].split(',')]
            else:
                content = items[2].strip()

            if hanzi in unihan_dic:
                unihan_dic[hanzi][kvalue] = content
            else:
                unihan_dic[hanzi] = {kvalue: content}

    return unihan_dic
