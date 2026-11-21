'use strict';
// Research-only decoder for verified Hornet3000 ONNX [1,9,8400] output.
// Does not load models, activate a camera, send alerts, or claim species identification.
(function (root) {
  const CLASSES = Object.freeze(['amel','vcra','vespsp','vvel','vzon']);
  function iou(a,b) {
    const dx=Math.max(0,Math.min(a[2],b[2])-Math.max(a[0],b[0]));
    const dy=Math.max(0,Math.min(a[3],b[3])-Math.max(a[1],b[1]));
    const intersection=dx*dy;
    const areaA=(a[2]-a[0])*(a[3]-a[1]),areaB=(b[2]-b[0])*(b[3]-b[1]);
    return areaA+areaB>intersection?intersection/(areaA+areaB-intersection):0;
  }
  function decode(tensor,confidence=0.5,iouThreshold=0.45,maxDetections=100) {
    if(!tensor||!Array.isArray(tensor.dims)||tensor.dims.join(',')!=='1,9,8400'||
      !tensor.data||tensor.data.length!==75600)throw Error('Unerwartete ONNX-Ausgabeform');
    if(!(confidence>0&&confidence<=1&&iouThreshold>=0&&iouThreshold<1&&
      Number.isInteger(maxDetections)&&maxDetections>=1&&maxDetections<=1000))throw Error('Ungueltige Grenzwerte');
    const data=tensor.data,candidates=[];
    for(let i=0;i<8400;i++){
      const values=[];
      for(let j=0;j<9;j++){const v=Number(data[j*8400+i]);if(!Number.isFinite(v))throw Error('Nichtendlicher Modellwert');values.push(v)}
      const [x,y,w,h]=values;
      const scores=values.slice(4);
      if(scores.some(s=>s<0||s>1))throw Error('Ungueltiger Klassenscore');
      let cls=0;
      for(let j=1;j<5;j++)if(scores[j]>scores[cls])cls=j;
      if(scores[cls]<confidence||w<=0||h<=0)continue;
      const box=[Math.max(0,x-w/2),Math.max(0,y-h/2),Math.min(640,x+w/2),Math.min(640,y+h/2)];
      if(box[2]<=box[0]||box[3]<=box[1])continue;
      candidates.push({class_id:cls,class_code:CLASSES[cls],confidence:scores[cls],
        box_xyxy_input_pixels:box,verification_status:'unverified'});
    }
    candidates.sort((a,b)=>b.confidence-a.confidence);
    const selected=[];
    for(const item of candidates){
      if(selected.every(old=>old.class_id!==item.class_id||
        iou(item.box_xyxy_input_pixels,old.box_xyxy_input_pixels)<=iouThreshold)){
        selected.push(item);
        if(selected.length>=maxDetections)break;
      }
    }
    return selected;
  }
  const api=Object.freeze({CLASSES,decode});
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  if(root)root.VespaGuardHornetDecoder=api;
})(typeof window!=='undefined'?window:null);
