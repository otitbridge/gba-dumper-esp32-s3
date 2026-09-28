// Run after KiCad exports each copper layer with Edge.Cuts, top view.
const sharp=require('sharp'),fs=require('fs');
const dir='output/pcb/ad6_rerouted_layers';
const names=['F.Cu','In1.Cu','In2.Cu','B.Cu'];
(async()=>{
 const images=[];
 for(const [i,n] of names.entries()){
  await sharp(`${dir}/${n}.svg`,{density:508}).flatten({background:'#ffffff'}).png().toFile(`${dir}/${n}.png`);
  const copper=await sharp(`${dir}/${n}.svg`,{density:254}).resize(1000,1000).flatten({background:'#ffffff'}).png().toBuffer();
  const title=Buffer.from(`<svg width="1060" height="80"><rect width="1060" height="80" fill="white"/><text x="30" y="35" font-family="Arial" font-size="26" fill="#14213d">L${i+1} / ${n}${i===1?' / GND plane':''}</text><text x="30" y="64" font-family="Arial" font-size="17" fill="#475569">After AD6 reroute | top view, not mirrored | 100 x 100 mm</text></svg>`);
  const panel=await sharp({create:{width:1060,height:1110,channels:3,background:'white'}}).composite([{input:title,left:0,top:0},{input:copper,left:30,top:80}]).png().toBuffer();
  images.push({input:panel,left:(i%2)*1060,top:Math.floor(i/2)*1110});
 }
 await sharp({create:{width:2120,height:2220,channels:3,background:'white'}}).composite(images).png().toFile(`${dir}/four_layers.png`);
})();
