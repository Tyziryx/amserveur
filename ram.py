import json

import psutil



ram = {"ram" : psutil.virtual_memory().percent}


resultat = json.dumps(ram)


print(resultat)