(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports) module.exports=api;
  else root.GatopleCore=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const NOTE_COUNT=12;
  const A_INDEX=9;
  const MODALITY='Eólico';
  const mod=(value,base=NOTE_COUNT)=>((value%base)+base)%base;
  const ORIGIN_POSITION=A_INDEX; // 9 h: horizontal de origen
  const noteAtPosition=(tonic,position)=>mod(tonic+position-ORIGIN_POSITION);
  const positionForNote=(tonic,note)=>mod(note-tonic+ORIGIN_POSITION);
  const CHROMATIC_HOURS=[3,8,1,6,11,4,9,2,7,12,5,10];
  const hourForPosition=position=>CHROMATIC_HOURS[position];
  const normalizeAngleDelta=delta=>((delta+180)%360+360)%360-180;
  const semitoneStepsFromDrag=(startAngle,currentAngle)=>Math.round(normalizeAngleDelta(currentAngle-startAngle)/30);
  const rotateHPlus=tonic=>mod(tonic+5);
  const rotateHMinus=tonic=>mod(tonic-5);
  const zeroPythagoras=tonic=>[0,1,2,3].map(step=>mod(tonic+step*5));
  return {NOTE_COUNT,A_INDEX,ORIGIN_POSITION,MODALITY,mod,noteAtPosition,positionForNote,hourForPosition,normalizeAngleDelta,semitoneStepsFromDrag,rotateHPlus,rotateHMinus,zeroPythagoras};
});
