(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports) module.exports=api;
  else root.GatopleCore=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const NOTE_COUNT=12;
  const A_INDEX=9;
  const MODALITY='Eólico';
  const GLYPHS=Object.freeze(['□','★I','+','★II','♀','↑','★III','↓','★IV','∶','★V','△']);
  const PIANO_WHITE=Object.freeze([
    {note:9,off:0},{note:11,off:0},{note:0,off:1},{note:2,off:1},
    {note:4,off:1},{note:5,off:1},{note:7,off:1},{note:9,off:1}
  ]);
  const PIANO_BLACK=Object.freeze([
    {note:10,off:0},null,{note:1,off:1},{note:3,off:1},
    null,{note:6,off:1},{note:8,off:1}
  ]);
  const mod=(value,base=NOTE_COUNT)=>((value%base)+base)%base;
  const ORIGIN_POSITION=A_INDEX; // 9 h: horizontal de origen
  const stationForPosition=position=>mod(position*5);
  const noteAtPosition=(tonic,position)=>mod(tonic+position-ORIGIN_POSITION);
  const positionForNote=(tonic,note)=>mod(note-tonic+ORIGIN_POSITION);
  const hourForPosition=position=>{
    const station=stationForPosition(position);
    return station===0?12:station;
  };
  const normalizeAngleDelta=delta=>((delta+180)%360+360)%360-180;
  const semitoneStepsFromDrag=(startAngle,currentAngle)=>Math.round(normalizeAngleDelta(currentAngle-startAngle)/30);
  const rotateHPlus=tonic=>mod(tonic+5);
  const rotateHMinus=tonic=>mod(tonic-5);
  const zeroPythagoras=tonic=>[0,1,2,3].map(step=>mod(tonic+step*5));
  return {NOTE_COUNT,A_INDEX,ORIGIN_POSITION,MODALITY,GLYPHS,PIANO_WHITE,PIANO_BLACK,mod,stationForPosition,noteAtPosition,positionForNote,hourForPosition,normalizeAngleDelta,semitoneStepsFromDrag,rotateHPlus,rotateHMinus,zeroPythagoras};
});
