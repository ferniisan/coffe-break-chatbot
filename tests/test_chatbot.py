import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]) )
from modules.nlp import classify,entities
from modules.dialogue import handle
from modules.orders import add_item,subtotal,total,remove_item,modify_size,MENU

class NLPTests(unittest.TestCase):
 def test_01_greet(self):self.assertEqual(classify('hola')['intent'],'greet')
 def test_02_goodbye(self):self.assertEqual(classify('hasta luego')['intent'],'goodbye')
 def test_03_menu(self):self.assertEqual(classify('ver menú')['intent'],'menu')
 def test_04_price(self):self.assertEqual(classify('cuánto cuesta')['intent'],'price')
 def test_05_ingredients(self):self.assertEqual(classify('ingredientes')['intent'],'ingredients')
 def test_06_recommend(self):self.assertEqual(classify('qué me recomiendas')['intent'],'recommend')
 def test_07_promos(self):self.assertEqual(classify('promociones')['intent'],'promotions')
 def test_08_start(self):self.assertEqual(classify('quiero pedir')['intent'],'start_order')
 def test_09_add(self):self.assertEqual(classify('agrega algo')['intent'],'add')
 def test_10_modify(self):self.assertEqual(classify('cambiar tamaño')['intent'],'modify')
 def test_11_remove(self):self.assertEqual(classify('quita')['intent'],'remove')
 def test_12_cart(self):self.assertEqual(classify('carrito')['intent'],'cart')
 def test_13_confirm(self):self.assertEqual(classify('confirmar')['intent'],'confirm')
 def test_14_cancel(self):self.assertEqual(classify('cancelar pedido')['intent'],'cancel')
 def test_15_hours(self):self.assertEqual(classify('horario')['intent'],'hours')
 def test_16_delivery(self):self.assertEqual(classify('entrega a domicilio')['intent'],'delivery')
 def test_17_payment(self):self.assertEqual(classify('formas de pago')['intent'],'payment')
 def test_18_help(self):self.assertEqual(classify('ayuda')['intent'],'help')
 def test_19_thanks(self):self.assertEqual(classify('gracias')['intent'],'thanks')
 def test_20_fallback(self):self.assertEqual(classify('xyz blorf quack')['intent'],'unknown')
 def test_21_size(self):self.assertEqual(entities('tamaño grande',MENU)['size'],'grande')
 def test_22_qty(self):self.assertEqual(entities('quiero 3',MENU)['quantity'],3)
 def test_23_product(self):self.assertEqual(entities('un cold brew',MENU)['product'],'coldbrew')
 def test_24_extras(self):self.assertIn('vainilla',entities('vainilla',MENU)['extras'])
 def test_25_service(self):self.assertEqual(entities('a domicilio',MENU)['service'],'delivery')

class CartDialogueTests(unittest.TestCase):
 def fresh(self):return {'cart':[],'pending':None,'service':None,'confirmed':False}
 def test_26_add_and_subtotal(self):c=[];add_item(c,'latte','mediana');self.assertEqual(subtotal(c),65)
 def test_27_delivery_fee(self):c=[];add_item(c,'cookie','único');self.assertEqual(total(c,'delivery'),60)
 def test_28_remove(self):c=[];add_item(c,'cookie','único');self.assertTrue(remove_item(c,'cookie'));self.assertEqual(len(c),0)
 def test_29_modify_size(self):c=[];add_item(c,'latte','chica');self.assertTrue(modify_size(c,'grande'));self.assertEqual(c[-1]['unit_price'],75)
 def test_30_context_size(self):s=self.fresh();r=handle('quiero un cold brew',s);self.assertEqual(s['pending']['product'],'coldbrew');r=handle('grande',s);self.assertEqual(s['cart'][0]['size'],'grande');self.assertEqual(r['intent'],'context_size')
 def test_31_unknown_recovery(self):s=self.fresh();r=handle('blorp xyz',s);self.assertIn('No entendí',r['reply'])
 def test_32_restriction_warning(self):s=self.fresh();r=handle('soy vegano',s);self.assertIn('no confirmar seguridad',r['reply'])
 def test_33_service_prompt(self):s=self.fresh();add_item(s['cart'],'cookie','único');r=handle('confirmar',s);self.assertIn('recoger',r['reply'])
 def test_34_cancel_flow(self):s=self.fresh();add_item(s['cart'],'cookie','único');handle('cancelar pedido',s);self.assertFalse(s['cart'])
 def test_35_recovery_after_pending(self):s=self.fresh();handle('quiero un latte',s);r=handle('mediana',s);self.assertEqual(len(s['cart']),1);self.assertIn('postre',r['reply'])

if __name__=='__main__':unittest.main()
