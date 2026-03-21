import customtkinter as ctk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import struct
from plot import rysuj_przebieg_czasowy, rysuj_histogram
from generate import *
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
        self.history = []
        self.history_index = -1

        # Mapowanie nazw wyświetlanych w menu na numery sygnałów
        self.warianty_dict = {
            "(S1) Szum o rozkładzie jednostajnym": "1",
            "(S2) Szum gaussowski": "2",
            "(S3) Sygnał sinusoidalny": "3",
            "(S4) Sinusoidalny wyprostowany jednopołówkowo": "4",
            "(S5) Sinusoidalny wyprostowany dwupołówkowo": "5",
            "(S6) Sygnał prostokątny": "6",
            "(S7) Sygnał prostokątny symetryczny": "7",
            "(S8) Sygnał trójkątny": "8",
            "(S9) Skok jednostkowy": "9",
            "(S10) Impuls jednostkowy": "10",
            "(S11) Szum impulsowy": "11"
        }

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkScrollableFrame(self, width=400, corner_radius=0, fg_color="#f2f2f2")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="WYBÓR SYGNAŁU", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 5))

        # --- MENU ---
        self.signal_option_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=list(self.warianty_dict.keys()),
            command=self.update_inputs_visibility,
            dynamic_resizing=False,
            width=300
        )
        self.signal_option_menu.pack(pady=10, padx=20, fill="x")
        self.signal_option_menu.set(list(self.warianty_dict.keys())[0])

        ctk.CTkLabel(self.sidebar, text="Parametry:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 0))

        # --- KONTENER NA PARAMETRY ---
        self.params_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.params_container.pack(fill="x")

        self.inputs = {}
        self.add_input("Amplituda (A)", "A", "5.0")
        self.add_input("Czas start (t1)", "t1", "1.0")
        self.add_input("Czas trwania (d)", "d", "10.0")
        self.add_input("Częstotliwość próbkowania (f) [Hz]", "f", "100.0")
        self.add_input("Okres (T) [s]", "T", "1.0")
        self.add_input("Współczynnik wypełnienia / p", "kw", "0.5")
        self.add_input("Moment skoku/impulsu (ts)", "ts", "5.0")
        self.add_input("Biny (histogram)", "bins", "15")

        ctk.CTkButton(self.sidebar, text="GENERUJ SYGNAŁ", command=self.generate, fg_color="#2ecc71",
                      hover_color="#27ae60").pack(pady=10, padx=20, fill="x")

        # Nawigacja i Buffory
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(pady=5, padx=20, fill="x")
        self.btn_prev = ctk.CTkButton(nav_frame, text="← Poprzedni", width=10, command=self.prev_signal,
                                      state="disabled")
        self.btn_prev.grid(row=0, column=0, padx=5, sticky="ew")
        self.btn_next = ctk.CTkButton(nav_frame, text="Następny →", width=10, command=self.next_signal,
                                      state="disabled")
        self.btn_next.grid(row=0, column=1, padx=5, sticky="ew")
        nav_frame.grid_columnconfigure((0, 1), weight=1)

        buffer_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        buffer_frame.pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(buffer_frame, text="Bieżący → S1", command=lambda: self.set_to_buffer(1), fg_color="#e67e22",
                      width=10).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(buffer_frame, text="Bieżący → S2", command=lambda: self.set_to_buffer(2), fg_color="#e67e22",
                      width=10).grid(row=0, column=1, padx=5, sticky="ew")
        buffer_frame.grid_columnconfigure((0, 1), weight=1)

        # Operacje i Statystyki
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

        # --- WYKRESY ---
        self.plot_frame = ctk.CTkFrame(self, fg_color="white")
        self.plot_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(7, 9), facecolor='white')
        self.fig.tight_layout(pad=6.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill="both")

        self.update_inputs_visibility()

    def add_input(self, label, key, default):
        row_frame = ctk.CTkFrame(self.params_container, fg_color="transparent")
        row_frame.pack(padx=20, pady=2, fill="x")
        lbl = ctk.CTkLabel(row_frame, text=label, font=ctk.CTkFont(size=11))
        lbl.pack(anchor="w")
        entry = ctk.CTkEntry(row_frame, height=25)
        entry.insert(0, default)
        entry.pack(fill="x")
        self.inputs[key] = {"entry": entry, "frame": row_frame}

    def update_inputs_visibility(self, *args):
        wybrana_nazwa = self.signal_option_menu.get()
        wybor = self.warianty_dict[wybrana_nazwa]

        mapa = {
            "1": ["A", "t1", "d", "f"],
            "2": ["A", "t1", "d", "f"],
            "3": ["A", "t1", "d", "f", "T"],
            "4": ["A", "t1", "d", "f", "T"],
            "5": ["A", "t1", "d", "f", "T"],
            "6": ["A", "t1", "d", "f", "T", "kw"],
            "7": ["A", "t1", "d", "f", "T", "kw"],
            "8": ["A", "t1", "d", "f", "T", "kw"],
            "9": ["A", "t1", "d", "f", "ts"],
            "10": ["A", "t1", "d", "f", "ts"],
            "11": ["A", "t1", "d", "f", "kw"]
        }
        potrzebne = mapa.get(wybor, []) + ["bins"]
        for key in self.inputs:
            if key in potrzebne:
                self.inputs[key]["frame"].pack(padx=20, pady=2, fill="x")
            else:
                self.inputs[key]["frame"].pack_forget()

    def generate(self):
        try:
            A = float(self.inputs["A"]["entry"].get())
            t1 = float(self.inputs["t1"]["entry"].get())
            d = float(self.inputs["d"]["entry"].get())
            f = float(self.inputs["f"]["entry"].get())
            T = float(self.inputs["T"]["entry"].get())
            kw = float(self.inputs["kw"]["entry"].get())
            ts = float(self.inputs["ts"]["entry"].get())

            nazwa_wyswietlana = self.signal_option_menu.get()
            wybor = self.warianty_dict[nazwa_wyswietlana]

            if wybor == "1":
                self.current_t, self.current_a = szum_o_rozkladzie_jednostkowym(A, t1, d, f)
            elif wybor == "2":
                self.current_t, self.current_a = szum_gaussowski(A, t1, d, f)
            elif wybor == "3":
                self.current_t, self.current_a = sygnal_sinusoidalny(A, T, t1, d, f)
            elif wybor == "4":
                self.current_t, self.current_a = sygnal_sinusoidalny_wyp_jed(A, T, t1, d, f)
            elif wybor == "5":
                self.current_t, self.current_a = sygnal_sinusoidalny_wyp_dwu(A, T, t1, d, f)
            elif wybor == "6":
                self.current_t, self.current_a = sygnal_prostokatny(A, T, t1, d, kw, f)
            elif wybor == "7":
                self.current_t, self.current_a = sygnal_prostokatny_symetryczny(A, T, t1, d, kw, f)
            elif wybor == "8":
                self.current_t, self.current_a = sygnal_trojkatny(A, T, t1, d, kw, f)
            elif wybor == "9":
                self.current_t, self.current_a = skok_jednostkowy(A, t1, d, ts, f)
            elif wybor == "10":
                self.current_t, self.current_a = impuls_jednostkowy(A, t1, d, ts, f)
            elif wybor == "11":
                self.current_t, self.current_a = szum_impulsowy(A, t1, d, kw, f)

            self.update_view(nazwa_wyswietlana)
        except Exception as e:
            messagebox.showerror("Błąd", f"Niepoprawne parametry: {e}")

    def perform_math(self, op):
        if self.sig1["a"] is None or self.sig2["a"] is None:
            messagebox.showwarning("Błąd", "Wczytaj oba pliki!")
            return
        a1, a2 = np.array(self.sig1["a"]), np.array(self.sig2["a"])
        length = min(len(a1), len(a2))
        a1, a2 = a1[:length], a2[:length]
        if op == "+":
            self.current_a = a1 + a2
        elif op == "-":
            self.current_a = a1 - a2
        elif op == "*":
            self.current_a = a1 * a2
        elif op == "/":
            self.current_a = a1 / np.where(a2 == 0, 1e-9, a2)
        self.current_t = np.array(self.sig1["t"])[:length]
        self.update_view(f"Operacja: {op}")

    def update_view(self, nazwa, save_to_history=True):
        res = {
            "Średnia": stats.srednia(self.current_a),
            "Śr. Bezwz.": stats.srednia_bezw(self.current_a),
            "Skuteczna": stats.skuteczna(self.current_a),
            "Wariancja": stats.wariancja(self.current_a),
            "Moc średnia": stats.moc_srednia(self.current_a)
        }
        self.stats_box.delete("0.0", "end")
        self.stats_box.insert("end", f"NAZWA: {nazwa}\n" + "-" * 25 + "\n")
        for k, v in res.items(): self.stats_box.insert("end", f"{k:15}: {v:.4f}\n")

        if save_to_history:
            if self.history_index < len(self.history) - 1: self.history = self.history[:self.history_index + 1]
            self.history.append((np.array(self.current_t).copy(), np.array(self.current_a).copy(), nazwa))
            self.history_index = len(self.history) - 1
            self.update_nav_buttons()

        rysuj_przebieg_czasowy(self.ax1, self.current_t, self.current_a, nazwa)
        rysuj_histogram(self.ax2, self.current_a, int(self.inputs["bins"]["entry"].get()))
        self.canvas.draw()

    def save_to_bin(self):
        if self.current_a is None: return
        path = filedialog.asksaveasfilename(defaultextension=".bin")
        if path:
            fs = float(self.inputs["f"]["entry"].get())
            header = struct.pack('ddii', self.current_t[0], fs, 0, len(self.current_a))
            with open(path, 'wb') as f:
                f.write(header)
                for val in self.current_a: f.write(struct.pack('d', float(val)))
            messagebox.showinfo("Zapis", "Poprawnie zapisano.")

    def load_and_show(self):
        path = filedialog.askopenfilename(filetypes=[("Pliki binarne", "*.bin")])
        if path:
            t, a, fs = self._read_bin(path)
            self.current_t, self.current_a = t, a
            self.update_view(f"Plik: {path.split('/')[-1]}")

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
        return np.array([t1 + i / fs for i in range(N)]), np.array(d), fs

    def set_to_buffer(self, num):
        if self.current_a is not None:
            data = {"t": np.array(self.current_t).copy(), "a": np.array(self.current_a).copy(),
                    "fs": float(self.inputs["f"]["entry"].get())}
            if num == 1:
                self.sig1 = data
                self.label_s1.configure(text="S1: Bieżący (pamięć)")
            else:
                self.sig2 = data
                self.label_s2.configure(text="S2: Bieżący (pamięć)")
            messagebox.showinfo("Pamięć", f"Zapisano w buforze S{num}")

    def prev_signal(self):
        if self.history_index > 0: self.history_index -= 1; self.load_from_history()

    def next_signal(self):
        if self.history_index < len(self.history) - 1: self.history_index += 1; self.load_from_history()

    def load_from_history(self):
        t, a, n = self.history[self.history_index]
        self.current_t, self.current_a = t, a
        self.update_view(n, False)
        self.update_nav_buttons()

    def update_nav_buttons(self):
        self.btn_prev.configure(state="normal" if self.history_index > 0 else "disabled")
        self.btn_next.configure(state="normal" if self.history_index < len(self.history) - 1 else "disabled")


if __name__ == "__main__":
    app = SignalApp()
    app.mainloop()