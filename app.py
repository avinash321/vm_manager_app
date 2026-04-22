from flask import Flask, render_template, request, redirect, session, flash, jsonify
import requests

app = Flask(__name__)
app.secret_key = "supersecret"

BASE_URL = "https://vm-manager-api.onrender.com/api/v1"


# ---------------- COMMON ----------------
def get_headers():
    token = session.get("token")
    if not token:
        return None
    return {"Authorization": f"Bearer {token}"}


# ---------------- START APP ----------------
@app.route("/start-app")
def start_app():
    try:
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


# ---------------- LOGIN ----------------
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
    headers = get_headers()
    if not headers:
        return redirect("/")

    params = {
        "skip": request.args.get("skip", 0),
        "limit": 10
    }

    # Filters
    if request.args.get("name"):
        params["name"] = request.args.get("name")

    if request.args.get("status"):
        params["status"] = request.args.get("status")

    # ✅ NEW: Search by ID
    vm_id = request.args.get("id")
    if vm_id:
        res = requests.get(f"{BASE_URL}/vms/{vm_id}", headers=headers)

        if res.status_code == 200:
            vms = [res.json()]
        else:
            flash("VM not found")
            vms = []

        return render_template("dashboard.html", vms=vms, skip=0)

    # Normal list API
    res = requests.get(f"{BASE_URL}/vms", headers=headers, params=params)

    if res.status_code != 200:
        flash("Failed to fetch VMs")
        vms = []
    else:
        vms = res.json()

    return render_template("dashboard.html", vms=vms, skip=int(params["skip"]))


# ---------------- VIEW VM ----------------
@app.route("/vm/<int:vm_id>")
def view_vm(vm_id):
    headers = get_headers()
    if not headers:
        return redirect("/")

    res = requests.get(f"{BASE_URL}/vms/{vm_id}", headers=headers)

    if res.status_code != 200:
        flash("VM not found")
        return redirect("/dashboard")

    vm = res.json()
    return render_template("view_vm.html", vm=vm)


# ---------------- CREATE ----------------
@app.route("/create", methods=["GET", "POST"])
def create_vm():
    headers = get_headers()
    if not headers:
        return redirect("/")

    if request.method == "POST":
        res = requests.post(
            f"{BASE_URL}/vms",
            json=request.form,
            headers=headers
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
    headers = get_headers()
    if not headers:
        return redirect("/")

    if request.method == "POST":
        res = requests.put(
            f"{BASE_URL}/vms/{vm_id}",
            json=request.form,
            headers=headers
        )

        if res.status_code == 200:
            flash("VM updated successfully")
        else:
            flash("Update failed")

        return redirect("/dashboard")

    res = requests.get(f"{BASE_URL}/vms/{vm_id}", headers=headers)
    vm = res.json()

    return render_template("update_vm.html", vm=vm)


# ---------------- DELETE ----------------
@app.route("/delete/<int:vm_id>")
def delete_vm(vm_id):
    headers = get_headers()
    if not headers:
        return redirect("/")

    res = requests.delete(f"{BASE_URL}/vms/{vm_id}", headers=headers)

    if res.status_code == 200:
        flash("VM deleted")
    else:
        flash("Delete failed")

    return redirect("/dashboard")

# ---------------- PROFILE ----------------
@app.route("/profile")
def profile():
    headers = get_headers()
    if not headers:
        return redirect("/")

    res = requests.get(f"{BASE_URL}/users/me", headers=headers)

    if res.status_code != 200:
        flash("Failed to load profile")
        return redirect("/dashboard")

    user = res.json()

    return render_template("profile.html", user=user)


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)