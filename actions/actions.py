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
import csv
import gspread
import asyncio

from oauth2client.service_account import ServiceAccountCredentials

# import tensorflow as tf
# from transformers import BertTokenizer, TFBertModel
from sklearn.metrics.pairwise import cosine_similarity

# tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
# model = TFBertModel.from_pretrained('bert-base-uncased')

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

from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
stemmer = PorterStemmer()
 
# stem words in the list of tokenized words
def stem_words(keywords):
    stems = [stemmer.stem(word) for word in keywords]
    print("here" + str(stems))
    return stems

states = set()

for row in data:
    states.add(row['state'])

def read_csv_file(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        data = []
        for row in reader:
            data.append(row)
    return data

class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_request_option"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Enter option: \n1. Case Study \n2. Lawyer Information \n3. General Question \n")

        return []   

class SubmitLawyerInfo(Action):
    def name(self):
        return "action_submit_lawyer_form"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
               
        type_of_court = tracker.get_slot("type_of_court")        
        state = tracker.get_slot("state")
        type_of_case = tracker.get_slot("type_of_case")

        # To check whether lawyer data for given requirement exists or not in the csv file
        flag = False 

        for row in data:
            if type_of_court == "supreme":
                if row['court of practice'].find(type_of_court) != -1 and row['area of practice'].find(type_of_case) != -1:
                    if row['address'] == "":
                        dispatcher.utter_message(text=f"Lawyer Name: {row['name']} \nLawyer State: {row['state']} \nAddress: Not Available")
                    else:
                        dispatcher.utter_message(text=f"Lawyer Name: {row['name']} \nLawyer State: {row['state']} \nAddress: {row['address']}")
                    flag = True
            else:
                if row['state'] == state and row['court of practice'].find(type_of_court) != -1 and row['area of practice'].find(type_of_case) != -1:
                    if row['address'] == "":
                        dispatcher.utter_message(text=f"Lawyer Name: {row['name']} \nLawyer State: {row['state']} \nAddress: Not Available")
                    else:
                        dispatcher.utter_message(text=f"Lawyer Name: {row['name']} \nLawyer State: {row['state']} \nAddress: {row['address']}")
                    flag = True
        
        if not flag:
            dispatcher.utter_message("No data found")

        return [SlotSet("state", None), SlotSet("type_of_court", None), SlotSet("type_of_case", None)]
    
class SubmitCaseStudyInfo(Action):

    def name(self) -> Text:
        return "action_submit_case_study_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        file_path = 'C:/Users/Esha Srivastav/Desktop/dev/fyp/Judgement_cases.csv'
        data = read_csv_file(file_path)

        type_of_court = tracker.get_slot("type_of_court")        
        state = tracker.get_slot("state") 
        type_of_case = tracker.get_slot("type_of_case")
        keywords = tracker.get_slot("keywords") 

        if keywords != None:
            [x.lower() for x in keywords]
            print(keywords)   
            stem_words(keywords)     

        flag = False 

        for row in data:
            if keywords != None:
                res = [word for word in keywords if (word in row[2])]
                if type_of_court == "supreme":
                    if row[2].find(type_of_court) != -1 or row[2].find(type_of_case) != -1 or res == True:
                        dispatcher.utter_message(text=f"Judgement Case Name: {row[0]} \nCase Link: {row[1]}")
                        flag = True
                elif row[2].find(state) != -1 or row[2].find(type_of_court) != -1 or row[2].find(type_of_case) != -1 or res == True:
                        dispatcher.utter_message(text=f"Judgement Case Name: {row[0]} \nCase Link: {row[1]}")
                        flag = True
            else:
                if type_of_court == "supreme":
                    if row[2].find(type_of_court) != -1 or row[2].find(type_of_case) != -1:
                        dispatcher.utter_message(text=f"Judgement Case Name: {row[0]} \nCase Link: {row[1]}")
                        flag = True
                elif row[2].find(state) != -1 or row[2].find(type_of_court) != -1 or row[2].find(type_of_case) != -1:
                        dispatcher.utter_message(text=f"Judgement Case Name: {row[0]} \nCase Link: {row[1]}")
                        flag = True

        if not flag:
            dispatcher.utter_message("No data found")

        return [SlotSet("state", None), SlotSet("type_of_court", None), SlotSet("type_of_case", None), SlotSet("opt_keywords", None), SlotSet("keywords", None)]
    
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
            {"payload": "/request_case_study", "title": "Case Study"},
            {"payload": "/request_lawyer", "title": "Lawyer Information"},
            {"payload": "/consumer_rights", "title": "General Question"}
        ]

        message = "Please select an option:"
        dispatcher.utter_message(text=message, buttons=buttons, ignore_text=True)
        
        return []
    
class ActionOfferTOCOptions(Action):
    def name(self) -> Text:
        return "action_ask_type_of_court"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        buttons = [
            {"payload": "district", "title": "District"},
            {"payload": "high", "title":"High"},
            {"payload": "supreme", "title": "Supreme"}
        ]

        message = "What type of court is your case in?"
        dispatcher.utter_message(text=message, buttons=buttons)

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

        message = "Which state should the case belong to?"
        dispatcher.utter_message(text=message, buttons=buttons)

        return []
    
class ActionOfferTOCaOptions(Action):
    def name(self) -> Text:
        return "action_ask_type_of_case"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        buttons = [
            {"payload": "criminal", "title": "Criminal"},
            {"payload": "civil", "title": "Civil"},
            {"payload": "divorce", "title": "Divorce"},
            {"payload": "sexual harassment", "title": "Sexual Harassment"},
            {"payload": "child custody", "title": "Child Custody"}
        ] 

        message = "What type of case do you have?"
        dispatcher.utter_message(text=message, buttons=buttons)

        return []

class ActionOfferOptKeywordsOptions(Action):
    def name(self) -> Text:
        return "action_ask_opt_keywords"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        buttons = [
            {"payload": "yes", "title": "Yes"},
            {"payload": "no", "title": "No"}
        ] 

        message = "Do you want to add any keywords?"
        dispatcher.utter_message(text=message, buttons=buttons)

        return []
    
class ActionOfferKeywordsOptions(Action):
    def name(self) -> Text:
        return "action_ask_keywords"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
            message = "Mention additional keywords (comma separated)"
            dispatcher.utter_message(text=message)
            text_data = tracker.latest_message.get("text")
            keywords = list(text_data.split(","))    
            return [SlotSet("keywords", keywords)]
    
class ValidateLawyerForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_lawyer_form"
    
    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[Text]:
        updated_slots = domain_slots.copy()
        if tracker.slots.get("type_of_court") == "supreme":
            updated_slots.remove("state")

        return updated_slots
        
    def validate_state(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `state` value."""
        print(slot_value)
        if slot_value in states:
            return {"state": slot_value}
        else:
            dispatcher.utter_message(text="Incorrect option for state.")
            return {"state": None}

    def validate_type_of_court(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `type_of_court` value."""
        if slot_value in ["district", "high", "supreme"]:
            return {"type_of_court": slot_value}
        else:
            dispatcher.utter_message(text="Incorrect option for toc.")
            return {"type_of_court": None}
        
    def validate_type_of_case(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `type_of_case` value."""
        if isinstance(slot_value, str):
            return {"type_of_case": slot_value}
        else:
            dispatcher.utter_message(text="Incorrect option for tocc.")
            return {"type_of_case": None}
        
class ValidateCaseStudyForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_case_study_form"
    
    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[Text]:
        updated_slots = domain_slots.copy()
        if tracker.slots.get("type_of_court") == "supreme":
            updated_slots.remove("state")
        if tracker.slots.get("opt_keywords") == "no":
            updated_slots.remove("keywords")

        return updated_slots
    
#     def validate_state(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         """Validate `state` value."""
#         if slot_value in states:
#             return {"state": slot_value}
#         else:
#             dispatcher.utter_message(text="Incorrect option for state.")
#             return {"state": None}
        
#     def validate_type_of_court(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         """Validate `type_of_court` value."""
#         if slot_value in ["district", "high", "supreme"]:
#             return {"type_of_court": slot_value}
#         else:
#             dispatcher.utter_message(text="Incorrect option for toc.")
#             return {"type_of_court": None}
        
#     def validate_type_of_case(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         """Validate `type_of_case` value."""
#         if isinstance(slot_value, str):
#             return {"type_of_case": slot_value}
#         else:
#             dispatcher.utter_message(text="Incorrect option for tocc.")
#             return {"type_of_case": None}
        
# class ValidatePredefinedSlots(ValidationAction):    
#     def validate_options(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         """Validate `options` value."""
#         print(slot_value)
#         if slot_value in ["/request_case_study", "/request_lawyer", "/hindu_marriage"]:
#             return {"options": slot_value}
#         else:
#             dispatcher.utter_message(text="Incorrect option.")
#             return {"options": None}

class ActionHandleAffirmation(Action):
    def name(self) -> Text:
        return "action_handle_affirmation"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Do something in response to an affirmative response, e.g. confirm submission
        dispatcher.utter_message("Great, we will submit your form. Is there anything else I can help with?")
        return []
