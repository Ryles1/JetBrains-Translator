import requests
import bs4
import os
import sys


def get_elems(dirn, translate_word, s=None):
    global header

    url = f'https://context.reverso.net/translation/{dirn}/{translate_word}'
    if not s:
        r = requests.get(url, headers=header)
        try:
            r.raise_for_status()
        except HTTPError:
            print('Something wrong with your internet connection')
            sys.exit()
    else:
        r = s.get(url, headers=header)

    soup = bs4.BeautifulSoup(r.content, 'html.parser')
    wordElems = soup.select('div#translations-content a')
    if len(wordElems) == 0:
        print(f'Sorry, unable to find {translate_word}')
        sys.exit()
    translations = [elem.text for elem in wordElems]

    sentenceElems = soup.select('div.example div span.text')
    sentences = [elem.text for elem in sentenceElems]
    return translations, sentences


def print_examples(translations, sentences, language):
    # print('Content examples:\n')
    print(f'{language} Translations:')
    for t in range(5):
        print(translations[t].strip())

    print(f'\n{language} Examples:')
    for i, s in enumerate(sentences):
        print(s.strip())
        if i % 2 == 1:
            print()
        if i == 9:
            break


def write_file(t, s, l, fn):
    if os.path.exists(fn):
        with open(fn, 'a', encoding='utf-8') as f:
            f.write(f'{l.capitalize()} Translations:\n')
            f.write(t.strip() + '\n\n')
            f.write(f'{l.capitalize()} Examples:\n')
            for i in s:
                f.write(i.strip() + '\n')
            f.write('\n')
    else:
        with open(fn, 'w', encoding='utf-8') as f:
            f.write(f'{l.capitalize()} Translations:\n')
            f.write(t.strip())
            f.write('\n\n')
            f.write(f'{l.capitalize()} Examples:\n')
            for i in s:
                f.write(i.strip())
                f.write('\n')
            f.write('\n')


def translate_one(from_lang, to_lang, word, sesh=None):
    lang = '-'.join([from_lang, to_lang])
    if not sesh:
        raw_translations, raw_sentences = get_elems(lang, word)
    else:
        raw_translations, raw_sentences = get_elems(lang, word, sesh)
    return raw_translations, raw_sentences


def translate_all(from_lang, word, language_list):
    global header
    file_name = f'{word}.txt'
    if os.path.exists(file_name):
        os.remove(file_name)
    url = f'https://context.reverso.net'
    session = requests.Session()
    s = session.get(url, headers=header)
    try:
        s.raise_for_status()
    except HTTPError:
        print('Something wrong with your internet connection')
        sys.exit()
    for lang in language_list:
        if lang == from_lang:
            continue
        translations, sentences = translate_one(from_lang, lang, word, session)
        write_file(translations[0], sentences[:2], lang, file_name)
    session.close()


def main_no_args():
    global languages
    print("Hello, welcome to the translator. Translator supports:\n \
        1. Arabic\n \
        2. German\n \
        3. English\n \
        4. Spanish\n \
        5. French\n \
        6. Hebrew\n \
        7. Japanese\n \
        8. Dutch\n \
        9. Polish\n \
        10. Portuguese\n \
        11. Romanian\n \
        12. Russian\n \
        13. Turkish")
    start = int(input('Type the number of your language: ')) - 1
    end1 = int(input('Type the number of the language you want to translate to or "0" to translate to all languages: '))
    if end1 == 0:
        try:
            start = languages[start]
            end = None
        except IndexError:
            print('Enter one of the options.')
            main()
    else:
        try:
            start = languages[start]
            end = languages[end1 - 1]
        except IndexError:
            print('Enter one of the options.')
            main()

    word = input('Type the word you want to translate:').lower()

    if not end:
        translate_all(start, word, languages)
        with open(f'{word}.txt') as f:
            for line in f:
                print(line)
    else:
        print(f'You chose "{end}" as the language to translate "{word}" to.')
        raw_translations, raw_sentences = translate_one(start, end, word)
        print_examples(raw_translations, raw_sentences, end.capitalize())


def main(args):
    global languages
    start_lang, to_lang, translate_word = args[1], args[2], args[3]
    if start_lang not in languages:
        print(f'Sorry, the program doesn\'t support {start_lang}')
    elif to_lang != 'all' and to_lang not in languages:
        print(f'Sorry, the program doesn\'t support {to_lang}')
    elif to_lang == 'all':
        translate_all(start_lang, translate_word, languages)
        with open(f'{translate_word}.txt') as f:
            for line in f:
                print(line)
    elif start_lang in languages and to_lang in languages:
        raw_translations, raw_sentences = translate_one(start_lang, to_lang, translate_word)
        print_examples(raw_translations, raw_sentences, to_lang.capitalize())
    else:
        print('Please enter valid languages.')


if __name__ == '__main__':
    header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0'}
    languages = ('arabic', 'german', 'english', 'spanish', 'french', 'hebrew', 'japanese', 'dutch',
                 'polish', 'portuguese', 'romanian', 'russian', 'turkish',)
    if len(sys.argv) == 1:
        main_no_args()
    else:
        main(sys.argv)
