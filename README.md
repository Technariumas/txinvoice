# txinvoice

Programa sąskaitų generavimui.

## Instaliavimas

Iš sisteminių paketų `texlive` ir `tex-gyre`. Python dependencus galima gauti
su

    pip3 install --user -r requirements.txt


## Naudojimas

    curl -X POST -d '{
        "seller": {
            "name": "UAB Įmonita",
            "id": "00666"
        },
        "client": {
            "name": "Jonas Jonavičius",
            "address": "Bistryčios g. 13, Vilnius"
        },
        "series": "ŠK",
        "number": "00001",
        "items": [
          {"title": "Narystė", "unit": "mėn.", "quantity": "1", "price": "10", "total": "10"}
        ],
        "sum": "10",
        "vat": "0",
        "total": "10"
    }' http://127.0.0.1:8080/ > invoice.pdf
