from flask import Flask
app = Flask(__name__)

import matrix
import os

hostname = os.environ.get('HOSTNAME')

@app.route('/mmul/<size>')
def matrix_multiplication(size='100'):
    res = matrix.mmul(int(size))
    return {"res": res.tolist(), "host": hostname}


@app.route('/lu/<size>')
def lu_decomposition(size='100'):
    p, l, u = matrix.lu(int(size))
    return {"p": p.tolist(), "l": l.tolist(), "u": u.tolist(), "host": hostname}


@app.route('/qr/<size>')
def qr_decomposition(size='100'):
    q, r = matrix.qr(int(size))
    return {"q": q.tolist(), "r": r.tolist(), "host": hostname}
