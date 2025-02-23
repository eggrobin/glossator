from collections import defaultdict
import re
import unicodedata
import sys

import grammar
import lexicon

with open(sys.argv[1], "r", encoding="utf-8") as f:
  atf_lines = f.read().splitlines()

word_counts : dict[str, int] = defaultdict(int)
verbs_by_law: defaultdict[int, list[tuple[str, str, list[grammar.KamilDecomposition]]]] = defaultdict(list)

law = None
line_number = None

NONVERBS = frozenset(
  ("īnšu",
   "inūma",)
)

def normalize_n_assimilation(s):
  return re.sub(r'n([C])'.replace('C', ''.join(grammar.CONSONANTS)), r'\1\1', s)

possible_glosses = []

for atf_line in atf_lines:
  if atf_line == "@epilogue":
    break
  match = re.match(r"@law (\d+)", atf_line)
  if match:
    if law:
      print("=== End of law %d; identified %d verbs" % (law, len(verbs_by_law[law])))
    law = int(match.group(1))
    continue
  if not law:
    continue
  print(atf_line)
  if not atf_line.startswith("#tr.ts:"):
    if atf_line.startswith("#tr.en:"):
      for gloss in possible_glosses:
        characteristics = [
          f for f in gloss.functions
          if not any(f in g.functions for g in possible_glosses if g is not gloss)]
        print('\n'.join('   ' + l for l in str(gloss).split('\n')))
        if len(possible_glosses) > 1:
          print('^-- %s' % ' '.join(str(c) for c in characteristics))
      if possible_glosses:
        sys.stdin.readline()
    elif not atf_line.startswith(("#", "$")):
      line_number = atf_line.split('.', 1)[0]
    continue
  if not line_number:
    raise ValueError("No line number for %s" % atf_line)
  # Use U+02BE ʾ MODIFIER LETTER RIGHT HALF RING rather than U+2019 ’ RIGHT
  # SINGLE QUOTATION MARK for the aleph so that the words comprise only letters.
  atf_line = atf_line.replace("’", "ʾ", )
  # Drop the editorial marks, taking the corrected version.
  atf_line = atf_line.replace("<", "").replace(">", "")
  words = re.split(r"(?:tr.ts|\W)+", atf_line)
  for word in words:
    if word:
      normalized_word = normalize_n_assimilation(word)
      word_counts[word] += 1
      if word not in NONVERBS:
        lexicon.load_candidates(normalized_word)
        possible_glosses: list[grammar.KamilDecomposition] = []
        if False and normalized_word in lexicon.forms_to_glosses:
          possible_glosses = list(lexicon.forms_to_glosses[normalized_word].values())
        elif grammar.shorten_vowels(normalized_word) in lexicon.shortened_forms_to_forms:
          for form in lexicon.ungeminated_forms_to_forms[grammar.ungeminate_consonants(grammar.shorten_vowels(normalized_word))]:
            possible_glosses += list(lexicon.forms_to_glosses[form].values())
        if possible_glosses:
          verbs_by_law[law].append((line_number, word, possible_glosses))

glossed_verbs = 0
ambiguous_verbs = 0

def akkadian_collation_key(s: str):
  return unicodedata.normalize(
    "NFD",
    s.replace("š", "sz")  # ASCII hacks to sort these letters primary-after
     .replace("ṣ", "s,")  # the ASCII ones without using proper collation
     .replace("ṭ", "t,")  # weights.
     .replace("y", "j")   # y collates equal to j.
    ).replace("\u0304", "").replace("\u0302", "") # Drop macron and circumflex.

glossed_forms = 0

for word, count in sorted(word_counts.items(), key=lambda kv: (-kv[1], akkadian_collation_key(kv[0]))):
  normalized_word = normalize_n_assimilation(word)
  if normalized_word in lexicon.forms_to_glosses or grammar.shorten_vowels(normalized_word) in lexicon.shortened_forms_to_forms:
    glossed_forms += 1

with open('glosses.txt', 'w', encoding='utf-8') as f:
  for law, verbs in verbs_by_law.items():
    print("Law", law, file=f)
    for line_number, word, glosses in verbs:
      print("l.", line_number,
            ('~' if any(gloss.text() != word for gloss in glosses) else '') + word,
            file=f)
      glossed_verbs += 1
      for gloss in glosses:
        print(gloss, file=f)
      if len(glosses) > 1:
        ambiguous_verbs += 1
  for file in (f, sys.stdout):
    print(file=file)
    print("Glossed %d verbs with %d ambiguities" % (glossed_verbs, ambiguous_verbs),
          file=file)
    print("Glossed %d unique forms" % (glossed_forms),
          file=file)