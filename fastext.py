import tkinter as tk
from abc import ABC, abstractmethod
import time
import random
from typing import List, Optional
from dataclasses import dataclass

# Entidad de datos para los resultados
@dataclass
class TypingResult:
    wpm: float
    accuracy: float
    time_elapsed: float
    is_perfect: bool

# Interface para la fuente de frases
class PhraseProvider(ABC):
    @abstractmethod
    def get_phrases(self) -> List[str]:
        pass

# Implementación concreta para cargar frases desde archivo
class FilePhraseProvider(PhraseProvider):
    def __init__(self, filename: str):
        self.filename = filename

    def get_phrases(self) -> List[str]:
        try:
            with open(self.filename, "r", encoding='utf-8') as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            return ["El archivo de frases no se encontró. Esta es una frase de ejemplo."]

# Clase para la lógica del test de velocidad
class TypingSpeedTest:
    def __init__(self, phrase_provider: PhraseProvider):
        self.phrase_provider = phrase_provider
        self.phrases = self.phrase_provider.get_phrases()
        self.current_phrase: Optional[str] = None
        self.start_time: Optional[float] = None

    def start_new_test(self) -> str:
        self.current_phrase = random.choice(self.phrases)
        self.start_time = time.time()
        return self.current_phrase

    def evaluate_test(self, user_input: str) -> TypingResult:
        if not self.current_phrase or not self.start_time:
            raise ValueError("Test no iniciado")

        time_elapsed = time.time() - self.start_time
        words = len(self.current_phrase.split())
        minutes = time_elapsed / 60
        wpm = words / minutes

        # Calcula la precisión usando la distancia de Levenshtein
        accuracy = self._calculate_accuracy(user_input, self.current_phrase)
        is_perfect = user_input == self.current_phrase

        return TypingResult(
            wpm=wpm,
            accuracy=accuracy,
            time_elapsed=time_elapsed,
            is_perfect=is_perfect
        )

    def _calculate_accuracy(self, s1: str, s2: str) -> float:
        if len(s2) == 0:
            return 0.0

        if len(s1) == 0:
            return 0.0

        # Implementación simple de precisión basada en caracteres correctos
        matches = sum(1 for a, b in zip(s1, s2) if a == b)
        max_length = max(len(s1), len(s2))
        return (matches / max_length) * 100

# Clase para la interfaz gráfica
class TypingSpeedTestGUI:
    def __init__(self, test: TypingSpeedTest):
        self.test = test
        self.window = tk.Tk()
        self.setup_gui()

    def setup_gui(self):
        self.window.title("Prueba de Velocidad de Escritura")
        self.window.geometry("800x400")
        self.window.configure(padx=20, pady=20)

        # Frame principal
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Widgets
        self.create_widgets(main_frame)

    def create_widgets(self, frame):
        # Estilo y configuración mejorada
        title_style = {'font': ('Arial', 14, 'bold'), 'pady': 10}
        text_style = {'font': ('Arial', 12), 'pady': 5}
        button_style = {'font': ('Arial', 11), 'padx': 20, 'pady': 5}

        self.instruction_label = tk.Label(
            frame, 
            text="Presiona Empezar y escribe la frase que aparece:",
            **text_style
        )
        self.instruction_label.pack()

        self.phrase_label = tk.Label(
            frame, 
            text="",
            wraplength=700,
            **text_style
        )
        self.phrase_label.pack(pady=20)

        self.entry = tk.Entry(frame, width=50, font=('Arial', 12))
        self.entry.pack(pady=10)

        button_frame = tk.Frame(frame)
        button_frame.pack(pady=10)

        self.start_button = tk.Button(
            button_frame,
            text="Empezar",
            command=self.start_test,
            **button_style
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.evaluate_button = tk.Button(
            button_frame,
            text="Evaluar",
            command=self.evaluate_test,
            state=tk.DISABLED,
            **button_style
        )
        self.evaluate_button.pack(side=tk.LEFT, padx=5)

        self.result_label = tk.Label(
            frame,
            text="",
            wraplength=700,
            **text_style
        )
        self.result_label.pack(pady=20)

    def start_test(self):
        phrase = self.test.start_new_test()
        self.phrase_label.config(text=phrase)
        self.entry.delete(0, tk.END)
        self.entry.focus()
        self.evaluate_button.config(state=tk.NORMAL)
        self.result_label.config(text="")

    def evaluate_test(self):
        try:
            result = self.test.evaluate_test(self.entry.get())
            self._display_results(result)
            self.evaluate_button.config(state=tk.DISABLED)
        except ValueError as e:
            self.result_label.config(text=f"Error: {str(e)}")

    def _display_results(self, result: TypingResult):
        status = "¡Perfecto!" if result.is_perfect else "Hay algunos errores."
        message = (
            f"{status}\n"
            f"Velocidad: {result.wpm:.2f} PPM\n"
            f"Precisión: {result.accuracy:.1f}%\n"
            f"Tiempo: {result.time_elapsed:.2f} segundos"
        )
        self.result_label.config(text=message)

    def run(self):
        self.window.mainloop()

# Función principal
def main():
    # Inicialización del sistema
    phrase_provider = FilePhraseProvider("frases.txt")
    typing_test = TypingSpeedTest(phrase_provider)
    gui = TypingSpeedTestGUI(typing_test)
    gui.run()

if __name__ == "__main__":
    main()