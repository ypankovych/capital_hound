import csv

class CsvReader:
    
   def __init__(self, file_name, method='r'):
       self.file_obj = open(file_name, method)

   def __enter__(self):
       return csv.DictReader(self.file_obj)

   def __exit__(self, type, value, traceback):
       self.file_obj.close()