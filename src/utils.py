import pandas as pd
import numpy as np
import re


def read_dict_file(fn):
    with open(fn, 'r') as f:
        content = f.readlines()

    df = pd.DataFrame(columns=['chapter', 'lemma', 'grammar', 'word_th_trans_en', 'freq'])
    current_row = []
    current_chapter = ''

    for line in content:
        line = line.strip()
        if line in 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ':  # start of chapter
            current_chapter = line
            current_row = []
            current_row.append(current_chapter)
        else:
            if line not in ['', 'lemma', 'grammar', 'word_th_trans_en', 'freq']:
                current_row.append(line)
            if line.isdigit():
                if len(current_row) < 5:
                    print(current_row)
                elif len(current_row) == 5:
                    df.loc[len(df.index)] = current_row
                    current_row = [current_chapter]
    df.freq = df.freq.astype(int)
    return df

def mark_loans(original_df):
    df = original_df.copy()
    df['loan'] = (df.lemma == df.word_th_trans_en) |  \
        (df.word_th_trans_en.str.startswith(r'[А-ЯЁ]'))  # exclude loans and proper names
    return df

def process_homophones(original_df):
    df = original_df.copy()
    for idx, values in df.iterrows():
        lemmas = values[1].split('/')
        grammars = values[2].split(' | ')
        word_th_trans_ens = values[-2].split(' | ')

        df.drop(labels=[idx], inplace=True)
        if len(lemmas) == len(grammars):
            new_rows = pd.DataFrame({
                'chapter': [values[0]] * len(lemmas),
                'lemma': lemmas,
                'grammar': grammars,
                'word_th_trans_en': word_th_trans_ens if len(word_th_trans_ens) == len(lemmas) else values[-2],
                'freq': [max(values[-1] // len(lemmas), 1)] * len(lemmas),
            })
            df = pd.concat((df, new_rows))

    return df.sort_values('chapter').reset_index(drop=True)
class HiatusParser:
    def __init__(self):
        self.vowels = 'аяэеиыуюоёə'
        self.heavy_vowels = 'аяэеоё'
        self.light_vowels = 'иыуюə'

    def preprocess_word(self, word, pos='V'):  # insert schwas
        seen_vowel = False
        corrected_word = ''
        for segment in word:
            if segment in 'оёэе':
                if seen_vowel:
                    corrected_word += 'ə'
                else:
                    corrected_word += segment
            else:
                corrected_word += segment
            if segment in self.vowels:
                seen_vowel = True

        # strip verbal bases
        if corrected_word.endswith('əмс') and pos == 'V':
            corrected_word = re.sub('əмс', '', corrected_word)
        elif corrected_word.endswith('мс') and pos == 'V':
            corrected_word = re.sub('мс', '', corrected_word)

        # exclude shi-composites
        if corrected_word.endswith('ши') and pos == 'N' and self.syllable_count(word) > 1:
            corrected_word = corrected_word + '_'

        return corrected_word

    def compute_stress_position(self, word):
        word = self.preprocess_word(word)
        word_vowels = list(filter(lambda x: x in self.vowels, word))
        stressed = 0
        for idx, vowel in enumerate(word_vowels):
            if vowel in self.heavy_vowels:
                stressed = idx
                break
        return -1 if stressed == len(word_vowels) - 1 else stressed

    def final_segment(self, word, pos='V'):
        word = self.preprocess_word(word, pos)
        if word[-1] in self.light_vowels and self.compute_stress_position(word) == -1:
            return 'VV'
        elif word[-1] in self.light_vowels and word[-1] != 'ə':
            return 'V_high'
        elif word[-1] == 'ə':
            return 'V_ə'
        elif word[-1] in self.heavy_vowels:
            return 'VV'
        else:
            return 'C'

    def syllable_count(self, word):
        return len(list(filter(lambda x: x in self.vowels, word)))

    def j_insertion(self, word, pos):
        pos_ = pos.split(', ')
        if self.syllable_count(word) == 1 and ('N' in pos_ or 'V' in pos_):
            return True
        return False

    def homorganic_glides(self, word, pos):
        pos_ = pos.split(', ')
        if not self.j_insertion(word, pos) and self.final_segment(word, pos) == 'V_high' and (
                'N' in pos_ or 'V' in pos_):
            return True
        return False

