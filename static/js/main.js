// BagshAI — Main JavaScript
// Mongolian Lesson Plan Generator

async function loadSubjects() {
  const grade = document.getElementById('gradeSelect').value;
  const subjectSelect = document.getElementById('subjectSelect');
  const topicSelect = document.getElementById('topicSelect');
  
  // Reset downstream
  subjectSelect.innerHTML = '<option value="">— Уншиж байна... —</option>';
  subjectSelect.disabled = true;
  topicSelect.innerHTML = '<option value="">— Эхлээд хичээл сонгоно уу —</option>';
  topicSelect.disabled = true;
  
  if (!grade) {
    subjectSelect.innerHTML = '<option value="">— Эхлээд анги сонгоно уу —</option>';
    return;
  }

  try {
    const res = await fetch(`/api/subjects/${grade}`);
    const subjects = await res.json();
    
    subjectSelect.innerHTML = '<option value="">— Сонгох —</option>';
    subjects.forEach(s => {
      const opt = document.createElement('option');
      opt.value = s;
      opt.textContent = s;
      subjectSelect.appendChild(opt);
    });
    subjectSelect.disabled = false;
  } catch (e) {
    subjectSelect.innerHTML = '<option value="">Алдаа гарлаа</option>';
  }
}

async function loadTopics() {
  const grade = document.getElementById('gradeSelect').value;
  const subject = document.getElementById('subjectSelect').value;
  const topicSelect = document.getElementById('topicSelect');
  
  topicSelect.innerHTML = '<option value="">— Уншиж байна... —</option>';
  topicSelect.disabled = true;
  
  if (!grade || !subject) return;

  try {
    const res = await fetch(`/api/topics/${grade}/${encodeURIComponent(subject)}`);
    const topics = await res.json();
    
    topicSelect.innerHTML = '<option value="">— Сонгох —</option>';
    topics.forEach(t => {
      const opt = document.createElement('option');
      opt.value = t;
      opt.textContent = t;
      topicSelect.appendChild(opt);
    });
    topicSelect.disabled = false;
  } catch (e) {
    topicSelect.innerHTML = '<option value="">Алдаа гарлаа</option>';
  }
}

async function generatePlan() {
  const grade = document.getElementById('gradeSelect').value;
  const subject = document.getElementById('subjectSelect').value;
  const topicSelect = document.getElementById('topicSelect').value;
  const topicCustom = document.getElementById('topicCustom').value.trim();
  const topic = topicCustom || topicSelect;
  const period = document.getElementById('periodSelect').value;
  const objectives = document.getElementById('objectives').value;
  const managerName = document.getElementById('managerName').value.trim();
  const teacherName = document.getElementById('teacherName').value.trim();

  if (!grade || !subject || !topic) {
    alert('Анги, хичээл, сэдвийг сонгоно уу!');
    return;
  }

  // Show loading
  showState('loading');

  try {
    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ grade, subject, topic, period, objectives, manager_name: managerName, teacher_name: teacherName })
    });
    
    const data = await res.json();
    renderPlan(data.plan);
    showState('output');
  } catch (e) {
    alert('Алдаа гарлаа. Дахин оролдоно уу.');
    showState('empty');
  }
}

function showState(state) {
  document.getElementById('emptyState').classList.add('hidden');
  document.getElementById('loadingState').classList.add('hidden');
  document.getElementById('planOutput').classList.add('hidden');
  
  if (state === 'empty') document.getElementById('emptyState').classList.remove('hidden');
  if (state === 'loading') document.getElementById('loadingState').classList.remove('hidden');
  if (state === 'output') document.getElementById('planOutput').classList.remove('hidden');
}

function renderPlan(plan) {
  const h = plan.header;
  const o = plan.objectives;
  const d = plan.design;
  const stages = plan.stages;
  const diff = plan.differentiation;

  const html = `
    <div class="plan-document" id="printable">

      <!-- HEADER -->
      <div class="doc-header">
        <div class="doc-header-top">
          <div>
            <div class="doc-school-name" style="font-size:11px;color:#8899bb;margin-bottom:2px;">
              ${h.manager ? `Сургалтын менежер: <strong style="color:#e8edf5">${h.manager}</strong>` : 'Ерөнхий боловсролын сургууль'}
              ${h.teacher ? ` &nbsp;|&nbsp; Багш: <strong style="color:#e8edf5">${h.teacher}</strong>` : ''}
            </div>
            <div style="font-size:20px;font-weight:700;color:#e8edf5;margin-top:6px;">
              ${h.subject} — ${h.topic}
            </div>
          </div>
          <div class="doc-badge">ХИЧЭЭЛИЙН ХӨТӨЛБӨР</div>
        </div>
        <div class="doc-meta-grid">
          <div class="doc-meta-item">
            <span class="doc-meta-label">Хичээл</span>
            <span class="doc-meta-value">${h.subject}</span>
          </div>
          <div class="doc-meta-item">
            <span class="doc-meta-label">Анги</span>
            <span class="doc-meta-value">${h.grade}</span>
          </div>
          <div class="doc-meta-item">
            <span class="doc-meta-label">Сэдэв</span>
            <span class="doc-meta-value">${h.topic}</span>
          </div>
          <div class="doc-meta-item">
            <span class="doc-meta-label">Хугацаа</span>
            <span class="doc-meta-value">${h.period}</span>
          </div>
        </div>
      </div>

      <!-- 1. СУРАЛЦАХУЙН ЗОРИЛТ -->
      <div class="plan-section">
        <div class="section-header">
          <div class="section-num red">1</div>
          <div class="section-title">Суралцахуйн зорилт</div>
        </div>
        <div class="section-body">
          <div class="bloom-grid">
            <div class="bloom-card a">
              <div class="bloom-label">А — Мэдлэг</div>
              <div class="bloom-name">Мэдэх (Know)</div>
              <div class="bloom-text">${o.A}</div>
            </div>
            <div class="bloom-card b">
              <div class="bloom-label">Б — Чадвар</div>
              <div class="bloom-name">Ойлгох (Understand)</div>
              <div class="bloom-text">${o.B}</div>
            </div>
            <div class="bloom-card c">
              <div class="bloom-label">В — Хэрэглэгч</div>
              <div class="bloom-name">Хэрэглэх (Apply)</div>
              <div class="bloom-text">${o.C}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 2. ХИЧЭЭЛИЙН БЭЛТГЭЛ БА ДИЗАЙН -->
      <div class="plan-section">
        <div class="section-header">
          <div class="section-num blue">2</div>
          <div class="section-title">Хичээлийн бэлтгэл ба дизайн</div>
        </div>
        <div class="section-body">
          <div class="design-grid">
            <div class="design-item">
              <div class="design-item-label">Арга зүй</div>
              <div class="design-item-text">${d.method}</div>
            </div>
            <div class="design-item">
              <div class="design-item-label">Хэрэглэгдэхүүн & Цахим</div>
              <div class="design-item-text">${d.tools}</div>
            </div>
            <div class="design-item">
              <div class="design-item-label">Ангийн зохион байгуулалт</div>
              <div class="design-item-text">${d.engagement}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. ҮЙЛ АЖИЛЛАГААНЫ УРСГАЛ -->
      <div class="plan-section">
        <div class="section-header">
          <div class="section-num green">3</div>
          <div class="section-title">Хичээлийн үйл ажиллагааны урсгал</div>
        </div>
        <div class="section-body" style="padding:0;">
          <table class="stages-table">
            <thead>
              <tr>
                <th style="width:120px;">Үе шат</th>
                <th>Зорилго</th>
                <th>Багшийн үйл ажиллагаа</th>
                <th>Сурагчийн үйл ажиллагаа</th>
                <th style="width:130px;">Үнэлгээ / Хэрэгсэл</th>
              </tr>
            </thead>
            <tbody>
              ${stages.map(s => `
              <tr>
                <td>
                  <div class="stage-name">${s.name}</div>
                  <div class="stage-time">${s.time} мин</div>
                </td>
                <td>${s.purpose}</td>
                <td>${s.teacher_actions.replace(/\n/g, '<br>')}</td>
                <td>${s.student_actions.replace(/\n/g, '<br>')}</td>
                <td>${s.assessment}</td>
              </tr>`).join('')}
            </tbody>
          </table>
        </div>
      </div>

      <!-- 4. ЯЛГАВАРТАЙ ХАНДЛАГА -->
      <div class="plan-section">
        <div class="section-header">
          <div class="section-num orange">4</div>
          <div class="section-title">Хичээлээс гадуур үйл ажиллагаа</div>
        </div>
        <div class="section-body">
          <div class="diff-grid">
            <div class="diff-card">
              <div class="diff-icon">🎯</div>
              <div class="diff-label">Гэрийн даалгавар (бүтээлч)</div>
              <div class="diff-text">${plan.homework}</div>
            </div>
            <div class="diff-card">
              <div class="diff-icon">📊</div>
              <div class="diff-label">Ялгавартай хандлага</div>
              <div class="diff-text">
                <strong style="color:#66bb6a;font-size:11px;">Дэмжлэг хэрэгтэй:</strong><br>
                ${diff.support}<br><br>
                <strong style="color:#ffa726;font-size:11px;">Дэвшилтэт сурагчид:</strong><br>
                ${diff.advanced}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div style="text-align:center;padding-top:16px;font-size:11px;color:#556080;">
        БагшAI — Монгол ЕБС-ийн хичээлийн хөтөлбөр боловсруулагч &nbsp;|&nbsp; bagsh.ai
      </div>
    </div>
  `;

  document.getElementById('planContent').innerHTML = html;
}

function printPlan() {
  window.print();
}

function copyPlan() {
  const content = document.getElementById('planContent');
  const text = content ? content.innerText : '';
  navigator.clipboard.writeText(text).then(() => {
    const btn = event.target;
    const orig = btn.textContent;
    btn.textContent = '✅ Хуулагдлаа!';
    setTimeout(() => btn.textContent = orig, 2000);
  });
}

function resetOutput() {
  showState('empty');
  document.getElementById('planContent').innerHTML = '';
}
