import json
import zipfile
from io import TextIOWrapper
import csv

race_lookup = {
    "1": "American Indian or Alaska Native",
    "2": "Asian",
    "3": "Black or African American",
    "4": "Native Hawaiian or Other Pacific Islander",
    "5": "White",
    "21": "Asian Indian",
    "22": "Chinese",
    "23": "Filipino",
    "24": "Japanese",
    "25": "Korean",
    "26": "Vietnamese",
    "27": "Other Asian",
    "41": "Native Hawaiian",
    "42": "Guamanian or Chamorro",
    "43": "Samoan",
    "44": "Other Pacific Islander"
}

class Applicant:
    def __init__(self, age, race):
        self.age = age
        self.race = set()
        if isinstance(race, str):
            race = [race]
        for r in race:
            if r in race_lookup:
                self.race.add(race_lookup[r])
                
    def __repr__(self):
        race_list = sorted(self.race)
        return f"Applicant('{self.age}', {race_list})"
    
    def lower_age(self):
        age_str = self.age.replace("<", "").replace(">", "")
        lower_age = age_str.split("-")[0]
        return int(lower_age)
    
    def __lt__(self, other):
        return self.lower_age() < other.lower_age()
    
    
class Loan:
    def __init__(self, values):
        # loan amount - float
        self.loan_amount = self.float_extract(values["loan_amount"])
        # property value - float
        self.property_value = self.float_extract(values["property_value"])
        # interest rate - float
        self.interest_rate = self.float_extract(values["interest_rate"])
        # applicants - Applicant object
        self.applicants = []
        
        primary_applicant = Applicant(
            age=values["applicant_age"], 
            race=self.extract_races(values, prefix="applicant_race-")
        )
        self.applicants.append(primary_applicant)
        
        if values["co-applicant_age"] != "9999":
            co_applicant = Applicant(
                age=values["co-applicant_age"], 
                race=self.extract_races(values, prefix="co-applicant_race-")
            )
            self.applicants.append(co_applicant)

    def float_extract(self, string):
        if string == "NA" or string == "Exempt":
            return -1
        else:
            return float(string)
            
    def extract_races(self, values, prefix):
        races = []
        for i in range(1, 6):
            race_code = values.get(f"{prefix}{i}", "")
            if race_code:
                races.append(race_code)
        return races
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return f"<Loan: {self.interest_rate}% on ${self.loan_amount} with {len(self.applicants)} applicant(s)>"
    
    def yearly_amounts(self, yearly_payment):
        
        amt = self.loan_amount
        # converting the percentage to decimal
        rate = self.interest_rate / 100
        
        while amt > 0:
            yield amt
            amt += amt * rate
            amt -= yearly_payment
            # if amt < 0:
            #     amt = 0
    
with open('banks.json', 'r') as f:
    bank_data = json.load(f)
    
class Bank:
    # init should check that the given name appears in the banks.json file
    def __init__(self, name):
        # checking if the name appears
        matching_bank = None
        for bank in bank_data:
            if bank["name"] == name:
                matching_bank = bank
                break

        if matching_bank is None:
            raise ValueError(f"Bank '{name}' not found in banks.json")
            
        self.name = name
        self.lei = matching_bank["lei"]
        self.loan_list = []
        
        # Process the CSV data from wi.zip
        with zipfile.ZipFile('wi.zip', 'r') as z:
            with z.open('wi.csv') as csvfile:
                reader = csv.DictReader(TextIOWrapper(csvfile, 'utf-8'))
                for row in reader:
                    if row["lei"] == self.lei:
                        loan = Loan(row)
                        self.loan_list.append(loan)
                        
    def __len__(self):
        return len(self.loan_list)
    
    def __getitem__(self, index):
        return self.loan_list[index]
    
