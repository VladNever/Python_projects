symbol_list = ['a', 'a', 0, 2, 2,'a']

def get_first_element(symbol_list):
    previous_element = None
    for element in symbol_list:
        if element == previous_element:
            return  previous_element
        else:
            previous_element = element
    return 'There are no repeating elements'

first_element = get_first_element(symbol_list)
print(first_element)
