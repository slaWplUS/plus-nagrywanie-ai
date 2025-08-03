# PRD: Aplikacja do Pobierania Nagrań i Transkrypcji

## 1. Przegląd Aplikacji

### 1.1 Cel
Aplikacja umożliwia pobieranie nagrań audio z serwisu nagrywanie.plus.pl, ich automatyczną transkrypcję przy użyciu modelu WhisperX z diaryzacją mówiących i organizację plików według dat w Google Drive użytkownika.

### 1.2 Platforma
- **Środowisko**: Google Colab
- **Framework**: Gradio
- **Język**: Python
- **Dostęp**: Publiczny link generowany przez Gradio w Colab

## 2. Funkcjonalności Główne

### 2.1 Konfiguracja Początkowa
- **Montowanie Google Drive**: Automatyczne podłączenie dysku Google użytkownika
- **Instalacja WhisperX**: Pobranie i konfiguracja modelu WhisperX z funkcją diaryzacji
- **Uruchomienie interfejsu**: Start aplikacji Gradio z publicznym URL

### 2.2 Interfejs Użytkownika
- **Pola logowania**: Wprowadzenie nazwy użytkownika i hasła do API nagrywanie.plus.pl
- **Lista rozwijana z datami**: Dropdown z datami z ostatnich 3 miesięcy
  - Format wyświetlania: "YYYY-MM-DD (Dzień tygodnia)"
  - Opcje sortowane od najnowszej do najstarszej daty
  - Automatyczne generowanie dat na podstawie aktualnej daty systemu
- **Przycisk "Pobierz nagrania"**: Inicjuje proces pobierania i przetwarzania
- **Licznik plików**: Wyświetlanie ilości plików do pobrania dla wybranej daty (po wywołaniu API)
- **Postęp pobierania**: 
  - Progress bar dla każdego pobieranego pliku
  - Nazwa aktualnie pobieranego pliku
  - Ogólny postęp pobierania (X z Y plików)
- **Postęp transkrypcji z diaryzacją**:
  - Progress bar dla każdego transkrybowanego nagrania
  - Nazwa aktualnie przetwarzanego pliku audio
  - Etapy: transkrypcja → alignment → diaryzacja
  - Ogólny postęp transkrypcji (X z Y nagrań)
- **Status operacji**: Aktualny etap procesu
- **Logi**: Szczegółowe informacje o przetwarzanych plikach

### 2.3 Zarządzanie Plikami
- **Tworzenie katalogów**: Automatyczne utworzenie folderu w formacie `YYYY-MM-DD`
- **Pobieranie ZIP**: Download plików z API nagrywanie.plus.pl
- **Rozpakowywanie**: Automatyczna ekstrakcja plików MP3
- **Czyszczenie**: Usuwanie plików ZIP po rozpakowaniu

### 2.4 Transkrypcja z Diaryzacją
- **Przetwarzanie MP3**: Konwersja audio na tekst przez WhisperX
- **Alignment**: Precyzyjne wyrównanie timestampów
- **Diaryzacja**: Identyfikacja i rozdzielenie różnych mówiących
- **Zapis TXT**: Utworzenie plików tekstowych z oznaczonymi mówiącymi i timestampami
- **HF Token**: Wykorzystanie tokenu z Google Colab Secrets dla modeli diaryzacji

## 3. Przepływ Operacji

### 3.1 Inicjalizacja
1. Użytkownik uruchamia notebook w Colab
2. **Użytkownik konfiguruje HuggingFace Token w Google Colab Secrets (klucz: "HF_TOKEN")**
3. System montuje Google Drive
4. Instaluje i konfiguruje WhisperX + modele diaryzacji (z tokenem z Secrets)
5. **Generuje listę dat z ostatnich 3 miesięcy dla dropdown'a**
6. Uruchamia interfejs Gradio z formularzem logowania i generuje publiczny link

### 3.2 Proces Główny
1. **Użytkownik wprowadza nazwę użytkownika i hasło do API nagrywanie.plus.pl**
2. **Użytkownik wybiera datę z listy rozwijanej**
3. **Użytkownik klika przycisk "Pobierz nagrania"**
4. **System waliduje dane logowania i wykonuje zapytanie API**:
   ```
   GET https://nagrywanie.plus.pl/recordingApi/recordingsPaged/?size=100&page=0&dateFrom=2025-07-22T00:00:00&status=RECORDED
   Authorization: Basic (user:password)
   ```
5. **System parsuje odpowiedź i wyciąga wszystkie recId z content[]**
6. **System obsługuje paginację - pobiera kolejne strony jeśli last: false**
7. **System wyświetla totalElements dostępnych plików dla wybranej daty**
8. Jeśli są dostępne pliki, system tworzy folder `YYYY-MM-DD` na Google Drive
9. **Pobieranie z monitoringiem postępu**:
   - Iteracyjnie pobiera każde nagranie używając endpoint `/recording/{recId}`
   - Wyświetla recId i generowaną nazwę każdego pobieranego nagrania
   - Aktualizuje progress bar dla każdego pliku
   - Pokazuje ogólny postęp (X z totalElements plików)
10. Zapisuje wszystkie pliki audio do utworzonego folderu z nazwami opartymi na metadanych
9. Jeśli pliki są w ZIP - rozpakuje wszystkie pliki ZIP (jeśli applicable)
10. Usuwa pliki ZIP po rozpakowaniu (jeśli applicable)
11. **Transkrypcja z diaryzacją i monitoringiem postępu**:
    - Wyświetla nazwę każdego przetwarzanego pliku MP3
    - Pokazuje etapy: transkrypcja → alignment → diaryzacja
    - Aktualizuje progress bar dla każdego etapu
    - Pokazuje ogólny postęp transkrypcji (X z Y nagrań)
12. Zapisuje transkrypcję z diaryzacją do pliku TXT
13. **Wyświetla komunikat o zakończeniu procesu**

## 4. Architektura Techniczna

### 4.1 Komponenty
- **UI Layer**: Gradio z formularzem logowania, dropdown z datami, przyciskiem akcji i monitoringiem postępu
- **Date Generator**: Moduł generowania listy dat z ostatnich 3 miesięcy dla dropdown'a
- **Date Formatter**: Moduł formatowania dat do formatu API
- **Form Handler**: Obsługa formularza i walidacja danych wejściowych
- **Progress Monitor**: Moduł śledzenia i wyświetlania postępu operacji
- **API Client**: Klient do komunikacji z nagrywanie.plus.pl API z Basic Auth
  - Metoda `get_recordings_list()`: Pobieranie paginowanej listy nagrań dla daty
  - Metoda `download_recording()`: Pobieranie pojedynczego nagrania po recId
  - Obsługa paginacji i retry mechanizmów
  - Parsowanie metadanych dla nazw plików
- **File Manager**: Moduł zarządzania plikami i folderami
- **WhisperX Processor**: Wrapper dla WhisperX z diaryzacją i monitoringiem postępu
- **Storage Handler**: Obsługa Google Drive

### 4.2 Struktura Folderów
```
Google Drive/
└── [data-wybrana]/
    ├── nagranie1.mp3
    ├── nagranie1.txt  # z diaryzacją i timestampami
    ├── nagranie2.mp3
    ├── nagranie2.txt  # z diaryzacją i timestampami
    └── ...
```

### 4.3 Instalacja Dependencies
```python
# Automatyczna instalacja przy starcie
pip install whisperx gradio torch torchaudio requests datetime

# Inicjalizacja z tokenem z Colab Secrets
from google.colab import userdata
hf_token = userdata.get('HF_TOKEN')
```

## 5. Wymagania Funkcjonalne

### 5.1 Formularz Użytkownika
- **Pola logowania**: Text input dla nazwy użytkownika i password input dla hasła
- **Lista dat**: Dropdown z datami z ostatnich 3 miesięcy w formacie "YYYY-MM-DD (Dzień tygodnia)"
- **Przycisk akcji**: "Pobierz nagrania" - inicjuje cały proces
- **Walidacja**: Sprawdzenie czy wszystkie pola są wypełnione przed wywołaniem API

### 5.2 Generator Dat dla Dropdown'a
- **Automatyczne generowanie**: Lista dat z ostatnich 3 miesięcy od aktualnej daty
- **Format opcji**: "YYYY-MM-DD (Dzień tygodnia)" (np. "2025-07-22 (Poniedziałek)")
- **Sortowanie**: Daty sortowane od najnowszej do najstarszej
- **Statyczna lista**: Generowana przy starcie aplikacji, nie wymaga wywołania API

### 5.3 Obsługa Przycisku "Pobierz nagrania"
- **Walidacja formularza**: Sprawdzenie czy użytkownik wprowadził login, hasło i wybrał datę
- **Wywołanie API**: Automatyczne formatowanie daty i wysłanie zapytania
- **Feedback użytkownikowi**: Informowanie o stanie operacji (ładowanie, błędy, sukces)
- **Blokowanie**: Przycisk nieaktywny podczas przetwarzania

### 5.4 Integracja API nagrywanie.plus.pl
- **Endpoint**: `https://nagrywanie.plus.pl/recordingApi/recordingsPaged/`
- **Metoda**: GET z Basic Authentication
- **Automatyczne formatowanie parametrów**: 
  - `dateFrom`: `[wybrana-data]T00:00:00`
  - `dateTo`: `[wybrana-data]T23:59:59`
- **Autoryzacja**: Basic Auth z credentials z formularza
- **Wywołanie**: Tylko po kliknięciu przycisku "Pobierz nagrania"

### 5.5 Monitoring Plików (Po Wywołaniu API)
- **Licznik plików**: Parsowanie odpowiedzi API i wyświetlenie `totalElements` dostępnych nagrań
- **Wyciągnięcie recId**: Ekstrakcja wszystkich `recId` z tablicy `content[]`
- **Obsługa paginacji**: Automatyczne pobieranie kolejnych stron gdy `last: false`
- **Walidacja**: Informowanie użytkownika gdy brak nagrań dla wybranej daty (`totalElements: 0`)
- **Metadane**: Wyświetlanie informacji o plikach (recordingNumber, startTime, length, size)
- **Nazwy plików**: Generowanie nazw na podstawie pól odpowiedzi API:
<recId> - id nagrania 
<callingUserPart>  -  część  user  part  adresu  SIP  URI  dla  użytkownika  dzwoniącego. 
<calledUserPart>  -  część  user  part  adresu  SIP  URI  dla  użytkownika  odbierającego.
Najczęściej numer MSISDN. Wartość jaka została otrzymana z sieci bez normalizacji  
<callDirection> - kierunek nagrywanego połączenia: MO - połączenie wychodzące, MT - 
połączenie przychodzące 
przykład nazwy plku mp3 i pliku transkypcji
recid-callingUserPart-calledUserPart-callDirection
1539595123456-223334455-226667788-MO

### 5.6 Pobieranie z Monitoringiem
- **Progress tracking**: Indywidualny postęp każdego pobieranego pliku
- **Nazwa pliku**: Wyświetlanie nazwy generowanej z recordingNumber i startTime
- **recId tracking**: Wyświetlanie aktualnie pobieranego recId nagrania
- **Ogólny postęp**: Contador "X z Y plików pobranych" (bazując na totalElements)
- **Paginacja**: Automatyczne przechodzenie przez kolejne strony API
- **Iteracyjne pobieranie**: Sekwencyjne wywołanie `/recording/{recId}` dla każdego recId
- **Retry mechanizm**: Obsługa błędów z informowaniem użytkownika
- **Real-time updates**: Aktualizacja interfejsu w czasie rzeczywistym
- **Zarządzanie plikami**: Automatyczne nazewnictwo bazujące na metadanych z API

### 5.7 Przetwarzanie
- Automatyczne rozpoznawanie formatów plików (MP3, WAV)
- Pobrane pliki z serwera API są bezpośrednio w formacie ZIP nalezy je rozpakować do formatu mp3
- Walidacja poprawności pobranych plików audio
- Obsługa różnych kodowań i bitrate'ów

### 5.8 Transkrypcja WhisperX z Diaryzacją
- **Multi-stage processing**:
  - Etap 1: Transkrypcja WhisperX
  - Etap 2: Word-level alignment
  - Etap 3: Speaker diarization (z HF Token)
- **Progress tracking**: Indywidualny postęp każdego etapu transkrypcji
- **Nazwa pliku**: Wyświetlanie nazwy aktualnie przetwarzanego pliku MP3
- **Ogólny postęp**: Contador "X z Y nagrań przetworzonych"
- **Format wyjściowy**: TXT z timestampami i oznaczonymi mówiącymi
- **Speaker identification**: Automatyczna identyfikacja SPEAKER_00, SPEAKER_01, etc.
- **Error handling**: Informowanie o plikach uszkodzonych
- **HF Token**: Automatyczne pobieranie z Google Colab Secrets

### 5.9 Konfiguracja WhisperX
- **Model**: Automatyczny wybór optymalnego modelu dla Colab
- **Batch size**: Optymalizacja dla dostępnej pamięci GPU/CPU
- **Alignment model**: Automatyczny wybór modelu alignment dla języka
- **Diarization**: Konfiguracja pyannote.audio dla speaker diarization z HF Token
- **Cache**: Lokalne przechowywanie modeli w sesji
- **Język**: Auto-detect lub możliwość wyboru przez użytkownika
- **HF Token**: Automatyczne pobieranie z Google Colab Secrets (klucz: "HF_TOKEN")

## 6. Wymagania Niefuncjonalne

### 6.1 Użyteczność
- **Prosty formularz**: Login + hasło + data + przycisk
- **Jednokierunkowy przepływ**: Wszystko dzieje się po kliknięciu jednego przycisku
- **Przejrzysty monitoring**: Wizualne wskaźniki postępu dla każdego etapu
- **Jasne komunikaty**: Informacje o stanie operacji na każdym etapie
- **Responsywny interfejs**: Real-time updates z wykorzystaniem yield w Gradio

### 6.2 Niezawodność
- **Walidacja formularza**: Sprawdzenie danych przed wywołaniem API
- **Obsługa błędów API**: Informative error messages (401, 404, 500, timeout)
- **Obsługa błędów sieciowych**: Graceful handling z informowaniem użytkownika
- **Walidacja plików**: Sprawdzenie przed przetwarzaniem
- **Szczegółowe logowanie**: Operacje dla każdego etapu
- **Recovery**: Możliwość ponownego uruchomienia procesu

### 6.3 Wydajność
- **Optymalizacja Colab**: Efektywne wykorzystanie GPU/CPU
- **Zarządzanie pamięcią**: Szczególnie podczas diaryzacji
- **Szybka inicjalizacja**: Generowanie listy dat bez opóźnień
- **Minimalne opóźnienia UI**: Responsive interface updates z Gradio

### 6.4 Bezpieczeństwo
- **Password input**: Ukrywanie hasła podczas wprowadzania (gr.Textbox(type="password"))
- **Basic Auth**: Implementacja zgodna ze standardem
- **Brak logowania credentials**: Bezpieczne zarządzanie danymi uwierzytelniającymi
- **Session management**: Bezpieczne przechowywanie w sesji Gradio

## 7. Interfejs API nagrywanie.plus.pl

### 7.1 Specyfikacja API

#### 7.1.1 Lista Nagrań
- **Endpoint**: `https://nagrywanie.plus.pl/recordingApi/recordingsPaged/`
- **Metoda**: GET
- **Autoryzacja**: Basic Authentication (username:password)
- **Content-Type**: application/json (expected response)
- **Wywołanie**: Tylko po kliknięciu przycisku "Pobierz nagrania"
- **Cel**: Pobranie paginowanej listy nagrań z recId dla wybranej daty
- **Parametry**:
  - `size`: Liczba wyników na stronę (domyślnie 10, można zwiększyć dla lepszej wydajności)
  - `page`: Numer strony (zaczynając od 0)
  - `dateFrom`: Data rozpoczęcia w formacie ISO (YYYY-MM-DDTHH:mm:ss)
  - `status`: Status nagrania (RECORDED dla pobranych nagrań)

#### 7.1.2 Pobieranie Pojedynczego Nagrania
- **Endpoint**: `https://nagrywanie.plus.pl/recordingApi/recording/{recId}`
- **Metoda**: GET
- **Autoryzacja**: Basic Authentication (username:password)
- **Parametr**: `{recId}` - ID nagrania zwrócone z listy nagrań
- **Content-Type**: audio/mpeg (expected response)
- **Cel**: Pobranie pliku audio dla konkretnego ID nagrania

### 7.2 Automatyczne Formatowanie Parametrów
- **Input**: Data z dropdown (np. "2025-07-22 (Poniedziałek)")
- **Parsing**: Wyciągnięcie daty "2025-07-22"
- **Output dla listy nagrań**: 
  - `size=100` (zwiększona wartość dla efektywności)
  - `page=0` (zawsze zaczynamy od pierwszej strony)
  - `dateFrom=2025-07-22T00:00:00`
  - `status=RECORDED` (tylko nagrane pliki)

### 7.3 Przykłady Zapytań API

#### 7.3.1 Pobranie Listy Nagrań (Automatycznie Generowane)
```bash
# Dla daty wybranej przez użytkownika i kliknięcia przycisku
curl -u 'username':'password' \
  -X GET \
  'https://nagrywanie.plus.pl/recordingApi/recordingsPaged/?size=100&page=0&dateFrom=2025-07-22T00:00:00&status=RECORDED'
```

#### 7.3.2 Pobranie Pojedynczego Nagrania
```bash
# Dla każdego ID nagrania zwróconego z listy
curl -u 'username':'password' \
  -X GET \
  'https://nagrywanie.plus.pl/recordingApi/recording/1539512345678'
```

#### 7.3.3 Proces Pobierania
1. **Krok 1**: Wywołanie API listy nagrań dla wybranej daty z parametrami paginacji
2. **Krok 2**: Parsowanie odpowiedzi i wyciągnięcie wszystkich recId z `content[]`
3. **Krok 3**: Obsługa paginacji - sprawdzenie czy `last: false` i pobieranie kolejnych stron
4. **Krok 4**: Iteracyjne pobieranie każdego nagrania używając endpoint `/recording/{recId}`
5. **Krok 5**: Zapis każdego pliku audio do folderu na Google Drive z nazwą bazującą na metadanych

### 7.4 Oczekiwane Odpowiedzi

#### 7.4.1 Lista Nagrań (Paginowana)
```json
{
  "content": [
    {
      "calledUserPart": "48000110200",
      "callingUserPart": "48500111222",
      "establishedTime": "2025-07-22T11:32:47",
      "startCopyTime": null,
      "markedForRemoval": true,
      "markedForCopy": false,
      "fileCount": 1,
      "recordingCopied": false,
      "departmentName": "d1",
      "callDirection": "MT",
      "recordingFailed": false,
      "recordingRemoved": false,
      "status": "RECORDED",
      "recId": 1539595123456,
      "recordingNumber": "48000110200",
      "compressed": true,
      "endTime": "2025-07-22T11:32:58",
      "otherNumber": "48500111222",
      "description": "abcd",
      "startTime": "2025-07-22T11:32:41",
      "length": 10120,
      "size": 20955
    },
    {
      "calledUserPart": "48500000111",
      "callingUserPart": "48607999999",
      "establishedTime": "2025-07-22T12:22:49",
      "startCopyTime": null,
      "markedForRemoval": true,
      "markedForCopy": false,
      "fileCount": 1,
      "recordingCopied": false,
      "departmentName": null,
      "callDirection": "MO",
      "recordingFailed": false,
      "recordingRemoved": false,
      "status": "RECORDED",
      "recId": 1539598654321,
      "recordingNumber": "48607999999",
      "compressed": true,
      "endTime": "2025-07-22T12:22:56",
      "otherNumber": "48500000111",
      "description": null,
      "startTime": "2025-07-22T12:22:47",
      "redirectType": 0,
      "length": 6020,
      "size": 12747
    }
  ],
  "last": true,
  "totalElements": 2,
  "totalPages": 1,
  "sort": null,
  "first": true,
  "numberOfElements": 2,
  "size": 10,
  "number": 0
}
```

**Kluczowe pola:**
- **`recId`**: Identyfikator nagrania do pobierania
- **`recordingNumber`**: Numer telefonu dla nazwy pliku
- **`startTime`**: Timestamp rozpoczęcia dla nazwy pliku
- **`length`**: Długość nagrania w milisekundach
- **`size`**: Rozmiar pliku w bajtach
- **`totalElements`**: Całkowita liczba nagrań
- **`last`**: Czy to ostatnia strona (dla paginacji)

#### 7.4.2 Pojedyncze Nagranie
- **Content-Type**: audio/mpeg lub audio/wav
- **Response**: Surowy plik audio (binary data)
- **Headers**: Content-Length, Content-Disposition z nazwą pliku

#### 7.4.3 Status Codes
- **200**: Sukces (lista nagrań lub plik audio)
- **401**: Unauthorized (nieprawidłowe credentials)
- **404**: Not found (brak nagrań dla daty lub nieistniejące ID)
- **500**: Server error

## 8. Ograniczenia i Założenia

### 8.1 Ograniczenia Colab
- Limit czasu sesji (długość przetwarzania WhisperX + diaryzacja)
- Ograniczenia pamięci GPU/RAM dla diaryzacji
- Brak stałego storage

### 8.2 Założenia
- Użytkownik ma konto Google
- **Użytkownik ma skonfigurowany HuggingFace Token w Google Colab Secrets**
- Użytkownik ma ważne credentials do API nagrywanie.plus.pl
- API nagrywanie.plus.pl jest dostępne i zwraca pliki audio przy wywołaniu
- Nagrania zawierają mowę ludzką nadającą się do diaryzacji
- Nagrania są w formacie obsługiwanym przez WhisperX

### 8.3 Zakres Dat
- **Okres**: Ostatnie 3 miesiące od daty uruchomienia aplikacji
- **Format dropdown**: YYYY-MM-DD (Dzień tygodnia)
- **Ograniczenia**: Tylko pełne dni, bez możliwości wyboru godzin

### 8.4 Wymagania WhisperX
- **HuggingFace Token**: Wymagany dla modeli diaryzacji, przechowywany w Google Colab Secrets
- **Konfiguracja Secrets**: Klucz "HF_TOKEN" w Google Colab Secrets z tokenem z HuggingFace
- **GPU Access**: Preferowane dla szybszego przetwarzania
- **Pamięć**: Minimum 8GB RAM dla diaryzacji
- **Akceptacja warunków**: Użytkownik musi zaakceptować warunki modeli Pyannote na HuggingFace

## 9. Scenariusze Użycia

### 9.1 Scenariusz Podstawowy
1. Użytkownik uruchamia aplikację w Colab
2. **Gradio generuje publiczny link dostępny dla użytkownika**
3. **Widzi formularz z polami: username, password, lista dat, przycisk**
4. **Wprowadza swoją nazwę użytkownika i hasło do nagrywanie.plus.pl**
5. **Wybiera datę z listy rozwijanej (np. "2025-07-22 (Poniedziałek)")**
6. **Klika przycisk "Pobierz nagrania"**
7. **System wywołuje API listy nagrań i wyświetla totalElements dostępnych nagrań**
8. **System parsuje odpowiedź, obsługuje paginację i wyciąga wszystkie recId do pobrania**
9. **Obserwuje postęp pobierania każdego pliku po recId z generowanymi nazwami**
9. **Śledzi postęp transkrypcji WhisperX dla każdego nagrania z diaryzacją**
10. Pliki audio i transkrypcje z diaryzacją są dostępne w folderze na Google Drive
11. **Otrzymuje komunikat o zakończeniu procesu**

### 9.2 Scenariusze Błędów
- **Niekompletny formularz**: Komunikat o konieczności wypełnienia wszystkich pól
- **Nieprawidłowe credentials**: 401 Unauthorized z wyjaśnieniem
- **Brak nagrań dla wybranej daty**: "totalElements: 0 dla daty 2025-07-22"
- **Błąd połączenia z API**: Komunikat o problemach sieciowych z sugestią ponownej próby
- **Timeout API calls**: Informacja o przekroczeniu czasu z możliwością retry
- **Nieistniejące recId nagrania**: 404 Not Found dla konkretnego recId z pominięciem i kontynuacją
- **Błąd paginacji**: Informowanie o problemach z pobieraniem kolejnych stron
- **0 nagrań dla wybranej daty**: "totalElements: 0 dla daty 2025-07-22"
- **Błąd diaryzacji**: Zapisuje transkrypcję bez speaker labels
- **Błąd HF Token**: Informuje o problemach z tokenem i konieczności konfiguracji Secrets
- **Przekroczenie limitów Colab**: Informuje użytkownika o ograniczeniach

## 10. Testowanie Aplikacji

### 10.1 Środowisko Testowe
- **Wyłącznie Google Colab**: Wszystkie testy przeprowadzane są w środowisku Google Colab
- **Brak konfiguracji lokalnej**: Użytkownik nie konfiguruje środowiska lokalnego
- **Testowanie w chmurze**: Wykorzystanie infrastruktury Google Colab do walidacji funkcjonalności

### 10.2 Zakres Testów

#### 10.2.1 Testy Jednostkowe w Colab
- **Test generatora dat**: Walidacja poprawności listy dat z ostatnich 3 miesięcy
- **Test formatowania dat**: Sprawdzenie konwersji z dropdown do formatu API
- **Test Basic Auth**: Weryfikacja kodowania credentials
- **Test parsowania API response**: Walidacja ekstrakcji recId z odpowiedzi JSON
- **Test nazewnictwa plików**: Sprawdzenie generowania nazw z metadanych

#### 10.2.2 Testy Integracyjne w Colab
- **Test połączenia z API**: Rzeczywiste wywołania endpoint'ów nagrywanie.plus.pl
- **Test paginacji**: Obsługa wielu stron wyników
- **Test pobierania plików**: Download nagrań i zapis na Google Drive
- **Test WhisperX**: Transkrypcja przykładowych plików audio
- **Test diaryzacji**: Werifikacja identyfikacji mówiących
- **Test HF Token**: Sprawdzenie konfiguracji w Colab Secrets

#### 10.2.3 Testy UI w Colab
- **Test interfejsu Gradio**: Funkcjonalność formularza i komponentów
- **Test walidacji**: Obsługa błędnych danych wejściowych
- **Test progress tracking**: Aktualizacja pasków postępu
- **Test real-time updates**: Wykorzystanie yield dla live updates
- **Test publicznego linku**: Dostępność aplikacji spoza Colab

### 10.3 Procedura Testowania

#### 10.3.1 Setup Testowy
1. **Uruchomienie nowego notebook'a Colab**
2. **Konfiguracja HF Token w Secrets**
3. **Instalacja dependencies**
4. **Montowanie Google Drive**
5. **Inicjalizacja WhisperX i modeli diaryzacji**

#### 10.3.2 Wykonanie Testów
1. **Test podstawowego przepływu**:
   - Wprowadzenie poprawnych credentials
   - Wybór daty z ostatnich 3 miesięcy
   - Kliknięcie przycisku "Pobierz nagrania"
   - Monitorowanie całego procesu od API do transkrypcji

2. **Test scenariuszy błędów**:
   - Nieprawidłowe credentials (401)
   - Brak nagrań dla wybranej daty (totalElements: 0)
   - Problemy z połączeniem sieciowym
   - Błędy w procesie diaryzacji

3. **Test wydajnościowy**:
   - Pobieranie większej liczby nagrań (>10 plików)
   - Transkrypcja długich nagrań (>10 minut)
   - Wykorzystanie pamięci GPU/CPU w Colab

#### 10.3.3 Kryteria Akceptacji Testów
- **100% testów przeprowadzanych w Colab**: Żadne testy nie są wykonywane lokalnie
- **Sukces podstawowego przepływu**: Pełny cykl od logowania do zapisania transkrypcji
- **Obsługa błędów**: Graceful handling wszystkich scenariuszy błędów
- **Performance**: Aplikacja działa stabilnie w limitach Colab
- **UI responsiveness**: Real-time updates działają poprawnie
- **Data integrity**: Poprawność nazw plików i struktury folderów

### 10.4 Dokumentacja Testów w Colab
- **Test logs**: Szczegółowe logowanie każdego testu w notebook'u
- **Screenshots**: Zrzuty ekranu interfejsu Gradio
- **Performance metrics**: Czasy wykonania i wykorzystanie zasobów
- **Error handling demos**: Dokumentacja obsługi różnych błędów
- **Success scenarios**: Przykłady pomyślnych wykonań dla różnych dat

### 10.5 Continuous Testing w Colab
- **Regularne testy**: Cotygodniowe sprawdzenie funkcjonalności
- **API monitoring**: Weryfikacja dostępności nagrywanie.plus.pl
- **Model updates**: Testowanie po aktualizacjach WhisperX
- **Colab compatibility**: Sprawdzenie po zmianach w środowisku Google Colab

## 11. Metryki Sukcesu
- **Prosty interfejs**: Formularz z 4 elementami (login + hasło + data + przycisk)
- **Jedna akcja**: Cały proces uruchamiany jednym kliknięciem przycisku
- **Intuicyjny wybór daty**: Lista z ostatnich 3 miesięcy z nazwami dni tygodnia
- **Automatyczne formatowanie**: Bezproblemowa konwersja dat do formatu API
- **Pomyślne połączenie z API**: Reliable communication z nagrywanie.plus.pl
- **Real-time monitoring**: Przejrzysty postęp dla każdego etapu
- **Pomyślna diaryzacja**: Wysokiej jakości transkrypcje z speaker identification
- **0 błędów w organizacji plików**: Poprawna struktura folderów i nazw
- **Kompletny feedback**: Użytkownik zawsze wie co się dzieje
- **Niezawodne przetwarzanie**: Obsługa różnych długości nagrań i liczby mówiących
- **Publiczny dostęp**: Możliwość udostępnienia linku innym użytkownikom
- **Bezpieczne zarządzanie tokenów**: HF Token przechowywany w Colab Secrets
- **100% testów w Colab**: Wszystkie testy przeprowadzone wyłącznie w środowisku chmurowym

## 12. Format Wyjściowy Transkrypcji

### 12.1 Struktura pliku TXT
```
[00:00:12.34 - 00:00:18.56] SPEAKER_00: Tekst wypowiedzi pierwszego mówcy.
[00:00:19.12 - 00:00:25.78] SPEAKER_01: Tekst wypowiedzi drugiego mówcy.
[00:00:26.45 - 00:00:32.10] SPEAKER_00: Kolejna wypowiedź pierwszego mówcy.
```

### 12.2 Metadane
- Precyzyjne timestampy (do setnych części sekundy)
- Automatyczna numeracja mówiących (SPEAKER_00, SPEAKER_01, ...)
- Zachowanie formatowania i interpunkcji

## 13. Specyfikacja Interfejsu Gradio

### 13.1 Layout Formularza
```
┌─────────────────────────────────────┐
│ Nazwa użytkownika: [textbox]        │
│ Hasło: [textbox type="password"]    │
│ Data: [dropdown with dates]         │
│ [Button: Pobierz nagrania]          │
│ ────────────────────────────────────│
│ Status: [textbox readonly]          │
│ Progress: [progress bar]            │
│ Logi: [textbox multiline readonly]  │
└─────────────────────────────────────┘
```

### 13.2 Komponenty Gradio
- **gr.Textbox()**: Nazwa użytkownika
- **gr.Textbox(type="password")**: Hasło
- **gr.Dropdown()**: Lista dat z ostatnich 3 miesięcy
- **gr.Button()**: Przycisk akcji
- **gr.Textbox(interactive=False)**: Status operacji
- **gr.Progress()**: Pasek postępu
- **gr.Textbox(lines=10, interactive=False)**: Logi operacji

### 13.3 Funkcja Główna
- **Dekorator**: `@gr.Interface` lub budowa z `gr.Blocks()`
- **Generator**: Użycie `yield` dla real-time updates
- **Publiczny link**: `share=True` dla dostępu spoza Colab
- **Walidacja**: Sprawdzenie wszystkich inputów przed rozpoczęciem procesu

## 14. Konfiguracja HuggingFace Token

### 14.1 Wymagania Wstępne
- **Konto HuggingFace**: Użytkownik musi mieć konto na https://huggingface.co
- **Akceptacja warunków**: Zaakceptowanie warunków użytkowania modeli Pyannote:
  - `pyannote/speaker-diarization-3.1`
  - `pyannote/segmentation-3.0`
- **Wygenerowanie tokenu**: Utworzenie Read Token w ustawieniach HuggingFace

### 14.2 Konfiguracja w Google Colab
1. **Otwarcie panelu Secrets**:
   - Kliknięcie ikony klucza w lewym panelu Colab
   - Lub przejście do menu Runtime → Manage Sessions → Secrets

2. **Dodanie nowego Secret**:
   - Nazwa klucza: `HF_TOKEN`
   - Wartość: Token z HuggingFace (format: `hf_...`)
   - Włączenie dostępu dla notebook'a

3. **Weryfikacja konfiguracji**:
   ```python
   from google.colab import userdata
   try:
       hf_token = userdata.get('HF_TOKEN')
       print("✅ HF Token skonfigurowany pomyślnie")
   except Exception as e:
       print("❌ Błąd konfiguracji HF Token:", e)
   ```

### 14.3 Bezpieczeństwo
- **Prywatność**: Token nie jest widoczny w kodzie ani logach
- **Lokalne przechowywanie**: Token dostępny tylko w danej sesji Colab
- **Automatyczne zarządzanie**: Brak konieczności manualnej obsługi w kodzie aplikacji

### 14.4 Troubleshooting
- **Błąd dostępu**: Sprawdzenie czy modele zostały zaakceptowane na HuggingFace
- **Nieprawidłowy token**: Wygenerowanie nowego tokenu Read w ustawieniach HF
- **Brak dostępu**: Upewnienie się że Secret jest włączony dla notebook'a

## 15. Szczegóły Implementacyjne

### 15.1 Error Handling w Detalach
- **API Timeouts**: Automatyczny retry z exponential backoff
- **Network errors**: Graceful degradation z informowaniem użytkownika
- **Uszkodzone pliki audio**: Pomija z logiem błędu, kontynuuje przetwarzanie

### 15.2 Real-time Updates
- **Yield progress**: Aktualizacja paska postępu dla każdego pliku
- **Yield status**: Informacje o aktualnym etapie operacji
- **Yield logs**: Szczegółowe logi dla każdej operacji
- **Error handling**: Graceful updates w przypadku błędów

### 15.3 Optymalizacje Wydajności
- **Batch processing**: Grupowanie operacji dla lepszej wydajności
- **Memory management**: Czyszczenie pamięci po każdym pliku
- **GPU utilization**: Optymalne wykorzystanie dostępnego GPU w Colab
- **Concurrent downloads**: Równoległe pobieranie plików (jeśli możliwe)

### 15.4 Logging i Monitoring
- **Structured logs**: JSON format dla łatwiejszego parsowania
- **Progress tracking**: Szczegółowe metryki każdego etapu
- **Error categorization**: Klasyfikacja błędów według typu
- **Performance metrics**: Czasy wykonania każdej operacji

## 16. Maintenance i Updates

### 16.1 Aktualizacje Modeli
- **WhisperX updates**: Procedura aktualizacji modelu transkrypcji
- **Pyannote updates**: Aktualizacja modeli diaryzacji
- **Compatibility testing**: Testowanie po każdej aktualizacji

### 16.2 API Changes
- **Monitoring**: Śledzenie zmian w API nagrywanie.plus.pl
- **Backward compatibility**: Obsługa starszych wersji API
- **Error handling updates**: Adaptacja do nowych kodów błędów

### 16.3 Colab Environment
- **Python version updates**: Kompatybilność z nowymi wersjami Python
- **Library updates**: Aktualizacja dependencies
- **Resource limits**: Adaptacja do zmian w limitach Colab