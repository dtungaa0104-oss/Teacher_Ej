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

@app.route('/api/units/<grade>/<subject>')
def get_units(grade, subject):
    grade_data = CURRICULUM['grades'].get(grade, {})
    subjects   = grade_data.get('subjects', {})
    units = [{'title': u['title'], 'lesson_count': len(u['lessons'])}
             for u in subjects.get(subject, {}).get('units', [])]
    return jsonify(units)

@app.route('/api/lessons/<grade>/<subject>/<int:unit_idx>')
def get_lessons(grade, subject, unit_idx):
    grade_data = CURRICULUM['grades'].get(grade, {})
    units      = grade_data.get('subjects', {}).get(subject, {}).get('units', [])
    if unit_idx >= len(units):
        return jsonify([])
    return jsonify(units[unit_idx]['lessons'])

@app.route('/api/generate', methods=['POST'])
def generate_plan():
    data = request.json
    manager_name = data.get('manager_name', '')
    teacher_name = data.get('teacher_name', '')
    subject      = data.get('subject', '')
    topic        = data.get('topic', '')
    unit_title   = data.get('unit_title', '')
    is_eeljit    = data.get('is_eeljit', False)
    grade        = data.get('grade', '')
    period       = data.get('period', '40')
    objectives   = data.get('objectives', '')

    grade_label = CURRICULUM['grades'].get(grade, {}).get('label', f'{grade}-р анги')

    plan = generate_lesson_plan(
        manager_name=manager_name,
        teacher_name=teacher_name,
        subject=subject,
        topic=topic,
        unit_title=unit_title,
        is_eeljit=is_eeljit,
        grade_label=grade_label,
        period=period,
        objectives=objectives
    )
    return jsonify({'plan': plan})


def generate_lesson_plan(manager_name, teacher_name, subject, topic,
                         unit_title, is_eeljit, grade_label, period, objectives):
    period_int = int(period)

    intro_time    = max(5, period_int // 8)
    explore_time  = int(period_int * 0.35)
    practice_time = int(period_int * 0.28)
    evaluate_time = period_int - intro_time - explore_time - practice_time

    topic_type = "Ээлжит хичээл" if is_eeljit else "Нэгж хичээл"

    return {
        'header': {
            'subject':    subject,
            'topic':      topic,
            'unit_title': unit_title,
            'topic_type': topic_type,
            'grade':      grade_label,
            'period':     f'{period} минут',
            'manager':    manager_name,
            'teacher':    teacher_name
        },
        'objectives': {
            'A': f'Сурагч "{topic}"-ийн үндсэн ойлголт, тодорхойлолтыг мэдэж, жишээ дурдах чадвартай болно.',
            'B': f'Сурагч "{topic}"-ийг өмнөх мэдлэгтэй холбон тайлбарлах, шинэ нөхцөлд хэрэглэж чадна.',
            'C': f'Сурагч "{topic}"-ийн мэдлэгийг амьдралын нөхцөлд хэрэглэж, бүтээлч даалгавар гүйцэтгэх чадвартай болно.'
        },
        'design': {
            'method':     'Discovery Learning (судалгаанд суурилсан): сурагч жишээ дүн шинжилгээгээр дүгнэлт гаргана. Cooperative Learning: хос болон бүлгийн хамтарсан суралцахуй.',
            'tools':      f'Wordwall.net интерактив дасгал; Jamboard/Padlet бүлгийн самбар; {subject}-ийн сурах бичиг; хэлхэмж зургийн карт.',
            'engagement': f'Сурагчид 4-5 хүний бүлгээр ширээний тогтмол байрлалаар ажиллана. "{topic}" сэдвийн хичээлд интерактив хэрэглэгдэхүүн ашиглана.'
        },
        'stages': [
            {
                'name':            'I. ЭХЛЭЛ',
                'time':            intro_time,
                'purpose':         'Оролцоо ба идэвхжүүлэлт',
                'teacher_actions': f'Нээлттэй асуулт тавьж урьдчилсан мэдлэгийг идэвхжүүлнэ. "{topic}"-тай холбоотой сонирхолтой жишээ эсвэл зураг харуулна. Хичээлийн зорилтыг тодорхойлно.',
                'student_actions': f'"{topic}"-тай холбоотой мэдлэг, туршлагаа хуваалцана. Анхны санааг тэмдэглэнэ.',
                'assessment':      'Нээлттэй асуулт, харилцан ярилцалт'
            },
            {
                'name':            'II. СУДЛАЛ',
                'time':            explore_time,
                'purpose':         'Шинэ мэдлэг олж авах',
                'teacher_actions': f'Explore ({int(explore_time*0.4)}мин): жишээ, нотолгоог судлуулна.\nExplain ({int(explore_time*0.3)}мин): дүгнэлтийг нэгтгэн тайлбарлана.\nGuided practice ({int(explore_time*0.3)}мин): Wordwall.net дасгал, карт ажил.',
                'student_actions': f'Хос болон бүлгээр ажиллан "{topic}"-ийн дүрэм, шинж чанарыг нээнэ. Самбарт дүгнэлтийг бичнэ.',
                'assessment':      'Бүлгийн танилцуулга, Wordwall дасгал'
            },
            {
                'name':            'III. ДАСГАЛ',
                'time':            practice_time,
                'purpose':         'Мэдлэг бататгах',
                'teacher_actions': 'Дасгалын хуудас тарааж ганцаарчилсан ажил хийлгэнэ. Алдааг тухайд нь залруулж дэмжлэг үзүүлнэ.',
                'student_actions': 'Дасгалыг ганцаарчилсан болон хосоор бөглөнө. Хариултаа харилцан шалгаж засна.',
                'assessment':      'Дасгалын хуудас, харилцан шалгалт'
            },
            {
                'name':            'IV. ДҮГНЭЛТ',
                'time':            evaluate_time,
                'purpose':         'Ойлголт үнэлэх',
                'teacher_actions': 'Хичээлийн үр дүнг нэгтгэж, дараагийн холбоог тодорхойлно. Гэрийн даалгавар тайлбарлана.',
                'student_actions': '3-2-1 карт бөглөнө (3 сурсан зүйл, 2 сонирхолтой, 1 асуулт). Exit ticket бөглөнө.',
                'assessment':      '3-2-1 карт, Exit ticket'
            }
        ],
        'differentiation': {
            'support':  f'Дэмжлэг хэрэгтэй сурагчид: хялбаршуулсан жишээ, нөхөх дасгал, нэмэлт хос ажил, зурагт дэмжлэг.',
            'advanced': f'Дэвшилтэт сурагчид: ахисан түвшний даалгавар, бүтээлч хэрэглээний жишээ гаргах, бусдад тайлбарлах, нэмэлт судалгаа.'
        },
        'homework': f'"{topic}"-тай холбоотой 5–7 жишээ бичиж тайлбарлах. Econtent.mn дээрх нэмэлт дасгал гүйцэтгэх.'
    }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
