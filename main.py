#!/usr/bin/python3

import fitz
import argparse
import os
import enum
import nltk

parser = argparse.ArgumentParser(description="Выделение грамматических конструкций английского языка в PDF файлах")
parser.add_argument("path", type=str, help="Путь до файла") 
args = parser.parse_args()

# Если пакет отсутствует, начните по его загрузке
nltk.download('tagsets')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

tagdict = nltk.data.load('help/tagsets/upenn_tagset.pickle')

class Word_type(enum.Enum):
    # Основные типы:
    noun = 0  # cуществительное, местоимение
    verb = 1  # глагол, инфинитив
    adj = 2  # прилогательное
    adv = 3  # наречие
    # Герундий - noun + verb 
    # Отглагольное прилогательное, причастие, деепричастие: verb + adj
    # ...
    prep = 4  # предлог
    conj = 5  # союз

tagset = {'CC': 	'Coordinating conjunction',
          'CD': 	'Cardinal number',
          'DT': 	'Determiner',
          'EX': 	'Existential there',
          'FW': 	'Foreign word',
          'IN': 	'Preposition or subordinating conjunction',
          'JJ': 	'Adjective',
          'JJR': 	'Adjective, comparative',
          'JJS': 	'Adjective, superlative',
          'LS': 	'List item marker',
          'MD': 	'Modal',
          'NN': 	'Noun, singular or mass',
          'NNS': 	'Noun, plural',
          'NNP': 	'Proper noun, singular',
          'NNPS': 	'Proper noun, plural',
          'PDT': 	'Predeterminer',
          'POS': 	'Possessive ending',
          'PRP': 	'Personal pronoun',
          'PRP$': 	'Possessive pronoun',
          'RB': 	'Adverb',
          'RBR': 	'Adverb, comparative',
          'RBS': 	'Adverb, superlative',
          'RP': 	'Particle',
          'SYM': 	'Symbol',
          'TO': 	'to',
          'UH': 	'Interjection',
          'VB': 	'Verb, base form',
          'VBD': 	'Verb, past tense',
          'VBG': 	'Verb, gerund or present participle',
          'VBN': 	'Verb, past participle',
          'VBP': 	'Verb, non-3rd person singular present',
          'VBZ': 	'Verb, 3rd person singular present',
          'WDT': 	'Wh-determiner',
          'WP': 	'Wh-pronoun',
          'WP$': 	'Possessive wh-pronoun',
          'WRB': 	'Wh-adverb'}

word_type_color = {'VB': (0.75, 0.75, 0),
                   'VBD': (0.5, 0.5, 0),
                   'VBG': (0.5, 0.75, 0.2),
                   'VBN': (0.75, 0.5, 0),
                   'VBP': (0.75, 0.5, 0.75),
                   'VBZ': (0.75, 0.2, 0.75),
                   'RP': (0.75, 0.5, 0.5),
                   'MD': (0.75, 0.3, 0.3)}

def get_type_word(word):
   pass 

def mark_word(page):
    """Underline each word that contains 'text'.
    """
    found = 0
    wlist = page.get_text("words", delimiters=None)  # make the word list
    text = []
    sentense = []
    text_index = [] # список предложений с индексами, для того чтобы можно было найти слово в w list
    sentense_index = []
    for i,w in enumerate(wlist):
        if  w[4][-1] == '.': # конец предложения
            print('Q', w[4])
            text.append(sentense)
            sentense.clear()
            text_index.append(sentense_index)
            sentense_index.clear()
        else:
            sentense.append(w[4])
            sentense_index.append(i)
            
    # print(text, sentense)
    words_type = nltk.pos_tag_sents(text)
    # print(words_type)

    for w in words_type:
        if w == 'built':
            print(w, ':', word_type)


    for w in wlist:  # scan through all words on page
        # структура w: https://pymupdf.readthedocs.io/en/latest/textpage.html#TextPage.extractWORDS
        # if text in w[4]:  # w[4] is the word's string
        word_type = nltk.pos_tag([w[4]])[0][1]
        if w[4] == 'built':
            print(w[4], ':', word_type)

        for w_c_k in word_type_color.keys(): 
            if w_c_k == word_type:
                found += 1  # count
                # r = fitz.Rect(w[:4])  # make rect from word bbox
                annot = page.add_highlight_annot (w[:4])  # underline
                info = annot.info                      # get info dict
                info["title"] = w[4]
                info["content"] = tagset[word_type] # in popup window
                annot.set_info(info)
                annot.set_colors({"stroke":word_type_color[w_c_k]})
                annot.update()
    return found

if __name__ == '__main__':
    doc = fitz.open(args.path)

    doc.


    new_doc = False
    for page in doc:
        if mark_word(page) > 0 :
            new_doc = True
    if new_doc:
        name = os.path.splitext(args.path)
        name = name[0] + ' - translate helper' + name[1]
        doc.save(name)


    
