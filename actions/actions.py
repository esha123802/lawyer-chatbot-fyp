# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction, ValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict

import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope of the Google Sheets API
scope = ['https://www.googleapis.com/auth/spreadsheets']

# Set the path to the credentials file for your GCP project
credentials_path = 'C:/Users/Esha Srivastav/Desktop/dev/fyp/rasa-fyp-a5e02f110091.json'

# Authenticate your project using the credentials file
credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)

# Set the ID of the Google Sheets spreadsheet you want to access
spreadsheet_id = '1HZ6FwP0u_zT4pbgFWusInln7p1Nmp6H388jsDsuBq6o' # final
# spreadsheet_id = '1SfZcwQ9TuT2BTGRHxS-YEMZjHCwgsFyTJQ2cPGND6ws'

# Create a client to access the Google Sheets API
client = gspread.authorize(credentials)

# Open the worksheet you want to read data from
worksheet = client.open_by_key(spreadsheet_id).sheet1

# Read the data from the worksheet
data = worksheet.get_all_records()

states = set()

for row in data:
    states.add(row['state'])

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
               
        state = tracker.get_slot("state")
        court_of_practice = tracker.get_slot("court_of_practice")        

        # To check whether lawyer data for given requirement exists or not in the csv file
        flag = False 


        for row in data:
            if row['state'] == state and row['court of practice'].find(court_of_practice) != -1:
                if row['address'] == "":
                    dispatcher.utter_message(text=f"Lawyer Name: {row['name']} \nLawyer State: {row['state']} \nAddress: Not Available")
                else:
                    dispatcher.utter_message(text=f"Lawyer Name: {row['name']} \nLawyer State: {row['state']} \nAddress: {row['address']}")
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
    
class ActionGreetUser(Action):
    def name(self) -> Text:
        return "action_greet_user"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message("Hello! How can I help you today?")

        return []
    
class ActionOfferOptions(Action):
    def name(self) -> Text:
        return "action_offer_options"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        buttons = [
            {"payload": "/hindu_marriage", "title": "Case Study"},
            {"payload": "/request_lawyer", "title": "Lawyer Information"},
            {"payload": "/consumer_rights", "title": "General Question"}
        ]

        message = "Please select an option:"
        dispatcher.utter_message(text=message, buttons=buttons, ignore_text=True)
        
        return []
    
class ActionOfferStateOptions(Action):
    def name(self) -> Text:
        return "action_ask_state"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        buttons = []

        for state in states:
                buttons.append({"payload": state, "title": state}) 

        message = "Which state should the lawyer belong to?"
        dispatcher.utter_message(text=message, buttons=buttons, ignore_text=True)

        return []
    
class ActionOfferCOPOptions(Action):
    def name(self) -> Text:
        return "action_ask_court_of_practice"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        state = tracker.get_slot("state")

        buttons = [
            {"payload": "district", "title": "District"},
            {"payload": "high", "title": state + " High"},
            {"payload": "supreme", "title": "Supreme"}
        ]

        message = "What court should the lawyer practice in?"
        dispatcher.utter_message(text=message, buttons=buttons, ignore_text=True)

        return []

class ValidateLawyerForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_lawyer_form"
        
    def validate_state(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `state` value."""
        if slot_value in states:
            return {"state": slot_value}
        else:
            dispatcher.utter_message(text="Incorrect option for state.")
            return {"state": None}
        
    def validate_court_of_practice(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `court_of_practice` value."""
        if slot_value in ["district", "high", "supreme"]:
            return {"court_of_practice": slot_value}
        else:
            dispatcher.utter_message(text="Incorrect option for cop.")
            return {"court_of_practice": None}
        
class ValidatePredefinedSlots(ValidationAction):    
    def validate_options(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `options` value."""
        print(slot_value)
        if slot_value in ["/consumer_rights", "/request_lawyer", "/hindu_marriage"]:
            return {"options": slot_value}
        else:
            dispatcher.utter_message(text="Incorrect option.")
            return {"options": None}