"""Manim: saubere Sinuswelle, dann mit 5. und 7. Oberschwingung verzerrt (Hochformat).
Nutzung: manim -qh --resolution 1080,1920 welle.py Welle
"""

import numpy as np
from manim import (
    DOWN,
    UP,
    Axes,
    Create,
    FadeIn,
    FadeOut,
    Scene,
    Text,
    ValueTracker,
    always_redraw,
    config,
)

config.background_color = "#0b0f14"
config.frame_width = 9
config.frame_height = 16

GELB = "#f5c400"
ROT = "#ff5a3c"


class Welle(Scene):
    def construct(self):
        ax = Axes(
            x_range=[0, 4 * np.pi, np.pi],
            y_range=[-1.6, 1.6, 1],
            x_length=8,
            y_length=5,
            axis_config={"color": "#5a6470", "stroke_width": 2},
        )
        k = ValueTracker(0)
        kurve = always_redraw(
            lambda: ax.plot(
                lambda x: (
                    np.sin(x)
                    + k.get_value() * (0.25 * np.sin(5 * x) + 0.15 * np.sin(7 * x))
                ),
                color=GELB if k.get_value() < 0.5 else ROT,
                stroke_width=7,
            )
        )
        titel = Text(
            "Sauberer Sinus", font="Inter", weight="BOLD", color="white"
        ).scale(0.9)
        titel.next_to(ax, UP, buff=1.2)
        unten = (
            Text("50 Hz", font="Inter", color=GELB)
            .scale(0.7)
            .next_to(ax, DOWN, buff=1.0)
        )
        self.add(ax)
        self.play(Create(kurve), FadeIn(titel), FadeIn(unten), run_time=1.2)
        neu = Text(
            "Mit 5. und 7. Harmonischer", font="Inter", weight="BOLD", color="white"
        )
        neu.scale(0.75).move_to(titel)
        neu_u = (
            Text("Oberschwingungen", font="Inter", color=ROT).scale(0.7).move_to(unten)
        )
        self.play(
            FadeOut(titel, shift=UP * 0.3), FadeOut(unten, shift=DOWN * 0.3), run_time=0.35
        )
        self.play(
            k.animate.set_value(1),
            FadeIn(neu, shift=UP * 0.3),
            FadeIn(neu_u, shift=DOWN * 0.3),
            run_time=1.25,
        )
        self.wait(1.2)
