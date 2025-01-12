# 2025-01-09

## Propozycje do omówienia

### FileFormat - nowy temat
- Pageable 
- Convertable
- Filetype guesser
- Architektura zamieniania

### Drzewo 

```aiignore
text-extract-api/
├── pdf_exttract_api/                           
│   ├── api/           # Wystawione endpointy 
│   │   ├── ocr_endpoints.py        
│   │   ├── file_endpoints.py     
│   │   └── format_endpoints.py    
│   ├── services/                     # Usługi wysokopoziomowe
│   │   ├── __init__.py #  wyczytalem że takie pliiki powinniśmy wrzucać
│   │   ├── ocr_service.py           
│   │   ├── file_service.py          
│   │   └── converter_service.py     
│   ├── files/          #      Moduł odpowiedzialny za pliki ogólnie
│   │   ├── __init__.py #  wyczytalem że takie pliiki powinniśmy wrzucać
│   │   ├── formats/             # Formaty czyli to co zrobiłem dzisija
│   │   │   ├── __init__.py
│   │   │   ├── pdf_file_format.py   
│   │   │   ├── image_file_format.py 
│   │   │   └── audio_file_format.py
│   │   ├── storage/             # Storage bo to w końću pliki :)
│   │   │   ├── local_storage.py    
│   │   │   ├── s3_storage.py        
│   │   │   └── azure_storage.py    
│   │   ├── converters/           # convertery 
│   │   │   ├── pdf_to_jpeg.py       
│   │   ├── file_manager.py         
│   │   └── file_validator.py        # validatory do wykorzytstywania w api każ∂y moduł powinien miećswoje
│   ├── ocr/                        
│   │   ├── strategy/                
│   │   │   ├── base_ocr.py          
│   │   │   ├── tesseract_ocr.py    
│   │   │   ├── llama_ocr.py         
│   │   │   └── custom_marker_ocr.py  
│   │   ├── ocr_manager.py     
│   ├   └── ocr_validator.py
│   ├── utils/                      
│   │   ├── __init__.py
│   │   ├── image_processor.py       
│   │   ├── logger.py            
│   │   ├── filetype.py             
│   │   ├── common.py              
│   │   └── config.py                
│   └── main.py                
```

### Drzewo v2
----

```^ v2 maly update do przegadania
│   ├── files/          #      Moduł odpowiedzialny za pliki ogólnie
│   │   ├── __init__.py #  wyczytalem że takie pliiki powinniśmy wrzucać
│   │   ├── formats/             # Formaty czyli to co zrobiłem dzisija
│   │   │   ├── __init__.py
│   │   │   ├── pdf_file_format.py   
│   │   │   ├── image_file_format.py 
│   │   ├── file_format.py # interfejs
│   │   ├── file_format_factory.py # factory
```

---

### Rrequirements uspójniony 
- Po wstępnej weryfikacji nie ma w naszym przypadku sensu wydzielna requirementsów per te mały utilsy, szczególnie jeżeli są uruchamiane na .venv bo to trafia do tego samego miejsca z paczkami

### From maker models było zepsute w run.sh
- I naprawiłem, dłużej się ładuje, ale maker i tak za chwilę wylatuje z głównego repo i poza tym w następnych PR pójdzie refactor run

### 
- Storage nie powinien być na tym samym 