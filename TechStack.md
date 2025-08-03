# Specyfikacja Techniczna: Aplikacja do Pobierania i Transkrypcji Nagrań

## 1. Wprowadzenie

Niniejszy dokument stanowi specyfikację techniczną dla aplikacji do pobierania i transkrypcji nagrań z serwisu `nagrywanie.plus.pl`. Opisuje architekturę, komponenty, przepływy danych i wymagania niezbędne do implementacji systemu w środowisku Google Colab z interfejsem Gradio. Dokument przeznaczony jest dla deweloperów odpowiedzialnych za realizację projektu.

## 2. Architektura Systemu

### 2.1. Przegląd Ogólny

System jest aplikacją monolityczną uruchamianą w ramach pojedynczego notebooka Google Colab. Architektura opiera się na trzech głównych warstwach:

1.  **Warstwa Prezentacji (UI)**: Realizowana przez bibliotekę Gradio, udostępnia interfejs użytkownika w przeglądarce internetowej. Jest odpowiedzialna za zbieranie danych od użytkownika i wizualizację postępu oraz wyników.
2.  **Warstwa Logiki Biznesowej (Backend)**: Rdzeń aplikacji napisany w języku Python. Odpowiada za orkiestrację całego procesu: komunikację z zewnętrznym API, zarządzanie plikami, przetwarzanie audio i obsługę błędów.
3.  **Warstwa Danych i Usług Zewnętrznych**: Składa się z Dysku Google (do przechowywania plików), API `nagrywanie.plus.pl` (źródło nagrań) oraz modeli AI (WhisperX, Pyannote) hostowanych na Hugging Face.

### 2.2. Stos Technologiczny

| Komponent | Wybrana Technologia | Rola |
| :--- | :--- | :--- |
| **Środowisko uruchomieniowe** | Google Colab | Hostowanie aplikacji, dostarczanie zasobów GPU i zarządzanie sekretami. |
| **Język programowania** | Python 3.x | Język implementacji całej logiki aplikacji. |
| **Framework UI** | Gradio | Budowa interaktywnego interfejsu webowego i jego publiczne udostępnianie. |
| **Klient HTTP** | Requests | Komunikacja z API `nagrywanie.plus.pl`. |
| **Transkrypcja i Diaryzacja** | WhisperX | Przetwarzanie plików audio: transkrypcja, alignment, diaryzacja. |
| **Framework AI/ML** | PyTorch, torchaudio | Środowisko do uruchamiania modeli AI (WhisperX). |
| **Zarządzanie plikami** | Moduły `os`, `pathlib`, `zipfile` | Operacje na plikach i katalogach na zamontowanym Dysku Google. |
| **Magazyn danych** | Google Drive | Trwałe przechowywanie pobranych plików audio i wygenerowanych transkrypcji. |
| **Zarządzanie sekretami** | Google Colab Userdata | Bezpieczne zarządzanie tokenem dostępowym do Hugging Face. |
| **Obsługa dat** | Moduł `datetime` | Generowanie i formatowanie dat. |

### 2.3. Struktura Katalogów na Google Drive

Aplikacja będzie tworzyć i zarządzać katalogami na Dysku Google użytkownika zgodnie z poniższą strukturą. Główny folder dla każdego dnia będzie nazwany w formacie `YYYY-MM-DD`.

```
/content/drive/MyDrive/
└── YYYY-MM-DD/
    ├── nagranie_1.mp3
    ├── nagranie_1.txt
    ├── nagranie_2.mp3
    ├── nagranie_2.txt
    └── ...
```

## 3. Specyfikacja Komponentów

### 3.1. Moduł Inicjalizacyjny
*   **Odpowiedzialność**: Przygotowanie środowiska przy starcie notebooka Colab.
*   **Zadania**:
    1.  Automatyczna instalacja wszystkich wymaganych zależności (`whisperx`, `gradio`, `requests`, `torch`, `pyannote.audio`).
    2.  Montowanie Dysku Google użytkownika pod ścieżką `/content/drive/MyDrive/`.
    3.  Pobranie tokenu `HF_TOKEN` z menedżera sekretów Google Colab.
    4.  Inicjalizacja i pobranie modeli WhisperX oraz modeli diaryzacji `pyannote` z wykorzystaniem pobranego tokenu. Modele zostaną załadowane do pamięci GPU, jeśli jest dostępne.

### 3.2. Interfejs Użytkownika (Gradio)
*   **Odpowiedzialność**: Interakcja z użytkownikiem.
*   **Komponenty**:
    *   `gr.Textbox` (label="Nazwa użytkownika"): Pole do wprowadzenia loginu API.
    *   `gr.Textbox` (label="Hasło", type="password"): Pole do wprowadzenia hasła API.
    *   `gr.Dropdown` (label="Data"): Lista rozwijana z datami z ostatnich 3 miesięcy, wygenerowana statycznie przy starcie. Format etykiet: `YYYY-MM-DD (Dzień tygodnia)`.
    *   `gr.Button` (value="Pobierz nagrania"): Przycisk inicjujący główny proces. Będzie dezaktywowany na czas przetwarzania.
    *   `gr.Textbox` (label="Status", interactive=False): Wyświetlanie aktualnego stanu operacji (np. "Pobieranie listy nagrań...", "Transkrypcja pliku X...").
    *   `gr.Progress` (label="Postęp"): Wizualizacja ogólnego postępu operacji.
    *   `gr.Textbox` (label="Logi", lines=10, interactive=False): Wyświetlanie szczegółowych logów z operacji.
*   **Interaktywność**: Aktualizacje komponentów Status, Postęp i Logi będą realizowane asynchronicznie za pomocą mechanizmu `yield` w głównej funkcji obsługującej.

### 3.3. Kontroler Procesu
*   **Odpowiedzialność**: Orkiestracja całego przepływu pracy po kliknięciu przycisku.
*   **Logika**:
    1.  Walidacja danych wejściowych z formularza (login, hasło, data muszą być podane).
    2.  Wywołanie Klienta API w celu pobrania listy nagrań.
    3.  Aktualizacja UI o liczbę znalezionych plików.
    4.  Jeśli znaleziono pliki, wywołanie Zarządcy Plików w celu utworzenia katalogu docelowego.
    5.  W pętli, dla każdego `recId` z listy:
        a. Wywołanie Klienta API w celu pobrania pliku audio.
        b. Wywołanie Zarządcy Plików w celu zapisu pliku na dysku.
        c. Aktualizacja UI z postępem pobierania.
    6.  Po pobraniu wszystkich plików, w pętli dla każdego pliku audio:
        a. Wywołanie Procesora Transkrypcji.
        b. Aktualizacja UI z postępem transkrypcji.
    7.  Wyświetlenie komunikatu o zakończeniu operacji.

### 3.4. Klient API
*   **Odpowiedzialność**: Komunikacja z API `nagrywanie.plus.pl`.
*   **Metody**:
    *   `get_recordings_list(date, credentials)`: Wysyła zapytanie GET na endpoint `/recordingsPaged/`. Obsługuje paginację, iteracyjnie pobierając wszystkie strony wyników, aż pole `last` w odpowiedzi będzie miało wartość `true`. Składa pełną listę `recId` ze wszystkich stron.
    *   `download_recording(recId, credentials, save_path)`: Wysyła zapytanie GET na endpoint `/recording/{recId}` i zapisuje strumieniowo odpowiedź binarną do pliku w podanej ścieżce.
*   **Implementacja**: Wykorzysta bibliotekę `requests`. Uwierzytelnianie Basic Auth zostanie skonfigurowane na podstawie danych z formularza. Zapytania będą zawierać mechanizm obsługi timeoutów.

### 3.5. Zarządca Plików
*   **Odpowiedzialność**: Operacje na systemie plików.
*   **Funkcjonalności**:
    *   Tworzenie katalogu docelowego na Dysku Google, jeśli nie istnieje.
    *   Generowanie nazw plików na podstawie metadanych z API w formacie `recId-callingUserPart-calledUserPart-callDirection`.
    *   Zapisywanie plików audio pobranych przez Klienta API.
    *   W przypadku pobrania archiwum ZIP, rozpakowanie jego zawartości do katalogu docelowego i usunięcie pliku ZIP.
    *   Zapisywanie plików tekstowych `.txt` z wynikami transkrypcji.

### 3.6. Procesor Transkrypcji
*   **Odpowiedzialność**: Konwersja plików audio na tekst z identyfikacją mówców.
*   **Proces**: Dla każdego pliku audio wykonuje sekwencję operacji z użyciem biblioteki WhisperX:
    1.  **Transkrypcja**: Załadowanie pliku audio i przetworzenie go przez model Whisper w celu uzyskania surowej transkrypcji.
    2.  **Wyrównanie (Alignment)**: Użycie modelu alignment do precyzyjnego dopasowania słów do znaczników czasu.
    3.  **Diaryzacja (Diarization)**: Użycie modelu `pyannote.audio` do identyfikacji segmentów mowy poszczególnych mówców i przypisania im etykiet (SPEAKER_00, SPEAKER_01, itd.).
    4.  **Zapis wyniku**: Sformatowanie połączonych wyników do formatu tekstowego i przekazanie ich do Zarządcy Plików w celu zapisu.

## 4. Przepływ Operacji
1.  **Start**: Użytkownik uruchamia notebooka. Moduł Inicjalizacyjny instaluje zależności, montuje dysk i ładuje modele AI. Interfejs Gradio jest uruchamiany.
2.  **Interakcja Użytkownika**: Użytkownik wprowadza dane logowania, wybiera datę i klika "Pobierz nagrania".
3.  **Pobieranie Listy**: Kontroler Procesu wywołuje Klienta API. Klient API wysyła zapytanie o listę nagrań dla wybranej daty, obsługując paginację.
4.  **Tworzenie Katalogu**: Kontroler, po otrzymaniu listy `recId`, zleca Zarządcy Plików utworzenie folderu `YYYY-MM-DD`.
5.  **Pobieranie Plików**: Kontroler iteruje po liście `recId`. W każdej iteracji Klient API pobiera jeden plik audio, Zarządca Plików zapisuje go na dysku, a UI jest aktualizowane o postęp.
6.  **Transkrypcja**: Po zakończeniu pobierania Kontroler iteruje po pobranych plikach audio. W każdej iteracji Procesor Transkrypcji przetwarza plik, a UI jest aktualizowane o postęp.
7.  **Zapis Transkrypcji**: Wynik z Procesora Transkrypcji jest przekazywany do Zarządcy Plików i zapisywany jako plik `.txt`.
8.  **Zakończenie**: UI wyświetla komunikat o pomyślnym zakończeniu wszystkich operacji.

## 5. Obsługa Błędów i Niezawodność
*   **Błędy API**:
    *   `401 Unauthorized`: Przechwycenie błędu, przerwanie procesu i wyświetlenie w UI komunikatu o błędnych danych logowania.
    *   `404 Not Found` / `5xx Server Error`: Przechwycenie błędu, zalogowanie go w UI i kontynuacja procesu dla pozostałych plików (w przypadku błędu przy pobieraniu pojedynczego nagrania) lub przerwanie (w przypadku błędu przy pobieraniu listy).
    *   `Timeout`: Implementacja mechanizmu ponawiania prób (retry) z opóźnieniem (exponential backoff) dla zapytań API.
*   **Błędy Plików**: Jeśli plik audio jest uszkodzony i Procesor Transkrypcji zwróci błąd, plik zostanie pominięty, a informacja o błędzie zostanie zapisana w logach w UI.
*   **Brak Nagrań**: Jeśli API zwróci `totalElements: 0`, proces zostanie zatrzymany, a użytkownik otrzyma stosowny komunikat.
*   **Błąd Tokena HF**: Aplikacja na starcie zweryfikuje obecność tokena. W razie jego braku, proces zostanie przerwany z instrukcją konfiguracji w Colab Secrets.

## 6. Bezpieczeństwo
*   **Dane logowania**: Hasło użytkownika będzie wprowadzane w polu typu `password`, co zapobiega jego wyświetlaniu. Dane logowania będą przechowywane w pamięci tylko na czas trwania operacji i nie będą zapisywane na stałe.
*   **Token Hugging Face**: Token będzie pobierany wyłącznie z bezpiecznego menedżera sekretów Google Colab i nigdy nie będzie jawnie umieszczony w kodzie notebooka ani logach.

## 7. Specyfikacja Danych
*   **Format daty w API**: Data będzie formatowana do postaci `YYYY-MM-DDTHH:mm:ss`, np. `2025-07-22T00:00:00`.
*   **Format pliku wyjściowego (`.txt`)**: Każda linia będzie zawierać znacznik czasu, identyfikator mówcy i tekst wypowiedzi, zgodnie ze wzorcem:
    `[HH:MM:SS.ms - HH:MM:SS.ms] SPEAKER_XX: Treść wypowiedzi.`

## 8. Referencyjny Skrypt Colab (Baza Implementacji)

### 8.1. Przegląd
W ramach przygotowań do implementacji został utworzony i przetestowany skrypt Colab (`WhisperDiarizationManualColab.ipy`), który implementuje pełny workflow transkrypcji i diaryzacji audio. Skrypt stanowi referencyjną implementację funkcjonalności Procesora Transkrypcji opisanej w sekcji 3.6.

### 8.2. Komponenty Skryptu

#### Instalacja i Konfiguracja
```python
# Aktualizacja systemu i instalacja dependencji CUDA
!apt update & apt upgrade -y
!apt install libcudnn8 libcudnn8-dev -y
!pip install whisperx

# Import bibliotek i konfiguracja
import whisperx
import gc
from google.colab import userdata
import os

# Konfiguracja tokenu Hugging Face
HF_TOKEN = userdata.get('HF_TOKEN')
os.environ['HF_TOKEN'] = HF_TOKEN
```

#### Parametry Konfiguracyjne
*   **Device**: `"cuda"` - wykorzystanie GPU dla przyspieszenia
*   **Batch Size**: `16` - rozmiar batcha (redukcja przy ograniczeniach pamięci GPU)
*   **Compute Type**: `"float16"` - precyzja obliczeń (alternatywnie `"int8"` przy niskiej pamięci)
*   **Model Whisper**: `"large-v2"` - wersja modelu do transkrypcji

#### Workflow Przetwarzania (3-stopniowy)

1. **Transkrypcja (Whisper)**:
   ```python
   model = whisperx.load_model("large-v2", device, compute_type=compute_type)
   audio = whisperx.load_audio(audio_file)
   result = model.transcribe(audio, batch_size=batch_size)
   ```

2. **Alignment (Wyrównanie czasowe)**:
   ```python
   model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
   result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
   ```

3. **Diarization (Identyfikacja mówców)**:
   ```python
   diarize_model = whisperx.diarize.DiarizationPipeline(use_auth_token=HF_TOKEN, device=device)
   diarize_segments = diarize_model(audio)
   result = whisperx.assign_word_speakers(diarize_segments, result)
   ```

### 8.3. Formaty Wyjściowe

Skrypt implementuje zapisywanie wyników w czterech formatach:

1. **JSON** (`transcription_result.json`): Pełny wynik z wszystkimi metadanymi
2. **TXT** (`transcription.txt`): Format czytelny zgodny ze specyfikacją:
   ```
   [start_time - end_time] SPEAKER_XX: tekst wypowiedzi
   ```
3. **CSV** (`transcription.csv`): Format tabelaryczny z kolumnami: Start, End, Speaker, Text
4. **CSV diaryzacji** (`diarization_segments.csv`): Segmenty identyfikacji mówców

### 8.4. Optymalizacja Pamięci GPU

Skrypt zawiera mechanizmy zarządzania pamięcią GPU:
```python
# Opcjonalne czyszczenie pamięci między etapami
import gc; import torch; 
gc.collect(); torch.cuda.empty_cache(); del model
```

### 8.5. Implementacja w Aplikacji Docelowej

**Zmiany wymagane do integracji**:

1. **Parametryzacja ścieżek**: Zastąpienie stałej ścieżki `/content/test.mp3` dynamicznymi ścieżkami plików z Zarządcy Plików
2. **Obsługa błędów**: Dodanie mechanizmów try-catch dla każdego etapu przetwarzania
3. **Aktualizacje UI**: Integracja z komponentami Gradio dla raportowania postępu
4. **Wsadowe przetwarzanie**: Adaptacja do przetwarzania wielu plików w pętli
5. **Konfiguracja modeli**: Przeniesienie ładowania modeli do Modułu Inicjalizacyjnego
6. **Format wyjściowy**: Standaryzacja na format TXT zgodny ze specyfikacją z sekcji 7

**Zalety referencyjnej implementacji**:
*   Przetestowana funkcjonalność na rzeczywistych danych
*   Optymalna konfiguracja parametrów dla środowiska Colab
*   Sprawdzone mechanizmy zarządzania pamięcią GPU
*   Wieloformatowe wyjście umożliwiające elastyczność