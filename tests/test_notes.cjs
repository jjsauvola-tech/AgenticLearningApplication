const {test}=require('node:test');const assert=require('node:assert/strict');const vm=require('node:vm');const fs=require('node:fs');
test('failed note write keeps durable draft and retry uses same id and captured vault',async()=>{
 const storage=new Map(),elements={};for(const id of ['noteTitle','noteBody','noteForm','closeModal','saveNote','noteSaveStatus'])elements['#'+id]={value:'',focus(){}};
 let failWrite=true;const writes=[];
 const ctx={S:{active:'vault-a',doc:{id:'doc'},page:2,settings:{language:'fi'}},crypto:{randomUUID:()=> 'stable-id'},
  localStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)},
  window:{addEventListener(){}},$:id=>elements[id],cur:()=>({title:'Section'}),contextLabel:()=> 'Source',t:k=>k,h:s=>s,
  modal:(_t,_h,ready)=>ready(),closeModal(){},render(){},toast(){},showConnectionStatus(){},
  api:async(path,body,options)=>{if(body){writes.push({body,options});if(failWrite)throw Error('connection_lost');}return [];}};
 vm.createContext(ctx);vm.runInContext(fs.readFileSync('web/notes.js','utf8'),ctx);
 ctx.noteDialog();elements['#noteBody'].value='My preserved thought';elements['#noteBody'].oninput();
 ctx.S.active='vault-b';await elements['#noteForm'].onsubmit({preventDefault(){}});
 assert.equal(JSON.parse([...storage.values()][0]).body,'My preserved thought');assert.equal(elements['#saveNote'].disabled,false);
 failWrite=false;await elements['#noteForm'].onsubmit({preventDefault(){}});
 assert.equal(writes[0].body.id,writes[1].body.id);assert.equal(writes[1].options.headers['X-ALA-Vault'],'vault-a');assert.equal(storage.size,0);
});
