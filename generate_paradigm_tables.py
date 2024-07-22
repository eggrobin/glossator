from grammar import Verb, Gender, Number, Stem

def complete_conjugation(verb: Verb, stem: Stem):
  table = []
  for number in (Number.SG, Number.PL):
    for person in (3, 2, 1):
      for gender in ((Gender.M, Gender.F)
                      if (person, number) in ((2, Number.SG),
                                              (3, Number.PL)) else
                      (Gender.F,)):
        row = []
        row.append(verb.durative((person, gender, number), stem=stem).text())
        row.append(verb.perfective((person, gender, number), stem=stem, t='t').text())
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
  print("7b", file=f)
  table=[]
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

  print("8b", file=f)
  for verb in (Verb("ʾmr", "a", "u"),
               Verb("ʾrk", "i", "i"),
               Verb("ʾkš", "u", "u"),
               Verb("ʾlk", "a", "i")):
    print_table(complete_conjugation(verb, Stem.G), f)
    print('---', file=f)

  print("9b", file=f)
  table=[]
  for verb in (Verb("ḥpš", "a", "u"),
               Verb("ʿzb", "i", "i"),
               Verb("ʿrb", "u", "u")):
    print_table(complete_conjugation(verb, Stem.G), f)
    print('---', file=f)

  print("10b", file=f)
  table=[]
  for verb in (Verb("nqr", "a", "u"),
               Verb("nks", "i", "i"),
               Verb("nsk", "u", "u")):
    print_table(complete_conjugation(verb, Stem.G), f)
    print('---', file=f)

  print("11b", file=f)
  table=[]
  for verb in (Verb("wrd", "a", "i"),
               Verb("wtr", "i", "i")):
    print_table(complete_conjugation(verb, Stem.G), f)
    print('---', file=f)

  print("12b", file=f)
  table=[]
  for verb in (Verb("kwn", "a", "u"),
               Verb("qyš", "a", "i"),
               Verb("šʾl", "a", "a"),
               Verb("nḥr", "a", "a")):
    print_table(complete_conjugation(verb, Stem.G), f)
    print('---', file=f)
  print_table(complete_conjugation(Verb("kwn", "a", "u"), Stem.D), f)

  print("13b", file=f)
  table=[]
  for verb in (Verb("bnʾ", "i", "i"),
               Verb("ḫdʾ", "u", "u"),
               Verb("mlʾ", "a", "a"),
               Verb("lqḥ", "a", "a")):
    print_table(complete_conjugation(verb, Stem.G), f)
    print('---', file=f)
