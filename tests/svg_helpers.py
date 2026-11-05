def svg_attr(svg: str, name: str) -> float:
    return float(svg.split(f'{name}="')[1].split('"')[0])
