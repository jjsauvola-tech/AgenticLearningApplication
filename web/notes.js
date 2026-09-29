'use strict';
let activeNoteDraft=null;
function writeNoteDraft(){
 if(!activeNoteDraft||!$('#noteBody'))return;
 activeNoteDraft.value.title=$('#noteTitle').value;activeNoteDraft.value.body=$('#noteBody').value;
 try{localStorage.setItem(activeNoteDraft.key,JSON.stringify(activeNoteDraft.value));}catch{}
}
function noteDialog(note){
 const vault=S.active,did=note?note.document_id:S.doc?.id||null,page=note?note.page:S.doc?S.page:null;
 const key=['ala.noteDraft',vault,note?.id||'new',did||'',page||''].join(':');
 let value={id:note?.id||crypto.randomUUID(),document_id:did,page,title:note?.title||cur()?.title||'',body:note?.body||''};
 try{const saved=JSON.parse(localStorage.getItem(key)||'null');if(saved&&saved.document_id===did&&saved.page===page&&typeof saved.body==='string')value={...value,id:saved.id||value.id,title:saved.title||'',body:saved.body};}catch{}
 activeNoteDraft={key,value};
 modal(note?t('note'):t('newNote'),`<p class="meta">${h(contextLabel())}</p><form id="noteForm" class="stack"><label>${t('title')}<input id="noteTitle" maxlength="200"></label><label>${t('body')}<textarea class="note-body" id="noteBody"></textarea></label><p id="noteSaveStatus" class="note-error" role="status"></p><button class="primary" id="saveNote">${t('save')}</button></form>`,()=>{
  $('#noteTitle').value=value.title;$('#noteBody').value=value.body;
  $('#noteTitle').oninput=writeNoteDraft;$('#noteBody').oninput=writeNoteDraft;
  $('#closeModal').onclick=()=>{writeNoteDraft();activeNoteDraft=null;closeModal();};
  $('#noteForm').onsubmit=async event=>{
   event.preventDefault();writeNoteDraft();const button=$('#saveNote'),status=$('#noteSaveStatus');button.disabled=true;
   const body={...value};
   try{
    await api('/api/notes',body,{headers:{'X-ALA-Vault':vault}});
    try{localStorage.removeItem(key);}catch{}
    activeNoteDraft=null;closeModal();
    if(S.active===vault){try{S.notes=await api('/api/notes',undefined,{headers:{'X-ALA-Vault':vault}});}catch{}render();}
    toast(t('saved'));
   }catch(error){status.textContent=(S.settings.language==='fi'?'Tallennus ei varmistunut. Luonnos on tässä selaimessa tallessa. Yhdistä uudelleen ja paina Tallenna.':'Save was not confirmed. The draft is retained in this browser. Reconnect and save again.');showConnectionStatus(error);}
   finally{button.disabled=false;}
  };$('#noteBody').focus();
 });
}
window.addEventListener('beforeunload',writeNoteDraft);
