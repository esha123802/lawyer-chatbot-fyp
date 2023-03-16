# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_request_option"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Enter option: \n1. Case Study \n2. Lawyer Information \n3. General Question \n")

        return []    

class PrintLawyerInfo(Action):
    def name(self):
        return "action_print_lawyer_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Define the scope of the Google Sheets API
        scope = ['https://www.googleapis.com/auth/spreadsheets']

        # Set the path to the credentials file for your GCP project
        credentials_path = 'C:/Users/Esha Srivastav/Desktop/dev/fyp/rasa-fyp-a5e02f110091.json'

        # Authenticate your project using the credentials file
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)

        # Set the ID of the Google Sheets spreadsheet you want to access
        spreadsheet_id = '1SfZcwQ9TuT2BTGRHxS-YEMZjHCwgsFyTJQ2cPGND6ws'

        # Create a client to access the Google Sheets API
        client = gspread.authorize(credentials)

        # Open the worksheet you want to read data from
        worksheet = client.open_by_key(spreadsheet_id).sheet1

        # Read the data from the worksheet
        data = worksheet.get_all_records()
        
        state = tracker.get_slot("state")
        court_of_practice = tracker.get_slot("court_of_practice")

        flag = False

        # Use the data in your Rasa chatbot as needed
        for row in data:
            # Access the values in each row of the worksheet   
            if row['state'] == state and row['court of practice'] == court_of_practice:
                dispatcher.utter_message(text=f"Lawyer Name: {row['name']} \nLawyer State: {row['state']} \nMobile No.: {row['mobile']}")
                flag = True
        
        if not flag:
            dispatcher.utter_message("No data found")

        return []

class ActionResetSlots(Action):
    def name(self) -> Text:
        return "action_reset_all_slots"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        return [SlotSet(slot, None) for slot in ["state", "court_of_practice"]]