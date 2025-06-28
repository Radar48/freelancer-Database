
from flask import Blueprint, render_template, redirect, url_for, request, flash, Response, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
import plotly.graph_objs as go
import plotly.offline as pyo
from datetime import datetime

routes = Blueprint('routes', __name__)

@routes.route("/register", methods=["GET", "POST"])
def register():
    from app import db
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        hashed = generate_password_hash(password)
         # Get currency from dropdown menu in the registration form
        currency = request.form.get("currency")
        new_user = User(username=username, email=email, password_hash=hashed, currency=currency)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful!")
        return redirect(url_for("routes.login"))
    return render_template("register.html")

@routes.route("/login", methods=["GET", "POST"])
def login():
    from app import db
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = db.session.query(User).filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            new_currency = request.form.get("currency")
            if new_currency and new_currency != user.currency:
                user.currency = new_currency
                db.session.commit()

            return redirect(url_for("routes.dashboard"))
        flash("Invalid credentials")
    return render_template("login.html")

@routes.route("/")
def home():
    return render_template("home.html")

@routes.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("routes.login"))

@routes.route("/dashboard")
@login_required
def dashboard():
    from app import db
    from app.models import IncomeEntry
    from collections import Counter, defaultdict

    user_currency=current_user.currency

    selected_month = request.args.get("month", type=int)
    selected_year = request.args.get("year", type=int)
    selected_currency = request.args.get("currency")
    chart_type = request.args.get("chart_type", default="category")

    query = db.session.query(IncomeEntry).filter_by(user_id=current_user.user_id)
    if selected_year:
        query = query.filter(db.extract("year", IncomeEntry.date) == selected_year)
    if selected_month:
        query = query.filter(db.extract("month", IncomeEntry.date) == selected_month)

    entries = query.all()
    total_income = sum(entry.amount for entry in entries)

    # Stats: most used platform & highest amount
    platform_counts = Counter()
    platform_income = defaultdict(float)
    highest_amount = 0

    for entry in entries:
        if entry.platform:
            platform_counts[entry.platform.name] += 1
            platform_income[entry.platform.name] += entry.amount
        if entry.amount > highest_amount:
            highest_amount = entry.amount

    most_used_platform = platform_counts.most_common(1)[0][0] if platform_counts else "N/A"
    most_lucrative_platform = max(platform_income.items(), key=lambda x: x[1])[0] if platform_income else "N/A"

    # Chart logic
    chart_totals = {}
    for entry in entries:
        if chart_type == "platform":
            key = entry.platform.name if entry.platform else "Other"
        else:
            key = entry.category.name if entry.category else "Uncategorized"
        chart_totals[key] = chart_totals.get(key, 0) + entry.amount

    data = [go.Bar(
        x=list(chart_totals.keys()),
        y=list(chart_totals.values()),
        marker=dict(color='#636EFA'),
        text=list(chart_totals.values()),
        textposition="auto"
    )]

    layout = go.Layout(
        title=f"Income by {chart_type.capitalize()}",
        xaxis=dict(title=chart_type.capitalize()),
        yaxis=dict(title="Total Income"),
        transition=dict(duration=500)
    )

    fig = go.Figure(data=data, layout=layout)
    chart_html = pyo.plot(fig, output_type="div")

    return render_template("dashboard.html",
                           chart_type=chart_type,
                           username=current_user.username,
                           user_currency=user_currency,

                           total_income=total_income,
                           most_used_platform=most_used_platform,
                           most_lucrative_platform=most_lucrative_platform,
                           highest_amount=highest_amount,
                           entries=entries,
                           date=datetime,
                           chart_html=chart_html,
                           selected_month=selected_month,
                           selected_year=selected_year)

@routes.route("/add-entry", methods=["GET", "POST"])
@login_required
def add_entry():
    from app import db
    from app.models import IncomeEntry, Platform, Category
    from datetime import datetime

    platforms = Platform.query.all()
    categories = Category.query.all()

    if request.method == "POST":
        amount = float(request.form["amount"])
        description = request.form["description"]
        entry_date_str = request.form.get("date") or datetime.today().strftime("%Y-%m-%d")
        try:
            entry_date = datetime.strptime(entry_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.")
            return render_template("add_entry.html", platforms=platforms, categories=categories)
        
        platform_id = int(request.form["platform_id"])
        selected_platform = Platform.query.get(platform_id)
        if selected_platform and selected_platform.name == "Other":
            custom_platform_name = request.form.get("custom_platform")
            if custom_platform_name:

                existing = Platform.query.filter_by(name=custom_platform_name).first()
                if existing:
                    platform_id = existing.platform_id
                else:
                    new_platform = Platform(name=custom_platform_name, description="User defined")
                    db.session.add(new_platform)
                    db.session.commit()
                    platform_id = new_platform.platform_id


        category_id = int(request.form["category_id"])
        selected_category = Category.query.get(category_id)
        if selected_category and selected_category.name == "Other":
            custom_category_name = request.form.get("custom_category")
            if custom_category_name:
                existing = Category.query.filter_by(name=custom_category_name).first()
                if existing:
                    category_id = existing.category_id
                else:
                    new_category = Category(name=custom_category_name, description="User defined")
                    db.session.add(new_category)
                    db.session.commit()
                    category_id = new_category.category_id




        new_entry = IncomeEntry(
            user_id=current_user.user_id,
            amount=amount,
            description=description,
            date=entry_date,
            platform_id=platform_id,
            category_id=category_id
        )
        db.session.add(new_entry)
        db.session.commit()
        flash("Income entry added successfully!")
        return redirect(url_for("routes.dashboard"))

    return render_template("add_entry.html", platforms=platforms, categories=categories)

@routes.route("/export")
@login_required
def export_data():
    from app import db
    from app.models import IncomeEntry
    import csv
    from io import StringIO, BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    export_format = request.args.get("format", "csv")
    entries = db.session.query(IncomeEntry).filter_by(user_id=current_user.user_id).all()

    if export_format == "csv":
        si = StringIO()
        writer = csv.writer(si)
        writer.writerow(["Date", "Platform", "Category", f"Amount ({current_user.currency})", "Description"])
        for entry in entries:
            writer.writerow([
                entry.date,
                entry.platform.name if entry.platform else "",
                entry.category.name if entry.category else "",
                entry.amount,
                entry.description or ""
            ])
        output = Response(si.getvalue(), mimetype="text/csv")
        output.headers["Content-Disposition"] = "attachment; filename=income_data.csv"
        return output

    elif export_format == "pdf":
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.drawString(50, 750, f"{current_user.username}'s Income Entries")
        y = 730
        for entry in entries:
            line = f"{entry.date} | {entry.platform.name if entry.platform else ''} | {entry.category.name if entry.category else ''} | {current_user.currency} {entry.amount:.2f} | {entry.description or ''}"
            p.drawString(50, y, line)
            y -= 15
            if y < 50:
                p.showPage()
                y = 750
        p.save()
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="income_data.pdf", mimetype="application/pdf")

    flash("Invalid export format requested.")
    return redirect(url_for("routes.dashboard"))

@routes.route("/clear-all", methods=["POST"])
@login_required
def clear_all_entries():
    from app import db
    from app.models import IncomeEntry

    IncomeEntry.query.filter_by(user_id=current_user.user_id).delete()
    db.session.commit()
    flash("All income entries cleared.")
    return redirect(url_for("routes.dashboard"))