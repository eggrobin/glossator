from collections import defaultdict
import re
import unicodedata
import sys

import grammar
import lexicon

with open(sys.argv[1], "r", encoding="utf-8") as f:
  atf_lines = f.read().splitlines()

word_counts = defaultdict(int)
verbs_by_law: defaultdict[int, list[tuple[int, list[grammar.KamilDecomposition]]]] = defaultdict(list)

law = None
line_number = None

for atf_line in atf_lines:
  if atf_line == "@epilogue":
    break
  match = re.match(r"@law (\d+)", atf_line)
  if match:
    law = int(match.group(1))
    continue
  if not law:
    continue
  if not atf_line.startswith("#tr.ts:"):
    if not atf_line.startswith(("#", "$")):
      line_number = atf_line.split('.', 1)[0]
    continue
  # Use U+02BE ʾ MODIFIER LETTER RIGHT HALF RING rather than U+2019 ’ RIGHT
  # SINGLE QUOTATION MARK for the aleph so that the words comprise only letters.
  atf_line = atf_line.replace("’", "ʾ", )
  # Drop the editorial marks, taking the corrected version.
  atf_line = atf_line.replace("<", "").replace(">", "")
  words = re.split(r"(?:tr.ts|\W)+", atf_line)
  for word in words:
    if word:
      word = re.sub(r'nma$', r'mma', word)
      word_counts[word] += 1
      if word in lexicon.forms_to_glosses:
        verbs_by_law[law].append((line_number, list(lexicon.forms_to_glosses[word].values())))
      elif grammar.shorten_vowels(word) in lexicon.shortened_forms_to_forms:
        loose_match = re.compile(
          grammar.nfc(re.sub(r'([aeui])', r'[\1\1' + grammar.MACRON + r']', word)))
        for form in lexicon.shortened_forms_to_forms[grammar.shorten_vowels(word)]:
          if loose_match.match(form):
            verbs_by_law[law].append((line_number, list(lexicon.forms_to_glosses[form].values())))

glossed_verbs = 0
ambiguous_verbs = 0

for law, verbs in verbs_by_law.items():
  print("Law %d, identified %d verbs" % (law, len(verbs)))
  for line_number, glosses in verbs:
    glossed_verbs += 1
    print("Line %s:" % line_number)
    if len(glosses) == 1:
        print(glosses[0])
    else:
      ambiguous_verbs += 1
      for gloss in glosses:
        characteristics = [
          f for f in gloss.functions
          if not any(f in g.functions for g in glosses if g is not gloss)]
        print(gloss)
        print('^-- %s' % ' '.join(str(c) for c in characteristics))
    print('===')
  print()

def akkadian_collation_key(s):
  return unicodedata.normalize(
    "NFD",
    s.replace("š", "sz")  # ASCII hacks to sort these letters primary-after
     .replace("ṣ", "s,")  # the ASCII ones without using proper collation
     .replace("ṭ", "t,")  # weights.
     .replace("y", "j")   # y collates equal to j.
    ).replace("\u0304", "").replace("\u0302", "") # Drop macron and circumflex.

glossed_forms = 0
ambiguous_forms = 0

for word, count in sorted(word_counts.items(), key=lambda kv: (-kv[1], akkadian_collation_key(kv[0]))):
  print(count, "\t", word)
  if word in lexicon.forms_to_glosses:
    glossed_forms += 1
    if len(lexicon.forms_to_glosses[word]) > 1:
      ambiguous_forms += 1
    print('\n---\n'.join(lexicon.forms_to_glosses[word]))

print("Glossed %d verbs with %d ambiguities" % (glossed_verbs, ambiguous_verbs))
print("Glossed %d unique forms with %d ambiguities" % (glossed_forms, ambiguous_forms))