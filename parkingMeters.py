import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import xmljson
from json import dumps

class example(dml.Algorithm):
    #contributor = 'alice_bob'
    #reads = []
    #writes = ['alice_bob.lost', 'alice_bob.found']
    
    contributor = 'emilyh23_yazhang'
    reads = []
    writes = ['emilyh23_yazhang.lost', 'emilyh23_yazhang.found']    
    
    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
        
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        #repo.authenticate('alice_bob', 'alice_bob')
        repo.authenticate('emilyh23_yazhang', 'emilyh23_yazhang')       
        
        filen = '../data/parking_meters.json'
        res = open(filen, 'r')
        r = json.load(res)
        repo.dropPermanent("parkingMeters")
        repo.createPermanent("parkingMeters")
        repo['emilyh23_yazhang.parkingMeters'].insert_many(r)   
        
        # x = longitude, y = latitude
        url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=42.35015281775182,-71.049828962808604&key=AIzaSyCZqcBDxeWDYJHJgj_77njtzSY6khsCtik'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        # r is a list        
        r = json.loads(response)        
        # s is a string
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropPermanent("geoCoding")
        repo.createPermanent("geoCoding")
        repo['emilyh23_yazhang.geoCoding'].insert_one(r) 

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}

    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
        Create the provenance document describing everything happening
        in this script. Each run of the script will generate a new
        document describing that invocation event.
        '''

         # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        #repo.authenticate('alice_bob', 'alice_bob')
        repo.authenticate('emilyh23_yazhang', 'emilyh23_yazhang')
        
        #doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        #doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/emilyh23_yazhang') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/emilyh23_yazhang') # The data sets are in <user>#<collection> format.
        
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        #doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')
        doc.add_namespace('bod', 'http://bostonopendata.boston.opendata.arcgis.com/') # boston open data
        doc.add_namespace('gma', 'https://developers.google.com/maps/') # google maps api

        this_script = doc.agent('alg:parkingMeters', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})

        resource = doc.entity('bod:wc8w-nujj', {'prov:label':'Parking Meters', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        this_run = doc.activity('log:a'+str(uuid.uuid4()), startTime, endTime, {prov.model.PROV_TYPE:'ont:Computation', 'ont:Query':'?accessType=DOWNLOAD'})
        doc.wasAssociatedWith(this_run, this_script)
        doc.used(this_run, resource, startTime)

        '''
        this_script = doc.agent('alg:alice_bob#example', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:wc8w-nujj', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_found = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_lost = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_found, this_script)
        doc.wasAssociatedWith(get_lost, this_script)
        doc.usage(get_found, resource, startTime, None,
                {prov.model.PROV_TYPE:'ont:Retrieval',
                 'ont:Query':'?type=Food+Found&$select=type,latitude,longitude,OPEN_DT'
                }
            )
        doc.usage(get_lost, resource, startTime, None,
                {prov.model.PROV_TYPE:'ont:Retrieval',
                 'ont:Query':'?type=Food+Lost&$select=type,latitude,longitude,OPEN_DT'
                }
            )
        lost = doc.entity('dat:alice_bob#lost', {prov.model.PROV_LABEL:'Animals Lost', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(lost, this_script)
        doc.wasGeneratedBy(lost, get_lost, endTime)
        doc.wasDerivedFrom(lost, resource, get_lost, get_lost, get_lost)
        found = doc.entity('dat:alice_bob#found', {prov.model.PROV_LABEL:'Animals Found', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(found, this_script)
        doc.wasGeneratedBy(found, get_found, endTime)
        doc.wasDerivedFrom(found, resource, get_found, get_found, get_found)
        '''       
        
        parkMeters = doc.entity('dat:parkMeters', {prov.model.PROV_LABEL:'parkMeters', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(parkMeters, this_script)
        #doc.wasGeneratedBy(parkMeters, get_lost, endTime)
        #doc.wasDerivedFrom(parkMeters, resource, get_lost, get_lost, get_lost)
        #don't delete -- need for later
        doc.wasGeneratedBy(parkMeters, this_run, endTime)
        doc.wasDerivedFrom(parkMeters, resource, this_run, this_run, this_run)
        
        geoCoding = doc.entity('dat:geoCoding', {prov.model.PROV_LABEL:'geoCoding', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(geoCoding, this_script)
        #doc.wasGeneratedBy(parkMeters, get_lost, endTime)
        #doc.wasDerivedFrom(parkMeters, resource, get_lost, get_lost, get_lost)
        #don't delete -- need for later
        doc.wasGeneratedBy(geoCoding, this_run, endTime)
        doc.wasDerivedFrom(geoCoding, resource, this_run, this_run, this_run)
                        
        repo.record(doc.serialize()) # Record the provenance document.
        repo.logout()

        return doc

example.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof