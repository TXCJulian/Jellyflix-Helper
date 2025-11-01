# Beispiel-Ordnerstruktur

Platziere hier deine Musik nach folgendem Schema:

```
Music/
├── The Beatles/
│   ├── Abbey Road/
│   │   ├── 01-Come Together.flac
│   │   ├── 02-Something.flac
│   │   └── 03-Maxwell's Silver Hammer.flac
│   └── Revolver/
│       ├── 01-Taxman.flac
│       └── 02-Eleanor Rigby.flac
└── Pink Floyd/
    └── Dark Side of the Moon/
        ├── 01-Speak to Me.flac
        └── 02-Breathe.flac
```

Das Tool wird FLAC-Dateien basierend auf ihren Metadaten (Title, Track, Disc) umbenennen.
Format: `{Disc:02d}-{Track:02d} {Title}.flac`
