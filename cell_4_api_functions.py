#######################
## KOMÓRKA 4 ##
#######################

# KOMÓRKA 4: DEFINICJE - Funkcje API i Zarządzania Plikami
# Ta komórka zawiera WYŁĄCZNIE definicje funkcji.
# Uruchomienie tej komórki nie wywołuje żadnej z tych funkcji,
# a jedynie udostępnia je w pamięci notatnika.
# 
# ZALEŻNOŚCI: Wymaga uruchomienia komórki 2 (zmienne globalne)

print("🔧 Definiuję funkcje API i zarządzania plikami...")
print("=" * 60)

# =============================================================================
# FUNKCJE KOMUNIKACJI Z API
# =============================================================================

def get_recordings_list(username, password, selected_date_str):
    """
    Pobiera paginowaną listę nagrań z API dla wybranej daty.
    
    Args:
        username (str): Nazwa użytkownika API
        password (str): Hasło API
        selected_date_str (str): Data w formacie "YYYY-MM-DD (Dzień tygodnia)"
    
    Returns:
        tuple: (lista_nagrań, total_elements) lub ([], 0) w przypadku błędu
    """
    try:
        from requests.auth import HTTPBasicAuth
        import requests
        import re
        
        # Wyciągnięcie daty z formatu "2025-07-22 (Poniedziałek)"
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', selected_date_str)
        if not date_match:
            print(f"❌ Błąd: Niepoprawny format daty: {selected_date_str}")
            return [], 0
        
        date_str = date_match.group(1)
        
        # Formatowanie parametrów dla API
        date_from = f"{date_str}T00:00:00"
        date_to = f"{date_str}T23:59:59"
        
        print(f"📅 Pobieranie nagrań dla daty: {date_str}")
        print(f"🔍 Zakres: {date_from} - {date_to}")
        
        # Konfiguracja
        auth = HTTPBasicAuth(username, password)
        all_recordings = []
        page = 0
        total_elements = 0
        
        while True:
            # Parametry zapytania
            params = {
                'size': DEFAULT_PAGE_SIZE,
                'page': page,
                'dateFrom': date_from,
                'dateTo': date_to,
                'status': 'RECORDED'
            }
            
            print(f"📄 Pobieranie strony {page + 1}...")
            
            # Wywołanie API
            response = requests.get(
                f"{API_BASE_URL}/recordingsPaged/",
                params=params,
                auth=auth,
                timeout=API_TIMEOUT
            )
            
            # Sprawdzenie odpowiedzi
            if response.status_code == 401:
                print("❌ Błąd 401: Nieprawidłowe dane logowania")
                return [], 0
            elif response.status_code == 404:
                print("❌ Błąd 404: Endpoint nie został znaleziony")
                return [], 0
            elif response.status_code != 200:
                print(f"❌ Błąd API {response.status_code}: {response.text}")
                return [], 0
            
            # Parsowanie JSON
            try:
                data = response.json()
            except ValueError as e:
                print(f"❌ Błąd parsowania JSON: {e}")
                return [], 0
            
            # Wyciągnięcie danych z pierwszej strony
            if page == 0:
                total_elements = data.get('totalElements', 0)
                total_pages = data.get('totalPages', 0)
                print(f"📊 Znaleziono {total_elements} nagrań na {total_pages} stronach")
                
                if total_elements == 0:
                    print(f"ℹ️ Brak nagrań dla daty {date_str}")
                    return [], 0
            
            # Dodanie nagrań z aktualnej strony
            content = data.get('content', [])
            all_recordings.extend(content)
            print(f"✅ Strona {page + 1}: {len(content)} nagrań")
            
            # Sprawdzenie czy to ostatnia strona
            if data.get('last', True):
                break
                
            page += 1
        
        print(f"🎯 Pobrano łącznie {len(all_recordings)} nagrań")
        return all_recordings, total_elements
        
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout: Przekroczono limit czasu {API_TIMEOUT}s")
        return [], 0
    except requests.exceptions.ConnectionError:
        print("🌐 Błąd połączenia z API")
        return [], 0
    except Exception as e:
        print(f"❌ Nieoczekiwany błąd: {e}")
        return [], 0


def download_recording(session, recId, save_path):
    """
    Pobiera pojedyncze nagranie z API.
    
    Args:
        session (requests.Session): Sesja z ustawioną autoryzacją
        recId (int/str): ID nagrania
        save_path (str): Ścieżka zapisu pliku
    
    Returns:
        bool: True jeśli sukces, False w przypadku błędu
    """
    try:
        print(f"🎵 Pobieranie nagrania {recId}...")
        
        # Wywołanie API
        response = session.get(
            f"{API_BASE_URL}/recording/{recId}",
            timeout=API_TIMEOUT,
            stream=True  # Streaming dla dużych plików
        )
        
        if response.status_code == 404:
            print(f"⚠️ Nagranie {recId} nie zostało znalezione (404)")
            return False
        elif response.status_code != 200:
            print(f"❌ Błąd pobierania {recId}: HTTP {response.status_code}")
            return False
        
        # Zapis pliku strumieniowo
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Sprawdzenie rozmiaru pliku
        file_size = os.path.getsize(save_path)
        if file_size == 0:
            print(f"⚠️ Plik {recId} jest pusty")
            return False
        
        # Sprawdzenie czy to plik ZIP i automatyczne rozpakowanie
        if save_path.endswith('.mp3'):
            try:
                import zipfile
                # Sprawdź czy plik to faktycznie ZIP
                if zipfile.is_zipfile(save_path):
                    print(f"📦 Wykryto plik ZIP: {recId}")
                    
                    # Zmień rozszerzenie na .zip
                    zip_path = save_path.replace('.mp3', '.zip')
                    os.rename(save_path, zip_path)
                    
                    # Rozpakuj do tego samego katalogu
                    directory = os.path.dirname(save_path)
                    extracted_files = unzip_file(zip_path, directory)
                    
                    if extracted_files:
                        print(f"✅ Rozpakowano {len(extracted_files)} plików z {recId}")
                        return True
                    else:
                        print(f"❌ Błąd rozpakowania ZIP: {recId}")
                        return False
                else:
                    print(f"✅ Pobrano {recId}: {file_size/1024:.1f} KB (MP3)")
                    return True
                    
            except Exception as e:
                print(f"⚠️ Błąd sprawdzania ZIP dla {recId}: {e}")
                print(f"✅ Pobrano jako MP3: {file_size/1024:.1f} KB")
                return True
        else:
            print(f"✅ Pobrano {recId}: {file_size/1024:.1f} KB")
            return True
        
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout pobierania {recId}")
        return False
    except Exception as e:
        print(f"❌ Błąd pobierania {recId}: {e}")
        return False


# =============================================================================
# FUNKCJE ZARZĄDZANIA PLIKAMI
# =============================================================================

def create_target_directory(selected_date_str):
    """
    Tworzy katalog docelowy na Google Drive.
    
    Args:
        selected_date_str (str): Data w formacie "YYYY-MM-DD (Dzień tygodnia)"
    
    Returns:
        str: Ścieżka utworzonego katalogu lub None w przypadku błędu
    """
    try:
        import re
        from pathlib import Path
        
        # Wyciągnięcie daty
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', selected_date_str)
        if not date_match:
            print(f"❌ Błąd: Niepoprawny format daty: {selected_date_str}")
            return None
        
        date_str = date_match.group(1)
        
        # Utworzenie ścieżki
        target_dir = Path(MYDRIVE_PATH) / date_str
        
        # Utworzenie katalogu
        target_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Utworzono katalog: {target_dir}")
        return str(target_dir)
        
    except Exception as e:
        print(f"❌ Błąd tworzenia katalogu: {e}")
        return None


def generate_filename_base(record_metadata):
    """
    Generuje bazową nazwę pliku na podstawie metadanych nagrania.
    
    Args:
        record_metadata (dict): Metadane nagrania z API
    
    Returns:
        str: Bazowa nazwa pliku w formacie recId-callingUserPart-calledUserPart-callDirection
    """
    try:
        recId = record_metadata.get('recId', 'unknown')
        calling = record_metadata.get('callingUserPart', 'unknown')
        called = record_metadata.get('calledUserPart', 'unknown')
        direction = record_metadata.get('callDirection', 'unknown')
        
        # Sanityzacja nazw (usunięcie niepożądanych znaków)
        def sanitize(value):
            return str(value).replace('/', '_').replace('\\', '_').replace(':', '_')
        
        filename_base = f"{sanitize(recId)}-{sanitize(calling)}-{sanitize(called)}-{sanitize(direction)}"
        
        return filename_base
        
    except Exception as e:
        print(f"❌ Błąd generowania nazwy pliku: {e}")
        return f"recording_{record_metadata.get('recId', 'unknown')}"


def save_transcription(directory, base_filename, transcription_data):
    """
    Zapisuje transkrypcję z diaryzacją do pliku TXT.
    
    Args:
        directory (str): Katalog docelowy
        base_filename (str): Bazowa nazwa pliku (bez rozszerzenia)
        transcription_data (dict): Dane transkrypcji z WhisperX
    
    Returns:
        bool: True jeśli sukces, False w przypadku błędu
    """
    try:
        from pathlib import Path
        
        # Ścieżka pliku
        txt_path = Path(directory) / f"{base_filename}.txt"
        
        # Formatowanie transkrypcji
        with open(txt_path, 'w', encoding='utf-8') as f:
            if 'segments' in transcription_data:
                for segment in transcription_data['segments']:
                    start_time = segment.get('start', 0)
                    end_time = segment.get('end', 0)
                    text = segment.get('text', '').strip()
                    speaker = segment.get('speaker', 'SPEAKER_UNKNOWN')
                    
                    # Formatowanie czasu
                    start_formatted = format_timestamp(start_time)
                    end_formatted = format_timestamp(end_time)
                    
                    # Zapis linii transkrypcji
                    f.write(f"[{start_formatted} - {end_formatted}] {speaker}: {text}\n")
            else:
                # Fallback dla transkrypcji bez diaryzacji
                text = transcription_data.get('text', 'Brak transkrypcji')
                f.write(f"[00:00:00.00 - 00:00:00.00] SPEAKER_00: {text}\n")
        
        print(f"📝 Zapisano transkrypcję: {txt_path.name}")
        return True
        
    except Exception as e:
        print(f"❌ Błąd zapisu transkrypcji {base_filename}: {e}")
        return False


def generate_date_dropdown_options():
    """
    Generuje listę dat z ostatnich 3 miesięcy dla dropdown'a.
    
    Returns:
        list: Lista dat w formacie "YYYY-MM-DD (Dzień tygodnia)"
    """
    try:
        from datetime import datetime, timedelta
        
        # Aktualna data
        end_date = datetime.now().date()
        
        # Data sprzed 3 miesięcy (przybliżenie: 90 dni)
        start_date = end_date - timedelta(days=90)
        
        # Generowanie listy dat
        date_options = []
        current_date = start_date
        
        # Polskie nazwy dni tygodnia
        polish_weekdays = {
            0: 'Poniedziałek',
            1: 'Wtorek', 
            2: 'Środa',
            3: 'Czwartek',
            4: 'Piątek',
            5: 'Sobota',
            6: 'Niedziela'
        }
        
        while current_date <= end_date:
            weekday_name = polish_weekdays[current_date.weekday()]
            date_option = f"{current_date.strftime('%Y-%m-%d')} ({weekday_name})"
            date_options.append(date_option)
            current_date += timedelta(days=1)
        
        # Sortowanie od najnowszej do najstarszej
        date_options.reverse()
        
        print(f"📅 Wygenerowano {len(date_options)} opcji dat")
        return date_options
        
    except Exception as e:
        print(f"❌ Błąd generowania dat: {e}")
        return []


def unzip_file(zip_path, extract_to_directory):
    """
    Rozpakowuje plik ZIP do określonego katalogu.
    
    Args:
        zip_path (str): Ścieżka do pliku ZIP
        extract_to_directory (str): Katalog docelowy
    
    Returns:
        list: Lista rozpakowanych plików lub pusta lista w przypadku błędu
    """
    try:
        import zipfile
        from pathlib import Path
        
        extracted_files = []
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Lista plików w archiwum
            file_list = zip_ref.namelist()
            print(f"📦 Rozpakowywanie {len(file_list)} plików z {Path(zip_path).name}")
            
            # Rozpakowanie wszystkich plików
            zip_ref.extractall(extract_to_directory)
            
            # Sprawdzenie rozpakowanych plików
            for file_name in file_list:
                extracted_path = Path(extract_to_directory) / file_name
                if extracted_path.exists():
                    extracted_files.append(str(extracted_path))
                    print(f"✅ Rozpakowano: {file_name}")
        
        # Usunięcie pliku ZIP po rozpakowaniu
        os.remove(zip_path)
        print(f"🗑️ Usunięto plik ZIP: {Path(zip_path).name}")
        
        return extracted_files
        
    except zipfile.BadZipFile:
        print(f"❌ Błąd: {zip_path} nie jest prawidłowym plikiem ZIP")
        return []
    except Exception as e:
        print(f"❌ Błąd rozpakowania {zip_path}: {e}")
        return []


# =============================================================================
# FUNKCJE POMOCNICZE
# =============================================================================

def format_timestamp(seconds):
    """
    Formatuje sekundy do formatu HH:MM:SS.ms zgodnie z dokumentacją
    
    Args:
        seconds (float): Czas w sekundach
    
    Returns:
        str: Sformatowany timestamp w formacie HH:MM:SS.ms
    """
    try:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        
        # Format zgodny z dokumentacją: HH:MM:SS.ms
        return f"{hours:02d}:{minutes:02d}:{secs:05.2f}"
    except:
        return "00:00:00.00"


print()
print("=" * 60)
print("✅ KOMÓRKA 4 - DEFINICJE FUNKCJI ZAKOŃCZONA")
print("=" * 60)
print("📋 Zdefiniowane funkcje:")
print("   🌐 get_recordings_list() - pobieranie listy nagrań z paginacją")
print("   📥 download_recording() - pobieranie pojedynczego nagrania")
print("   📁 create_target_directory() - tworzenie katalogu docelowego")
print("   🏷️ generate_filename_base() - generowanie nazw plików")
print("   📝 save_transcription() - zapis transkrypcji do TXT")
print("   📅 generate_date_dropdown_options() - lista dat dla UI")
print("   📦 unzip_file() - rozpakowanie plików ZIP")
print("   ⏱️ format_timestamp() - formatowanie timestampów")
print()
print("🎯 Następny krok: Definicje funkcji przetwarzania audio (WhisperX)")
print("▶️ Uruchom komórkę 5, aby zdefiniować funkcje transkrypcji i diaryzacji") 