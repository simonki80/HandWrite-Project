import os
import base64
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image as PILImage  # Para evitar conflicto con Flask
from flask import Flask, Response, jsonify, request, send_file
from flask_cors import CORS

from digit_pipeline import ProduccionPredicciones
from strtraductor import (
    Organizarcadena,
    depurar_parentesis,
    depurar_trigonometria,
    exponentes,
    modificar_indices,
    raices,
)


app = Flask(__name__)
CORS(app)  # 🔹 Permite solicitudes desde cualquier origen

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

import requests

API_KEY = "sk-beec782b063a4a3790bd97d86c7adb50"
API_URL = "https://api.deepseek.com/v1/chat/completions"


@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        # Respuesta simple para preflight requests
        response = jsonify()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response, 200
    
    try:
        body = request.get_json(silent=True) or {}
        attachments = body.pop("attachments", []) or []
        stream = body.get("stream", False)

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        if attachments:
            messages = body.get("messages", [])
            if messages:
                user_message = messages[-1]
                current_content = user_message.get("content", "")

                if isinstance(current_content, list):
                    content_items = current_content
                else:
                    content_items = [{"type": "text", "text": current_content or ""}]

                for attachment in attachments:
                    mime_type = attachment.get("type", "")
                    data_url = attachment.get("dataUrl")
                    name = attachment.get("name", "archivo")
                    text_content = attachment.get("textContent")

                    if mime_type.startswith("image/") and data_url:
                        url = data_url if data_url.startswith("data:") else f"data:{mime_type};base64,{data_url}"
                        content_items.append({
                            "type": "image_url",
                            "image_url": {"url": url}
                        })
                    elif mime_type == "application/pdf":
                        if text_content:
                            content_items.append({
                                "type": "text",
                                "text": f'Contenido del PDF "{name}":\n{text_content}'
                            })
                        else:
                            content_items.append({
                                "type": "text",
                                "text": f'Se adjuntó el PDF "{name}", pero no se pudo extraer su contenido.'
                            })
                    elif text_content:
                        content_items.append({
                            "type": "text",
                            "text": f'Contenido extraído de "{name}":\n{text_content}'
                        })

                user_message["content"] = content_items

        # 🔹 Streaming
        if stream:
            def generate():
                with requests.post(API_URL, headers=headers, json=body, stream=True) as r:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            yield chunk
            
            # Para streaming, crear una Response manualmente con headers CORS
            response = Response(generate(), content_type="text/event-stream")
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response

        # 🔹 Normal (sin streaming)
        resp = requests.post(API_URL, headers=headers, json=body)
        response = jsonify(resp.json())
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    except Exception as e:
        response = jsonify({"error": str(e)})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500
# Bloque principal al final
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
