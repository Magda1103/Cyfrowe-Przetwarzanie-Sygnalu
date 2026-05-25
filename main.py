import customtkinter as ctk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from file_manager import *
from plot import *
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
        self.oryginalny_t = None
        self.oryginalny_a = None
        self.probkowany_t = None
        self.probkowany_a = None

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
        self.add_input("Częstotliwość próbkowania (fs) docelowa [Hz]", "fs_new", "20.0")
        self.add_input("Liczba bitów kwantyzatora (b)", "bits", "4")
        self.add_input("Liczba próbek sinc (N)", "sinc_n", "10")

        # ... istniejące parametry ...
        self.add_input("Rząd filtru (M)", "M", "63")
        self.add_input("Współczynnik odcięcia (K)", "K", "8.0")

        # --- PARAMETRY RADARU (od strony środowiska) ---
        self.add_input("Krok czasu symulacji (dt) [s]", "dt_sim", "0.0001")
        self.add_input("Prędkość obiektu (v_obj) [m/s]", "v_obj", "15.0")
        self.add_input("Prędkość sygnału (V) [m/s]", "v_sig", "300.0")
        self.add_input("Początkowa odległość obiektu [m]", "d0", "50.0")

        # --- PARAMETRY RADARU (od strony czujnika) ---
        self.add_input("Długość bufora radaru (N próbek)", "N_radar", "500")
        self.add_input("Okres raportowania [s]", "T_rep", "1.0")
        self.add_input("Liczba kroków symulacji (raportów)", "n_reps", "10")

        # --- SEKCJA FILTRACJI ---
        ctk.CTkLabel(self.sidebar, text="FILTRACJA", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 5))

        self.window_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=["Ok. Prostokątne", "Ok. Blackmana (O3)"]
        )
        self.window_menu.pack(pady=5, padx=20, fill="x")

        self.filter_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=["Dolnoprzepustowy", "Górnoprzepustowy (F2)"]
        )
        self.filter_menu.pack(pady=5, padx=20, fill="x")

        ctk.CTkButton(self.sidebar, text="FILTRUJ", command=self.perform_filtering,
                      fg_color="#d35400", hover_color="#e67e22").pack(pady=10, padx=20, fill="x")

        # --- SEKCJA RADARU ---
        ctk.CTkLabel(self.sidebar, text="RADAR KORELACYJNY", font=ctk.CTkFont(size=16, weight="bold")).pack(
            pady=(20, 5))
        ctk.CTkButton(self.sidebar, text="SKANUJ OBIEKT", command=self.simulate_radar,
                      fg_color="#8e44ad", hover_color="#9b59b6").pack(pady=10, padx=20, fill="x")

        # --- SEKCJA KONWERSJI ---
        ctk.CTkLabel(self.sidebar, text="KONWERSJA A/C i C/A", font=ctk.CTkFont(size=16, weight="bold")).pack(
            pady=(20, 5))

        konw_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        konw_frame.pack(pady=5, padx=20, fill="x")

        ctk.CTkButton(konw_frame, text="S1 + Q2 (Próbkowanie i Kwantyzacja)", command=self.perform_ac,
                      fg_color="#e74c3c").pack(pady=2, fill="x")
        ctk.CTkButton(konw_frame, text="Rekonstrukcja (R2 - FOH)", command=lambda: self.perform_ca("R2"),
                      fg_color="#34495e").pack(pady=2, fill="x")
        ctk.CTkButton(konw_frame, text="Rekonstrukcja (R3 - Sinc)", command=lambda: self.perform_ca("R3"),
                      fg_color="#34495e").pack(pady=2, fill="x")

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

        ops = [("+", "D1"), ("-", "D2"), ("*", "D3"), ("/", "D4"),
               ("Splot", "Splot"), ("Kor. bezp.", "Kor_bezp"), ("Kor. splot", "Kor_splot")]

        for i, op in enumerate(ops):
            ctk.CTkButton(ops_frame, text=op[0], width=90, command=lambda o=op[1]: self.perform_math(o)).grid(
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

        potrzebne = mapa.get(wybor, []) + ["bins", "fs_new", "bits", "sinc_n", "M", "K",
                                           "v_sig", "d0", "N_radar", "dt_sim", "v_obj", "T_rep", "n_reps"]
        for key in self.inputs:
            if key in potrzebne:
                self.inputs[key]["frame"].pack(padx=20, pady=2, fill="x")
            else:
                self.inputs[key]["frame"].pack_forget()

    def generate(self):
        try:
            def get_val(key):
                val = self.inputs[key]["entry"].get()
                return float(val) if val else 0.0

            A = get_val("A")
            t1 = get_val("t1")
            d = get_val("d")
            f = get_val("f")
            T = get_val("T")
            kw = get_val("kw")
            ts = get_val("ts")

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

            sygnaly_okresowe = ["3", "4", "5", "6", "7", "8"]
            if wybor in sygnaly_okresowe:
                liczba_pelnych_okresow = int(d // T)
                if liczba_pelnych_okresow > 0:
                    t_max = t1 + (liczba_pelnych_okresow * T)

                    t_arr = np.array(self.current_t)
                    a_arr = np.array(self.current_a)

                    maska = t_arr < t_max
                    self.current_t = t_arr[maska]
                    self.current_a = a_arr[maska]
                else:
                    messagebox.showwarning("Uwaga",
                                           "Czas trwania jest krótszy niż jeden okres. Statystyki mogą być błędne.")

            # ustaw nowy oryginał
            self.oryginalny_t = np.array(self.current_t)
            self.oryginalny_a = np.array(self.current_a)

            # wyczyść stare A/C
            self.probkowany_t = None
            self.probkowany_a = None

            self.update_view(nazwa_wyswietlana)

        except Exception as e:
            messagebox.showerror("Błąd", f"Niepoprawne parametry: {e}")

    def perform_math(self, op):
        if self.sig1["a"] is None or self.sig2["a"] is None:
            messagebox.showwarning("Błąd", "Wczytaj oba pliki!")
            return

        a1, a2 = np.array(self.sig1["a"]), np.array(self.sig2["a"])

        if op in ["Splot", "Kor_bezp", "Kor_splot"]:
            M = len(a1)
            N = len(a2)
            dlugosc = M + N - 1

            self.current_a = np.zeros(dlugosc)

            if op == "Splot":
                # Algorytm splotu
                for n in range(dlugosc):
                    suma = 0.0
                    for k in range(M):
                        if 0 <= n - k < N:
                            suma += a1[k] * a2[n - k]
                    self.current_a[n] = suma
                nazwa_op = "Splot"

            elif op == "Kor_bezp":
                # WARIANT 1: Implementacja bezpośrednia korelacji wzajemnej
                for m in range(dlugosc):
                    suma = 0.0
                    shift = m - (N - 1)
                    for k in range(M):
                        if 0 <= k - shift < N:
                            suma += a1[k] * a2[k - shift]
                    self.current_a[m] = suma
                nazwa_op = "Korelacja (bezpośrednia)"

            elif op == "Kor_splot":
                # WARIANT 2: Implementacja z użyciem splotu
                a2_rev = a2[::-1]
                for n in range(dlugosc):
                    suma = 0.0
                    for k in range(M):
                        if 0 <= n - k < N:
                            suma += a1[k] * a2_rev[n - k]
                    self.current_a[n] = suma
                nazwa_op = "Korelacja (przez splot)"

            if len(self.sig1["t"]) > 1:
                dt = self.sig1["t"][1] - self.sig1["t"][0]
            else:
                dt = 1.0

            t_start = self.sig1["t"][0]
            self.current_t = np.array([t_start + i * dt for i in range(dlugosc)])

            self.update_view(f"Operacja: {nazwa_op}")
            return

        length = min(len(a1), len(a2))
        a1, a2 = a1[:length], a2[:length]

        if op == "+":
            self.current_a = a1 + a2
        elif op == "-":
            self.current_a = a1 - a2
        elif op == "*":
            self.current_a = a1 * a2
        elif op == "/":
            a2_safe = np.where(np.abs(a2) < 1e-9, np.nan, a2)
            self.current_a = a1 / a2_safe

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

        if self.oryginalny_t is not None and self.oryginalny_a is not None:
            rysuj_przebieg_czasowy(
                self.ax1,
                self.current_t,
                self.current_a,
                nazwa,
                t_ref=self.oryginalny_t,
                a_ref=self.oryginalny_a
            )
        else:
            rysuj_przebieg_czasowy(
                self.ax1,
                self.current_t,
                self.current_a,
                nazwa
            )
        rysuj_histogram(self.ax2, self.current_a, int(self.inputs["bins"]["entry"].get()))
        self.canvas.draw()

    def save_to_bin(self):
        if self.current_a is None: return
        path = filedialog.asksaveasfilename(defaultextension=".bin")
        if path:
            fs = float(self.inputs["f"]["entry"].get())
            wybor = self.warianty_dict[self.signal_option_menu.get()]

            typ_sygnalu = 1 if wybor in ["9", "10", "11"] else 0

            zapisz_sygnal_binarnie(path, self.current_t[0], fs, self.current_a, typ=typ_sygnalu)
            messagebox.showinfo("Zapis", "Sygnał zapisany z informacją o typie.")

    def load_and_show(self):
        path = filedialog.askopenfilename(filetypes=[("Pliki binarne", "*.bin")])
        if path:
            t, a, fs, typ = odczytaj_sygnal_binarnie(path)
            self.current_t, self.current_a = t, a

            nazwa_pliku = path.split('/')[-1]
            if typ == 1:
                nazwa_wyswietlana = f"Impuls - {nazwa_pliku}"
            else:
                nazwa_wyswietlana = nazwa_pliku

            self.update_view(nazwa_wyswietlana)

    def load_to_buffer(self, num):
        path = filedialog.askopenfilename(filetypes=[("Pliki binarne", "*.bin")], title=f"Wczytaj do S{num}")
        if path:
            t, a, fs, typ = odczytaj_sygnal_binarnie(path)
            name = path.split('/')[-1]
            if num == 1:
                self.sig1 = {"t": t, "a": a, "fs": fs}
                self.label_s1.configure(text=f"S1: {name}")
            else:
                self.sig2 = {"t": t, "a": a, "fs": fs}
                self.label_s2.configure(text=f"S2: {name}")

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

    def perform_ac(self):
        if self.current_t is None or self.current_a is None:
            messagebox.showwarning("Błąd", "Najpierw wygeneruj sygnał!")
            return

        try:
            self.oryginalny_t = np.array(self.current_t)
            self.oryginalny_a = np.array(self.current_a)

            fs_new = float(self.inputs["fs_new"]["entry"].get())
            bits = int(self.inputs["bits"]["entry"].get())

            # --- S1: PRÓBKOWANIE ---
            t_p, a_p = probkowanie_rownomierne(
                self.oryginalny_t,
                self.oryginalny_a,
                fs_new
            )

            # --- Q2: KWANTYZACJA ---
            a_pq = kwantyzacja_q2(a_p, bits)


            self.s1_t = t_p
            self.s1_a = a_p

            self.q2_t = t_p
            self.q2_a = a_pq


            self.probkowany_t = t_p
            self.probkowany_a = a_p
            self.kwantyzowany_a = a_pq

            # --- DO STATYSTYK ---
            a_rec_sampling = rekonstrukcja_r2(
                self.oryginalny_t,
                t_p,
                a_p
            )
            self.a_rec_s1 = a_rec_sampling

            # --- RYSOWANIE ---
            self.ax1.clear()

            # 🟢 ORYGINAŁ
            self.ax1.plot(
                self.oryginalny_t,
                self.oryginalny_a,
                color='green',
                linewidth=2,
                label="Oryginał"
            )

            # 🔴 PRÓBKI
            self.ax1.plot(
                self.s1_t,
                self.s1_a,
                'ro',
                markersize=4,
                label="Próbki (S1)"
            )

            # 🔵 KWANTYZACJA
            self.ax1.step(
                self.q2_t,
                self.q2_a,
                where='post',
                color='blue',
                linewidth=2,
                label="Kwantyzacja (Q2)"
            )

            self.ax1.set_title("Próbkowanie i kwantyzacja")
            self.ax1.set_xlabel("T [s]")
            self.ax1.set_ylabel("Amplituda")
            self.ax1.grid(True)
            self.ax1.legend()

            # histogram z kwantyzacji
            rysuj_histogram(self.ax2, self.q2_a, int(self.inputs["bins"]["entry"].get()))

            self.canvas.draw()

            # --- STATYSTYKI ---
            self.stats_box.delete("0.0", "end")
            self.stats_box.insert("end", "NAZWA: S1 + Q2\n")
            self.stats_box.insert("end", "-" * 25 + "\n")

            # błędy próbkowania
            self.show_metrics(
                self.oryginalny_a,
                a_rec_sampling,
                "BŁĘDY PRÓBKOWANIA (S1)"
            )

            # błędy kwantyzacji
            self.show_metrics(
                a_p,
                a_pq,
                "BŁĘDY KWANTYZACJI (Q2)"
            )

            snr_teoria = 6.02 * bits + 1.76
            self.stats_box.insert("end", f"SNR teoretyczne: {snr_teoria:.2f} dB\n")

            # ustaw current na kwantyzację (żeby dalej działało GUI)
            self.current_t = t_p
            self.current_a = a_pq

        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd w konwersji A/C: {e}")

    def perform_ca(self, metoda):
        if self.s1_t is None or self.oryginalny_t is None:
            messagebox.showwarning("Błąd", "Najpierw wykonaj S1 + Q2!")
            return

        try:
            if metoda == "R2":
                a_rek = self.a_rec_s1
                nazwa = "Zrekonstruowany (R2 - FOH)"



            elif metoda == "R3":

                n_sinc = int(self.inputs["sinc_n"]["entry"].get())

                a_rek = rekonstrukcja_r3(

                    self.oryginalny_t,

                    self.s1_t,

                    self.s1_a,

                    n_sinc

                )
                nazwa = f"Zrekonstruowany (R3 - Sinc, N={n_sinc})"
            self.current_t = self.oryginalny_t
            self.current_a = a_rek

            self.update_view(nazwa)
            self.show_metrics(self.oryginalny_a, a_rek, f"BŁĘDY REKONSTRUKCJI ({metoda})")

        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd w rekonstrukcji: {e}")

    def show_metrics(self, oryginal, po_zmianie, tytul):
        # Funkcja obliczająca i dopisująca statystyki C1-C4 do okienka
        m_mse = stats.mse(oryginal, po_zmianie)
        m_snr = stats.snr(oryginal, po_zmianie)
        m_psnr = stats.psnr(oryginal, po_zmianie)
        m_md = stats.md(oryginal, po_zmianie)
        val_enob = stats.enob(m_snr)

        self.stats_box.insert("end", f"\n--- {tytul} ---\n")
        self.stats_box.insert("end", f"MSE (C1) : {m_mse:.4f}\n")
        self.stats_box.insert("end", f"SNR (C2) : {m_snr:.4f} dB\n")
        self.stats_box.insert("end", f"PSNR (C3): {m_psnr:.4f} dB\n")
        self.stats_box.insert("end", f"MD (C4)  : {m_md:.4f}\n")
        if val_enob != float('inf'):
            self.stats_box.insert("end", f"ENOB     : {val_enob:.2f} bitów\n")

    def perform_filtering(self):
        if self.current_a is None or self.current_t is None:
            messagebox.showwarning("Błąd", "Najpierw wygeneruj sygnał do przefiltrowania!")
            return

        try:
            M = int(self.inputs["M"]["entry"].get())
            K = float(self.inputs["K"]["entry"].get())

            if M % 2 == 0:
                M += 1
                messagebox.showinfo("Informacja", f"Rząd filtru M musi być nieparzysty. Zmieniono M na {M}.")

            h = np.zeros(M)
            center = (M - 1) / 2

            window_type = self.window_menu.get()
            filter_type = self.filter_menu.get()

            for n in range(M):
                # 1. Baza: Idealny filtr dolnoprzepustowy
                if n == center:
                    h[n] = 2.0 / K
                else:
                    h[n] = np.sin(2.0 * np.pi * (n - center) / K) / (np.pi * (n - center))

                if "Blackmana" in window_type:
                    w = 0.42 - 0.5 * np.cos(2.0 * np.pi * n / M) + 0.08 * np.cos(4.0 * np.pi * n / M)
                else:
                    w = 1.0  # Okno prostokątne

                h[n] *= w

                if "Górnoprzepustowy" in filter_type:
                    h[n] *= (-1) ** n

            # Filtracja sygnału za pomocą splotu
            x = np.array(self.current_a)
            N_sig = len(x)
            y = np.zeros(N_sig)

            for n in range(N_sig):
                suma = 0.0
                for k in range(M):
                    if n - k >= 0:
                        suma += h[k] * x[n - k]
                y[n] = suma

            if self.oryginalny_a is None or len(self.oryginalny_a) != len(self.current_a):
                self.oryginalny_a = self.current_a.copy()
                self.oryginalny_t = self.current_t.copy()

            self.current_a = y
            rysuj_przebieg_czasowy(self.ax1, self.current_t, self.current_a,
                                   tytul=f"Filtrowanie: {filter_type}...",
                                   show_ref=False)
            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas filtracji: {e}")

    def simulate_radar(self):
        try:
            # Odczyt parametrów środowiska i obiektu
            dt_sim = float(self.inputs["dt_sim"]["entry"].get())
            v_obj = float(self.inputs["v_obj"]["entry"].get())
            V = float(self.inputs["v_sig"]["entry"].get())
            d0 = float(self.inputs["d0"]["entry"].get())

            # Odczyt parametrów czujnika
            fs = float(self.inputs["f"]["entry"].get())
            N = int(self.inputs["N_radar"]["entry"].get())
            T_rep = float(self.inputs["T_rep"]["entry"].get())
            T_probe = float(self.inputs["T"]["entry"].get()) if self.inputs["T"]["entry"].get() else 1.0
            n_reps = int(self.inputs["n_reps"]["entry"].get())

            self.stats_box.delete("0.0", "end")
            self.stats_box.insert("end", "--- SYMULACJA RADARU (W CZASIE) ---\n")

            historia_t = []
            historia_d_true = []
            historia_d_calc = []

            for step in range(n_reps):
                obecny_czas = step * T_rep

                # Obliczenie rzeczywistej odległości w danej chwili (obiekt się porusza)
                d_true = d0 + v_obj * obecny_czas
                t_delay_true = (2.0 * d_true) / V  # Rzeczywiste opóźnienie sygnału

                czas_bufora = N / fs

                t_cont = np.arange(-t_delay_true - 1.0, czas_bufora + 1.0, dt_sim)

                # Złożony, ciągły sygnał sondujący
                x_cont = np.sin(2.0 * np.pi * (1.0 / T_probe) * t_cont) + 0.5 * np.cos(
                    2.0 * np.pi * (2.0 / T_probe) * t_cont)

                # Próbkowanie sygnałów do buforów (krok czujnika)
                t_radar = np.arange(0, N) / fs

                # Sygnał wysłany z radaru (próbkowany z x_cont)
                x_sampled = np.interp(t_radar, t_cont, x_cont)

                # Sygnał odebrany (prawidłowo opóźniony - odejmujemy opóźnienie od osi docelowej)
                y_sampled = np.interp(t_radar - t_delay_true, t_cont, x_cont)

                dlugosc_R = 2 * N - 1
                R = np.zeros(dlugosc_R)

                for m in range(dlugosc_R):
                    suma = 0.0
                    shift = m - (N - 1)
                    for k in range(N):
                        if 0 <= k - shift < N:
                            suma += y_sampled[k] * x_sampled[k - shift]
                    R[m] = suma

                center_idx = N - 1
                right_side = R[center_idx:]

                peak_idx = np.argmax(right_side)
                t_calc = peak_idx / fs
                d_calc = (V * t_calc) / 2.0

                historia_t.append(obecny_czas)
                historia_d_true.append(d_true)
                historia_d_calc.append(d_calc)

                self.stats_box.insert("end",
                                      f"Raport {step + 1} (t={obecny_czas}s) | Rzeczywista: {d_true:.2f}m | Zmierzona: {d_calc:.2f}m\n")

            self.fig.clear()

            ax1 = self.fig.add_subplot(311)
            ax2 = self.fig.add_subplot(312)
            ax3 = self.fig.add_subplot(313)
            self.fig.subplots_adjust(hspace=0.6)

            # --- Wykres 1: Sygnał oryginalny x ---
            ax1.plot(x_sampled, color="black")
            ax1.set_title("sygnał okresowy oryginalny x", loc='left', fontsize=10)
            ax1.grid(True, linestyle="--")
            ax1.set_xlim(0, N)

            # --- Wykres 2: Sygnał opóźniony y ---
            ax2.plot(y_sampled, color="black")
            ax2.set_title(f"sygnał okresowy x opóźniony o {peak_idx} próbek zwany dalej sygnałem y", loc='left',
                          fontsize=10)
            ax2.grid(True, linestyle="--")
            ax2.set_xlim(0, N)

            # --- Wykres 3: Korelacja wzajemna ---
            ax3.plot(R, color="black")
            ax3.set_title("korelacja sygnałów y oraz x", loc='left', fontsize=10)
            ax3.grid(True, linestyle="--")
            ax3.set_xlim(0, len(R))

            max_pos = center_idx + peak_idx
            y_text = right_side[peak_idx] * 1.15 if right_side[peak_idx] > 0 else 50

            ax3.annotate('pierwsze maksimum',
                         xy=(max_pos, right_side[peak_idx]),
                         xytext=(max_pos + 40, y_text),
                         arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.5),
                         fontsize=10, fontweight='bold')

            self.canvas.draw()

            self.ax1 = ax1
            self.ax2 = ax2

        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd w symulacji radaru: {e}")

if __name__ == "__main__":
    app = SignalApp()
    app.mainloop()