import os

import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template


load_dotenv()  #by this python can you access the .env and get info like os.getenv("DB_HOST") 

app = Flask(__name__)  #creates flask application and stores it in app


def get_db_connection():
    return psycopg2.connect(           #connects to postgreSQL database
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        dbname=os.getenv("DB_NAME")
    )

@app.route("/") #when visited / it calls the home function
def home():
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health():
    try:
        conn = get_db_connection() #conn represents my connection.
        cursor = conn.cursor() #cursor is used to send SQL commands and retrive results.

        cursor.execute("SELECT 1;") #SELECT 1 is a sql command, means send this sql command to postgreSQL

        cursor.close()
        conn.close()

        return jsonify({"status": "healthy"}), 200

    except Exception as e:
        return jsonify({"status": "unhealthy"}), 500


@app.route("/api/poll", methods=["GET"])
def get_poll():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM poll_options ORDER BY id;")

    rows = cursor.fetchall() #fetch all the rows

    cursor.close()
    conn.close()

    poll_options = []

    for row in rows:
        poll_options.append({
            "id": row[0],
            "option_name": row[1],
            "votes": row[2]
        })

    return jsonify(poll_options)


@app.route("/api/vote", methods=["POST"])
def vote():
    data = request.get_json()

    option_id = data.get("id")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE poll_options SET votes = votes + 1 WHERE id = %s;",
        (option_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Vote recorded"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)