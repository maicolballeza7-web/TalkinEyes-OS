import colorsys
import tkinter as tk


class Menu:
    """Representa un menú escaneable de opciones."""

    def __init__(
        self,
        ventana: tk.Tk,
        titulo: str,
        opciones: list[str],
        colores: list[str],
        on_select,
        layout: str = "lista",
        subtitulo: str = "",
    ) -> None:
        # Guardamos los datos que necesita el menú.
        self.ventana = ventana
        self.titulo = titulo
        self.opciones = opciones
        self.colores = colores
        self.on_select = on_select
        self.layout = layout
        self.subtitulo = subtitulo

        # Inicializamos el estado del escaneo.
        self.indice_actual: int = 0
        self.timer_id = None
        self.rectangulos: list[int] = []
        self.halo_actual: int | None = None
        self.coordenadas: list[tuple[int, int, int, int]] = []

        # El frame se crea oculto hasta que se llame a iniciar().
        self.frame = tk.Frame(
            ventana,
            width=740,
            height=600,
            bg="#F0F4F8",
        )
        self.canvas = None

        self.dibujar()

    def _color_mas_intenso(self, color: str) -> str:
        """Aumenta el brillo y la saturación de un color hexadecimal."""
        color_limpio = color.lstrip("#")
        rojo = int(color_limpio[0:2], 16) / 255.0
        verde = int(color_limpio[2:4], 16) / 255.0
        azul = int(color_limpio[4:6], 16) / 255.0

        h, l, s = colorsys.rgb_to_hls(rojo, verde, azul)
        s = min(1.0, s * 1.3 + 0.15)
        l = min(0.72, l * 1.15 + 0.12)
        rojo, verde, azul = colorsys.hls_to_rgb(h, l, s)

        return "#{:02X}{:02X}{:02X}".format(
            round(rojo * 255),
            round(verde * 255),
            round(azul * 255),
        )

    def _rectangulo_redondeado(
        self,
        izquierda: float,
        arriba: float,
        derecha: float,
        abajo: float,
        radio: float = 18,
        **opciones,
    ) -> int:
        """Dibuja una tarjeta redondeada con un polígono suavizado."""
        puntos = [
            izquierda + radio,
            arriba,
            derecha - radio,
            arriba,
            derecha,
            arriba + radio,
            derecha,
            abajo - radio,
            derecha - radio,
            abajo,
            izquierda + radio,
            abajo,
            izquierda,
            abajo - radio,
            izquierda,
            arriba + radio,
        ]
        return self.canvas.create_polygon(
            puntos,
            smooth=True,
            splinesteps=36,
            **opciones,
        )

    def dibujar(self) -> None:
        """Dibuja el título, las opciones y sus tarjetas."""
        if self.canvas is not None:
            self.canvas.destroy()

        self.rectangulos = []
        self.coordenadas = []
        self.halo_actual = None
        self.canvas = tk.Canvas(
            self.frame,
            width=740,
            height=600,
            bg="#F0F4F8",
            highlightthickness=0,
        )
        self.canvas.pack()

        self.canvas.create_text(
            370,
            25,
            text=self.titulo,
            font=("Segoe UI", 25, "bold"),
            fill="#263238",
        )

        if self.subtitulo:
            self.canvas.create_text(
                370,
                53,
                text=self.subtitulo,
                font=("Segoe UI", 12, "bold"),
                fill="#64748B",
            )

        self.canvas.create_text(
            370,
            550,
            text="Selecciona con un parpadeo",
            font=("Segoe UI", 13, "bold"),
            fill="#64748B",
        )

        if self.layout == "cuadricula":
            coordenadas = [
                (20, 80, 360, 290),
                (380, 80, 720, 290),
                (20, 300, 360, 510),
                (380, 300, 720, 510),
            ]
            fuente = ("Segoe UI", 32, "bold")
        else:
            coordenadas = [
                (20, 50, 720, 150),
                (20, 170, 720, 270),
                (20, 290, 720, 390),
                (20, 410, 720, 510),
            ]
            fuente = ("Segoe UI", 28, "bold")

        self.coordenadas = coordenadas[: len(self.opciones)]

        for indice, opcion in enumerate(self.opciones):
            izquierda, arriba, derecha, abajo = self.coordenadas[indice]
            color = self.colores[indice % len(self.colores)]

            # La sombra se dibuja primero para quedar detrás de la tarjeta.
            self._rectangulo_redondeado(
                izquierda + 5,
                arriba + 7,
                derecha + 5,
                abajo + 7,
                fill="#D9E2F1",
                outline="#D9E2F1",
            )

            rectangulo = self._rectangulo_redondeado(
                izquierda,
                arriba,
                derecha,
                abajo,
                fill=color,
                outline=color,
                width=0,
            )
            self.rectangulos.append(rectangulo)

            self.canvas.create_text(
                (izquierda + derecha) / 2,
                (arriba + abajo) / 2,
                text=opcion,
                font=fuente,
                fill="#263238",
            )

    def resaltar(self) -> None:
        """Restaura las tarjetas y destaca la opción actual."""
        if self.canvas is None:
            return

        if self.halo_actual is not None:
            self.canvas.delete(self.halo_actual)
            self.halo_actual = None

        for indice, rectangulo in enumerate(self.rectangulos):
            color = self.colores[indice % len(self.colores)]
            self.canvas.itemconfig(
                rectangulo,
                fill=color,
                outline=color,
                width=0,
            )

        if self.rectangulos:
            rectangulo_actual = self.rectangulos[self.indice_actual]
            color_actual = self.colores[
                self.indice_actual % len(self.colores)
            ]
            self.canvas.itemconfig(
                rectangulo_actual,
                fill=self._color_mas_intenso(color_actual),
                outline="#1E293B",
                width=6,
            )

            izquierda, arriba, derecha, abajo = self.coordenadas[
                self.indice_actual
            ]
            self.halo_actual = self._rectangulo_redondeado(
                izquierda - 12,
                arriba - 12,
                derecha + 12,
                abajo + 12,
                radio=30,
                fill="",
                outline="#FFFFFF",
                width=2,
            )
            self.canvas.tag_lower(self.halo_actual)

    def siguiente(self) -> None:
        """Avanza a la siguiente opción y programa otro avance."""
        if self.opciones:
            self.indice_actual += 1
            if self.indice_actual >= len(self.opciones):
                self.indice_actual = 0

            self.resaltar()
            self.timer_id = self.ventana.after(2500, self.siguiente)

    def iniciar(self) -> None:
        """Muestra el menú y comienza el escaneo automático."""
        self.frame.place(x=260, y=0)
        self.resaltar()
        self.siguiente()

    def detener(self) -> None:
        """Oculta el menú y cancela el avance programado."""
        self.frame.place_forget()

        if self.timer_id is not None:
            self.ventana.after_cancel(self.timer_id)
            self.timer_id = None

    def seleccionar(self) -> None:
        """Selecciona la opción actual y avisa mediante el callback."""
        self.detener()
        self.on_select(self.indice_actual)
