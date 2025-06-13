from django.db import models
import csv
from datetime import datetime
from django.conf import settings
import os

# 8-1-3
class Voter(models.Model):
    '''
    Model for each voter
    '''
    # Voter info
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    street_number = models.CharField(max_length=10)
    street_name = models.CharField(max_length=100)
    apartment_number = models.CharField(max_length=20, blank=True, null=True)
    zip_code = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    date_of_registration = models.DateField()
    party_affiliation = models.CharField(max_length=2)
    precinct_number = models.CharField(max_length=10)
    # Election participation
    v20state = models.CharField(max_length=10)
    v21town = models.CharField(max_length=10)
    v21primary = models.CharField(max_length=10)
    v22general = models.CharField(max_length=10)
    v23town = models.CharField(max_length=10)
    voter_score = models.IntegerField()

    def __str__(self):
        '''Return string representation of model instance'''
        return f"{self.first_name} {self.last_name} ({self.precinct_number})"
    
# 8-1-4
def load_data():
    '''Loads data from csv into django'''
    # filepath = os.path.join(settings.BASE_DIR, 'newton_voters.csv') #og
    # with open(filepath, newline='', encoding='utf-8') as csvfile:
    #     reader = csv.DictReader(csvfile)
    #     for row in reader:
    #         Voter.objects.create(
    #             last_name=row['Last Name'],
    #             first_name=row['First Name'],
    #             street_number=row['Residential Address - Street Number'],
    #             street_name=row['Residential Address - Street Name'],
    #             apartment_number=row.get('Residential Address - Apartment Number') or None,
    #             zip_code=row['Residential Address - Zip Code'],
    #             date_of_birth=datetime.strptime(row['Date of Birth'], '%Y-%m-%d').date(),
    #             date_of_registration=datetime.strptime(row['Date of Registration'], '%Y-%m-%d').date(),
    #             party_affiliation=row['Party Affiliation'],
    #             precinct_number=row['Precinct Number'],
    #             v20state=row['v20state'] == '1',
    #             v21town=row['v21town'] == '1',
    #             v21primary=row['v21primary'] == '1',
    #             v22general=row['v22general'] == '1',
    #             v23town=row['v23town'] == '1',
    #             voter_score=int(row['voter_score'])
    #         )
    # Voter.objects.all().delete()
    
    filename = '/Users/jaylinstarlinganaway/Desktop/django/newton_voters.csv' # new
    f = open(filename) # open file

    f.readline() # discard headers

    for line in f:
        line = f.readline().strip()
        fields = line.split(',')

        try:
            voter = Voter(last_name=fields[1],
                            first_name=fields[2],
                            street_number=fields[3],
                            street_name=fields[4],
                            apartment_number=fields[5],
                            zip_code=fields[6],
                            date_of_birth=fields[7],
                            date_of_registration=fields[8],
                            party_affiliation=fields[9],
                            precinct_number=fields[10],
                            v20state=fields[11],
                            v21town=fields[12],
                            v21primary=fields[13],
                            v22general=fields[14],
                            v23town=fields[15],
                            voter_score=fields[16],
                )
            voter.save()
            print(f'Created voter: {voter}')
        except:
            print(f"Skipped: {fields}")
    
    print(f"Done. Created {len(Voter.objects.all())} Results")
    # read entire file
    # for line in f:
    #     line = f.readline().strip()
    #     fields = line.split(',')
    #     try:
            # print(fields)
            # for j in range(len(fields)):
            #     print(f'fields[{j}] = {fields[j]}')
            # fields[0] = 10KSA1343001
            # fields[1] = KIGGEN
            # fields[2] = SHEILA
            # fields[3] = 193
            # fields[4] = OAK ST
            # fields[5] = 103E
            # fields[6] = 02464
            # fields[7] = 1943-10-13
            # fields[8] = 2016-02-10
            # fields[9] = D 
            # fields[10] = 1
            # fields[11] = TRUE
            # fields[12] = TRUE
            # fields[13] = FALSE
            # fields[14] = TRUE
            # fields[15] = FALSE
            # fields[16] = 3

        #     voter = Voter(last_name=fields[0],
        #                 first_name=fields[1],
        #                 street_number=fields[2],
        #                 street_name=fields[3],
        #                 apartment_number=fields[4],
        #                 zip_code=fields[5],
        #                 date_of_birth=fields[6],
        #                 date_of_registration=fields[7],
        #                 party_affiliation=fields[8],
        #                 precinct_number=fields[9],
        #                 v20state=fields[10],
        #                 v21town=fields[11],
        #                 v21primary=fields[12],
        #                 v22general=fields[13],
        #                 v23town=fields[14],
        #                 voter_score=fields[15],
        #     )
        #     voter.save() # commit voter to database
        #     print(f'Created result {voter}.')

        # except:
        #     print(f"Skipped: {fields}")


    