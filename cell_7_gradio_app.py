#######################
## KOMÓRKA 7 ##
#######################

# KOMÓRKA 7: URUCHOMIENIE - Interfejs Użytkownika (Gradio)
# Ostatnia komórka, która URUCHAMIA całą aplikację.
# Tworzy interfejs użytkownika i wiąże akcję przycisku z funkcją main_process.
# Jest to jedyny punkt wejścia dla użytkownika końcowego.

# =============================================================================
# IMPORTY WYMAGANE DLA KOMÓRKI 7
# =============================================================================

print("📦 Sprawdzanie dostępności bibliotek...")

# Import datetime dla lokalnej funkcji generowania dat
from datetime import datetime, timedelta

# Sprawdzenie czy Gradio jest dostępne (powinno być zaimportowane w komórce 2)
try:
    gr  # Sprawdź czy gr jest już zdefiniowane
    print("✅ Gradio dostępne z komórki 2")
except NameError:
    print("⚠️  Gradio nie zostało zaimportowane - uruchom najpierw komórkę 2")
    print("   Importuję Gradio lokalnie...")
    import gradio as gr
    print("✅ Gradio zaimportowane lokalnie")

print("🎨 Tworzę interfejs użytkownika Gradio...")
print("=" * 60)

# =============================================================================
# PRZYGOTOWANIE DANYCH DLA UI
# =============================================================================

print("📅 Generowanie listy dat...")

# Lokalna implementacja generowania dat (bez zależności od komórki 4)
def generate_date_dropdown_options_local():
    """
    Generuje opcje dat dla dropdown z ostatnich 3 miesięcy.
    Lokalna wersja dla komórki 7.
    """
    
    options = []
    current_date = datetime.now()
    
    # Słownik dni tygodnia po polsku
    days_pl = {
        0: "Poniedziałek", 1: "Wtorek", 2: "Środa", 3: "Czwartek",
        4: "Piątek", 5: "Sobota", 6: "Niedziela"
    }
    
    # Generowanie dat wstecz przez 90 dni
    for i in range(90):
        date = current_date - timedelta(days=i)
        day_name = days_pl[date.weekday()]
        date_str = date.strftime("%Y-%m-%d")
        formatted_option = f"{date_str} ({day_name})"
        options.append(formatted_option)
    
    return options

# Wygenerowanie opcji dat z ostatnich 3 miesięcy
date_options = generate_date_dropdown_options_local()

if not date_options:
    print("❌ Błąd generowania dat - używam datę domyślną")
    date_options = ["2025-01-09 (Czwartek)"]  # Fallback

print(f"✅ Wygenerowano {len(date_options)} opcji dat")
print(f"   📅 Zakres: {date_options[-1]} - {date_options[0]}")

# =============================================================================
# DEFINICJA INTERFEJSU GRADIO
# =============================================================================

print("🎨 Konfiguracja interfejsu Gradio...")

# Tworzenie aplikacji z Gradio Blocks dla pełnej kontroli layoutu
with gr.Blocks(
    title="Aplikacja do Pobierania i Transkrypcji Nagrań",
    theme=gr.themes.Soft(),
    css="""
    .gradio-container {
        max-width: 1000px !important;
    }
    .progress-bar {
        height: 25px;
    }
    """
) as demo:
    
    # =================================================================
    # NAGŁÓWEK APLIKACJI
    # =================================================================
    
    gr.Markdown("""
    # 🎙️ Aplikacja do Pobierania i Transkrypcji Nagrań
    
    **Funkcjonalności:**
    - 📥 Pobieranie nagrań z API nagrywanie.plus.pl
    - 🎤 Transkrypcja audio przez WhisperX
    - 👥 Diaryzacja mówiących (rozpoznawanie kto mówi)
    - 📁 Automatyczna organizacja plików na Google Drive
    
    **Instrukcje:**
    1. Wprowadź dane logowania do API nagrywanie.plus.pl
    2. Wybierz datę z ostatnich 3 miesięcy
    3. Kliknij "Pobierz nagrania" i obserwuj postęp
    4. Pliki audio i transkrypcje będą zapisane na Google Drive
    """)
    
    # =================================================================
    # SEKCJA FORMULARZA WEJŚCIOWEGO
    # =================================================================
    
    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### 📋 Dane logowania")
            
            # Pola logowania
            username_input = gr.Textbox(
                label="👤 Nazwa użytkownika",
                placeholder="Wprowadź nazwę użytkownika API",
                info="Dane logowania do nagrywanie.plus.pl"
            )
            
            password_input = gr.Textbox(
                label="🔐 Hasło", 
                type="password",
                placeholder="Wprowadź hasło API",
                info="Hasło będzie ukryte podczas wprowadzania"
            )
            
            # Lista dat
            date_input = gr.Dropdown(
                label="📅 Wybierz datę",
                choices=date_options,
                value=date_options[0] if date_options else None,
                info="Dostępne daty z ostatnich 3 miesięcy"
            )
        
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ Działanie")
            
            # Przycisk akcji
            process_button = gr.Button(
                "🚀 Pobierz nagrania",
                variant="primary",
                size="lg",
                interactive=True
            )
            
            # Informacje dodatkowe
            gr.Markdown("""
            **💡 Wymagania:**
            - Google Drive zamontowany
            - HF_TOKEN w Colab Secrets
            - Poprawne dane API
            
            **⏱️ Czas przetwarzania:**
            - ~1-2 min na nagranie
            - Zależny od długości audio
            """)
    
    # =================================================================
    # SEKCJA MONITORINGU I LOGÓW
    # =================================================================
    
    gr.Markdown("### 📊 Monitoring procesu")
    
    with gr.Row():
        with gr.Column(scale=1):
            # Status operacji
            status_output = gr.Textbox(
                label="📈 Status operacji",
                value="⏳ Oczekiwanie na start...",
                interactive=False,
                lines=1
            )
            
            # Informacja o postępie (gr.Progress nie ma label)
            gr.Markdown("**🔄 Postęp operacji:**")
            # Progress bar jest obsługiwany automatycznie przez Gradio
        
        with gr.Column(scale=2):
            # Szczegółowe logi
            logs_output = gr.Textbox(
                label="📝 Szczegółowe logi",
                value="Aplikacja gotowa do działania.\nWprowadź dane i kliknij 'Pobierz nagrania'.\n",
                interactive=False,
                lines=12,
                max_lines=20,
                autoscroll=True
            )
    
    # =================================================================
    # SEKCJA INFORMACYJNA
    # =================================================================
    
    with gr.Accordion("ℹ️ Dodatkowe informacje", open=False):
        gr.Markdown("""
        ### 🔧 Konfiguracja techniczna
        
        **Modele AI:**
        - **WhisperX**: Transkrypcja audio z alignment
        - **Pyannote**: Diaryzacja mówiących (wymaga HF Token)
        
        **Format plików:**
        - **Audio**: MP3 (pobrane z API)
        - **Transkrypcje**: TXT z timestampami i speakerami
        - **Nazwy**: `recId-callingUserPart-calledUserPart-callDirection`
        
        **Przykład transkrypcji:**
        ```
        [00:01:23.45 - 00:01:28.67] SPEAKER_00: Dzień dobry, jak się masz?
        [00:01:29.12 - 00:01:35.78] SPEAKER_01: Dziękuję, wszystko w porządku.
        ```
        
        **Rozwiązywanie problemów:**
        - Sprawdź połączenie internetowe
        - Upewnij się że Google Drive jest zamontowany
        - Zweryfikuj HF_TOKEN w Colab Secrets
        - Sprawdź poprawność danych logowania API
        """)
    
    # =================================================================
    # KONFIGURACJA ZDARZEŃ I INTERAKCJI
    # =================================================================
    
    print("🔗 Konfiguracja zdarzeń interfejsu...")
    
    # Funkcja wrapper dla obsługi progress w Gradio
    def run_main_process(username, password, selected_date, progress=gr.Progress()):
        """
        Wrapper funkcji main_process dla Gradio z obsługą postępu.
        """
        try:
            # Generator z main_process zwraca (status, progress_value, logs)
            for status, progress_value, logs in main_process(username, password, selected_date, progress):
                # Aktualizacja paska postępu
                progress(progress_value / 100, desc=status)
                
                # Yield dla aktualizacji UI
                yield (
                    status,              # status_output
                    logs,               # logs_output  
                    gr.update(interactive=False)  # process_button (dezaktywacja)
                )
            
            # Po zakończeniu - ponowna aktywacja przycisku
            yield (
                status,              # status_output (ostatni)
                logs,               # logs_output (ostatni)
                gr.update(interactive=True)   # process_button (aktywacja)
            )
            
        except Exception as e:
            error_msg = f"❌ Błąd aplikacji: {e}"
            error_logs = f"Krytyczny błąd aplikacji:\n{str(e)}\n\nSprawdź konfigurację i spróbuj ponownie."
            
            yield (
                error_msg,
                error_logs,
                gr.update(interactive=True)
            )
    
    # Podłączenie przycisku do funkcji głównej
    process_button.click(
        fn=run_main_process,
        inputs=[username_input, password_input, date_input],
        outputs=[status_output, logs_output, process_button],
        show_progress=True
    )
    
    # =================================================================
    # DODATKOWE FUNKCJONALNOŚCI UI
    # =================================================================
    
    # Auto-clear logów przy zmianie inputów
    def clear_status():
        return (
            "⏳ Oczekiwanie na start...",
            "Parametry zmienione. Gotowy do nowego procesu.\n"
        )
    
    # Podłączenie event handlerów
    username_input.change(fn=clear_status, outputs=[status_output, logs_output])
    password_input.change(fn=clear_status, outputs=[status_output, logs_output])
    date_input.change(fn=clear_status, outputs=[status_output, logs_output])

print("✅ Interfejs Gradio skonfigurowany")

# =============================================================================
# URUCHOMIENIE APLIKACJI
# =============================================================================

print()
print("=" * 60)
print("🚀 URUCHAMIAM APLIKACJĘ GRADIO")
print("=" * 60)

try:
    print("📡 Tworzenie publicznego linku...")
    print("🔄 Uruchamianie serwera Gradio...")
    print("\n💡 UWAGA: Sprawdzenie środowiska nastąpi po kliknięciu 'Pobierz nagrania'")
    print("   Upewnij się że uruchomiłeś komórki 2-6 przed użyciem aplikacji")
    
    # Uruchomienie aplikacji z publicznym dostępem
    demo.launch(
        share=True,          # Publiczny link dostępny spoza Colab
        debug=True,          # Dodatkowe informacje debugowania
        server_name="0.0.0.0",  # Słuchanie na wszystkich interfejsach
        server_port=None,    # Automatyczny wybór portu
        max_threads=10,      # Limit równoczesnych połączeń
        auth=None,           # Brak dodatkowej autoryzacji
        inbrowser=False,     # Nie otwieraj automatycznie w przeglądarce
        quiet=False          # Pokaż wszystkie komunikaty
    )
    
except Exception as e:
    print(f"❌ Błąd uruchomienia aplikacji: {e}")
    print("💡 Spróbuj uruchomić komórkę ponownie")
    print("   Sprawdź czy wszystkie poprzednie komórki zostały wykonane")

print()
print("=" * 60)
print("✅ KOMÓRKA 7 - APLIKACJA GRADIO URUCHOMIONA")
print("=" * 60)
print("🌐 Aplikacja powinna być dostępna pod publicznym linkiem")
print("📱 Link można udostępnić innym użytkownikom")
print("🔄 Aplikacja działa dopóki komórka jest aktywna")
print("⚠️ Nie zamykaj tej komórki podczas korzystania z aplikacji") 