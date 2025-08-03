#######################
## KOMÓRKA 6 ##
#######################

# KOMÓRKA 6: DEFINICJA - Główna Logika Aplikacji (Orkiestrator)
# Ta komórka zawiera DEFINICJĘ jednej, głównej funkcji main_process,
# która łączy wszystkie wcześniej zdefiniowane komponenty.
# Ta funkcja zostanie wywołana dopiero przez interfejs Gradio.

print("🎯 Definiuję główną logikę aplikacji...")
print("=" * 60)

# =============================================================================
# GŁÓWNA FUNKCJA ORKIESTRUJĄCA
# =============================================================================

def main_process(username, password, selected_date, progress=None):
    """
    Główna funkcja orkiestrująca cały proces pobierania i transkrypcji nagrań.
    
    Args:
        username (str): Nazwa użytkownika API
        password (str): Hasło API  
        selected_date (str): Wybrana data w formacie "YYYY-MM-DD (Dzień tygodnia)"
        progress (gr.Progress): Obiekt postępu Gradio
    
    Yields:
        tuple: (status_text, progress_value, logs_text) dla aktualizacji UI
    """
    
    try:
        # =================================================================
        # INICJALIZACJA I WALIDACJA
        # =================================================================
        
        yield ("🔍 Walidacja danych wejściowych...", 0, "Rozpoczynanie procesu...\n")
        
        # Sprawdzenie czy wszystkie pola są wypełnione
        if not username or not password or not selected_date:
            error_msg = "❌ Błąd: Wszystkie pola muszą być wypełnione"
            yield (error_msg, 0, error_msg + "\n")
            return
        
        logs = f"📋 Parametry:\n"
        logs += f"   👤 Użytkownik: {username}\n"
        logs += f"   📅 Data: {selected_date}\n"
        logs += f"   🔐 Hasło: {'*' * len(password)}\n\n"
        
        yield ("✅ Walidacja zakończona", 5, logs)
        
        # =================================================================
        # INICJALIZACJA MODELI WHISPERX
        # =================================================================
        
        yield ("🚀 Inicjalizacja modeli WhisperX...", 10, logs + "🤖 Ładowanie modeli AI...\n")
        
        try:
            from google.colab import userdata
            hf_token = userdata.get('HF_TOKEN')
            
            models = initialize_models(hf_token)
            
            if not models:
                error_msg = "❌ Błąd inicjalizacji modeli WhisperX"
                yield (error_msg, 10, logs + error_msg + "\n")
                return
                
            logs += "✅ Modele WhisperX załadowane pomyślnie\n"
            logs += f"   🎤 Whisper: {'✅' if models.get('whisper') else '❌'}\n"
            logs += f"   🎯 Alignment: {'✅' if models.get('alignment') else '❌'}\n"
            logs += f"   👥 Diarization: {'✅' if models.get('diarization') else '❌'}\n\n"
            
        except Exception as e:
            error_msg = f"❌ Błąd inicjalizacji modeli: {e}"
            yield (error_msg, 10, logs + error_msg + "\n")
            return
        
        yield ("✅ Modele WhisperX gotowe", 15, logs)
        
        # =================================================================
        # POBIERANIE LISTY NAGRAŃ Z API
        # =================================================================
        
        yield ("📡 Pobieranie listy nagrań z API...", 20, logs + "🌐 Łączenie z nagrywanie.plus.pl...\n")
        
        recordings_list, total_elements = get_recordings_list(username, password, selected_date)
        
        if total_elements == 0:
            info_msg = f"ℹ️ Brak nagrań dla daty {selected_date.split()[0]}"
            yield (info_msg, 100, logs + info_msg + "\n✅ Proces zakończony")
            return
        
        logs += f"📊 Znaleziono {total_elements} nagrań do pobrania\n\n"
        yield (f"📊 Znaleziono {total_elements} nagrań", 25, logs)
        
        # =================================================================
        # UTWORZENIE KATALOGU DOCELOWEGO
        # =================================================================
        
        yield ("📁 Tworzenie katalogu docelowego...", 30, logs + "📂 Konfiguracja folderu...\n")
        
        target_directory = create_target_directory(selected_date)
        if not target_directory:
            error_msg = "❌ Błąd tworzenia katalogu docelowego"
            yield (error_msg, 30, logs + error_msg + "\n")
            return
        
        logs += f"📁 Katalog utworzony: {target_directory}\n\n"
        yield ("✅ Katalog gotowy", 35, logs)
        
        # =================================================================
        # POBIERANIE PLIKÓW AUDIO
        # =================================================================
        
        yield ("📥 Rozpoczynam pobieranie nagrań...", 40, logs + "🎵 Pobieranie plików audio...\n")
        
        downloaded_files = []
        failed_downloads = []
        
        # Utworzenie sesji HTTP z autoryzacją
        import requests
        from requests.auth import HTTPBasicAuth
        
        session = requests.Session()
        session.auth = HTTPBasicAuth(username, password)
        
        # Pętla pobierania
        for i, recording in enumerate(recordings_list):
            recId = recording.get('recId')
            
            # Generowanie nazwy pliku dla pobierania (może być ZIP)
            filename_base = generate_filename_base(recording)
            file_path = os.path.join(target_directory, f"{filename_base}.mp3")
            
            # Aktualizacja postępu
            download_progress = 40 + (i / total_elements) * 30  # 40-70%
            status_msg = f"📥 Pobieranie {i+1}/{total_elements}: {recId}"
            
            current_logs = logs + f"📥 Pobieranie nagrania {i+1}/{total_elements}\n"
            current_logs += f"   🎵 RecID: {recId}\n"
            current_logs += f"   📄 Plik: {filename_base}.mp3\n"
            
            yield (status_msg, download_progress, current_logs)
            
            # Pobieranie pliku
            success = download_recording(session, recId, file_path)
            
            if success:
                downloaded_files.append({
                    'path': file_path,
                    'filename_base': filename_base,
                    'metadata': recording
                })
                logs += f"✅ Pobrano: {filename_base}.mp3\n"
            else:
                failed_downloads.append(recId)
                logs += f"❌ Błąd pobierania: {recId}\n"
        
        logs += f"\n📊 Podsumowanie pobierania:\n"
        logs += f"   ✅ Pobrane: {len(downloaded_files)} plików\n"
        logs += f"   ❌ Błędy: {len(failed_downloads)} plików\n\n"
        
        yield (f"✅ Pobrano {len(downloaded_files)} plików", 70, logs)
        
        if not downloaded_files:
            error_msg = "❌ Nie udało się pobrać żadnych plików"
            yield (error_msg, 70, logs + error_msg + "\n")
            return
        
        # =================================================================
        # WYSZUKIWANIE RZECZYWISTYCH PLIKÓW MP3 PO ROZPAKOWANIU
        # =================================================================
        
        # Funkcja pomocnicza do znajdowania plików MP3 w katalogu
        def find_mp3_files_in_directory(directory):
            """Znajduje wszystkie pliki MP3 w katalogu"""
            mp3_files = []
            for file in os.listdir(directory):
                if file.lower().endswith('.mp3'):
                    full_path = os.path.join(directory, file)
                    mp3_files.append({
                        'path': full_path,
                        'filename': file,
                        'filename_base': os.path.splitext(file)[0]
                    })
            return mp3_files
        
        # Znajdź wszystkie pliki MP3 w katalogu docelowym
        actual_mp3_files = find_mp3_files_in_directory(target_directory)
        
        logs += f"🔍 Znaleziono {len(actual_mp3_files)} plików MP3 w katalogu:\n"
        for mp3_file in actual_mp3_files:
            logs += f"   📄 {mp3_file['filename']}\n"
        logs += "\n"
        
        # =================================================================
        # PRZETWARZANIE AUDIO I TRANSKRYPCJA
        # =================================================================
        
        yield ("🎙️ Rozpoczynam transkrypcję z diaryzacją...", 75, logs + "🤖 Przetwarzanie AI...\n")
        
        processed_count = 0
        transcription_errors = []
        
        for i, file_info in enumerate(actual_mp3_files):
            file_path = file_info['path']
            filename_base = file_info['filename_base']
            
            # Aktualizacja postępu
            transcription_progress = 75 + (i / len(actual_mp3_files)) * 20  # 75-95%
            status_msg = f"🎙️ Transkrypcja {i+1}/{len(actual_mp3_files)}: {filename_base}"
            
            current_logs = logs + f"🎙️ Przetwarzanie {i+1}/{len(actual_mp3_files)}\n"
            current_logs += f"   📄 Plik: {filename_base}.mp3\n"
            current_logs += f"   🤖 Etapy: Whisper → Alignment → Diaryzacja\n"
            
            yield (status_msg, transcription_progress, current_logs)
            
            # Walidacja pliku audio
            if not validate_audio_file(file_path):
                transcription_errors.append(filename_base)
                logs += f"❌ Nieprawidłowy plik audio: {filename_base}\n"
                continue
            
            # Przetwarzanie przez WhisperX
            transcription_result = process_audio_file(file_path, models)
            
            if transcription_result:
                # Zapis transkrypcji
                save_success = save_transcription(
                    target_directory, 
                    filename_base, 
                    transcription_result
                )
                
                if save_success:
                    processed_count += 1
                    logs += f"✅ Transkrypcja: {filename_base}.txt\n"
                else:
                    transcription_errors.append(filename_base)
                    logs += f"❌ Błąd zapisu transkrypcji: {filename_base}\n"
            else:
                transcription_errors.append(filename_base)
                logs += f"❌ Błąd transkrypcji: {filename_base}\n"
            
            # Czyszczenie pamięci po każdym pliku
            cleanup_audio_processing()
        
        # =================================================================
        # FINALIZACJA I PODSUMOWANIE
        # =================================================================
        
        logs += f"\n🎯 PODSUMOWANIE KOŃCOWE:\n"
        logs += f"   📊 Nagrań znalezionych: {total_elements}\n"
        logs += f"   📥 Plików pobranych: {len(downloaded_files)}\n"
        logs += f"   🎵 Plików MP3 rozpakowanych: {len(actual_mp3_files)}\n"
        logs += f"   🎙️ Transkrypcji utworzonych: {processed_count}\n"
        logs += f"   ❌ Błędów: {len(failed_downloads) + len(transcription_errors)}\n"
        logs += f"   📁 Katalog: {target_directory}\n\n"
        
        if transcription_errors:
            logs += f"⚠️ Pliki z błędami:\n"
            for error_file in transcription_errors:
                logs += f"   - {error_file}\n"
            logs += "\n"
        
        final_status = f"✅ Proces zakończony: {processed_count}/{total_elements} transkrypcji"
        logs += "🎉 Aplikacja zakończyła działanie pomyślnie!"
        
        yield (final_status, 100, logs)
        
    except Exception as e:
        error_msg = f"❌ Nieoczekiwany błąd: {e}"
        final_logs = logs if 'logs' in locals() else "Błąd w trakcie inicjalizacji\n"
        final_logs += f"\n{error_msg}\n"
        final_logs += "💡 Sprawdź konfigurację i spróbuj ponownie"
        
        yield (error_msg, 0, final_logs)


print()
print("=" * 60)
print("✅ KOMÓRKA 6 - DEFINICJA GŁÓWNEJ LOGIKI ZAKOŃCZONA")
print("=" * 60)
print("📋 Zdefiniowana funkcja:")
print("   🎯 main_process() - kompletny orkiestrator aplikacji")
print("")
print("🔧 Funkcjonalności:")
print("   ✅ Walidacja danych wejściowych")
print("   🚀 Inicjalizacja modeli WhisperX")
print("   📡 Pobieranie listy nagrań z API")
print("   📁 Tworzenie struktury katalogów")
print("   📥 Pobieranie plików audio")
print("   🎙️ Transkrypcja z diaryzacją")
print("   📊 Szczegółowe raportowanie postępu")
print("   🛡️ Obsługa błędów i cleanup")
print("")
print("🎯 Następny krok: Interfejs użytkownika Gradio")
print("▶️ Uruchom komórkę 7, aby utworzyć aplikację web") 