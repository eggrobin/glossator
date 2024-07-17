import sys

from grammar import Gender, Number, Stem, Verb

subj = 'subj' in sys.argv
conj = 'conj' in sys.argv
acc = None
for arg in sys.argv:
  if arg.startswith('acc'):
    (_, p, g, n) = arg.rsplit('.')
    acc = (int(p), Gender[g], Number[n])
for verb in (Verb(*sys.argv[1:4]),):
  for stem in Stem:
    for n in Number:
      for p in (1, 2, 3):
          glosses = {str(gloss): gloss for gloss in (verb.durative((p, g, n), t=False, subj=subj, conj=conj, stem=stem, acc=acc) for g in Gender)}
          print('\n/\n'.join(str(g) for g in glosses.values()))
    print('---')
    for n in Number:
      for p in (1, 2, 3):
          glosses = {str(gloss): gloss for gloss in (verb.perfective((p, g, n), t=False, subj=subj, conj=conj, stem=stem, acc=acc) for g in Gender)}
          print('\n/\n'.join(str(g) for g in glosses.values()))
    print('---')
    for n in Number:
      for p in (1, 2, 3):
          glosses = {str(gloss): gloss for gloss in (verb.perfective((p, g, n), t=True, subj=subj, conj=conj, stem=stem, acc=acc) for g in Gender)}
          print('\n/\n'.join(str(g) for g in glosses.values()))
    print('===')