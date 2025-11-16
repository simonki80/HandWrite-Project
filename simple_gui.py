import tkinter as tk
from tkinter import ttk, messagebox

from PIL import Image, ImageDraw

from recognizer import reconocer_expresion


CANVAS_WIDTH = 640
CANVAS_HEIGHT = 360


class DrawingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Local Math Recognizer")

        self.pen_width = tk.IntVar(value=6)
        self.result_var = tk.StringVar(value="Resultado: (sin calcular)")

        self._build_widgets()
        self._init_drawing_surface()

    def _build_widgets(self):
        self.canvas = tk.Canvas(
            self,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg="white",
            highlightthickness=1,
            highlightbackground="#cccccc",
        )
        self.canvas.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
        self.canvas.bind("<ButtonPress-1>", self._start_draw)
        self.canvas.bind("<B1-Motion>", self._draw_motion)
        self.canvas.bind("<ButtonRelease-1>", self._end_draw)

        ttk.Label(self, text="Grosor del trazo").grid(row=1, column=0, sticky="w", padx=10)
        self.size_label = ttk.Label(self, text=f"{self.pen_width.get()} px")
        self.size_label.grid(row=1, column=1, sticky="w")

        self.size_slider = ttk.Scale(
            self,
            from_=1,
            to=30,
            orient="horizontal",
            command=self._update_pen_label,
            variable=self.pen_width,
        )
        self.size_slider.grid(row=1, column=2, sticky="we", padx=10)

        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)

        calc_button = ttk.Button(button_frame, text="Calcular", command=self._calculate)
        calc_button.grid(row=0, column=0, padx=5)

        clear_button = ttk.Button(button_frame, text="Limpiar", command=self._clear_canvas)
        clear_button.grid(row=0, column=1, padx=5)

        self.result_label = ttk.Label(
            self,
            textvariable=self.result_var,
            wraplength=CANVAS_WIDTH,
            anchor="center",
            justify="center",
        )
        self.result_label.grid(row=3, column=0, columnspan=3, padx=10, pady=(0, 10))

        self.columnconfigure(2, weight=1)

    def _init_drawing_surface(self):
        self.image = Image.new("L", (CANVAS_WIDTH, CANVAS_HEIGHT), color=255)
        self.image_draw = ImageDraw.Draw(self.image)
        self.last_point = None

    def _update_pen_label(self, _event=None):
        self.size_label.config(text=f"{int(self.pen_width.get())} px")

    def _start_draw(self, event):
        self.last_point = (event.x, event.y)

    def _draw_motion(self, event):
        if self.last_point is None:
            self.last_point = (event.x, event.y)
            return

        x1, y1 = self.last_point
        x2, y2 = event.x, event.y
        width = int(self.pen_width.get())

        self.canvas.create_line(x1, y1, x2, y2, fill="black", width=width, capstyle="round")
        self.image_draw.line([x1, y1, x2, y2], fill=0, width=width)
        self.last_point = (x2, y2)

    def _end_draw(self, _event):
        self.last_point = None

    def _clear_canvas(self):
        self.canvas.delete("all")
        self._init_drawing_surface()
        self.result_var.set("Resultado: (sin calcular)")

    def _calculate(self):
        expresion = reconocer_expresion(self.image.copy())
        if expresion:
            self.result_var.set(f"Resultado: {expresion}")
        else:
            self.result_var.set("Resultado: no se pudo interpretar.")
            messagebox.showwarning(
                "Sin resultado", "No se pudo reconocer la expresión. Intenta escribirla de nuevo."
            )


if __name__ == "__main__":
    app = DrawingApp()
    app.mainloop()
