from flask import Flask, render_template, request, send_file
import praw
import matplotlib.pyplot as plt
import os
import base64
from io import BytesIO

app = Flask(__name__)
from datetime import datetime

def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    return datetime.fromtimestamp(value).strftime(format)
app.jinja_env.filters['datetimeformat'] = datetimeformat

# Reddit API configuration (replace with your own credentials)
REDDIT_CLIENT_ID = "enter your client id here"
REDDIT_CLIENT_SECRET = "enter your clien secret key here"
REDDIT_USER_AGENT = "YourAppName/1.0 by YourRedditUsername"

# Initialize PRAW Reddit instance
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

# Utility function to generate graphs
def generate_graph(data, title, xlabel, ylabel):
    plt.figure(figsize=(8, 6))
    plt.bar(data.keys(), data.values(), color='#FF4500')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha='right')
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    graph_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()
    return graph_base64

@app.route('/', methods=['GET', 'POST'])
def index():
    user_info = None
    graphs = {}
    suggestions = []

    if request.method == 'POST':
        username = request.form['username']

        try:
            user = reddit.redditor(username)
            user_info = {
                'name': user.name,
                'comment_karma': user.comment_karma,
                'link_karma': user.link_karma,
                'created_utc': user.created_utc
            }

            # Example visualization: Post types distribution
            post_types = {'Submissions': user.link_karma, 'Comments': user.comment_karma}
            graphs['Post Types Distribution'] = generate_graph(post_types, 'Post Types Distribution', 'Type', 'Karma')

            # Example suggestion: Improve engagement
            if user.comment_karma < user.link_karma:
                suggestions.append('Consider engaging more with other users through comments.')
            else:
                suggestions.append('Great job on engaging with the community through comments!')

        except Exception as e:
            suggestions.append(f'Error fetching data for user: {e}')

    return render_template('index.html', user_info=user_info, graphs=graphs, suggestions=suggestions)


@app.route('/download_report/<username>')
def download_report(username):
    # For simplicity, let's create a text report on the fly
    report_path = f'reports/{username}_report.txt'
    os.makedirs('reports', exist_ok=True)

    with open(report_path, 'w') as report_file:
        report_file.write(f'Report for Reddit User: {username}\n')
        report_file.write('This is a sample report. You can expand this to include detailed user analysis.\n')

    return send_file(report_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
