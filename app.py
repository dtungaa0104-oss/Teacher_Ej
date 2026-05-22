from flask import Flask, render_template, request, jsonify
import json
import os
import anthropic

app = Flask(__name__)

# Load curriculum data
with open('data/curriculum.json', 'r', encoding='utf-8') as f:
    CURRICULUM = json.load(f)

client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY env var

@app.route('/')
def index():
    return render_template('index.html',
                           grades=CURRICULUM['grades'],
                           periods=CURRICULUM['periods'])

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

    prompt = f"""Та Монгол ЕБС-ийн мэргэшсэн хичээлийн хөтөлбөр боловсруулагч AI байна.
Дараах мэдээллээр БҮРЭН, ДЭЛГЭРЭНГҮЙ хичээлийн хөтөлбөр үүсгэнэ үү.

МЭДЭЭЛЭЛ:
- Сургалтын менежер: {manager_name or 'тодорхойгүй'}
- Багш: {teacher_name or 'тодорхойгүй'}
- Анги: {grade_label}
- Хичээл: {subject}
- {'Нэгж хичээл: ' + unit_title if unit_title else ''}
- {'Ээлжит хичээлийн сэдэв: ' + topic if is_eeljit else 'Сэдэв: ' + topic}
- Хугацаа: {period} минут
- Нэмэлт зорилт: {objectives or 'байхгүй'}

JSON ФОРМАТААР ХАРИУЛНА УУ (бусад текст огт оруулахгүй):
{{
  "header": {{
    "subject": "{subject}",
    "topic": "{topic}",
    "grade": "{grade_label}",
    "period": "{period} минут",
    "manager": "{manager_name}",
    "teacher": "{teacher_name}"
  }},
  "objectives": {{
    "A": "Сурагч [сэдэв]-ийн үндсэн ойлголтыг мэдэж, дурдаж чадна — тодорхой мэдлэгийн зорилт",
    "B": "Сурагч [сэдэв]-ийг ойлгож, тайлбарлах, жишээ гаргах чадвартай болно — чадварын зорилт",
    "C": "Сурагч [сэдэв]-ийг өөрийн амьдрал, дараагийн сурлагад хэрэглэж чадна — хэрэглээний зорилт"
  }},
  "design": {{
    "method": "Энэ сэдэвт тохирсон дэлгэрэнгүй арга зүй — Discovery Learning, Cooperative Learning гэх мэт",
    "tools": "Энэ хичээлд хэрэглэх тодорхой цахим болон биет хэрэглэгдэхүүн",
    "engagement": "Ангийн зохион байгуулалт, бүлгийн тоо, байрлал, оролцооны арга"
  }},
  "stages": [
    {{
      "name": "I. ЭХЛЭЛ",
      "time": {max(5, int(period)//8)},
      "purpose": "Урьдчилсан мэдлэг идэвхжүүлэлт",
      "teacher_actions": "Тодорхой нээлттэй асуулт, жишээ, видео эсвэл зураг ашиглах — дэлгэрэнгүй",
      "student_actions": "Сурагчдын хийх тодорхой үйлдэл",
      "assessment": "Үнэлгээний арга"
    }},
    {{
      "name": "II. СУДЛАЛ",
      "time": {int(period)//3 + int(period)//4},
      "purpose": "Шинэ мэдлэг олж авах, практик",
      "teacher_actions": "Алхам алхамаар дэлгэрэнгүй үйл ажиллагаа — Explore, Explain, Practice",
      "student_actions": "Сурагчдын хийх тодорхой ажил, хэлэлцэх асуулт",
      "assessment": "Бүлгийн ажил үнэлгээ"
    }},
    {{
      "name": "III. ДҮГНЭЛТ",
      "time": {int(period) - max(5, int(period)//8) - int(period)//3 - int(period)//4},
      "purpose": "Ойлголт бататгал, үнэлгээ",
      "teacher_actions": "3-2-1 арга, Exit ticket, дараагийн холбоо",
      "student_actions": "3-2-1 карт бөглөх: 3 сурсан, 2 сонирхолтой, 1 асуулт",
      "assessment": "Exit ticket, 3-2-1 карт"
    }}
  ],
  "differentiation": {{
    "support": "Дэмжлэг хэрэгтэй сурагчдад зориулсан тодорхой арга, даалгавар",
    "advanced": "Дэвшилтэт сурагчдад зориулсан нэмэлт, өргөтгөсөн даалгавар"
  }},
  "homework": "Тодорхой, хэмжигдэхүйц гэрийн даалгавар — econtent.mn болон бусад эх сурвалжтай холбосон"
}}

Бүх талбарыг МОНГОЛ ХЭЛЭЭР, ДЭЛГЭРЭНГҮЙ, ТОДОРХОЙ бөглөнө үү. Зөвхөн JSON буцаана уу."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        plan = json.loads(raw.strip())
        return jsonify({'plan': plan})
    except Exception as e:
        # Fallback to template-based plan if API fails
        plan = fallback_plan(manager_name, teacher_name, subject, topic,
                             unit_title, grade_label, period)
        return jsonify({'plan': plan, 'fallback': True})


def fallback_plan(manager, teacher, subject, topic, unit_title, grade_label, period):
    p = int(period)
    intro = max(5, p // 8)
    main  = p // 3 + p // 4
    end   = p - intro - main
    return {
        'header': {
            'subject': subject, 'topic': topic,
            'grade': grade_label, 'period': f'{period} минут',
            'manager': manager, 'teacher': teacher
        },
        'objectives': {
            'A': f'Сурагч «{topic}»-ийн үндсэн ойлголт, тодорхойлолтыг мэдэж, дурдаж чадна.',
            'B': f'Сурагч «{topic}»-ийг өмнөх мэдлэгтэй холбон тайлбарлах, жишээ гаргаж чадна.',
            'C': f'Сурагч «{topic}»-ийн мэдлэгийг өөрийн амьдралд хэрэглэж, бүтээлч даалгавар гүйцэтгэх чадвартай болно.'
        },
        'design': {
            'method': 'Discovery Learning + Cooperative Learning: сурагч жишээ шинжилгээгээр дүгнэлт гаргах, бүлгийн хамтарсан суралцахуй.',
            'tools': f'Wordwall.net интерактив дасгал; Jamboard бүлгийн самбар; {subject} сурах бичиг; econtent.mn.',
            'engagement': 'Сурагчдыг 4–5 хүний бүлгээр ширээний тогтмол байрлалаар зохион байгуулна.'
        },
        'stages': [
            {
                'name': 'I. ЭХЛЭЛ', 'time': intro,
                'purpose': 'Урьдчилсан мэдлэг идэвхжүүлэлт',
                'teacher_actions': f'«{topic}»-тай холбоотой нээлттэй асуулт тавьж, сурагчдын урьдчилсан мэдлэгийг идэвхжүүлнэ. Хичээлийн зорилтыг тодорхойлно.',
                'student_actions': f'«{topic}»-тай холбоотой өөрсдийн мэдлэг, туршлагаа хуваалцана.',
                'assessment': 'Нээлттэй асуулт, харилцан ярилцалт'
            },
            {
                'name': 'II. СУДЛАЛ', 'time': main,
                'purpose': 'Шинэ мэдлэг, практик',
                'teacher_actions': f'Explore: «{topic}»-ийн жишээ судлуулна.\nExplain: Дүгнэлтийг нэгтгэн тайлбарлана.\nPractice: Wordwall болон бүлгийн практик дасгал.',
                'student_actions': f'Хос болон бүлгээр ажиллан «{topic}»-ийн шинж чанарыг нээнэ. Самбарт дүгнэлтийг бичнэ.',
                'assessment': 'Бүлгийн танилцуулга, Wordwall тест'
            },
            {
                'name': 'III. ДҮГНЭЛТ', 'time': end,
                'purpose': 'Бататгал, үнэлгээ',
                'teacher_actions': 'Хичээлийг нэгтгэж, дараагийн холбоог тодорхойлно. Гэрийн даалгавар тайлбарлана.',
                'student_actions': '3-2-1 карт бөглөнө (3 сурсан, 2 сонирхолтой, 1 асуулт). Exit ticket.',
                'assessment': '3-2-1 карт, Exit ticket'
            }
        ],
        'differentiation': {
            'support': f'Хялбаршуулсан жишээ, нөхөх дасгал, нэмэлт хос ажил.',
            'advanced': f'Ахисан түвшний даалгавар, бусдад тайлбарлах, нэмэлт судалгаа.'
        },
        'homework': f'«{topic}»-тай холбоотой 5–7 жишээ бичиж тайлбарлах. econtent.mn дахь нэмэлт дасгал.'
    }


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
