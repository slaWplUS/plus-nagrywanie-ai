# plus-nagrywanie-ai
Plus Nagrywanie Rozmów + AI: Automatyczna Transkrypcja i Diaryzacja


# 🎙️ Plus Nagrywanie Rozmów + AI: Automatyczna Transkrypcja i Diaryzacja

**Futurystyczne narzędzie do analizy nagrań audio, które łączy moc sztucznej inteligencji (WhisperX, PyAnnote) z wygodą Google Colab i usługą Plus Nagrywanie Rozmów.**

---

## 🛠️ Funkcjonalności

- **📥 Pobieranie nagrań** z API [Plus Nagrywanie Rozmów](https://nagrywanie.plus.pl/).
- **🎤 Transkrypcja audio** za pomocą modelu WhisperX.
- **👥 Diaryzacja mówców** – automatyczne przypisywanie fragmentów rozmowy do konkretnych osób.
- **📁 Organizacja plików** – automatyczne zapisywanie nagrań i transkrypcji na Google Drive.
- **🔄 Dynamiczne przetwarzanie** – od pobrania nagrań po gotowe transkrypcje w jednym procesie.

---

## 🚀 Jak uruchomić projekt?

### 1. Wymagania wstępne
- Konto Google (do korzystania z Google Colab i Google Drive).
- Konto na [Hugging Face](https://huggingface.co/) z wygenerowanym tokenem API (format: `hf_...`).
- Akceptacja licencji modeli:
  - [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
  - [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
- Dane logowania do API Plus Nagrywanie Rozmów.

### 2. Instrukcja krok po kroku
1. **Sklonuj repozytorium**:
   ```bash
   git clone https://github.com/slaWplUS/plus-nagrywanie-ai.git
   cd plus-nagrywanie-ai
   ```
2. **Otwórz projekt w Google Colab**:
   - Prześlij pliki do Colaba lub otwórz bezpośrednio z repozytorium.
3. **Uruchom komórki w kolejności**:
   - **Komórka 1**: Instalacja zależności.
   - **Komórka 2**: Importy i konfiguracja globalna.
   - **Komórka 3**: Montowanie Google Drive i konfiguracja tokenu Hugging Face.
   - **Komórka 4-6**: Funkcje API, przetwarzanie audio i transkrypcja.
   - **Komórka 7**: Uruchomienie interfejsu Gradio.
4. **Wprowadź dane logowania i tokeny**:
   - Dodaj `HF_TOKEN` w sekcji "Secrets" w Colabie.
   - Wprowadź dane API w interfejsie Gradio.
---

## 📋 Wymagania techniczne

- **Google Colab** z dostępem do GPU (zalecane).
- **Biblioteki**:
  - `whisperx`
  - `gradio`
  - `torch`
  - `torchaudio`
  - `requests`
  - `pyannote.audio`
- **Dostęp do internetu** w Colabie.

---

## 🖥️ Technologie użyte w projekcie

- **WhisperX** – transkrypcja audio z precyzyjnym dopasowaniem czasowym.
- **PyAnnote** – diaryzacja mówców.
- **Gradio** – interfejs użytkownika.
- **Google Colab** – środowisko do uruchamiania kodu.
- **Plus Nagrywanie Rozmów** – źródło nagrań audio.

---

## 📂 Struktura projektu

- `cell_1_installation.py` – instalacja zależności.
- `cell_2_imports.py` – importy i konfiguracja globalna.
- `cell_3_environment.py` – montowanie Google Drive i konfiguracja tokenów.
- `cell_4_api_functions.py` – funkcje do komunikacji z API.
- `cell_5_fixed.py` – funkcje przetwarzania audio i transkrypcji.
- `cell_6_main_process.py` – główna logika aplikacji.
- `cell_7_gradio_app.py` – interfejs użytkownika.

---
**Zautomatyzuj nudne rzeczy i zyskaj więcej czasu na kawę! ☕**
