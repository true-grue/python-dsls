from pywasm import pywasm, add_import

julia = '''
def make_matrix(width, height):
    rows = []
    y = 0
    while y < height:
        row = []
        x = 0
        while x < width:
            color = []
            color.append(0)
            color.append(0)
            color.append(0)
            row.append(color)
            x += 1
        rows.append(row)
        y += 1
    return rows

def set_pixel(pixel, r, g, b):
    pixel[0] = r
    pixel[1] = g
    pixel[2] = b

def julia(x, y, times):
    i = 0
    zr = x
    zi = y
    while i < times:
        zr_new = zr * zr - zi * zi - 0.1
        zi = 2 * zr * zi + 0.65
        zr = zr_new
        if zr * zr + zi * zi >= 4:
            return 255 * i / times
        i += 1
    return 255

def make_fractal(min_x, min_y, max_x, max_y, image, width, height):
    pixel_x = (max_x - min_x) / width
    pixel_y = (max_y - min_y) / height
    x = 0
    while x < width:
        real = min_x + x * pixel_x
        y = 0
        while y < height:
            imag = min_y + y * pixel_y
            c = julia(real, imag, 200)
            set_pixel(image[y][x], c, c, 50)
            y += 1
        x += 1

def main(zoom):
    w = 200
    h = 200
    image = make_matrix(w, h)
    make_fractal(-1 - zoom + 0.5, -zoom, -1 + zoom + 0.5, zoom, image, w, h)
    imshow(image)
'''

imports = {}
add_import(imports, 'imshow', 1, 0)
with open('julia.wat', 'w') as f:
    f.write(pywasm(imports, julia))
