# Finalny Plan Implementacji: Aplikacja w Notatniku Google Colab (Wersja Deweloperska)

Niniejszy dokument stanowi kompletny, krok-po-kroku przewodnik implementacyjny dla aplikacji do pobierania i transkrypcji nagrań. Struktura dokumentu odzwierciedla podział na komórki w notatniku Google Colab, z wyraźnym oddzieleniem komórek definicyjnych od uruchomieniowych, co ułatwia wdrożenie i debugowanie.

---

### **Komórka 1: Instalacja Zależności**

**Opis:**
Ta komórka jest odpowiedzialna za zainstalowanie wszystkich bibliotek niezbędnych do działania aplikacji. Uruchamiana jest jako pierwsza. **Celowo nie używamy flagi `-q` (`--quiet`), aby zapewnić pełną widoczność procesu instalacji i umożliwić łatwe debugowanie.**

**Zadania do zaimplementowania:**
*   Instalacja `whisperx`, `gradio`, `requests`, `torch`, `torchaudio`, `pyannote.audio`.

```python
# Zawartość do wklejenia w komórce 1
!pip install "whisperx[dev] @ git+https://github.com/m-bain/whisperx.git" gradio torch torchaudio requests pyannote.audio==3.1.1
```

---

### **Komórka 2: Importy i Konfiguracja Globalna**

**Opis:**
W tej komórce centralizujemy wszystkie importy, co ułatwia zarządzanie zależnościami w kodzie.

**Zadania do zaimplementowania:**
*   Import modułów standardowych (`os`, `datetime`, `json`).
*   Import bibliotek zewnętrznych (`requests`, `gradio as gr`, `torch`).
*   Import modułów z Colab (`drive`, `userdata`).

---

### **Komórka 3: Inicjalizacja Środowiska (Dysk i Sekrety)**

**Opis:**
Ta komórka wykonuje kluczowe operacje konfiguracyjne: montowanie Dysku Google oraz weryfikację dostępu do tokenu Hugging Face.

**Zadania do zaimplementowania:**
1.  **Montowanie Dysku Google:** `drive.mount('/content/drive')`.
2.  **Konfiguracja Tokenu HF:** Weryfikacja istnienia `HF_TOKEN` w `userdata` i wyświetlenie instrukcji w razie jego braku.

---

### **Komórka 4: DEFINICJE - Funkcje Pomocnicze (API i Pliki)**

**Opis:**
Ta komórka zawiera **wyłącznie definicje** funkcji odpowiedzialnych za komunikację z API oraz operacje na plikach. Uruchomienie tej komórki nie wywołuje żadnej z tych funkcji, a jedynie udostępnia je w pamięci notatnika.

**Zadania do zaimplementowania (jako definicje `def`):**
1.  `get_recordings_list(username, password, selected_date_str)`
    *   **Formatowanie daty**: Przetwarza datę wybraną z listy (np. "2023-10-26...") na dwa stringi w formacie `YYYY-MM-DDTHH:mm:ss`, wymaganym przez API.
        *   Parametr `dateFrom` zostanie ustawiony na początek dnia, np. `2023-10-26T00:00:00`.
        *   Parametr `dateTo` zostanie ustawiony na koniec dnia, np. `2023-10-26T23:59:59`.
    *   **Obsługa paginacji**: Implementuje pętlę, która automatycznie wysyła kolejne żądania do API, inkrementując numer strony, aż pole `last` w odpowiedzi będzie miało wartość `true`.
    *   **Agregacja wyników**: Zbiera `recId` i metadane ze wszystkich stron odpowiedzi, aby stworzyć jedną, kompletną listę nagrań dla danego dnia.
2.  `download_recording(session, recId, save_path)`
3.  `create_target_directory(selected_date_str)`
4.  `generate_filename_base(record_metadata)`
    *   **Logika nazewnictwa**: Tworzy bazową nazwę pliku (bez rozszerzenia) na podstawie metadanych pojedynczego nagrania.
    *   **Format nazwy**: `recId-callingUserPart-calledUserPart-callDirection`.
    *   **Przykład**: `1539595123456-223334455-226667788-MO`. Ta bazowa nazwa będzie później używana do tworzenia plików `.mp3` i `.txt`.
5.  `save_transcription(directory, base_filename, transcription_data)`
6.  `generate_date_dropdown_options()`
7.  `unzip_file(zip_path, extract_to_directory)`
    *   **Logika dekompresji**: Rozpakowuje plik `.zip` i umieszcza jego zawartość w określonym katalogu.

---

### **Komórka 5: DEFINICJE - Funkcje Przetwarzania Audio (WhisperX)**

**Opis:**
Ta komórka izoluje **definicje** funkcji związanych z przetwarzaniem AI.

**Zadania do zaimplementowania (jako definicje `def`):**
1.  `initialize_models(hf_token)`
2.  `process_audio_file(audio_path, models)`

---

### **Komórka 6: DEFINICJA - Główna Logika Aplikacji (Orkiestrator)**

**Opis:**
Ta komórka zawiera **definicję** jednej, głównej funkcji `main_process`, która łączy wszystkie wcześniej zdefiniowane komponenty. Ta funkcja zostanie wywołana dopiero przez interfejs Gradio.

**Zadania do zaimplementowania (jako definicja `def`):**
1.  `main_process(username, password, selected_date, progress=gr.Progress(track_tqdm=True))`
    *   Zaimplementuj pełen przepływ operacji (walidacja, pobieranie listy, logowanie, pętle pobierania i transkrypcji), używając `yield` do komunikacji z interfejsem.

---

### **Komórka 7: URUCHOMIENIE - Interfejs Użytkownika (Gradio)**

**Opis:**
Ostatnia komórka, która **uruchamia** całą aplikację. Tworzy interfejs użytkownika i wiąże akcję przycisku z funkcją `main_process`. Jest to jedyny punkt wejścia dla użytkownika końcowego.

**Zadania do zaimplementowania:**
1.  Przygotuj dane dla UI (wygeneruj listę dat).
2.  Zdefiniuj layout `gr.Blocks()`.
3.  Połącz przycisk z funkcją `main_process` za pomocą `button.click()`, mapując wejścia i wyjścia.
4.  Uruchom aplikację: `demo.launch(share=True, debug=True)`.
