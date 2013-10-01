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
    Open a cedict file as a python dictionary.

    Args:
        cedict_file (file): The file object
        key ('trad'/'simp'): The property which is used as a key in the
            python dictionary.
    Returns:
        cedict (dict): The dictionary has the following structure:
            { '囧': [
                ('simp/trad', 'jiong1', (meaning1, meaning2), {}),
                ('simp/trad', 'hao3', (meaningA), {'tw': 'hao2',
                                                   'cl':'char[piny]'}),
                ('simp/trad', 'la4', (meaningX, meaningY), {})
                ]
            }
            Each pronunciation has a separate entry, which consists of:
            1. Either the simplified or traditional version of the key.
            2. The pinyin, space seperated as found in the file.
            3. A tuple with all the meanings
            4. A dictionary with extra info if available, for now:
                tw for taiwanese pronunciation
                cl for a measure word
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

def open_tatoeba(sentences=None,
                 links=None,
                 primary_lang='cmn',
                 secondary_langs = None):
    """
    Get grouped sentences from the tatoeba files.

    Args:
        sentences (file): The file with the sentences, detailed or not
        links (file): The file with the links between sentences
        primary_lang (str): The language code for the primary language for
            which you want to find translations, default 'cmn' (Chinese)
        secondary_langs([str]): The languages for the translations, a sentence
            is only included in the result if there is a version in the primary
            language and at least one of the secondary languages
    Returns:
        result (list): A list of the sentences, structured like this:
            [
            ((1st sent. in prim. lang.),
            (1st sent. in 1st sec. lang.),
            (1st sent. in 2nd sec. lang.)),
            ((2nd sent. in prim. lang), (...), (...))
            ...
            ]
    """

    if not secondary_langs:
        secondary_langs = ['eng']
    all_langs = {primary_lang: set()}
    for lang in secondary_langs:
        all_langs[lang] = set()

    # first run: get ids of all sentences in relevant languages
    for line in sentences:
        line = line.strip()
        line = line.split('\t')
        sentence_id = line[0]
        sentence_lang = line[1]
        if sentence_lang in all_langs:
            all_langs[sentence_lang].add(sentence_id)

    all_sec_lang_ids = set()
    for lang in secondary_langs:
        all_sec_lang_ids.update(all_langs[lang])

    # get links between sentences
    primary_lang_index = {}
    secondary_lang_relevant = set()
    for line in links:
        line = line.strip()
        line = line.split('\t')
        id1 = line[0]
        id2 = line[1]
        if (id1 in primary_lang_index) and\
        (id2 in all_sec_lang_ids):
            primary_lang_index[id1].append(id2)
            secondary_lang_relevant.add(id2)
        else:
            if (id1 in all_langs[primary_lang]) and\
            (id2 in all_sec_lang_ids):
                primary_lang_index[id1] = [id2]
                secondary_lang_relevant.add(id2)

    relevant_sentences = {}

    # second run: get relevant sentences
    sentences.seek(0)
    for line in sentences:
        line = line.strip()
        line = line.split('\t')
        sentence_id = line[0]
        sentence_lang = line[1]
        if (sentence_id in primary_lang_index) or\
        (sentence_id in secondary_lang_relevant):
            relevant_sentences[sentence_id] = line

    result = []
    lang_index = {}
    for i, lang in enumerate(secondary_langs):
        lang_index[lang] = i + 1

    # group sentences and add them to result
    boilerplate = ['' for i in range(len(secondary_langs) + 1)]
    for id1, id2s in primary_lang_index.items():
        item = copy.copy(boilerplate)
        item[0] = relevant_sentences[id1]
        for id2 in id2s:
            sentence2 = relevant_sentences[id2]
            lang2 = sentence2[1]
            item[lang_index[lang2]] = sentence2
        result.append(item)

    return result
