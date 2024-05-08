# Tolerance Principle check for Moksha vowel spreading

There is a hiatus avoiding strategy in Moksha that I argue to be produced by a rule rather than from lexical marking. When a polysyllabic base ending in a high vowel meets a vowel-initial suffix, a homorganic glide appears (e.g. *kelu + ən' = keluvən'* "birch-GEN").

This directory contains source code that reproduces my argument in favor of vowel spreading *rule* as a reason behind this phenomenon rather than lexically encoded floating glides. According to the Tolerance Principle (Yang 2015), the number of exceptions to a rule can only be as high as N / ln(N), where N is the number of items to which the rule applies. I show that the homorganic glide insertion process cannot possibly come from lexical marking, since it would constitute too many exceptions to the hiatus resolution rule of Moksha. If glide formation itself is treated as a rule, however, it can withstand pressure from loanwords, on which this rule does not work.

Despite not passing the Wug test, glide formation is still a rule. See [this manuscript](https://ling.auf.net/lingbuzz/007524) for more.

To reproduce my results, run the following shell script:

`python src/run.py`

## Data

I use the [Moksha corpora](http://moksha.web-corpora.net) developed and maintained by Timofey Arkhangelsky.