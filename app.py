from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = Flask(__name__)

db_config = {
    'host': 'ep-damp-darkness-aabzunhk-pooler.westus3.azure.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_Uo62MdzjHfEm',
    'port': 5432,
    'sslmode': 'require'
}


def get_connection():
    return psycopg2.connect(**db_config, cursor_factory=RealDictCursor)

@app.route('/post', methods=['POST'])
def post_data():
    data = request.json
    type = data.get('posttype')
    if type == "create":
        connection = None
        try:
            username = data.get('username')
            password = data.get('password')
            rname = data.get('rname')

            if not username or not password:
                return jsonify({"error": "Username and password are required"}), 400

            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (username, password, time, last) VALUES (%s, %s, %s, %s) ON CONFLICT (username) DO NOTHING",
                           (username, password, int(time.time()), int(time.time())))
            points = 0
            cursor.execute("INSERT INTO points (username, points) VALUES (%s, %s) ON CONFLICT (username) DO UPDATE SET points = EXCLUDED.points",
                           (username, points))
            cursor.execute("INSERT INTO loggedin (rname, username) VALUES (%s, %s) ON CONFLICT (rname) DO UPDATE SET username = EXCLUDED.username",
                           (rname, username))
            connection.commit()

            return jsonify({"message": "Data received!"}), 200

        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
        finally:
            if connection:
                cursor.close()
                connection.close()
    elif type == "login":
        connection = None
        try:
            connection = get_connection()
            cursor = connection.cursor()
            username = data.get('username')
            password = data.get('password')
            rname = data.get('rname')
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            if cursor.fetchone():
                cursor.execute("INSERT INTO loggedin (rname, username) VALUES (%s, %s) ON CONFLICT (rname) DO UPDATE SET username = EXCLUDED.username",
                               (rname, username))
                cursor.execute("UPDATE users SET last = %s WHERE username = %s", (int(time.time()), username))
                connection.commit()
            return jsonify({"message": "Logged In"}), 200
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
        finally:
            if connection:
                cursor.close()
                connection.close()
    elif type == "thread":
        connection = None
        try:
            connection = get_connection()
            cursor = connection.cursor()
            title = data.get('title')
            msg = data.get('message')
            threadtype = data.get('threadtype')
            username = data.get('username')
            cursor.execute("INSERT INTO threads (title, username, message, threadtype) VALUES (%s, %s, %s, %s)",
                           (title, username, msg, threadtype))
            connection.commit()
            return jsonify({"message": "Made Thread"}), 200
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
        finally:
            if connection:
                cursor.close()
                connection.close()
    elif type == "post":
        connection = None
        try:
            connection = get_connection()
            cursor = connection.cursor()
            thread = data.get('thread')
            msg = data.get('message')
            title = data.get('title')
            username = data.get('username')
            cursor.execute("INSERT INTO posts (username, message, subject, thread, time) VALUES (%s, %s, %s, %s, %s)",
                           (username, msg, title, thread, int(time.time())))
            connection.commit()
            return jsonify({"message": "Made Post"}), 200
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
        finally:
            if connection:
                cursor.close()
                connection.close()
    elif type == "view":
        connection = None
        try:
            connection = get_connection()
            cursor = connection.cursor()
            username = data.get('username')
            thread = data.get('thread')
            cursor.execute("INSERT INTO views (thread, username) VALUES (%s, %s)",
                           (thread, username))
            connection.commit()
            return jsonify({"message": "Viewed"}), 200
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
        finally:
            if connection:
                cursor.close()
                connection.close()
    elif type == "logout":
        connection = None
        try:
            connection = get_connection()
            cursor = connection.cursor()
            rname = data.get('rname')
            cursor.execute("DELETE FROM loggedin WHERE rname = %s", (rname,))
            connection.commit()
            return jsonify({"message": "Logged Out"}), 200
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
        finally:
            if connection:
                cursor.close()
                connection.close()
    elif type == "point":
        connection = None
        try:
            connection = get_connection()
            cursor = connection.cursor()
            username = data.get('username')
            points = data.get('points')
            cursor.execute("INSERT INTO points (username, points) VALUES (%s, %s) ON CONFLICT (username) DO UPDATE SET points = EXCLUDED.points",
                           (username, points))
            connection.commit()
            return jsonify({"message": "Added Points"}), 200
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
        finally:
            if connection:
                cursor.close()
                connection.close()
    else:
        return jsonify({"message": type}), 404

@app.route('/forumsthreads', methods=['GET'])
def forumthreads():
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT title, username, message, threadtype FROM threads")
        threads = cursor.fetchall()

        threads_list = [{"title": t["title"], "username": t["username"], "message": t["message"], "threadtype": t["threadtype"]} for t in threads]
        return jsonify(threads_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()

@app.route('/dynapoints', methods=['GET'])
def dynapoints():
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT username, points FROM points")
        points = cursor.fetchall()

        points_list = [{"username": p["username"], "points": p["points"]} for p in points]
        return jsonify(points_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()

@app.route('/forumsposts', methods=['GET'])
def forumposts():
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT username, message, subject, thread, time FROM posts")
        posts = cursor.fetchall()
        posts_list = [{"username": p["username"], "message": p["message"], "subject": p["subject"], "thread": p["thread"], "time": p["time"]} for p in posts]
        return jsonify(posts_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()

@app.route('/threadviews', methods=['GET'])
def threadviews():
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT thread, username FROM views")
        views = cursor.fetchall()
        views_list = [{"thread": v["thread"], "username": v["username"]} for v in views]
        return jsonify(views_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()

@app.route('/server2', methods=['GET'])
def server2():
    try:
        return jsonify("Server 2 is active")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/loggedin', methods=['GET'])
def roblox():
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT rname, username FROM loggedin")
        loggedusers = cursor.fetchall()

        user_list = [{"rname": u["rname"], "username": u["username"]} for u in loggedusers]
        return jsonify(user_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()

@app.route('/users', methods=['GET'])
def get_users():
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT username, password, time, last FROM users")
        users = cursor.fetchall()

        user_list = [{"username": u["username"], "password": u["password"], "time": u["time"], "last": u["last"]} for u in users]
        return jsonify(user_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1217)
