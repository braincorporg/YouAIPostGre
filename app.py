from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import psycopg2
import psycopg2.extras
import urllib.parse as urlparse

app = Flask(__name__)

# Rate Limiter Configuration
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/query', methods=['POST'])
@limiter.limit("10 per minute")  # Adjust rate limit as needed
def query_database():
    try:
        db_info = request.json
        url = urlparse.urlparse(db_info['database_url'])

        dbname = url.path[1:]
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port if url.port else '5432'

        connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )

        cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Parameterized query
        cursor.execute(db_info['query'], db_info.get('params', ()))

        result = cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=False)  # Set debug to False for production
