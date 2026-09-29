const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
function setup(){
 const calls=[],ctx={words:{fi:{},en:{}},document:{addEventListener(){}},S:{active:'vault-a',settings:{language:'fi'}},t:k=>k,toast(){},fail:e=>{throw e},navigator:{clipboard:{writeText:async text=>calls.push(text)}},api:async(...args)=>{calls.push(args);return []}};
 vm.createContext(ctx);vm.runInContext(fs.readFileSync('web/chat.js','utf8'),ctx);return {ctx,calls};
}
test('copy preserves a long answer and its source references',async()=>{
 const {ctx,calls}=setup();const message={body:'Long answer äö\n'.repeat(3000)+'END',sources:[{name:'Slide deck',page:2}]};
 await ctx.copyAnswer(message);assert.equal(calls[0],message.body+'\n\nsources\n[1] Slide deck · 2');
});
test('notes retain full answer, source anchor and captured vault',async()=>{
 const {ctx,calls}=setup();ctx.S.active='vault-b';const button={};
 const message={body:'answer\n'.repeat(4000),created:'2026-09-28T12:00:00Z',role:'assistant',sources:[{name:'Deck',document_id:'doc-a',page:3}]};
 await ctx.saveAnswer(message,button,'vault-a');
 assert.equal(calls[0][0],'/api/notes');assert.equal(calls[0][1].body,ctx.answerText(message));
 assert.equal(calls[0][1].document_id,'doc-a');assert.equal(calls[0][1].page,3);assert.equal(calls[0][2].headers['X-ALA-Vault'],'vault-a');assert.equal(button.disabled,false);assert.equal(calls.length,1);
});
