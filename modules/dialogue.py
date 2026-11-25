"""Context-aware turn handler. Business responses are grounded in the demo data."""
import json
from pathlib import Path
from .nlp import normalize,classify,entities
from .orders import MENU,add_item,subtotal,total,remove_item,modify_size,get_product
BASE=Path(__file__).resolve().parents[1]
PROMOS=json.loads((BASE/'data/promotions.json').read_text(encoding='utf8'))['promotions']
FAQ=json.loads((BASE/'data/faqs.json').read_text(encoding='utf8'))['faqs']

MENU_TEXT='\n'.join(f"• {p['name']}: "+', '.join(f"{s} ${v} MXN" for s,v in p['sizes'].items())+f" | Ingredientes: {', '.join(p['ingredients'])}" for p in MENU)
def product_text(p):return f"{p['name']} — {', '.join(f'{s}: ${v} MXN' for s,v in p['sizes'].items())}. Ingredientes: {', '.join(p['ingredients'])}."

def handle(text,state):
    n=normalize(text); cls=classify(text); intent=cls['intent']; ent=entities(text,MENU)
    state.setdefault('cart',[]); state.setdefault('pending',None);state.setdefault('service',None);state.setdefault('confirmed',False);state.setdefault('last_intent',None)
    pending=state['pending'];reply='';rule='';
    # Pending size is resolved first, so "grande" is not interpreted as a fresh intent.
    if pending and pending.get('kind')=='size':
        size=ent.get('size')
        p=get_product(pending['product'])
        if size:
            add_item(state['cart'],pending['product'],size,pending.get('qty',1),pending.get('extras',[]));state['pending']=None
            reply=f"Añadí {p['name']} tamaño {size}. ¿Deseas agregar un postre o revisar tu pedido?";rule='Contexto pendiente: elección de tamaño aplicada al producto solicitado.';intent='context_size'
        else:reply='¿Qué tamaño prefieres: chica, mediana o grande?';rule='Se mantiene la solicitud pendiente.';intent='clarification'
    elif ent.get('product') and (intent in ('add','start_order','unknown') or pending is None):
        pid=ent['product'];p=get_product(pid);size=ent.get('size');qty=ent.get('quantity',1);extras=ent.get('extras',[])
        if size and size in p['sizes']:
            add_item(state['cart'],pid,size,qty,extras);reply=f"Añadí {qty} {p['name']} tamaño {size}. ¿Deseas agregar algo más o revisar tu pedido?";rule='Catálogo y precios JSON + regla de carrito.'
        elif len(p['sizes'])==1:
            add_item(state['cart'],pid,'único',qty,extras);reply=f"Añadí {p['name']}. ¿Deseas agregar algo más o revisar tu pedido?";rule='Producto con tamaño único desde el catálogo.'
        else:
            state['pending']={'kind':'size','product':pid,'qty':qty,'extras':extras};reply=f"Claro, {p['name']}. ¿Qué tamaño prefieres: chica, mediana o grande?";rule='Gestor de diálogo guarda producto y espera entidad tamaño.'
        intent='add' if intent=='unknown' else intent
    elif ent.get('restriction') and not ent.get('product'):
        reply='Puedo señalar ingredientes declarados, pero no confirmar seguridad para alergias, contaminación cruzada ni ausencia de trazas. ¿Qué producto quieres consultar?';rule='Advertencia de restricción alimentaria: datos insuficientes para garantía.';intent='restriction'
    elif intent=='greet':reply='¡Hola! ☕ Bienvenido a Coffee Break. ¿Te muestro el menú o te ayudo a pedir?';rule='Patrones de saludo.'
    elif intent=='goodbye':reply='¡Gracias por visitar Coffee Break! Que tengas un gran día.';rule='Patrones de despedida.'
    elif intent in ('menu','price','ingredients'):reply='Menú de demostración:\n'+MENU_TEXT;rule='Archivo data/menu.json.'
    elif intent=='promotions':reply='Promociones de demostración:\n'+'\n'.join('• '+x['description'] for x in PROMOS if x['active']);rule='Archivo data/promotions.json.'
    elif intent=='recommend':
        if 'frio' in n or 'fría' in n or 'cold' in n: p=get_product('coldbrew')
        elif 'veg' in n or 'vegetal' in n: p=get_product('americano')
        elif 'dulce' in n: p=get_product('chai')
        else:p=get_product('latte')
        reply='Te recomiendo '+product_text(p)+' Si tienes alergias, confirma con el personal: este catálogo de demostración no garantiza ausencia de contaminación cruzada.';rule='Regla heurística de preferencia + catálogo.'
    elif intent=='start_order':reply='¡Claro! Escribe el nombre de una bebida o alimento, por ejemplo: un Cold Brew.';rule='Inicio de flujo de pedido.'
    elif intent=='remove':
        target=next((p['name'] for p in MENU if normalize(p['name']) in n),None)
        if target and remove_item(state['cart'],target):reply=f'Removí {target} del carrito.'
        else:reply='¿Qué producto deseas quitar? Escribe su nombre.'
        rule='Regla de eliminación por coincidencia con producto.'
    elif intent=='modify':
        size=ent.get('size');reply=('Actualicé el tamaño del último artículo.' if size and modify_size(state['cart'],size) else 'Indica el tamaño nuevo (chica, mediana o grande) para el último artículo.');rule='Modificación del último artículo en el carrito.'
    elif intent=='cart':
        if state['cart']:reply='Tu pedido:\n'+'\n'.join(f"• {i['qty']} × {i['name']} ({i['size']}) — ${i['unit_price']*i['qty']} MXN" for i in state['cart'])+f"\nSubtotal: ${subtotal(state['cart'])} MXN. Total actual: ${total(state['cart'],state['service'])} MXN.";rule='Carrito de sesión y cálculo de subtotal/total.'
        else:reply='Tu carrito está vacío. Puedes pedir una bebida o consultar el menú.';rule='Estado del carrito.'
    elif intent=='delivery':
        service=ent.get('service')
        if service:state['service']=service;reply=f"Servicio seleccionado: {'entrega a domicilio (+$25 MXN ficticios)' if service=='delivery' else 'recoger en cafetería'}. ¿Revisamos tu pedido?"
        else:reply='¿Prefieres entrega a domicilio o recoger en cafetería?';state['pending']={'kind':'service'}
        rule='Regla de servicio y tarifa demo.'
    elif pending and pending.get('kind')=='service':
        service=ent.get('service') or ('delivery' if 'domicilio' in n else 'pickup' if 'recoger' in n else None)
        if service:state['service']=service;state['pending']=None;reply=f"Servicio seleccionado: {service}. ¿Deseas revisar y confirmar?"
        else:reply='¿Entrega a domicilio o recoger?';rule='Servicio pendiente.'
    elif intent=='confirm':
        if not state['cart']:reply='No hay productos que confirmar.'
        elif not state['service']:reply='¿Tu pedido será para recoger o para entrega a domicilio?';state['pending']={'kind':'service'}
        else:state['confirmed']=True;reply=f"Pedido confirmado en modo demo. Servicio: {state['service']}. Total: ${total(state['cart'],state['service'])} MXN. Puedes descargar el comprobante. No se envió a una tienda.";rule='Confirmación local de pedido simulado.'
    elif intent=='cancel':state['cart']=[];state['pending']=None;state['service']=None;state['confirmed']=False;reply='Cancelé el pedido de demostración y vacié el carrito.';rule='Reinicio de estado comercial.'
    elif intent=='hours':reply=FAQ[0]['answer'];rule='FAQ horario.'
    elif intent=='payment':reply=next(x['answer'] for x in FAQ if x['q']=='pagos');rule='FAQ formas de pago.'
    elif intent=='help':reply='Puedo mostrar el menú, explicar ingredientes y precios, recomendar, consultar promociones, armar/modificar/cancelar un carrito y simular confirmación. Prueba: “Quiero un Cold Brew”.';rule='Respuesta de ayuda.'
    elif intent=='thanks':reply='¡Con gusto! ☕';rule='Patrón de agradecimiento.'
    elif ent.get('restriction'):
        reply='Puedo señalar ingredientes declarados, pero no confirmar seguridad para alergias, contaminación cruzada ni ausencia de trazas. ¿Qué producto quieres consultar?';rule='Advertencia de restricción alimentaria: datos insuficientes para garantía.'
    else:reply='No entendí del todo. ¿Quieres consultar el menú, ingredientes, promociones o hacer un pedido?';rule='Fallback seguro: aclaración sin inventar.';intent='unknown'
    state['last_intent']=intent
    return {'reply':reply,'intent':intent,'confidence':cls['confidence'],'entities':ent,'rule':rule,'state_snapshot':{'pending':state.get('pending'),'cart_count':len(state['cart']),'service':state.get('service'),'confirmed':state.get('confirmed')}}
