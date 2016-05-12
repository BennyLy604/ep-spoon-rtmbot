crontable = []
outputs = []


def process_message(data):
    if (data['text'].contains('eat')) :
        outputs.append([data['channel'], "Eat me."])
