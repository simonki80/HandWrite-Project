import os
import base64
import numpy as np
from PIL import Image as PILImage  # Para evitar conflicto con Flask
from flask import Flask, request, send_file, jsonify
import matplotlib.pyplot as plt
import cv2
import tflite_runtime.interpreter as tflite
from io import BytesIO
from strtraductor import Organizarcadena,modificar_indices,raices,depurar_parentesis,exponentes,depurar_trigonometria
from skimage.morphology import skeletonize

plt.rcParams['text.usetex'] = False

app = Flask(__name__)

@app.route("/render", methods=["POST"])
def render_latex():
    data = request.json
    latex_eq = data.get("latex_eq", "")
    solo_preview = data.get("solo_preview", False)

    if solo_preview:
        full_expression = latex_eq  # Sin adornar
    else:
        # ... lo que ya hacías con diferenciales, límites, etc.
        diferenciales = data.get("diferenciales", [])
        limitsdx = data.get("limitsdx", [None, None])
        limitsdy = data.get("limitsdy", [None, None])
        limitsdz = data.get("limitsdz", [None, None])
        ordendepresion = data.get("ordendepresion", [])

        full_expression = ""
        if diferenciales:
            for diff in reversed(diferenciales):
                if diff == 'dx':
                    lower, upper = limitsdx
                elif diff == 'dy':
                    lower, upper = limitsdy
                elif diff == 'dz':
                    lower, upper = limitsdz
                else:
                    lower, upper = None, None

                if lower is not None and upper is not None:
                    full_expression = f"\\int_{{{lower}}}^{{{upper}}} " + full_expression
                else:
                    full_expression = "\\int " + full_expression

            full_expression += f"\\left({latex_eq}\\right)"
            for diff in diferenciales:
                full_expression += f"\\,{diff}"
        elif ordendepresion:
            for deriv in ordendepresion:
                full_expression += f"\\frac{{\\partial}}{{\\partial {deriv[1:]}}}"
            if not diferenciales:
                full_expression += f"\\left({latex_eq}\\right)"
        else:
            full_expression = latex_eq

    # Generación de la imagen
    fig, ax = plt.subplots(figsize=(6, 2), facecolor='none')  # Fondo transparente
    ax.text(0.5, 0.5, f"${full_expression}$", fontsize=20, ha='center', va='center', color='black')
    ax.axis("off")

    buffer = BytesIO()
    plt.savefig(
        buffer,
        format="png",
        bbox_inches="tight",
        pad_inches=0.1,
        dpi=250,
        transparent=True  # 👈 Esta línea hace que el fondo sea transparente
    )
    
    # Convertir imagen a base64
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Devolver JSON con ambos datos
    return jsonify({
        "image": f"data:image/png;base64,{img_base64}",
        "latex_expression": full_expression
    })

import os  # 👈 Asegúrate de tener esto arriba si no lo tienes

def DeteccionRaiz(x, y, w, h, centros, indice_actual):
    centrosdentro = []
    raiz = False
    for i, centro in enumerate(centros): 
        if i == indice_actual:
            continue  # Excluirse a sí mismo
        x1, y1 = centro
        if (x < x1 < x + w) and (y < y1 < y + h): 
            centrosdentro.append(centro)
            raiz = True
    return raiz, centrosdentro


def tomartrazosygenerarcontornos(img):
    # Verificar si ya está en escala de grises
    if len(img.shape) == 3 and img.shape[2] == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()  # Ya está en escala de grises

    # Binarizar (invertido: negro = 255, fondo blanco = 0)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # Encontrar contornos externos
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    imagenes = []
    posiciones = []

    for i, cnt in enumerate(contours):
        mask = np.zeros_like(thresh)
        cv2.drawContours(mask, [cnt], -1, 255, -1)  # Rellenar el contorno
        trazo_mascara = cv2.bitwise_and(thresh, thresh, mask=mask)
        trazo_final = cv2.bitwise_not(trazo_mascara)  # Volver blanco el fondo
        x, y, w, h = cv2.boundingRect(cnt)
        recorte = trazo_final[y:y+h, x:x+w]
        imagenes.append(recorte)
        posiciones.append((x, y, w, h))  # Guardamos la posición también

    return imagenes, posiciones

def CrearContornos(imagen):
    imagenes_procesadas, posiciones_procesadas = tomartrazosygenerarcontornos(imagen)

    # También obtenemos los contornos directamente de la imagen binarizada
    _, umbralizada = cv2.threshold(imagen, 200, 255, cv2.THRESH_BINARY_INV)
    contornos_originales, _ = cv2.findContours(umbralizada, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return imagenes_procesadas, posiciones_procesadas, contornos_originales, imagen

def PonerFondoBlanco(digito, w, h): 
    mayorlado = max(w, h)
    imagen_fondo = PILImage.new('L', (mayorlado, mayorlado), 'white')
    imagen_encima = PILImage.fromarray(digito)
    posicion_x = (imagen_fondo.width - imagen_encima.width) // 2
    posicion_y = (imagen_fondo.height - imagen_encima.height) // 2
    imagen_fondo.paste(imagen_encima, (posicion_x, posicion_y))
    return imagen_fondo

def RedimensionarYEngrosar(digito, tamaño=45):
    # 1. Redimensionar a 45x45
    imagen_pil = PILImage.fromarray(digito)
    imagen_redimensionada = imagen_pil.resize((tamaño, tamaño), resample=PILImage.LANCZOS)
    imagen_np = np.array(imagen_redimensionada)

    # 2. Umbralizar: fondo blanco (255), trazo negro (0)
    _, binaria = cv2.threshold(imagen_np, 200, 255, cv2.THRESH_BINARY)

    # 3. Invertir: trazo blanco (255), fondo negro (0) → necesario para skeletonize
    invertida = cv2.bitwise_not(binaria)

    # 4. Convertir a booleana para skeletonize
    binaria_bool = invertida > 0  # True donde hay trazo (blanco), False donde fondo (negro)

    # 5. Esqueletizar (Zhang-Suen)
    skel = skeletonize(binaria_bool)

    # 6. Convertir esqueleto a imagen uint8 con trazo blanco (255)
    esqueleto_img = (skel * 255).astype(np.uint8)

    # 7. Engrosar el trazo blanco con el kernel indicado
    grosor = 1
    if grosor > 1:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (grosor, grosor))
        engrosado = cv2.dilate(esqueleto_img, kernel)
    else:
        engrosado = esqueleto_img.copy()

    _, engrosado = cv2.threshold(engrosado, 127, 255, cv2.THRESH_BINARY)

    # 10. Invertir
    resultado = cv2.bitwise_not(engrosado)

    return resultado

def ProcesarContornos(contornos_originales, imagen, imagenes_procesadas,posiciones_procesadas):
    digitos_originales = []
    posiciones_originales=[]
    centros_originales = []
    lista_digitos_procesados = []

    for i, contorno in enumerate(contornos_originales):
        x, y, w, h = cv2.boundingRect(contorno)

        # Aquí usas el trazo bien extraído, con huecos preservados
        recorte = imagen[y:y+h, x:x+w]  # Extrae el bounding box directamente
        posiciones_originales.append((x,y,w,h))
        digitos_originales.append(recorte)
        digitobueno = imagenes_procesadas[i]

        centro_x = x + w // 2
        centro_y = y + h // 2

        imagen_fondo = PonerFondoBlanco(digitobueno, posiciones_procesadas[i][2],posiciones_procesadas[i][3])
        imagen_np = np.array(imagen_fondo)

        digito_redimensionado = RedimensionarYEngrosar(imagen_np, tamaño=45)

        centro = [centro_x, centro_y]
        centros_originales.append(centro)
        lista_digitos_procesados.append((digito_redimensionado, (x, y, w, h)))

    indices_raices = []
    for i, contorno in enumerate(contornos_originales): 
        x, y, w, h = cv2.boundingRect(contorno)
        raiz, dentro = DeteccionRaiz(x, y, w, h, centros_originales, i)
        if raiz: 
            centros_originales[i] = (x, y + h // 2)
            indices_raices.append(i)
            print(f"Contorno {i} identificado como raíz: (x={x}, y={y}, w={w}, h={h})")
            print(f"   Contiene centros: {dentro}")

    return digitos_originales,posiciones_originales, centros_originales, lista_digitos_procesados

def ordenar_ecuacion(digitos_originales, centros, lista_digitos):
    matrix = [(digitos_originales[i], centros[i], lista_digitos[i]) for i in range(len(centros))]
    sorted_matrix = sorted(matrix, key=lambda x: x[1][0])
    imagenes_sort = [sorted_matrix[i][0] for i in range(len(sorted_matrix))]
    centros_sorted = [sorted_matrix[i][1] for i in range(len(sorted_matrix))]
    lista_digitos_sorted = [sorted_matrix[i][2] for i in range(len(sorted_matrix))]
    return imagenes_sort, centros_sorted, lista_digitos_sorted

def DeteccionDivResta(x, y, w, h, centros, i):
    resta = False
    fraccion = False

    ancho = x + w  # Coordenada derecha del símbolo
    arriba = False
    abajo = False

    print(f"\nProcesando símbolo {i}: x={x}, y={y}, w={w}, h={h}")

    if w > 8 * h:
        print(f"  -> Posible fracción/resta (w > 8h)")

        for j, (x1, y1) in enumerate(centros):            
            # Verificar si el centro está dentro del ancho del símbolo
            if x < x1 < ancho:
                print(f"  -> Centro {j} dentro del ancho: x1={x1}, y1={y1}")

                if y1 < y:  
                    arriba = True
                    print(f"    -> Centro {j} está arriba del símbolo")
                elif y1 > y:
                    abajo = True
                    print(f"    -> Centro {j} está abajo del símbolo")

        if arriba and abajo:
            print(f"  -> Es una fracción (tiene números arriba y abajo)")
            return True, False
        else: 
            print(f"  -> Es una resta (no tiene números arriba y abajo)")
            return False, True
    else: 
        print(f"  -> No es ni fracción ni resta (w <= 8h)")
        return False, False

def DeteccionPunto(digito):
    umbral = 0.2
    black_pixels = np.sum(digito < 0.5)
    total_pixels = digito.size
    black_ratio = black_pixels / total_pixels
    if black_ratio > umbral: 
        return True
    else: 
        return False

def DeteccionComa(h,w): 
    if h<20 and w<20: 
        return True
    else: 
        return False

def ConseguirAnchuras(sort_list):
    alturas = []
    anchos = []

    for _, (x, y, w, h) in sort_list:
        alturas.append(h)
        anchos.append(w)

    if not alturas:
        return 0, 0  # Prevent division by zero if no heights are added.

    promedioAltura = sum(alturas) / len(alturas)
    promedioAncho = sum(anchos) / len(anchos)
    
    return promedioAltura, promedioAncho

def detectarsimbolosespeciales(imagenes_sort,posiciones_originales,centros_sorted):
    print("\n=== Iniciando detección de símbolos especiales ===")

    diviciones = []
    puntos = []
    restas = []
    raizes = []
    comas = []
    
    diccionarioraizes = []
    
    for i, (digito_redimensionado,(x,y,w,h)) in enumerate(imagenes_sort):
        #x,y,w,h = posiciones_originales[i]
        print(f"\nProcesando símbolo {i}: x={x}, y={y}, w={w}, h={h}")
        
        # Detección de raíz
        raiz, centrosdentro = DeteccionRaiz(x, y, w, h, centros_sorted,i)
        if raiz:
            print(f"  -> Es una raíz")
            if i not in raizes: 
                raizes.append(i)
                centros_raiz = {i: centrosdentro}
                diccionarioraizes.append(centros_raiz)
        
        # Detección de división y resta
        fraccion, resta = DeteccionDivResta(x, y, w, h, centros=centros_sorted, i=i) 
        if fraccion:
            print(f"  -> Es una división")
            diviciones.append(i)
        if resta:
            print(f"  -> Es una resta")
            restas.append(i)

        # Detección de puntos
        if DeteccionPunto(digito_redimensionado):
            print(f"  -> Es un punto")
            puntos.append(i)

        # Detección de comas
        if DeteccionComa(h, w):
            print(f"  -> Es una coma")
            comas.append(i)

    print("\n=== Detección completada ===\n")
    return diviciones, puntos, raizes, restas, comas, diccionarioraizes

def optimized_img_to_array(img):
    """
    Versión optimizada de img_to_array que funciona igual en Android y PC
    Convierte PIL.Image directamente a array numpy normalizado
    """
    # Convertir a RGB si no lo está (compatible con modelos entrenados en RGB)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Conversión directa a array numpy + normalización
    return np.array(img, dtype=np.float32) / 255.0

def cargar_modelo():
    """
    Cargar el modelo TensorFlow Lite (.tflite) y lanzar un error claro si no se encuentra o no se puede cargar.
    """

    script_directory = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join("assets/models/MathSymbols_Optimized1.tflite")

    # Verificar si el archivo existe
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"❌ Modelo no encontrado en: {model_path}\n¿Está subido correctamente al repo?")

    try:
        # Intentar cargar el modelo
        interpreter = tflite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
        return interpreter
    except Exception as e:
        raise RuntimeError(f"❌ Error al cargar el modelo TFLite: {str(e)}")

def Ai(Class_Indices_inverse, img_array, interpreter):
    """
    Realiza la predicción usando el modelo TensorFlow Lite.
    """
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Preprocesar la entrada
    img_array = np.expand_dims(img_array, axis=-1)  # Asegurar que la imagen tiene la forma correcta
    img_array = np.expand_dims(img_array, axis=0)  # Añadir dimensión batch

    # Poner la imagen como entrada del modelo
    interpreter.set_tensor(input_details[0]['index'], img_array)
    interpreter.invoke()

    # Obtener las predicciones
    output_data = interpreter.get_tensor(output_details[0]['index'])
    predicted_class = np.argmax(output_data)

    return Class_Indices_inverse[predicted_class]

def ProduccionPredicciones(image):
    """
    Predice las clases de los símbolos matemáticos en la imagen.
    """
    # Cargar el modelo TensorFlow Lite
    interpreter = cargar_modelo()
    
    # Diccionario de clases
    Class_Indices = {'(': 0, ')': 1, '+': 2, '0': 3, '1': 4, '2': 5, '3': 6, '4': 7, '5': 8, '6': 9, '7': 10, '8': 11, '9': 12, 
                     'a': 13, 'c': 14, 'n': 15, 's': 16, 't': 17, 'd': 18, 'e': 19, 'pi': 20, 'x': 21, 'y': 22, 'z': 23}
    
    # Inverso del diccionario para decodificar las predicciones
    Class_Indices_inverse = {v: k for k, v in Class_Indices.items()}
    
    # Lista de caracteres reconocidos
    cadena = []
    
    # Crear contornos e imagen
    try:
        imagenes_procesadas, posiciones_procesadas, contornos_originales, imagen = CrearContornos(image)
    except Exception as e:
        raise RuntimeError(f"❌ Error en CrearContornos: {e}")

    try:
        digitos_originales,posiciones_originales, centros_originales, lista_digitos_procesados = ProcesarContornos(contornos_originales, imagen, imagenes_procesadas,posiciones_procesadas)
    except Exception as e:
        raise RuntimeError(f"❌ Error en ProcesarContornos: {e}")

    try:
        imagenes_sort, centros_sorted, lista_digitos_sorted = ordenar_ecuacion(digitos_originales, centros_originales, lista_digitos_procesados)
    except Exception as e:
        raise RuntimeError(f"❌ Error en ordenar_ecuacion: {e}")
    # Detectar símbolos especiales
    diviciones, puntos, raizes, restas, comas, raizes_centros = detectarsimbolosespeciales(lista_digitos_sorted,posiciones_originales,centros_sorted)

    # Recorrer los dígitos ordenados para predecir su clase
    for i, (digito_redimensionado, _) in enumerate(lista_digitos_sorted):
        
        if i in diviciones:
            cadena.append("div")
        elif i in restas:
            cadena.append("-")
        elif i in raizes:
            cadena.append("q")
        elif i in puntos: 
            cadena.append("*")
        elif i in comas: 
            cadena.append(".")
        else:
            # Preprocesar imagen y predecir con el modelo
            img_array = np.array(digito_redimensionado, dtype=np.float32) / 255.0
            prediccion = Ai(Class_Indices_inverse, img_array, interpreter)
            cadena.append(prediccion)

    return cadena, lista_digitos_sorted, centros_sorted, raizes_centros

from flask import jsonify
import base64
import numpy as np

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        img_b64 = data.get("image_base64", None)
        if not img_b64:
            return jsonify({"error": "No image provided"}), 400

        img_bytes = base64.b64decode(img_b64)
        img = PILImage.open(BytesIO(img_bytes)).convert("L")
        img_np = np.array(img)

        cadena, sort_list, centros, raices_centros = ProduccionPredicciones(img_np)

        # Todo el postprocesamiento
        cadena_organizada, indices = Organizarcadena(cadena, sort_list, centros)
        cadenafinaltrigonometrica = depurar_trigonometria(cadena_organizada)
        indicesparaexponentes = modificar_indices(cadenafinaltrigonometrica, indices)
        cadenarepuesto, indicesrepuesto = raices(cadenafinaltrigonometrica, indicesparaexponentes, sort_list, centros)
        cadenarepuesto = depurar_parentesis(cadenarepuesto, indicesrepuesto)
        cadenarepuesto, indicesrepuesto = exponentes(cadenarepuesto, indicesrepuesto, sort_list, centros)

        # Reemplazos finales
        cadenarepuesto = cadenarepuesto.replace("¿", "(")
        cadenarepuesto = cadenarepuesto.replace("?", ")")
        cadenarepuesto = cadenarepuesto.replace("p", "π")
        cadenarepuesto = cadenarepuesto.replace("r", "root")
        cadenarepuesto = cadenarepuesto.replace("q", "sqrt")
        cadenarepuesto = cadenarepuesto.replace("d", "/")

        return jsonify({"final_expression": cadenarepuesto})

    except Exception as e:
        import traceback
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route("/plot-function", methods=["POST"])
def plot_function():
    try:
        from sympy import symbols, sympify, lambdify
        from mpl_toolkits.mplot3d import Axes3D  # Necesario para 3D plots
        import numpy as np

        data = request.json
        expr_str = data.get("function", "")

        x, y, z = symbols("x y z")
        f = sympify(expr_str)
        vars_used = list(f.free_symbols & {x, y, z})

        fig = plt.figure()
        fig.patch.set_alpha(0.0)

        if len(vars_used) == 1:
            var = vars_used[0]
            f_lambda = lambdify(var, f, 'numpy')
            x_vals = np.linspace(-10, 10, 400)
            y_vals = f_lambda(x_vals)

            plt.plot(x_vals, y_vals)
            plt.grid(True)

        elif len(vars_used) == 2:
            var1, var2 = vars_used
            f_lambda = lambdify((var1, var2), f, 'numpy')
            v1_vals = np.linspace(-10, 10, 100)
            v2_vals = np.linspace(-10, 10, 100)
            V1, V2 = np.meshgrid(v1_vals, v2_vals)
            F_vals = f_lambda(V1, V2)

            ax = fig.add_subplot(111, projection='3d')
            ax.plot_surface(V1, V2, F_vals, cmap='Blues')

        else:
            return jsonify({"error": "Se admiten solo funciones con 1 o 2 variables"}), 400

        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=200, bbox_inches='tight', transparent=True)
        plt.close(fig)
        buf.seek(0)

        return send_file(buf, mimetype="image/png")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/plot-latex", methods=["POST"])
def plot_latex():
    try:
        data = request.json
        latex_str = data.get("latex_str", "")

        fig = plt.figure(figsize=(8, 2), facecolor='none')
        plt.axis('off')
        plt.text(0.5, 0.5, f"${latex_str}$", fontsize=30, ha='center', va='center', color='black')
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', transparent=True)
        plt.close(fig)
        buf.seek(0)

        return send_file(buf, mimetype="image/png")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ping")
def ping():
    return "pong", 200

# Bloque principal al final
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
