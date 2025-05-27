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



@app.route('/detail/<student_id>')
def detail(student_id):
    profile = None
    if os.path.exists('profiles.csv'):
        with open('profiles.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[2] == student_id:  # 学籍番号で一致
                    profile = row
                    break
    if profile:
        return render_template('detail.html', profile=profile)
    else:
        return "プロフィールが見つかりません", 404



@app.route('/search')
def search():
    target_name = request.args.get('name', '').strip()
    target_grade = request.args.get('grade', '').strip()
    matched = []

    if os.path.exists('profiles.csv'):
        with open('profiles.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                name_match = target_name in row[0] if target_name else True
                grade_match = row[1] == target_grade if target_grade else True
                if name_match and grade_match:
                    matched.append(row)

    return render_template('index.html', profiles=matched)
