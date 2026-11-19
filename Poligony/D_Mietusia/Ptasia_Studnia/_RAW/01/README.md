# Ptasia Studnia — paczka źródłowa 01

- **Status materiału:** dostępny
- **Pochodzenie danych:** Projekt Walls przekazany przez Marka Lorczyka. Wszystkie 16 plików w tym archiwum jest identycznych bajtowo z częścią Ptasiej Studni w [paczce z issue #28](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/issues/28).
- **Autorzy pomiarów:** nieznane
- **Daty pomiarów:** 2004-06-30, 2004-07-01 i 2004-07-02 według dyrektyw #DATE w przekazanych plikach SRV
- **Data pozyskania:** 2014-05-13 (data przekazania materiału o tej samej zawartości)
- **Dodał do _RAW:** Dariusz Lubomski
- **Licencja źródłowa:** nieznane
- **Kompletność:** 14 SRV użytych jako podstawa projektu, jeden SRV z pomiarami między otworami oraz plik projektu Walls. W paczce brak tabelek terenowych i pomiaru łączącego ciąg 10A z aktywną siecią.

## Zawartość

- `ptasia walls.zip` — archiwum ZIP z projektem Walls
- `Ptasia calosc popr/` — rozpakowane pliki projektu

## Powiązanie z katastrem

`10A.SRV` zawiera 27 odcinków od stacji `m1`. Przekazany plik ma lokalne
`#FIX m1`. W katastrze ciąg jest wykomentowany do czasu potwierdzenia
jego dowiązania do aktywnej sieci.

`OTW POW.SRV` zawiera 31 odcinków powierzchniowych od Ptasiej Studni
(`a1`) przez Lodową Litworową (`a14`) do Jaskini nad Dachem (`a22`)
oraz odgałęzienie do Jaskini nad Lodową Litworową (`A7`) i dalej do
początku wykopu (`A10`). Od wersji v1.3.7 plik pozostaje w archiwum.
`11A.SRV` jest osobnym, nadal aktywnym ciągiem powierzchniowym od otworu
Lodowej Litworowej (`n1` w źródle, `a14` w katastrze).
