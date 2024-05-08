from utils import HiatusParser

# tests
hp = HiatusParser()

preprocessing_tests = [
    'кизонь',
    'ивадема',
    'кодома',
    'керьтефтемс',
    'учема'
]

stress_position_tests = [
    'ава',
    'куду',
    'учема',
    'илезь',
    'кельтефтема',
]

final_segment_tests = [
    'ава',
    'прясь',
    'ши',
    'кельтеши',
    'калдо',
    'нан',
    'авомс',
    'калдамс',
    'удумс',
]

homorganic_glides_tests = [
    ('удомс', 'V'),
    ('видиемс', 'V'),
    ('мумс', 'V'),
    ('ава', 'N'),
    ('куду', 'N'),
    ('вано', 'N'),
    ('ялгаксши', 'N'),
]

for test in preprocessing_tests:
    print(test, hp.preprocess_word(test))

print()

for test in stress_position_tests:
    print(test, hp.compute_stress_position(test))

print()

for test in final_segment_tests:
    print(test, hp.final_segment(test))

print()

for test in homorganic_glides_tests:
    print(test, hp.homorganic_glides(*test))