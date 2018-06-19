import cairocffi as cairo

WIDTH, HEIGHT = 600, 900
OFFSET = 10

cheight = 0

ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
cr = cairo.Context(ims)

cr.set_source_rgb(1, 1, 1)
cr.rectangle(0, 0, 595, 842)
cr.fill()

cr.set_source_rgb(0, 0, 0)
cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

cheight += 30

cr.set_font_size(12)
cr.move_to(OFFSET, cheight)    
cr.show_text("Base Chart")

cr.set_font_size(18)
(x, y, width, height, dx, dy) = cr.text_extents("Name")
cr.move_to(WIDTH / 2 - width / 2, cheight)    
cr.show_text("Name")

cheight += 20

cr.set_font_size(12) 
(x, y, width, height, dx, dy) = cr.text_extents("ExpertSingle")
cr.move_to(WIDTH / 2 - width / 2, cheight)   
cr.show_text("ExpertSingle")

cheight += 30

cr.set_line_width(2)

for i in range(0, 5):

    if i == 0 or i == 4:
        cr.set_source_rgb(0.6, 0.6, 0.6)
    else:
        cr.set_source_rgb(0.7, 0.7, 0.7)

    cr.move_to(OFFSET * 4, cheight)
    cr.line_to(WIDTH - OFFSET * 4, cheight) 
    cr.stroke()
    cheight += 10

vline_pos = ((WIDTH - OFFSET * 4) - (OFFSET * 4))  / 6
cheight -= 50

for i in range(0, 8):
    cr.move_to(OFFSET * 4 + (i * vline_pos), cheight)
    cr.line_to(OFFSET * 4 + (i * vline_pos), cheight + 40) 
    cr.stroke()

ims.write_to_png("chart.png")