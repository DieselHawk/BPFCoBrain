#!/usr/bin/env python3
"""
Create a brain icon and desktop shortcut for the Brain Desktop app
Generates icon and creates Windows shortcut that works from anywhere
"""

import sys
import os
from pathlib import Path

# Windows UTF-8 fix
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Install PIL if needed
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Installing Pillow...")
    os.system("pip install Pillow -q")
    from PIL import Image, ImageDraw, ImageFont

VAULT_PATH = Path(__file__).parent
ICON_PATH = VAULT_PATH / 'brain-icon.ico'
SHORTCUT_PATH = VAULT_PATH / 'Brain.lnk'
LAUNCHER_PATH = VAULT_PATH / 'launch-brain.bat'

def create_brain_icon():
    """Create a beautiful brain icon"""
    # Create image
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Gradient background circle (dark blue to purple)
    center = size // 2
    radius = size // 2 - 4
    
    # Draw outer circle (dark blue)
    draw.ellipse(
        [(center - radius, center - radius), 
         (center + radius, center + radius)],
        fill=(25, 45, 85),
        outline=(100, 150, 200),
        width=3
    )
    
    # Draw brain-like shape (two hemispheres with connections)
    # Left hemisphere
    left_x = center - 40
    draw.ellipse(
        [(left_x - 35, center - 45), 
         (left_x + 35, center + 45)],
        fill=(100, 200, 255),
        outline=(200, 230, 255),
        width=2
    )
    
    # Right hemisphere
    right_x = center + 40
    draw.ellipse(
        [(right_x - 35, center - 45), 
         (right_x + 35, center + 45)],
        fill=(100, 200, 255),
        outline=(200, 230, 255),
        width=2
    )
    
    # Connection lines (synapses)
    connection_color = (150, 220, 255)
    draw.line([(center - 20, center - 30), (center - 10, center)], fill=connection_color, width=2)
    draw.line([(center - 15, center - 25), (center + 15, center - 25)], fill=connection_color, width=2)
    draw.line([(center + 10, center), (center + 20, center - 30)], fill=connection_color, width=2)
    
    # Add connection nodes (small circles)
    node_positions = [
        (center - 20, center - 30),
        (center - 10, center),
        (center, center - 25),
        (center + 10, center),
        (center + 20, center - 30),
    ]
    
    for x, y in node_positions:
        draw.ellipse(
            [(x - 3, y - 3), (x + 3, y + 3)],
            fill=(255, 220, 100),
            outline=(255, 255, 150)
        )
    
    # Center node (brighter)
    draw.ellipse(
        [(center - 5, center - 5), (center + 5, center + 5)],
        fill=(255, 150, 0),
        outline=(255, 200, 100),
        width=1
    )
    
    # Convert to RGB for ICO format (ICO doesn't support alpha well in all sizes)
    img_rgb = Image.new('RGB', (size, size), (25, 45, 85))
    img_rgb.paste(img, (0, 0), img)
    
    # Save multiple sizes for proper ICO
    img_rgb.save(str(ICON_PATH), format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    print(f"✅ Icon created: {ICON_PATH}")

def create_windows_shortcut():
    """Create Windows shortcut (.lnk) that works from anywhere"""
    try:
        import win32com.client
    except ImportError:
        print("Installing pywin32...")
        os.system("pip install pywin32 -q")
        import win32com.client
    
    # Get absolute path to launcher
    launcher_abs = str(LAUNCHER_PATH.absolute())
    icon_abs = str(ICON_PATH.absolute())
    shortcut_path = str(SHORTCUT_PATH)
    
    # Create shortcut using Windows COM
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    
    shortcut.TargetPath = launcher_abs
    shortcut.WorkingDirectory = str(VAULT_PATH.absolute())
    shortcut.IconLocation = icon_abs
    shortcut.Description = "🧠 Brain Desktop - Your Knowledge Vault"
    shortcut.WindowStyle = 1  # Normal window
    
    shortcut.save()
    print(f"✅ Shortcut created: {shortcut_path}")

def create_portable_shortcut():
    """Fallback: Create a batch shortcut that doesn't need pywin32"""
    shortcut_vbs = VAULT_PATH / 'create-shortcut.vbs'
    
    launcher_abs = str(LAUNCHER_PATH.absolute())
    icon_abs = str(ICON_PATH.absolute())
    shortcut_path = str(SHORTCUT_PATH)
    
    vbs_content = f"""
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"

Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{launcher_abs}"
oLink.WorkingDirectory = "{VAULT_PATH}"
oLink.IconLocation = "{icon_abs}"
oLink.Description = "Brain Desktop - Your Knowledge Vault"
oLink.WindowStyle = 1
oLink.Save
"""
    
    with open(shortcut_vbs, 'w') as f:
        f.write(vbs_content)
    
    print(f"✅ VBS helper created: {shortcut_vbs}")

def main():
    print("🧠 Creating Brain Desktop Icon & Shortcut...")
    print()
    
    # Create icon
    print("📐 Generating brain icon...")
    create_brain_icon()
    
    # Try to create shortcut
    print("🔗 Creating Windows shortcut...")
    try:
        create_windows_shortcut()
    except Exception as e:
        print(f"⚠️  Shortcut creation failed: {e}")
        print("📝 Creating VBS helper instead...")
        create_portable_shortcut()
        print("\n🔧 To create shortcut manually:")
        print(f"   1. Run: cscript create-shortcut.vbs")
        print(f"   2. Or use VBScript approach in create-shortcut.vbs")
    
    print()
    print("✅ ICON & SHORTCUT READY!")
    print()
    print("📥 Download these files:")
    print(f"   1. {ICON_PATH.name} (icon file)")
    print(f"   2. {SHORTCUT_PATH.name} (shortcut to copy to desktop)")
    print()
    print("📍 How to use:")
    print(f"   1. Copy {SHORTCUT_PATH.name} to Desktop")
    print(f"   2. Double-click to launch Brain Desktop")
    print(f"   3. Works from anywhere! 🎉")
    print()
    print("💡 The shortcut uses absolute paths, so it works even if moved.")

if __name__ == '__main__':
    main()
