from flask import Flask, request, jsonify
import psycopg2
import psycopg2.extras
import urllib.parse as urlparse

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def query_database():
    try:
        # Get connection URL from the request
        db_info = request.json
        url = urlparse.urlparse(db_info['database_url'])

        dbname = url.path[1:]
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port if url.port else '5432'  # Default PostgreSQL port

        # Establish a connection using the URL details
        connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )

        # Execute the query
        cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(db_info['query'])
        result = cursor.fetchall()

        # Close connection
        cursor.close()
        connection.close()

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
