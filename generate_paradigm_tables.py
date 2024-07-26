from grammar import Verb, Person, Gender, Number, Stem, Label

def append_3cs_conjugation(table, verb: Verb, stem: Stem, **kwargs):
  row = []
  row.append(verb.durative((Person(3), Gender.F, Number.SG), stem=stem, **kwargs).text())
  if 't' not in kwargs:
    row.append(verb.perfective((Person(3), Gender.F, Number.SG), stem=stem, t=Label.t, **kwargs).text())
  else:
    row.append('NYI')
  row.append(verb.perfective((Person(3), Gender.F, Number.SG), stem=stem, **kwargs).text())
  table.append(row)

def complete_conjugation(verb: Verb, stem: Stem):
  table = []
  for number in (Number.SG, Number.PL):
    for person in (Person(3), Person(2), Person(1)):
      for gender in ((Gender.M, Gender.F)
                      if (person, number) in ((Person(2), Number.SG),
                                              (Person(3), Number.PL)) else
                      (Gender.F,)):
        row = []
        row.append(verb.durative((person, gender, number), stem=stem).text())
        row.append(verb.perfective((person, gender, number), stem=stem, t=Label.t).text())
        row.append(verb.perfective((person, gender, number), stem=stem).text())
        table.append(row)
    if number == Number.SG:
      table.append([''] * 3)
  return table

def print_table(table, f):
  widths = []
  for j in range(len(table[0])):
    widths.append(max(len(row[j]) for row in table))
  for row in table:
    print(*(row[i].ljust(widths[i]) for i in range(len(row))), file=f)

with open('paradigms.txt', 'w', encoding='utf-8') as f:
  print("7a", file=f)
  table=[]
  for args in ({}, {'t':Label.t}, {'t':Label.tan}):
    for verb in (Verb("prs", "a", "u"),
                 Verb("ṣbt", "a", "a"),
                 Verb("šrq", "i", "i"),
                 Verb("mqt", "u", "u")):
      append_3cs_conjugation(table, verb, stem=Stem.G, **args)
    print_table(table, f)
    table=[]
    print('---', file=f)
  for args in ({}, {'t':Label.tan}):
    for verb in (Verb("prs", "a", "u"),
                 Verb("šrq", "i", "i")):
      append_3cs_conjugation(table, verb, stem=Stem.N, **args)
    print_table(table, f)
    table=[]
    print('---', file=f)
  for args in ({}, {'t':Label.t}, {'t':Label.tan}):
    append_3cs_conjugation(table, Verb("prs", "a", "u"), stem=Stem.D, **args)
  print_table(table, f)
  table=[]
  print('---', file=f)
  for args in ({}, {'t':Label.t}, {'t':Label.tan}):
    append_3cs_conjugation(table, Verb("prs", "a", "u"), stem=Stem.Š, **args)
  print_table(table, f)
  table=[]
  print('---', file=f)

  print("7b", file=f)
  for verb in (Verb("prs", "a", "u"),
               Verb("ṣbt", "a", "a"),
               Verb("šrq", "i", "i"),
               Verb("mqt", "u", "u")):
    print_table(complete_conjugation(verb, Stem.G), f)
    print('---', file=f)
  verb = Verb("prs", "a", "u")
  print_table(complete_conjugation(verb, Stem.N), f)
  print('---', file=f)
  print_table(complete_conjugation(verb, Stem.D), f)
  print('---', file=f)
  print_table(complete_conjugation(verb, Stem.Š), f)
  print('---', file=f)

  print("8a", file=f)
  table=[]
  for verb in (Verb("ʾḫz", "a", "u"),
                Verb("ʾrk", "i", "i"),
                Verb("ʾkš", "u", "u"),
                Verb("hlk", "a", "i")):
    append_3cs_conjugation(table, verb, stem=Stem.G)
  print_table(table, f)
  table=[]
  print('---', file=f)
  for verb in (Verb("ʾḫz", "a", "u"),
                Verb("hlk", "a", "i")):
    append_3cs_conjugation(table, verb, stem=Stem.G, t=Label.t)
  print_table(table, f)
  table=[]
  print('---', file=f)
  for verb in (Verb("ʾḫz", "a", "u"),
                Verb("ʾrk", "i", "i"),
                Verb("ʾkš", "u", "u"),
                Verb("hlk", "a", "i")):
    append_3cs_conjugation(table, verb, stem=Stem.G, t=Label.tan)
  print_table(table, f)
  table=[]
  print('---', file=f)
  for args in ({}, {'t':Label.tan}):
    append_3cs_conjugation(table, Verb("ʾḫz", "a", "u"), stem=Stem.N, **args)
    print_table(table, f)
    table=[]
    print('---', file=f)
  for args in ({}, {'t':Label.t}, {'t':Label.tan}):
    append_3cs_conjugation(table, Verb("ʾḫz", "a", "u"), stem=Stem.D, **args)
  print_table(table, f)
  table=[]
  print('---', file=f)
  for args in ({}, {'t':Label.t}, {'t':Label.tan}):
    append_3cs_conjugation(table, Verb("ʾḫz", "a", "u"), stem=Stem.Š, **args)
  print_table(table, f)
  table=[]
  print('---', file=f)

  print("8b", file=f)
  for verb in (Verb("ʾmr", "a", "u"),
               Verb("ʾrk", "i", "i"),
               Verb("ʾkš", "u", "u"),
               Verb("ʾlk", "a", "i")):
    print_table(complete_conjugation(verb, Stem.G), f)
    print('---', file=f)

  print("9b", file=f)
  for verb in (Verb("ḥpš", "a", "u"),
               Verb("ʿzb", "i", "i"),
               Verb("ʿrb", "u", "u")):
    print_table(complete_conjugation(verb, Stem.G), f)
    print('---', file=f)

  print("10b", file=f)
  for verb in (Verb("nqr", "a", "u"),
               Verb("nks", "i", "i"),
               Verb("nsk", "u", "u")):
    print_table(complete_conjugation(verb, Stem.G), f)
    print('---', file=f)

  print("11b", file=f)
  for verb in (Verb("wrd", "a", "i"),
               Verb("wtr", "i", "i")):
    print_table(complete_conjugation(verb, Stem.G), f)
    print('---', file=f)

  print("12b", file=f)
  for verb in (Verb("kwn", "a", "u"),
               Verb("qyš", "a", "i"),
               Verb("šʾl", "a", "a"),
               Verb("nḥr", "a", "a")):
    print_table(complete_conjugation(verb, Stem.G), f)
    print('---', file=f)
  print_table(complete_conjugation(Verb("kwn", "a", "u"), Stem.D), f)

  print("13b", file=f)
  for verb in (Verb("bnʾ", "i", "i"),
               Verb("ḫdʾ", "u", "u"),
               Verb("mlʾ", "a", "a"),
               Verb("lqḥ", "a", "a")):
    print_table(complete_conjugation(verb, Stem.G), f)
    print('---', file=f)

  print("13d", file=f)
  for verb in (Verb("bnʾ", "i", "i"),
               Verb("mnʾ", "u", "u"),
               Verb("klʾ", "a", "a"),
               Verb("lqḥ", "a", "a")):
    print_table(complete_conjugation(verb, Stem.N), f)
    print('---', file=f)

  print("13f", file=f)
  for stem in (Stem.D, Stem.Š):
    print_table(complete_conjugation(Verb("bnʾ", "i", "i"), stem), f)
    print('---', file=f)