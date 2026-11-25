"""Lightweight Spanish NLP: normalization, rule patterns, approximate matching and entities."""
import json, re, unicodedata
from difflib import SequenceMatcher
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]

def normalize(text):
    text=text.lower().strip()
    text=''.join(c for c in unicodedata.normalize('NFD',text) if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9\s$]', ' ', text).strip()

INTENTS=json.loads((BASE/'data/intents.json').read_text(encoding='utf8'))['intents']

def classify(text):
    t=normalize(text); best=('unknown',0.0)
    for intent in INTENTS:
        for pattern in intent['patterns']:
            p=normalize(pattern)
            score=1.0 if p in t else SequenceMatcher(None,p,t).ratio()
            # Exact token/phrase containment beats fuzzy matching.
            if score>best[1]: best=(intent['name'],score)
    if best[1]<0.48: return {'intent':'unknown','confidence':best[1]}
    return {'intent':best[0],'confidence':round(best[1],3)}

SIZE_MAP={'chica':'chica','pequeño':'chica','pequeno':'chica','small':'chica','mediana':'mediana','mediano':'mediana','regular':'mediana','grande':'grande','large':'grande'}

def entities(text,products):
    t=normalize(text); out={}
    for key,val in SIZE_MAP.items():
        if normalize(key) in t: out['size']=val; break
    m=re.search(r'\b(\d+)\b',t)
    if m: out['quantity']=int(m.group(1))
    for p in products:
        if normalize(p['name']) in t or normalize(p['id']) in t:
            out['product']=p['id']; out['product_name']=p['name']; break
    extra_words=['leche vegetal','shot extra','vainilla']
    for ex in extra_words:
        if normalize(ex) in t: out.setdefault('extras',[]).append(ex)
    if any(x in t for x in ['vegano','vegan','sin lactosa','vegetal']): out['restriction']='vegan_or_dairy_free'
    if any(x in t for x in ['sin gluten','gluten']): out['restriction']='gluten'
    if 'domicilio' in t: out['service']='delivery'
    if 'recoger' in t or 'pickup' in t: out['service']='pickup'
    budget=re.search(r'(?:menos de|hasta|presupuesto|\$)\s*(\d+)',t)
    if budget: out['budget']=int(budget.group(1))
    people=re.search(r'(\d+)\s*(?:personas|para nosotros|clientes)',t)
    if people: out['people']=int(people.group(1))
    return out
