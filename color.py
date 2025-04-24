from colorthief import ColorThief
import matplotlib.pyplot as plt

def extract_colors_with_colorthief(image_path, num_colors=5):
    color_thief = ColorThief(image_path)
    palette = color_thief.get_palette(color_count=num_colors)
    return palette

def show_colors(colors):
    fig, ax = plt.subplots(1, len(colors), figsize=(10, 2))
    for i, color in enumerate(colors):
        ax[i].imshow([[color]])
        ax[i].axis('off')
    plt.show()

if __name__ == "__main__":
    image_path = "t2.jpg"
    colors = extract_colors_with_colorthief(image_path, num_colors=2)
    show_colors(colors)