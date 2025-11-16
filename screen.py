from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.properties import ListProperty, StringProperty, BooleanProperty
from kivy.core.window import Window
from kivy.metrics import dp
import requests
import base64
from io import BytesIO
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
# KivyMD components
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout

# Para el cursor personalizado (opcional)
from kivy.core.window import Window
from Screens.ScreensUtils import LandscapeScreen
from Utils.UltilsElements import calcular_ancho_proporcional,capturar_widget,get_captura_scale

##3
from PIL import Image as PILImage
from io import BytesIO


def calcular_tamano_celda_adaptativo():
    ancho, alto = Window.size
    diagonal = (ancho**2 + alto**2) ** 0.5

    if diagonal >= 2000:
        return dp(100)  # Tablets grandes
    elif diagonal >= 1400:
        return dp(80)   # Tablets medianas
    else:
        return dp(60)   # Celulares
    
class GridWidget(Widget):
    def __init__(self, **kwargs):
        super(GridWidget, self).__init__(**kwargs)
        self.cell_size = calcular_tamano_celda_adaptativo() * 0.8
        self.bind(size=self._draw_grid)
        
    def _draw_grid(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.85, 0.85, 0.85, 0.4)  # Gris más oscuro y visible
            # Líneas horizontales
            for y in range(0, int(self.height), int(self.cell_size)):
                Line(points=[0, y, self.width, y], width=dp(1.2))
            # Líneas verticales
            for x in range(0, int(self.width), int(self.cell_size)):
                Line(points=[x, 0, x, self.height], width=dp(1.2))

class Draw(Widget):
    def __init__(self, **kwargs):
        super(Draw, self).__init__(**kwargs)
        self.eraser_active = False
        self.user_lines = []
        self.bind(size=self.update_canvas)
        Window.set_system_cursor('pen')

        # Fondo blanco con canvas.before
        with self.canvas.before:
            Color(1, 1, 1, 1)  # Color blanco
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        
        self.bind(size=self.update_bg, pos=self.update_bg)

    def update_bg(self, *args):
        """Asegura que el fondo blanco se ajuste si la ventana cambia de tamaño."""
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def update_canvas(self, *args):
        """Redibuja solo las líneas sin afectar el fondo."""
        self.canvas.after.clear()  # Borra solo las líneas (no el fondo)
        with self.canvas.after:
            for line in self.user_lines:
                Color(0, 0, 0, 1)  # Color negro
                self.canvas.add(line)

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):  # Verifica si el toque está dentro del widget
            return False  # Ignora el toque si está fuera

        if self.eraser_active:
            self.erase(touch)
        else:
            with self.canvas.after:
                Color(0, 0, 0, 1)
                grosor = calcular_ancho_proporcional(pen=True, eraser=False)
                touch.ud["line"] = Line(points=(touch.x, touch.y), width=grosor, cap='round', joint='round')
                self.user_lines.append(touch.ud["line"])
        return True  # Indica que el evento fue manejado

    def on_touch_move(self, touch):
        if not self.collide_point(touch.x, touch.y):  # Verifica si el toque está dentro del widget
            return False  # Ignora el toque si está fuera

        if self.eraser_active:
            self.erase(touch)
        else:
            touch.ud["line"].points += (touch.x, touch.y)

        return True  # Indica que el evento fue manejado

    def erase(self, touch):
        """Borra dibujando con color blanco sobre la línea."""
        eraser_size = calcular_ancho_proporcional(pen=False, eraser=True)
        with self.canvas.after:
            Color(1, 1, 1, 1)  # Mismo color del fondo
            Ellipse(pos=(touch.x - eraser_size / 2, touch.y - eraser_size / 2),
                    size=(eraser_size, eraser_size))
        
class SimpleDrawApp(LandscapeScreen):
    ordendepresion = ListProperty([])
    diferenciales = ListProperty([])
    cantidaddeintegrales = StringProperty("")
    has_shown_popup = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(SimpleDrawApp, self).__init__(**kwargs)

        with self.canvas.before:
            self.bg_color = Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)

        Window.clearcolor = (1, 1, 1, 1)
        layout = FloatLayout()

        # Widget de dibujo
        self.draw_widget = Draw(size=(Window.width, Window.height), size_hint=(1, 1))
        layout.add_widget(self.draw_widget)

        # Cuadrícula de fondo
        self.grid_widget = GridWidget(size_hint=(1, 1))
        layout.add_widget(self.grid_widget)

        blanco = (1, 1, 1, 1)
        azul = (0, 0.5, 1, 1)

        # 🔹 Botón de CALCULAR
        buttonCalculate = MDRectangleFlatButton(
            text="CALCULATE",
            font_size="18sp",
            theme_text_color="Custom",
            text_color=blanco,
            line_color=azul,
            md_bg_color=azul,
            size_hint=(None, None),
            size=(dp(140), dp(50)),
        )

        # 🔹 Botón de LIMPIAR
        buttonClear = MDRectangleFlatButton(
            text="CLEAR",
            font_size="18sp",
            theme_text_color="Custom",
            text_color=blanco,
            line_color=azul,
            md_bg_color=azul,
            size_hint=(None, None),
            size=(dp(120), dp(50)),
        )

        # 🖊️ Botón de borrador (superior derecha)
        buttonEraser = MDIconButton(
            icon='pen' if self.draw_widget.eraser_active else 'eraser',
            pos_hint={'right': 1, 'top': 1},
            size_hint=(None, None),
            size=(dp(48), dp(48)),
        )
        layout.add_widget(buttonEraser)

        info_button = MDIconButton(
            icon="information-outline",
            pos_hint={'x': 0.0, 'top': 1},
            size_hint=(None, None),
            size=(dp(100), dp(100)),
            theme_icon_color="Custom",
            icon_color=(0, 0.5, 1, 1),
            md_bg_color=(0, 0, 0, 0)
        )
        info_button.bind(on_release=self.popinfo)
        layout.add_widget(info_button)

        # Label al lado del botón de información
        info_label = Label(
            text="Only write the function/operation (not ∫ or d/dx)",
            size_hint=(None, None),
            size=(dp(300), dp(30)),
            pos_hint={'x': 0.05, 'top': 0.97},  # Ajusta la posición horizontal y vertical
            font_size="14sp",
            color=(0, 0.5, 1, 1),  # Gris oscuro
            halign="left",
            valign="middle",
            markup=True
        )
        layout.add_widget(info_label)

        # 🔳 Contenedor horizontal inferior
        botones_box = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(70),
            padding=[dp(16), dp(10)],
            spacing=dp(10),
            pos_hint={'x': 0, 'y': 0},
        )

        # Espaciador izquierdo
        botones_box.add_widget(buttonClear)
        botones_box.add_widget(Widget())  # espacio flexible
        botones_box.add_widget(buttonCalculate)

        layout.add_widget(botones_box)

        # Eventos
        buttonClear.bind(on_release=self.clear_canvas)
        buttonCalculate.bind(on_release=self.continue_button)
        buttonEraser.bind(on_release=self.toggle_eraser)

        self.add_widget(layout)

    def popinfo(self, instance):
        self.show_welcome_popup()

    def on_enter(self):  
        super().on_enter()    
        App.get_running_app().show_interstitial()
    
    def show_welcome_popup(self):
        self.dialog = MDDialog(
            title="[b][color=#0066CC]Help Us Understand You Better[/color][/b]",
            text=(
                "[b][color=#FF0000] Do not write integral symbols (∫) or differentials (d/dx)[/color][/b]\n"
                "Just write the function you want to process, e.g., x^2 + 3x or sin(x)/x.\n\n"
                "To improve recognition accuracy:\n"
                "• Use √ for roots or a^(2/5) format\n"
                "• Fraction bars must fully cover both numerator and denominator\n"
                "• Try writing each digit in a single stroke, without separations\n"
                "• Keep digits spaced and aligned with the grid\n"
                "• Dots or extra marks will be detected and may affect results\n"
                "• For better performance, write the letter 'i' without the dot"
            ),
            size_hint=(0.65, None),  # Adaptive width
            buttons=[
                MDRaisedButton(
                    text="CONTINUE",
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1),
                    md_bg_color=(0, 0.5, 1, 1),
                    on_release=lambda x: self.dialog.dismiss() 
                ),
            ],
        )
        self.dialog.open()

    def clear_canvas(self, instance):
        """Limpia el canvas y reinicia la lista de líneas."""
        self.draw_widget.canvas.before.clear()  # Limpiar el fondo
        self.draw_widget.canvas.after.clear()   # Limpiar las líneas
        self.draw_widget.user_lines = []        # Reiniciar la lista de líneas

        # Volver a dibujar el fondo blanco
        with self.draw_widget.canvas.before:
            Color(1, 1, 1, 1)  # Color blanco
            self.draw_widget.bg_rect = Rectangle(size=self.draw_widget.size, pos=self.draw_widget.pos)

    def continue_button(self, button):
        # Captura antes de resetear
        scale = get_captura_scale()
        image = capturar_widget(self.draw_widget, scale=scale)

        respuesta = self.enviar_imagen_al_backend(image)
        
        if respuesta:
            app = App.get_running_app()
            app.equation = respuesta.get("final_expression", "")
            
            self.manager.current = 'calculator_screen'
        else:
            print("Error en la predicción")
        
    def toggle_eraser(self, instance):
        self.draw_widget.eraser_active = not self.draw_widget.eraser_active
        if self.draw_widget.eraser_active:
            Window.set_system_cursor('crosshair')
            instance.icon = 'pen'  # Mostrar lápiz cuando el borrador está activo
        else:
            Window.set_system_cursor('arrow')
            instance.icon = 'eraser'  # Mostrar borrador cuando el lápiz está activo

    def reset_screen(self):
        self.draw_widget.canvas.after.clear()
        self.draw_widget.user_lines = []

        with self.draw_widget.canvas.before:
            Color(1, 1, 1, 1)
            self.draw_widget.bg_rect = Rectangle(size=self.draw_widget.size, pos=self.draw_widget.pos)

        self.draw_widget.update_canvas()
        self.draw_widget.update_bg()
        self.draw_widget.canvas.ask_update()

        self.has_shown_popup = False  # Si quieres volver a mostrar el popup

    def enviar_imagen_al_backend(self, image):
        try:
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            buffer.seek(0)
            img_b64 = base64.b64encode(buffer.read()).decode("utf-8")

            url = 'https://backend-6eik.onrender.com/predict'
            response = requests.post(url, json={"image_base64": img_b64})

            if response.status_code == 200:
                return response.json()
            else:
                print("❌ Error del servidor:", response.status_code)
                print("🧾 Respuesta:", response.text)
                return None
        except Exception as e:
            print("❌ Excepción al conectar con el servidor:", str(e))
            return None