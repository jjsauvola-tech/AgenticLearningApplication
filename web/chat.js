'use strict';
Object.assign(words.fi, {
  expandChat:'Suurenna keskustelu', shrinkChat:'Palauta sivupaneeli', chatWidth:'Leveys',
  copyAnswer:'Kopioi leikepöydälle', saveAnswer:'Tallenna muistiinpanoihin',
  readAnswer:'Lue koko vastaus', answerSaved:'Vastaus tallennettu muistiinpanoihin',
  copyFailed:'Kopiointi ei onnistunut. Avaa koko vastaus ja kopioi valittu teksti.',
  assistantNote:'Avustajan vastaus'
});
Object.assign(words.en, {
  expandChat:'Expand conversation', shrinkChat:'Restore side panel', chatWidth:'Width',
  copyAnswer:'Copy to clipboard', saveAnswer:'Save to notes', readAnswer:'Read full answer',
  answerSaved:'Answer saved to notes', copyFailed:'Copy failed. Open the full answer and copy the selected text.',
  assistantNote:'Assistant answer'
});

function bindChatSize() {
  const panel=$('.panel.assistant');
  if (!panel) return;
  $('#expandChat').onclick=()=>{
    const expanded=panel.classList.toggle('chat-expanded');
    $('#expandChat').textContent=t(expanded?'shrinkChat':'expandChat');
    $('#expandChat').setAttribute('aria-expanded',String(expanded));
  };
  $('#chatWidth').oninput=e=>document.documentElement.style.setProperty('--assistant',e.target.value+'px');
}
document.addEventListener('keydown',event=>{
  if(event.key==='Escape'&&!$('#modal-root').children.length&&$('.chat-expanded')) $('#expandChat').click();
});

function answerText(message) {
  const sources=(message.sources||[]).map((s,i)=>`[${i+1}] ${s.name} · ${s.page}`);
  return message.body+(sources.length?'\n\n'+t('sources')+'\n'+sources.join('\n'):'');
}

async function copyAnswer(message) {
  const text=answerText(message);
  try {
    try { await navigator.clipboard.writeText(text); }
    catch {
      const previous=document.activeElement;
      const input=document.createElement('textarea');input.value=text;
      input.style.cssText='position:fixed;left:-9999px;top:0';document.body.append(input);input.select();
      let copied=false;
      try {copied=document.execCommand('copy');} finally {input.remove();previous?.focus();}
      if(!copied) throw Error('copyFailed');
    }
    toast(t('copied'));
  } catch {toast(t('copyFailed'),true);}
}

async function saveAnswer(message, button, vault) {
  button.disabled=true;
  const anchor=message.document_id?message:(message.sources||[])[0];
  try {
    await api('/api/notes',{
      title:t(message.role==='external'?'externalRole':'assistantNote')+' · '+new Date(message.created).toLocaleString(S.settings.language),
      body:answerText(message), document_id:anchor?.document_id||null,page:anchor?.page||null
    },{headers:{'X-ALA-Vault':vault}});
    if(S.active===vault) S.notes=await api('/api/notes');
    toast(t('answerSaved'));
  } catch(e) {fail(e);}
  finally {button.disabled=false;}
}

function answerActions(message, vault, includeRead=true) {
  const actions=document.createElement('div');actions.className='answer-actions';
  const add=(label,handler)=>{
    const b=document.createElement('button');b.type='button';b.className='small';b.textContent=t(label);
    b.onclick=()=>handler(b);actions.append(b);
  };
  add('copyAnswer',()=>copyAnswer(message));
  add('saveAnswer',button=>saveAnswer(message,button,vault));
  if(includeRead) add('readAnswer',()=>{
    modal(t('answer'),'<div id="fullAnswerActions"></div><div id="fullAnswerText" class="full-answer-text" tabindex="0"></div>',()=>{
      $('.dialog').classList.add('answer-dialog');
      $('#fullAnswerText').textContent=answerText(message);
      $('#fullAnswerActions').append(answerActions(message,vault,false));
    },true);
  });
  return actions;
}

function renderMessages() {
  const el=$('#messages');if(!el)return;el.replaceChildren();
  const vault=S.active;
  const did=S.chatAll?null:S.doc?.id||null;
  const page=S.chatAll?null:S.doc?S.page:null;
  const messages=S.messages.filter(m=>m.document_id===did&&m.page===page).reverse();
  if(!messages.length){const p=document.createElement('p');p.className='empty-mini';p.textContent=t('noMessages');el.append(p);}
  for(const message of messages){
    const box=document.createElement('div');box.className='bubble '+message.role;
    const role=document.createElement('span');role.className='role';
    role.textContent=t(message.role==='user'?'you':message.role==='external'?'externalRole':'ai');
    const body=document.createElement('div');body.className='message-body';body.textContent=message.body;
    box.append(role);
    if(message.role!=='user') box.append(answerActions(message,vault));
    box.append(body);
    const links=document.createElement('div');links.className='answer-sources';
    for(const [i,source] of (message.sources||[]).entries()){
      const b=document.createElement('button');b.className='small';b.textContent=`[${i+1}] ${source.name} · ${source.page}`;
      b.onclick=()=>{S.view='lecture';openDoc(source.document_id,source.page);};links.append(b);
    }
    box.append(links);el.append(box);
  }
  el.scrollTop=el.scrollHeight;
}
Object.assign(words.fi,{showSlide:'Näytä kalvo',showSlideText:'Näytä teksti',slideLoading:'Kalvoa valmistellaan…',slide_preview_unavailable:'Kalvon esikatselu ei onnistunut. Se tarvitsee Windowsin ja asennetun PowerPointin. Voit käyttää tekstinäkymää tai ladata alkuperäisen.'});
Object.assign(words.en,{showSlide:'Show slide',showSlideText:'Show text',slideLoading:'Preparing slide…',slide_preview_unavailable:'Slide preview requires Windows and installed PowerPoint. Use the text view or download the original if preview fails.'});
let slideTextMode=false;
function renderReader(){
  if(S.doc.format!=='pptx'){renderTextReader();return;}
  const el=$('#reader');
  el.replaceChildren();
  const controls=document.createElement('div');controls.className='buttons slide-controls';
  for(const [label,textMode] of [['showSlide',false],['showSlideText',true]]){
    const button=document.createElement('button');button.textContent=t(label);
    button.className=slideTextMode===textMode?'primary':'';
    button.setAttribute('aria-pressed',String(slideTextMode===textMode));
    button.onclick=()=>{slideTextMode=textMode;renderReader();};controls.append(button);
  }
  if(slideTextMode){renderTextReader();el.prepend(controls);return;}
  el.append(controls);
  const status=document.createElement('p');status.className='notice';status.setAttribute('role','status');status.textContent=t('slideLoading');el.append(status);
  const image=document.createElement('img');image.className='slide-preview';image.alt=t('slide')+' '+S.page+' — '+cur().title;
  image.onload=()=>status.remove();image.onerror=()=>{image.remove();status.textContent=t('slide_preview_unavailable');};
  image.src='/api/preview/'+S.doc.id+'/'+S.page+'?vault='+S.active;el.append(image);
  if(S.settings.showNotes&&cur().notes){const detail=document.createElement('details');const label=document.createElement('summary');label.textContent=t('speakerNotes');const body=document.createElement('div');body.className='quote';body.textContent=cur().notes;detail.append(label,body);el.append(detail);}
}
