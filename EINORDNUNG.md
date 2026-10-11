# What prompts coverage of LGBTQ+?

🇩🇪 [Deutsche Version](EINORDNUNG.de.md) · [Back to the main page of the project](README.md)

This analysis adds a question of content to the project. The main analysis counts how often the four news websites name queer people in the headline or in the kicker. This part examines what prompts that coverage: violence, measures taken by the state, law, politics, or society and culture.

It is based on the same items as the main analysis, that is 494 text items and 57 videos from tagesschau.de, SPIEGEL, WELT and ZDFheute in the period from 1 November 2024 to 30 September 2026. The classification was carried out on 11 October 2026.

## Method

Two language models independently assigned every item to exactly one of six categories. For this purpose the models received only the kicker and the headline, and for tagesschau.de also the teaser text. They did not know the article itself and were instructed not to add anything from their own knowledge. For every assignment they gave a reason in one sentence.

| Category | What it covers |
|---|---|
| Violence and crime | attacks, assaults, murders, threats and hate crime against queer people, including statistics on these |
| State measures against the group | bans, raids, arrests, laws or orders that restrict rights, and exclusion by authorities, the military or associations |
| Law and equality | court rulings, lawsuits, laws that extend or clarify rights, anti-discrimination |
| Politics and debate | parties, elections, opinion pieces, disputes over symbols or terms, demonstrations without violence |
| Society and culture | everyday life, portraits, coming out, sport, film, music, religion, history, festivals |
| Other | animals or plants, plays on words, and items whose occasion cannot be identified from headline and kicker |

If an item fits several categories, the one listed first in the table applies. An item about a court ruling following an attack is therefore counted under violence and not under law.

The classification by the model `gpt-5.6-sol` by OpenAI is treated as the main result. As a check, the same task was given to a second, smaller model, `mistral-small3.1`, which ran on my own computer via Ollama. Both models received the same instruction and the same categories, and their answer was restricted to a fixed format with exactly these six categories. The items were passed on in batches, 20 at a time for `gpt-5.6-sol` and 10 at a time for `mistral-small3.1`. The instruction and the categories are contained in full in the script `beitraege_einordnen.py`.

The [dashboard](https://neurodiversity-lgbtq-german-news.streamlit.app/) shows the results on its fourth page.

## Findings

The following figures are based on the classification by `gpt-5.6-sol`. The comparison with the second model follows afterwards.

### Text items

| Occasion | Items | Share |
|---|---:|---:|
| Society and culture | 157 | 31.8% |
| Politics and debate | 108 | 21.9% |
| State measures against the group | 105 | 21.3% |
| Violence and crime | 65 | 13.2% |
| Law and equality | 50 | 10.1% |
| Other | 9 | 1.8% |
| **Total** | **494** | **100%** |

Violence and state measures against the group together are the occasion for 170 of the 494 text items, which is 34.4 percent. About one item in three therefore goes back to an attack, a ban or a restriction. The largest single category, however, is society and culture at 31.8 percent. Coverage therefore does not consist mainly of reports on violence and bans, but these make up a considerable part of it.

### By source

| Source | Violence | State measures | Law | Politics | Society | Other | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| tagesschau.de | 8 | 12 | 5 | 6 | 11 | 0 | 42 |
| SPIEGEL | 25 | 46 | 16 | 37 | 74 | 5 | 203 |
| WELT | 28 | 31 | 23 | 56 | 60 | 4 | 202 |
| ZDFheute | 4 | 16 | 6 | 9 | 12 | 0 | 47 |
| **Total** | **65** | **105** | **50** | **108** | **157** | **9** | **494** |

The share of violence and state measures differs clearly between the websites:

| Source | Violence and state measures | Share |
|---|---:|---:|
| tagesschau.de | 20 of 42 | 47.6% |
| ZDFheute | 20 of 47 | 42.6% |
| SPIEGEL | 71 of 203 | 35.0% |
| WELT | 59 of 202 | 29.2% |

According to this classification, almost every second item on the two public-service websites goes back to violence or a state measure; at SPIEGEL and WELT it is about one in three. The number of items at tagesschau.de and ZDFheute is small, however, so that a few items change the share noticeably; for ZDFheute, the second model does not confirm the high share (see below). At WELT, politics and debate is almost as strongly represented, with 56 items, as society and culture with 60.

### Videos

| Occasion | Videos | Share |
|---|---:|---:|
| State measures against the group | 16 | 28.1% |
| Politics and debate | 13 | 22.8% |
| Society and culture | 10 | 17.5% |
| Violence and crime | 9 | 15.8% |
| Law and equality | 6 | 10.5% |
| Other | 3 | 5.3% |
| **Total** | **57** | **100%** |

Of the 57 videos, 25 fall under violence and state measures, which is 43.9 percent. Because of the small number, these shares are of limited reliability.

## Comparison of the two models

The two models assigned 391 of the 494 text items to the same category, which is 79.1 percent. For the videos it is 51 of 57, or 89.5 percent. Cohen's kappa, a measure of agreement that discounts matches occurring by chance, is 0.73 for the text items.

| Occasion | gpt-5.6-sol | Share | mistral-small3.1 | Share |
|---|---:|---:|---:|---:|
| Violence and crime | 65 | 13.2% | 59 | 11.9% |
| State measures against the group | 105 | 21.3% | 105 | 21.3% |
| Law and equality | 50 | 10.1% | 54 | 10.9% |
| Politics and debate | 108 | 21.9% | 96 | 19.4% |
| Society and culture | 157 | 31.8% | 176 | 35.6% |
| Other | 9 | 1.8% | 4 | 0.8% |
| **Total** | **494** | **100%** | **494** | **100%** |

In the overall picture, both models arrive at a similar result. Violence and state measures account for 34.4 percent of the text items according to `gpt-5.6-sol` and for 33.2 percent according to `mistral-small3.1` (164 of 494). In both cases, society and culture is the largest category.

The models differ most often at the boundary between politics and society: 21 items that `gpt-5.6-sol` classifies as politics and debate are listed under society and culture by `mistral-small3.1`. Five items that `gpt-5.6-sol` lists under other are assigned to violence by `mistral-small3.1`. The smaller model therefore did not consistently follow the rule that only acts against queer people count as violence.

By source, the share of violence and state measures differs more strongly between the models:

| Source | gpt-5.6-sol | mistral-small3.1 |
|---|---:|---:|
| tagesschau.de | 47.6% | 50.0% |
| ZDFheute | 42.6% | 34.0% |
| SPIEGEL | 35.0% | 35.5% |
| WELT | 29.2% | 27.2% |

With both models, tagesschau.de has the highest share and WELT the lowest. For ZDFheute, by contrast, the classifications diverge, so that no reliable statement can be made about this source.

## Check by hand

As a check, I classified a random sample of 50 items myself and compared it with the models. My classification matches that of `gpt-5.6-sol` in 46 of 50 cases (92 percent) and that of `mistral-small3.1` in 44 of 50 (88 percent).

I differ from `gpt-5.6-sol` in four cases. I assigned two items about a fine for a homophobic remark in sport to law and equality, whereas the model assigned them to society and culture. I also classified an item about a dispute over a legal opinion as law, the model as politics and debate. I listed an item about an attack after a Christopher Street Day parade under other, because the headline does not show that the people attacked are queer; the model lists it under violence.

The sample is small. With 50 items, each single one corresponds to two percentage points, and I saw the model's classification while checking.

## Limitations

- The classification was made by language models and not by trained coders. Agreement between two models does not prove that their classification is correct. Only a sample of 50 items was checked by hand.
- The models saw only the kicker and the headline, and for tagesschau.de also the teaser text. What the article is actually about may differ from this.
- Every item receives exactly one category. Items with several occasions are simplified by the fixed order of the categories.
- The category violence covers only acts against queer people. Items in which a queer person is named as the perpetrator are listed under other.
- Derogatory remarks that are not a criminal offence are not counted as violence. Where such items belong instead is not clear-cut: `gpt-5.6-sol` lists a penalty for a homophobic remark in sport under society and culture, whereas I assign it to law and equality.
- State measures also include exclusion by associations, for example in sport, although associations are not state bodies.
- The categories were chosen by me. Other categories or a different order would produce different shares.
- A language model does not necessarily return the same assignment for every item when the run is repeated.
- The analysis covers LGBTQ+ only. No classification by occasion was carried out for ADHD, autism and neurodiversity.

## Files

| File | Content |
|---|---|
| `beitraege_einordnen.py` | passes the items to `gpt-5.6-sol` and counts the categories |
| `beitraege_einordnen_lokal.py` | the same classification with a local model via Ollama; sets both results side by side |
| `data/raw/einordnung_lgbtq_zahlen.csv` | number of items per source, type and category (`gpt-5.6-sol`) |
| `data/raw/einordnung_lgbtq_lokal_zahlen.csv` | number of items per source, type and category (`mistral-small3.1`) |
| `data/raw/einordnung_lgbtq_vergleich.csv` | both classifications side by side, per source, type and month; basis of the dashboard page |

Only the figures are published. The lists of items with headline, category and reason, as well as the samples, are not published, because the rights to the headlines remain with the respective media.

For access to the model, the script `beitraege_einordnen.py` uses the sign-in from my project rss-news-automation and cannot be run without that project. Both scripts also require the list of items that `neurodiv_websites.py` creates when collecting the data.
