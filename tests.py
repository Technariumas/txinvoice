#!/usr/bin/env python
import unittest
import doctest
from amount_words import pluralize, lithuanian_number, amount_words
import txinvoice
from subprocess import check_output


class TestFormatAmount(unittest.TestCase):
    def test_pluralize(self):
        forms = 'tūkstančių', 'tūkstantis', 'tūkstančiai'
        self.assertEqual(pluralize(0, *forms), 'tūkstančių')
        self.assertEqual(pluralize(10, *forms), 'tūkstančių')
        self.assertEqual(pluralize(11, *forms), 'tūkstančių')
        self.assertEqual(pluralize(17, *forms), 'tūkstančių')
        self.assertEqual(pluralize(1, *forms), 'tūkstantis')
        self.assertEqual(pluralize(21, *forms), 'tūkstantis')
        self.assertEqual(pluralize(3, *forms), 'tūkstančiai')
        self.assertEqual(pluralize(23, *forms), 'tūkstančiai')

    def test_lithuanian_number(self):
        self.assertEqual(lithuanian_number(0),
                         'nulis')
        self.assertEqual(lithuanian_number(1),
                         'vienas')
        self.assertEqual(lithuanian_number(13),
                         'trylika')
        self.assertEqual(lithuanian_number(21),
                         'dvidešimt vienas')
        self.assertEqual(lithuanian_number(30),
                         'trisdešimt')
        self.assertEqual(lithuanian_number(131),
                         'šimtas trisdešimt vienas')
        self.assertEqual(lithuanian_number(2711),
                         'du tūkstančiai septyni šimtai vienuolika')
        self.assertEqual(lithuanian_number(17191),
                         'septyniolika tūkstančių šimtas devyniasdešimt vienas')
        self.assertEqual(lithuanian_number(1234567890),
                         'milijardas du šimtai trisdešimt keturi milijonai penki šimtai šešiasdešimt septyni tūkstančiai aštuoni šimtai devyniasdešimt')

    def test_amount_words(self):
        self.assertEqual(amount_words("10.50"),
                         'dešimt eurų, 50 ct')
        self.assertEqual(amount_words("0.13"),
                         '13 ct')
        self.assertEqual(amount_words("190,00"),
                         'šimtas devyniasdešimt eurų, 00 ct')
        self.assertEqual(amount_words("190"),
                         'šimtas devyniasdešimt eurų, 00 ct')


class TestTxinvoice(unittest.TestCase):
    def test_render_invoice(self):
        pdf = txinvoice.render_invoice({
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
            "total": "10",
            "total_words": True,
        })
        self.assertEqual(check_output(["file", "-ib", "-"], input=pdf).strip(),
                         b"application/pdf; charset=binary")


if __name__ == "__main__":
    unittest.main()
