import os
from datetime import datetime

from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # Basic config
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    db_host = os.getenv("DB_HOST", "db")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "taskdb")
    db_user = os.getenv("DB_USER", "taskuser")
    db_password = os.getenv("DB_PASSWORD", "taskpass")

    # mysql+pymysql://user:pass@host:port/dbname
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    class Task(db.Model):
        __tablename__ = "tasks"
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(200), nullable=False)
        description = db.Column(db.Text, nullable=True)
        status = db.Column(db.String(20), nullable=False, default="PENDING")
        created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

        def to_dict(self):
            return {
                "id": self.id,
                "title": self.title,
                "description": self.description,
                "status": self.status,
                "created_at": self.created_at.isoformat() + "Z",
            }

    def init_db():
        # create tables if they don't exist
        db.create_all()

    @app.get("/health")
    def health():
        # Checks app and DB connectivity
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return jsonify({"status": "ok", "db": "ok"}), 200
        except Exception as e:
            return jsonify({"status": "degraded", "db": "error", "detail": str(e)}), 500

    @app.get("/tasks")
    def list_tasks():
        tasks = Task.query.order_by(Task.id.desc()).all()
        return jsonify([t.to_dict() for t in tasks]), 200

    @app.post("/tasks")
    def create_task():
        data = request.get_json(silent=True) or {}
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify({"error": "title is required"}), 400

        task = Task(
            title=title,
            description=(data.get("description") or "").strip() or None,
            status=(data.get("status") or "PENDING").strip().upper(),
        )
        if task.status not in {"PENDING", "IN_PROGRESS", "DONE"}:
            return jsonify({"error": "status must be PENDING, IN_PROGRESS, or DONE"}), 400

        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201

    @app.get("/tasks/<int:task_id>")
    def get_task(task_id: int):
        task = Task.query.get_or_404(task_id)
        return jsonify(task.to_dict()), 200

    @app.put("/tasks/<int:task_id>")
    def update_task(task_id: int):
        task = Task.query.get_or_404(task_id)
        data = request.get_json(silent=True) or {}

        if "title" in data:
            new_title = (data.get("title") or "").strip()
            if not new_title:
                return jsonify({"error": "title cannot be empty"}), 400
            task.title = new_title

        if "description" in data:
            desc = (data.get("description") or "").strip()
            task.description = desc or None

        if "status" in data:
            status = (data.get("status") or "").strip().upper()
            if status not in {"PENDING", "IN_PROGRESS", "DONE"}:
                return jsonify({"error": "status must be PENDING, IN_PROGRESS, or DONE"}), 400
            task.status = status

        db.session.commit()
        return jsonify(task.to_dict()), 200

    @app.delete("/tasks/<int:task_id>")
    def delete_task(task_id: int):
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return jsonify({"deleted": True, "id": task_id}), 200

    # Initialize DB tables at startup
    with app.app_context():
        init_db()

    return app


app = create_app()

if __name__ == "__main__":
    # For local debugging only; in Docker we use gunicorn.
    app.run(host="0.0.0.0", port=5000, debug=True)

import os
from datetime import datetime

from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # Basic config
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    db_host = os.getenv("DB_HOST", "db")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "taskdb")
    db_user = os.getenv("DB_USER", "taskuser")
    db_password = os.getenv("DB_PASSWORD", "taskpass")

    # mysql+pymysql://user:pass@host:port/dbname
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Helps avoid broken/stale DB connections (useful for Docker/EC2/RDS)
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

    db.init_app(app)

    class Task(db.Model):
        __tablename__ = "tasks"
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(200), nullable=False)
        description = db.Column(db.Text, nullable=True)
        status = db.Column(db.String(20), nullable=False, default="PENDING")
        created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

        def to_dict(self):
            return {
                "id": self.id,
                "title": self.title,
                "description": self.description,
                "status": self.status,
                "created_at": self.created_at.isoformat() + "Z",
            }

    def init_db():
        # create tables if they don't exist
        db.create_all()

    # -------------------------
    # API routes (existing)
    # -------------------------

    @app.get("/health")
    def health():
        # Checks app and DB connectivity
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return jsonify({"status": "ok", "db": "ok"}), 200
        except Exception as e:
            return jsonify({"status": "degraded", "db": "error", "detail": str(e)}), 500

    @app.get("/tasks")
    def list_tasks():
        tasks = Task.query.order_by(Task.id.desc()).all()
        return jsonify([t.to_dict() for t in tasks]), 200

    @app.post("/tasks")
    def create_task():
        data = request.get_json(silent=True) or {}
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify({"error": "title is required"}), 400

        task = Task(
            title=title,
            description=(data.get("description") or "").strip() or None,
            status=(data.get("status") or "PENDING").strip().upper(),
        )
        if task.status not in {"PENDING", "IN_PROGRESS", "DONE"}:
            return jsonify({"error": "status must be PENDING, IN_PROGRESS, or DONE"}), 400

        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201

    @app.get("/tasks/<int:task_id>")
    def get_task(task_id: int):
        task = Task.query.get_or_404(task_id)
        return jsonify(task.to_dict()), 200

    @app.put("/tasks/<int:task_id>")
    def update_task(task_id: int):
        task = Task.query.get_or_404(task_id)
        data = request.get_json(silent=True) or {}

        if "title" in data:
            new_title = (data.get("title") or "").strip()
            if not new_title:
                return jsonify({"error": "title cannot be empty"}), 400
            task.title = new_title

        if "description" in data:
            desc = (data.get("description") or "").strip()
            task.description = desc or None

        if "status" in data:
            status = (data.get("status") or "").strip().upper()
            if status not in {"PENDING", "IN_PROGRESS", "DONE"}:
                return jsonify({"error": "status must be PENDING, IN_PROGRESS, or DONE"}), 400
            task.status = status

        db.session.commit()
        return jsonify(task.to_dict()), 200

    @app.delete("/tasks/<int:task_id>")
    def delete_task(task_id: int):
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return jsonify({"deleted": True, "id": task_id}), 200

    # -------------------------
    # UI routes (new)
    # -------------------------

    @app.get("/")
    def ui_home():
        tasks = Task.query.order_by(Task.id.desc()).all()
        return render_template("index.html", title="Task Manager", tasks=tasks, error=None)

    @app.post("/ui/tasks")
    def ui_create_task():
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip() or None
        status = (request.form.get("status") or "PENDING").strip().upper()

        if not title:
            tasks = Task.query.order_by(Task.id.desc()).all()
            return render_template(
                "index.html",
                title="Task Manager",
                tasks=tasks,
                error="Title is required."
            ), 400

        if status not in {"PENDING", "IN_PROGRESS", "DONE"}:
            tasks = Task.query.order_by(Task.id.desc()).all()
            return render_template(
                "index.html",
                title="Task Manager",
                tasks=tasks,
                error="Invalid status."
            ), 400

        task = Task(title=title, description=description, status=status)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for("ui_home"))

    @app.post("/ui/tasks/<int:task_id>/status")
    def ui_update_status(task_id: int):
        task = Task.query.get_or_404(task_id)
        status = (request.form.get("status") or "").strip().upper()
        if status in {"PENDING", "IN_PROGRESS", "DONE"}:
            task.status = status
            db.session.commit()
        return redirect(url_for("ui_home"))

    @app.post("/ui/tasks/<int:task_id>/delete")
    def ui_delete_task(task_id: int):
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for("ui_home"))

    # Initialize DB tables at startup
    with app.app_context():
        init_db()

    return app


app = create_app()

if __name__ == "__main__":
    # For local debugging only; in Docker we use gunicorn.
    app.run(host="0.0.0.0", port=5000, debug=True)
