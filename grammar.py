from enum import Enum
from typing import Any, Literal, Optional
import unicodedata
import re

CIRCUMFLEX = unicodedata.lookup('COMBINING CIRCUMFLEX ACCENT')
MACRON = unicodedata.lookup('COMBINING MACRON')

STRONG_CONSONANTS = tuple('bdgḫyklmnpqrsṣštṭwz')
WEAK_CONSONANTS = tuple('ʾhḥʿwy')
CONSONANTS = tuple(list(STRONG_CONSONANTS) + list(WEAK_CONSONANTS))
VOWELS = tuple('aeuiāēūīâêûî')
SHORT_VOWELS = ('a', 'e', 'u', 'i')
def nfd(s: str) -> str:
  return unicodedata.normalize('NFD', s)
def nfc(s: str) -> str:
  return unicodedata.normalize('NFC', s)
def shorten_vowels(s: str) -> str:
  return nfc(nfd(s).replace(CIRCUMFLEX, '').replace(MACRON, ''))
def ungeminate_consonants(s: str) -> str:
  for c in CONSONANTS:
    s = s.replace(2 * c, c)
  return s

class Stem(Enum):
  G = 0
  D = 1
  Š = 2
  N = 3
  def __str__(self) -> str:
    return super().__str__().rsplit('.', 1)[-1]

class MetalanguageElement:
  pass

class Person(MetalanguageElement):
  def __init__(self, *p: Literal[1, 2, 3]):
    self._p = p
  def __repr__(self) -> str:
    return '%s%r' % (type(self).__name__, self._p)
  def __str__(self) -> str:
    return '|'.join(str(p) for p in self._p)
  def __eq__(self, other: Any) -> bool:
    return isinstance(other, Person) and other._p == self._p
  def __hash__(self) -> int:
    return hash(self._p)

class Gender(MetalanguageElement, Enum):
  M = 0
  F = 1
  def __str__(self) -> str:
    return super().__str__().rsplit('.', 1)[-1]

class Number(MetalanguageElement, Enum):
  SG = 1
  PL = 3
  def __str__(self) -> str:
    return super().__str__().rsplit('.', 1)[-1]

class VerbObject(MetalanguageElement):
  _label: str
  def __init__(self, p: Person, g: Optional[Gender], n: Number):
    self._p = p
    self._g = g
    self._n = n
  def __repr__(self) -> str:
    return '%s%r' % (type(self).__name__, (self._p, self._g, self._n))
  def __str__(self):
    return '.'.join(str(l) for l in (self._label, self._p, self._g, self._n) if l)
  def __eq__(self, other: Any) -> bool:
    return isinstance(other, VerbObject) and other._p == self._p and other._g == self._g and other._n == self._n
  def __hash__(self) -> int:
    return hash(self._p)

o = VerbObject(Person(3), Gender.F, Number.PL)

class DirectObject(VerbObject):
  _label = 'ACC'

class IndirectObject(VerbObject):
  _label = 'DAT'

class Label(MetalanguageElement, Enum):
  VENT = 0
  t = 1
  tan = 2
  PASS = 3
  CAUS = 4
  PFTV = 5
  IMPFV = 6
  D = 7
  SUBJ = 8
  CONJ = 9
  def __str__(self) -> str:
    return super().__str__().rsplit('.', 1)[-1]

class Radical(MetalanguageElement):
  def __init__(self, n: Literal[1, 2, 3]):
    self._n = n
  def __repr__(self) -> str:
    return '%s(%r)' % (type(self).__name__, self._n)
  def __str__(self) -> str:
    return 'R' + chr(ord('₁') + self._n - 1)
  def __eq__(self, other: Any) -> bool:
    return isinstance(other, Radical) and other._n == self._n
  def __hash__(self) -> int:
    return hash(self._n)  

class Root(MetalanguageElement):
  def __init__(self, root: str):
    self._root = root
  def __repr__(self) -> str:
    return '%s(%r)' % (type(self).__name__, (self._root))
  def __str__(self):
    return '√' + self._root
  def __eq__(self, other: Any) -> bool:
    return isinstance(other, Root) and other._root == self._root
  def __hash__(self) -> int:
    return hash(self._root)


class Morpheme:
  text: str
  morphographemic_spellings: list[str]
  functions: list[MetalanguageElement]
  infixes: list[tuple[int, "Morpheme"]]

  def plain_text(self):
    t = self.text
    for i, infix in self.infixes:
      t = t[:i] + infix.object_language() + t[i:]
    return t

  def object_language(self):
    t = self.text if self.text else '∅'
    for i, infix in self.infixes:
      t = '%s⟨%s⟩%s' % (t[:i], infix.object_language(), t[i:])
    return t

  def gloss(self):
    # TODO(egg): Allow for custom infix gloss placement.
    return (str(self.functions[0]) +
            ''.join('⟨%s⟩' % infix.gloss() for _, infix in self.infixes) +
            '.'.join(str(f) for f in self.functions[1:])
            if self.infixes else '.'.join(str(f) for f in self.functions))

  def __init__(self, text: str, functions: list[MetalanguageElement], infixes: list[tuple[int, "Morpheme"]] = []):
    self.text = text
    self.functions = list(functions)
    self.infixes = infixes

def personal_prefix(p: Person, g: Gender, n: Number):
  return (Morpheme('a' if n == Number.SG else 'ni', [p, n]) if p == Person(1) else
          Morpheme('ta', [p]) if p == Person(2) else
          Morpheme('i', [p]))

def personal_prefix_d(p: Person, g: Gender, n: Number):
  return (Morpheme('nu', [p, n]) if p == Person(1) and n == Number.PL else
          Morpheme('tu', [p]) if p == Person(2) else
          Morpheme('u', [p, n]) if n == Number.PL else
          Morpheme('u', [Person(1, 3), n]))

def personal_suffix(p: Person, g: Gender, n: Number, gloss_for_d : bool = False):
  return (Morpheme('ī', [p, g, n]) if p == Person(2) and g == Gender.F and n == Number.SG else
          Morpheme('ā', [p, n])    if p == Person(2) and                   n == Number.PL else
          Morpheme('ā', [p, g, n]) if p == Person(3) and g == Gender.F and n == Number.PL else
          Morpheme('ū', [p, g, n]) if p == Person(3) and g == Gender.M and n == Number.PL else
          Morpheme('', [Person(1, 3), n] if gloss_for_d and n == Number.SG and p in (Person(1), Person(3)) else
                       [p] if p == Person(1) else
                       [p, g, n] if p == Person(2) and n == Number.SG else
                       [p, n]))

def ventive(p: Person, g: Gender, n: Number):
  return Morpheme('nim' if n == Number.PL and p != 1 else
                  'm' if p == Person(2) and g == Gender.F else
                  'am',
                  [Label.VENT])

def acc_pronominal_suffix(p: Person, g: Gender, n: Number):
  return ((Morpheme('ni', [DirectObject(p, None, n)]) if p == Person(1) else
           (Morpheme('ki', [DirectObject(p, g, n)]) if g == Gender.F else
            Morpheme('ka', [DirectObject(p, g, n)])) if p == Person(2) else
           (Morpheme('ši', [DirectObject(p, g, n)]) if g == Gender.F else
            Morpheme('šu', [DirectObject(p, g, n)]))) if n == Number.SG else
          (Morpheme('niāti', [DirectObject(p, None, n)]) if p == Person(1) else
           (Morpheme('kināti', [DirectObject(p, g, n)]) if g == Gender.F else
            Morpheme('kunūti', [DirectObject(p, g, n)])) if p == Person(2) else
            (Morpheme('šināti', [DirectObject(p, g, n)]) if g == Gender.F else
             Morpheme('šunūti', [DirectObject(p, g, n)]))))

def dat_pronominal_suffix(p: Person, g: Gender, n: Number):
  return ((None if p == Person(1) else
           (Morpheme('kim', [IndirectObject(p, g, n)]) if g == Gender.F else
            Morpheme('kum', [IndirectObject(p, g, n)])) if p == Person(2) else
           (Morpheme('šim', [IndirectObject(p, g, n)]) if g == Gender.F else
            Morpheme('šum', [IndirectObject(p, g, n)]))) if n == Number.SG else
          (Morpheme('niāšim', [IndirectObject(p, None, n)]) if p == Person(1) else
           (Morpheme('kināšim', [IndirectObject(p, g, n)]) if g == Gender.F else
            Morpheme('kunūšim', [IndirectObject(p, g, n)])) if p == Person(2) else
            (Morpheme('šināšim', [IndirectObject(p, g, n)]) if g == Gender.F else
             Morpheme('šunūšim', [IndirectObject(p, g, n)]))))

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
  functions: set[MetalanguageElement]

  def __init__(self, root: str, morphemes: list[Morpheme]) -> None:
    self.root = root
    self.reconstructed = list(Morpheme(m.text, m.functions) for m in morphemes if m)
    self.morphemes = list(Morpheme(m.text, m.functions) for m in morphemes if m)
    self.functions = set(f for m in self.morphemes for f in m.functions)
    self.avoid_overlong_consonant_clusters()
    self.apply_global_a_colouring()
    self.lose_consonants()
    self.contract_vowels()
    self.lengthen_before_suffixes()
    self.assimilate_t()
    self.assimilate_object_š()
    self.assimilate_b()
    self.assimilate_ventive_dative_m()
    self.syncopate_vowels()
    self.assimilate_n()
    self.merge_root_morphemes()
    self.functions = set(f for m in self.morphemes for f in m.functions)

  def __str__(self):
    reconstruction = ''.join(m.text for m in self.reconstructed)
    actual_text = self.text()
    return ('-'.join(m.object_language() for m in self.morphemes) +
            '  (' +
            actual_text +
            ('' if reconstruction == actual_text else ' < *' + reconstruction) +
            ')\n' +
            '-'.join(m.gloss() for m in self.morphemes))

  def matches_spelling(self, transliteration: str) -> bool:
    pattern = re.sub(r"[₀₁₂₃₄₅₆₇₈₉-]", "", transliteration)
    any_consonant = "[%s]" % ''.join(CONSONANTS)
    any_vowel = "[%s]" % ''.join(VOWELS)
    pattern = re.sub(
      r"(?<!%s)" % any_consonant + "(" + any_consonant + ")" + r"(?!%s)" % any_consonant,
      r"\1+",
      pattern)
    pattern = re.sub(
      r"(%s)\1\1" % any_vowel,
      r"\1[%s]" % (MACRON + CIRCUMFLEX),
      pattern)
    

  def text(self):
    return ''.join(m.plain_text() for m in self.morphemes)
  
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

  def avoid_overlong_consonant_clusters(self):
    for i in range(len(self.morphemes)):
      if self.morphemes[i].text == 'tan':
        k, next_text = self.next_overt_morpheme(i)
        _, next_2 = self.next_overt_morpheme(k)
        lookahead = (next_text + next_2)
        if (lookahead.startswith(STRONG_CONSONANTS) and
            lookahead[1:].startswith(CONSONANTS)):
          self.morphemes[i].text = 'ta'
        elif (lookahead.startswith(WEAK_CONSONANTS) and
              lookahead[1:].startswith(CONSONANTS)):
          self.morphemes[k].text = ''

  def apply_global_a_colouring(self):
    for i in range(len(self.morphemes)):
      if (any(c in self.morphemes[i].text for c in 'ʿḥ') or
          # K p. 528 2.
          (self.morphemes[i].text == 'y' and
           Radical(1) in self.morphemes[i].functions)):
        for m in self.morphemes:
          if m and not (
              (m.text == 'ā' and m.functions in ([Person(3), Gender.F, Number.PL],
                                                 [Person(2), Number.PL])) or
              m.functions == [Label.CONJ] or
              any(isinstance(f, VerbObject) for f in m.functions) or
              m.functions == [Label.VENT]):
            m.text = nfc(nfd(m.text).replace('a', 'e'))

  def lose_consonants(self):
    for i in range(len(self.morphemes)):
      j, previous_text = self.previous_overt_morpheme(i)
      k, next_text = self.next_overt_morpheme(i)
      l, next_2 = self.next_overt_morpheme(k)
      _, next_3 = self.next_overt_morpheme(l)
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
          # V₁ʾʾV₂CV₃ > VCCV₃.
          if (Label.D not in self.morphemes[i].functions and
              self.morphemes[j].text.endswith('a')):
            # awwV₂CV₃ becomes uCCV₃ and
            # ayyV₂CV₃ becomes iCCV₃,
            # unless the gemination comes from the D-stem.
            if self.morphemes[i].text[0] == 'w':
              self.morphemes[k].text = 'u'
            elif self.morphemes[i].text[0] == 'y':
              self.morphemes[k].text = 'i'
          # Otherwise V₁ʾʾV₂CV₃ becomes V₂CCV₃.
          self.morphemes[i].text = ''
          self.morphemes[j].text = self.morphemes[j].text[:-1]
          self.morphemes[l].text *= 2
        # We are in a word-final V₁ʾʾV₂C₁ or V₁ʾʾV₂C₁C₂… case,
        # so C₁ cannot be doubled.
        elif Label.D in self.morphemes[i].functions:
          # V₁ʾʾV₂C becomes V̄₂C if the gemination comes from the D-stem.
          self.morphemes[j].text = self.morphemes[j].text[:-1]
          self.morphemes[i].text = ''
          self.morphemes[k].text = nfc(self.morphemes[k].text + MACRON)
        elif self.morphemes[i].text[0] == 'w' and  self.morphemes[j].text.endswith('a'):
          # awwV₂C > ūV₂C (leading to contraction).
          self.morphemes[j].text = self.morphemes[j].text[:-1]
          self.morphemes[i].text = 'ū'
        elif self.morphemes[i].text[0] == 'y' and  self.morphemes[j].text.endswith('a'):
          # ayyV₂C > īV₂C.
          self.morphemes[j].text = self.morphemes[j].text[:-1]
          self.morphemes[i].text = 'ī'
        else:
          # Just drop the geminated aleph, e.g., in *išaʾʾam, and let vowel
          # contraction do its thing to get išâm.
          self.morphemes[i].text = ''

      elif self.morphemes[i].text in WEAK_CONSONANTS:
        if previous_text.endswith(CONSONANTS):
          # CʾV > CʾV̄.
          self.morphemes[i].text = ''
          self.morphemes[k].text = nfc(self.morphemes[k].text + MACRON)

        if (previous_text.endswith(VOWELS) and
            next_text in ('a', 'e') and
            next_2.startswith(CONSONANTS) and next_2 == 2 * next_2[0] and
            (self.morphemes[i].text != 'w' or Label.D not in self.functions)):
          # VʾaCC > VCC for I-weak G PCL, H p. 106.
          # The a might have turned into an e depending on the ʾ.
          while l > i:
            l -= 1
            self.morphemes[l].text = ''
        elif previous_text.endswith('a') and next_text.startswith('a'):
          # awa > ū, aya > ī, aʾa > ā.
          self.morphemes[j].text = self.morphemes[j].text[:-1]
          self.morphemes[i].text = ('ū' if self.morphemes[i].text == 'w' else
                                    'ī' if self.morphemes[i].text == 'y' else
                                    'ā')
          self.morphemes[k].text = self.morphemes[k].text[1:]
        elif (self.root == 'hlk' and
              any(isinstance(f, Person) for f in self.morphemes[j].functions) and
              next_text in ('ta', 'tan')):
          # Special-case alākum -t- and -tan- morphemes:
          self.morphemes[i].text = 't'
        elif (self.root == 'hlk' and
              any(isinstance(f, Person) for f in self.morphemes[j].functions)
              and next_2 == 'i'):
          # Special-case alākum PCS:
          self.morphemes[i].text = self.morphemes[k].text
        elif (shorten_vowels(previous_text).endswith(SHORT_VOWELS) and
              shorten_vowels(next_text).startswith(CONSONANTS)):
          # H p. 38. (b) VʾC > V̄C.
          if previous_text.endswith(SHORT_VOWELS):
            self.morphemes[j].text = nfc(previous_text + MACRON)
          self.morphemes[i].text = ''
        elif self.morphemes[i].text != 'w':
          # H p. 38. (a).
          self.morphemes[i].text = ''

  def assimilate_n(self):
    for i in range(len(self.morphemes)):
      k, next_text = self.next_overt_morpheme(i)
      if (self.morphemes[i].text.endswith('n') and
          next_text.startswith(CONSONANTS) and
          # H pp. 359 & 450, no assimilation of I-n in the Ntn stem & N perfect.
          not (Radical(1) in self.morphemes[i].functions and
               Radical(2) in self.morphemes[k].functions and
               Label.PASS in self.functions and
               (Label.tan in self.functions or
                Label.t in self.functions))):
        self.morphemes[i].text = self.morphemes[i].text[:-1] + next_text[0]

  def assimilate_b(self):
    # H p. 49.
    for i in range(len(self.morphemes)):
      _, next_text = self.next_overt_morpheme(i)
      if (self.morphemes[i].text.endswith('b') and
          next_text.startswith('m')):
        self.morphemes[i].text = self.morphemes[i].text[:-1] + next_text[0]

  def assimilate_t(self):
    for i in range(len(self.morphemes)):
      _, previous_text = self.previous_overt_morpheme(i)
      # H p. 155.
      if ((Label.t in self.morphemes[i].functions or
           Label.tan in self.morphemes[i].functions) and
          self.morphemes[i].text.startswith('t') and
          previous_text.endswith(('d', 'ṭ', 's', 'ṣ'))):
        self.morphemes[i].text = previous_text[-1] + self.morphemes[i].text[1:]

  def assimilate_object_š(self):
    for i in range(len(self.morphemes)):
      j, previous_text = self.previous_overt_morpheme(i)
      # H p. 170.
      if (any(isinstance(f, VerbObject) for f in self.morphemes[i].functions) and
          self.morphemes[i].text.startswith('š') and
          previous_text.endswith(('d', 't', 'ṭ', 's', 'ṣ', 'z', 'š'))):
        self.morphemes[j].text = self.morphemes[j].text[:-1] + 's'
        self.morphemes[i].text = 's' + self.morphemes[i].text[1:]

  def assimilate_ventive_dative_m(self):
    for i in range(len(self.morphemes)):
      _, next_text = self.next_overt_morpheme(i)
      # H p. 170.
      if ((Label.VENT in self.morphemes[i].functions or
           any(isinstance(f, IndirectObject) for f in self.morphemes[i].functions)) and
          self.morphemes[i].text.endswith('m') and
          next_text.startswith(CONSONANTS)):
        self.morphemes[i].text = self.morphemes[i].text[:-1] + next_text[0]

  def syncopate_vowels(self):
    regex = "(?:[V][C])+([V])[C][^C]".replace('V', ''.join(SHORT_VOWELS)).replace('C', ''.join(CONSONANTS))
    match = re.search(regex, self.text())
    if match:
      syncopated_vowel_index = match.start(1)
      i = 0
      for m in self.morphemes:
        for l in range(len(m.text)):
          if i == syncopated_vowel_index:
            if any(isinstance(f, VerbObject) for f in m.functions):
              return
            m.text = m.text[:l] + m.text[l+1:]
            return
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
      if Label.CONJ in m.functions or any(isinstance(f, VerbObject) for f in m.functions):
        k, previous = self.previous_overt_morpheme(i)
        if previous.endswith(SHORT_VOWELS):
          self.morphemes[k].text = nfc(self.morphemes[k].text + MACRON)

  def merge_root_morphemes(self):
    root_morpheme = ''
    root_functions : list[MetalanguageElement] = [Root(self.root)]
    root_start = None
    root_end = None
    infixes : list[tuple[int, Morpheme]] = []
    for i, m in enumerate(self.morphemes):
      if root_start is not None and (Label.t in m.functions or Label.tan in m.functions):
        # TODO(egg): Do the fancy thing of sticking the infix inside the root gloss.
        infixes.append(
          (len(root_morpheme),
           Morpheme(m.text, [f for f in m.functions if not isinstance(f, Radical)])))
        root_functions += [f for f in m.functions if isinstance(f, Radical)]
        continue
      if Radical(1) in m.functions:
        root_start = i
      if root_start is not None and root_end is None:
        root_morpheme += m.text
        root_functions += (f for f in m.functions if f not in root_functions)
      if Radical(3) in m.functions:
        root_end = i
    if not root_end:
      raise ValueError('Could not find third radical in %s' % self)
    root_functions.remove(Radical(1))
    root_functions.remove(Radical(2))
    root_functions.remove(Radical(3))
    self.morphemes = self.morphemes[:root_start] + [Morpheme(root_morpheme, root_functions, infixes)] + self.morphemes[root_end + 1:]
class Verb:
  root: str
  durative_vowel: str
  perfective_vowel: str

  def __init__(self, root: str, durative_vowel: str, perfective_vowel: str) -> None:
    self.root = root
    self.durative_vowel = durative_vowel
    self.perfective_vowel = perfective_vowel
  def finite_form(
      self,
      p: tuple[Person, Gender, Number],
      pftv: bool,
      t: None|Literal[Label.t, Label.tan]=None,
      subj: bool = False,
      conj: bool = False,
      vent: bool = False,
      stem: Stem = Stem.G,
      acc: tuple[Person, Gender, Number]|None = None,
      dat: tuple[Person, Gender, Number]|None = None) -> KamilDecomposition:
    if ((acc and acc[0] == 1 and acc[-1] == Number.SG) or
        (dat and dat[0] == 1 and dat[-1] == Number.SG)):
      vent = True
    if vent:
      subj = False
    d_prefix = stem in (Stem.D, Stem.Š) or (
      self.root.startswith('w') and
      (self.durative_vowel == 'a' or self.root.endswith(WEAK_CONSONANTS)))
    morphemes : list[Morpheme] = []
    morphemes.append(personal_prefix_d(*p) if d_prefix else
                     personal_prefix(*p))
    if stem == Stem.N:
      morphemes.append(Morpheme('n', [Label.PASS]))
    if stem == Stem.Š:
      morphemes.append(Morpheme('š' if t else 'ša', [Label.CAUS]))
    if t and stem in (Stem.N, Stem.Š):
      if t == Label.tan:
        if not pftv:
          morphemes.append(Morpheme('tana', [t]))
        else:
          morphemes.append(Morpheme('tan', [t]))
      else:
        morphemes.append(Morpheme('ta', [t]))

    if (self.root.startswith('w') and
        self.durative_vowel != 'a' and
        not self.root.endswith(WEAK_CONSONANTS)):
      # Ugly hack, we should do this with the other transformations.
      morphemes.append(Morpheme('y', [Radical(1)]))
    elif stem == Stem.N and self.root.startswith(WEAK_CONSONANTS):
      morphemes.append(Morpheme('n', [Radical(1), Label.PASS]))
    else:
      morphemes.append(Morpheme(self.root[0], [Radical(1)]))

    if t and stem not in (Stem.N, Stem.Š):
      morphemes.append(Morpheme('ta' if t == Label.t else 'tan', [t]))

    # H p. 309.
    # TODO(egg): Can we do that with transformation rules instead?
    š_unlike_g = stem == stem.Š and self.root[0] not in WEAK_CONSONANTS

    if pftv:
      if stem in (Stem.D, Stem.N) and not t:
        morphemes.append(Morpheme('a', [Label.PFTV]))
    elif t != Label.t and not š_unlike_g:
      morphemes.append(Morpheme('a', [Label.IMPFV]))

    if stem == stem.D:
      morphemes.append(Morpheme(2 * self.root[1], [Radical(2), Label.D]))
    elif not pftv and not š_unlike_g and not (stem == Stem.N and t == Label.tan):
      morphemes.append(Morpheme(2 * self.root[1], [Radical(2), Label.IMPFV]))
    else:
      morphemes.append(Morpheme(self.root[1], [Radical(2)]))

    if pftv:
      morphemes.append(
        Morpheme(
          'i' if stem in (Stem.D, Stem.Š) or (stem == Stem.N and not t) else
          self.durative_vowel if t else
          self.perfective_vowel,
          [Label.PFTV]))
    else:
      morphemes.append(
        Morpheme('a' if stem in (Stem.D, Stem.Š) or
                        (stem == Stem.N and self.durative_vowel != 'i' and
                         not self.root.endswith(WEAK_CONSONANTS)) else
                 self.durative_vowel,
                 [Label.IMPFV]))

    morphemes.append(Morpheme(self.root[-1], [Radical(3)]))
    p_suffix = personal_suffix(*p, gloss_for_d=d_prefix)
    morphemes.append(p_suffix)
    if subj and not p_suffix.text:
      morphemes.append(Morpheme('u', [Label.SUBJ]))
    if vent:
      morphemes.append(ventive(*p))
    if dat:
      suffix = dat_pronominal_suffix(*dat)
      if suffix:
        morphemes.append(suffix)
    if acc:
      morphemes.append(acc_pronominal_suffix(*acc))
    if conj:
      morphemes.append(Morpheme('ma', [Label.CONJ]))
    return KamilDecomposition(self.root, morphemes)

  def durative(self, p: tuple[Person, Gender, Number], **kwargs):
    return self.finite_form(p, pftv=False, **kwargs)
  def perfective(self, p: tuple[Person, Gender, Number], **kwargs):
    return self.finite_form(p, pftv=True, **kwargs)