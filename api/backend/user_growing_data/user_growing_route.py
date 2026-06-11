from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from backend.utils import error_response
from mysql.connector import Error

user_growing_bp = Blueprint("user_growing", __name__)


@user_growing_bp.route("/", methods=["GET"])
def get_all_user_growing():
    current_app.logger.info('GET /user_growing')
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM user_growing_data")
        rows = cur.fetchall()
        cur.close()
        return jsonify(rows), 200
    except Error as e:
        current_app.logger.error(f"DB error: {e}")
        return error_response("Failed to fetch user_growing_data", 500)


@user_growing_bp.route("/<int:user_growing_data_id>", methods=["GET"])
def get_data_by_data_id(user_growing_data_id):
    current_app.logger.info(f'GET /user_growing/{user_growing_data_id}')
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM user_growing_data WHERE user_growing_data = %s",
            (user_growing_data_id,)
        )
        row = cur.fetchone()
        cur.close()
        if row is None:
            return error_response("user_growing_data not found", 404)
        return jsonify(row), 200
    except Error as e:
        current_app.logger.error(f"DB error: {e}")
        return error_response("Failed to fetch user_growing_data", 500)


@user_growing_bp.route("/farm/<int:farm_id>", methods=["GET"])
def get_data_by_farm_id(farm_id):
    current_app.logger.info(f'GET /user_growing/farm/{farm_id}')
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        # fetchall — a farm has MANY growing records
        cur.execute(
            """
            SELECT
                user_growing_data_id,
                type_of_crop, season, sown, harvested,
                DATEDIFF(harvested, sown) AS duration_days,
                water_source, temp, relative_humidity, n, p, k
            FROM user_growing_data
            WHERE farm_id = %s
            ORDER BY sown DESC
            """,
            (farm_id,)
        )
        rows = cur.fetchall()   # was fetchone — wrong, a farm has many records
        cur.close()
        if not rows:
            return error_response("No growing data found for this farm", 404)
        return jsonify(rows), 200
    except Error as e:
        current_app.logger.error(f"DB error: {e}")
        return error_response("Failed to fetch user_growing_data", 500)


@user_growing_bp.route("/count", methods=["GET"])
def get_user_growing_count():
    current_app.logger.info('GET /user_growing/count')
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) AS count FROM user_growing_data")
        row = cur.fetchone()
        cur.close()
        return jsonify(row), 200
    except Error as e:
        current_app.logger.error(f"DB error: {e}")
        return error_response("Failed to fetch user_growing_data", 500)


@user_growing_bp.route("/count-by-crop", methods=["GET"])
def get_user_growing_count_by_crop():
    current_app.logger.info('GET /user_growing/count-by-crop')
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT type_of_crop, COUNT(*) AS count "
            "FROM user_growing_data "
            "GROUP BY type_of_crop "
            "ORDER BY count DESC, type_of_crop ASC"
        )
        rows = cur.fetchall()
        cur.close()
        return jsonify(rows), 200
    except Error as e:
        current_app.logger.error(f"DB error: {e}")
        return error_response("Failed to fetch user_growing_data", 500)
    
@user_growing_bp.route("/count-by-farm", methods=["GET"])
def get_user_growing_count_by_farm():
    current_app.logger.info('GET /user_growing/count-by-crop')
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT farm_id, COUNT(*) AS count "
            "FROM user_growing_data "
            "GROUP BY farm_id "
            "ORDER BY count DESC, farm_id ASC"
        )
        rows = cur.fetchall()
        cur.close()
        return jsonify(rows), 200
    except Error as e:
        current_app.logger.error(f"DB error: {e}")
        return error_response("Failed to fetch user_growing_data", 500)


# NEW: map join — accepts optional ?season= and ?crop= query params
@user_growing_bp.route("/map-data", methods=["GET"])
def get_map_data():
    current_app.logger.info('GET /user_growing/map-data')
    season = request.args.get("season")   # e.g. ?season=Monsoon (Kharif)
    crop   = request.args.get("crop")     # e.g. ?crop=Cereals

    where_clauses = []
    params = []

    if season:
        where_clauses.append("ugd.season = %s")
        params.append(season)
    if crop:
        where_clauses.append("ugd.type_of_crop = %s")
        params.append(crop)

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    query = f"""
        SELECT
            f.farm_id,
            f.farm_name,
            f.latitude,
            f.longitude,
            f.country,
            (
                SELECT ugd2.type_of_crop
                FROM user_growing_data ugd2
                WHERE ugd2.farm_id = f.farm_id
                GROUP BY ugd2.type_of_crop
                ORDER BY COUNT(*) DESC
                LIMIT 1
            ) AS dominant_crop,
            MAX(CASE WHEN ugd.water_source = 'irrigated' THEN 1 ELSE 0 END)
                AS has_irrigated,
            AVG(ugd.temp)               AS avg_temp,
            AVG(ugd.relative_humidity)  AS avg_humidity,
            COUNT(ugd.user_growing_data_id) AS record_count
        FROM farms f
        LEFT JOIN user_growing_data ugd  ON f.farm_id = ugd.farm_id
        {where_sql}
        GROUP BY f.farm_id, f.farm_name, f.latitude, f.longitude, f.country
    """

    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params)
        rows = cur.fetchall()
        cur.close()
        return jsonify(rows), 200
    except Error as e:
        current_app.logger.error(f"DB error: {e}")
        return error_response("Failed to fetch map data", 500)


# NEW: summary stats for the overview tab metrics
@user_growing_bp.route("/stats", methods=["GET"])
def get_stats():
    current_app.logger.info('GET /user_growing/stats')
    season = request.args.get("season")
    where_sql = "WHERE season = %s" if season else ""
    params = [season] if season else []

    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute(f"""
            SELECT
                COUNT(*)                                    AS total_observations,
                (SELECT COUNT(*) FROM farms)                AS total_farms,
                COUNT(DISTINCT type_of_crop)                AS crop_types,
                COUNT(DISTINCT water_source)                AS water_sources,
                ROUND(
                    100.0 * SUM(water_source = 'rainfed') / COUNT(*), 1
                )                                           AS rainfed_pct
            FROM user_growing_data
            {where_sql}
        """, params)
        row = cur.fetchone()
        cur.close()
        return jsonify(row), 200
    except Error as e:
        current_app.logger.error(f"DB error: {e}")
        return error_response("Failed to fetch stats", 500)


# NEW: duration aggregated by crop + water source (for trend charts)
@user_growing_bp.route("/duration-by-crop", methods=["GET"])
def get_duration_by_crop():
    current_app.logger.info('GET /user_growing/duration-by-crop')
    season = request.args.get("season")
    where_sql = "WHERE season = %s" if season else ""
    params = [season] if season else []

    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute(f"""
            SELECT
                type_of_crop,
                water_source,
                ROUND(AVG(DATEDIFF(harvested, sown)), 1) AS avg_duration,
                COUNT(*) AS n
            FROM user_growing_data
            {where_sql}
            GROUP BY type_of_crop, water_source
            ORDER BY avg_duration DESC
        """, params)
        rows = cur.fetchall()
        cur.close()
        return jsonify(rows), 200
    except Error as e:
        current_app.logger.error(f"DB error: {e}")
        return error_response("Failed to fetch duration by crop", 500)
    
@user_growing_bp.route("/", methods=["POST"])
def create_growing_record():
    current_app.logger.info('POST /user_growing')
    data = request.get_json()

    required = ["farm_id", "n", "p", "k", "type_of_crop", "season",
                "sown", "harvested", "water_source", "temp",
                "relative_humidity", "created_by"]
    missing = [f for f in required if f not in data]
    if missing:
        return error_response(f"Missing required fields: {missing}", 400)

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO user_growing_data
                (farm_id, n, p, k, type_of_crop, season, sown, harvested,
                 water_source, temp, relative_humidity, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data["farm_id"],
            data["n"],
            data["p"],
            data["k"],
            data["type_of_crop"],
            data["season"],
            data["sown"],
            data["harvested"],
            data["water_source"],
            data["temp"],
            data["relative_humidity"],
            data["created_by"],
        ))
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        return jsonify({"message": "Growing record created", "user_growing_data_id": new_id}), 201
    except Error as e:
        current_app.logger.error(f"DB error: {e}")
        return error_response("Failed to create growing record", 500)


# PUT: update an existing growing record
@user_growing_bp.route("/<int:user_growing_data_id>", methods=["PUT"])
def update_growing_record(user_growing_data_id):
    current_app.logger.info(f'PUT /user_growing/{user_growing_data_id}')
    data = request.get_json()

    updatable = ["n", "p", "k", "type_of_crop", "season", "sown",
                 "harvested", "water_source", "temp", "relative_humidity"]
    updates = {k: v for k, v in data.items() if k in updatable}
    if not updates:
        return error_response("No valid fields to update", 400)
    if "updated_by" not in data:
        return error_response("Missing required field: updated_by", 400)

    updates["updated_by"] = data["updated_by"]
    set_clause = ", ".join(f"{col} = %s" for col in updates)
    params = list(updates.values()) + [user_growing_data_id]

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(f"""
            UPDATE user_growing_data
            SET {set_clause}
            WHERE user_growing_data_id = %s
        """, params)
        conn.commit()
        cur.close()
        if cur.rowcount == 0:
            return error_response("Record not found", 404)
        return jsonify({"message": "Growing record updated"}), 200
    except Error as e:
        current_app.logger.error(f"DB error: {e}")
        return error_response("Failed to update growing record", 500)


# DELETE: remove a growing record
@user_growing_bp.route("/<int:user_growing_data_id>", methods=["DELETE"])
def delete_growing_record(user_growing_data_id):
    current_app.logger.info(f'DELETE /user_growing/{user_growing_data_id}')
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM user_growing_data WHERE user_growing_data_id = %s",
            (user_growing_data_id,)
        )
        conn.commit()
        cur.close()
        if cur.rowcount == 0:
            return error_response("Record not found", 404)
        return jsonify({"message": "Growing record deleted"}), 200
    except Error as e:
        current_app.logger.error(f"DB error: {e}")
        return error_response("Failed to delete growing record", 500)
