import {cp, mkdir, rm, readFile, writeFile, readdir} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
process.chdir(root);
await rm('public',{recursive:true,force:true});
await cp('site','public',{recursive:true});
const origin=process.env.PUBLIC_ORIGIN || 'https://bridges-beacon.vercel.app';
for(const name of await readdir('public')) {
 if(/\.(html|json|txt|xml)$/.test(name)) {
  const p=path.join('public',name);
  await writeFile(p,(await readFile(p,'utf8')).replaceAll('__PUBLIC_ORIGIN__',origin));
 }
}
// A checkout can build without network access or downloading Beacon itself.
// Source downloads are produced from this checkout when Git metadata is present.
let hasGit=false;
try { execFileSync('git',['rev-parse','--verify','HEAD'],{stdio:'ignore'}); hasGit=true; } catch {}
if(hasGit) {
 execFileSync('git',['archive','--format=zip','--prefix=bridges-beacon/','-o','public/source.zip','HEAD']);
 execFileSync('git',['bundle','create','public/bridges-beacon.bundle','--all']);
 await mkdir('public/git',{recursive:true});
 execFileSync('git',['clone','--bare','public/bridges-beacon.bundle','public/git/bridges-beacon.git'],{stdio:'ignore'});
 execFileSync('git',['--git-dir=public/git/bridges-beacon.git','update-server-info']);
} else {
 // Source ZIP checkouts have no .git. All application files still build locally.
 console.warn('Git source downloads omitted; canonical source is on GitHub.');
}
console.log('Built public/ from local source.');
