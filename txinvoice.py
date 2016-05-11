import pystache
import tempfile
import os
import subprocess
import sh

PACKAGE_PATH = os.path.abspath(os.path.dirname(__file__))
INVOICE_TEMPLATE = os.path.join(os.path.dirname(__file__), "invoice_template.tex")

def render_tex(template, data):
    with open(template) as f:
        template_text = f.read()
    with tempfile.TemporaryDirectory(prefix='render_tex') as d:
        oldpwd = os.getcwd()
        try:
            os.chdir(d)
            out = open('output.tex', 'w')
            out.write(pystache.render(template_text, data))
            out.close()
            sh.xelatex(out.name, _env=dict(TEXINPUTS=PACKAGE_PATH + ':'))
            with open("output.pdf", "rb") as f:
                return f.read()
        finally:
            os.chdir(oldpwd)


def render_invoice(data):
    return render_tex(INVOICE_TEMPLATE, data)
