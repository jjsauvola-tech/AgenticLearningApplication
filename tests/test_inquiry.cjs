const {test}=require('node:test');const assert=require('node:assert/strict');
const draft=require('../web/inquiry.js');
test('retry reuses id for exactly the same pending payload',()=>{
 let count=0;const id=()=>String(++count);const body={attempt_id:'a',expected_revision:2,action:'answer',text:'My draft'};
 const first=draft.request({},body,id),retry=draft.request(first,body,id);
 assert.equal(first.body.request_id,retry.body.request_id);assert.equal(count,1);
 const changed=draft.request(first,{...body,text:'Changed draft'},id);
 assert.notEqual(changed.body.request_id,first.body.request_id);
});
test('draft keys isolate vault, attempt and phase and tolerate broken local storage',()=>{
 assert.notEqual(draft.key('a','x','attempt'),draft.key('b','x','attempt'));
 assert.notEqual(draft.key('a','x','attempt'),draft.key('a','y','attempt'));
 assert.notEqual(draft.key('a','x','attempt'),draft.key('a','x','revise'));
 assert.deepEqual(draft.read({getItem(){throw Error('blocked')}},'key'),{});
});
test('blocked browser storage retains pending retry in memory without preventing a save',()=>{
 const storage={getItem(){throw Error('blocked')},setItem(){throw Error('blocked')},removeItem(){}};
 const value={text:'Not lost during this session',pending:{id:'same'}};
 assert.equal(draft.write(storage,'blocked-key',value),false);
 assert.deepEqual(draft.read(storage,'blocked-key'),value);
 draft.remove(storage,'blocked-key');assert.deepEqual(draft.read(storage,'blocked-key'),{});
});
