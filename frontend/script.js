const API_URL = 'http://127.0.0.1:8000/deviant-forecast';
let barChart, radarChart;
const $ = (s)=>document.querySelector(s);
function clamp(n,min,max){return Math.max(min,Math.min(max,n));}
function level(score){ if(score < 30) return ['Низкий','#18b86b','Риск цифровой девиации низкий.']; if(score < 70) return ['Средний','#ff9800','Наблюдается умеренный уровень риска.']; return ['Высокий','#ef4444','Повышенный риск цифровой девиации. Рекомендуется обратить внимание на цифровые привычки.']; }
function formToPayload(){
  const f = new FormData($('#surveyForm'));
  const online = Number(f.get('onlineHours'));
  const social = Number(f.get('social'));
  const stress = Number(f.get('stress'));
  const addiction = Number(f.get('addiction'));
  const socialShare = Number(f.get('socialShare'));
  return [{
    internet_usage_pct: clamp(45 + online*5, 0, 100),
    social_media_usage_pct: social,
    avg_time_online_hours: online,
    social_media_time_share_pct: socialShare,
    internet_users_percent: clamp(45 + online*5, 0, 100),
    daily_internet_users: clamp(35 + online*6, 0, 100),
    internet_addiction_index: addiction,
    stress_from_devices: stress,
    youth_online_activity: clamp((social + addiction + stress)/3, 0, 100),
    avg_screen_time_hours: clamp(online + 0.8, 0, 16)
  }];
}
function localScore(p){
  const x=p[0];
  return clamp(0.16*x.social_media_usage_pct + 0.18*x.internet_addiction_index + 0.16*x.stress_from_devices + 3.2*x.avg_screen_time_hours + 0.12*x.youth_online_activity - 22, 0, 100);
}
async function predict(payload){
  try{
    const r = await fetch(API_URL,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    if(!r.ok) throw new Error('api');
    const data = await r.json();
    return Number(data[0].result);
  }catch(e){ return localScore(payload); }
}
function render(score,payload){
  const [lvl,color,desc] = level(score);
  $('#results').classList.remove('hidden');
  $('#score').textContent = Math.round(score);
  $('#level').textContent = lvl + ' уровень';
  $('#level').style.color = color;
  $('#desc').textContent = desc;
  $('#person').textContent = `Возраст: ${$('#age').value} лет • Пол: ${$('#gender').value || 'не указан'}`;
  $('.scoreCircle').style.background = `conic-gradient(${color} ${score*3.6}deg,#eef0fb 0deg)`;
  const x = payload[0];
  const values = [x.internet_addiction_index, x.social_media_usage_pct, x.stress_from_devices, x.youth_online_activity].map(v=>Math.round(v/10));
  const labels = ['Зависимость','Соцсети','Стресс','Активность'];
  if(barChart) barChart.destroy(); if(radarChart) radarChart.destroy();
  barChart = new Chart($('#barChart'),{type:'bar',data:{labels,datasets:[{label:'Баллы',data:values,backgroundColor:['#7b61ff','#ff6b35','#22c55e','#f59e0b'],borderRadius:8}]},options:{scales:{y:{min:0,max:10}}}});
  radarChart = new Chart($('#radarChart'),{type:'radar',data:{labels,datasets:[{label:'Профиль',data:values,borderColor:'#6157f5',backgroundColor:'rgba(97,87,245,.15)',pointBackgroundColor:'#6157f5'}]},options:{scales:{r:{min:0,max:10}}}});
  location.hash='results';
}
$('#surveyForm').addEventListener('submit',async e=>{e.preventDefault(); const p=formToPayload(); render(await predict(p),p);});
function setScenario(type){
  const map={low:[1.5,25,15,15,20],mid:[3.5,48,38,42,35],high:[9,92,88,90,85]}[type];
  $('[name=onlineHours]').value=map[0]; $('[name=social]').value=map[1]; $('[name=stress]').value=map[2]; $('[name=addiction]').value=map[3]; $('[name=socialShare]').value=map[4];
  $('#gender').value = $('#gender').value || 'Мужской'; $('#age').value = $('#age').value || 17;
  $('#surveyForm').dispatchEvent(new Event('submit'));
}
$('#demoLow').onclick=()=>setScenario('low'); $('#demoMid').onclick=()=>setScenario('mid'); $('#demoHigh').onclick=()=>setScenario('high');
$('#themeBtn').onclick=()=>document.body.classList.toggle('dark');
