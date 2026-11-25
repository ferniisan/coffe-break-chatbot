import streamlit as st, json
from pathlib import Path
from modules.dialogue import handle, MENU_TEXT
from modules.orders import MENU,subtotal,total,DELIVERY_FEE
from modules.pdf_receipt import receipt
from modules.nlp import classify,entities,normalize
BASE=Path(__file__).resolve().parent
st.set_page_config(page_title='Coffee Break | Chatbot',page_icon='☕',layout='wide')

if 'dialog' not in st.session_state: st.session_state.dialog={'cart':[],'pending':None,'service':None,'confirmed':False,'last_intent':None}
if 'messages' not in st.session_state: st.session_state.messages=[{'role':'assistant','content':'¡Hola! ☕ Soy el asistente de Coffee Break. Los productos, precios y pedidos son datos ficticios para una demostración académica. ¿Qué se te antoja?'}]
if 'trace' not in st.session_state: st.session_state.trace=[]

def respond(msg):
    st.session_state.messages.append({'role':'user','content':msg})
    result=handle(msg,st.session_state.dialog)
    st.session_state.messages.append({'role':'assistant','content':result['reply']})
    st.session_state.trace.append({'message':msg,**result})

st.title('☕ Coffee Break')
st.caption('Cafetería ficticia · Demo académica de PLN y gestión de diálogo · Precios en MXN')
with st.sidebar:
    st.header('Coffee Break')
    st.write('Menú de muestra, carrito local y reglas conversacionales.')
    if st.button('Reiniciar conversación',use_container_width=True):
        st.session_state.dialog={'cart':[],'pending':None,'service':None,'confirmed':False,'last_intent':None};st.session_state.messages=[{'role':'assistant','content':'¡Hola! ☕ ¿Qué te gustaría pedir?'}];st.session_state.trace=[];st.rerun()
    st.divider();st.subheader('Acceso rápido')
    for label,query in [('☕ Menú','menu'),('🎁 Promociones','promociones'),('🛒 Carrito','carrito'),('❔ Ayuda','ayuda')]:
        if st.button(label,use_container_width=True):respond(query);st.rerun()

chat_tab,menu_tab,cart_tab,learn_tab=st.tabs(['💬 Conversación','📋 Menú','🛒 Carrito','🧠 ¿Cómo funciona el chatbot?'])
with chat_tab:
    for msg in st.session_state.messages:
        with st.chat_message(msg['role']):st.markdown(msg['content'])
    user_input=st.chat_input('Escribe tu mensaje...')
    if user_input:respond(user_input);st.rerun()
with menu_tab:
    st.subheader('Menú de demostración')
    st.warning('Catálogo, ingredientes, promociones y precios son ficticios. No se verifican alergias ni contaminación cruzada.')
    for p in MENU:
        with st.expander(f"{p['name']} | {p['category'].capitalize()}"):
            st.write('**Ingredientes:** '+', '.join(p['ingredients']))
            st.write('**Tamaños y precios:** '+', '.join(f'{s}: ${v} MXN' for s,v in p['sizes'].items()))
            if p.get('extras'):st.write('**Extras:** '+', '.join(f'{e} +${v}' for e,v in p['extras'].items()))
            if st.button(f"Pedir {p['name']}",key=f"menu_{p['id']}"):
                respond('Quiero '+p['name']);st.rerun()
    promos=json.loads((BASE/'data/promotions.json').read_text(encoding='utf8'))['promotions']
    st.subheader('Promociones')
    for promo in promos:st.info(promo['description'])
with cart_tab:
    st.subheader('Carrito de compras')
    cart=st.session_state.dialog['cart']
    if cart:
        for idx,item in enumerate(cart):st.write(f"**{item['qty']} × {item['name']} ({item['size']})** — ${item['unit_price']*item['qty']} MXN"+(f" · Extras: {', '.join(item['extras'])}" if item['extras'] else ''))
        st.write(f"**Subtotal: ${subtotal(cart)} MXN**")
        service=st.session_state.dialog['service'];st.write(f"Servicio: {service or 'sin seleccionar'}")
        st.write(f"**Total: ${total(cart,service)} MXN**"+(f" (incluye $25 de entrega demo)" if service=='delivery' else ''))
        s=st.radio('Tipo de servicio',['Recoger en cafetería','Entrega a domicilio'],horizontal=True,key='serv_choice')
        st.session_state.dialog['service']='pickup' if s.startswith('Recoger') else 'delivery'
        if st.button('Confirmar pedido de demostración',type='primary'):
            respond('confirmar');st.rerun()
        if st.session_state.dialog['confirmed']:
            pdf=receipt(cart,st.session_state.dialog['service'],total(cart,st.session_state.dialog['service']))
            st.download_button('Descargar comprobante PDF',data=pdf,file_name='coffee_break_comprobante_demo.pdf',mime='application/pdf')
        if st.button('Vaciar / cancelar pedido'):respond('cancelar pedido');st.rerun()
    else:st.info('El carrito está vacío. Puedes agregar productos desde el menú o conversar con el chatbot.')
with learn_tab:
    st.subheader('Arquitectura')
    st.markdown('''```mermaid\nflowchart TD\n A[Usuario / Streamlit] --> B[Normalización]\n B --> C[Detector de intenciones]\n B --> D[Extractor de entidades]\n C --> E[Gestor de diálogo]\n D --> E\n E --> F[Reglas y carrito]\n F --> G[JSON: menú / FAQ / promociones]\n F --> H[Respuesta]\n F --> I[Comprobante PDF]\n```''')
    st.markdown('**Frontend:** Streamlit renderiza chat, catálogo, carrito y panel de aprendizaje. **Backend:** Python normaliza, clasifica, extrae entidades, administra contexto y calcula pedidos.')
    st.subheader('Demostración de interpretación')
    demo=st.text_input('Escribe un mensaje para analizar sin alterar el carrito',placeholder='Ej. Quiero un Cold Brew grande')
    if demo:
        c=classify(demo);e=entities(demo,MENU)
        st.write('**Intención:**',c['intent'],' · **Confianza heurística:**',c['confidence'])
        st.json(e);st.write('Texto normalizado:',normalize(demo))
    st.subheader('Último turno real')
    if st.session_state.trace:
        tr=st.session_state.trace[-1]
        st.write('**Intención:**',tr['intent'],' · **Confianza heurística:**',tr['confidence']);st.write('**Entidades:**');st.json(tr['entities']);st.write('**Regla/fuente:**',tr['rule']);st.write('**Estado contextual:**');st.json(tr['state_snapshot'])
    else:st.caption('Aún no hay turnos para mostrar.')
    st.subheader('Componentes de PLN')
    st.markdown('- Normalización de texto: minúsculas, retiro de acentos y signos.\n- Clasificación: patrones almacenados en JSON y coincidencia aproximada.\n- Entidades: producto, tamaño, cantidad, extras, restricciones, presupuesto, personas y servicio.\n- Contexto: estado pendiente y carrito dentro de `st.session_state`.\n- Fallback: solicita aclaración cuando no reconoce el mensaje.')
    st.subheader('Privacidad y alcance')
    st.write('No se procesan pagos, no se transmiten pedidos y no se almacenan datos personales. El estado vive en la sesión; el comprobante se descarga voluntariamente.')
