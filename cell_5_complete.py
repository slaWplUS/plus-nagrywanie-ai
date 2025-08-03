#######################
## KOMÓRKA 5 ##
#######################

# KOMÓRKA 5: DEFINICJE - Funkcje Przetwarzania Audio (WhisperX)
# Ta komórka izoluje DEFINICJE funkcji związanych z przetwarzaniem AI.
# Uruchomienie tej komórki nie wywołuje żadnej z tych funkcji,
# a jedynie udostępnia je w pamięci notatnika.
# 
# ZALEŻNOŚCI: Wymaga uruchomienia komórki 2 (zmienne globalne: DEVICE, COMPUTE_TYPE, etc.)

print("🎙️ Definiuję funkcje przetwarzania audio WhisperX...")
print("=" * 60)

# =============================================================================
# INICJALIZACJA MODELI WHISPERX
# =============================================================================

def initialize_models(hf_token):
    """
    Inicjalizuje wszystkie modele potrzebne do transkrypcji i diaryzacji.
    
    Args:
        hf_token (str): Token HuggingFace do modeli diaryzacji
    
    Returns:
        dict: Słownik z załadowanymi modelami lub None w przypadku błędu
    """
    try:
        import whisperx
        from google.colab import userdata
        
        print("🚀 Inicjalizacja modeli WhisperX...")
        print("=" * 40)
        
        models = {}
        
        # =================================================================
        # 1. ŁADOWANIE MODELU WHISPER
        # =================================================================
        print(f"📡 Ładowanie modelu Whisper: {WHISPER_MODEL}")
        print(f"🖥️ Urządzenie: {DEVICE}")
        print(f"🔢 Typ obliczeń: {COMPUTE_TYPE}")
        
        try:
            whisper_model = whisperx.load_model(
                WHISPER_MODEL, 
                device=DEVICE, 
                compute_type=COMPUTE_TYPE
                # Brak language parameter - auto-detekcja języka
                # Obsługuje polski, angielski i inne języki automatycznie
            )
            models['whisper'] = whisper_model
            print("✅ Model Whisper załadowany pomyślnie")
            
        except Exception as e:
            print(f"❌ Błąd ładowania modelu Whisper: {e}")
            return None
        
        # =================================================================
        # 2. ŁADOWANIE MODELU ALIGNMENT
        # =================================================================
        print("🎯 Ładowanie modelu alignment...")
        
        try:
            # Automatyczny wybór modelu alignment dla języka polskiego
            alignment_model, metadata = whisperx.load_align_model(
                language_code="pl", 
                device=DEVICE
            )
            models['alignment'] = alignment_model
            models['alignment_metadata'] = metadata
            print("✅ Model alignment załadowany pomyślnie")
            
        except Exception as e:
            print(f"❌ Błąd ładowania modelu alignment: {e}")
            print("⚠️ Kontynuacja bez alignmentu - timestampy mogą być mniej precyzyjne")
            models['alignment'] = None
            models['alignment_metadata'] = None
        
        # =================================================================
        # 3. ŁADOWANIE MODELU DIARYZACJI (POPRAWIONE)
        # =================================================================
        print("👥 Ładowanie modelu diaryzacji...")
        
        # Wyłączenie TF32 dla stabilności PyAnnote (zgodnie z GitHub Issue #1370)
        print("🔧 Wyłączanie TensorFloat-32 dla stabilności diaryzacji...")
        import torch
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        print("✅ TF32 wyłączone - zwiększona stabilność PyAnnote")

        try:
            if not hf_token:
                print("❌ Brak HF_TOKEN - diaryzacja niedostępna")
                models['diarization'] = None
            else:
                # Załadowanie modelu speaker diarization zgodnie z referencyjnym skryptem
                diarization_model = whisperx.diarize.DiarizationPipeline(
                    use_auth_token=hf_token, 
                    device=DEVICE
                )
                models['diarization'] = diarization_model
                print("✅ Model diaryzacji załadowany pomyślnie")
                
        except Exception as e:
            print(f"❌ Błąd ładowania modelu diaryzacji: {e}")
            print("💡 Sprawdź czy:")
            print("   - HF_TOKEN jest poprawny")
            print("   - Zaakceptowałeś warunki modeli pyannote na HuggingFace")
            models['diarization'] = None
        
        # =================================================================
        # PODSUMOWANIE ZAŁADOWANYCH MODELI
        # =================================================================
        print()
        print("📊 PODSUMOWANIE ZAŁADOWANYCH MODELI:")
        print(f"   🎤 Whisper: {'✅' if models.get('whisper') else '❌'}")
        print(f"   🎯 Alignment: {'✅' if models.get('alignment') else '❌'}")
        print(f"   👥 Diarization: {'✅' if models.get('diarization') else '❌'}")
        
        # Sprawdzenie dostępnej pamięci GPU
        if DEVICE == "cuda":
            try:
                import torch
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                allocated = torch.cuda.memory_allocated(0) / 1024**3
                print(f"   💾 GPU Memory: {allocated:.1f} / {gpu_memory:.1f} GB używane")
            except:
                pass
        
        print("✅ Inicjalizacja modeli zakończona")
        return models
        
    except Exception as e:
        print(f"❌ Krytyczny błąd inicjalizacji modeli: {e}")
        return None


# =============================================================================
# PRZETWARZANIE PLIKÓW AUDIO
# =============================================================================

def process_audio_file(audio_path, models):
    """
    Przetwarza pojedynczy plik audio przez WhisperX z pełnym pipeline.
    
    Args:
        audio_path (str): Ścieżka do pliku audio
        models (dict): Słownik z załadowanymi modelami
    
    Returns:
        dict: Dane transkrypcji z diaryzacją lub None w przypadku błędu
    """
    try:
        import whisperx
        from pathlib import Path
        
        filename = Path(audio_path).name
        print(f"🎵 Przetwarzanie: {filename}")
        print("=" * 50)
        
        # Sprawdzenie czy plik istnieje
        if not Path(audio_path).exists():
            print(f"❌ Plik nie istnieje: {audio_path}")
            return None
        
        # Sprawdzenie czy modele są załadowane
        if not models or not models.get('whisper'):
            print("❌ Model Whisper nie jest załadowany")
            return None
        
        # =================================================================
        # ETAP 1: TRANSKRYPCJA WHISPER
        # =================================================================
        print("🎤 Etap 1/3: Transkrypcja Whisper...")
        
        try:
            # Załadowanie pliku audio
            audio = whisperx.load_audio(audio_path)
            
            # Transkrypcja - zgodnie z referencyjnym skryptem
            result = models['whisper'].transcribe(
                audio, 
                batch_size=BATCH_SIZE  # Używa globalnej konfiguracji z komórki 2
            )
            
            print(f"✅ Transkrypcja zakończona: {len(result.get('segments', []))} segmentów")
            
        except Exception as e:
            print(f"❌ Błąd transkrypcji: {e}")
            return None
        
        # =================================================================
        # ETAP 2: WORD-LEVEL ALIGNMENT
        # =================================================================
        print("🎯 Etap 2/3: Word-level alignment...")
        
        try:
            if models.get('alignment') and models.get('alignment_metadata'):
                # Precyzyjne wyrównanie timestampów
                result = whisperx.align(
                    result['segments'], 
                    models['alignment'], 
                    models['alignment_metadata'], 
                    audio, 
                    DEVICE, 
                    return_char_alignments=False
                )
                print("✅ Alignment zakończony - precyzyjne timestampy")
            else:
                print("⚠️ Alignment pominięty - używane surowe timestampy")
                
        except Exception as e:
            print(f"⚠️ Błąd alignment: {e}")
            print("   Kontynuacja z surowymi timestampami...")
        
        # =================================================================
        # ETAP 3: SPEAKER DIARIZATION (POPRAWIONE)
        # =================================================================
        print("👥 Etap 3/3: Speaker diarization...")
        
        try:
            if models.get('diarization'):
                # Diaryzacja zgodnie z referencyjnym skryptem WhisperX
                print("🔄 Uruchamianie diaryzacji...")
                
                # Wywołanie modelu diaryzacji - z ograniczeniem do 2 mówców
                diarize_segments = models['diarization'](audio, min_speakers=1, max_speakers=3)
                
                # Przypisanie speakerów do segmentów - metoda WhisperX
                result = whisperx.assign_word_speakers(diarize_segments, result)
                
                # Zliczenie unikatowych speakerów
                speakers = set()
                for segment in result.get('segments', []):
                    if 'speaker' in segment:
                        speakers.add(segment['speaker'])
                
                print(f"✅ Diaryzacja zakończona: {len(speakers)} mówiących")
                print(f"   Identyfikowani mówcy: {', '.join(sorted(speakers))}")
                
            else:
                print("⚠️ Diaryzacja pominięta - brak modelu")
                # Dodanie domyślnego speakera
                for segment in result.get('segments', []):
                    segment['speaker'] = 'SPEAKER_00'
                
        except Exception as e:
            print(f"⚠️ Błąd diaryzacji: {e}")
            print("   Przypisywanie domyślnego speakera...")
            # Fallback - jeden speaker
            for segment in result.get('segments', []):
                segment['speaker'] = 'SPEAKER_00'
        
        # =================================================================
        # FINALIZACJA I STATYSTYKI
        # =================================================================
        
        # Obliczenie statystyk
        total_segments = len(result.get('segments', []))
        total_duration = 0
        word_count = 0
        
        for segment in result.get('segments', []):
            if 'end' in segment and 'start' in segment:
                total_duration += segment['end'] - segment['start']
            if 'text' in segment:
                word_count += len(segment['text'].split())
        
        print()
        print("📊 STATYSTYKI PRZETWARZANIA:")
        print(f"   ⏱️ Całkowity czas: {total_duration:.1f}s")
        print(f"   📝 Segmentów: {total_segments}")
        print(f"   🔤 Słów: {word_count}")
        print(f"   📄 Średnio słów/segment: {word_count/max(total_segments,1):.1f}")
        
        print(f"✅ Przetwarzanie {filename} zakończone pomyślnie")
        return result
        
    except Exception as e:
        print(f"❌ Nieoczekiwany błąd przetwarzania {audio_path}: {e}")
        return None


# =============================================================================
# FUNKCJE POMOCNICZE AUDIO (POPRAWIONE)
# =============================================================================

def validate_audio_file(audio_path):
    """
    Sprawdza czy plik audio jest prawidłowy i może być przetworzony.
    Obsługuje niestandardowe parametry MP3 (16kHz, 32kbps).
    """
    try:
        from pathlib import Path
        import torchaudio
        
        path = Path(audio_path)
        
        # Sprawdzenie istnienia pliku
        if not path.exists():
            print(f"❌ Plik nie istnieje: {audio_path}")
            return False
        
        # Sprawdzenie rozszerzenia
        valid_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.ogg'}
        if path.suffix.lower() not in valid_extensions:
            print(f"⚠️ Nieobsługiwane rozszerzenie: {path.suffix}")
            return False
        
        # Sprawdzenie rozmiaru pliku
        file_size = path.stat().st_size
        if file_size == 0:
            print(f"❌ Plik jest pusty: {audio_path}")
            return False
        
        # Próba załadowania pliku audio - pierwsze podejście przez WhisperX
        try:
            import whisperx
            # WhisperX loader jest bardziej tolerancyjny dla niestandardowych MP3
            audio_data = whisperx.load_audio(audio_path)
            
            # Sprawdzenie minimalnej długości (16kHz * 0.1s = 1600 sampli)
            if len(audio_data) < 1600:
                print(f"❌ Plik zbyt krótki: {len(audio_data)} sampli")
                return False
            
            duration = len(audio_data) / 16000  # WhisperX normalizuje do 16kHz
            print(f"✅ Plik audio prawidłowy: {duration:.1f}s, 16kHz (WhisperX)")
            return True
            
        except Exception as whisperx_error:
            print(f"⚠️ WhisperX loader błąd: {whisperx_error}")
            
            # Fallback: torchaudio
            try:
                waveform, sample_rate = torchaudio.load(audio_path)
                duration = waveform.shape[1] / sample_rate
                
                if duration < 0.1:
                    print(f"❌ Plik zbyt krótki: {duration:.2f}s")
                    return False
                
                print(f"✅ Plik audio prawidłowy: {duration:.1f}s, {sample_rate}Hz (TorchAudio)")
                return True
                
            except Exception as torchaudio_error:
                print(f"❌ TorchAudio błąd: {torchaudio_error}")
                print(f"💡 Sprawdź format pliku: {audio_path}")
                return False
        
    except Exception as e:
        print(f"❌ Błąd walidacji pliku {audio_path}: {e}")
        return False


def cleanup_audio_processing():
    """
    Czyszczenie pamięci po przetwarzaniu audio.
    """
    try:
        import torch
        import gc
        
        # Garbage collection
        gc.collect()
        
        # Czyszczenie cache GPU
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            print("🧹 Wyczyszczono pamięć GPU")
        
        print("🧹 Cleanup zakończony")
        
    except Exception as e:
        print(f"⚠️ Błąd cleanup: {e}")


print()
print("=" * 60)
print("✅ KOMÓRKA 5 - DEFINICJE FUNKCJI WHISPERX ZAKOŃCZONA")
print("=" * 60)
print("📋 Zdefiniowane funkcje:")
print("   🚀 initialize_models() - inicjalizacja WhisperX + diaryzacja")
print("   🎵 process_audio_file() - pełny pipeline transkrypcji")
print("   ✅ validate_audio_file() - walidacja plików audio")
print("   🧹 cleanup_audio_processing() - czyszczenie pamięci")
print()
print("🎯 Następny krok: Główna logika aplikacji (orkiestrator)")
print("▶️ Uruchom komórkę 6, aby zdefiniować funkcję main_process()") 