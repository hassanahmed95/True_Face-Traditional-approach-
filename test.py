def removeDuplicates(string):
    result=[]
    eve = []
    for char in string:
        if char not in eve:
            print(char)
            eve.append(char)
            # result.append(char)
    return eve


data = removeDuplicates("data")
print( "".join(data))