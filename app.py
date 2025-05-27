import os
import csv
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# アップロード先ディレクトリがなければ作成
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    profiles = []
    if os.path.exists('profiles.csv'):
        with open('profiles.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                profiles.append(row)
    return render_template('index.html', profiles=profiles)

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    grade = request.form['grade']
    student_id = request.form['student_id']
    hobby = request.form['hobby']
    photo = request.files['photo']

    filename = ''
    if photo and photo.filename != '':
        filename = secure_filename(photo.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(filepath)
        photo_url = f'/static/uploads/{filename}'
    else:
        photo_url = ''

    # CSV に保存
    with open('profiles.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([name, grade, student_id, hobby, photo_url])

    return redirect('/')

# 🔥 Render用に必要なポート設定
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
