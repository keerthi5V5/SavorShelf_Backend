import re
import os
import random
import smtplib
from datetime import datetime, timedelta, date
import cv2
import numpy as np
import pymysql
import pytesseract
from PIL import Image
from apscheduler.schedulers.background import BackgroundScheduler
from email.message import EmailMessage
from flask import Flask, request, jsonify, session, send_from_directory 
from flask_mail import Mail, Message
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
# (Keep your imports here if you are using them)
# ==========================================================
# ✅ APP INIT
# ==========================================================
app = Flask(__name__)
CORS(app)
app.secret_key = "supersecretkey"

# Path for Labeled (User-taken) photos
UPLOAD_FOLDER = 'uploads/products'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# ==========================================================
# ✅ MAIL CONFIG
# ==========================================================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'savorshelf1.0@gmail.com'
app.config['MAIL_PASSWORD'] = 'eoekijzviyyhbgsy'
mail = Mail(app)
# ==========================================================
# ✅ TESSERACT CONFIG
# ==========================================================
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# ==========================================================
# ✅ CONSTANTS
# ==========================================================
WEEKDAY_MAP = {
    "Sunday": 6,
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5
}
TIMING_TO_DAYS = {
    "1 day before": 1,
    "2 days before": 2,
    "3 days before": 3,
    "4 days before": 4,
    "5 days before": 5
}
VALID_UNLABELED_CATEGORIES = [
    "Fruits", "Vegetables", "Leafy Greens", "Meat & Seafood", "Dairy", "Herbs & Seasonings", "Others"
]
CATEGORY_NAME_MAP = {
    "Fruits": "fruits",
    "Vegetables": "vegetables",
    "Leafy Greens": "leafy_greens",
    "Meat & Seafood": "meat_and_seafood",
    "Dairy": "dairy",
    "Herbs & Seasonings": "herbs_and_seasonings"
}
VALID_STORAGE_TYPES = [
    "Fridge", "Freezer", "Room Temperature", "Pantry"
]
STORAGE_NORMALIZATION = {
    "Fridge": "Fridge",
    "Freezer": "Freezer",
    "Pantry": "Room Temperature",
    "Room Temperature": "Room Temperature"
}
CATEGORY_DEFAULTS = {
    "Fruits": 7,
    "Vegetables": 10,
    "Leafy Greens": 5,
    "Meat & Seafood": 3,
    "Dairy": 7,
    "Herbs & Seasonings": 14,
    "Others": 7
}

# ==========================================================
# ✅ DATABASE CONNECTION (DB NAME: savorshelf)
# ==========================================================
def get_db_connection():
    try:
        conn = pymysql.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="savorshelf",
            port=3306,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
        return conn
    except Exception as e:
        print("❌ Error while connecting to MySQL:", e)
        return None
def ensure_column(cursor, table_name, column_name, definition):
    cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE %s", (column_name,))
    if not cursor.fetchone():
        print(f"⚠️  Adding column {table_name}.{column_name}")
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")
def init_db():
    conn = get_db_connection()
    if not conn:
        print("❌ Database Migration Error: Could not connect to DB.")
        return
    try:
        with conn.cursor() as cursor:
            # 1. Ensure 'register' table (Users) exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS register (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    full_name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    otp VARCHAR(10) NULL,
                    otp_expiry DATETIME NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 2. Ensure 'user_alert_settings' table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_alert_settings (
                    user_id INT PRIMARY KEY,
                    is_enabled BOOLEAN DEFAULT TRUE,
                    expiry_days_before INT DEFAULT 3,
                    expiry_alert_time TIME DEFAULT '09:00:00',
                    weekly_summary_enabled BOOLEAN DEFAULT TRUE,
                    weekly_summary_day VARCHAR(20) DEFAULT 'Sunday',
                    weekly_summary_time TIME DEFAULT '09:00:00',
                    critical_alert_enabled BOOLEAN DEFAULT TRUE,
                    critical_alert_time TIME DEFAULT '09:00:00',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            # 3. Ensure 'notifications' table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    pantry_item_id INT NULL,
                    title VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    type VARCHAR(50) NULL,
                    is_unread BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 4. Ensure 'shelf_life_data' table exists (For fresh estimations)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shelf_life_data (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    item_name VARCHAR(100) UNIQUE NOT NULL,
                    fridge INT DEFAULT 7,
                    freezer INT DEFAULT 30,
                    room_temperature INT DEFAULT 3
                )
            """)
            ensure_column(cursor, "shelf_life_data", "fridge", "INT DEFAULT 7")
            ensure_column(cursor, "shelf_life_data", "freezer", "INT DEFAULT 30")
            ensure_column(cursor, "shelf_life_data", "room_temperature", "INT DEFAULT 3")
            # 5. Ensure 'pantry_items' table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pantry_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    item_name VARCHAR(255) NOT NULL,
                    category VARCHAR(100) NULL,
                    storage_type VARCHAR(100) NULL,
                    expiry_date DATE NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    image_path VARCHAR(255) NULL,
                    lot_number VARCHAR(100) NULL,
                    is_labeled BOOLEAN DEFAULT 0,
                    status VARCHAR(50) DEFAULT 'active'
                )
            """)
            # 6. Apply pantry_items migrations (ensuring extra columns exist)
            ensure_column(cursor, "pantry_items", "updated_at", "DATETIME NULL")
            ensure_column(cursor, "pantry_items", "quantity", "VARCHAR(100) NULL")
            ensure_column(cursor, "pantry_items", "purchase_date", "DATE NULL")
            ensure_column(cursor, "pantry_items", "mfg_date", "DATE NULL")
            ensure_column(cursor, "pantry_items", "hidden_from_products", "BOOLEAN DEFAULT 0")
            ensure_column(cursor, "pantry_items", "pending_weekly_cleanup", "BOOLEAN DEFAULT 0")
            ensure_column(cursor, "pantry_items", "expired_hidden_at", "DATETIME NULL")
            ensure_column(cursor, "pantry_items", "deleted_at", "DATETIME NULL")
            # 7. Check alert settings columns
            cursor.execute("SHOW COLUMNS FROM user_alert_settings")
            existing_cols = [row['Field'] for row in cursor.fetchall()]
            expected_cols = {
                "is_enabled": "BOOLEAN DEFAULT TRUE",
                "expiry_days_before": "INT DEFAULT 3",
                "expiry_alert_time": "TIME DEFAULT '09:00:00'",
                "weekly_summary_enabled": "BOOLEAN DEFAULT TRUE",
                "weekly_summary_day": "VARCHAR(20) DEFAULT 'Sunday'",
                "weekly_summary_time": "TIME DEFAULT '09:00:00'",
                "critical_alert_enabled": "BOOLEAN DEFAULT TRUE",
                "critical_alert_time": "TIME DEFAULT '09:00:00'"
            }
            for col, definition in expected_cols.items():
                if col not in existing_cols:
                    cursor.execute(f"ALTER TABLE user_alert_settings ADD COLUMN {col} {definition}")
            conn.commit()
            print("✅ Database initialization / migration complete.")
    except Exception as e:
        print(f"❌ Database Initialization Error: {e}")
        conn.rollback()
    finally:
        conn.close()
# ==========================================================
# ✅ SAFE INT HELPER
# ==========================================================
def _to_int(v, default=None):
    try:
        return int(v)
    except:
        return default
# ==========================================================
# ✅ Web Render (Clean URLs Support)
# ==========================================================
@app.route('/')
def index():
    return send_from_directory('Web_Application', 'index.html')

@app.route('/<path:filename>')
def render_spa(filename):
    # If the file exists directly (css, js, images), serve it
    if os.path.exists(os.path.join('Web_Application', filename)):
        return send_from_directory('Web_Application', filename)
    
    # If the filename + .html exists, serve that (for clean URLs like /dashboard)
    html_file = filename + '.html'
    if os.path.exists(os.path.join('Web_Application', html_file)):
        return send_from_directory('Web_Application', html_file)
    
    # Fallback to index.html for SPA behavior or 404
    return send_from_directory('Web_Application', 'index.html')
# ==========================================================
# ✅ PASSWORD VALIDATOR
# ==========================================================
def validate_password(password):
    missing = []
    if len(password) < 6:
        missing.append("at least 6 characters")
    if not any(c.islower() for c in password):
        missing.append("one lowercase letter")
    if not any(c.isupper() for c in password):
        missing.append("one uppercase letter")
    if not any(c.isdigit() for c in password):
        missing.append("one numerical digit")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        missing.append("one special character")
    return missing
# ==========================================================
# ✅ BASIC TEST ROUTE
# ==========================================================
@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "success", "message": "savorshelf backend running ✅"}), 200
# ==========================================================
# ✅ NOTIFICATION HELPERS
# ==========================================================
def parse_time_12h(time_str, default="9:00 AM"):
    try:
        return datetime.strptime((time_str or default).strip(), "%I:%M %p").strftime("%H:%M:%S")
    except Exception:
        return datetime.strptime(default, "%I:%M %p").strftime("%H:%M:%S")
def format_time_24_to_12(time_value):
    try:
        if isinstance(time_value, timedelta):
            total_seconds = int(time_value.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            dt = datetime.strptime(f"{hours:02d}:{minutes:02d}:00", "%H:%M:%S")
            return dt.strftime("%I:%M %p").lstrip("0")
        if isinstance(time_value, str):
            return datetime.strptime(time_value, "%H:%M:%S").strftime("%I:%M %p").lstrip("0")
        return str(time_value)
    except Exception:
        return "9:00 AM"
def parse_frontend_date(date_str):
    if not date_str:
        return None
    for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y", "%m/%d/%Y"]:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except Exception:
            pass
    return None
def parse_to_sql_date(date_str):
    return parse_frontend_date(date_str)
def slugify_path(name):
    if not name:
        return ""
    name = name.replace('&', 'and')
    name = re.sub(r'[^a-zA-Z0-9]', '_', name)
    name = re.sub(r'_+', '_', name).strip('_')
    return name.lower()
def fix_url(url, host=None):
    if not url:
        return f"{host.rstrip('/')}/static/default.jpg" if host else "/static/default.jpg"
    if url.startswith("http"):
        url = url.replace("127.0.0.1", "10.0.2.2").replace("localhost", "10.0.2.2")
        for folder in ["/uploads/", "/static/"]:
            if folder in url:
                url = url[url.find(folder):]
                break
    if url.startswith("/"):
        return f"{host.rstrip('/')}{url}" if host else url
    if url.startswith("uploads/") or url.startswith("static/"):
        return f"{host.rstrip('/')}/{url}" if host else f"/{url}"
    return url
def resolve_static_image(category_name, item_name):
    cat_slug = CATEGORY_NAME_MAP.get(category_name) or slugify_path(category_name)
    static_folder = os.path.join(app.root_path, 'static', cat_slug)
    if not os.path.exists(static_folder):
        return "/static/default.jpg"
    def get_fuzzy_slug(s):
        return re.sub(r'[^a-z0-9]', '', (s or '').lower())
    target_slug = get_fuzzy_slug(item_name)
    try:
        files = [f for f in os.listdir(static_folder) if not f.lower().endswith('.ini')]
        files.sort()
        for f in files:
            if get_fuzzy_slug(os.path.splitext(f)[0]) == target_slug:
                return f"/static/{cat_slug}/{f}"
        for f in files:
            f_slug = get_fuzzy_slug(os.path.splitext(f)[0])
            if target_slug and f_slug and (target_slug in f_slug or f_slug in target_slug):
                return f"/static/{cat_slug}/{f}"
    except Exception as e:
        print(f"❌ Error resolving image: {e}")
    return f"/static/{cat_slug}/{slugify_path(item_name)}.jpg"
def ensure_jpg(image_path):
    try:
        if not image_path.lower().endswith(".jpg"):
            img = Image.open(image_path)
            new_path = os.path.splitext(image_path)[0] + ".jpg"
            img.convert('RGB').save(new_path, "JPEG")
            os.remove(image_path)
            return new_path
    except Exception as e:
        print(f"❌ Error ensuring jpg: {e}")
    return image_path
def delete_associated_images(cursor, item_ids):
    """
    Deletes images from the server for the given pantry item IDs.
    Only deletes if the item is labeled.
    """
    if not item_ids:
        return
    try:
        # Convert single ID to list if needed
        if isinstance(item_ids, (int, str)):
            item_ids = [item_ids]
        format_strings = ','.join(['%s'] * len(item_ids))
        cursor.execute(f"SELECT image_path, is_labeled FROM pantry_items WHERE id IN ({format_strings})", tuple(item_ids))
        items = cursor.fetchall()
        for item in items:
            if item.get("is_labeled") and item.get("image_path"):
                img_path = item["image_path"]
                # We only delete if it's in the uploads folder (labeled data)
                if img_path.startswith("/uploads/products/"):
                    # /uploads/products/filename.jpg -> uploads/products/filename.jpg
                    rel_path = img_path.lstrip("/") 
                    abs_path = os.path.join(app.root_path, rel_path)
                    # 1. Delete Front Image
                    if os.path.exists(abs_path):
                        os.remove(abs_path)
                        print(f"🗑️ Deleted front image: {abs_path}")
                    # 2. Delete Expiry Image (Derive name: front -> expiry)
                    if "_front.jpg" in abs_path:
                        expiry_path = abs_path.replace("_front.jpg", "_expiry.jpg")
                        if os.path.exists(expiry_path):
                            os.remove(expiry_path)
                            print(f"🗑️ Deleted expiry image: {expiry_path}")
    except Exception as e:
        print(f"❌ Error deleting associated images: {e}")
def get_shelf_life_from_db(item_name, storage_type, category=None):
    if not item_name:
        raw_val = CATEGORY_DEFAULTS.get(category, 7)
        return apply_food_safety_rules(item_name, storage_type, category, raw_val)
    conn = get_db_connection()
    if not conn:
        raw_val = CATEGORY_DEFAULTS.get(category, 7)
        return apply_food_safety_rules(item_name, storage_type, category, raw_val)
    try:
        with conn.cursor() as cursor:
            # Normalize storage type
            storage_lower = (storage_type or "").lower()
            # --- PRIORITY 1: Check 'shelf_life_data' (The Seeded Dataset) ---
            ld_col_map = {"room temperature": "room_temperature", "fridge": "fridge", "freezer": "freezer"}
            ld_target = ld_col_map.get(storage_lower, "fridge")
            # 1. Exact match
            cursor.execute(f"SELECT {ld_target} FROM shelf_life_data WHERE item_name=%s", (item_name,))
            res = cursor.fetchone()
            if res and res.get(ld_target) is not None:
                return apply_food_safety_rules(item_name, storage_type, category, int(res[ld_target]))
            # 2. Fuzzy match
            cursor.execute(f"""
                SELECT {ld_target} FROM shelf_life_data 
                WHERE %s LIKE CONCAT('%%', item_name, '%%') 
                OR item_name LIKE CONCAT('%%', %s, '%%')
                ORDER BY LENGTH(item_name) DESC LIMIT 1
            """, (item_name, item_name))
            res = cursor.fetchone()
            if res and res.get(ld_target) is not None:
                return apply_food_safety_rules(item_name, storage_type, category, int(res[ld_target]))
            cursor.execute(f"""
                SELECT {ld_target} FROM shelf_life_data 
                WHERE %s LIKE CONCAT('%%', item_name, '%%') 
                OR item_name LIKE CONCAT('%%', %s, '%%')
                ORDER BY LENGTH(item_name) DESC LIMIT 1
            """, (item_name, item_name))
            res = cursor.fetchone()
            if res and res.get(ld_target) is not None:
                return apply_food_safety_rules(item_name, storage_type, category, int(res[ld_target]))
            # --- PRIORITY 3: Fallback ---
            raw_val = CATEGORY_DEFAULTS.get(category, 7)
            return apply_food_safety_rules(item_name, storage_type, category, raw_val)
    except Exception as e:
        print(f"❌ Error in get_shelf_life_from_db: {e}")
        return CATEGORY_DEFAULTS.get(category, 7)
    finally:
        conn.close()
def get_item_total_life_days(item):
    expiry_date = item.get("expiry_date")
    if not expiry_date:
        return 0
    # Determine start date: Prioritize explicit dates, fallback to creation date
    if item.get("is_labeled"):
        start_date = item.get("mfg_date")
    else:
        start_date = item.get("purchase_date")
    if not start_date:
        # Fallback to created_at if mfg/purchase date is missing
        created_at = item.get("created_at")
        if hasattr(created_at, 'date'):
            start_date = created_at.date()
        elif isinstance(created_at, datetime):
            start_date = created_at.date()
        else:
            start_date = date.today()
    total_days = (expiry_date - start_date).days
    return max(total_days, 1) # Ensure at least 1 to avoid div by zero
def calculate_freshness(item):
    today = date.today()
    expiry_date = item.get("expiry_date")
    # Consistent start date logic
    if item.get("is_labeled"):
        start_date = item.get("mfg_date")
    else:
        start_date = item.get("purchase_date")
    if not start_date:
        created_at = item.get("created_at")
        if hasattr(created_at, 'date'):
            start_date = created_at.date()
        elif isinstance(created_at, datetime):
            start_date = created_at.date()
        else:
            start_date = today
    if not expiry_date:
        return {
            "freshness_label": "Unknown",
            "days_remaining": 0,
            "progress": 0,
            "detail_value": "Expiry unknown",
            "start_date": start_date,
            "total_life_days": 1,
            "consumed_days": 0
        }
    total_life = get_item_total_life_days(item)
    days_remaining = (expiry_date - today).days
    consumed_days = (today - start_date).days
    # Progress: How much LIFE is left
    remaining_ratio = max(0.0, min(1.0, days_remaining / total_life))
    progress = int(round(remaining_ratio * 100))
    # Freshness Status Logic (Smart thresholds)
    if days_remaining < 0:
        freshness_label = "Expired"
        detail_value = f"Expired {abs(days_remaining)} day(s) ago"
    elif days_remaining == 0:
        freshness_label = "Use Soon"
        detail_value = "Expires today"
    else:
        # We classify based on both absolute days AND percentage of life remaining
        # This handles short-life items (meat) and long-life items (canned) accurately.
        is_use_soon = (days_remaining <= 3) or (remaining_ratio <= 0.15)
        is_moderate = (days_remaining <= 7) or (remaining_ratio <= 0.35)
        if is_use_soon:
            freshness_label = "Use Soon"
        elif is_moderate:
            freshness_label = "Moderate"
        else:
            freshness_label = "Fresh"
        detail_value = f"{days_remaining} day(s) left"
    # Add custom detail branding
    if item.get("is_labeled"):
        # Labeled products usually care about the dates more
        date_str = f"EXP: {expiry_date.strftime('%d %b %Y')}"
        detail_value = f"Labeled | {date_str}"
    qty = item.get("quantity")
    if qty and str(qty).strip():
        detail_value = f"{qty} | {detail_value}"
    return {
        "freshness_label": freshness_label,
        "days_remaining": days_remaining,
        "progress": progress,
        "detail_value": detail_value,
        "start_date": start_date,
        "total_life_days": total_life,
        "consumed_days": consumed_days
    }
def build_item_card_payload(item, host_url=None):
    f = calculate_freshness(item)
    return {
        "id": str(item.get("id")),
        "name": item.get("item_name") or "Unknown Product",
        "detailValue": f.get("detail_value") or "Status Unknown",
        "freshnessLabel": f.get("freshness_label") or "Unknown",
        "storageType": item.get("storage_type") or "Pantry",
        "imageUrl": fix_url(item.get("image_path") or "", host=host_url),
        "progress": f.get("progress", 0),
        "isLabeled": bool(item.get("is_labeled", 0)),
        "daysRemaining": f.get("days_remaining"),
        "expiryDate": item.get("expiry_date").strftime("%Y-%m-%d") if item.get("expiry_date") else None,
        "purchaseDate": item.get("purchase_date").strftime("%Y-%m-%d") if item.get("purchase_date") else None,
        "mfgDate": item.get("mfg_date").strftime("%Y-%m-%d") if item.get("mfg_date") else None,
        "quantity": item.get("quantity")
    }
def insert_notification(user_id, title, message, notif_type, pantry_item_id=None):
    conn = get_db_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO notifications
                (user_id, pantry_item_id, title, message, type, is_unread, created_at)
                VALUES (%s, %s, %s, %s, %s, 1, NOW())
            """, (user_id, pantry_item_id, title, message, notif_type))
            conn.commit()
        print(f"🔔 [NOTIF] User {user_id}: {title}")
        # NOTE:
        # DB notification is saved immediately. For real popup when mobile app is closed,
        # you must integrate Firebase Cloud Messaging (FCM) or another push service in mobile app.
        # This backend currently stores notifications for in-app display.
    except Exception as e:
        print("❌ Insert notification error:", e)
        conn.rollback()
    finally:
        conn.close()
def get_weekly_summary_enabled(cursor, user_id):
    cursor.execute("SELECT weekly_summary_enabled FROM user_alert_settings WHERE user_id=%s", (user_id,))
    row = cursor.fetchone()
    return bool(row and row.get("weekly_summary_enabled"))
def hide_or_delete_expired_items():
    """
    Rule:
    - Items expiring or marked as consumed/wasted are hidden from products immediately.
    - If weekly summary enabled: keep until summary is sent, then delete.
    - If weekly summary disabled: delete automatically 7 days after the last update (consumption/waste/expiry).
    """
    conn = get_db_connection()
    if not conn:
        print("❌ Hide/Delete expired items: DB connection failed")
        return
    try:
        with conn.cursor() as cursor:
            # 1. Hide active items that expired > 1 day ago and mark them for weekly cleanup
            cursor.execute("""
                UPDATE pantry_items
                SET hidden_from_products=1,
                    pending_weekly_cleanup=1,
                    status='wasted',
                    expired_hidden_at=COALESCE(expired_hidden_at, NOW()),
                    updated_at=NOW()
                WHERE status='active'
                  AND expiry_date IS NOT NULL
                  AND expiry_date <= CURDATE() - INTERVAL 1 DAY
                  AND hidden_from_products=0
            """)
            # 2. Permanent deletion for items that have been "hidden" (wasted/consumed/expired) for more than 7 days
            # ONLY for users where weekly summary is DISABLED (or no settings exist, meaning no summary is sent).
            # This follows the requirement: "if user disable weekly summary report, consumed and wasted items delete after a week".
            cursor.execute("""
                SELECT p.id FROM pantry_items p
                LEFT JOIN user_alert_settings s ON p.user_id = s.user_id
                WHERE (p.status IN ('consumed', 'wasted') OR p.hidden_from_products=1)
                  AND p.updated_at <= NOW() - INTERVAL 7 DAY
                  AND (s.weekly_summary_enabled IS NULL OR s.weekly_summary_enabled = 0)
            """)
            ids_to_del = [row['id'] for row in cursor.fetchall()]
            if ids_to_del:
                delete_associated_images(cursor, ids_to_del)
                format_strings = ','.join(['%s'] * len(ids_to_del))
                cursor.execute(f"DELETE FROM pantry_items WHERE id IN ({format_strings})", tuple(ids_to_del))
            conn.commit()
    except Exception as e:
        print(f"❌ hide_or_delete_expired_items error: {e}")
        if conn: conn.rollback()
    finally:
        if conn: conn.close()
def delete_pending_weekly_cleanup_items(cursor, user_id):
    cursor.execute("SELECT id FROM pantry_items WHERE user_id=%s AND pending_weekly_cleanup=1", (user_id,))
    ids = [r['id'] for r in cursor.fetchall()]
    if ids:
        delete_associated_images(cursor, ids)
        format_strings = ','.join(['%s'] * len(ids))
        cursor.execute(f"DELETE FROM pantry_items WHERE id IN ({format_strings})", tuple(ids))
def process_notifications():
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_weekday = now.weekday()
    today = date.today()
    def as_hm(t):
        if isinstance(t, timedelta):
            ts = int(t.total_seconds())
            return f"{ts // 3600:02d}:{(ts % 3600) // 60:02d}"
        if isinstance(t, str) and len(t) >= 5:
            return t[:5]
        return "09:00"
    conn = get_db_connection()
    if not conn:
        print("❌ process_notifications: DB connection failed")
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT *
                FROM user_alert_settings
                WHERE is_enabled = 1
            """)
            settings_rows = cursor.fetchall()
            for setting in settings_rows:
                user_id = setting["user_id"]
                expiry_days_before = int(setting.get("expiry_days_before") or 3)
                expiry_alert_time = as_hm(setting.get("expiry_alert_time"))
                weekly_summary_enabled = int(setting.get("weekly_summary_enabled") or 0)
                weekly_summary_day = setting.get("weekly_summary_day") or "Sunday"
                weekly_summary_time = as_hm(setting.get("weekly_summary_time"))
                critical_alert_enabled = int(setting.get("critical_alert_enabled") or 0)
                critical_alert_time = as_hm(setting.get("critical_alert_time"))
                # 1. EXPIRY BEFORE ALERT
                if current_time >= expiry_alert_time:
                    target_date = today + timedelta(days=expiry_days_before)
                    cursor.execute("""
                        SELECT id, user_id, item_name, expiry_date, is_labeled, mfg_date,
                               purchase_date, created_at, storage_type, image_path, category,
                               quantity
                        FROM pantry_items
                        WHERE user_id = %s
                          AND status = 'active'
                          AND hidden_from_products = 0
                          AND expiry_date = %s
                    """, (user_id, target_date))
                    items = cursor.fetchall()
                    for item in items:
                        cursor.execute("""
                            SELECT id
                            FROM notifications
                            WHERE user_id = %s
                              AND pantry_item_id = %s
                              AND type = 'expiry_before'
                              AND DATE(created_at) = CURDATE()
                        """, (user_id, item["id"]))
                        already_sent = cursor.fetchone()
                        if not already_sent:
                            title = "Expiring Soon"
                            message = f'{item["item_name"]} will expire in {expiry_days_before} day(s).'
                            insert_notification(
                                user_id=user_id,
                                title=title,
                                message=message,
                                notif_type="expiry_before",
                                pantry_item_id=item["id"]
                            )
                # 2. CRITICAL ALERT (EXPIRING TODAY)
                if critical_alert_enabled == 1 and current_time >= critical_alert_time:
                    cursor.execute("""
                        SELECT id, user_id, item_name, expiry_date, is_labeled, mfg_date,
                               purchase_date, created_at, storage_type, image_path, category,
                               quantity
                        FROM pantry_items
                        WHERE user_id = %s
                          AND status = 'active'
                          AND hidden_from_products = 0
                          AND expiry_date = %s
                    """, (user_id, today))
                    items = cursor.fetchall()
                    for item in items:
                        cursor.execute("""
                            SELECT id
                            FROM notifications
                            WHERE user_id = %s
                              AND pantry_item_id = %s
                              AND type = 'critical_expiry'
                              AND DATE(created_at) = CURDATE()
                        """, (user_id, item["id"]))
                        already_sent = cursor.fetchone()
                        if not already_sent:
                            title = "Urgent: Item Expiring Today!"
                            message = f'{item["item_name"]} expires today. Use it immediately!'
                            insert_notification(
                                user_id=user_id,
                                title=title,
                                message=message,
                                notif_type="critical_expiry",
                                pantry_item_id=item["id"]
                            )
                # 3. WEEKLY SUMMARY ALERT
                if (
                    weekly_summary_enabled == 1
                    and WEEKDAY_MAP.get(weekly_summary_day, 6) == current_weekday
                    and current_time >= weekly_summary_time
                ):
                    # Check if already sent BEFORE running heavy queries
                    cursor.execute("""
                        SELECT id
                        FROM notifications
                        WHERE user_id = %s
                          AND type = 'weekly_summary'
                          AND YEARWEEK(created_at, 1) = YEARWEEK(NOW(), 1)
                    """, (user_id,))
                    already_sent = cursor.fetchone()

                    if not already_sent:
                        week_start = today - timedelta(days=7)
                        cursor.execute("""
                            SELECT COUNT(*) AS cnt
                            FROM pantry_items
                            WHERE user_id = %s
                              AND status = 'active'
                              AND hidden_from_products = 0
                        """, (user_id,))
                        active_count = cursor.fetchone()["cnt"]
                        cursor.execute("""
                            SELECT COUNT(*) AS cnt
                            FROM pantry_items
                            WHERE user_id = %s
                              AND status = 'consumed'
                              AND updated_at >= %s
                        """, (user_id, week_start))
                        consumed_count = cursor.fetchone()["cnt"]
                        cursor.execute("""
                            SELECT COUNT(*) AS cnt
                            FROM pantry_items
                            WHERE user_id = %s
                              AND status = 'wasted'
                              AND updated_at >= %s
                        """, (user_id, week_start))
                        wasted_count = cursor.fetchone()["cnt"]
                        cursor.execute("""
                            SELECT COUNT(*) AS cnt
                            FROM pantry_items
                            WHERE user_id = %s
                              AND (
                                    (status = 'active' AND expiry_date < %s)
                                    OR pending_weekly_cleanup = 1
                                  )
                        """, (user_id, today))
                        expired_count = cursor.fetchone()["cnt"]
                        cursor.execute("""
                            SELECT COUNT(*) AS cnt
                            FROM pantry_items
                            WHERE user_id = %s
                              AND status = 'active'
                              AND hidden_from_products = 0
                              AND expiry_date BETWEEN %s AND %s
                        """, (user_id, today, today + timedelta(days=3)))
                        use_soon_count = cursor.fetchone()["cnt"]
                        cursor.execute("""
                            SELECT COUNT(*) AS cnt
                            FROM pantry_items
                            WHERE user_id = %s
                              AND status = 'active'
                              AND hidden_from_products = 0
                              AND expiry_date > %s + INTERVAL 3 DAY
                        """, (user_id, today))
                        fresh_count = cursor.fetchone()["cnt"]

                        title = "Weekly Pantry Summary"
                        message = (
                            f"Used: {consumed_count}, "
                            f"Wasted: {wasted_count}, "
                            f"In Pantry: {active_count}, "
                            f"Use Soon: {use_soon_count}, "
                            f"Expired: {expired_count}, "
                            f"Fresh: {fresh_count}"
                        )
                        insert_notification(
                            user_id=user_id,
                            title=title,
                            message=message,
                            notif_type="weekly_summary"
                        )
                        # Permanently delete items that were hidden only for weekly summary
                        cursor.execute("""
                            SELECT id FROM pantry_items
                            WHERE user_id = %s
                              AND (pending_weekly_cleanup = 1 OR status IN ('consumed', 'wasted'))
                        """, (user_id,))
                        ids_to_del = [r['id'] for r in cursor.fetchall()]
                        if ids_to_del:
                            delete_associated_images(cursor, ids_to_del)
                            format_strings = ','.join(['%s'] * len(ids_to_del))
                            cursor.execute(f"DELETE FROM pantry_items WHERE id IN ({format_strings})", tuple(ids_to_del))
                        conn.commit()
            # Cleanup orphaned items (safety check - 7 days instead of 14 as requested)
                        cursor.execute("""
                            SELECT id FROM pantry_items
                            WHERE status IN ('consumed', 'wasted')
                              AND updated_at <= NOW() - INTERVAL 7 DAY
                        """)
                        ids_to_del = [r['id'] for r in cursor.fetchall()]
                        if ids_to_del:
                            delete_associated_images(cursor, ids_to_del)
                            format_strings = ','.join(['%s'] * len(ids_to_del))
                            cursor.execute(f"DELETE FROM pantry_items WHERE id IN ({format_strings})", tuple(ids_to_del))
                        conn.commit()
    except Exception as e:
        print("❌ Scheduler error:", e)
        conn.rollback()
    finally:
        conn.close()
# ==========================================================
# ✅ OCR HELPERS
# ==========================================================
def preprocess_image_variants_for_ocr(img_array):
    variants = []
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    variants.append(gray)
    denoised = cv2.GaussianBlur(gray, (3, 3), 0)
    variants.append(denoised)
    _, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants.append(thresh1)
    adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 31, 11)
    variants.append(adaptive)
    enlarged = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    variants.append(enlarged)
    return variants
def extract_text_with_best_effort(img_array):
    variants = preprocess_image_variants_for_ocr(img_array)
    best_text = ""
    best_score = -1
    configs = [
        "--oem 3 --psm 6",
        "--oem 3 --psm 11",
        "--oem 3 --psm 4"
    ]
    for variant in variants:
        for cfg in configs:
            try:
                text = pytesseract.image_to_string(variant, config=cfg)
                cleaned = re.sub(r'\s+', ' ', text or '').strip()
                score = len(cleaned)
                if score > best_score:
                    best_score = score
                    best_text = text
            except Exception:
                pass
    return best_text.strip()
def normalize_ocr_text(text):
    text = text or ""
    text = text.replace("\n", " ")
    text = re.sub(r'\s+', ' ', text)
    text = text.replace("O", "0")
    return text.strip()
def extract_product_details(text):
    raw_text = text or ""
    text = normalize_ocr_text(raw_text)
    details = {
        "expiry_date": None,
        "mfg_date": None,
        "lot_number": None
    }
    date_patterns = [
        r'\b\d{2}[/-]\d{2}[/-]\d{2,4}\b',
        r'\b\d{4}[/-]\d{2}[/-]\d{2}\b',
        r'\b\d{2}\s+[A-Za-z]{3,9}\s+\d{2,4}\b',
        r'\b[A-Za-z]{3,9}\s+\d{2},?\s+\d{2,4}\b'
    ]
    all_dates = []
    for pattern in date_patterns:
        all_dates.extend(re.findall(pattern, text, flags=re.IGNORECASE))
    def search_labeled_date(label_patterns):
        for label in label_patterns:
            m = re.search(label, text, flags=re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return None
    expiry_text = search_labeled_date([
        r'(?:EXP|EXPIRY|EXPIRES|BEST\s*BEFORE|USE\s*BY|EXP\s*DATE|E\.|EXP\.?)\s*[:\-]?\s*([A-Za-z0-9/\- ,.]+?)(?:LOT|MFG|PKD|BATCH|$)',
    ])
    mfg_text = search_labeled_date([
        r'(?:MFG|MFD|MANUFACTURED|PKD|PACKED\s*ON|MFG\s*DATE|M\.|MFD\.?)\s*[:\-]?\s*([A-Za-z0-9/\- ,.]+?)(?:EXP|LOT|BATCH|$)',
    ])
    if not expiry_text and all_dates:
        expiry_text = all_dates[-1]
    if not mfg_text and len(all_dates) > 1:
        # If we have multiple dates, first one is likely MFG, last is EXP
        mfg_text = all_dates[0]
    lot_match = re.search(r'(?:LOT|BATCH|LOT\s*NO|LOT#|L\.NO|B\.NO|BN|B\.N|BATCH\s*NO|LOT\s*NUMBER|B\.#|BATCH#)\s*[:#\-]?\s*([A-Z0-9\-_/]+)', text, re.IGNORECASE)
    if lot_match:
        details["lot_number"] = lot_match.group(1).strip().rstrip('.,-')
    # Clean extracted date strings from common punctuation artifacts
    details["expiry_date"] = expiry_text.strip().rstrip('.,-') if expiry_text else None
    details["mfg_date"] = mfg_text.strip().rstrip('.,-') if mfg_text else None
    return details
# ==========================================================
# ✅ REGISTER
# ==========================================================
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")
    confirm_password = data.get("confirm_password")
    if not full_name or not email or not password or not confirm_password:
        return jsonify({"status": "error", "message": "All fields are required"}), 400
    if not re.match(r"^[A-Za-z\s]+$", full_name):
        return jsonify({"status": "error", "message": "Full name must contain only letters and spaces"}), 400
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_pattern, email):
        return jsonify({"status": "error", "message": "Invalid email format"}), 400
    missing_requirements = validate_password(password)
    if missing_requirements:
        return jsonify({"status": "error", "message": f"Password must contain: {', '.join(missing_requirements)}"}), 400
    if password != confirm_password:
        return jsonify({"status": "error", "message": "Passwords do not match"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM register WHERE email=%s", (email,))
            existing_user = cursor.fetchone()
            if existing_user:
                return jsonify({"status": "error", "message": "Mail already registered"}), 409
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO register (full_name, email, password) VALUES (%s, %s, %s)",
                (full_name, email, hashed_password)
            )
            conn.commit()
        return jsonify({"status": "success", "message": "User registered successfully"}), 201
    finally:
        conn.close()
# ==========================================================
# ✅ LOGIN
# ==========================================================
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password are required"}), 400
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_pattern, email):
        return jsonify({"status": "error", "message": "Invalid email format"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM register WHERE email=%s", (email,))
            user = cursor.fetchone()
            if not user:
                return jsonify({"status": "error", "message": "Email is not registered. Please create an account."}), 404
            if not check_password_hash(user["password"], password):
                return jsonify({"status": "error", "message": "Incorrect password. Please try again."}), 401
            return jsonify({
                "status": "success",
                "message": "Login successful",
                "user": {
                    "id": user["id"],
                    "full_name": user["full_name"],
                    "email": user["email"]
                }
            }), 200
    finally:
        conn.close()
# ==========================================================
# ✅ PASSWORD RESET ROUTES
# ==========================================================
@app.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    if not email:
        return jsonify({"status": "error", "message": "Email is required"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM register WHERE email=%s", (email,))
            user = cursor.fetchone()
            if not user:
                return jsonify({"status": "error", "message": "Email not registered"}), 404
            otp = str(random.randint(1000, 9999))
            cursor.execute(
                "UPDATE register SET otp=%s, otp_expiry=DATE_ADD(NOW(), INTERVAL 2 MINUTE) WHERE id=%s",
                (otp, user["id"])
            )
            conn.commit()
        try:
            import smtplib
            from email.message import EmailMessage
            msg = EmailMessage()
            msg.set_content(f"Your Reset Password OTP is: {otp}. It is valid for 2 minutes.")
            msg['Subject'] = "Password Reset OTP"
            msg['From'] = "savorshelf1.0@gmail.com"
            msg['To'] = email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login("savorshelf1.0@gmail.com", "eoekijzviyyhbgsy")
            server.send_message(msg)
            server.quit()
            # OTP print removed for security
            print(f"DEBUG: Email sent successfully to {email}")
        except Exception as e:
            print("Mail Error:", e)
            return jsonify({"status": "error", "message": f"Failed to send OTP: {str(e)}"}), 500
        return jsonify({"status": "success", "message": "OTP sent to registered email"}), 200
    finally:
        conn.close()
@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    otp = (data.get("otp") or "").strip()
    if not email:
        return jsonify({"status": "error", "message": "Email required"}), 400
    if not otp:
        return jsonify({"status": "error", "message": "OTP required"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT otp, (otp_expiry > NOW()) as is_valid FROM register WHERE email=%s", (email,))
            user = cursor.fetchone()
            if not user:
                return jsonify({"status": "error", "message": "User not found"}), 404
            db_otp = str(user.get("otp") or "").strip()
            if db_otp != otp:
                return jsonify({"status": "error", "message": "Invalid OTP"}), 400
            if not user.get("is_valid"):
                return jsonify({"status": "error", "message": "OTP expired"}), 400
        return jsonify({"status": "success", "message": "OTP verified. Ready to reset password."}), 200
    finally:
        conn.close()
@app.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")
    if not email or not new_password or not confirm_password:
        return jsonify({"status": "error", "message": "All fields are required"}), 400
    if new_password != confirm_password:
        return jsonify({"status": "error", "message": "Passwords do not match"}), 400
    missing_requirements = validate_password(new_password)
    if missing_requirements:
        return jsonify({"status": "error", "message": f"Password must contain: {', '.join(missing_requirements)}"}), 400
    hashed_password = generate_password_hash(new_password)
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE register SET password=%s, otp=NULL, otp_expiry=NULL WHERE email=%s",
                (hashed_password, email)
            )
            conn.commit()
        return jsonify({"status": "success", "message": "Password reset successfully"}), 200
    finally:
        conn.close()
# ==========================================================
# ✅ UNLABELED PRODUCT ADD (Frontend-Aligned)
# ==========================================================
@app.route("/add-unlabeled-product", methods=["POST"])
def add_unlabeled_product():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    category = (data.get("category") or "").strip()
    selected_item_name = (data.get("item_name") or "").strip()
    custom_name = (data.get("custom_name") or "").strip()
    purchase_date_str = (data.get("purchase_date") or "").strip()
    quantity = (data.get("quantity") or "").strip()
    storage_type = STORAGE_NORMALIZATION.get((data.get("storage_type") or "").strip(), (data.get("storage_type") or "").strip())
    if not user_id:
        return jsonify({"status": "error", "message": "User ID is required"}), 400
    if not category:
        return jsonify({"status": "error", "message": "Category is required"}), 400
    if category not in VALID_UNLABELED_CATEGORIES:
        return jsonify({"status": "error", "message": "Invalid category selected"}), 400
    if not selected_item_name and not custom_name:
        return jsonify({"status": "error", "message": "Please select a product or enter a custom name"}), 400
    if not purchase_date_str:
        return jsonify({"status": "error", "message": "Purchase date is required"}), 400
    if not storage_type or storage_type not in ["Fridge", "Freezer", "Room Temperature"]:
        return jsonify({"status": "error", "message": "Invalid storage type"}), 400
    purchase_date = parse_frontend_date(purchase_date_str)
    if not purchase_date:
        return jsonify({"status": "error", "message": "Invalid purchase date format. Use dd/MM/yyyy"}), 400
    if purchase_date > date.today():
        return jsonify({"status": "error", "message": "Purchase date cannot be in the future"}), 400
    final_item_name = custom_name if custom_name else selected_item_name
    lookup_name = selected_item_name if selected_item_name else final_item_name
    shelf_life_days = get_shelf_life_from_db(lookup_name, storage_type)
    expiry_date = purchase_date + timedelta(days=shelf_life_days)
    image_url = resolve_static_image(category, lookup_name)
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM register WHERE id=%s", (user_id,))
            if not cursor.fetchone():
                return jsonify({"status": "error", "message": "User not found"}), 404
            cursor.execute("""
                INSERT INTO pantry_items
                (user_id, item_name, category, storage_type, purchase_date, expiry_date, created_at,
                 image_path, lot_number, is_labeled, status, quantity, hidden_from_products,
                 pending_weekly_cleanup, expired_hidden_at, deleted_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s, 0, 0, NULL, NULL)
            """, (
                user_id, final_item_name, category, storage_type, purchase_date, expiry_date,
                image_url, None, 0, "active", quantity if quantity else None
            ))
            conn.commit()
            inserted_id = cursor.lastrowid
        return jsonify({
            "status": "success",
            "message": "Unlabeled product added successfully",
            "item_id": inserted_id,
            "item_name": final_item_name,
            "category": category,
            "purchase_date": purchase_date.strftime("%Y-%m-%d"),
            "expiry": expiry_date.strftime("%Y-%m-%d"),
            "quantity": quantity,
            "storage_type": storage_type,
            "image_url": image_url,
            "estimated_shelf_life_days": shelf_life_days
        }), 201
    except Exception as e:
        print(f"❌ Add Unlabeled Product Error: {e}")
        conn.rollback()
        return jsonify({"status": "error", "message": f"Failed to add unlabeled product: {e}"}), 500
    finally:
        conn.close()
# ==========================================================
# ✅ SCAN PRODUCT INFO API
# ==========================================================
@app.route("/scan-product-info", methods=["POST"])
def scan_product_info():
    if "image" not in request.files:
        return jsonify({"status": "error", "message": "No image file provided"}), 400
    file = request.files["image"]
    try:
        img = Image.open(file.stream).convert("RGB")
        img_array = np.array(img)
        text = extract_text_with_best_effort(img_array)
        extracted_data = extract_product_details(text)
        return jsonify({
            "status": "success",
            "detected_text": text,
            "extracted_data": extracted_data
        }), 200
    except Exception as e:
        print(f"❌ Scan Product Info Error: {e}")
        return jsonify({"status": "error", "message": "Failed to scan product info"}), 500
# ==========================================================
# ✅ LABELED PRODUCT ADD (OCR + FILE UPLOAD)
# ==========================================================
@app.route("/add-labeled-product", methods=["POST"])
def add_labeled_product():
    if "front_image" not in request.files:
        return jsonify({"status": "error", "message": "Front image is required"}), 400
    if "expiry_image" not in request.files:
        return jsonify({"status": "error", "message": "Expiry image is required"}), 400
    front_file = request.files["front_image"]
    expiry_file = request.files["expiry_image"]
    user_id = request.form.get("user_id")
    item_name = (request.form.get("item_name") or "").strip()
    category = (request.form.get("category") or "").strip()
    storage_type = STORAGE_NORMALIZATION.get((request.form.get("storage_type") or "").strip(), (request.form.get("storage_type") or "").strip())
    if not user_id:
        return jsonify({"status": "error", "message": "User ID is required"}), 400
    if not item_name:
        return jsonify({"status": "error", "message": "Item name is required"}), 400
    if storage_type not in ["Fridge", "Freezer", "Room Temperature"]:
        return jsonify({"status": "error", "message": "Storage type is required"}), 400
    # User check removed here, will be checked during insertion in the next DB block
    try:
        timestamp = int(datetime.now().timestamp())
        front_temp_path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(front_file.filename))
        front_file.save(front_temp_path)
        front_jpg_path = ensure_jpg(front_temp_path)
        front_filename = f"user_{user_id}_{timestamp}_front.jpg"
        front_final_path = os.path.join(app.config["UPLOAD_FOLDER"], front_filename)
        os.rename(front_jpg_path, front_final_path)
        expiry_temp_path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(expiry_file.filename))
        expiry_file.save(expiry_temp_path)
        expiry_jpg_path = ensure_jpg(expiry_temp_path)
        expiry_filename = f"user_{user_id}_{timestamp}_expiry.jpg"
        expiry_final_path = os.path.join(app.config["UPLOAD_FOLDER"], expiry_filename)
        os.rename(expiry_jpg_path, expiry_final_path)
        front_image_url = f"/uploads/products/{front_filename}"
        expiry_image_url = f"/uploads/products/{expiry_filename}"
        img = Image.open(expiry_final_path).convert("RGB")
        ocr_text = extract_text_with_best_effort(np.array(img))
        ocr_details = extract_product_details(ocr_text)
        # User-entered data always overrides OCR
        confirmed_expiry = (request.form.get("expiry_date") or "").strip()
        confirmed_mfg = (request.form.get("mfg_date") or "").strip()
        confirmed_lot = (request.form.get("lot_number") or "").strip()
        final_expiry = parse_to_sql_date(confirmed_expiry) or parse_to_sql_date(ocr_details.get("expiry_date"))
        final_mfg = parse_to_sql_date(confirmed_mfg) or parse_to_sql_date(ocr_details.get("mfg_date"))
        final_lot = confirmed_lot if confirmed_lot else ocr_details.get("lot_number")
        if not final_expiry:
            return jsonify({"status": "error", "message": "Expiry date is required. Please check the scan or enter manually."}), 400
        if not final_mfg:
            return jsonify({"status": "error", "message": "Manufacture date is required. Please check the scan or enter manually."}), 400
        if final_mfg > date.today():
            return jsonify({"status": "error", "message": "Manufacture date cannot be in the future"}), 400
        if final_mfg and final_expiry and final_mfg > final_expiry:
            return jsonify({"status": "error", "message": "Manufacture date cannot be after expiry date"}), 400
        quantity = (request.form.get("quantity") or "").strip()
        conn = get_db_connection()
        if not conn:
            return jsonify({"status": "error", "message": "DB connection failed"}), 500
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO pantry_items
                    (user_id, item_name, category, storage_type, mfg_date, expiry_date, created_at,
                     image_path, lot_number, is_labeled, status, quantity, hidden_from_products,
                     pending_weekly_cleanup, expired_hidden_at, deleted_at)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s, 0, 0, NULL, NULL)
                """, (
                    user_id, item_name, category if category else None, storage_type,
                    final_mfg, final_expiry, front_image_url, final_lot, 1, "active", quantity if quantity else None
                ))
                conn.commit()
                inserted_id = cursor.lastrowid
            return jsonify({
                "status": "success",
                "message": "Labeled product added successfully",
                "item_id": inserted_id,
                "item_name": item_name,
                "image_url": front_image_url,
                "expiry_image_url": expiry_image_url,
                "saved_expiry": str(final_expiry),
                "saved_mfg_date": str(final_mfg) if final_mfg else None,
                "saved_lot_number": final_lot,
                "ocr_text": ocr_text,
                "extracted": ocr_details,
                "final_source": {
                    "expiry_date": "manual" if parse_to_sql_date(confirmed_expiry) else "ocr",
                    "mfg_date": "manual" if parse_to_sql_date(confirmed_mfg) else ("ocr" if final_mfg else "none"),
                    "lot_number": "manual" if confirmed_lot else ("ocr" if final_lot else "none")
                }
            }), 201
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    except Exception as e:
        print(f"❌ Add Labeled Product Error: {e}")
        return jsonify({"status": "error", "message": f"Failed to add labeled product: {e}"}), 500
# ==========================================================
# ✅ STATIC / UPLOAD SERVING
# ==========================================================
@app.route("/static/<category>/<filename>")
def serve_item_image(category, filename):
    directory = os.path.join("static", category)
    return send_from_directory(directory, filename)
@app.route("/uploads/products/<filename>")
def serve_uploaded_product_image(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
# ==========================================================
# ✅ DASHBOARD & REPORT LOGIC
# ==========================================================
@app.route("/get-dashboard", methods=["GET"])
def get_dashboard():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "User ID required"}), 400
    # hide_or_delete_expired_items() removed - handled by background task
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, user_id, item_name, category, expiry_date, image_path, created_at,
                       is_labeled, mfg_date, purchase_date, storage_type, quantity, hidden_from_products
                FROM pantry_items
                WHERE user_id=%s AND status='active' AND hidden_from_products=0
                ORDER BY expiry_date ASC, created_at DESC
            """, (user_id,))
            items = cursor.fetchall()
        fresh_count = 0
        use_soon_count = 0
        expired_count = 0
        recent_items = []
        freshness_cards = []
        for item in items:
            card = build_item_card_payload(item, host_url=request.host_url)
            freshness_cards.append(card)
            if card["freshnessLabel"] == "Expired":
                expired_count += 1
            elif card["freshnessLabel"] in ["Use Soon", "Moderate"]:
                use_soon_count += 1
            else:
                fresh_count += 1
        # recent items should match the order in the products page (expiring soonest)
        for item in items[:4]:
            payload = build_item_card_payload(item, host_url=request.host_url)
            payload["addedTime"] = f"Added {(date.today() - item['created_at'].date()).days} day(s) ago"
            # Map statusLabel and statusValue for the Frontend DashboardRecentItem model
            f_data = calculate_freshness(item)
            days = f_data.get("days_remaining", 0)
            if days < 0:
                payload["statusLabel"] = "EXPIRED"
                payload["statusValue"] = f"{abs(days)} DAYS AGO"
            elif days == 0:
                payload["statusLabel"] = "EXPIRES"
                payload["statusValue"] = "TODAY"
            else:
                payload["statusLabel"] = "EXPIRES IN"
                payload["statusValue"] = f"{days} DAYS"
            recent_items.append(payload)
        tips = [
            "Store potatoes in a cool, dark place away from onions.",
            "Keep milk in the main part of the fridge, not the door.",
            "Wrap leafy greens in paper towels to absorb excess moisture.",
            "Store herbs upright in water like flowers to keep them fresh longer.",
            "Keep bananas away from other fruits to prevent over-ripening.",
            "Wrap celery tightly in aluminum foil to keep it crisp for weeks.",
            "Store mushrooms in a paper bag instead of plastic to prevent sliminess.",
            "Keep tomatoes on the counter at room temperature to preserve flavor.",
            "Store asparagus upright in a jar with an inch of water in the fridge.",
            "Wash berries in a vinegar-water solution to kill mold spores before storing.",
            "Store cucumbers on the counter to avoid 'chill injury' from the fridge.",
            "Keep onions in a well-ventilated area, away from potatoes and light.",
            "Store flour and nuts in the freezer to prevent natural oils from going rancid.",
            "Keep eggs in their original carton on a middle shelf for temperature stability.",
            "Store bread in a cool, dry bread box rather than the refrigerator.",
            "Wrap hard cheeses in parchment or wax paper to allow them to breathe.",
            "Keep citrus fruits in a mesh bag to ensure proper air circulation.",
            "Store honey in a sealed glass jar in a dark pantry; it never expires.",
            "Freeze ginger root to make it last longer and easier to grate.",
            "Store avocados on the counter until ripe, then move to the fridge.",
            "Keep coffee beans in an airtight, opaque container in a cool cupboard.",
            "Store open bags of chips or crackers in airtight clips or jars.",
            "Keep garlic in a cool, dry place with plenty of airflow.",
            "Store olive oil in a dark glass bottle away from the heat of the stove.",
            "Place a bay leaf in flour or rice containers to keep pests away.",
            "Store apples in the refrigerator crisper drawer to keep them crunchy.",
            "Keep scallions in a glass of water on the windowsill to keep them growing.",
            "Store maple syrup in the refrigerator after opening to prevent mold."
        ]
        return jsonify({
            "status": "success",
            "summary": {
                "fresh": fresh_count,
                "use_soon": use_soon_count,
                "expired": expired_count
            },
            "daily_tip": random.choice(tips),
            "freshness_cards": freshness_cards,
            "recent_items": recent_items
        }), 200
    except Exception as e:
        print(f"❌ Dashboard Error: {e}")
        return jsonify({"status": "error", "message": "Could not load dashboard"}), 500
    finally:
        conn.close()
# ==========================================================
# ✅ PRODUCT APIs (LIST, LABELED, UNLABELED)
# ==========================================================
@app.route("/get-pantry-items", methods=["GET"])
def get_pantry_items():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "User ID required"}), 400
    # hide_or_delete_expired_items() removed - handled by background task
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, user_id, item_name, category, expiry_date, image_path, is_labeled,
                       storage_type, mfg_date, purchase_date, created_at, quantity
                FROM pantry_items
                WHERE user_id=%s AND status='active' AND hidden_from_products=0
                ORDER BY expiry_date ASC, created_at DESC
            """, (user_id,))
            rows = cursor.fetchall()
        items = [build_item_card_payload(row, host_url=request.host_url) for row in rows]
        return jsonify({"status": "success", "items": items}), 200
    finally:
        conn.close()
# ==========================================================
# ✅ GET SINGLE PRODUCT DETAILS API
# ==========================================================
@app.route("/get-product-details", methods=["GET"])
def get_product_details():
    product_id = request.args.get("id")
    # hide_or_delete_expired_items() removed - handled by background task
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM pantry_items WHERE id=%s", (product_id,))
            p = cursor.fetchone()
            if not p:
                return jsonify({"status": "error", "message": "Item not found"}), 404
            f = calculate_freshness(p)
            start = f["start_date"]
            return jsonify({
                "status": "success",
                "data": {
                    "item_name": p["item_name"],
                    "image_path": fix_url(p.get("image_path"), host=request.host_url),
                    "category": p.get("category"),
                    "storage_location": p.get("storage_type"),
                    "primary_date_label": "Manufacture Date" if p.get("is_labeled") else "Purchase Date",
                    "primary_date_value": start.strftime("%d %b %Y") if start else None,
                    "expiry_label": "Detected Expiry" if p.get("is_labeled") else "Expected Expiry",
                    "expiry_value": p["expiry_date"].strftime("%d %b %Y") if p.get("expiry_date") else None,
                    "freshness_progress": int(f["progress"]),
                    "days_remaining": f["days_remaining"],
                    "freshness_label": f["freshness_label"],
                    "detail_value": f["detail_value"],
                    "lot_number": p.get("lot_number"),
                    "quantity": p.get("quantity")
                }
            }), 200
    finally:
        conn.close()
# ==========================================================
# ✅ FRESHNESS REPORT API (Aggregated Data & Counts)
# ==========================================================
@app.route("/get-freshness-report", methods=["GET"])
def get_freshness_report():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "User ID required"}), 400
    # hide_or_delete_expired_items() removed - handled by background task
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, user_id, item_name, image_path, expiry_date, mfg_date, purchase_date,
                       storage_type, is_labeled, created_at, quantity, category
                FROM pantry_items
                WHERE user_id=%s AND status='active' AND hidden_from_products=0
                ORDER BY expiry_date ASC, created_at DESC
            """, (user_id,))
            items = cursor.fetchall()
        fresh_count = 0
        use_soon_count = 0
        expired_count = 0
        report_items = []
        for item in items:
            payload = build_item_card_payload(item, host_url=request.host_url)
            report_items.append(payload)
            if payload["freshnessLabel"] == "Expired":
                expired_count += 1
            elif payload["freshnessLabel"] in ["Use Soon", "Moderate"]:
                use_soon_count += 1
            else:
                fresh_count += 1
        # Calculate Weekly Stats (Last 7 Days) for the Waste Impact Banner
        with conn.cursor() as cursor:
            week_ago = date.today() - timedelta(days=7)
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN status='consumed' THEN 1 END) as consumed,
                    COUNT(CASE WHEN status='wasted' THEN 1 END) as wasted
                FROM pantry_items
                WHERE user_id=%s AND updated_at >= %s
            """, (user_id, week_ago))
            stats = cursor.fetchone()
            weekly_consumed = stats["consumed"] if stats else 0
            weekly_wasted = stats["wasted"] if stats else 0
            # Find Most Wasted Item Name for personalized tip
            cursor.execute("""
                SELECT item_name, COUNT(*) as cnt
                FROM pantry_items
                WHERE user_id=%s AND status='wasted' AND updated_at >= %s
                GROUP BY item_name
                ORDER BY cnt DESC LIMIT 1
            """, (user_id, week_ago))
            most_wasted_row = cursor.fetchone()
            most_wasted_item = most_wasted_row["item_name"] if most_wasted_row else None
        return jsonify({
            "status": "success",
            "summary": {
                "fresh": fresh_count,
                "use_soon": use_soon_count,
                "expired": expired_count,
                "weekly_consumed": weekly_consumed,
                "weekly_wasted": weekly_wasted,
                "most_wasted_item": most_wasted_item
            },
            "items": report_items
        }), 200
    except Exception as e:
        print(f"❌ Report Error: {e}")
        return jsonify({"status": "error", "message": "Could not generate report"}), 500
    finally:
        conn.close()
# ==========================================================
# ✅ STATUS / DELETE ROUTES
# ==========================================================
@app.route("/update-item-status", methods=["POST"])
def update_item_status():
    data = request.get_json(silent=True) or {}
    item_id = data.get("item_id")
    new_status = data.get("status")
    if not item_id:
        return jsonify({"status": "error", "message": "Item ID is required"}), 400
    if new_status not in ["consumed", "wasted", "active"]:
        return jsonify({"status": "error", "message": "Invalid status"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM pantry_items WHERE id=%s", (item_id,))
            if not cursor.fetchone():
                return jsonify({"status": "error", "message": "Item not found"}), 404
            cursor.execute("""
                UPDATE pantry_items
                SET status=%s,
                    updated_at=NOW(),
                    hidden_from_products=CASE WHEN %s='active' THEN 0 ELSE 1 END,
                    pending_weekly_cleanup=CASE WHEN %s='active' THEN 0 ELSE 1 END,
                    expired_hidden_at=CASE WHEN %s='active' THEN NULL ELSE COALESCE(expired_hidden_at, NOW()) END
                WHERE id=%s
            """, (new_status, new_status, new_status, new_status, item_id))
            conn.commit()
        return jsonify({"status": "success", "message": f"Item marked as {new_status}"}), 200
    finally:
        conn.close()
@app.route("/delete-product", methods=["POST"])
def delete_product():
    data = request.get_json(silent=True) or {}
    item_id = data.get("id")
    if not item_id:
        return jsonify({"status": "error", "message": "Item ID is required"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM pantry_items WHERE id=%s", (item_id,))
            if not cursor.fetchone():
                return jsonify({"status": "error", "message": "Item not found"}), 404
            cursor.execute("""
                UPDATE pantry_items 
                SET status='consumed', 
                    updated_at=NOW(), 
                    hidden_from_products=1,
                    pending_weekly_cleanup=1
                WHERE id=%s
            """, (item_id,))
            conn.commit()
        return jsonify({"status": "success", "message": "Product marked as consumed", "consumed_id": item_id}), 200
    except Exception as e:
        print(f"❌ Delete Product Error: {e}")
        conn.rollback()
        return jsonify({"status": "error", "message": "Internal server error"}), 500
    finally:
        conn.close()
# ==========================================================
# ✅ PROFILE ROUTES
# ==========================================================
@app.route("/update-profile", methods=["PUT"])
def update_profile():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    new_name = data.get("full_name")
    if not user_id:
        return jsonify({"status": "error", "message": "User ID is required"}), 400
    if not new_name or not re.match(r"^[A-Za-z\s]+$", new_name):
        return jsonify({"status": "error", "message": "Invalid name. Use letters and spaces only."}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM register WHERE id=%s", (user_id,))
            if not cursor.fetchone():
                return jsonify({"status": "error", "message": "User not found"}), 404
            cursor.execute("UPDATE register SET full_name=%s WHERE id=%s", (new_name, user_id))
            conn.commit()
        return jsonify({
            "status": "success",
            "message": "Profile updated successfully",
            "new_name": new_name
        }), 200
    except Exception as e:
        print(f"❌ Update Error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500
    finally:
        conn.close()
@app.route("/change-password", methods=["POST"])
def change_password():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    current_password = data.get("current_password")
    new_password = data.get("new_password")
    confirm_new_password = data.get("confirm_new_password")
    if not all([user_id, current_password, new_password, confirm_new_password]):
        return jsonify({"status": "error", "message": "All fields are required"}), 400
    if new_password != confirm_new_password:
        return jsonify({"status": "error", "message": "New passwords do not match"}), 400
    missing_reqs = validate_password(new_password)
    if len(new_password) < 6:
        missing_reqs.append("at least 8 characters")
    if missing_reqs:
        return jsonify({
            "status": "error",
            "message": f"New password fails requirements: {', '.join(set(missing_reqs))}"
        }), 400
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT password FROM register WHERE id=%s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({"status": "error", "message": "User not found"}), 404
            if not check_password_hash(user["password"], current_password):
                return jsonify({"status": "error", "message": "Current password is incorrect"}), 401
            new_hashed_password = generate_password_hash(new_password)
            cursor.execute("UPDATE register SET password=%s WHERE id=%s", (new_hashed_password, user_id))
            conn.commit()
        return jsonify({"status": "success", "message": "Password updated successfully"}), 200
    except Exception as e:
        print(f"❌ Password Update Error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500
    finally:
        conn.close()
@app.route("/delete-account", methods=["POST"])
def delete_account():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "User ID is required"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM register WHERE id=%s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({"status": "error", "message": "User not found"}), 404
            cursor.execute("DELETE FROM notifications WHERE user_id=%s", (user_id,))
            cursor.execute("DELETE FROM user_alert_settings WHERE user_id=%s", (user_id,))
            # Delete images before deleting pantry_items
            cursor.execute("SELECT id FROM pantry_items WHERE user_id=%s", (user_id,))
            ids_to_del = [r['id'] for r in cursor.fetchall()]
            if ids_to_del:
                delete_associated_images(cursor, ids_to_del)
                format_strings = ','.join(['%s'] * len(ids_to_del))
                cursor.execute(f"DELETE FROM pantry_items WHERE id IN ({format_strings})", tuple(ids_to_del))
            cursor.execute("DELETE FROM register WHERE id=%s", (user_id,))
            conn.commit()
        return jsonify({
            "status": "success",
            "message": "Account deleted successfully"
        }), 200
    except Exception as e:
        print(f"❌ Delete Account Error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500
    finally:
        conn.close()
# ==========================================================
# ✅ ALERT SETTINGS / NOTIFICATIONS
# ==========================================================
@app.route("/save-alert-settings", methods=["POST"])
def save_alert_settings():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "User ID is required"}), 400
    expiry_days_before = _to_int(data.get("expiry_days_before"), 3) or 3
    expiry_alert_time = parse_time_12h(data.get("expiry_alert_time"), "9:00 AM")
    is_enabled = 1 if data.get("is_enabled", True) else 0
    weekly_summary_enabled = 1 if data.get("weekly_summary_enabled", True) else 0
    weekly_summary_day = data.get("weekly_summary_day", "Sunday")
    weekly_summary_time = parse_time_12h(data.get("weekly_summary_time"), "9:00 AM")
    critical_alert_enabled = 1 if data.get("critical_alert_enabled", True) else 0
    critical_alert_time = parse_time_12h(data.get("critical_alert_time"), "9:00 AM")
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO user_alert_settings
                (user_id, is_enabled, expiry_days_before, expiry_alert_time,
                 weekly_summary_enabled, weekly_summary_day, weekly_summary_time,
                 critical_alert_enabled, critical_alert_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    is_enabled=VALUES(is_enabled),
                    expiry_days_before=VALUES(expiry_days_before),
                    expiry_alert_time=VALUES(expiry_alert_time),
                    weekly_summary_enabled=VALUES(weekly_summary_enabled),
                    weekly_summary_day=VALUES(weekly_summary_day),
                    weekly_summary_time=VALUES(weekly_summary_time),
                    critical_alert_enabled=VALUES(critical_alert_enabled),
                    critical_alert_time=VALUES(critical_alert_time)
            """, (
                user_id, is_enabled, expiry_days_before, expiry_alert_time,
                weekly_summary_enabled, weekly_summary_day, weekly_summary_time,
                critical_alert_enabled, critical_alert_time
            ))
            conn.commit()
        return jsonify({"status": "success", "message": "Alert settings saved"}), 200
    except Exception as e:
        print(f"❌ Save Alert Settings Error: {e}")
        conn.rollback()
        return jsonify({"status": "error", "message": f"Server Error: {str(e)}"}), 500
    finally:
        conn.close()
@app.route("/get-alert-settings", methods=["GET"])
def get_alert_settings():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "User ID is required"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM user_alert_settings WHERE user_id=%s", (user_id,))
            row = cursor.fetchone()
        if not row:
            return jsonify({
                "status": "success",
                "settings": {
                    "is_enabled": True,
                    "expiry_days_before": 3,
                    "expiry_alert_time": "9:00 AM",
                    "weekly_summary_enabled": True,
                    "weekly_summary_day": "Sunday",
                    "weekly_summary_time": "9:00 AM",
                    "critical_alert_enabled": True,
                    "critical_alert_time": "9:00 AM"
                }
            }), 200
        row["is_enabled"] = bool(row.get("is_enabled", 1))
        row["weekly_summary_enabled"] = bool(row.get("weekly_summary_enabled", 1))
        row["critical_alert_enabled"] = bool(row.get("critical_alert_enabled", 1))
        row["expiry_alert_time"] = format_time_24_to_12(row["expiry_alert_time"])
        row["weekly_summary_time"] = format_time_24_to_12(row["weekly_summary_time"])
        row["critical_alert_time"] = format_time_24_to_12(row["critical_alert_time"])
        return jsonify({"status": "success", "settings": row}), 200
    finally:
        conn.close()
@app.route("/get-notifications", methods=["GET"])
def get_notifications():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "User ID is required"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, pantry_item_id, title, message, type, is_unread, created_at
                FROM notifications
                WHERE user_id=%s
                ORDER BY id DESC
            """, (user_id,))
            rows = cursor.fetchall()
        for row in rows:
            row["is_unread"] = bool(row["is_unread"])
        return jsonify({"status": "success", "notifications": rows}), 200
    finally:
        conn.close()
@app.route("/mark-all-notifications-read", methods=["POST"])
def mark_all_notifications_read():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "user_id is required"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE notifications SET is_unread=0 WHERE user_id=%s", (user_id,))
            conn.commit()
        return jsonify({"status": "success", "message": "All notifications marked as read"}), 200
    finally:
        conn.close()
@app.route("/delete-all-notifications", methods=["POST"])
def delete_all_notifications():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "user_id is required"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM notifications WHERE user_id=%s", (user_id,))
            conn.commit()
        return jsonify({"status": "success", "message": "All notifications deleted"}), 200
    finally:
        conn.close()
@app.route("/mark-notification-read", methods=["POST"])
def mark_notification_read():
    data = request.get_json(silent=True) or {}
    notification_id = data.get("notification_id")
    if not notification_id:
        return jsonify({"status": "error", "message": "notification_id is required"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE notifications SET is_unread=0 WHERE id=%s", (notification_id,))
            conn.commit()
        return jsonify({"status": "success", "message": "Notification marked as read"}), 200
    finally:
        conn.close()
@app.route("/delete-notification/<int:notification_id>", methods=["DELETE"])
def delete_notification(notification_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "DB connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM notifications WHERE id=%s", (notification_id,))
            conn.commit()
        return jsonify({"status": "success", "message": "Notification deleted"}), 200
    finally:
        conn.close()
# ==========================================================
# ✅ MANUAL SCHEDULER TRIGGER
# ==========================================================
@app.route("/trigger-scheduler", methods=["GET"])
def trigger_scheduler():
    hide_or_delete_expired_items()
    process_notifications()
    return jsonify({"status": "success", "message": "Scheduler triggered"}), 200
# ==========================================================
# ✅ SCHEDULER
# ==========================================================
scheduler = BackgroundScheduler()
scheduler.add_job(hide_or_delete_expired_items, 'interval', minutes=30)
scheduler.add_job(process_notifications, 'interval', minutes=30)
scheduler.start()
# ==========================================================
# Run Server
# ==========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 5000, debug = True)
    