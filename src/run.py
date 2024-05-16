import json
import math
import os
import sys

import pandas as pd

from utils import *

sys.path.append('/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages')

import gspread
from oauth2client.service_account import ServiceAccountCredentials

with open('config.json', 'r') as f:
    config = json.load(f)

hp = HiatusParser()

def process_file(path):
    if 'processed_df.csv' in os.listdir('output/' + path):
        return pd.read_csv('output/' + path + '/processed_df.csv')
    df = read_dict_file('data/' + path + '.txt')
    df = process_homophones(df)
    df = mark_loans(df)
    df = df.drop_duplicates(subset=['lemma', 'grammar'])
    df.chapter = df.chapter.replace({'': 'А'})
    hg_context = [hp.homorganic_glides(word, pos) for word, pos in
                  zip(df.lemma.tolist(), df.grammar.tolist())]
    df['hg_context'] = hg_context
    df.to_csv('output/' + path + '/processed_df.csv')
    return df

def get_candidates(path):
    df = process_file(path)
    candidates = df.loc[df.hg_context].drop_duplicates(subset='lemma')
    if config['live_editing']:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
        gc = gspread.authorize(creds)

        def create_new_sheet_if_not_exist(title):
            if title not in [sh.title for sh in gc.openall()]:
                gc.create(title)
            print([sh.title for sh in gc.openall()])

        create_new_sheet_if_not_exist('moksha_edit_loans')

        sh = gc.open("moksha_edit_loans")
        sh.share(config['email'], perm_type='user', role='writer')

        worksheet = sh.worksheet('new_sheet')
        worksheet.clear()
        worksheet.update([candidates.columns.values.tolist()] + candidates.values.tolist())

        print('prepare to edit the google sheet \"moksha_edit_loans\" shared with you. mark loans with final stress')
        inp = ''
        while inp != 'done':
            inp = input('type \"done\" when you are done: ')
        cand_df = pd.DataFrame(worksheet.get_all_values()[1:], columns=worksheet.get_all_values()[0])
        cand_df.to_csv('output/' + path + '/clean_candidates.csv')
    else:
        cand_df = pd.read_csv('output/' + path + '/clean_candidates.csv')
    return cand_df

def run_tolerance_principle(candidates):
    theta = candidates.hg_context.sum() / math.log(candidates.hg_context.sum())
    if config['live_editing']:
        candidates = candidates.loc[candidates.hg_context == 'TRUE']
        loan_count = (candidates.loan == 'TRUE').sum()
    else:
        candidates = candidates.loc[candidates.hg_context]
        loan_count = candidates.loan.sum()
        # loan_count = (candidates.loan == 'TRUE').sum()

    print('total candidate count:', candidates.shape[0])
    print('theta:', math.floor(theta))
    print('loan count:', loan_count)
    print('NOT PRODUCTIVE; over' if loan_count > theta else 'PRODUCTIVE; under', 'the threshold for productivity')

def main():
    for fn in filter(lambda x: 'txt' in x, os.listdir('data')):
        path = fn.split('.')[0]
        try:
            os.mkdir('output/' + path)
        except:
            print('directory already exists, continuing')
        candidates = get_candidates(path)
        run_tolerance_principle(candidates)

if __name__ == '__main__':
    main()
