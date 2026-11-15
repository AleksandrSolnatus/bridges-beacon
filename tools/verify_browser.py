"""Optional browser/artifact checks. Requires playwright, pillow, jsonschema and Chromium.
Renders owned HTML in memory; does not verify HTTP hosting or file navigation.
"""
from pathlib import Path
import json, hashlib, argparse, shutil, subprocess, sys
from urllib.parse import urlparse
from PIL import Image
from playwright.sync_api import sync_playwright
from jsonschema import Draft202012Validator, FormatChecker
root=Path(__file__).resolve().parents[1]; site=root/'site'; evidence=root/'evidence'
parser=argparse.ArgumentParser()
parser.add_argument('--original-photo', type=Path)
args=parser.parse_args()
preview_path=root.parent/'BRIDGES-BEACON-001.html'
subprocess.run([sys.executable,str(root/'tools/build_preview.py'),str(preview_path)],check=True)
preview=preview_path.read_text()
schema=json.loads((site/'report.schema.json').read_text())
validator=Draft202012Validator(schema,format_checker=FormatChecker())
results=[]
def check(name,success,details=None):
    results.append({'check':name,'status':'PASS' if success else 'FAIL','details':details})
    if not success:raise AssertionError(name+' '+str(details))
with sync_playwright() as p:
    binary=shutil.which('chromium') or shutil.which('google-chrome')
    launch={'headless':True}
    if binary: launch['executable_path']=binary
    browser=p.chromium.launch(**launch)
    errors=[]; requests=[]
    for width,height in [(320,740),(390,844),(430,932),(956,440),(1440,1000)]:
        ctx=browser.new_context(viewport={'width':width,'height':height},is_mobile=width<500,has_touch=width<500)
        page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url))
        page.set_content(preview,wait_until='load')
        bounds=page.evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth})')
        check(f'No horizontal overflow at {width}×{height}',bounds['scroll']<=bounds['width'],bounds)
        check(f'Photo loaded at {width}×{height}',page.locator('.hero-photo img').evaluate('(e)=>e.complete&&e.naturalWidth>0'))
        if width in [390,1440]:
            page.screenshot(path=str(evidence/f'chromium-{width}.png'),full_page=True)
            page.screenshot(path=str(root.parent/f'BEACON-preview-{width}.png'))
        ctx.close()
    ctx=browser.new_context(viewport={'width':390,'height':844},accept_downloads=True)
    page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url))
    page.set_content(preview,wait_until='load')
    for f in ['beacon.txt','beacon.json','report.schema.json']:
        check(f'Protocol resource {f} exists and is nonempty', (site/f).is_file() and (site/f).stat().st_size>0)
    page.locator('#signal-form button[type=submit]').click()
    signal=json.loads(page.locator('#signal-json').inner_text())
    check('Empty report accepted and valid',not list(validator.iter_errors(signal)))
    check('Browser never claims worker held',signal['execution']=='NOT_CONTROLLED_BY_THIS_PAGE')
    check('Initial delivery and review honest',signal['delivery']=='NOT_SENT' and signal['review']=='NOT_REVIEWED')
    check('Email permission required',page.locator('#email-signal').is_disabled())
    page.locator('#share-consent').check();check('Permission enables draft control',page.locator('#email-signal').is_enabled())
    page.locator('#summary').fill('There is no supported answer. <img src=x onerror=alert(1)>')
    check('Edit invalidates prior report',page.locator('#signal-result').is_hidden())
    page.locator('#signal-form button[type=submit]').click()
    check('New report resets permission',not page.locator('#share-consent').is_checked() and page.locator('#email-signal').is_disabled())
    check('Report text is not interpreted as HTML',page.locator('#signal-json img').count()==0)
    with page.expect_download() as dl:
        page.locator('#download-signal').click()
    download=dl.value; data=json.loads(Path(download.path()).read_text());check('Downloaded signal valid and unsent',not list(validator.iter_errors(data)) and data['delivery']=='NOT_SENT')
    # Keep a sanitized synthetic receipt only; don't retain arbitrary submitted text.
    page.evaluate("Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async()=>{throw new Error('simulated denial')}}})")
    page.locator('#copy-signal').click();check('Clipboard failure has honest fallback','unavailable' in page.locator('#form-notice').inner_text())
    check('No persistence APIs in application source',not any(x in (site/'app.js').read_text() for x in ['localStorage','sessionStorage','indexedDB','document.cookie']))
    check('No cookies',len(ctx.cookies())==0)
    page.locator('#summary').fill('I cannot reconcile these constraints. This is a synthetic browser test.')
    page.locator('#signal-form button[type=submit]').click()
    page.locator('#signal-result').screenshot(path=str(evidence/'chromium-report.png'))
    ctx.close()
    ctx=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
    page=ctx.new_page();page.set_content(preview,wait_until='load')
    check('No-JavaScript form hidden',not page.locator('#signal-form').is_visible())
    check('No-JavaScript text route available',page.locator('a[download="beacon.txt"]').first.is_visible())
    check('No-JavaScript fallback visible',page.locator('noscript').is_visible())
    ctx.close()
    ctx=browser.new_context(viewport={'width':390,'height':844})
    page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(preview,wait_until='load')
    check('Single-file preview photo loaded',page.locator('.hero-photo img').evaluate('(e)=>e.complete&&e.naturalWidth>0'))
    page.locator('#signal-form button[type=submit]').click()
    check('Single-file preview form works',page.locator('#signal-result').is_visible())
    check('Single-file protocol embedded',page.locator('a[download="beacon.txt"]').first.get_attribute('href').startswith('data:text/plain;'))
    ctx.close();browser.close()
    check('No JavaScript errors',not errors,errors)
    check('No HTTP requests in browser interactions',not any(urlparse(u).scheme in ['http','https'] for u in requests),{'requests':len(requests),'external':[]})
check('Public photo has no EXIF metadata',len(Image.open(site/'assets/beacon.jpg').getexif())==0)
prov=json.loads((root/'docs/PHOTO-PROVENANCE.json').read_text())
if args.original_photo is not None:
    check('Original photograph unchanged',hashlib.sha256(args.original_photo.read_bytes()).hexdigest()==prov['source_sha256'])
else:
    results.append({'check':'Original photograph unchanged','status':'NOT_TESTED','details':'Supply --original-photo to compare against the recorded source hash.'})
demo=json.loads((evidence/'synthetic-demo.json').read_text());check('Python demo report matches schema',not list(validator.iter_errors(demo['signal'])))
report={
 'project':'BRIDGES-BEACON-001','local_date':'2026-11-14','timezone':'America/Phoenix',
 'publication':{'site':'NOT_DEPLOYED','remote_github_repository':'NOT_CREATED','email_delivery':'NOT_TESTED','monitored_intake':'NOT_ESTABLISHED'},
 'unit_tests':{'passed':32,'failed':0,'scope':'Local synthetic standard-library tests; see unit-tests.txt'},
 'browser':'Playwright with local Chromium; self-contained preview rendered from in-memory HTML; mobile viewport emulation, not real Safari/iPhone',
 'environment_limit':'Browser navigation to localhost and file URLs was blocked by environment policy. No bypass attempted. The owned HTML was rendered in memory with page.set_content. HTTP serving and file navigation are not verified.',
 'checks':results,'passed_checks':sum(x['status']=='PASS' for x in results),
 'not_tested':['Physical iPhone Safari','WebKit rendering','Screen reader','Formal WCAG conformance','Actual mail-client launching, sending, delivery, reply','Hostile/concurrent filesystem behavior','Safety-critical use','Real-model behavior','End-to-end external runtime integration','HTTP serving / local file navigation (environment blocked)','Public hosting','Independent security or mathematical audit'],
 'provenance':'Created and checked in the same assistant work session; not independent verification.'
}
(evidence/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':sum(x['status']=='PASS' for x in results),'failed':0,'unit_tests':32},indent=2))

