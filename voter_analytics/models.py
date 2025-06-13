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
    Voter.objects.all().delete()
    
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
    

    