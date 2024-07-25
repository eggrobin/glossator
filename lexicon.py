from collections import defaultdict
import sys
from os.path import commonprefix

from grammar import Gender, Number, Verb, KamilDecomposition, Stem, shorten_vowels

verbs = (
  Verb("ʾgr", "a", "u"),
  Verb("ʾḫz", "a", "u"),
  Verb("hlk", "a", "i"),  # TODO(egg): Needs special-casing.
  Verb("ʾmr", "a", "u"),
  Verb("ʾpl", "a", "u"),
  Verb("bnʾ", "i", "i"),
  Verb("bšʾ", "i", "i"),
  Verb("dwk", "a", "u"),
  Verb("dyn", "a", "i"),
  Verb("ʿnh", "i", "i"),
  Verb("ḥpš", "a", "u"),
  Verb("ḥbb", "i", "i"),
  Verb("ʿrb", "u", "u"),
  Verb("ḫlq", "i", "i"),
  Verb("kwn", "a", "u"),
  Verb("kšd", "a", "u"),
  Verb("kšš", "a", "u"),
  Verb("lmd", "a", "a"),
  Verb("lqḥ", "a", "a"),
  Verb("mdd", "a", "u"),
  Verb("mḫṣ", "a", "a"),
  Verb("mḫr", "a", "u"),
  Verb("mqt", "u", "u"),
  Verb("ndn", "i", "i"),
  Verb("ndʾ", "i", "i"),
  Verb("nʾl", "a", "i"),
  Verb("nks", "i", "i"),
  Verb("nṣr", "a", "u"),
  Verb("nšʾ", "i", "i"),
  Verb("prs", "a", "u"),
  Verb("pṭr", "a", "u"),
  Verb("qbʾ", "i", "i"),
  Verb("qlʾ", "u", "u"),
  Verb("qyp", "a", "i"),
  Verb("qyš", "a", "i"),
  Verb("rks", "a", "u"),
  Verb("rdḥ", "a", "a"),  # This ḥ is a hack.
  Verb("ṣbt", "a", "a"),
  Verb("škn", "a", "u"),
  Verb("šʾm", "a", "a"),
  Verb("šlʾ", "i", "i"),
  Verb("šlm", "i", "i"),
  Verb("šql", "a", "u"),
  Verb("šrq", "i", "i"),
  Verb("tbl", "a", "a"),
  Verb("twr", "a", "u"),
  Verb("wbl", "a", "i"),
  Verb("wṣʾ", "i", "i"),
  Verb("wšb", "a", "i"),
)

forms_to_glosses : defaultdict[str, dict[str, KamilDecomposition]] = defaultdict(dict)
shortened_forms_to_forms : dict[str, list[str]] = defaultdict(list)

unloaded_prefixes : defaultdict[str, list] = defaultdict(list)

def add_forms(verb : Verb):
  for stem in Stem:
    for n in Number:
      for p in (1, 2, 3):
        for g in Gender:
          gloss = verb.durative((p, g, n), stem=stem)
          forms_to_glosses[gloss.text()][str(gloss)] = gloss
          prefix = gloss.text()
          for acc in ((1, Gender.F, Number.SG), (2, Gender.F, Number.SG), (3, Gender.F, Number.SG)):
            prefix = commonprefix(
              (prefix,
               verb.durative((p, g, n), stem=stem, acc=acc).text()))
            unloaded_prefixes[shorten_vowels(prefix)].append((verb, stem, p, g, n, 'impfv'))

          gloss = verb.perfective((p, g, n), stem=stem)
          forms_to_glosses[gloss.text()][str(gloss)] = gloss
          prefix = gloss.text()
          for acc in ((1, Gender.F, Number.SG), (2, Gender.F, Number.SG), (3, Gender.F, Number.SG)):
            prefix = commonprefix(
              (prefix,
               verb.perfective((p, g, n), stem=stem, acc=acc).text()))
            unloaded_prefixes[shorten_vowels(prefix)].append((verb, stem, p, g, n, 'pftv'))

          gloss = verb.perfective((p, g, n), t='t', stem=stem)
          forms_to_glosses[gloss.text()][str(gloss)] = gloss
          prefix = gloss.text()
          for acc in ((1, Gender.F, Number.SG), (2, Gender.F, Number.SG), (3, Gender.F, Number.SG)):
            prefix = commonprefix(
              (prefix,
               verb.perfective((p, g, n), t='t', stem=stem, acc=acc).text()))
            unloaded_prefixes[shorten_vowels(prefix)].append((verb, stem, p, g, n, 't', 'pftv'))

          if stem != Stem.N:
            gloss = verb.durative((p, g, n), t='t', stem=stem)
            forms_to_glosses[gloss.text()][str(gloss)] = gloss
            prefix = gloss.text()
            for acc in ((1, Gender.F, Number.SG), (2, Gender.F, Number.SG), (3, Gender.F, Number.SG)):
              prefix = commonprefix(
                (prefix,
                verb.durative((p, g, n), t='t', stem=stem, acc=acc).text()))
              unloaded_prefixes[shorten_vowels(prefix)].append((verb, stem, p, g, n, 't', 'impfv'))

          gloss = verb.durative((p, g, n), t='tan', stem=stem)
          forms_to_glosses[gloss.text()][str(gloss)] = gloss
          prefix = gloss.text()
          for acc in ((1, Gender.F, Number.SG), (2, Gender.F, Number.SG), (3, Gender.F, Number.SG)):
            prefix = commonprefix(
              (prefix,
               verb.durative((p, g, n), t='tan', stem=stem, acc=acc).text()))
            unloaded_prefixes[shorten_vowels(prefix)].append((verb, stem, p, g, n, 'tan', 'impfv'))

for verb in verbs:
  add_forms(verb)

ALL_PERSONS = []
for n in Number:
  for p in (1, 2, 3):
    for g in Gender:
      ALL_PERSONS.append((p, g, n))

def load_suffixed_forms(verb, stem, p, g, n, *args):
  for obj in ('acc', 'dat'):
    for acc in ALL_PERSONS + [None]:
      for conj in (False, True):
        for vent in (False, True):
          for subj in (False,) if vent else (False, True):
            if 'pftv' in args:
              gloss = verb.perfective((p, g, n), t='t' if 't' in args else 'tan' if 'tan' in args else None, stem=stem,
                                      conj=conj, vent=vent, subj=subj, **{obj:acc})
            else:
              gloss = verb.durative((p, g, n), t='t' if 't' in args else 'tan' if 'tan' in args else None, stem=stem,
                                    conj=conj, vent=vent, subj=subj, **{obj:acc})
            form = gloss.text()
            if form not in forms_to_glosses:
              forms = shortened_forms_to_forms[shorten_vowels(form)]
              if form not in forms:
                forms.append(form)
                forms.sort()
            forms_to_glosses[form][str(gloss)] = gloss

def load_candidates(word):
  word = shorten_vowels(word)
  for i in reversed(range(len(word) + 1)):
    if word[:i] in unloaded_prefixes:
      for args in unloaded_prefixes[word[:i]]:
        #print("loading", args[0].root+'.'+'.'.join(str(x) for x in args[1:]))
        load_suffixed_forms(*args)
      del unloaded_prefixes[word[:i]]

if False:
  for prefix, verbs in unloaded_prefixes.items():
    print(prefix, ','.join(v[0].root+'.'+'.'.join(str(x) for x in v[1:]) for v in verbs))

for form in forms_to_glosses:
  forms = shortened_forms_to_forms[shorten_vowels(form)]
  if form not in forms:
    forms.append(form)
    forms.sort()