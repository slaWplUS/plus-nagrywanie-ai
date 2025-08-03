#######################
## KOMÓRKA 2 ##
#######################

# KOMÓRKA 2: Importy i Konfiguracja Globalna
# Ta komórka centralizuje wszystkie importy dla łatwiejszego zarządzania zależnościami

print("📦 Ładuję moduły i biblioteki...")

# =============================================================================
# IMPORTY MODUŁÓW STANDARDOWYCH
# =============================================================================
import os
import json
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

print("✅ Moduły standardowe załadowane")

# =============================================================================
# IMPORTY BIBLIOTEK ZEWNĘTRZNYCH
# =============================================================================
import requests
from requests.auth import HTTPBasicAuth
import gradio as gr
import torch
import torchaudio

print("✅ Biblioteki zewnętrzne załadowane")

# =============================================================================
# IMPORTY WHISPERX I PYANNOTE
# =============================================================================
try:
    import whisperx
    print("✅ WhisperX załadowany pomyślnie")
except ImportError as e:
    print(f"❌ Błąd ładowania WhisperX: {e}")
    print("   Sprawdź czy komórka 1 została uruchomiona pomyślnie")

try:
    from pyannote.audio import Pipeline
    print("✅ Pyannote.audio załadowany pomyślnie")
except ImportError as e:
    print(f"❌ Błąd ładowania pyannote.audio: {e}")
    print("   Sprawdź czy komórka 1 została uruchomiona pomyślnie")

# =============================================================================
# IMPORTY GOOGLE COLAB
# =============================================================================
try:
    from google.colab import drive, userdata
    print("✅ Moduły Google Colab załadowane")
except ImportError:
    print("⚠️ Ostrzeżenie: Moduły Google Colab niedostępne")
    print("   To normalne jeśli uruchamiasz kod poza Google Colab")

# =============================================================================
# KONFIGURACJA GLOBALNA
# =============================================================================

# Ustawienia API
API_BASE_URL = "https://nagrywanie.plus.pl/recordingApi"
API_TIMEOUT = 30  # sekundy
MAX_RETRIES = 3

# Ustawienia WhisperX (zgodnie z referencyjnym skryptem i dokumentacją)
WHISPER_MODEL = "large-v2"  # Model zgodny z referencyjnym skryptem i dokumentacją TechStack
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
COMPUTE_TYPE = "float32" if torch.cuda.is_available() else "int8"  # float32 dla lepszej wydajności GPU
BATCH_SIZE = 16  # Rozmiar batcha - zgodnie z referencyjnym skryptem (redukcja przy ograniczeniach pamięci GPU)

# Ustawienia paginacji API
DEFAULT_PAGE_SIZE = 100  # Zwiększona wartość dla efektywności

# Ścieżki
DRIVE_MOUNT_POINT = "/content/drive"
MYDRIVE_PATH = "/content/drive/MyDrive"

print(f"🖥️ Urządzenie obliczeniowe: {DEVICE}")
print(f"🔢 Typ obliczeń: {COMPUTE_TYPE}")
print(f"🎤 Model Whisper: {WHISPER_MODEL}")
print(f"📦 Batch size: {BATCH_SIZE}")

# Dodatkowe szczegóły środowiska
if torch.cuda.is_available():
    gpu_name = torch.cuda.get_device_name(0)
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f"🚀 GPU: {gpu_name}")
    print(f"💾 Pamięć GPU: {gpu_memory:.1f} GB")
else:
    print("💻 Używane będą obliczenia CPU")

print(f"🌐 API Endpoint: {API_BASE_URL}")
print(f"⏱️ Timeout API: {API_TIMEOUT}s")
print(f"🔄 Max retries: {MAX_RETRIES}")
print(f"📄 Rozmiar strony API: {DEFAULT_PAGE_SIZE}")

# Weryfikacja wersji kluczowych bibliotek
try:
    import torch
    print(f"🔥 PyTorch: {torch.__version__}")
except:
    pass

try:
    import whisperx
    print(f"🎙️ WhisperX: załadowany pomyślnie")
except:
    print("❌ WhisperX: nie załadowany")

try:
    import gradio as gr
    print(f"🎨 Gradio: {gr.__version__}")
except:
    pass

print()
print("=" * 50)
print("✅ KOMÓRKA 2 ZAKOŃCZONA POMYŚLNIE")
print("=" * 50)
print("📊 Status: Wszystkie moduły i konfiguracja gotowe")
print("🎯 Następny krok: Inicjalizacja środowiska")
print("▶️ Uruchom komórkę 3, aby zamontować Google Drive i skonfigurować HF Token") 