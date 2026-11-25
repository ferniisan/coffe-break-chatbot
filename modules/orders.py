from pathlib import Path
import json
BASE=Path(__file__).resolve().parents[1]
MENU=json.loads((BASE/'data/menu.json').read_text(encoding='utf8'))['products']
DELIVERY_FEE=25

def get_product(pid): return next((p for p in MENU if p['id']==pid),None)
def add_item(cart,pid,size,qty=1,extras=None):
    p=get_product(pid)
    if not p: return False
    size=size if size in p['sizes'] else ('único' if 'único' in p['sizes'] else 'mediana')
    extras=extras or []
    extra_prices=p.get('extras',{})
    ex_cost=sum(extra_prices.get(e,0) for e in extras)
    cart.append({'id':pid,'name':p['name'],'size':size,'qty':max(1,int(qty)),'extras':extras,'unit_price':p['sizes'][size]+ex_cost})
    return True
def subtotal(cart): return sum(i['unit_price']*i['qty'] for i in cart)
def total(cart,service=None): return subtotal(cart)+(DELIVERY_FEE if service=='delivery' and cart else 0)
def remove_item(cart,name):
    key=name.lower()
    for i,item in enumerate(cart):
        if key in item['name'].lower() or key in item['id']:
            cart.pop(i); return True
    return False
def modify_size(cart,size):
    if not cart:return False
    item=cart[-1];p=get_product(item['id'])
    if size not in p['sizes']:return False
    old=item['unit_price'];item['size']=size;item['unit_price']=p['sizes'][size]+sum(p.get('extras',{}).get(e,0) for e in item['extras']);return True
