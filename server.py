#!/usr/bin/env python3
import txinvoice
import bottle
import json

import argparse

parser = argparse.ArgumentParser(description='Invoice generation server')
parser.set_defaults(verbose=False)
parser.add_argument('--host', default='127.0.0.1', help='server host')
parser.add_argument('--port', default=8080, type=int, help='server port')
parser.add_argument('--verbose', action='store_true', help='show TeX output')
args = parser.parse_args()

@bottle.post('/')
def index():
    return txinvoice.render_invoice(json.loads(bottle.request.body.read().decode('utf-8')),
                                    verbose=args.verbose)

bottle.run(host=args.host, port=args.port)
