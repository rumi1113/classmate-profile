import os
import csv
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
import cv2  # 顔検出に必要

def detect_face(image_path):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    return len(faces) > 0


from deepface import DeepFace

def analyze_gender(image_path):
    try:
        result = DeepFace.analyze(image_path, actions=['gender'], enforce_detection=False)
        return result[0]['gender']  # 'Man' or 'Woman'
    except Exception as e:
        print("性別判定エラー:", e)
        return "Unknown"

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
    gender = '不明'
    if photo and photo.filename != '':
        filename = secure_filename(photo.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(filepath)

        # 顔検出
        if not detect_face(filepath):
            os.remove(filepath)  # 顔がない画像は削除
            return "⚠️ 顔が検出できませんでした。別の写真をアップロードしてください。", 400

        # 性別判定
        gender_raw = analyze_gender(filepath)
        if gender_raw == 'Man':
            gender = '男性'
        elif gender_raw == 'Woman':
            gender = '女性'

        photo_url = f'/static/uploads/{filename}'
    else:
        photo_url = ''

    # CSV に保存
    with open('profiles.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([name, grade, student_id, hobby, photo_url, gender])

    return redirect('/')


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
    target_gender = request.args.get('gender', '').strip()
    matched = []

    if os.path.exists('profiles.csv'):
        with open('profiles.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) < 6:
                    continue  # 列数が足りない行は無視

                name_match = target_name in row[0] if target_name else True
                grade_match = row[1] == target_grade if target_grade else True
                gender_match = row[5] == target_gender if target_gender else True
                if name_match and grade_match and gender_match:
                    matched.append(row)

    return render_template('index.html', profiles=matched)


# 🔥 Render用に必要なポート設定（最後に置く！）
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
