from db import *
from dim import *


class MainETL():
    # list of columns need to be replaced
    def __init__(self) -> None:
        self.drop_columns = []
        self.dimension_tables = []

    # Step 1: Extract data from source
    def extract(self, csv_file="ETL_Example_Data.csv"):
        print(f'Step 1: Extracting data from csv file')
        self.fact_table = df
        print(f'We find {len(self.fact_table.index)} rows and {len(self.fact_table.columns)} columns in csv file: {csv_file}')
        print(f'Step 1 finished')

    # Step 2: Transform data to fit the star schema model
    def transform(self):
        # transform data types
        self.fact_table[['travelallowanceRate']] = self.fact_table[['travelallowanceRate']].astype(float)
        int_cols = ['travel distance', 'weatehr allowance', 'work hours', 'job hourly']
        self.fact_table[int_cols] = self.fact_table[int_cols].astype(int)
        self.fact_table[['weather', 'temperature']] = self.fact_table[['weather', 'temperature']].astype(str)

        # fetch staff dimension table
        dim_staff = DimStaff()
        self.drop_columns += dim_staff.columns
        self.dimension_tables.append(dim_staff)

        # fetch date dimension table
        dim_date = DimDate()
        self.drop_columns += dim_date.columns
        new_dim =  dim_date.dimension_table[['date']]

        # convert the date column to datetime format
        new_dim['date'] = pd.to_datetime(new_dim['date'], format='%d/%m/%Y')
        self.fact_table['date'] = pd.to_datetime(self.fact_table['date'], format='%d/%m/%Y')

        # extract the month number and convert it to month name
        new_dim['date'] = new_dim['date'].dt.month_name()
        self.fact_table['date'] = self.fact_table['date'].dt.month_name()
        new_dim = new_dim.drop_duplicates()

        # modify primary key for date dimension table
        new_dim[f'Date_id'] = range(1, len(new_dim) + 1)
        dim_date.dimension_table = new_dim
        self.dimension_tables.append(dim_date)

        # fetch maintenance job dimension table
        dim_job = DimMaintenanceJob()
        self.drop_columns += dim_job.columns
        self.dimension_tables.append(dim_job)

        # fetch department dimension table
        dim_department = DimDepartment()
        self.drop_columns += dim_department.columns
        self.dimension_tables.append(dim_department)

        # fetch travel dimension table
        dim_travel_allowance = DimTravelAllowancePolicy()
        self.drop_columns += dim_travel_allowance.columns
        self.dimension_tables.append(dim_travel_allowance)

        # fetch weather dimension table
        dim_weather_allowance = DimWeatherAllowancePolicy()
        self.drop_columns += dim_weather_allowance.columns

        new_weather = dim_weather_allowance.dimension_table[['weather', 'temperature', 'weatehr allowance']]
        new_weather.loc[new_weather['weather'] == "heavy rain", 'weather'] = "rain"
        self.fact_table.loc[self.fact_table['weather'] == "heavy rain", 'weather'] = "rain"

        new_weather = new_weather.drop_duplicates()

        # Create new foreign key column
        new_weather['WeatherAllowancePolicy_id'] = range(1, len(new_weather) + 1)
        dim_weather_allowance.dimension_table = new_weather
        self.dimension_tables.append(dim_weather_allowance)

        # fetch holiday dimension table
        dim_holiday = ModelAbstract()
        dim_holiday.dimension_generator('Holiday', ['isholiday'])
        self.drop_columns += dim_holiday.columns
        self.dimension_tables.append(dim_holiday)

        # get Travel Allowance amount
        travel_allowance_amount = self.fact_table['travel distance'] * self.fact_table['travelallowanceRate']
        self.fact_table['travel allowance amount'] = travel_allowance_amount

        # get Weather Allowance Amount
        weather_allowance_amount = self.fact_table['weatehr allowance']
        self.fact_table['weather allowance amount'] = weather_allowance_amount

        # get Hourly Work Payment
        work_payment = self.fact_table['work hours'] * self.fact_table['job hourly']
        self.fact_table['work payment'] = work_payment

        # get Total Payment
        self.fact_table['total pay this job'] = work_payment + travel_allowance_amount + weather_allowance_amount

        # replace columns in fact table with respective foreign keys
        for dim in self.dimension_tables:
            self.fact_table = pd.merge(self.fact_table, dim.dimension_table, on=dim.columns, how='left')
        self.fact_table = self.fact_table.drop(columns=self.drop_columns)

        print(f'Step 2 finished')

    # Step 3: Load data into Azure SQL Database
    def load(self):
        # Load dimension tables first
        for table in self.dimension_tables:
            table.load()

        # Load fact table and create foreign key constraints
        with engine.connect() as con:
            trans = con.begin()
            self.fact_table['Total_Pay_Fact_id'] = range(1, len(self.fact_table) + 1)
            database.upload_dataframe_sqldatabase(f'Total_Pay_Fact', blob_data=self.fact_table)

            self.fact_table.to_csv('./data/Total_Pay_Fact.csv')

            fact_qt = sql_table('Total_Pay_Fact')
            for table in self.dimension_tables:
                dim_qt = sql_table(f'{table.name}_dim')
                con.execute(text(
                    f'ALTER TABLE {fact_qt} WITH NOCHECK ADD CONSTRAINT [FK_{table.name}_dim] '
                    f'FOREIGN KEY ([{table.name}_id]) REFERENCES {dim_qt} ([{table.name}_id]) '
                    f'ON UPDATE CASCADE ON DELETE CASCADE;'
                ))
            trans.commit()

        print(f'Step 3 finished')

    # main loop to run the ETL process
    def mainLoop(self):
        # Step 1
        self.extract()
        # Step 2
        self.transform()
        # Step 3
        try:
            database.delete_sqldatabase('Total_Pay_Fact')
            self.load()
        except:
            self.load()

def main():
    # create an instance of MainETL
    main = MainETL()
    main.mainLoop()

if __name__ == '__main__':
    main()



