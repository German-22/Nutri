from reportlab.pdfgen import canvas

c = canvas.Canvas("prueba.pdf")
x = 50
y = 50
d = 40
dist = y 
while dist <= 810:    
    print(dist)
    c.line(x, dist, x + 500, dist)
    dist = dist + d
xh = 50
yh = 50
dh = 250
dist = 0
while dist <= 500:    
    c.line(xh + dist, yh, xh + dist, 810 )
    dist = dist + dh
c.save()