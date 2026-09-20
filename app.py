from flask import Flask, request, render_template_string, redirect, url_for, jsonify
from instagrapi import Client
import time
import random
import threading
import argparse
import os

---------- Setup ----------

app = Flask(name)

SECRET_KEY environment variable se lega

app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

Global variables

client = None
group_threads = []
logs = []
lock = threading.Lock()

---------- Logging System ----------

def log(msg):
"""Live console ke liye log store karo."""
with lock:
logs.append(f"[{time.strftime('%H:%M:%S')}] {msg}")

if len(logs) > 500:  
        del logs[:-500]  

print(msg, flush=True)

def get_logs():
with lock:
return list(logs)

---------- Port Option ----------

parser = argparse.ArgumentParser(
description="Aayush Shrivastava Insta Msg Sender"
)

parser.add_argument(
"--port",
type=int,
default=int(os.environ.get("PORT", 5000)),
help="Port number"
)

args = parser.parse_args()
PORT = args.port

---------- HTML Template ----------

HTML_PAGE = r'''

<!DOCTYPE html>  <html>  
<head>  
    <title>Aayush Shrivastava Insta Msg Sender</title>  <style>  
    * {  
        box-sizing: border-box;  
    }  

    body {  
        font-family: 'Segoe UI', Arial, sans-serif;  
        background: #0f172a;  
        color: #e2e8f0;  
        margin: 0;  
        padding: 20px;  
    }  

    .container {  
        max-width: 800px;  
        margin: 0 auto;  
    }  

    h1 {  
        text-align: center;  
        color: #38bdf8;  
        font-size: 2rem;  
    }  

    .card {  
        background: #1e293b;  
        border-radius: 12px;  
        padding: 20px;  
        margin-bottom: 15px;  
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);  
    }  

    label {  
        display: block;  
        margin-top: 12px;  
        font-weight: 500;  
        color: #94a3b8;  
    }  

    input,  
    select,  
    textarea,  
    button {  
        width: 100%;  
        padding: 10px;  
        margin-top: 5px;  
        border: 1px solid #334155;  
        border-radius: 6px;  
        background: #0f172a;  
        color: #e2e8f0;  
        font-size: 14px;  
    }  

    button {  
        background: #0095f6;  
        border: none;  
        font-weight: bold;  
        cursor: pointer;  
        transition: 0.2s;  
        margin-top: 15px;  
    }  

    button:hover {  
        background: #0077cc;  
    }  

    .error {  
        color: #f87171;  
    }  

    .console {  
        background: #0f172a;  
        border: 1px solid #334155;  
        border-radius: 8px;  
        padding: 10px;  
        height: 220px;  
        overflow-y: auto;  
        font-family: monospace;  
        font-size: 12px;  
        color: #a7f3d0;  
    }  

    a {  
        color: #38bdf8;  
    }  

    .group-list {  
        background: #0f172a;  
        border: 1px solid #334155;  
        border-radius: 6px;  
        padding: 8px;  
        max-height: 200px;  
        overflow-y: auto;  
    }  

    .group-list label {  
        display: block;  
        margin: 3px 0;  
        font-weight: normal;  
    }  

    .group-list input {  
        width: auto;  
        margin-right: 8px;  
    }  

    .footer {  
        text-align: center;  
        margin-top: 20px;  
        color: #64748b;  
        font-size: 12px;  
    }  
</style>

</head>  <body>  <div class="container">  <h1>📨 Aayush Shrivastava Insta Msg Sender</h1>  

{% if not logged_in %}  

<div class="card">  

    <h3>🔑 Instagram Login</h3>  

    <form method="POST" action="/login">  

        <label>Username</label>  

        <input  
            type="text"  
            name="username"  
            placeholder="Your Instagram username"  
            required  
        >  

        <label>Password</label>  

        <input  
            type="password"  
            name="password"  
            placeholder="Your password"  
            required  
        >  

        <label>Proxy (optional)</label>  

        <input  
            type="text"  
            name="proxy"  
            placeholder="http://user:pass@ip:port"  
        >  

        <button type="submit">  
            Login  
        </button>  

    </form>  

</div>  

{% else %}  

<div class="card">  

    <h3>💬 Groups</h3>  

    <form method="POST" action="/send">  

        <label>Select Group(s)</label>  

        <div class="group-list">  

            {% for g in groups %}  

            <label>  
                <input  
                    type="checkbox"  
                    name="groups"  
                    value="{{ g.id }}"  
                >  

                {{ g.title }}  
            </label>  

            {% endfor %}  

        </div>  

        <label>Message Text</label>  

        <textarea  
            name="message"  
            rows="3"  
            placeholder="Jo message bhejna hai..."  
            required  
        ></textarea>  

        <label>Kitni baar bhejna hai?</label>  

        <input  
            type="number"  
            name="times"  
            value="1"  
            min="1"  
            max="10"  
        >  

        <button type="submit">  
            Send Messages  
        </button>  

    </form>  

    <p>  
        <a href="/logout">Logout</a>  
    </p>  

</div>  

{% endif %}  

<div class="card">  

    <h3>🖥️ Live Console</h3>  

    <div class="console" id="console"></div>  

</div>  

<div class="footer">  
    Aayush Shrivastava Insta Msg Sender  
</div>

</div>  <script>  
  
async function refreshLogs() {  
  
    try {  
  
        const res = await fetch('/get_logs');  
  
        const data = await res.json();  
  
        const consoleDiv =  
            document.getElementById('console');  
  
        consoleDiv.innerHTML =  
            data.logs  
            .map(l => '<div>' + l + '</div>')  
            .join('');  
  
        consoleDiv.scrollTop =  
            consoleDiv.scrollHeight;  
  
    } catch (e) {  
        // Ignore temporary errors  
    }  
}  
  
setInterval(refreshLogs, 1000);  
  
refreshLogs();  
  
</script>  </body>  
</html>  
'''  ---------- Routes ----------

@app.route("/")
def index():

return render_template_string(  
    HTML_PAGE,  
    logged_in=(client is not None),  
    groups=group_threads  
)

@app.route("/login", methods=["POST"])
def login():

global client, group_threads  

username = request.form.get(  
    "username", ""  
).strip()  

password = request.form.get(  
    "password", ""  
).strip()  

proxy = request.form.get(  
    "proxy", ""  
).strip()  

if not username or not password:  

    return (  
        "❌ Username/Password empty hai",  
        400  
    )  

cl = Client()  

cl.delay_range = [1, 3]  

if proxy:  

    try:  
        cl.set_proxy(proxy)  
        log("🌍 Proxy configured")  

    except Exception as e:  
        log(f"⚠️ Proxy error: {e}")  

log("🔄 Login try ho raha hai...")  

try:  

    cl.login(  
        username,  
        password  
    )  

    client = cl  

    log(  
        f"✅ Login successful: "  
        f"{cl.account_info().username}"  
    )  

    log(  
        "🔄 Groups fetch ho rahe hain..."  
    )  

    threads = cl.direct_threads(  
        amount=50  
    )  

    group_threads = []  

    for t in threads:  

        if t.thread_type == "group":  

            title = (  
                t.thread_title  
                or "Untitled Group"  
            )  

            group_threads.append({  
                "id": t.id,  
                "title": title  
            })  

            log(  
                f"📂 Group mila: {title}"  
            )  

    if not group_threads:  

        log("⚠️ Koi group nahi mila")  

    else:  

        log(  
            f"✅ {len(group_threads)} "  
            f"groups mil gaye"  
        )  

    return redirect(  
        url_for("index")  
    )  

except Exception as e:  

    log(  
        f"❌ Login failed: {e}"  
    )  

    return (  
        "<div class='error'>"  
        f"Login failed: {e}"  
        "<br>"  
        "<a href='/'>Back</a>"  
        "</div>"  
    )

@app.route("/send", methods=["POST"])
def send():

global client  

if not client:  
    return redirect(url_for("index"))  

group_ids = request.form.getlist(  
    "groups"  
)  

message = request.form.get(  
    "message", ""  
).strip()  

try:  

    times = int(  
        request.form.get(  
            "times", 1  
        )  
    )  

    times = max(  
        1,  
        min(times, 10)  
    )  

except (TypeError, ValueError):  

    times = 1  

if not group_ids or not message:  

    return (  
        "❌ Group ya message empty hai",  
        400  
    )  

log(  
    f"📤 Send start: "  
    f"{len(group_ids)} groups, "  
    f"{times} baar"  
)  

for gid in group_ids:  

    for i in range(times):  

        try:  

            client.direct_send(  
                message,  
                thread_ids=[gid]  
            )  

            log(  
                f"✅ Sent to {gid} "  
                f"(copy {i + 1})"  
            )  

        except Exception as e:  

            log(  
                f"❌ Failed {gid}: {e}"  
            )  

        time.sleep(  
            random.uniform(3, 6)  
        )  

log("🏁 Send complete")  

return redirect(  
    url_for("index")  
)

@app.route("/logout")
def logout():

global client, group_threads  

client = None  
group_threads = []  

log("🔒 Logout ho gaya")  

return redirect(  
    url_for("index")  
)

@app.route("/get_logs")
def get_logs_route():

return jsonify({  
    "logs": get_logs()  
})

---------- Main ----------

if name == "main":

log(  
    f"🚀 Aayush Shrivastava Insta Msg Sender start: "  
    f"http://localhost:{PORT}"  
)  

app.run(  
    host="0.0.0.0",  
    port=PORT,  
    debug=False  
)
