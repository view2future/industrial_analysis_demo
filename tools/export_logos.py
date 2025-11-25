import os
from pathlib import Path

try:
    import cairosvg
except Exception:
    cairosvg = None

BASE = Path(__file__).parent.parent / 'static' / 'img' / 'logos'
OUT = BASE / 'png'

LOGOS = [
    'logo_ai_report.svg',
    'logo_documents_compare.svg',
    'logo_trend_forecast.svg',
    'logo_knowledge_graph.svg',
    'logo_map_3d.svg',
    'logo_industry_chain.svg',
    'logo_policy_read.svg',
    'logo_terms_dictionary.svg',
]

SIZES = [32, 64, 128, 256]

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if cairosvg is None:
        print('cairosvg not installed. Install with: pip install cairosvg')
        return
    for svg_name in LOGOS:
        svg_path = BASE / svg_name
        if not svg_path.exists():
            print(f'Skip missing {svg_path}')
            continue
        for size in SIZES:
            out_path = OUT / f"{svg_path.stem}-{size}.png"
            cairosvg.svg2png(url=str(svg_path), write_to=str(out_path), output_width=size, output_height=size, background_color=None)
            print(f'Wrote {out_path}')

if __name__ == '__main__':
    main()

