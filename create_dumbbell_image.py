from PIL import Image, ImageDraw

def create_dumbbell_image(width=64, height=64, filename="dumbbell.png"):
    """Create a realistic dumbbell image"""
    # Create image with transparent background
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Colors
    metal_color = (169, 169, 169)  # Dark grey metal
    handle_color = (105, 105, 105)  # Darker grey for handle
    highlight = (220, 220, 220)  # Light grey highlight
    
    # Calculate proportions
    center_y = height // 2
    handle_width = width // 3
    handle_height = height // 8
    weight_width = width // 4
    weight_height = height // 2
    
    # Draw left weight
    left_weight_x = 0
    draw.ellipse([left_weight_x, center_y - weight_height//2, 
                  left_weight_x + weight_width, center_y + weight_height//2], 
                 fill=metal_color, outline=handle_color, width=2)
    
    # Draw right weight
    right_weight_x = width - weight_width
    draw.ellipse([right_weight_x, center_y - weight_height//2,
                  right_weight_x + weight_width, center_y + weight_height//2],
                 fill=metal_color, outline=handle_color, width=2)
    
    # Draw handle
    handle_x1 = weight_width - 5
    handle_x2 = width - weight_width + 5
    draw.rectangle([handle_x1, center_y - handle_height//2,
                    handle_x2, center_y + handle_height//2],
                   fill=handle_color, outline=highlight, width=1)
    
    # Add grip texture to handle
    for i in range(3):
        grip_y = center_y - handle_height//4 + i * handle_height//4
        draw.line([handle_x1 + 5, grip_y, handle_x2 - 5, grip_y], 
                  fill=highlight, width=1)
    
    # Add highlights to weights for 3D effect
    draw.arc([left_weight_x + 2, center_y - weight_height//2 + 2,
              left_weight_x + weight_width - 2, center_y + weight_height//2 - 2],
             start=225, end=315, fill=highlight, width=2)
    
    draw.arc([right_weight_x + 2, center_y - weight_height//2 + 2,
              right_weight_x + weight_width - 2, center_y + weight_height//2 - 2],
             start=225, end=315, fill=highlight, width=2)
    
    img.save(filename)
    print(f"Dumbbell image saved as {filename}")
    return filename

if __name__ == "__main__":
    # Create different sizes
    create_dumbbell_image(32, 32, "dumbbell_small.png")
    create_dumbbell_image(48, 48, "dumbbell_medium.png")
    create_dumbbell_image(64, 64, "dumbbell_large.png")