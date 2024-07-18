from collections import defaultdict
import sys

from grammar import Gender, Number, Verb, KamilDecomposition, Stem, shorten_vowels

verbs = (
  Verb("ʾgr", "a", "u"),
  Verb("ʾḫz", "a", "u"),
  Verb("ʾlk", "a", "i"),  # TODO(egg): Needs special-casing.
  Verb("ʾmr", "a", "u"),
  Verb("bnʾ", "i", "i"),
  Verb("bšʾ", "i", "i"),
  Verb("dwk", "a", "u"),
  Verb("ḥpš", "a", "u"),
  Verb("ḥbb", "i", "i"),
  Verb("kwn", "a", "u"),
  Verb("kšd", "a", "u"),
  Verb("kšš", "a", "u"),
  Verb("lqḥ", "a", "a"),
  Verb("mdd", "a", "u"),
  Verb("mḫṣ", "a", "a"),
  Verb("mḫr", "a", "u"),
  Verb("ndn", "i", "i"),
  Verb("ndʾ", "i", "i"),
  Verb("prs", "a", "u"),
  Verb("qbʾ", "i", "i"),
  Verb("qyš", "a", "i"),
  Verb("ṣbt", "a", "a"),
  Verb("šʾm", "a", "a"),
  Verb("šlʾ", "i", "i"),
  Verb("šlm", "i", "i"),
  Verb("šql", "a", "u"),
  Verb("wbl", "a", "u"),
)

forms_to_glosses : defaultdict[str, dict[str, KamilDecomposition]] = defaultdict(dict)
shortened_forms_to_forms : dict[str, set[str]] = defaultdict(set)

loaded_accs = set()

def add_forms(acc):
  if acc in loaded_accs:
    return
  loaded_accs.add(acc)
  if acc:
    print("loading acc.%s" % '.'.join(str(f) for f in acc), file=sys.stderr)
  for stem in Stem:
    for conj in (False, True):
      for vent in (False, True):
        for subj in (False,) if vent else (False, True):
          for verb in verbs:
            for n in Number:
              for p in (1, 2, 3):
                for g in Gender:
                  gloss = verb.durative((p, g, n), t=False, subj=subj, conj=conj, vent=vent, stem=stem, acc=acc)
                  forms_to_glosses[gloss.text()][str(gloss)] = gloss
            for n in Number:
              for p in (1, 2, 3):
                for g in Gender:
                  gloss = verb.perfective((p, g, n), t=False, subj=subj, conj=conj, vent=vent, stem=stem, acc=acc)
                  forms_to_glosses[gloss.text()][str(gloss)] = gloss
            for n in Number:
              for p in (1, 2, 3):
                for g in Gender:
                  gloss = verb.perfective((p, g, n), t=True, subj=subj, conj=conj, vent=vent, stem=stem, acc=acc)
                  forms_to_glosses[gloss.text()][str(gloss)] = gloss

add_forms(acc=None)
for n in Number:
  for p in (1, 2, 3):
    for g in Gender:
      add_forms(acc=(p, g, n))

for form in forms_to_glosses:
  shortened_forms_to_forms[shorten_vowels(form)].add(form)