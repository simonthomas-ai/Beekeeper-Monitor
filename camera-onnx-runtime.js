'use strict';
// Disabled research stub. No model/runtime is approved; no remote code is loaded.
(() => {
 const select=document.getElementById('camera-model'),file=document.getElementById('hornet-model-file');
 const start=document.getElementById('start-ai'),stop=document.getElementById('stop-ai');
 const result=document.getElementById('camera-ai-result'),video=document.getElementById('live-camera');
 const modelStatus=document.getElementById('camera-model-status');
 const EXPECTED_SHA='1df95cedd08426dc218f8aa9e02667e068c0bda218c29a44032638fab005276f';
 const EXPECTED_SIZE=44737849;
 let running=false,session=null,objectUrl=null,generation=0;
 const canvas=document.createElement('canvas');canvas.width=640;canvas.height=640;
 const ctx=canvas.getContext('2d',{willReadFrequently:true});
 function say(message){result.textContent=message}
 function ready(){start.disabled=running||select.value!=='hornet3000'||!file.files?.length}
 function deactivate(){
   running=false;generation++;stop.disabled=true;session=null;
   if(objectUrl){URL.revokeObjectURL(objectUrl);objectUrl=null}
   modelStatus.textContent='Ausgewählt: '+select.options[select.selectedIndex].text+'. Status: NICHT AKTIV.';
   ready();
 }
 select.addEventListener('change',()=>{deactivate();ready()});
 file.addEventListener('change',()=>{deactivate();ready()});
 stop.addEventListener('click',()=>{deactivate();say('Experimentelle Kamera-KI gestoppt.')});
 document.getElementById('stop-media').addEventListener('click',()=>{deactivate();say('KI und Kamera gestoppt.')});
 window.addEventListener('pagehide',deactivate);
 async function loadRuntime(){
   // Fail closed until a locally bundled, hash-pinned and license-reviewed runtime is approved.
   // Never execute JavaScript or fetch WASM from a third-party CDN at camera activation time.
   throw Error('KI-Laufzeit nicht freigegeben: Es wird keine externe ONNX-Laufzeit nachgeladen.');
 }
 function frameTensor(ort){
   if(!ctx||video.readyState<2||video.videoWidth===0)throw Error('Kamera noch nicht bereit');
   // Letterbox image to 640x640, maintaining original aspect ratio.
   ctx.fillStyle='#727272';ctx.fillRect(0,0,640,640);
   const scale=Math.min(640/video.videoWidth,640/video.videoHeight);
   const w=video.videoWidth*scale,h=video.videoHeight*scale;
   ctx.drawImage(video,(640-w)/2,(640-h)/2,w,h);
   const pixels=ctx.getImageData(0,0,640,640).data;
   const data=new Float32Array(3*640*640);
   for(let i=0;i<640*640;i++){
     data[i]=pixels[i*4]/255;
     data[640*640+i]=pixels[i*4+1]/255;
     data[2*640*640+i]=pixels[i*4+2]/255;
   }
   return new ort.Tensor('float32',data,[1,3,640,640]);
 }
 start.addEventListener('click',async()=>{
   if(running||select.value!=='hornet3000'||!file.files?.length)return;
   if(!video.srcObject||video.readyState<2){say('Bitte zuerst die Kamera einschalten.');return}
   const chosen=file.files[0];
   if(chosen.size!==EXPECTED_SIZE){say('Falsche ONNX-Dateigröße. Modell nicht geladen.');return}
   const token=++generation;running=true;start.disabled=true;stop.disabled=false;
   try{
     say('Prüfe SHA-256 der lokalen ONNX-Datei …');
     const bytes=await chosen.arrayBuffer();
     const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)))
       .map(b=>b.toString(16).padStart(2,'0')).join('');
     if(hash!==EXPECTED_SHA)throw Error('SHA-256 stimmt nicht mit dem dokumentierten Hornet3000-Kandidaten überein');
     if(!running||token!==generation)return;
     say('Lade ONNX-Laufzeit und Modell …');
     const ort=await loadRuntime();
     if(!running||token!==generation)return;
     session=await ort.InferenceSession.create(bytes,{executionProviders:['wasm']});
     if(!running||token!==generation)return;
     if(session.inputNames.length!==1||session.inputNames[0]!=='images'||
        session.outputNames.length!==1||session.outputNames[0]!=='output0')
       throw Error('Unerwartete Modell-Ein-/Ausgaben');
     modelStatus.textContent='Hornet3000: NICHT FREIGEGEBEN – keine produktive Inferenz.';
     say('Kamera-KI nicht freigegeben; es wird keine Inferenz gestartet.');
     while(running&&token===generation){
       const tensor=frameTensor(ort);
       const output=await session.run({images:tensor});
       if(!running||token!==generation)break;
       const found=window.VespaGuardHornetDecoder.decode(output.output0,0.5);
       const velutina=found.filter(x=>x.class_code==='vvel');
       say('Unbestätigte Kandidaten: '+found.length+' · Asiatische Hornisse (vvel): '+velutina.length+
         '. Keine gesicherte Artbestimmung. Keine Alarme.');
       await new Promise(resolve=>setTimeout(resolve,800));
     }
   }catch(err){if(token===generation)say('KI nicht gestartet: '+(err.message||String(err)))}
   finally{if(token===generation)deactivate()}
 });
 ready();
})();
