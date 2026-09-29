'use strict';
let aiState={state:'checking'},aiCheckAt=0,aiChecking=false,aiPoll=null;
const aiWords={fi:{checking:'Tarkistan AI-yhteyttä…',offline:'Paikallinen AI ei ole käynnissä.',available:'Malli on asennettu. Käynnistä AI ladataksesi sen.',ready:'AI on valmis',starting:'Käynnistän palvelua ja lataan mallia…',choose_model:'Valitse asennettu keskustelumalli AI-asetuksista.',not_installed:'Ollamaa ei löytynyt tältä koneelta. Asenna se tai määritä AI-palvelu asetuksissa.',endpoint_unreachable:'Asetettu AI-palvelu ei vastaa. Tarkista sen osoite.',start_failed:'AI ei käynnistynyt. Voit yrittää uudelleen tai tarkistaa asetukset.',disconnected:'ALA-yhteys katkesi. Luonnos säilyy. Käynnistä ALA työpöytäkuvakkeesta ja yhdistä uudelleen.',start:'Käynnistä AI',reconnect:'Yhdistä uudelleen',settings:'AI-asetukset',local:'Paikallinen AI'},en:{checking:'Checking AI connection…',offline:'Local AI is not running.',available:'Model installed. Start AI to load it.',ready:'AI is ready',starting:'Starting service and loading model…',choose_model:'Choose an installed chat model in AI settings.',not_installed:'Ollama was not found. Install it or configure an AI service.',endpoint_unreachable:'The configured AI service is not responding.',start_failed:'AI did not start. Retry or check settings.',disconnected:'ALA is disconnected. Your draft is retained. Launch the ALA desktop shortcut and reconnect.',start:'Start AI',reconnect:'Reconnect',settings:'AI settings',local:'Local AI'}};
function paintAI(){
 const host=$('#aiRuntime');if(!host)return;const w=aiWords[S.settings.language]||aiWords.fi;
 host.innerHTML=`<span role="status" aria-live="polite">${w.local}${aiState.model?' · '+h(aiState.model):''}: ${h(w[aiState.state]||w.offline)}</span><button id="startAI" ${aiState.state==='starting'?'disabled':''}>${aiState.state==='disconnected'?w.reconnect:w.start}</button><button id="aiSettings">${w.settings}</button>`;
 $('#aiSettings').onclick=()=>settings('model');$('#startAI').onclick=startAI;
}
async function checkAI(){
 if(aiChecking)return;aiChecking=true;aiCheckAt=Date.now();
 try{aiState=await api('/api/ai/status',undefined,{timeout:10000});}
 catch{aiState={state:'disconnected'};}
 finally{aiChecking=false;paintAI();}
 clearTimeout(aiPoll);if(aiState.state==='starting')aiPoll=setTimeout(checkAI,2000);
}
async function startAI(){
 if(aiState.state==='disconnected'){await boot();await checkAI();return;}
 if(aiState.state==='choose_model'||aiState.state==='not_installed'){settings('model');return;}
 aiState={...aiState,state:'starting'};paintAI();
 try{await api('/api/ai/start',{});await checkAI();}
 catch{aiState={state:'disconnected'};paintAI();}
}
function mountAIRuntime(){
 $('#aiRuntime')?.remove();const host=document.createElement('div');host.id='aiRuntime';host.className='ai-runtime';
 const dock=$('#learningAgents');if(dock)dock.append(host);else $('.workspace-bar').after(host);
 paintAI();if(Date.now()-aiCheckAt>15000)checkAI();
}
function showAIProblem(error){
 if(!['model_unavailable','model_not_configured','request_timeout','connection_lost'].includes(error.message))return false;
 aiState={...aiState,state:error.message==='connection_lost'?'disconnected':error.message==='model_not_configured'?'choose_model':'offline'};paintAI();
 if(error.message==='connection_lost')showConnectionStatus(error);
 return true;
}
