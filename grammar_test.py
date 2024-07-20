import sys

from grammar import Gender, Number, Stem, Verb

subj = 'subj' in sys.argv
conj = 'conj' in sys.argv
vent = 'vent' in sys.argv
stem = next((Stem[arg] for arg in sys.argv if arg in dir(Stem)), Stem.G)
show_gloss = 'gloss' in sys.argv
acc = None
for arg in sys.argv:
  if arg.startswith('acc'):
    (_, p, g, n) = arg.rsplit('.')
    acc = (int(p), Gender[g], Number[n])
for verb in (Verb(*sys.argv[1:4]),):
  for n in Number:
    for p in (1, 2, 3):
        glosses = {str(gloss): gloss for gloss in (verb.durative((p, g, n), t='t' if 't' in sys.argv else 'tan' if 'tan' in sys.argv else None, subj=subj, conj=conj, vent=vent, stem=stem, acc=acc) for g in Gender)}
        print('\n/\n'.join(str(g) for g in glosses.values()) if show_gloss else '/'.join(g.text() for g in glosses.values()))
  print('---')
  for n in Number:
    for p in (1, 2, 3):
        glosses = {str(gloss): gloss for gloss in (verb.perfective((p, g, n), t='t' if 't' in sys.argv else 'tan' if 'tan' in sys.argv else None, subj=subj, conj=conj, vent=vent, stem=stem, acc=acc) for g in Gender)}
        print('\n/\n'.join(str(g) for g in glosses.values()) if show_gloss else '/'.join(g.text() for g in glosses.values()))
  print('---')
  if not 't' in sys.argv and not 'tan' in sys.argv:
    for n in Number:
      for p in (1, 2, 3):
          glosses = {str(gloss): gloss for gloss in (verb.perfective((p, g, n), t='t', subj=subj, conj=conj, vent=vent, stem=stem, acc=acc) for g in Gender)}
          print('\n/\n'.join(str(g) for g in glosses.values()) if show_gloss else '/'.join(g.text() for g in glosses.values()))
