# Copyright © 2015 Jeffrey Meyers
# This program is released under the "MIT License".
# Please see the file COPYING in the source
# distribution of this software for license terms.

from api import app

@app.route('/')
def index():
    return "On-Off Index"

