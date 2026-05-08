#!/bin/bash

# ZipIt Logo Generator - Create all sizes from 512px source
echo "⚡ Generating ZipIt Logo Sizes..."

cd static/images

# Check if source logo exists
if [ ! -f "logo-512.png" ]; then
    echo "❌ Source logo-512.png not found!"
    exit 1
fi

echo "📐 Generating logo sizes from logo-512.png..."

# Generate different sizes using ImageMagick (if available) or Python
if command -v convert >/dev/null 2>&1; then
    echo "Using ImageMagick..."
    
    # PWA Icons
    convert logo-512.png -resize 192x192 logo-192.png
    
    # Favicon sizes
    convert logo-512.png -resize 32x32 favicon-32.png
    convert logo-512.png -resize 16x16 favicon-16.png
    
    # Navigation and UI
    convert logo-512.png -resize 120x40 logo-nav.png
    convert logo-512.png -resize 80x30 logo-footer.png
    convert logo-512.png -resize 200x200 logo-square.png
    
    # Horizontal version (crop to 4:1 ratio)
    convert logo-512.png -resize 400x100^ -gravity center -extent 400x100 logo-horizontal.png
    
    # Social media
    convert logo-512.png -resize 1200x630^ -gravity center -extent 1200x630 logo-og.png
    convert logo-512.png -resize 800x200^ -gravity center -extent 800x200 logo-banner.png
    
    # Create ICO favicon
    convert logo-512.png -resize 32x32 favicon.ico
    
    echo "✅ All logo sizes generated with ImageMagick!"
    
else
    echo "Using Python PIL..."
    
    python3 << 'EOF'
from PIL import Image
import os

# Load source image
try:
    img = Image.open('logo-512.png').convert('RGBA')
    print(f"Source image size: {img.size}")
    
    # Generate different sizes
    sizes = {
        'logo-192.png': (192, 192),
        'favicon-32.png': (32, 32), 
        'favicon-16.png': (16, 16),
        'logo-nav.png': (120, 40),
        'logo-footer.png': (80, 30),
        'logo-square.png': (200, 200),
        'logo-horizontal.png': (400, 100),
        'logo-og.png': (1200, 630),
        'logo-banner.png': (800, 200)
    }
    
    for filename, size in sizes.items():
        # Resize maintaining aspect ratio
        resized = img.copy()
        resized.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Create new image with target size and transparent background
        new_img = Image.new('RGBA', size, (0, 0, 0, 0))
        
        # Center the resized image
        x = (size[0] - resized.size[0]) // 2
        y = (size[1] - resized.size[1]) // 2
        new_img.paste(resized, (x, y), resized)
        
        # Save
        new_img.save(filename, 'PNG')
        print(f"✅ Generated {filename} ({size[0]}x{size[1]})")
    
    # Create favicon.ico
    favicon = img.resize((32, 32), Image.Resampling.LANCZOS)
    favicon.save('favicon.ico', format='ICO')
    print("✅ Generated favicon.ico")
    
    print("🎉 All logo sizes generated successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Please install Pillow: pip install Pillow")
EOF

fi

# List generated files
echo ""
echo "📁 Generated Logo Files:"
ls -la *.png *.ico 2>/dev/null | grep -E "(logo|favicon)" || echo "No files generated"

echo ""
echo "⚡ ZipIt Logo Generation Complete!"