# Specyfikacja usług REST API 
## 1.4  Pobranie listy nagrań i połączeń 
Opis  Usługa pobrania listy nagrań i połączeń według zadanych kryteriów 
*URL  /recordingApi/recordingsPaged/ *
### Parametry żądania  
size=<size> 
page=<page> 
dateFrom=<dateFrom> 
dateTo=<dateTo> 
numberA=<numberA> 
numberB=<numberB> 
status=<status> 
recordingRemoved=<recordingRemoved> 
description=<description> 
Zawartość żądania  - 
Metoda  GET 
### Opis parametrów żądania  <size> - ilość elementów na stronie (domyślnie 20) 
<page> - numer strony (0=pierwsza strona, domyślnie 0) 
<dateFrom> - data początkowa połączenia (opcjonalne) 
<dateTo> - data końcowa połączenia (opcjonalnie) 
<numberA> - numer odbierający (opcjonalnie) 
<numberB> - numer dzwoniący (opcjonalnie) 
<status>  -  lista  statusów  połączenia  (opcjonalnie),  możliwe  wartości: 
RECORDED/NOT_RECORDED/MISSED/FAILED 
<recordingRemoved>  -  flaga  oznaczająca  połączenia  usunięte  (opcjonalnie),  true  – 
zwrócone  zostaną  tylko  połączenia  oznaczone  jako  usunięte,  false  –  zwrócone  zostaną 
tylko połączenia nie oznaczone usunięte, brak – zwrócone zostaną wszystkie połączenia 
<description> - pozwala na filtrowanie po opisie połączenia (opcjonalnie), jeśli parametr 
jest niepusty zwrócone zostaną tylko połączenia z dopasowanym opisem, jeśli parametr 
wystąpi ale z pustą wartością (description=) zwrócone zostaną tylko połączenia z pustym 
opisem, przy braku parametru zwracane są wszystkie połączenia 
Kod odpowiedzi  200 OK 
400 Bad Request - błędne zapytanie 
401 Unauthorized - błąd autoryzacji 
Zawartość odpowiedzi  Lista nagrań w formacie JSON: 
{ 
    "content": [ 
        { 
            "calledUserPart": "<calledUserPart>",          
            "callingUserPart": "<callingUserPart>", 
            "establishedTime": "<establishedTime>", 
            "startCopyTime": "<startCopyTime>", 
            "markedForRemoval": <markedForRemoval>, 
            "markedForCopy": <markedForCopy>, 
            "recordingCopied": <recordingCopied> 
            "departmentName": "<departmentName>" 
            "callDirection": "<callDirection>", 
            "recordingFailed": <recordingFailed>, 
            "recId": <recId>, 
            "recordingRemoved": <recordingRemoved>, 
            "status": <status>, 
            "endTime": "<endTime>", 
            "otherNumber": "<otherNumber>", 
            "recordingNumber": "<recordingNumber>", 
            "compressed": <compressed>, 
            "fileCount": <fileCount>, 
            "description": "<description>", 
            "startTime": "<startTime>", 
            "redirectType": "<redirectType>", 
            "length": <length>, 
            "size": <size>, 
        },(...) 
    ], 
    "last": <last>, 
    "totalPages": <totalPages>, 
    "totalElements": <totalElements>, 
    "size": <size>, 
    "number": <number>, 
    "sort": null, 
    "numberOfElements": <numberOfElements>, 
    "first": <first> 
} 
Opis elementów odpowiedzi  Atrybuty nagrań (element content): 
<recId> - id nagrania 
<calledUserPart>  -  część  user  part  adresu  SIP  URI  dla  użytkownika  odbierającego. 
Najczęściej numer MSISDN. Wartość jaka została otrzymana z sieci bez normalizacji 
<callingUserPart>  -  część  user  part  adresu  SIP  URI  dla  użytkownika  dzwoniącego. 
Najczęściej numer MSISDN. Wartość jaka została otrzymana z sieci bez normalizacji  
<startTime> - czas zainicjowania połączenia 
<endTime> - czas zakończenia połączenia 
<establishedTime> - czas zestawienia połączenia 
<fileCount> -  liczba plików z nagraniem: 1 jeśli dla połączenia jest gotowe nagranie do 
pobrania, 0 jeśli dla połączenia nie ma nagrania 
<size> - rozmiar pliku z nagraniem w bajtach          
<length> - długość nagrania w milisekundach 
<callDirection> - kierunek nagrywanego połączenia: MO - połączenie wychodzące, MT - 
połączenie przychodzące 
<recordingNumber> - numer MSISDN strony nagrywanej ( np. jeżeli kierunek nagrywania 
MO to numer strony dzwoniącej) 
<otherNumber> - numer MSISDN drugiej strony (np. jeżeli kierunek nagrywania MO, to 
numer strony odbierającej)  
<description> - opis nagrania, null gdy nie jest wypełniony 
<recordingFailed> - true/false - nagranie nieudane - jeśli true to nagranie dla połączenia 
nie jest dostępne 
<markedForRemoval> - true/false - nagranie oznaczone jako przeznaczone do usunięcia w 
najbliższym czasie  
<markedForCopy>  -  true/false  -  nagranie  jest  przeznaczone  do  kopiowania  na  serwer 
SFTP 
<recordingRemoved>  -  true/false  -  nagranie  zostało  usunięte,  dostępne  są  tylko 
metadane nagrania 
<status> - status nagrania (RECORDED/NOT_RECORDED/MISSED/FAILED) 
<startCopyTime> - data skopiowania na serwer SFTP 
<recordingCopied> - true/false - nagranie zostało skopiowane na serwer SFTP 
<departmentName>  -  nazwa  działu,  do  którego  przypisany  był  numer  nagrywany  w 
momencie rozmowy 
<compressed> - flaga informująca o tym czy nagranie zostało skompresowane do formatu 
mp3 (true/false) 
<redirectType> - wartość informująca o przekierowaniu połączenia przekierowanie null-
brak przekierowania, 0-VOICE_MAIL 
Atrybuty listy nagrań: 
<last> - czy pobrana strona jest ostatnią stroną z listy 
<totalPages> - liczba wszystkich stron dostępnych do pobrania 
<totalElements> - liczba wszystkich elementów 
<size>  -  maksymalna  liczba  elementów  na  stronie  (żądana  wielkość  strony  lub 
maksymalna wielkość dopuszczalna przez system) 
<number> - numer pobranej strony 
<numberOfElements> - liczba nagrań na pobranej liście 
<first> - czy pobrana strona jest pierwszą stroną 

### Przykład wywołania: 
curl -u 'user':'password' \  
-X GET \ 
'https://nagrywanie.plus.pl/recordingApi/recordingsPaged/?size=10&page=0&dateFrom=2018-
10-15T08:09:35&status=RECORDED' 

### Przykład odpowiedzi: 
{ 
  "content" : [ { 
    "calledUserPart" : "48000110200",          
 
8 / 53 
    "callingUserPart" : "48500111222", 
    "establishedTime" : "2018-10-15T11:32:47", 
    "startCopyTime" : null, 
    "markedForRemoval" : true, 
    "markedForCopy" : false, 
    "fileCount" : 1, 
    "recordingCopied" : false, 
    "departmentName" : "d1", 
    "callDirection" : "MT", 
    "recordingFailed" : false, 
    "recordingRemoved" : false, 
    "status": "RECORDED", 
    "recId" : 1539595123456, 
    "recordingNumber" : "48000110200", 
    "compressed" : true, 
    "endTime" : "2018-10-15T11:32:58", 
    "otherNumber" : "48500111222", 
    "description" : "abcd", 
    "startTime" : "2018-10-15T11:32:41", 
    "length" : 10120, 
    "size" : 20955 
  }, { 
    "calledUserPart" : "48500000111", 
    "callingUserPart" : "48607999999", 
    "establishedTime" : "2018-10-15T12:22:49", 
    "startCopyTime" : null, 
    "markedForRemoval" : true, 
    "markedForCopy" : false, 
    "fileCount" : 1, 
    "recordingCopied" : false, 
    "departmentName" : null, 
    "callDirection" : "MO", 
    "recordingFailed" : false, 
    "recordingRemoved" : false, 
    "status": "RECORDED", 
    "recId" : 1539598654321, 
    "recordingNumber" : "48607999999", 
    "compressed" : true, 
    "endTime" : "2018-10-15T12:22:56", 
    "otherNumber" : "48500000111", 
    "description" : null, 
    "startTime" : "2018-10-15T12:22:47", 
    "redirectType" :0, 
    "length" : 6020, 
    "size" : 12747 
  } ], 
  "last" : true, 
  "totalElements" : 2, 
  "totalPages" : 1, 
  "sort" : null,  
9 / 53 
  "first" : true, 
  "numberOfElements" : 2, 
  "size" : 10, 
  "number" : 0 
} 

## Pobranie pliku z nagraniem 

*URL  /recordingApi/recording/{recId} *

### Parametry żądania  - 
#### Zawartość żądania  - 
Metoda  GET 
Opis parametrów żądania  
{recId} - id nagrania do pobrania 
{encrypted} – opcjonalna wartość typu boolean, jeżeli true zwracane nagranie będzie w postaci zaszyfrowanej, false w postaci odszyfrowanej (o ile odszyfrowanie jest możliwe). 
Domyślna wartość - false 
Kod odpowiedzi  200 OK 
400 Bad Request - błędne zapytanie 
401 Unauthorized - błąd autoryzacji 
404 Not Found - plik nie został odnaleziony 
Zawartość odpowiedzi  W odpowiedzi wysłany jest skompresowany plik zip z nagraniem 

### Opis  elementów odpowiedzi 
Przykład wywołania:
curl -u 'user':'password' \  
-X GET \ 
https://nagrywanie.plus.pl/recordingApi/recording/1539512345678 
Przykład odpowiedzi: 
- 