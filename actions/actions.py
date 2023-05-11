from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction, ValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict
from sklearn.metrics.pairwise import cosine_similarity
from oauth2client.service_account import ServiceAccountCredentials
from transformers import LongformerTokenizer, LongformerModel

import csv
csv.field_size_limit(100000000)

import gspread
import numpy as np
import re
import ast
import json

# Load the Longformer model and tokenizer
tokenizer = LongformerTokenizer.from_pretrained('allenai/longformer-base-4096')
model = LongformerModel.from_pretrained('allenai/longformer-base-4096')


scope = ['https://www.googleapis.com/auth/spreadsheets']

credentials_path = 'C:/Users/Esha Srivastav/Desktop/dev/fyp/rasa-fyp-a5e02f110091.json'

credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)

# Google sheets id for Lawyer Information
spreadsheet_id = '1HZ6FwP0u_zT4pbgFWusInln7p1Nmp6H388jsDsuBq6o' 

client = gspread.authorize(credentials)

# Open the worksheet for Lawyer Information
worksheet = client.open_by_key(spreadsheet_id).sheet1

# Read the data from the worksheet
data = worksheet.get_all_records()

from nltk.stem import PorterStemmer 
from nltk.tokenize import word_tokenize
stemmer = PorterStemmer()
 
# stem words in the list of tokenized words
def stem_words(keywords):
    stems = [stemmer.stem(word) for word in keywords]
    return stems

from difflib import get_close_matches

def are_all_similar_words_in_set(input_words, word_set, i):
    # Find the similar words in the word set for each input word
    similar_words = [get_close_matches(word, word_set, n=1, cutoff=0.8)[0]
                     for word in input_words
                     if get_close_matches(word, word_set, n=1, cutoff=0.8)]
    
    # print(str(i) + " " + str(similar_words))

    return (len(similar_words)/len(input_words) > 0)

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

doc_embeddings = []

# def read_cases_file(file_path):
#     with open(file_path, 'r') as file:
#         csv_reader = csv.reader(file)
#         csv_reader = next(csv_reader)  # Skip the header row if present
#         for row in csv_reader:
#             # print(row[3])
#             embedding = re.split(r',\s+', row[3])
#             embedding = re.split(r',\s+', row[3])
#             embedding_list = []
#             for value in embedding:
#                 if value != '':
#                     try:
#                         if 'e' in value or 'E' in value:
#                             embedding_list.append(float(value))
#                         else:
#                             embedding_list.append(float(value.replace(',', '')))
#                     except ValueError:
#                         pass

#             doc_embeddings.append(embedding_list)
    
#     print(doc_embeddings)

case_names = []

def read_cases_file(file_path):
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        # print(csv_reader[1][3])
        for row in csv_reader:
            if(row[3] != "Word embeddings"):
                embedding = ast.literal_eval(row[3])
                doc_embeddings.append(embedding)
                case_names.append(row[0])

class ActionGreetUser(Action):
    def name(self) -> Text:
        return "action_greet_user"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message("Hello! How can I help you today?")

        return []

class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_request_option"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hi. Welcome to our chatbot!\n")

        return []   

class SubmitLawyerInfo(Action):
    def name(self):
        return "action_submit_lawyer_form"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
                     
        state = tracker.get_slot("state")
        type_of_case = tracker.get_slot("type_of_case")

        # To check whether lawyer data for given requirement exists or not in the csv file
        flag = False 

        for row in data:
            if state == "supreme":
                if row['court of practice'].find(state) != -1 and (row['area of practice'].find(type_of_case) != -1 or type_of_case == "none"):
                    if row['address'] == "":
                        dispatcher.utter_message(text=f"Lawyer Name: {row['name']} \nLawyer State: {row['state']} \nAddress: Not Available")
                    else:
                        dispatcher.utter_message(text=f"Lawyer Name: {row['name']} \nLawyer State: {row['state']} \nAddress: {row['address']}")
                    flag = True
            elif state == "none":
                if row['area of practice'].find(type_of_case) != -1:
                    if row['address'] == "":
                        dispatcher.utter_message(text=f"Lawyer Name: {row['name']} \nLawyer State: {row['state']} \nAddress: Not Available")
                    else:
                        dispatcher.utter_message(text=f"Lawyer Name: {row['name']} \nLawyer State: {row['state']} \nAddress: {row['address']}")
                    flag = True
            else:
                if row['state'].find(state) != -1 and (row['area of practice'].find(type_of_case) != -1 or type_of_case == "none"):
                    if row['address'] == "":
                        dispatcher.utter_message(text=f"Lawyer Name: {row['name']} \nLawyer State: {row['state']} \nAddress: Not Available")
                    else:
                        dispatcher.utter_message(text=f"Lawyer Name: {row['name']} \nLawyer State: {row['state']} \nAddress: {row['address']}")
                    flag = True
        
        if not flag:
            dispatcher.utter_message("No data found")

        return [SlotSet("state", None), SlotSet("type_of_case", None), SlotSet("keywords", None)]
    
class SubmitCaseStudyInfo(Action):

    def name(self) -> Text:
        return "action_submit_case_study_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        file_path = 'FinalJudgement_cases - 2.csv'
        read_cases_file(file_path)

        keywords = tracker.get_slot("keywords")
        
        flag = False 

        similarity_scores = []            

        if keywords != None:
            keywords = list(keywords.split(", "))
            [x.lower() for x in keywords]
            stem_words(keywords)  
            encoded = tokenizer.encode_plus(keywords, padding=True, truncation=True, return_tensors='pt')
            input_ids = encoded['input_ids']  # Remove the batch dimension
            attention_mask = encoded['attention_mask']  # Remove the batch dimension
            outputs = model(input_ids, attention_mask=attention_mask)
            keywords_embedding = outputs.last_hidden_state[:, 0, :].detach().numpy()

            # print(keywords_embedding[0])
            key_reshaped = np.repeat(np.array(keywords_embedding[0]).reshape(1, -1), len(doc_embeddings), axis=0)

            # Flatten innermost lists in Y
            docs_flat = [item for sublist in doc_embeddings for item in sublist]

            # # Convert Y_flat into a NumPy array
            # docs_array = np.array(docs_flat)

            # # Reshape Y_array
            # docs_reshaped = docs_array.reshape(len(doc_embeddings), -1)


            # print(keywords_embedding)

            # similarity_scores = cosine_similarity(doc_embeddings, keywords_embedding)
            

            # print(keywords_embedding[0])           

            # for key_embedding in keywords_embedding:
            score = cosine_similarity(key_reshaped, docs_flat)
            similarity_scores.append(score)                

            # print(similarity_scores)

            # Determine if document contains user keywords
            threshold = 0.8  # Set your desired similarity threshold

            for i, similarity_score in enumerate(similarity_scores):
                similarity_scores_list = similarity_score.tolist()[0]
                print(similarity_scores_list)
                if any(score >= threshold for score in similarity_scores_list):
                    print(case_names[i] + " contains user keywords.")

        if not flag:
            dispatcher.utter_message("No data found")

        return [SlotSet("state", None), SlotSet("type_of_case", None), SlotSet("opt_keywords", None), SlotSet("keywords", None)]
    
class ActionOfferOptions(Action):
    def name(self) -> Text:
        return "action_offer_options"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        buttons = [
            {"payload": "/request_case_study", "title": "Case Study"},
            {"payload": "/request_lawyer", "title": "Lawyer Information"},
            {"payload": "/gen_questions", "title": "General Question"}
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

        buttons = [
            {"payload": "supreme", "title": "Supreme"},
            {"payload": "none", "title": "None"}
        ]
        
        for state in states:
            buttons.append({"payload": state, "title": state}) 

        message = "Which court should the case belong to? Type your state if not mentioned in the options."
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
            {"payload": "child custody", "title": "Child Custody"},
            {"payload": "none", "title": "None"}
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
        return updated_slots
        
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
        elif slot_value == "supreme":
            return {"state": slot_value}
        elif slot_value == "none":
            return {"state": slot_value}
        else:
            dispatcher.utter_message(text="Incorrect option for state.")
            return {"state": None}
        
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
        if tracker.slots.get("opt_keywords") == "no":
            updated_slots.remove("keywords")

        return updated_slots
    
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
        elif slot_value == "supreme":
            return {"state": slot_value}
        elif slot_value == "none":
            return {"state": slot_value}
        else:
            dispatcher.utter_message(text="Incorrect option for state.")
            return {"state": None}    
        
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
            dispatcher.utter_message(text="Incorrect option for type of case.")
            return {"type_of_case": None}

    def validate_opt_keywords(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `opt_keywords` value."""
        if slot_value in ["yes", "no"]:
            return {"opt_keywords": slot_value}
        else:
            dispatcher.utter_message(text="Incorrect option for opting keywords.")
            return {"opt_keywords": None}

class ActionHandleAffirmation(Action):
    def name(self) -> Text:
        return "action_handle_affirmation"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Do something in response to an affirmative response, e.g. confirm submission
        dispatcher.utter_message("Great, we will submit your form. Is there anything else I can help with?")
        return []