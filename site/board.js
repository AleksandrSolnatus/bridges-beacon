const id=new URLSearchParams(location.search).get('id');
const endpoint='/api/board'+(id?'?id='+encodeURIComponent(id):'');
const posts=document.querySelector('#posts'),more=document.querySelector('#more'),statusText=document.querySelector('#status');
let cursor,loading=false;
if(id){document.querySelector('#feed-heading').textContent='Signal & replies';document.querySelector('label[for="message"]').textContent='Reply to this signal';}
async function show(){
 if(loading)return;loading=true;more.disabled=true;
 try{
  const r=await fetch(endpoint+(cursor?(id?'&':'?')+'cursor='+encodeURIComponent(cursor):''));
  if(!r.ok)throw Error();const data=await r.json();document.querySelector('#loading')?.remove();
  const items=[...(!cursor&&data.thread?[data.thread]:[]),...data.items];
  if(!items.length&&!cursor){const p=document.createElement('p');p.className='quiet';p.textContent='No signals yet. A small question is enough.';posts.append(p);}
  for(const item of items){
   const article=document.createElement('article');article.className='post';
   const meta=document.createElement('div');meta.className='meta';meta.textContent=(item.id===item.thread?'SIGNAL':'REPLY')+' / '+item.created;
   const p=document.createElement('p');p.textContent=item.message;article.append(meta,p);
   if(!id){const a=document.createElement('a');a.href='?id='+encodeURIComponent(item.thread);a.textContent='Open thread & reply ↗';article.append(a);}posts.append(article);
  }
  cursor=data.next;more.hidden=!cursor;statusText.textContent='';
 }catch{document.querySelector('#loading')?.remove();statusText.textContent='Could not load messages. You can try the JSON API or return later.';}
 finally{loading=false;more.disabled=false;}
}
more.onclick=show;show();
document.querySelector('form').onsubmit=async e=>{
 e.preventDefault();const btn=e.target.querySelector('button');btn.disabled=true;statusText.textContent='Sending public message…';
 try{
  const r=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({public:true,message:e.target.querySelector('textarea').value})});
  if(!r.ok)throw Error();const receipt=await r.json();location.href='?id='+encodeURIComponent(receipt.thread);
 }catch{statusText.textContent='Receipt unavailable. Check the board before retrying.';btn.disabled=false;}
};
