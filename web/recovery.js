'use strict';
Object.assign(words.fi,{
 connection_lost:'Yhteys paikalliseen palvelimeen katkesi. Luonnos säilyy. Käynnistä tarvittaessa Start-ALA.cmd.',
 request_timeout:'Toiminto ylitti aikarajan. Tallennus on saattanut valmistua; tarkista tilanne ennen uudelleenyritystä.',
 server_busy:'Palvelin käsittelee muita töitä. Yritä hetken kuluttua uudelleen.',
 retryLoad:'Yritä latausta uudelleen',partialLoad:'Osa tiedoista ei latautunut. Aineisto on edelleen käytettävissä.',
 startupFailed:'Työtilaa ei saatu avattua. Tietoja ei poistettu.',technicalError:'Käyttöliittymässä tapahtui virhe. Voit yrittää latausta uudelleen.'
});
Object.assign(words.en,{
 connection_lost:'Connection to the local server was lost. Your draft is retained. Launch Start-ALA.cmd if needed.',
 request_timeout:'The operation timed out. A write may have completed; check before retrying.',
 server_busy:'The server is processing other work. Try again shortly.',
 retryLoad:'Retry loading',partialLoad:'Some information could not be loaded. Materials remain available.',
 startupFailed:'The workspace could not be opened. No data was deleted.',technicalError:'An interface error occurred. You can retry loading.'
});
let connectionLost=false,booting=false,recoveryError=null;
const pendingChats=new Set();
let chatDrafts={};
try{chatDrafts=JSON.parse(sessionStorage.getItem('alaDrafts')||'{}');}catch{}
function persistChatDrafts(){try{sessionStorage.setItem('alaDrafts',JSON.stringify(chatDrafts));}catch{}}
function captureChatDraft(){const input=$('#chatInput');if(input?.dataset.draftKey){chatDrafts[input.dataset.draftKey]=input.value;persistChatDrafts();}}
function restoreChatDraft(){
 const input=$('#chatInput');if(!input)return;
 const key=[S.active,S.chatAll?'all':S.doc?.id||'none',S.chatAll?'':S.page].join(':');
 input.dataset.draftKey=key;input.value=chatDrafts[key]||'';input.oninput=captureChatDraft;
 $('#sendChat').disabled=pendingChats.has(key);
}
function showConnectionStatus(error){
 if(error)recoveryError=error;error=recoveryError;
 let banner=$('#recoveryStatus');
 if(!banner){banner=document.createElement('div');banner.id='recoveryStatus';banner.className='notice recovery-status';banner.setAttribute('role','status');document.body.prepend(banner);}
 banner.replaceChildren();
 const message=error?t(error.message):connectionLost?t('connection_lost'):S.loadFailures?.length?t('partialLoad'):'';
 banner.hidden=!message;if(!message)return;
 const text=document.createElement('span');text.textContent=message+(error?.eventId?' ('+error.eventId+')':'');banner.append(text);
 const retry=document.createElement('button');retry.textContent=t('retryLoad');retry.onclick=boot;banner.append(retry);
}
async function boot(){
 if(booting)return;booting=true;
 try{const session=await api('/api/bootstrap');if(session.sessionToken){token=session.sessionToken;sessionStorage.setItem('alaToken',token);}await load();connectionLost=false;recoveryError=null;showConnectionStatus();}
 catch(e){
  if(!$('#vaultSelect')){
   const main=document.createElement('main');main.className='empty';const title=document.createElement('h1');title.textContent='ALA';
   const description=document.createElement('p');description.textContent=t('startupFailed');main.append(title,description);$('#app').replaceChildren(main);
  }
  showConnectionStatus(e);
 }finally{booting=false;}
}
window.addEventListener('error',event=>{showConnectionStatus(Error('technicalError'));api('/api/client-error',{file:(event.filename||'').split('/').pop(),line:event.lineno||0}).catch(()=>{});});
window.addEventListener('unhandledrejection',()=>{showConnectionStatus(Error('technicalError'));api('/api/client-error',{}).catch(()=>{});});
window.addEventListener('beforeunload',captureChatDraft);
