# Diff paczki Witolda Hoffmanna

Porownanie wykonane 2026-05-22 przed importem danych do glownych plikow `.SRV`.
Surowe pliki z paczki pozostaja bez zmian w katalogu `_RAW/02`.

## Nowe ciagi

- `BK-N3D-G.SRV` wystepuje tylko w paczce Witolda; zaimportowano jako `Poligony/D_Koscieliska/Kom_Wierch/Bandzioch_Kom/BK-N3D-G.SRV`.
- `surferow.srv` wystepuje tylko w paczce Witolda; zaimportowano jako `Poligony/D_Koscieliska/Kom_Wierch/Bandzioch_Kom/SURFEROW.SRV`, z nazwa zgodna z konwencja repozytorium.
- Do importu wybrano wersje Walls, bo `ready_survex/Surferow.svx` nie zawiera koncowej odnogi `12 -> 45 -> 46 -> 47 -> 48 -> 49`, obecnej w `surferow.srv`.

## Istniejace pliki Bandziocha

Po pominieciu roznic technicznych dodanych w repozytorium (`#prefix`, daty, jednostki, flagi/notatki i formatowanie), pliki o tych samych nazwach sa pomiarowo zgodne z aktualnym repozytorium poza ponizszymi punktami:

- `BK-BCG-G.SRV`: paczka Witolda ma przecinki dziesietne w `GB002001 GB002002 5,00...` oraz `GCA017 GCA018 9,00...`; repozytorium ma poprawione kropki.
- `BK-BCG-G.SRV`: paczka Witolda zawiera dwa aktywne powtorzenia `GC014 GC015 8.4 320 -90`; repozytorium zostawia jedno aktywne, a drugie jako komentarz z adnotacja o powtorzeniu.
- `BK-BCG-S.SRV`: paczka Witolda ma przecinek dziesietny w `H H001 2,00...`; repozytorium ma poprawiona kropke.
- `BK-BSD-S.SRV`: repozytorium zawiera dodatkowe polaczenie `BC016 BE020 0 0 0` opisane jako polaczenie z ciagiem 7 Dna wg arkusza raw; w paczce Witolda tej poprawki nie ma.
- `BK-CG.SRV`: paczka Witolda zawiera lokalny `#fix 000 5455060.050 416262.210 1456.3`; repozytorium trzyma wspolrzedne otworow w `Poligony/OTWORY.SRV.j2` i `Poligony/OTWORY.SRV`, wiec nie przeniesiono tego wpisu.
- `BK-W.SRV`: roznica dotyczy tylko znaku diakrytycznego w opisie (`pomiarów` vs repozytoryjne ASCII `pomiarow`).

Wniosek: nie przenosic hurtowo starszych plikow Witolda na istniejace pliki repozytorium. Zachowac je w `_RAW`, a do aktywnych danych wlaczyc tylko brakujace ciagi.
