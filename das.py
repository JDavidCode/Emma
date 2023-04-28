import json
import os


history = f'web_server\\json\\awdqdw.json'
if not os.path.exists(history):
    # Create the directory if it doesn't exist
    with open(history, 'w') as f:
        json.dump({}, f, indent=4)
        f.close()

with open(history, 'w') as f:
    dataset = {}
    for i in range(0, 20):
        dataset[f'{i}'] = 'doqnwdqpdwq'
    json = json.dumps(dataset, indent=4)
    f.write(json)
    f.close()
