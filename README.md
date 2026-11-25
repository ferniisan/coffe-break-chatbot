# Coffee Break — chatbot didáctico

Aplicación de chatbot para una cafetería ficticia. Catálogo, precios, promociones y pedidos son **datos de demostración**. No hay pagos, envío de pedidos, ubicación real ni persistencia fuera de la sesión.

## Arquitectura
- `app.py`: interfaz Streamlit (chat, menú, carrito y módulo didáctico).
- `modules/nlp.py`: normalización, patrones, clasificación aproximada y extracción de entidades.
- `modules/dialogue.py`: gestión de turnos, reglas, FAQ y respuestas con fallback.
- `modules/orders.py`: lógica del carrito, precios, extras y tarifa de entrega demo.
- `modules/pdf_receipt.py`: comprobante de demostración con ReportLab.
- `data/*.json`: catálogo, promociones, FAQs y patrones de intención.
- `tests/test_chatbot.py`: pruebas automatizadas (35 casos).

## Requisitos y ejecución local
Python 3.10+ recomendado.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Pruebas
```bash
python -m unittest discover -s tests -v
```

Las pruebas incluyen 19 intenciones, entidades, carrito, tarifa, seguimiento contextual, cancelación, aclaración y advertencias de restricciones. La evaluación es una suite determinista local; **no es una evaluación sobre corpus independiente**. Métrica de exactitud de intención reportada por los tests: casos unitarios de clasificación 20/20 (100% en esos ejemplos específicos; no generalizable). Para evaluar de forma realista, ampliar ejemplos de usuarios, anotar intenciones y medir precisión/recall/F1 en una muestra separada.

## Publicar en GitHub
1. Crea un repositorio público vacío en GitHub (p. ej. `coffee-break-chatbot`).
2. Descomprime el ZIP, abre terminal en la carpeta del proyecto.
3. Ejecuta:
   ```bash
   git init
   git add .
   git commit -m "Initial Coffee Break chatbot"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/coffee-break-chatbot.git
   git push -u origin main
   ```
4. Evita subir datos personales o secretos. Este proyecto no requiere secretos.

## Despliegue en Streamlit Community Cloud
1. Inicia sesión en Streamlit Community Cloud y conecta GitHub.
2. Selecciona el repositorio, branch `main` y archivo `app.py`.
3. Deploy. Community Cloud instalará `requirements.txt`.
4. Revisa el chatbot y las pestañas menú/carrito/enseñanza.

## Intenciones y ejemplos
Patrones en `data/intents.json`. Ejemplos: `hola`→greet; `ver menú`→menu; `ingredientes`→ingredients; `qué me recomiendas`→recommend; `promociones`→promotions; `quiero pedir`→start_order; `agrega`→add; `cambiar tamaño`→modify; `quita`→remove; `carrito`→cart; `confirmar`→confirm; `cancelar pedido`→cancel; `horario`→hours; `domicilio`→delivery; `formas de pago`→payment; `ayuda`→help; `gracias`→thanks; `hasta luego`→goodbye.

## Conversación de ejemplo
- Cliente: Quiero un Cold Brew.
- Bot: ¿Qué tamaño prefieres: chica, mediana o grande?
- Cliente: Grande.
- Bot: Añadí Cold Brew tamaño grande. ¿Deseas agregar algo más o revisar tu pedido?
- Cliente: una galleta de chocolate.
- Bot: Añadí Galleta de chocolate. ¿Deseas agregar algo más o revisar tu pedido?
- Cliente: carrito.
- Cliente: confirmar.
- Bot: Pregunta por servicio, calcula total y habilita PDF tras confirmar.

## Limitaciones conocidas / verificación
- PLN por reglas y similitud aproximada, no modelo estadístico entrenado; puede fallar con expresiones poco comunes.
- Menú y condiciones comerciales ficticias; los avisos de alergias no garantizan seguridad.
- No hay integración real con tienda, pagos, inventario, mapas, ni persistencia de pedidos.
- El panel didáctico presenta interpretación de reglas y estado; no es una explicación de un modelo neuronal.
- Confirmar que Community Cloud despliega correctamente tras publicar es una verificación pendiente fuera de este entorno.
