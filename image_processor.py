import requests
from PIL import Image, ImageDraw, ImageFont
import time
import pytz
from datetime import datetime, timedelta

# Define section positions for each lottery on the image
positions = {
    'DMC4D': {
        '1st': (55, 170),
        '2nd': (135, 170),
        '3rd': (215, 170),
        'special': (45, 230),
        'consolation': (45, 305),
        'color': 'black',
        'dd': (30, 100),
        'dn': (215, 100)
    },
    'M4D': {
        '1st': (330, 170),
        '2nd': (410, 170),
        '3rd': (490, 170),
        'special': (320, 230),
        'consolation': (320, 305),
        'color': 'white',
        'dd': (305, 100),
        'dn': (490, 100)
    },
    'TT': {
        '1st': (615, 170),
        '2nd': (695, 170),
        '3rd': (775, 170),
        'special': (605, 230),
        'consolation': (605, 305),
        'color': 'black',
        'dd': (590, 100),
        'dn': (775, 100)
    },
    'SCS': {
        '1st': (55, 515),
        '2nd': (135, 515),
        '3rd': (215, 515),
        'special': (45, 575),
        'consolation': (45, 650),
        'color': 'black',
        'dd': (30, 445),
        'dn': (215, 445)
    },
    'SB': {
        '1st': (330, 515),
        '2nd': (410, 515),
        '3rd': (490, 515),
        'special': (320, 575),
        'consolation': (320, 650),
        'color': 'black',
        'dd': (305, 445),
        'dn': (490, 445)
    },
    'SGP4D': {
        '1st': (615, 515),
        '2nd': (695, 515),
        '3rd': (775, 515),
        'special': (605, 575),
        'consolation': (605, 650),
        'color': 'white',
        'dd': (590, 445),
        'dn': (775, 445)
    }
}

# API URL (replace this with your actual API endpoint)
API_URL = "https://4dresult88.com/fetchall?_="


def fetch_lottery_results(api_url):
    # Get current Unix timestamp
    current_timestamp = int(time.time())  # Get the current timestamp (seconds since epoch)

    # Construct the full API URL with the timestamp
    api_url_with_timestamp = f"{api_url}{current_timestamp}"

    # Make the API request
    response = requests.get(api_url_with_timestamp)
    if response.status_code == 200:
        return response.json()  # Assuming the API returns JSON data
    else:
        return None


def draw_lottery_results(draw, data, section_name, font):
    if section_name not in positions:
        print(f"Warning: '{section_name}' is not a recognized lottery type.")
        return  # Skip drawing for unrecognized section names

    # Get color and position data for the current section
    color = positions[section_name]['color']

    # Handle dynamic line splitting for 'DD' text, based on pixel width
    dd_text = f"{data['DD']}"
    max_width = 100  # Maximum width for each line in pixels
    dd_lines = []
    current_line = ""

    # Split the text into lines based on the maximum width
    for word in dd_text.split():
        # Check the width of the current line with the new word
        test_line = current_line + (" " + word if current_line else word)
        text_bbox = draw.textbbox((0, 0), test_line, font=font)  # Get the bounding box
        text_width = text_bbox[2] - text_bbox[0]  # Width of the text

        if text_width <= max_width:
            current_line = test_line  # Add word to the current line if it fits
        else:
            dd_lines.append(current_line)  # Save the current line
            current_line = word  # Start a new line with the current word

    # Add any remaining text in the current line
    if current_line:
        dd_lines.append(current_line)

    # Draw 'DD' text with line breaks
    dd_x, dd_y = positions[section_name]['dd']
    line_height = 15  # Get the height of a single line of text
    for line in dd_lines:
        draw.text((dd_x, dd_y), line, fill=color, font=font)
        dd_y += line_height  # Move to the next line

    # Draw the remaining static text for 1st, 2nd, and 3rd positions
    draw.text(positions[section_name]['1st'], f"{data['P1']}", fill=color, font=font)
    draw.text(positions[section_name]['2nd'], f"{data['P2']}", fill=color, font=font)
    draw.text(positions[section_name]['3rd'], f"{data['P3']}", fill=color, font=font)

    # Draw 'DN' text
    draw.text(positions[section_name]['dn'], f"{data['DN']}", fill=color, font=font)

    # Draw Special numbers in rows
    special_numbers = [data[f'S{i}'] for i in range(1, 14) if f'S{i}' in data]  # Only include existing keys
    special_columns = 5  # Number of columns for special numbers
    special_x_start = positions[section_name]['special'][0]
    special_y_start = positions[section_name]['special'][1]
    special_item_width = 45  # Width allocated for each item
    special_item_height = 15  # Height allocated for each item
    for index, number in enumerate(special_numbers):
        x = special_x_start + (index % special_columns) * special_item_width
        y = special_y_start + (index // special_columns) * special_item_height
        draw.text((x, y), number, fill=color, font=font)

    # Draw Consolation numbers in rows
    consolation_numbers = [data[f'C{i}'] for i in range(1, 11) if f'C{i}' in data]  # Only include existing keys
    consolation_columns = 5  # Number of columns for consolation numbers
    consolation_x_start = positions[section_name]['consolation'][0]
    consolation_y_start = positions[section_name]['consolation'][1]
    consolation_item_width = 45  # Width allocated for each item
    consolation_item_height = 20  # Height allocated for each item
    for index, number in enumerate(consolation_numbers):
        x = consolation_x_start + (index % consolation_columns) * consolation_item_width
        y = consolation_y_start + (index // consolation_columns) * consolation_item_height
        draw.text((x, y), number, fill=color, font=font)


def create_result_image(data):
    # Load background image
    base_image = Image.open("background_image.jpg")
    draw = ImageDraw.Draw(base_image)

    # Font with error handling
    try:
        font = ImageFont.truetype("arial.ttf", 14)  # Adjust font and size
    except IOError:
        print("Font file not found. Using default font.")
        font = ImageFont.load_default()

    # Draw results for each lottery
    for section, section_data in data.items():
        draw_lottery_results(draw, section_data, section, font)

    # Get the current date in GMT+8
    gmt_plus_8 = pytz.timezone('Asia/Singapore')  # GMT+8 timezone
    current_date = datetime.now(gmt_plus_8).strftime("%d-%m-%Y")

    # Create the output filename with the date
    output_image = f"4d_results_{current_date}.png"
    base_image.save(output_image)
    return output_image


if __name__ == "__main__":
    # Fetch results from API
    lottery_results = fetch_lottery_results()

    if lottery_results:
        # Create result image
        final_image = create_result_image(lottery_results)
        print(f"Result image saved as {final_image}")
    else:
        print("Failed to fetch lottery results.")
