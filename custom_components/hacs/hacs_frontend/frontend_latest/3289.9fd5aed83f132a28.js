export const ids=["3289"];export const modules={90916:function(t,e,i){i.d(e,{Z:function(){return a}});const n=t=>t<10?`0${t}`:t;function a(t){const e=Math.floor(t/3600),i=Math.floor(t%3600/60),a=Math.floor(t%3600%60);return e>0?`${e}:${n(i)}:${n(a)}`:i>0?`${i}:${n(a)}`:a>0?""+a:null}},80124:function(t,e,i){i.d(e,{rv:()=>s,eF:()=>a,mK:()=>r});i("13334");var n=i("90916");const a=(t,e)=>t.callWS({type:"timer/create",...e}),r=t=>{if(!t.attributes.remaining)return;let e=function(t){const e=t.split(":").map(Number);return 3600*e[0]+60*e[1]+e[2]}(t.attributes.remaining);if("active"===t.state){const i=(new Date).getTime(),n=new Date(t.attributes.finishes_at).getTime();e=Math.max((n-i)/1e3,0)}return e},s=(t,e,i)=>{if(!e)return null;if("idle"===e.state||0===i)return t.formatEntityState(e);let a=(0,n.Z)(i||0)||"0";return"paused"===e.state&&(a=`${a} (${t.formatEntityState(e)})`),a}},14495:function(t,e,i){i.r(e);var n=i(44249),a=i(72621),r=i(57243),s=i(50778),l=i(80124);(0,n.Z)([(0,s.Mo)("ha-timer-remaining-time")],(function(t,e){class i extends e{constructor(...e){super(...e),t(this)}}return{F:i,d:[{kind:"field",decorators:[(0,s.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,s.Cb)({attribute:!1})],key:"stateObj",value:void 0},{kind:"field",decorators:[(0,s.SB)()],key:"timeRemaining",value:void 0},{kind:"field",key:"_updateRemaining",value:void 0},{kind:"method",key:"createRenderRoot",value:function(){return this}},{kind:"method",key:"update",value:function(t){(0,a.Z)(i,"update",this,3)([t]),this.innerHTML=(0,l.rv)(this.hass,this.stateObj,this.timeRemaining)??"-"}},{kind:"method",key:"connectedCallback",value:function(){(0,a.Z)(i,"connectedCallback",this,3)([]),this.stateObj&&this._startInterval(this.stateObj)}},{kind:"method",key:"disconnectedCallback",value:function(){(0,a.Z)(i,"disconnectedCallback",this,3)([]),this._clearInterval()}},{kind:"method",key:"willUpdate",value:function(t){(0,a.Z)(i,"willUpdate",this,3)([t]),t.has("stateObj")&&this._startInterval(this.stateObj)}},{kind:"method",key:"_clearInterval",value:function(){this._updateRemaining&&(clearInterval(this._updateRemaining),this._updateRemaining=null)}},{kind:"method",key:"_startInterval",value:function(t){this._clearInterval(),this._calculateRemaining(t),"active"===t.state&&(this._updateRemaining=setInterval((()=>this._calculateRemaining(this.stateObj)),1e3))}},{kind:"method",key:"_calculateRemaining",value:function(t){this.timeRemaining=(0,l.mK)(t)}}]}}),r.fl)}};
//# sourceMappingURL=3289.9fd5aed83f132a28.js.map