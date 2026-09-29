'use strict';
function projectLearningModules(documents){
 const groups=new Map();
 for(const doc of documents){const key=doc.course||'Omat materiaalit';if(!groups.has(key))groups.set(key,{key,title:key.split(' / ').at(-1).replace(/_/g,' '),documents:[],count:0,completed:0});const item=groups.get(key);item.documents.push(doc);item.count+=Math.max(0,Number(doc.count)||0);item.completed+=Math.min(Math.max(0,Number(doc.completed)||0),Math.max(0,Number(doc.count)||0));}
 return [...groups.values()].map(m=>({...m,percent:m.count?Math.round(m.completed/m.count*100):0}));
}
if(typeof module!=='undefined'&&module.exports){module.exports={projectLearningModules};}
else (()=>{
 const enabled=new URLSearchParams(location.search).get('ux')==='agents';
 if(!enabled)return;
 const labels={fi:{path:'Oppimismatka',progress:'Omat opiskelumerkinnät · eivät osaamisarvio',team:'Oppimisen agentit',tutor:'AI-tutor',ready:'Valmis pohtimaan kanssasi',thinking:'Käsittelen pyyntöäsi',fixing:'Pyyntö ei onnistunut — kokeillaan uudelleen',files:'Aineistoluettelo',preview:'UX-kokeilu',motion:'Animaatiot',back:'Perusnäkymä',reading:'Tutki aineistoa ja tee oma havainto.',reflect:'Palaa omaan ajatukseesi: mikä muuttui?',practice:'Kokeile ensin omin sanoin. Palaute auttaa seuraavassa yrityksessä.',role:'Aktiivinen moduuli',marked:'merkitty opiskelluksi',scope:'Agentit ovat käyttöliittymän rooleja, eivät erillisiä taustalla työskenteleviä malleja.'},en:{path:'Learning journey',progress:'Your study marks · not a mastery assessment',team:'Learning agents',tutor:'AI tutor',ready:'Ready to think with you',thinking:'Processing your request',fixing:'The request failed — let’s try again',files:'Material list',preview:'UX experiment',motion:'Animations',back:'Classic view',reading:'Explore the material and make your own observation.',reflect:'Revisit your idea: what changed?',practice:'Try in your own words first. Feedback supports your next attempt.',role:'Active module',marked:'marked studied',scope:'Agents are interface roles, not separate models working in the background.'}};
 const label=k=>(labels[S.settings.language]||labels.fi)[k];
 const palette=['#277a69','#7164ad','#a76532','#397b9b','#9a5778'];
 const color=key=>palette[[...key].reduce((n,c)=>n+c.codePointAt(0),0)%palette.length];
 let motion=true;try{motion=localStorage.getItem('ala.agentMotion')!=='off';}catch{}
 const jobs=new Map(),failures=new Set();let layoutObserver=null;
 function face(mood='neutral',accent='#277a69',live=false){return `<span class="learning-face ${live?'is-live':''}" style="--agent-color:${accent}" aria-hidden="true"><img class="learning-base" src="/assets/svla-faces/base.png" alt=""><img class="learning-expression" src="/assets/svla-faces/expr/${mood}.png" alt=""></span>`;}
 function tutorState(){return [...jobs.values()].includes(S.active)?'thinking':failures.has(S.active)?'fixing':'ready';}
 function activeModule(modules){return modules.find(m=>m.documents.some(d=>d.id===S.doc?.id));}
 window.learningAgentFlow=()=>{
  const modules=projectLearningModules(S.documents),current=activeModule(modules);
  return `<aside class="panel flow agent-flow" aria-label="${label('path')}"><div class="eyebrow">${label('path')}</div><h2>${current?h(current.title):label('team')}</h2><p class="agent-meta">${label('progress')}</p><ol class="learning-route">${modules.map((m,i)=>`<li class="${m===current?'is-current':''}"><button data-doc="${h(m.documents[0].id)}" ${m===current?'aria-current="step"':''} aria-label="${h(m.title)}: ${m.completed}/${m.count} ${label('marked')}"><span class="learning-orbit" style="--progress:${m.percent}%;--agent-color:${color(m.key)}">${face(m.completed===m.count&&m.count?'success':m===current?'reading':'neutral',color(m.key))}</span><span><strong>${h(m.title)}</strong><small>${m.completed} / ${m.count} · ${m.percent}%</small></span></button></li>`).join('')}</ol><details class="agent-materials"><summary>${label('files')}</summary>${legacyFlow()}</details></aside>`;
 };
 function updateStatus(){
  const target=$('#agentTutorStatus');if(!target)return;
  const state=tutorState();target.textContent=label(state);
  const avatar=$('#agentTutorFace');avatar.innerHTML=face(state==='ready'?'questioning':state,'#277a69',state==='thinking');
 }
 function applyMotion(){document.body.classList.toggle('agents-still',!motion||!!S.settings.reduceMotion||document.hidden);}
 window.beginLearningAgentActivity=vault=>{const key={};jobs.set(key,vault);failures.delete(vault);updateStatus();return failed=>{jobs.delete(key);if(failed)failures.add(vault);else failures.delete(vault);updateStatus();};};
 window.mountLearningAgents=()=>{
  layoutObserver?.disconnect();
  document.body.classList.add('agent-mode');applyMotion();
  $('#learningAgents')?.remove();
  const modules=projectLearningModules(S.documents),current=activeModule(modules);
  const dock=document.createElement('section');dock.id='learningAgents';dock.className='agent-dock';dock.setAttribute('aria-label',label('team'));
  dock.innerHTML=`<div class="agent-tutor"><span id="agentTutorFace"></span><div><strong>${label('tutor')}</strong><span id="agentTutorStatus" role="status" aria-live="polite"></span></div></div><div class="agent-module-strip" aria-label="${label('team')}">${modules.map(m=>`<button class="agent-chip ${m===current?'is-current':''}" data-module-doc="${h(m.documents[0].id)}" title="${h(m.title)}" aria-label="${h(m.title)}" ${m===current?'aria-current="true"':''}>${face(m===current?'reading':'neutral',color(m.key))}<span>${h(m.title)}</span></button>`).join('')}</div><div class="agent-controls"><span>${label('preview')}</span><button id="agentMotion" class="small" aria-pressed="${motion}">${label('motion')}</button><a class="button small" href="/">${label('back')}</a></div>`;
  $('.workspace-bar').after(dock);
  const selected=dock.querySelector('.agent-chip.is-current'),strip=dock.querySelector('.agent-module-strip');
  if(selected)strip.scrollLeft=Math.max(0,selected.offsetLeft-strip.offsetLeft-strip.clientWidth/2+selected.offsetWidth/2);
  const updateLayout=()=>{const header=$('.topbar'),top=getComputedStyle(header).position==='static'?0:header.getBoundingClientRect().height;document.body.style.setProperty('--agent-dock-top',top+'px');document.body.style.setProperty('--agent-panels-top',(top+dock.getBoundingClientRect().height)+'px');};
  if(typeof ResizeObserver==='function'){layoutObserver=new ResizeObserver(updateLayout);layoutObserver.observe($('.topbar'));layoutObserver.observe(dock);}updateLayout();
  dock.querySelectorAll('[data-module-doc]').forEach(b=>b.onclick=()=>{S.view='lecture';openDoc(b.dataset.moduleDoc);});
  $('#agentMotion').onclick=()=>{motion=!motion;try{localStorage.setItem('ala.agentMotion',motion?'on':'off');}catch{}applyMotion();$('#agentMotion').setAttribute('aria-pressed',String(motion));};
  updateStatus();
  const host=$('.reader-shell')||$('main.wide');
  if(host){const prompt=document.createElement('div');prompt.className='agent-guidance';prompt.innerHTML=`${face(S.view==='verification'?'questioning':S.view==='teacher'?'thinking':'reading',current?color(current.key):'#277a69')}<div><strong>${current?h(current.title):label('tutor')}</strong><p>${label(S.view==='verification'?'practice':S.view==='teacher'?'reflect':'reading')}</p><small>${label('scope')}</small></div>`;host.prepend(prompt);}
 };
 document.addEventListener('visibilitychange',applyMotion);
})();
