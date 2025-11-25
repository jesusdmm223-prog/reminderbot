#!/usr/bin/env python3
"""
Script para crear iconos para la PWA
Requiere: pip install pillow
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Crea un icono cuadrado con el símbolo de checklist"""
    # Crear imagen con fondo gradiente
    img = Image.new('RGB', (size, size), color='#6366f1')
    draw = ImageDraw.Draw(img)

    # Dibujar un cuadrado con check (símbolo de tarea)
    margin = size // 4
    square_size = size // 2
    x1 = margin
    y1 = margin
    x2 = x1 + square_size
    y2 = y1 + square_size

    # Fondo blanco del cuadrado
    draw.rectangle([x1, y1, x2, y2], fill='white', outline='white', width=5)

    # Dibujar checkmark
    check_points = [
        (x1 + square_size * 0.2, y1 + square_size * 0.5),
        (x1 + square_size * 0.4, y1 + square_size * 0.7),
        (x1 + square_size * 0.8, y1 + square_size * 0.3)
    ]
    draw.line(check_points, fill='#10b981', width=size//15, joint='curve')

    # Guardar
    img.save(filename, 'PNG')
    print(f"✅ Icono creado: {filename}")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Crear iconos de diferentes tamaños
    create_icon(192, os.path.join(script_dir, 'icon-192.png'))
    create_icon(512, os.path.join(script_dir, 'icon-512.png'))

    print("\n✨ Iconos creados exitosamente!")
