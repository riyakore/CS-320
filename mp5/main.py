import pandas as pd
from flask import Flask, request, jsonify, make_response
import time
import re
import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# TODO: I have chosen the star dataset to predict the star type. We can classify stars by plotting its features based on the HR Diagram.

app = Flask(__name__)
df = pd.read_csv("main.csv")
last_access = {}
visitor_ips = []
visit_count = 0
clicks_from_A = 0
clicks_from_B = 0
selected_version = None

@app.route('/')
def home():
    
    global visit_count, clicks_from_A, clicks_from_B
    
    with open("index.html") as f:
        html = f.read()
        
    if visit_count < 10:
        
        if visit_count % 2 == 0:
            html = html.replace('<a href = "/donate.html">Donate</a>', '<a href="/donate.html?from=A" style="color:blue;">Donate</a>')
            
        else:
            html = html.replace('<a href = "/donate.html">Donate</a>', '<a href="/donate.html?from=B" style="color:red;">Donate</a>')
        
        visit_count += 1
        
    else:
        
        if clicks_from_A >= clicks_from_B:
            html = html.replace('<a href = "/donate.html">Donate</a>', '<a href="/donate.html?from=A" style="color:blue;">Donate</a>')
        
        else:
            html = html.replace('<a href = "/donate.html">Donate</a>', '<a href="/donate.html?from=B" style="color:red;">Donate</a>')

    return html

@app.route('/browse.html')
def browse():
    html_table = df.to_html(index=False, float_format="%.6f")
    return f"<html><body><h1>Data Browser</h1><p>This is the star dataset to predict the star type. We can classify stars by plotting its features based on the HR Diagram.</p>{html_table}</body></html>"

@app.route('/browse.json')
def browse_json():
    
    client_ip = request.remote_addr
    current_time = time.time()
    
    if client_ip in last_access and (current_time - last_access[client_ip]) < 60:
        
        retry_after = int(60 - (current_time - last_access[client_ip]))
        
        response = make_response(
            jsonify({"error": "Try again later"}), 429
        )
        response.headers["Retry-After"] = retry_after
        return response
    
    last_access[client_ip] = current_time
    
    if client_ip not in visitor_ips:
        visitor_ips.append(client_ip)
    
    return jsonify(df.to_dict(orient="records"))

@app.route('/visitors.json')
def visitors_json():
    return jsonify(visitor_ips)

@app.route('/donate.html')
def donate():
    
    global clicks_from_A, clicks_from_B
    
    from_version = request.args.get("from")    
    if from_version == "A":
        clicks_from_A += 1
        version_content = "<p>Thank you for supporting us through Version A. Your donation will help keep this platform running.</p>"
        
    elif from_version == "B":
        clicks_from_B += 1
        version_content = "<p>Thank you for supporting us through Version B. We appreciate your help in maintaining our services.</p>"
        
    else:
        version_content = "<p>Thank you for considering a donation! Every contribution helps us continue our work.</p>"
        
    with open('donate.html') as f:
        html = f.read()
        
    html = html.replace("<!--VERSION_CONTENT-->", version_content)
        
    return html

@app.route('/email', methods=["POST"])
def email():
    email = str(request.data, "utf-8")
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{3}$"
    if len(re.findall(email_pattern, email)) > 0: # 1
        with open("emails.txt", "a") as f: # open file in append mode
            f.write(email + "\n") # 2
            
        with open("emails.txt", "r") as f:
            num_subscribed = sum(1 for _ in f)
            
        return jsonify(f"thanks, your subscriber number is {num_subscribed}!")
    
    return jsonify("Please enter a valid email address. Stop being so careless!") # 3

@app.route('/temperature_distribution.svg')
def temperature_distribution():
    
    bins = int(request.args.get('bins', 10))

    fig, ax = plt.subplots()
    ax.hist(df['Temperature (K)'], bins=bins, color='blue', edgecolor='black')
    ax.set_xlabel('Temperature (K)')
    ax.set_ylabel('Frequency')
    ax.set_title(f'Temperature Distribution with {bins} Bins')
    
    if bins == 10:
        fig.savefig('dashboard1.svg')
    
    else:
        fig.savefig('dashboard1-query.svg')

    plt.close(fig)

    return make_response(open('dashboard1.svg' if bins == 10 else 'dashboard1-query.svg').read(), 200, {'Content-Type': 'image/svg+xml'})

@app.route('/luminosity_by_star_color.svg')
def luminosity_by_star_color():
    
    fig, ax = plt.subplots()
    df.boxplot(column='Luminosity(L/Lo)', by='Star color', ax=ax)
    ax.set_xlabel('Star Color')
    ax.set_ylabel('Luminosity (L/Lo)')
    ax.set_title('Luminosity by Star Color')
    fig.suptitle("")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    fig.savefig('dashboard2.svg')
    plt.close(fig)

    return make_response(open('dashboard2.svg').read(), 200, {'Content-Type': 'image/svg+xml'})

@app.route('/temperature_vs_radius.svg')
def temperature_vs_radius():
    
    fig, ax = plt.subplots()
    ax.scatter(df['Temperature (K)'], df['Radius(R/Ro)'], color='green', alpha=0.5)
    ax.set_xlabel('Temperature (K)')
    ax.set_ylabel('Radius (R/Ro)')
    ax.set_title('Temperature vs. Radius')

    fig.savefig('temperature_vs_radius.svg')
    plt.close(fig)

    return make_response(open('temperature_vs_radius.svg').read(), 200, {'Content-Type': 'image/svg+xml'})


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!

# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.
