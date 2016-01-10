#!env/bin/python

# Copyright (C) 2015 Jeffrey Meyers
# This program is released under the "MIT License".
# Please see the file COPYING in the source
# distribution of this software for license terms.

from api import app
app.run(debug=True, port=9000)
