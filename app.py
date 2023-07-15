from flask import Flask, request
import pymssql
import datetime
import jwt
from flask import jsonify


def db_connect():
    global conn
    conn = pymssql.connect("host=db_host", "user=db_user", "password=db_password", "database=db_name", charset='ISO'
                                                                                                             '-8859-9')

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Uye')


app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello!</p>"


@app.route("/uyegiris")
def uyegiris():
    TC = request.args.get('TC')
    Sifre = request.args.get('Sifre')

    cursor2 = conn.cursor()
    query = "SELECT * FROM Uye WHERE TC = '" + str(TC) + "' AND (Tel1 = '" + str(Sifre) + "' OR Tel2 = '" + str(
        Sifre) + "')"
    print(query)
    cursor2.execute(query)

    token = generate_token(TC)
    rows = cursor2.fetchone()

    if rows:
        return token


def generate_token(TC):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(days=50)

    payload = {
        'username': TC,
        'exp': expiration
    }

    token = jwt.encode(payload, 'YOUR SECRET KEY', algorithm='HS256')

    return token


@app.route('/validate_token', methods=['GET', 'POST'])
def validate_token():
    token = request.headers.get('Authorization')

    if token:
        token = token.replace('Bearer ', '')

        try:
            decoded_token = jwt.decode(token, 'YOUR SECRET KEY', algorithms=['HS256'])
            username = decoded_token.get('username')

            return jsonify({'valid': True}), 200

        except jwt.ExpiredSignatureError:

            return jsonify({'valid': False}), 401

        except jwt.InvalidTokenError:

            return jsonify({'valid': False}), 401

    else:

        return jsonify({'valid': False}), 401


@app.route('/user_paket', methods=['GET'])
def get_user_paket():
    token = request.headers.get('Authorization')

    if token:
        token = token.replace('Bearer ', '')

        try:
            decoded_token = jwt.decode(token, 'YOUR SECRET KEY', algorithms=['HS256'])
            username = decoded_token.get('username')

            cursor = conn.cursor()
            query = "SELECT * FROM Uye WHERE TC = %s"
            cursor.execute(query, (username,))
            user_info = cursor.fetchone()

            query = "SELECT * FROM UyePaket WHERE UyeId = %d"
            cursor.execute(query, (int(user_info[0]),))
            user_paket = cursor.fetchone()

            if user_paket:
                return jsonify({
                    'Id': user_paket[0],
                    'UyeId': user_paket[1],
                    'Paket': user_paket[2],
                    'Tutar': user_paket[3],


                }), 200, {'Content-Type': 'application/json'}

            else:
                return jsonify({'error': 'Kullanıcı bulunamadı'}), 404

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Geçersiz veya süresi dolmuş token'}), 401

        except jwt.InvalidTokenError:
            return jsonify({'error': 'Geçersiz token'}), 401

    else:
        return jsonify({'error': 'Token bulunamadı'}), 401


@app.route('/user_info', methods=['GET'])
def get_user_info():
    token = request.headers.get('Authorization')

    if token:
        token = token.replace('Bearer ', '')

        try:
            decoded_token = jwt.decode(token, 'YOUR SECRET KEY', algorithms=['HS256'])
            username = decoded_token.get('username')

            cursor = conn.cursor()
            query = "SELECT * FROM Uye WHERE TC = %s"
            cursor.execute(query, (username,))
            user_info = cursor.fetchone()

            if user_info:
                return jsonify({
                    'Id': user_info[0],
                    'TC': user_info[1],
                    'Ad': user_info[2],
                    'Soyad': user_info[3],


                }), 200, {'Content-Type': 'application/json'}

            else:
                return jsonify({'error': 'Kullanıcı bulunamadı'}), 404

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Geçersiz veya süresi dolmuş token'}), 401

        except jwt.InvalidTokenError:
            return jsonify({'error': 'Geçersiz token'}), 401

    else:
        return jsonify({'error': 'Token bulunamadı'}), 401



if __name__ == '__main__':
    db_connect()
    app.run(debug=True)
