from PIL import Image, ImageDraw

def create_muscular_person_image(width=200, height=150, filename="muscular_person.png"):
    """Create a muscular person silhouette image"""
    # Create image with transparent background
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Colors
    silhouette_color = (70, 130, 180)  # Steel blue
    highlight_color = (100, 149, 237)  # Cornflower blue
    
    center_x = width // 2
    
    # Head (circle)
    head_radius = 20
    head_y = 30
    draw.ellipse([center_x - head_radius, head_y - head_radius, 
                  center_x + head_radius, head_y + head_radius], 
                 fill=silhouette_color, outline=highlight_color, width=2)
    
    # Neck
    neck_width = 8
    neck_height = 15
    draw.rectangle([center_x - neck_width//2, head_y + head_radius,
                    center_x + neck_width//2, head_y + head_radius + neck_height],
                   fill=silhouette_color)
    
    # Torso (muscular chest and abs)
    torso_top = head_y + head_radius + neck_height
    torso_width = 60
    torso_height = 70
    
    # Main torso
    draw.rectangle([center_x - torso_width//2, torso_top,
                    center_x + torso_width//2, torso_top + torso_height],
                   fill=silhouette_color, outline=highlight_color, width=2)
    
    # Chest muscles (pectorals)
    pec_width = 20
    pec_height = 25
    # Left pec
    draw.ellipse([center_x - torso_width//2 + 5, torso_top + 5,
                  center_x - 5, torso_top + 5 + pec_height],
                 fill=highlight_color)
    # Right pec
    draw.ellipse([center_x + 5, torso_top + 5,
                  center_x + torso_width//2 - 5, torso_top + 5 + pec_height],
                 fill=highlight_color)
    
    # Arms (muscular)
    arm_width = 25
    arm_length = 60
    arm_y = torso_top + 10
    
    # Left arm (bicep)
    draw.ellipse([center_x - torso_width//2 - arm_width, arm_y,
                  center_x - torso_width//2 + 5, arm_y + arm_length],
                 fill=silhouette_color, outline=highlight_color, width=2)
    
    # Right arm (bicep)
    draw.ellipse([center_x + torso_width//2 - 5, arm_y,
                  center_x + torso_width//2 + arm_width, arm_y + arm_length],
                 fill=silhouette_color, outline=highlight_color, width=2)
    
    # Forearms
    forearm_width = 15
    forearm_length = 30
    forearm_y = arm_y + arm_length - 10
    
    # Left forearm
    draw.rectangle([center_x - torso_width//2 - forearm_width, forearm_y,
                    center_x - torso_width//2, forearm_y + forearm_length],
                   fill=silhouette_color)
    
    # Right forearm
    draw.rectangle([center_x + torso_width//2, forearm_y,
                    center_x + torso_width//2 + forearm_width, forearm_y + forearm_length],
                   fill=silhouette_color)
    
    # Abs definition lines
    abs_y = torso_top + 35
    for i in range(3):
        y_pos = abs_y + i * 12
        draw.line([center_x - 15, y_pos, center_x + 15, y_pos], 
                  fill=highlight_color, width=2)
    
    # V-taper waist
    waist_width = 40
    waist_y = torso_top + torso_height
    draw.polygon([center_x - torso_width//2, waist_y,
                  center_x + torso_width//2, waist_y,
                  center_x + waist_width//2, waist_y + 20,
                  center_x - waist_width//2, waist_y + 20],
                 fill=silhouette_color, outline=highlight_color)
    
    img.save(filename)
    print(f"Muscular person image saved as {filename}")
    return filename

if __name__ == "__main__":
    create_muscular_person_image(200, 150, "muscular_person.png")