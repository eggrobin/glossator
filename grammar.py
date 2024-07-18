from enum import Enum
from typing import Literal
import unicodedata

CIRCUMFLEX = unicodedata.lookup('COMBINING CIRCUMFLEX ACCENT')
MACRON = unicodedata.lookup('COMBINING MACRON')

CONSONANTS = tuple('bdgḫyklmnpqrsṣštṭwz')
WEAK_CONSONANTS = tuple('ʾwyḥ')
VOWELS = tuple('aeuiāēūīâêûî')
SHORT_VOWELS = ('a', 'e', 'u', 'i')
def nfd(s: str) -> str:
  return unicodedata.normalize('NFD', s)
def nfc(s: str) -> str:
  return unicodedata.normalize('NFC', s)
def shorten_vowels(s: str) -> str:
  return nfc(nfd(s).replace(CIRCUMFLEX, '').replace(MACRON, ''))

class Morpheme:
  text: str
  functions: list

  def gloss_text(self):
    return self.text if self.text else '∅'

  def __init__(self, text, function):
    self.text = text
    self.functions = ['.'.join(str(g) for g in f) if isinstance(f, list) else f for f in function]

class Gender(Enum):
  M = 0
  F = 1
  def __str__(self) -> str:
    return super().__str__().rsplit('.', 1)[-1]

class Stem(Enum):
  G = 0
  D = 1
  #Š = 2
  N = 3
  def __str__(self) -> str:
    return super().__str__().rsplit('.', 1)[-1]

class Number(Enum):
  SG = 1
  PL = 3
  def __str__(self) -> str:
    return super().__str__().rsplit('.', 1)[-1]

Person = tuple[Literal[1, 2, 3], Gender, Number]

def personal_prefix(p: Literal[1, 2, 3], g: Gender, n: Number):
  return (Morpheme('a' if n == Number.SG else 'ni', [p, n]) if p == 1 else
          Morpheme('ta', [p]) if p == 2 else
          Morpheme('i', [p]))

def personal_prefix_d(p: Literal[1, 2, 3], g: Gender, n: Number):
  return (Morpheme('u' if n == Number.SG else 'nu', [p, n]) if p == 1 else
          Morpheme('tu', [p]) if p == 2 else
          Morpheme('u', [p]))

def personal_suffix(p: Literal[1, 2, 3], g: Gender, n: Number):
  return (Morpheme('ī', [p, g, n]) if p == 2 and g == Gender.F and n == Number.SG else
          Morpheme('ā', [p, n])    if p == 2 and                   n == Number.PL else
          Morpheme('ā', [p, g, n]) if p == 3 and g == Gender.F and n == Number.PL else
          Morpheme('ū', [p, g, n]) if p == 3 and g == Gender.M and n == Number.PL else
          Morpheme('', [p] if p == 1 else
                       [p, g, n] if p == 2 and n == Number.SG else
                       [p, n]))

def ventive(p: Literal[1, 2, 3], g: Gender, n: Number):
  return Morpheme('nim' if n == Number.PL and p != 1 else
                  'm' if p == 2 and g == Gender.F else
                  'am',
                  ['VENT'])

def acc_pronominal_suffix(p: Literal[1, 2, 3], g: Gender, n: Number):
  f = ['ACC', p]
  return ((Morpheme('ni', [f + [n]]) if p == 1 else
           (Morpheme('ki', [f + [g, n]]) if g == Gender.F else
            Morpheme('ka', [f + [g, n]])) if p == 2 else
           (Morpheme('ši', [f + [g, n]]) if g == Gender.F else
            Morpheme('šu', [f + [g, n]]))) if n == Number.SG else
          (Morpheme('niāti', [f + [n]]) if p == 1 else
           (Morpheme('kināti', [f + [g, n]]) if g == Gender.F else
            Morpheme('kunūti', [f + [g, n]])) if p == 2 else
            (Morpheme('šināti', [f + [g, n]]) if g == Gender.F else
             Morpheme('šunūti', [f + [g, n]]))))

ACC_PRONOMINAL_SUFFIXES: dict[str, Person] = {}

for p in (1, 2, 3):
  for g in Gender:
    for n in Number:
      ACC_PRONOMINAL_SUFFIXES[acc_pronominal_suffix(p, g, n).text] = (p, g, n)

def contract_vowels(v1: str, v2: str) -> str:
  if nfd(v1)[0] in ('e', 'i') and nfd(v2)[0] == 'a':
    return v1 + v2
  elif v1 in ('ā', 'ē') and nfd(v2)[0] == 'i':
    return 'ê'
  else:
    return nfc(nfd(v2)[0] + unicodedata.lookup('COMBINING CIRCUMFLEX ACCENT'))


class KamilDecomposition:
  root: str
  reconstructed: list[Morpheme]
  morphemes: list[Morpheme]
  functions: set

  def __init__(self, root, morphemes) -> None:
    self.root = root
    self.reconstructed = list(Morpheme(m.text, m.functions) for m in morphemes if m)
    self.morphemes = list(Morpheme(m.text, m.functions) for m in morphemes if m)
    self.lose_consonants()
    self.harmonize()
    self.contract_vowels()
    self.lengthen_before_suffixes()
    self.assimilate_n()
    self.assimilate_t()
    self.assimilate_object_š()
    self.assimilate_ventive_m()
    self.merge_root_morphemes()
    self.functions = set(f for m in self.morphemes for f in m.functions)

  def __str__(self):
    reconstruction = ''.join(m.text for m in self.reconstructed)
    actual_text = self.text()
    return ('-'.join(m.gloss_text() for m in self.morphemes) +
            '  (' +
            actual_text +
            ('' if reconstruction == actual_text else ' < *' + reconstruction) +
            ')\n' +
            '-'.join('.'.join(str(f) for f in m.functions)
                     for m in self.morphemes))

  def text(self):
    return ''.join(m.text for m in self.morphemes)
  
  def next_overt_morpheme(self, i: int) -> tuple[int, str]:
    next_text = ''
    k = i + 1
    while k < len(self.morphemes):
      next_text = self.morphemes[k].text
      if next_text:
        break
      k += 1
    return (k, next_text)
  
  def previous_overt_morpheme(self, i: int) -> tuple[int, str]:
    previous_text = ''
    j = i - 1
    while j >= 0:
      previous_text = self.morphemes[j].text
      if previous_text:
        break
      j -= 1
    return (j, previous_text)

  def lose_consonants(self):
    i = 0
    while i < len(self.morphemes):
      j, previous_text = self.previous_overt_morpheme(i)
      k, next_text = self.next_overt_morpheme(i)
      l, next_2 = self.next_overt_morpheme(k)
      m, next_3 = self.next_overt_morpheme(l)
      if (self.morphemes[i].text and
          self.morphemes[i].text[0] in WEAK_CONSONANTS and
          self.morphemes[i].text == 2 * self.morphemes[i].text[0]):
        # We are looking at the ʾʾ in V₁ʾʾV₂C.
        if not previous_text.endswith(SHORT_VOWELS):
          raise ValueError("%s should end with a short vowel in %s" % (previous_text, self))
        if next_text not in SHORT_VOWELS:
          raise ValueError("%s should be a short vowel in %s" % (next_text, self))
        if next_2 not in CONSONANTS:
          raise ValueError("%s should be a consonant %s" % (next_2, self))
        if next_3.startswith(VOWELS):
          # V₁ʾʾV₂CV₃ becomes V₂CCV₃.
          self.morphemes[j].text = self.morphemes[j].text[:-1]
          self.morphemes[i].text = ''
          self.morphemes[l].text *= 2
        elif 'D' in self.morphemes[i].functions:
          # V₁ʾʾV₂C becomes V̄₂C if the gemination comes from the D-stem.
          self.morphemes[j].text = self.morphemes[j].text[:-1]
          self.morphemes[i].text = ''
          self.morphemes[k].text = nfc(self.morphemes[k].text + MACRON)
        elif self.morphemes[i].text[0] == 'w' and  self.morphemes[j].text.endswith('a'):
          # aww > ū.
          self.morphemes[j].text = self.morphemes[j].text[:-1]
          self.morphemes[i].text = 'ū'
        elif self.morphemes[i].text[0] == 'y' and  self.morphemes[j].text.endswith('a'):
          # ayy > ī.
          self.morphemes[j].text = self.morphemes[j].text[:-1]
          self.morphemes[i].text = 'ī'
        else:
          # Just drop the geminated aleph, e.g., in *išaʾʾam, and let vowel
          # contraction do its thing to get išâm.
          self.morphemes[i].text = ''

      elif self.morphemes[i].text in ('y', 'w'):
        if (previous_text.endswith(CONSONANTS) and
            ((self.morphemes[i].text == 'w' and next_text == 'u') or
             (self.morphemes[i].text == 'y' and next_text == 'i'))):
          # Cwu > Cū, Cyi > Cī.
          self.morphemes[i].text = ''
          self.morphemes[k].text = nfc(self.morphemes[k].text + MACRON)
        elif previous_text.endswith('a') and next_text.startswith('a'):
          # awa > ū, aya > ī.
          self.morphemes[j].text = self.morphemes[j].text[:-1]
          self.morphemes[i].text = 'ū' if self.morphemes[i].text == 'w' else 'ī'
          self.morphemes[k].text = self.morphemes[k].text[1:]

      elif self.morphemes[i].text in ('ʾ', 'ḥ'):
        if not next_text or not previous_text:
          self.morphemes[i].text = ''
        elif (shorten_vowels(previous_text).endswith(SHORT_VOWELS) and
              shorten_vowels(next_text).startswith(CONSONANTS)):
          # VʾC > V̄C.
          if previous_text.endswith(SHORT_VOWELS):
            self.morphemes[j].text = nfc(previous_text[:-1] + previous_text[-1] + MACRON)
          self.morphemes[i].text = ''
        elif (previous_text.endswith(VOWELS) and
              next_text == 'a' and
              next_2.startswith(CONSONANTS) and next_2 == 2 * next_2[0]):
          # VʾaCC > VCC for I-weak PCL.
          while l > i:
            l -= 1
            self.morphemes[l].text = ''
          continue
        else:
          self.morphemes[i].text = ''
      i += 1

  def harmonize(self):
    if 'ḥ' in self.root:
      for m in self.morphemes:
        if ((m.text == 'ā' and m.functions in ([3, Gender.F, Number.PL],
                                               [2, Number.PL])) or
            m.functions == ['CONJ'] or
            any('ACC' in f for f in m.functions if isinstance(f, str)) or
            m.functions == ['VENT']):
          continue
        m.text = nfc(nfd(m.text).replace('a', 'e'))

  def assimilate_n(self):
    i = 0
    while i < len(self.morphemes):
      k, next_text = self.next_overt_morpheme(i)
      if (self.morphemes[i].text.endswith('n') and
          next_text.startswith(CONSONANTS)):
        self.morphemes[i].text = self.morphemes[i].text[:-1] + next_text[0]
      i += 1

  def assimilate_t(self):
    i = 0
    while i < len(self.morphemes):
      _, previous_text = self.previous_overt_morpheme(i)
      # H p. 155.
      if ('t' in self.morphemes[i].functions and
          self.morphemes[i].text.startswith('t') and
          previous_text.endswith(('d', 'ṭ', 's', 'ṣ'))):
        self.morphemes[i].text = previous_text[-1] + self.morphemes[i].text[1:]
      i += 1

  def assimilate_object_š(self):
    i = 0
    while i < len(self.morphemes):
      j, previous_text = self.previous_overt_morpheme(i)
      # H p. 170.
      if (any('ACC' in f for f in self.morphemes[i].functions if isinstance(f, str)) and
          self.morphemes[i].text.startswith('š') and
          previous_text.endswith(('d', 't', 'ṭ', 's', 'ṣ', 'z', 'š'))):
        self.morphemes[j].text = self.morphemes[j].text[:-1] + 's'
        self.morphemes[i].text = 's' + self.morphemes[i].text[1:]
      i += 1

  def assimilate_ventive_m(self):
    i = 0
    while i < len(self.morphemes):
      _, next_text = self.next_overt_morpheme(i)
      # H p. 170.
      if ('VENT' in self.morphemes[i].functions and
          self.morphemes[i].text.endswith('m') and
          next_text.startswith(CONSONANTS)):
        self.morphemes[i].text = self.morphemes[i].text[:-1] + next_text[0]
      i += 1

  def contract_vowels(self):
    i = 0
    while i < len(self.morphemes):
      k, next_text = self.next_overt_morpheme(i)
      if self.morphemes[i].text.endswith(VOWELS) and next_text.startswith(VOWELS):
        v1 = self.morphemes[i].text[-1]
        v2 = next_text[0]
        contraction = contract_vowels(v1, v2)
        if contraction != v1 + v2:
          self.morphemes[i].text = self.morphemes[i].text[:-1] + contraction + next_text[1:]
          for l in range(i + 1, k + 1):
            for f in self.morphemes[l].functions:
              if f not in self.morphemes[i].functions:
                self.morphemes[i].functions.append(f)
          while k > i:
            self.morphemes.pop(k)
            k -= 1
      i += 1

  def lengthen_before_suffixes(self):
    for i, m in enumerate(self.morphemes):
      if 'CONJ' in m.functions or any('ACC' in f for f in m.functions if isinstance(f, str)):
        k, previous = self.previous_overt_morpheme(i)
        if previous.endswith(SHORT_VOWELS):
          self.morphemes[k].text = nfc(self.morphemes[k].text + MACRON)

  def merge_root_morphemes(self):
    # TODO(egg): Keep the t-morpheme separate as an infix.
    root_morpheme = ''
    root_functions = ['√' + self.root]
    root_start = None
    root_end = None
    for i, m in enumerate(self.morphemes):
      if 'R₁' in m.functions:
        root_start = i
      if root_start is not None and root_end is None:
        root_morpheme += m.text
        root_functions += (f for f in m.functions if f not in root_functions)
      if 'R₃' in m.functions:
        root_end = i
    root_functions.remove('R₁')
    root_functions.remove('R₂')
    root_functions.remove('R₃')
    self.morphemes = self.morphemes[:root_start] + [Morpheme(root_morpheme, root_functions)] + self.morphemes[root_end + 1:]
class Verb:
  root: str
  durative_vowel: str
  perfective_vowel: str

  def __init__(self, root: str, durative_vowel: str, perfective_vowel: str) -> None:
    self.root = root
    self.durative_vowel = durative_vowel
    self.perfective_vowel = perfective_vowel
  def durative(self,
               p: Person,
               t: bool=False,
               subj: bool = False,
               conj: bool = False,
               vent: bool = False,
               stem: Stem = Stem.G,
               acc: tuple[Literal[1, 2, 3], Gender, Number]|None = None) -> KamilDecomposition:
    if acc and acc[0] == 1 and acc[-1] == Number.SG:
      vent = True
    if vent:
      subj = False
    return KamilDecomposition(
      self.root,
      (personal_prefix_d(*p) if stem == Stem.D else personal_prefix(*p),
        Morpheme('n', ['PASS']) if stem == Stem.N else None,
        Morpheme('ta', ['t']) if t and stem == Stem.N else None,
        Morpheme(self.root[0], ['R₁']),
        (Morpheme('ta', ['t']) if t and stem != Stem.N else
        Morpheme('a', ['IMPFV'])),
        Morpheme(2 * self.root[1], ['R₂', 'D' if stem == Stem.D else 'IMPFV']),
        Morpheme('a' if stem == Stem.D or
                        (stem == Stem.N and self.durative_vowel != 'i') else
                self.durative_vowel,
                ['IMPFV']),
        Morpheme(self.root[-1], ['R₃']),
        personal_suffix(*p),
        Morpheme('u', ['SUBJ']) if subj and not personal_suffix(*p).text else None,
        ventive(*p) if vent else None,
        acc_pronominal_suffix(*acc) if acc else None,
        Morpheme('ma', ['CONJ']) if conj else None))
  def perfective(self,
                 p: Person,
                 t: bool=False,
                 subj: bool = False,
                 conj: bool = False,
                 vent: bool = False,
                 stem: Stem = Stem.G,
                 acc: tuple[Literal[1, 2, 3], Gender, Number]|None = None) -> KamilDecomposition:
    if acc and acc[0] == 1 and acc[-1] == Number.SG:
      vent = True
    if vent:
      subj = False
    return KamilDecomposition(
      self.root,
      (personal_prefix_d(*p) if stem == Stem.D else personal_prefix(*p),
        Morpheme('n', ['PASS']) if stem == Stem.N else None,
        Morpheme('ta', ['t']) if t and stem == Stem.N else None,
        Morpheme(self.root[0], ['R₁']),
        (Morpheme('ta', ['t']) if t and stem != Stem.N else
        Morpheme('a', ['PFTV']) if stem in (Stem.D, Stem.N) else None),
        Morpheme(self.root[1]  * (2 if stem == Stem.D else 1),
                ['R₂', 'D'] if stem == Stem.D else ['R₂']),
        Morpheme('i' if stem == Stem.D or (stem == Stem.N and not t) else
                self.durative_vowel if t else
                self.perfective_vowel,
                ['PFTV']),
        Morpheme(self.root[-1], ['R₃']),
        personal_suffix(*p),
        Morpheme('u', ['SUBJ']) if subj and not personal_suffix(*p).text else None,
        ventive(*p) if vent else None,
        acc_pronominal_suffix(*acc) if acc else None,
        Morpheme('ma', ['CONJ']) if conj else None))