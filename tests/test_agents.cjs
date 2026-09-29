const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');const vm=require('node:vm');
const {projectLearningModules,preferredModuleDocument,pairedModuleMaterials}=require('../web/agents.js');
test('document and slide selectors stay in the same module',()=>{
 const docs=[{id:'guide',course:'A',format:'docx'},{id:'deck',course:'A',format:'pptx'},{id:'other',course:'B',format:'pptx'}];
 assert.deepEqual(pairedModuleMaterials(docs,docs[0]),{documents:[docs[0]],slides:[docs[1]]});
 assert.equal(pairedModuleMaterials(docs,docs[2]).documents.length,0);
});
test('module navigation prefers slides and preserves document fallback',()=>{
 const docs=[{id:'guide',format:'docx'},{id:'slides',format:'pptx'}];
 assert.equal(preferredModuleDocument(docs).id,'slides');
 assert.equal(preferredModuleDocument(docs.slice(0,1)).id,'guide');
});

test('module progress counts study marks and clamps invalid completion',()=>{
 const result=projectLearningModules([
  {id:'a',course:'Course / Module_1',count:8,completed:4},
  {id:'b',course:'Course / Module_1',count:2,completed:9},
  {id:'c',course:'Course / Module_2',count:0,completed:2},
  {id:'d',count:-2,completed:-1}
 ]);
 assert.equal(result[0].title,'Module 1');assert.equal(result[0].percent,60);
 assert.equal(result[0].documents.length,2);assert.equal(result[1].percent,0);
 assert.equal(result[2].count,0);
});
test('same module titles in different courses do not merge',()=>{
 const result=projectLearningModules([{course:'A / Module_1',count:1},{course:'B / Module_1',count:2}]);
 assert.equal(result.length,2);assert.equal(result[0].count,1);assert.equal(result[1].count,2);
 assert.deepEqual(projectLearningModules([]),[]);
});
test('opt-in graph escapes document identifiers and collection names',()=>{
 const ctx={URLSearchParams,location:{search:'?ux=agents'},window:{},
  document:{addEventListener(){}},localStorage:{getItem(){}},
  S:{settings:{language:'fi'},documents:[{id:'"><script>',course:'<img onerror=alert(1)>',count:1,completed:0}],doc:null},
  h:s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;'),
  legacyFlow:()=>'<aside>Legacy</aside>'};
 vm.createContext(ctx);vm.runInContext(fs.readFileSync('web/agents.js','utf8'),ctx);
 const html=ctx.window.learningAgentFlow();
 assert.ok(html.includes('&lt;img'));assert.ok(!html.includes('<script>'));
 assert.ok(html.includes('eivät osaamisarvio'));assert.ok(html.includes('Legacy'));
});
test('tutor activity follows concurrent requests and stays scoped to the active vault',()=>{
 const status={},avatar={};const ctx={URLSearchParams,location:{search:'?ux=agents'},window:{},
  document:{addEventListener(){}},localStorage:{getItem(){}},
  S:{active:'a',settings:{language:'en'}},$:s=>s==='#agentTutorStatus'?status:avatar};
 vm.createContext(ctx);vm.runInContext(fs.readFileSync('web/agents.js','utf8'),ctx);
 const finishA=ctx.window.beginLearningAgentActivity('a');
 const finishB=ctx.window.beginLearningAgentActivity('a');
 assert.equal(status.textContent,'Processing your request');
 finishA(false);assert.equal(status.textContent,'Processing your request');
 finishB(true);assert.equal(status.textContent,'The request failed — let’s try again');
 const finishOld=ctx.window.beginLearningAgentActivity('a');ctx.S.active='b';finishOld(true);
 assert.equal(status.textContent,'Ready to think with you');
});
