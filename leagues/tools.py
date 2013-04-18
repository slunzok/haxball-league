from haxball.settings import MEDIA_ROOT

def create_schedule(list, rounds):
    """ 
    Create a schedule for the teams in the list and return it
    See http://stackoverflow.com/questions/1037057/how-to-automatically-generate-a-sports-league-schedule/1037156#1037156
    """
    s = []

    if len(list) % 2 == 1: list = list + ["BYE"]

    for i in range(rounds*(len(list)-1)):

        mid = len(list) / 2
        l1 = list[:mid]
        l2 = list[mid:]
        l2.reverse()    

        # Switch sides after each round
        if(i % 2 == 1):
            s = s + [ zip(l1, l2) ]
        else:
            s = s + [ zip(l2, l1) ]

        list.insert(1, list.pop())

    return s
    
def handle_uploaded_file(f, replay_name):
    """
    See https://docs.djangoproject.com/en/dev/topics/http/file-uploads/#handling-uploaded-files
    """
    with open(MEDIA_ROOT+'replays/'+replay_name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
