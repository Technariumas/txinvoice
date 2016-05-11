#!/usr/bin/env python3
import txinvoice
import bottle
import json

@bottle.post('/')
def index():
    return txinvoice.render_invoice(json.loads(bottle.request.body.read().decode('utf-8')))

if __name__ == "__main__":
    bottle.run()
