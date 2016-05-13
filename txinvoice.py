import pystache
import tempfile
import os
import subprocess
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


TEX_RENDERER = pystache.Renderer(escape=tex_escape)

def render_tex(template, data, filename=None):
    if filename is not None:
        filename = os.path.abspath(filename)
    with tempfile.TemporaryDirectory(prefix='render_tex') as d:
        oldpwd = os.getcwd()
        try:
            os.chdir(d)
            with open('output.tex', 'w') as tex:
                tex.write(TEX_RENDERER.render_path(template, data, escape=tex_escape))
            try:
                sh.xelatex('-halt-on-error', tex.name, _env=dict(TEXINPUTS=TEX_PATH + ':'))
            except sh.ErrorReturnCode as e:
                raise Exception("XeLaTeX failed with: {}".format(e.stdout.decode('utf-8')))
            if filename is None:
                with open("output.pdf", "rb") as f:
                    return f.read()
            else:
                os.chdir(oldpwd)
                shutil.copyfile(os.path.join(d, "output.pdf"), filename)
        finally:
            os.chdir(oldpwd)


def render_invoice(data, filename=None):
    return render_tex(INVOICE_TEMPLATE, data, filename=filename)
