'use strict';
const assert=require('node:assert/strict');
const test=require('node:test');
const {decode,CLASSES}=require('../hornet-onnx-decoder.js');
const make=()=>({dims:[1,9,8400],data:new Float32Array(9*8400)});
function candidate(t,i,cls,score,x=100,y=100,w=20,h=20){
  [x,y,w,h].forEach((v,k)=>{t.data[k*8400+i]=v});
  t.data[(4+cls)*8400+i]=score;
}
test('Correct five classes and velutina class 3',()=>{
 assert.deepEqual(CLASSES,['amel','vcra','vespsp','vvel','vzon']);
 const t=make();candidate(t,4,3,0.9);
 const result=decode(t);
 assert.equal(result.length,1);assert.equal(result[0].class_code,'vvel');
 assert.equal(result[0].verification_status,'unverified');
});
test('Overlapping same class suppressed; different class retained',()=>{
 const t=make();candidate(t,0,3,0.9);candidate(t,1,3,0.8);candidate(t,2,1,0.7);
 assert.deepEqual(decode(t).map(x=>x.class_code),['vvel','vcra']);
});
test('Below threshold not emitted',()=>{const t=make();candidate(t,0,3,0.2);assert.equal(decode(t).length,0)});
test('Reject unexpected output shape',()=>assert.throws(()=>decode({dims:[1,6,8400],data:new Float32Array(6*8400)})));
test('Reject non-finite output',()=>{const t=make();t.data[0]=NaN;assert.throws(()=>decode(t))});
test('Reject invalid class score',()=>{const t=make();t.data[4*8400]=-1;assert.throws(()=>decode(t))});
