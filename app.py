from flask import Flask, render_template, request, redirect, session, flash, jsonify
import requests

app = Flask(__name__)
app.secret_key = "supersecret"

BASE_URL = "https://vm-manager-api.onrender.com/api/v1"


def get_headers():
    token = session.get("token")
    return {"Authorization": f"Bearer {token}"}


# ---------------- LOGIN ----------------

@app.route("/start-app")
def start_app():
    try:
        # Hit your Render app
        response = requests.get(BASE_URL)

        return jsonify({
            "status": "success",
            "message": "App is starting / reloading..."
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        res = requests.post(f"{BASE_URL}/login", json=request.form)

        if res.status_code == 200:
            session["token"] = res.json()["access_token"]
            return redirect("/dashboard")
        else:
            flash("Invalid credentials")

    return render_template("login.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        res = requests.post(f"{BASE_URL}/register", json=request.form)

        if res.status_code == 200:
            flash("Registered successfully. Please login.")
            return redirect("/")
        else:
            flash("User already exists")

    return render_template("register.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    params = {
        "skip": request.args.get("skip", 0),
        "limit": 10
    }

    # Filters
    if request.args.get("name"):
        params["name"] = request.args.get("name")

    if request.args.get("status"):
        params["status"] = request.args.get("status")

    res = requests.get(f"{BASE_URL}/vms", headers=get_headers(), params=params)

    vms = res.json() if res.status_code == 200 else []

    return render_template("dashboard.html", vms=vms, skip=int(params["skip"]))


# ---------------- CREATE ----------------
@app.route("/create", methods=["GET", "POST"])
def create_vm():
    if request.method == "POST":
        res = requests.post(
            f"{BASE_URL}/vms",
            json=request.form,
            headers=get_headers()
        )

        if res.status_code == 200:
            flash("VM created successfully")
            return redirect("/dashboard")
        else:
            flash("Error creating VM")

    return render_template("create_vm.html")


# ---------------- UPDATE ----------------
@app.route("/update/<int:vm_id>", methods=["GET", "POST"])
def update_vm(vm_id):
    if request.method == "POST":
        requests.put(
            f"{BASE_URL}/vms/{vm_id}",
            json=request.form,
            headers=get_headers()
        )
        flash("VM updated")
        return redirect("/dashboard")

    res = requests.get(f"{BASE_URL}/vms/{vm_id}", headers=get_headers())
    vm = res.json()

    return render_template("update_vm.html", vm=vm)


# ---------------- DELETE ----------------
@app.route("/delete/<int:vm_id>")
def delete_vm(vm_id):
    requests.delete(f"{BASE_URL}/vms/{vm_id}", headers=get_headers())
    flash("VM deleted")
    return redirect("/dashboard")


if __name__ == "__main__":
    app.run(debug=True)