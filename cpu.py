import json

import psutil

cpu_usage = { "cpu_usage" :
    psutil.cpu_percent(interval=1)
}

cpu=json.dumps(cpu_usage)


print(cpu)
