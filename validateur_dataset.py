
# Function validateur_dataset is used to validate the dataset creation form
def validateur_dataset(id=None,name=None,age=None,gendre=None):
    errors = []
    print(id,name,age,gendre)
    if(id is None or id.isdigit() == False):
        # send error message
        errors.append("Id must be a number and not empty")
        
    if(name is None or name.isalpha() == False):
        # send error message
        errors.append("Name must be a string and not empty")
        
    if(age is None or age.isdigit() == False):
        # send error message
        errors.append("Age must be a number and not empty")
        
    if(gendre is None or gendre not in ['MAN','WOMEN']):
        # send error message
        errors.append("Gendre is required and not empty")
        
    return errors