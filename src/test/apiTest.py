import os.path
import datetime as dt
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]
load_dotenv()
CALENDAR_ID = os.getenv("KAI_EM_CALENDAR_ID")

def format_event_time(time_str):
    if not time_str:
        return ""
    
    if len(time_str) <= 10:
        return "All Day"
    
    dt_obj = dt.datetime.fromisoformat(time_str.replace("Z", "+00:00"))
    return dt_obj.strftime("%I:%M %p")


def main():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

            with open("token.json", "w") as token:
                token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        today = dt.datetime.now(dt.UTC)
        days_since_monday = today.weekday()
        start_of_week = today - dt.timedelta (days=days_since_monday)
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

        end_of_week= start_of_week + dt.timedelta(days=6)
        end_of_week = end_of_week.replace(hour=23, minute=59, second=59, microsecond=0)

        timeMin = start_of_week.isoformat().replace("+00:00", "Z")
        timeMax = end_of_week.isoformat().replace("+00:00", "Z")

        event_result = service.events().list(calendarId=CALENDAR_ID, timeMin=timeMin, timeMax=timeMax, singleEvents=True, orderBy="startTime").execute()
        events = event_result.get("items", [])

        if not events:
            print("no upcoming events found")
            return
        
        weekly_list = []
        for event in events:
            start = event["start"].get("dateTime") or event["start"].get("date")
            end = event["end"].get("dateTime") or event["end"].get("date")
            summary = event.get("summary", "(No Title)")

            event_date = dt.datetime.fromisoformat(start[:10])
            weekly_list.append({
                    "day": event_date.strftime("%A"),
                    "start": format_event_time(start),
                    "end": format_event_time(end),
                    "summary": summary,
                    "is_all_day": "dateTime" not in event["start"]
                })

        print(weekly_list)
        # for event in events:
        #     start = event["start"].get("dateTime", event["start"].get("date"))
        #     print(start, event["summary"])

    except HttpError as error:
        print("An error occurred:", error)
    

if __name__ == "__main__":
    main()