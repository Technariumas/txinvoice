import pystache
import tempfile
import os
import sh
import shutil
import re
from amount_words import amount_words

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
    if data.get("total_words", False) == True:
        data["total_words"] = amount_words(str(data["total"]))
    return render_tex(INVOICE_TEMPLATE, data, filename=filename, verbose=verbose)
