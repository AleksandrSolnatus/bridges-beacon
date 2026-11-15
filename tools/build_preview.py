"""Produce one self-contained HTML preview from the canonical static site."""
from pathlib import Path
import base64
import sys

root=Path(__file__).resolve().parents[1]
site=root/'site'
output=Path(sys.argv[1]) if len(sys.argv)>1 else root.parent/'BRIDGES-BEACON-001.html'
html=(site/'index.html').read_text()
html=html.replace('<link rel="stylesheet" href="style.css">','<style>\n'+(site/'style.css').read_text()+'\n</style>')
html=html.replace('<script src="app.js" defer></script>','')
html=html.replace('</body>', '<script>\n'+(site/'app.js').read_text()+'\n</script>\n</body>')
html=html.replace("style-src 'self'; script-src 'self';", "style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline';")
photo=base64.b64encode((site/'assets/beacon.jpg').read_bytes()).decode('ascii')
html=html.replace('src="assets/beacon.jpg"',f'src="data:image/jpeg;base64,{photo}"')
for name,mime in [('beacon.txt','text/plain'),('beacon.json','application/json'),('report.schema.json','application/json')]:
    data=base64.b64encode((site/name).read_bytes()).decode('ascii')
    html=html.replace(f'href="{name}"',f'href="data:{mime};base64,{data}" download="{name}"')
output.write_text(html)
print(output)
