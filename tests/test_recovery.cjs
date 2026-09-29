const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');const fs=require('node:fs');
function setup(){
 const elements=new Map(),listeners={},stored=new Map();
 const ctx={console,AbortController,URL,Set,Map,Date,Promise,Error,TypeError,
  location:{hash:'#test',pathname:'/'},history:{replaceState(){}},sessionStorage:{getItem:k=>stored.get(k),setItem:(k,v)=>stored.set(k,v)},
  matchMedia:()=>({matches:false,addEventListener(){}}),setInterval(){return 1},clearInterval(){},setTimeout,clearTimeout,
  window:{addEventListener(){},scrollTo(){}},navigator:{},
  document:{querySelector:s=>elements.get(s)||null,addEventListener:(n,fn)=>{listeners[n]=fn},createElement:()=>({append(){},replaceChildren(){},setAttribute(){}}),body:{prepend(){},classList:{toggle(){}}}},
  fetch:async()=>({ok:true,json:async()=>({})})};
 vm.createContext(ctx);
 for(const file of ['app.js','goals.js','imports.js','chat.js','recovery.js'])vm.runInContext(fs.readFileSync('web/'+file,'utf8'),ctx,{filename:file});
 return {ctx,elements,listeners,run:code=>vm.runInContext(code,ctx)};
}
test('all production scripts load in order without early dependency errors',()=>{
 const {listeners}=setup();assert.equal(typeof listeners.DOMContentLoaded,'function');
});
test('optional history failure does not prevent material load',async()=>{
 const {ctx,run}=setup();ctx.api=async path=>{
 if(path==='/api/state')return {active:'a',settings:{language:'fi'},vaults:[]};
 if(path==='/api/documents')return [{id:'doc'}];if(path==='/api/document/doc')return {id:'doc'};
 if(path==='/api/messages')throw Error('history failure');return [];
 };let rendered=false;ctx.render=()=>rendered=true;ctx.applyAppearance=()=>{};ctx.showConnectionStatus=()=>{};
 await ctx.load();assert.equal(rendered,true);assert.equal(run('S.doc.id'),'doc');assert.equal(run('S.loadFailures.join()'),'messages');
});
test('out-of-order document responses cannot replace the latest selection',async()=>{
 const {ctx,run}=setup();run("S.active='a'");const requests={};ctx.api=path=>new Promise(resolve=>requests[path]=resolve);ctx.render=()=>{};
 const first=ctx.openDoc('first'),second=ctx.openDoc('second');requests['/api/document/second']({id:'second'});await second;
 requests['/api/document/first']({id:'first'});await first;assert.equal(run('S.doc.id'),'second');
});
test('chat drafts survive rerender and remain separate by scope',()=>{
 const {ctx,elements,run}=setup();const input={dataset:{},value:''};elements.set('#chatInput',input);elements.set('#sendChat',{});
 run("S.active='a';S.doc={id:'doc'};S.page=1");ctx.restoreChatDraft();input.value='draft one';ctx.captureChatDraft();
 run('S.page=2');ctx.restoreChatDraft();assert.equal(input.value,'');input.value='draft two';ctx.captureChatDraft();
 run('S.page=1');ctx.restoreChatDraft();assert.equal(input.value,'draft one');
});
test('failed boot preserves an already mounted workspace',async()=>{
 const {ctx,elements}=setup();elements.set('#vaultSelect',{});ctx.api=async()=>{throw Error('connection_lost')};let error;ctx.showConnectionStatus=e=>error=e;
 await ctx.boot();assert.equal(error.message,'connection_lost');
});
test('requests have an actual abort deadline and no automatic write retry',async()=>{
 const {ctx}=setup();let count=0;
 ctx.fetch=(_url,options)=>{count++;return new Promise((resolve,reject)=>options.signal.addEventListener('abort',()=>reject(Object.assign(Error(),{name:'AbortError'}))));};
 await assert.rejects(ctx.api('/api/notes',{body:'test'},{timeout:10}),/request_timeout/);assert.equal(count,1);
});
test('a late workspace load cannot overwrite a newer vault and document',async()=>{
 const {ctx,run}=setup();let stateCall=0,releaseFirst,firstStarted;
 const waiting=new Promise(resolve=>firstStarted=resolve);
 ctx.api=async(path,body,opts)=>{
  if(path==='/api/state')return {active:++stateCall===1?'a':'b',settings:{language:'fi'},vaults:[]};
  if(path==='/api/documents')return [{id:opts.headers['X-ALA-Vault']}];
  if(path==='/api/document/a'){firstStarted();return new Promise(resolve=>releaseFirst=resolve);}
  if(path==='/api/document/b')return {id:'b'};
  return [];
 };
 ctx.render=()=>{};ctx.applyAppearance=()=>{};ctx.showConnectionStatus=()=>{};
 const first=ctx.load();await waiting;await ctx.load();releaseFirst({id:'a'});await first;
 assert.equal(run('S.active'),'b');assert.equal(run('S.doc.id'),'b');
});
