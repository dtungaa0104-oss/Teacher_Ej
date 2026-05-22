from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# Load curriculum data
with open('data/curriculum.json', 'r', encoding='utf-8') as f:
    CURRICULUM = json.load(f)

@app.route('/')
def index():
    return render_template('index.html', 
                           grades=CURRICULUM['grades'],
                           periods=CURRICULUM['periods'])

@app.route('/api/subjects/<grade>')
def get_subjects(grade):
    grade_data = CURRICULUM['grades'].get(grade, {})
    subjects = list(grade_data.get('subjects', {}).keys())
    return jsonify(subjects)

@app.route('/api/topics/<grade>/<subject>')
def get_topics(grade, subject):
    grade_data = CURRICULUM['grades'].get(grade, {})
    subjects = grade_data.get('subjects', {})
    topics = subjects.get(subject, {}).get('topics', [])
    return jsonify(topics)

@app.route('/api/generate', methods=['POST'])
def generate_plan():
    data = request.json
    
    manager_name = data.get('manager_name', '')
    subject = data.get('subject', '')
    topic = data.get('topic', '')
    grade = data.get('grade', '')
    period = data.get('period', '40')
    teacher_name = data.get('teacher_name', '')
    
    grade_label = CURRICULUM['grades'].get(grade, {}).get('label', f'{grade}-р анги')
    
    try:
        total_min = int(period)
    except:
        total_min = 40
        
    intro_time = max(5, total_min // 8)
    explore_time = total_min // 3
    practice_time = total_min // 4
    elaborate_time = total_min // 6
    evaluate_time = total_min - intro_time - explore_time - practice_time - elaborate_time

    math_section = None
    if "Математик" in subject or "Алгебр" in subject or "Геометр" in subject:
        math_section = {
            "example_title": f"👨‍🏫 Сурах бичгийн жишээ бодлого ({topic})",
            "example_body": f"🧬 <b>Бодлого:</b> {topic} сэдвийн дүрмийг ашиглан дараах илэрхийллийг хялбарчлан бод.<br>"
                            f"<i>Бодолтын алхам:</i><br>"
                            f"1. Өгөгдсөн нөхцөлийг томьёоны дагуу анхны хэлбэрт шилжүүлэх.<br>"
                            f"2. Үйлдлийг дэс дарааллын дагуу гүйцэтгэх.",
            "exercises": [
                f"1. {topic} сэдвийг бататгах үндсэн түвшний дасгал (Сурах бичгийн Бодлого №1)",
                f"2. Логик сэтгэлгээ шаардсан ахисан түвшний даалгавар (Сурах бичгийн Бодлого №2)"
            ]
        }

    plan_data = {
        'header': {
            'manager': manager_name,
            'teacher': teacher_name,
            'grade': grade_label,
            'subject': subject,
            'topic': topic,
            'period': f"{period} минут"
        },
        'objectives': {
            'A': f'Сурагч "{topic}" сэдвийн ухагдахууныг таньж мэдэх, сурах бичгийн дүрмийг ойлгох.',
            'B': f'Өгөгдсөн жишээ бодлогын алгоритмыг ашиглан {topic} дасгалыг бие даан зөв бодож сурах.',
            'C': f'Сурсан мэдлэгээ багш болон хосын дэмжлэгтэйгээр бататгаж, практик амьдралд хэрэглэх.'
        },
        'design': {
            'method': 'Судалгаанд суурилсан индуктив арга (Discovery Learning) ба Багаар хамтран суралцах техник.',
            'tools': f'Математик сурах бичгүүд, багшийн гарын авлага, Wordwall интерактив дасгал.',
            'engagement': 'Анги нийтээр идэвхтэй оролцох бөгөөд Explore үе шатанд 4-5 хүнтэй багт хуваагдаж дасгал ажиллана.'
        },
        'stages': [
            {
                'name': 'I. ЭХЛЭЛ (ИДЭВХЖҮҮЛЭЛТ)',
                'time': intro_time,
                'purpose': 'Өмнөх мэдлэгийг сэргээх, сэдэл төрүүлэх',
                'teacher_actions': 'Хичээлийн зорилгыг танилцуулна. Шинэ сэдэвтэй холбоотой өдөр тутмын амьдралын жишээ асуулт тавина.',
                'student_actions': 'Багшийн асуултад хариулж, тархины шуурга аргаар өмнөх үзсэн хичээлээ сэргээн ярилцана.',
                'assessment': 'Асуулт хариултын идэвхжүүлэлт'
            },
            {
                'name': 'II. ӨРНӨЛ (ШИНЭ МЭДЛЭГ)',
                'time': explore_time + practice_time + elaborate_time,
                'purpose': 'Агуулгыг судлах, дадлага хийх',
                'teacher_actions': f'Шинэ мэдлэгийн дүрмийг сурах бичгийн дагуу тайлбарлана. Дасгал, бодлогуудыг самбарт чиглүүлэн бодуулж, Wordwall дасгал нээнэ.',
                'student_actions': 'Тэмдэглэл хөтөлнө. Хосоор болон багаар ажиллаж, өгөгдсөн даалгаврыг сурах бичгээс бие даан гүйцэтгэнэ.',
                'assessment': 'Гүйцэтгэлийн үнэлгээ, хоорондын хяналт'
            },
            {
                'name': 'III. ТӨГСГӨЛ (ҮНЭЛГЭЭ)',
                'time': evaluate_time,
                'purpose': 'Ойлголтыг баталгаажуулах, рефлекси',
                'teacher_actions': 'Хичээлийг нэгтгэн дүгнэж, гэрийн даалгаврыг зааварчилна. Идэвхтэй сурагчдыг үнэлнэ.',
                'student_actions': 'Юу сурснаа "3-2-1" картаар тэмдэглэнэ. Exit ticket хуудсыг бөглөж багшид хураалгана.',
                'assessment': '3-2-1 карт, хуудасны хураалт'
            }
        ],
        'math_section': math_section,
        'homework': f'Сурах бичгийн арын холбогдох хуудасны дасгалыг гүйцэтгэж, жишээг хуулж ирэх.',
        'diff': {
            'support': 'Дэмжлэг хэрэгтэй сурагчдад хялбаршуулсан карт болон багшийн нэмэлт зааварчилгаа өгнө.',
            'advanced': 'Дэвшилтэт сурагчдад логик сэтгэлгээ шаардсан нэмэлт бодлого, бүтээлч даалгавар өгнө.'
        }
    }
    
    return jsonify(plan_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
