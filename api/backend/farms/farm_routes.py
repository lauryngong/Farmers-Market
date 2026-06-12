from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from backend.utils import error_response
from mysql.connector import Error

farms_bp = Blueprint("farms", __name__)


# GET: single farm by farm_id with location details
@farms_bp.route("/farm_id/<int:farm_id>", methods=["GET"])
def get_farm(farm_id):
    current_app.logger.info(f'GET /farms/farm_id/{farm_id}')
    try:
        query = """
            SELECT f.farm_id,
                f.farm_name,
                f.user_id,
                u.user_name AS owner_name,
                f.country,
                f.latitude,
                f.longitude,
                f.created_at,
            FROM farms f
            LEFT JOIN users u ON f.user_id = u.user_id
            WHERE f.farm_id = %s
        """
        with get_db().cursor(dictionary=True, buffered=True) as cursor:
            cursor.execute(query, (farm_id,))
            farm = cursor.fetchone()

            if not farm:
                return error_response("Farm not found", 404)

        return jsonify(farm), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_farm: {e}')
        return error_response(str(e))


# GET: all farms for a user, 
@farms_bp.route("/user/<int:user_id>", methods=["GET"])
def get_farm_by_user(user_id):
    current_app.logger.info(f'GET /farms/user/{user_id}')
    try:
        query = """
            SELECT f.farm_id,
                f.farm_name,
                f.user_id,
                u.user_name AS owner_name,
                f.created_at,
                f.country,
                f.latitude,
                f.longitude
            FROM farms f
            LEFT JOIN users u ON f.user_id = u.user_id
            WHERE f.user_id = %s
        """
        with get_db().cursor(dictionary=True, buffered=True) as cursor:
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            if not rows:
                return error_response("You do not own any farms!", 404)
        return jsonify(rows), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_farm_by_user: {e}')
        return error_response(str(e))


# POST: create a farm and its first location atomically
@farms_bp.route("/", methods=["POST"])
def create_farm():
    current_app.logger.info('POST /farms/')
    data = request.get_json()

    required_farm = ["farm_name", "user_id", "created_by"]
    required_loc  = ["longitude", "latitude", "country"]

    missing = [f for f in required_farm + required_loc if f not in data]
    if missing:
        return error_response(f"Missing required fields: {missing}", 400)

    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO farms (farm_name, longitude, latitude, country, user_id, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data["farm_name"], data["longitude"], data["latitude"],
            data["country"], data["user_id"], data["created_by"]))
        farm_id = cur.lastrowid
        conn.commit()
        cur.close()
        return jsonify({"message": "Farm created", "farm_id": farm_id}), 201
    except Error as e:
        conn.rollback()
        current_app.logger.error(f"DB error: {e}")
        return error_response("Failed to create farm", 500)


# PUT: update a farm
@farms_bp.route("/farm_id/<int:farm_id>", methods=["PUT"])
def update_farm(farm_id):
    current_app.logger.info(f'PUT /farms/farm_id/{farm_id}')
    data = request.get_json()

    if "farm_name" not in data:
        return error_response("Missing required field: farm_name", 400)
    if "updated_by" not in data:
        return error_response("Missing required field: updated_by", 400)

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE farms
            SET farm_name = %s, longitude = %s, latitude = %s,
            country = %s, updated_by = %s
            WHERE farm_id = %s
        """, (data["farm_name"], data["longitude"], data["latitude"], data["country"], data["updated_by"], farm_id))
        conn.commit()
        if cur.rowcount == 0:
            cur.close()
            return error_response("Farm not found", 404)
        cur.close()
        return jsonify({"message": "Farm updated"}), 200
    except Error as e:
        current_app.logger.error(f"DB error: {e}")
        return error_response("Failed to update farm", 500)


# DELETE: remove a farm (cascade handles locations + growing records)
@farms_bp.route("/farm_id/<int:farm_id>", methods=["DELETE"])
def delete_farm(farm_id):
    current_app.logger.info(f'DELETE /farms/farm_id/{farm_id}')
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM farms WHERE farm_id = %s", (farm_id,))
        conn.commit()
        if cur.rowcount == 0:
            cur.close()
            return error_response("Farm not found", 404)
        cur.close()
        return jsonify({"message": "Farm deleted"}), 200
    except Error as e:
        current_app.logger.error(f"DB error: {e}")
        return error_response("Failed to delete farm", 500)