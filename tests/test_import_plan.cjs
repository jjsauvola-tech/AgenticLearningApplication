const {test}=require('node:test');
const assert=require('node:assert/strict');
const {planImport}=require('../web/imports.js');
const file=(name,path='')=>({name,webkitRelativePath:path});

test('folder import includes nested materials and skips package metadata and ZIP copies',()=>{
  const plan=planImport([
    file('slides.PPTX','release/02_Module_2/slides.PPTX'),
    file('notes.docx','release/01_Module_1/notes.docx'),
    file('source.pdf','release/01_Module_1/references/source.pdf'),
    file('guide.docx','release/guide.docx'),
    file('manifest.json','release/manifest.json'),
    file('all.zip','release/all.zip'),
    file('~$notes.docx','release/~$notes.docx')
  ],'Course');
  assert.equal(plan.supported.length,4);
  assert.equal(plan.skipped.length,3);
  assert.equal(plan.supported[0].course,'Course / 01_Module_1');
  assert.equal(plan.supported[1].course,'Course / 01_Module_1 / references');
  assert.equal(plan.supported.find(x=>x.file.name==='guide.docx').course,'Course');
});

test('individual files retain the selected course and same-name files remain separate',()=>{
  const one=planImport([file('slides.pptx')],' Biology ');
  assert.equal(one.supported[0].course,'Biology');
  const two=planImport([file('slides.pptx','release/01/slides.pptx'),file('slides.pptx','release/02/slides.pptx')],'Biology');
  assert.equal(two.supported.length,2);
  assert.notEqual(two.supported[0].course,two.supported[1].course);
});

test('empty and unsupported-only folders produce no import requests',()=>{
  assert.equal(planImport([],'Course').supported.length,0);
  assert.equal(planImport([file('metadata.json')],'Course').supported.length,0);
});
