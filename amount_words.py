LITHUANIAN_NUMBER_COMMON = ("nulis",
                            "vienas", "du", "trys", "keturi", "penki", "šeši", "septyni", "aštuoni", "devyni",
                            "dešimt", "vienuolika", "dvylika", "trylika", "keturiolika", "penkiolika", "šešiolika",
                            "septyniolika", "aštuoniolika", "devyniolika")
LITHUANIAN_NUMBER_TENS = {2: "dvidešimt",
                          3: "trisdešimt",
                          4: "keturiasdešimt",
                          5: "penkiasdešimt",
                          6: "šešiasdešimt",
                          7: "septyniasdešimt",
                          8: "aštuoniasdešimt",
                          9: "devyniasdešimt"}


def pluralize(n, zero, singular, plural):
    if n % 10 == 0 or 11 <= n % 100 <= 19:
        return zero
    if n % 10 == 1:
        return singular
    else:
        return plural


def lithuanian_number(number):
    assert number >= 0
    items = []
    common = number % 100
    hundreds = number % 1000 // 100
    thousands = number % 1000000 // 1000
    millions = number % 1000000000 // 1000000
    milliards = number // 1000000000
    if milliards:
        if milliards > 1:
            items.append(lithuanian_number(milliards))
        items.append(pluralize(milliards, "milijardų", "milijardas", "milijardai"))
    if millions:
        if millions > 1:
            items.append(lithuanian_number(millions))
        items.append(pluralize(millions, "milijonų", "milijonas", "milijonai"))
    if thousands:
        if thousands > 1:
            items.append(lithuanian_number(thousands))
        items.append(pluralize(thousands, "tūkstančių", "tūkstantis", "tūkstančiai"))
    if hundreds:
        if hundreds > 1:
            items.append(LITHUANIAN_NUMBER_COMMON[hundreds])
        items.append(pluralize(hundreds, "šimtų", "šimtas", "šimtai"))
    if common or not items:
        if 1 <= common <= len(LITHUANIAN_NUMBER_COMMON):
            items.append(LITHUANIAN_NUMBER_COMMON[common])
        else:
            ones = common % 10
            tens = common // 10
            if tens:
                items.append(LITHUANIAN_NUMBER_TENS[tens])
            if ones or not tens:
                items.append(LITHUANIAN_NUMBER_COMMON[ones])
    return " ".join(items)

def amount_words(amount):
    amount = amount.replace(",", ".")
    if '.' in amount:
        euros, cents = amount.rsplit(".", 1)
        euros = int(euros)
        cents = int(cents)
        assert cents < 100
    else:
        euros = int(amount)
        cents = 0

    items = []
    assert euros or cents
    if euros:
        items.append("{} {}".format(lithuanian_number(euros),
                                    pluralize(euros, "Eurų", "Euras", "Eurai")))
    items.append("{:02} ct".format(cents))
    return ", ".join(items)
