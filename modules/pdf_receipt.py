from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def receipt(cart,service,total_amount):
    b=BytesIO();c=canvas.Canvas(b,pagesize=letter);y=740
    c.setFont('Helvetica-Bold',18);c.drawString(50,y,'Coffee Break | Comprobante de demostración');y-=30
    c.setFont('Helvetica',10);c.drawString(50,y,datetime.now().strftime('Fecha: %Y-%m-%d %H:%M'));y-=20
    c.drawString(50,y,f'Servicio: {service or "sin seleccionar"}');y-=30
    c.setFont('Helvetica-Bold',11);c.drawString(50,y,'Producto');c.drawString(340,y,'Cantidad');c.drawString(430,y,'Precio');y-=18
    c.setFont('Helvetica',10)
    for it in cart:
        line=f"{it['name']} ({it['size']})" + (f" + {', '.join(it['extras'])}" if it['extras'] else '')
        c.drawString(50,y,line[:55]);c.drawString(340,y,str(it['qty']));c.drawString(430,y,f"${it['unit_price']*it['qty']:.2f} MXN");y-=18
        if y<80:c.showPage();y=740
    y-=10;c.setFont('Helvetica-Bold',12);c.drawString(50,y,f'Total: ${total_amount:.2f} MXN');y-=30
    c.setFont('Helvetica',9);c.drawString(50,y,'Pedido ficticio: no se envió ni se procesó pago.');c.save();b.seek(0);return b.getvalue()
