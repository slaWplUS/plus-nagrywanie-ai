########################################################
# KOMÓRKA 1: Instalacja Zależności
########################################################
# Ta komórka instaluje wszystkie biblioteki niezbędne do działania aplikacji
# Uruchamiana jako pierwsza. Bez flagi -q dla pełnej widoczności procesu instalacji.

print("🔄 Rozpoczynam instalację zależności...")
print("📦 Instaluję WhisperX, Gradio, PyTorch, PyAnnote i inne biblioteki...")

# Instalacja wszystkich wymaganych pakietów
# WhisperX - do transkrypcji i diaryzacji
# Gradio - do interfejsu użytkownika  
# PyTorch + torchaudio - backend dla modeli AI
# requests - do komunikacji z API
# pyannote.audio - do diaryzacji mówiących (wersja kompatybilna z WhisperX)

get_ipython().system('pip install "whisperx[dev] @ git+https://github.com/m-bain/whisperx.git" gradio torch torchaudio requests')

print("ℹ️ Uwaga: pyannote.audio zostanie automatycznie zainstalowane jako zależność WhisperX")
print("   w kompatybilnej wersji (>=3.3.2)")

print("✅ Instalacja zakończona pomyślnie!")
print("▶️ Przejdź do następnej komórki, aby skonfigurować środowisko.") 