import requests,re


def get_id(input):
    valid = True
    if '@' in input and 'soton.ac.uk' in input and ' ' not in input:   #Basic email validation, more rules could be added
        id = input.split('@')
        if len(id) == 2 and len(id[0])>0:   #Confirms there is only a single '@' and there is a user id entered
            return id[0]
    print("Invalid email, emails must be in the format '[id]@soton.ac.uk'")
    return 0


if __name__ == '__main__':
    email = input('Enter your email address: ')   #Get the email address for the request
    while get_id(email) == 0:   #Attempt to get the email address from the user until they enter an email address of the requested format
        email = input('Please try again: ')

    id = get_id(email)
    print(f'Your email is {email}, so your university ID is: {id}')
    url = "https://ecs.soton.ac.uk/people/"+id
    print(f'The created url is: {url}')
    try:
        req = requests.get(url)
        found = False
        if req.url != url:   #Check the old url has been successfully redirected
            page = req.text
            name_response = re.findall('title" content=".*"',page)
            if len(name_response) > 0:   #Checks there is a match for the expression
                name = name_response[0].split('"')[2]
                found = True

        if found:   #Checks that a name has been found
            print(f'Name is: {name}')
        else:
            print('Could not find a match')
    except Exception as e:
        print('Error: request failed')
    input('Press Enter to quit:')