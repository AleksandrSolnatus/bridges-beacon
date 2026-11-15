import {list,put,head} from '@vercel/blob';
import {randomUUID} from 'node:crypto';
export default async function handler(req,res){
res.setHeader('Cache-Control','no-store');
const id=req.query.id;
if(id!==undefined&&!/^[0-9a-f-]{36}$/.test(id))return res.status(400).json({error:'Invalid thread ID'});
const path=id?'signals/'+id+'.json':null;
try{
if(req.method!=='GET'&&req.method!=='POST')return res.status(405).end();
let original;
if(id){try{original=await head(path)}catch(e){if(e.name==='BlobNotFoundError')return res.status(404).json({error:'Unknown thread'});throw e}}
if(req.method==='GET'){
const page=await list({prefix:id?'replies/'+id+'/':'signals/',limit:25,cursor:req.query.cursor||undefined});
const read=async b=>{const response=await fetch(b.url);if(!response.ok)throw Error('read');return response.json()};
return res.json({thread:id?await read(original):undefined,items:await Promise.all(page.blobs.map(read)),next:page.hasMore?page.cursor:null})}
const b=req.body;
if(!b||b.public!==true||typeof b.message!=='string'||!b.message.trim()||b.message.length>1200)return res.status(400).json({error:'Submit JSON with public=true and message of 1–1200 characters'});
const key=randomUUID(),thread=id||key,record={id:key,thread,message:b.message.trim(),created:new Date().toISOString()};
await put(id?'replies/'+id+'/'+key+'.json':'signals/'+key+'.json',JSON.stringify(record),{access:'public',contentType:'application/json',addRandomSuffix:false});
return res.status(201).json({status:'stored',id:key,thread,receipt:'/api/board?id='+thread})
}catch(e){console.error(e.name);return res.status(503).json({error:'Board storage unavailable'})}}