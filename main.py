import customtkinter as ctk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import struct

from generate import szum_o_rozkladzie_jednostkowym
import stats

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class SignalApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Generator i Edytor Sygnałów - Cyfrowe Przetwarzanie Sygnałów")
        self.geometry("1300x900")
        self.configure(fg_color="#ffffff")

        self.current_t = None
        self.current_a = None

        self.sig1 = {"t": None, "a": None, "fs": None}
        self.sig2 = {"t": None, "a": None, "fs": None}

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkScrollableFrame(self, width=400, corner_radius=0, fg_color="#f2f2f2")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="GENERATOR (S1-S11)", font=ctk.CTkFont(size=18, weight="bold")).pack(
            pady=(10, 5))

        self.signal_var = ctk.StringVar(value="1")
        warianty_s = [
            ("(S1) Szum o rozkładzie jednostajnym", "1"), ("(S2) Szum gaussowski", "2"),
            ("(S3) Sygnał sinusoidalny", "3"), ("(S4) Sygnał sinusoidalny wyprostowany jednopołówkowo", "4"),
            ("(S5) Sygnał sinusoidalny wyprostowany dwupołówkowo", "5"), ("(S6) Sygnał prostokątny", "6"),
            ("(S7) Sygnał prostokątny symetryczny", "7"), ("(S8) Sygnał trójkątny", "8"),
            ("(S9) Skok jednostkowy", "9"), ("(S10) Impuls jednostkowy", "10"),
            ("(S11) Szum impulsowy", "11")
        ]
        for txt, val in warianty_s:
            ctk.CTkRadioButton(self.sidebar, text=txt, variable=self.signal_var, value=val,
                               font=ctk.CTkFont(size=11)).pack(pady=1, padx=20, anchor="w")

        ctk.CTkLabel(self.sidebar, text="Parametry:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 0))
        self.inputs = {}
        self.add_input("Amplituda (A)", "A", "5.0")
        self.add_input("Czas start (t1)", "t1", "1.0")
        self.add_input("Czas trwania (d)", "d", "10.0")
        self.add_input("Częstotliwość (f) / Okres (T)", "fT", "1.0")
        self.add_input("Biny (histogram)", "bins", "15")

        ctk.CTkButton(self.sidebar, text="GENERUJ SYGNAŁ", command=self.generate, fg_color="#2ecc71",
                      hover_color="#27ae60").pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.sidebar, text="OPERACJE (D1-D4)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 5))
        ctk.CTkButton(self.sidebar, text="WCZYTAJ PLIK 1", command=lambda: self.load_to_buffer(1),
                      fg_color="#9b59b6").pack(pady=2, padx=20, fill="x")
        self.label_s1 = ctk.CTkLabel(self.sidebar, text="S1: brak", font=ctk.CTkFont(size=10))
        self.label_s1.pack()

        ctk.CTkButton(self.sidebar, text="WCZYTAJ PLIK 2", command=lambda: self.load_to_buffer(2),
                      fg_color="#9b59b6").pack(pady=2, padx=20, fill="x")
        self.label_s2 = ctk.CTkLabel(self.sidebar, text="S2: brak", font=ctk.CTkFont(size=10))
        self.label_s2.pack()

        ops_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        ops_frame.pack(pady=5)
        for i, op in enumerate([("+", "D1"), ("-", "D2"), ("*", "D3"), ("/", "D4")]):
            ctk.CTkButton(ops_frame, text=op[0], width=60, command=lambda o=op[0]: self.perform_math(o)).grid(
                row=i // 2, column=i % 2, padx=5, pady=5)

        ctk.CTkLabel(self.sidebar, text="PLIKI", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 0))
        ctk.CTkButton(self.sidebar, text="ZAPISZ BIEŻĄCY", command=self.save_to_bin, fg_color="#3498db").pack(pady=2,
                                                                                                              padx=20,
                                                                                                              fill="x")
        ctk.CTkButton(self.sidebar, text="ODCZYTAJ I POKAŻ", command=self.load_and_show, fg_color="#3498db").pack(
            pady=2, padx=20, fill="x")

        self.stats_box = ctk.CTkTextbox(self.sidebar, height=180, fg_color="white", border_width=1, text_color="black")
        self.stats_box.pack(pady=15, padx=20, fill="x")

        self.plot_frame = ctk.CTkFrame(self, fg_color="white")
        self.plot_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(7, 9), facecolor='white')
        self.fig.tight_layout(pad=6.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill="both")

    def add_input(self, label, key, default):
        ctk.CTkLabel(self.sidebar, text=label, font=ctk.CTkFont(size=11)).pack(anchor="w", padx=20)
        entry = ctk.CTkEntry(self.sidebar, height=25)
        entry.insert(0, default)
        entry.pack(padx=20, pady=2, fill="x")
        self.inputs[key] = entry

    # --- LOGIKA PROGRAMU ---

    def generate(self):
        try:
            A = float(self.inputs["A"].get())
            t1 = float(self.inputs["t1"].get())
            d = float(self.inputs["d"].get())
            wybor = self.signal_var.get()

            if wybor == "1":
                self.current_t, self.current_a = szum_o_rozkladzie_jednostkowym(A, t1, d)
                self.update_view("S1: Szum Jednostajny")
            else:
                messagebox.showinfo("Informacja", "Wybierz S1. Pozostałe wzory wymagają uzupełnienia w generate.py")
        except Exception as e:
            messagebox.showerror("Błąd", f"Niepoprawne parametry: {e}")

    def perform_math(self, op):
        if self.sig1["a"] is None or self.sig2["a"] is None:
            messagebox.showwarning("Błąd", "Wczytaj najpierw oba pliki do operacji!")
            return

        length = min(len(self.sig1["a"]), len(self.sig2["a"]))
        a1, a2 = self.sig1["a"][:length], self.sig2["a"][:length]

        if op == "+":
            self.current_a = a1 + a2
        elif op == "-":
            self.current_a = a1 - a2
        elif op == "*":
            self.current_a = a1 * a2
        elif op == "/":
            self.current_a = a1 / np.where(a2 == 0, 1e-9, a2)

        self.current_t = self.sig1["t"][:length]
        self.update_view(f"Wynik operacji: {op}")

    def update_view(self, nazwa):
        res = {
            "Średnia": stats.srednia(self.current_a),
            "Śr. Bezwz.": stats.srednia_bezw(self.current_a),
            "Skuteczna": stats.skuteczna(self.current_a),
            "Wariancja": stats.wariancja(self.current_a),
            "Moc średnia": stats.moc_srednia(self.current_a)
        }

        self.stats_box.delete("0.0", "end")
        self.stats_box.insert("end", f"NAZWA: {nazwa}\n" + "-" * 25 + "\n")
        for k, v in res.items():
            self.stats_box.insert("end", f"{k:15}: {v:.4f}\n")

        self.ax1.clear()
        self.ax1.plot(self.current_t, self.current_a, color='#2980b9')
        self.ax1.set_title("PRZEBIEG CZASOWY", fontweight='bold')
        self.ax1.grid(True, alpha=0.3)

        self.ax2.clear()
        b = int(self.inputs["bins"].get())
        self.ax2.hist(self.current_a, bins=b, color='#3498db', edgecolor='white')
        self.ax2.set_title("HISTOGRAM", fontweight='bold')
        self.canvas.draw()

    # --- OBSŁUGA PLIKÓW ---

    def save_to_bin(self):
        if self.current_a is None: return
        path = filedialog.asksaveasfilename(defaultextension=".bin")
        if path:
            header = struct.pack('ddii', self.current_t[0], 10.0, 0, len(self.current_a))
            with open(path, 'wb') as f:
                f.write(header)
                for val in self.current_a:
                    f.write(struct.pack('d', float(val)))
            messagebox.showinfo("Zapis", "Sygnał zapisany poprawnie.")

    def load_and_show(self):
        path = filedialog.askopenfilename(filetypes=[("Pliki binarne", "*.bin")])
        if path:
            t, a, fs = self._read_bin(path)
            self.current_t, self.current_a = t, a
            self.update_view(f"Z pliku: {path.split('/')[-1]}")

    def load_to_buffer(self, num):
        path = filedialog.askopenfilename(filetypes=[("Pliki binarne", "*.bin")])
        if path:
            t, a, fs = self._read_bin(path)
            name = path.split('/')[-1]
            if num == 1:
                self.sig1 = {"t": t, "a": a, "fs": fs}
                self.label_s1.configure(text=f"S1: {name}")
            else:
                self.sig2 = {"t": t, "a": a, "fs": fs}
                self.label_s2.configure(text=f"S2: {name}")

    def _read_bin(self, path):
        with open(path, 'rb') as f:
            h = struct.unpack('ddii', f.read(24))
            t1, fs, typ, N = h
            d = [struct.unpack('d', f.read(8))[0] for _ in range(N)]
        t = np.array([t1 + i / fs for i in range(N)])
        return t, np.array(d), fs


if __name__ == "__main__":
    app = SignalApp()
    app.mainloop()