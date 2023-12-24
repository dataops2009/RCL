from flask import Flask, render_template, redirect, url_for, request



app = Flask(__name__)

teams = []

@app.route('/subscribe')
def subscribe():
    # Define your subscription tiers
    tiers = [
        {'name': 'Basic', 'price': '$5.50/month', 'features': ['Feature 1', 'Feature 2']},
        {'name': 'Premium', 'price': '$10/month', 'features': ['Feature 1', 'Feature 2', 'Feature 3']},
        {'name': 'Pro', 'price': '$20/month', 'features': ['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4']}
    ]
    return render_template('subscribe.html', tiers=tiers)

@app.route('/profile')
def profile():
    # ... any necessary logic ...
    return render_template('profile.html')

@app.route('/create-team', methods=['GET'])
def create_team_form():
    # ... any necessary logic ...
    return render_template('create_team.html')

@app.route('/submit-team', methods=['POST'])
def submit_team():
    team_name = request.form['team_name']
    team_description = request.form['team_description']
    teams.append({'team_name':team_name,'team_description':team_description})
    # Redirect to the profile or another appropriate page
    print(teams)
    return redirect(url_for('profile'))

if __name__ == '__main__':
    app.run(debug=True)
