#######################
## KOMÓRKA 3 ##
#######################

# KOMÓRKA 3: Inicjalizacja Środowiska (Dysk i Sekrety)
# Ta komórka wykonuje kluczowe operacje konfiguracyjne:
# - Montowanie Google Drive
# - Weryfikacja dostępu do tokenu Hugging Face

print("🚀 Inicjalizuję środowisko...")
print("=" * 50)

# =============================================================================
# MONTOWANIE GOOGLE DRIVE
# =============================================================================
print("📂 Montowanie Google Drive...")

try:
    from google.colab import drive
    
    # Montowanie dysku
    drive.mount('/content/drive')
    
    # Weryfikacja dostępu
    import os
    if os.path.exists('/content/drive/MyDrive'):
        print("✅ Google Drive zamontowany pomyślnie")
        print(f"📁 Ścieżka: /content/drive/MyDrive")
        
        # Sprawdzenie miejsca na dysku
        import shutil
        total, used, free = shutil.disk_usage('/content/drive/MyDrive')
        free_gb = free // (1024**3)
        total_gb = total // (1024**3)
        print(f"💾 Dostępne miejsce: {free_gb} GB / {total_gb} GB")
        
    else:
        print("❌ Błąd: Nie można uzyskać dostępu do /content/drive/MyDrive")
        print("   Sprawdź czy Google Drive został poprawnie zamontowany")
        
except ImportError:
    print("⚠️ Ostrzeżenie: Moduł google.colab.drive niedostępny")
    print("   To normalne jeśli uruchamiasz kod poza Google Colab")
    
except Exception as e:
    print(f"❌ Błąd montowania Google Drive: {e}")
    print("   Spróbuj uruchomić komórkę ponownie")

print()

# =============================================================================
# WERYFIKACJA HUGGING FACE TOKEN
# =============================================================================
print("🔑 Weryfikacja Hugging Face Token...")

try:
    from google.colab import userdata
    
    # Próba pobrania tokenu
    hf_token = userdata.get('HF_TOKEN')
    
    if hf_token:
        # Sprawdzenie czy token ma poprawny format
        if hf_token.startswith('hf_'):
            print("✅ HF_TOKEN skonfigurowany pomyślnie")
            print(f"🔐 Token format: {hf_token[:8]}..." + "*" * (len(hf_token) - 8))
            print("✅ Token ma poprawny format (hf_...)")
        else:
            print("⚠️ Ostrzeżenie: Token może mieć niepoprawny format")
            print("   Sprawdź czy token zaczyna się od 'hf_'")
    else:
        print("❌ HF_TOKEN nie został znaleziony!")
        print()
        print("🔧 INSTRUKCJE KONFIGURACJI HF_TOKEN:")
        print("1. Przejdź na https://huggingface.co/settings/tokens")
        print("2. Utwórz nowy token (Read access wystarczy)")
        print("3. Skopiuj token (format: hf_...)")
        print("4. W Google Colab:")
        print("   - Kliknij ikonę klucza 🔑 w lewym panelu")
        print("   - Lub idź do Runtime → Manage Sessions → Secrets")
        print("5. Dodaj nowy secret:")
        print("   - Nazwa: HF_TOKEN")
        print("   - Wartość: Twój token z HuggingFace")
        print("   - Włącz dostęp dla tego notebooka")
        print("6. Uruchom tę komórkę ponownie")
        print()
        print("⚠️ WAŻNE: Musisz też zaakceptować warunki modeli:")
        print("   - https://huggingface.co/pyannote/speaker-diarization-3.1")
        print("   - https://huggingface.co/pyannote/segmentation-3.0")
        
except ImportError:
    print("⚠️ Ostrzeżenie: Moduł google.colab.userdata niedostępny")
    print("   To normalne jeśli uruchamiasz kod poza Google Colab")
    
except Exception as e:
    print(f"❌ Błąd dostępu do HF_TOKEN: {e}")

print()

# =============================================================================
# UTWORZENIE FUNKCJI POMOCNICZEJ DO SPRAWDZANIA ŚRODOWISKA
# =============================================================================

def check_environment():
    """Sprawdza czy środowisko jest poprawnie skonfigurowane"""
    issues = []
    
    # Sprawdzenie Google Drive
    if not os.path.exists('/content/drive/MyDrive'):
        issues.append("Google Drive nie jest zamontowany")
    
    # Sprawdzenie HF Token
    try:
        from google.colab import userdata
        hf_token = userdata.get('HF_TOKEN')
        if not hf_token:
            issues.append("HF_TOKEN nie jest skonfigurowany")
        elif not hf_token.startswith('hf_'):
            issues.append("HF_TOKEN ma niepoprawny format")
    except:
        issues.append("Nie można sprawdzić HF_TOKEN")
    
    return issues

# Sprawdzenie środowiska
print("🔍 Sprawdzanie gotowości środowiska...")
environment_issues = check_environment()

if not environment_issues:
    print("✅ Środowisko jest gotowe!")
    print("📊 Status: Wszystkie komponenty skonfigurowane poprawnie")
    print()
    print("=" * 50)
    print("✅ KOMÓRKA 3 ZAKOŃCZONA POMYŚLNIE")
    print("=" * 50)
    print("🎯 Następny krok: Definicje funkcji API i zarządzania plikami")
    print("▶️ Uruchom komórkę 4, aby zdefiniować funkcje komunikacji z API")
else:
    print("⚠️ Wykryto problemy z konfiguracją:")
    for issue in environment_issues:
        print(f"   - {issue}")
    print()
    print("🔧 Rozwiąż powyższe problemy przed przejściem do następnej komórki")
    print("💡 Możesz uruchomić tę komórkę ponownie po naprawieniu problemów")

print()
print("📝 Uwaga: Ta komórka może wymagać autoryzacji Google Drive")
print("   Postępuj zgodnie z instrukcjami na ekranie") 