#!/usr/bin/python3




import argparse

parser = argparse.ArgumentParser(description="Выделение грамматических конструкций английского языка в PDF файлах")
parser.add_argument("path", type=str, help="Путь до файла") 
args = parser.parse_args()

import nltk
# Если пакет отсутствует, начните по его загрузке
nltk.download('tagsets')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

#tagdict = nltk.data.load('help/tagsets/upenn_tagset.pickle')


import fitz
from pathlib import Path

file_name = Path(args.path).stem
file_dir_path = Path(args.path).parent.resolve()


# Вычитывание разметки

doc = fitz.open(args.path)

text = []
for i,doc_page in enumerate(doc):
    page = {}
    for annot in doc_page.annots():
        page[annot.info['content']] = doc_page.get_text(clip=annot.rect)
    keys = sorted(page.keys())
    print(f'{i}', keys)
    text.append(page)

# Обыединение "разорванных" абзацев
for page_i,page in enumerate(text):
    keys = list(reversed(sorted(page.keys())))
#     print(f'{keys=}')
    for i,k in enumerate(keys):
        if len(k)>=3 and (k[-2] == 'p' or k[-1] == 'p'):
#             print(k, k[-2])
            if k[-2] == 'p': # part prev page
                pp_i = page_i-1
                pp_keysRevers = reversed(sorted(text[pp_i].keys()))
                
                pp_k = None
                for pp_k in pp_keysRevers : 
                    if pp_k[0].isdigit():
#                         print(f'{page_i=}, {pp_i=}, {pp_k=}')
                        break
                text[pp_i][pp_k] = text[pp_i][pp_k] + page[k]
                        
                    
            else: # part prev column
#                 print(f'{i=}')
                dest_k = keys[i+1]
#                 print(f'{k=} {dest_k=}')
                page[dest_k] = page[dest_k] + page[k] 
            page.pop(k, None)

# Токинезация
tokenaise_text = []
for page in text:
    tokenaise_page = {}
    keys = sorted(page.keys())
    for k in keys:
        sents = nltk.sent_tokenize(page[k])
        s = [nltk.word_tokenize(s) for s in sents]
        tokenaise_page[k] = nltk.pos_tag_sents(s, tagset=None, lang='eng')
    tokenaise_text.append(tokenaise_page)

# Экспор в html
class Tag():
    def __init__(self, file, open_tag, close_tag = None):
        self.file = file
        self.open_tag = open_tag
        self.close_tag = close_tag
        if close_tag is None:
            self.close_tag = f'</{self.open_tag[1:]}'
        
    def __enter__(self):
        self.file.write(self.open_tag)

    def __exit__(self, type, value, traceback):
        self.file.write(self.close_tag)

colors_parts = {'f': '#fffcde'}

tagset = {'CC':'Coordinating conjunction',
          'CD':'Cardinal number',
          'DT':'Determiner',
          'EX':'Existential there',
          'FW':'Foreign word',
          'IN':'Preposition or subordinating conjunction',
          'JJ':'Adjective',
          'JJR':'Adjective, comparative',
          'JJS':'Adjective, superlative',
          'LS':'List item marker',
          'MD':'Modal',
          'NN':'Noun, singular or mass',
          'NNS':'Noun, plural',
          'NNP':'Proper noun, singular',
          'NNPS':'Proper noun, plural',
          'PDT':'Predeterminer',
          'POS':'Possessive ending',
          'PRP':'Personal pronoun',
          'PRP$':'Possessive pronoun',
          'RB':'Adverb',
          'RBR':'Adverb, comparative',
          'RBS':'Adverb, superlative',
          'RP':'Particle',
          'SYM':'Symbol',
          'TO':'to',
          'UH':'Interjection',
          'VB':'Verb, base form',
          'VBD':'Verb, past tense',
          'VBG':'Verb, gerund or present participle',
          'VBN':'Verb, past participle',
          'VBP':'Verb, non-3rd person singular present',
          'VBZ':'Verb, 3rd person singular present',
          'WDT':'Wh-determiner',
          'WP':'Wh-pronoun',
          'WP$':'Possessive wh-pronoun',
          'WRB':'Wh-adverb',
          '.':'.'}

colors_tags = {'VB': '#ff0000',
               'VBD': '#00ff00',
               'VBG': '#0000ff',
               'VBN': '#ff00ff',
               'VBP': '#ffff00',
               'VBZ': '#00ffff',
               'RP': '#800000',
               'MD': '#008000',
               '.': '#000000'}

def colorize_word(tagged_word):
    keys = colors_tags.keys()
    if tagged_word[1] in keys:
        word = f'<text style="background-color: {colors_tags[tagged_word[1]]}">{tagged_word[0]}</text>'
        return word
    return tagged_word[0]

# # легенда
# with open(f'{file_dir_path}/{file_name}-legend.html', 'w') as f:
#         for c in colors_tags:

def write_legend(file):
    with Tag(file, '<pre>', '</pre>\n') as t:
        file.write('Легенда:\n\n')
        for k,v in colors_tags.items():
            file.write(colorize_word(('***',k)))
            file.write(f' - {tagset[k]}\n')
            
def write_doc(file):
    for pi,page in enumerate(tokenaise_text):
        file.write(f'<h4>[--- Page {pi+1} ---]</h3>\n')
        keys = sorted(page.keys())
        tag = ''
        close_tag = None
        for k in keys:
            if len(k) == 0: # это на случай ошибки в разметке, когда область даже не показывается во вьювере
                continue 
            tag = '<p>'
            if len(k)>1 and k[-1] == 'h':
                tag = '<h3>'
            elif k[0] == 'f':
                tag = f'<p  style="background-color: {colors_parts["f"]}">'
                close_tag = '</p>'

            with Tag(file, tag, close_tag) as tparagraff:
                first_word = True
                for sentence in page[k]:
                    for word in sentence:
                        word_tag = word[1]
                        if word_tag != '.' and word_tag != ',':
                            first_word = False
                            file.write(' ')

                        file.write( colorize_word(word) )
    

with open(f'html_base/Base.html', 'r') as f_html_base:
    with open(f'{file_dir_path}/{file_name}.html', 'w') as f_dest:
        for line in f_html_base:
            if line != '' and line[0] == '@':
                if 'legend' in line:
                    write_legend(f_dest)
                elif 'doc' in line:
                    write_doc(f_dest)
            else:
                f_dest.write(line)
