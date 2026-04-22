from db import *

# raw file's blob name in Azure Storage
blob_name = "ETL_Example_Data.csv"

# intialize AzureDB
database = AzureDB()

# access the container and read the csv file
database.access_container("test")
df = database.access_blob_csv(blob_name=blob_name)

class ModelAbstract():
    def __init__(self):
        self.columns = None
        self.dimension_table = None

    def dimension_generator(self, name:str, columns:list):
        dim = df[columns]
        dim = dim.drop_duplicates()

        # create primary key
        dim[f'{name}_id'] = range(1, len(dim) + 1)

        self.dimension_table = dim
        self.name = name
        self.columns = columns

    def load(self):
        if self.dimension_table is not None:
            # upload dimension table to data warehouse
            database.upload_dataframe_sqldatabase(f'{self.name}_dim', blob_data=self.dimension_table)

            # save dimension table as separate file
            self.dimension_table.to_csv(f'./data/{self.name}_dim.csv')
        else:
            print("Please create a dimension table first")

# staff dimension table
class DimStaff(ModelAbstract):
    def __init__(self):
        super().__init__()
        self.dimension_generator('Staff', ['Natural Key Staff ID', 'Name', 'Contact Phone', 'Home Address', "Email"])

# date dimension table
class DimDate(ModelAbstract):
    def __init__(self):
        super().__init__()
        self.dimension_generator('Date', ['date'])

# holiday dimension table
class DimDepartment(ModelAbstract):
    def __init__(self):
        super().__init__()
        self.dimension_generator('Department', ['Department'])

# maintenance job dimension table
class DimMaintenanceJob(ModelAbstract):
    def __init__(self):
        super().__init__()
        self.dimension_generator('MaintenanceJob', ['work type'])

# travel allowance policy dimension table
class DimTravelAllowancePolicy(ModelAbstract):
    def __init__(self):
        super().__init__()
        self.dimension_generator('TravelAllowancePolicy', ['vehicle type', 'travelallowanceRate'])

# weather allowance policy dimension table
class DimWeatherAllowancePolicy(ModelAbstract):
    def __init__(self):
        super().__init__()
        self.dimension_generator('WeatherAllowancePolicy', ['weather', 'temperature', 'weatehr allowance'])
