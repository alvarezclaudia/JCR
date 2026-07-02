"""
AGENT 3 — BUILD
Lee jcr_clean.json y jcr_agg.json y genera index.html completo
"""
import json, os

OUT_DIR = '/sessions/practical-kind-cori/mnt/outputs/'
HTML_OUT = '/sessions/practical-kind-cori/mnt/JCR/index.html'

with open(OUT_DIR+'jcr_clean.json') as f: data = json.load(f)
with open(OUT_DIR+'jcr_agg.json') as f: agg = json.load(f)

agg['years'] = [int(y) for y in agg['years']]
agg['by_year_cat'] = {str(k): v for k,v in agg['by_year_cat'].items()}
agg['avg_jif'] = {str(k): v for k,v in agg['avg_jif'].items()}
agg['quart_by_year'] = {str(k): v for k,v in agg['quart_by_year'].items()}

clean_json = json.dumps(data, separators=(',',':'), ensure_ascii=True)
agg_json   = json.dumps(agg,  separators=(',',':'), ensure_ascii=True)

total    = len(data)
yr_first = agg['years'][0]
yr_last  = agg['years'][-1]
cats     = agg['categories']
n_years  = len(agg['years'])

palette = ['#6c63ff','#ff6584','#43e97b','#f7971e','#38f9d7','#ff9f43','#a29bfe']
cat_colors = {c: palette[i % len(palette)] for i, c in enumerate(cats)}
cat_colors_js = json.dumps(cat_colors, separators=(',',':'))
cats_js = json.dumps(cats, separators=(',',':'))
cat_options = chr(10).join(f'<option>{c}</option>' for c in cats)
ov_cat_options = chr(10).join(f'<option>{c}</option>' for c in ['BUSINESS','ECONOMICS','MANAGEMENT'])

# Read the current HTML template from the installed file
import re
with open(HTML_OUT) as f:
    current = f.read()

# Re-embed data using fixed markers to avoid truncation
MARKER_START = '<!-- DATA_START -->'
MARKER_END   = '<!-- DATA_END -->'

s = current.find('<script>')+8
e = current.rfind('</script>')
if e == -1:
    raise ValueError('</script> not found in HTML — file may be truncated. Restore it first.')

js_all = current[s:e]
ov_pos = js_all.find('const OV_CATS=')
js_logic = js_all[ov_pos:]

html_before_script = current[:s]
# Rebuild data constants
data_block = (
    f'const RAW={clean_json};\n'
    f'const AGG={agg_json};\n'
    f'const CAT_COLORS={cat_colors_js};\n'
    f'const CATS={cats_js};\n'
)
html_tail = current[e:]

# Update header stats
def repl_header(html, yr_first, yr_last, total, n_years):
    html = re.sub(r'\d{4} to \d{4}', f'{yr_first} to {yr_last}', html)
    html = re.sub(r'[\d,]+ records', f'{total:,} records', html)
    html = re.sub(r'\d+ years', f'{n_years} years', html)
    return html

# Update default year in init
js_logic_new = re.sub(r"value='\d{4}'", f"value='{yr_last}'", js_logic)

new_html = html_before_script + data_block + js_logic_new + html_tail
new_html = repl_header(new_html, yr_first, yr_last, total, n_years)

# Fix category dropdowns (safe: no DOTALL)
ov_cats = ['BUSINESS','ECONOMICS','MANAGEMENT']
ov_opts = 