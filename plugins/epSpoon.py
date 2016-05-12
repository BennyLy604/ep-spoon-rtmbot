crontable = []
outputs = []


def process_message(data):
    if 'eat' in data['text']:
        outputs.append([data['channel'], "Eat me."])
