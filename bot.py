import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from pytz import timezone
from telegram import Bot
from telegram.error import TelegramError

# Bot API token
API_TOKEN = '7456669912:AAE4CNow-1sV-j41h_dcM88IG5c7INg2zIo'
bot = Bot(token=API_TOKEN)

# Channel username or ID
CHANNEL_ID = '-1002174484217'

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name('kartcutter-74b6f323ce2e.json', scope)
client = gspread.authorize(creds)

# Open the Google Sheet using Spreadsheet ID
spreadsheet_id = '1hDK8y3f6TQGwFwPEMPeYNr63MeQLr6JsUGDqFS20bN8'  # Replace with your spreadsheet ID
sheet = client.open_by_key(spreadsheet_id).sheet1
data = sheet.get_all_records()

# Function to send post
async def send_post(row):
    title = row['title']
    link = row['link']
    message = row['message']
    product_title = row['product_title']
    product_description = row['product_description']
    image_url = row['image_url']
    date_str = row['date']
    time_str = row.get('time', '00:00')  # Assuming 'time' column might not always be present

    # Combine date and time into datetime object
    datetime_str = f"{date_str} {time_str}"
    post_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

    # Convert datetime to UTC before scheduling (adjust timezone as needed)
    post_datetime_utc = post_datetime.astimezone(timezone('UTC'))

    text = f"*{title}*\n\n[ ]({link})\n{message}\n\n*Amazon*\n[{product_title}]({link})\n{product_description}"

    try:
        # Calculate delay until post time
        current_time_utc = datetime.now(timezone('UTC'))
        delay_seconds = (post_datetime_utc - current_time_utc).total_seconds()

        if delay_seconds > 0:
            print(f"Waiting {delay_seconds} seconds until {post_datetime}")
            await asyncio.sleep(delay_seconds)

        # Send the message with photo
        await bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=image_url,
            caption=text,
            parse_mode='Markdown'
        )

        # Adding the date as a small overlay using a separate message (optional)
        await bot.send_message(chat_id=CHANNEL_ID, text=f"`{date_str}`", parse_mode='Markdown')

        print(f"Post sent: {title}")
    except TelegramError as e:
        print(f"Failed to send post: {title}")
        print(e)

# Main function to run asyncio loop
async def main():
    for row in data:
        await send_post(row)

if __name__ == "__main__":
    asyncio.run(main())
    print("All posts sent successfully!")
