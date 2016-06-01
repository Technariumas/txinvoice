import pystache
import tempfile
import os
import sh
import shutil
import re

TEX_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "tex")
INVOICE_TEMPLATE = os.path.join(TEX_PATH, "invoice_template.tex")


def tex_escape(text):
    """
        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX
    """
    conv = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless',
        '>': r'\textgreater',
    }
    regex = re.compile('|'.join(re.escape(key) for key in sorted(conv.keys(), key = lambda item: - len(item))))
    return regex.sub(lambda match: conv[match.group()], text)


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
    """
    >>> pluralize(0, 'tūkstančių', 'tūkstantis', 'tūkstančiai')
    'tūkstančių'
    >>> pluralize(10, 'tūkstančių', 'tūkstantis', 'tūkstančiai')
    'tūkstančių'
    >>> pluralize(11, 'tūkstančių', 'tūkstantis', 'tūkstančiai')
    'tūkstančių'
    >>> pluralize(17, 'tūkstančių', 'tūkstantis', 'tūkstančiai')
    'tūkstančių'
    >>> pluralize(1, 'tūkstančių', 'tūkstantis', 'tūkstančiai')
    'tūkstantis'
    >>> pluralize(21, 'tūkstančių', 'tūkstantis', 'tūkstančiai')
    'tūkstantis'
    >>> pluralize(3, 'tūkstančių', 'tūkstantis', 'tūkstančiai')
    'tūkstančiai'
    >>> pluralize(23, 'tūkstančių', 'tūkstantis', 'tūkstančiai')
    'tūkstančiai'
    """
    if n % 10 == 0 or 11 <= n % 100 <= 19:
        return zero
    if n % 10 == 1:
        return singular
    else:
        return plural

def lithuanian_number(number):
    """
    >>> lithuanian_number(0)
    'nulis'
    >>> lithuanian_number(1)
    'vienas'
    >>> lithuanian_number(13)
    'trylika'
    >>> lithuanian_number(21)
    'dvidešimt vienas'
    >>> lithuanian_number(30)
    'trisdešimt'
    >>> lithuanian_number(131)
    'šimtas trisdešimt vienas'
    >>> lithuanian_number(2711)
    'du tūkstančiai septyni šimtai vienuolika'
    >>> lithuanian_number(17191)
    'septyniolika tūkstančių šimtas devyniasdešimt vienas'
    >>> lithuanian_number(1234567890)
    'milijardas du šimtai trisdešimt keturi milijonai penki šimtai šešiasdešimt septyni tūkstančiai aštuoni šimtai devyniasdešimt'
    """
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
    """
    >>> amount_words("10.50")
    'dešimt eurų, penkiasdešimt centų'
    >>> amount_words("190,00")
    'šimtas devyniasdešimt eurų, nulis centų'
    """
    euros, cents = amount.replace(",", ".").rsplit(".", 1)
    euros = int(euros)
    cents = int(cents)
    assert cents < 100
    return "{} {}, {} {}".format(lithuanian_number(euros),
                                 pluralize(euros, "eurų", "euras", "eurai"),
                                 lithuanian_number(cents),
                                 pluralize(cents, "centų", "centas", "centai"))


TEX_RENDERER = pystache.Renderer(escape=tex_escape)

def render_tex(template, data, filename=None, verbose=False):
    if filename is not None:
        filename = os.path.abspath(filename)
    with tempfile.TemporaryDirectory(prefix='render_tex') as d:
        tex = os.path.join(d, 'output.tex')
        pdf = os.path.join(d, 'output.pdf')
        with open(tex, 'w') as f:
            f.write(TEX_RENDERER.render_path(template, data, escape=tex_escape))
        try:
            out = sh.xelatex('-halt-on-error',
                             '-output-directory=' + d,
                             tex,
                             _env=dict(TEXINPUTS=TEX_PATH + ':',
                                       PATH=os.getenv("PATH")))
            if verbose:
                print(out)
        except sh.ErrorReturnCode as e:
            raise Exception("LaTeX failed with: {}".format(e.stdout.decode('utf-8')))
        if filename is None:
            with open(pdf, "rb") as f:
                return f.read()
        else:
            shutil.copyfile(pdf, filename)


def render_invoice(data, filename=None, verbose=False):
    if data["total_words"] == True:
        data["total_words"] = amount_words(str(data["total"]))
    return render_tex(INVOICE_TEMPLATE, data, filename=filename, verbose=verbose)
