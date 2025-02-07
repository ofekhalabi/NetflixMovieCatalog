import boto3
# Initialize DynamoDB client with a specific AWS region
client = boto3.client('dynamodb', region_name='eu-north-1')  #

# Perform scan operation to retrieve all items
data_tv_response = client.scan(TableName='ofekh-netflix-movie-tv')
data_movies_response = client.scan(TableName='ofekh-netflix-catalog-movies')

# Extract the items from the response
items_tv = data_tv_response.get('Items', [])
items_movies = data_movies_response.get('Items', [])

# Convert items from DynamoDB format to a standard JSON-like structure
def dynamodb_to_json(dynamodb_item):
    json_item = {}
    for key, value in dynamodb_item.items():
        # Extracting the actual values from DynamoDB format
        if 'S' in value:
            json_item[key] = value['S']
        elif 'N' in value:
            json_item[key] = float(value['N']) if '.' in value['N'] else int(value['N'])
        elif 'BOOL' in value:
            json_item[key] = value['BOOL']
        elif 'L' in value:
            json_item[key] = [dynamodb_to_json(v) for v in value['L']]
        elif 'M' in value:
            json_item[key] = dynamodb_to_json(value['M'])
        elif 'NS' in value:
            json_item[key] = [int(n) for n in value['NS']]
        elif 'SS' in value:
            json_item[key] = value['SS']
        else:
            json_item[key] = None  # Handle unexpected cases
    return json_item

# Convert all items to a dictionary with a unique key
def convert_list_to_dict(items, key_field):
    data_dict = {}
    for item in items:
        json_item = dynamodb_to_json(item)
        key_value = json_item.get(key_field)
        if key_value:
            data_dict[key_value] = json_item  # Use key_field as dictionary key
    return data_dict


# Choose a field to be the dictionary key (change "id" to the actual key field in your table)
data_tv = convert_list_to_dict(items_tv, key_field="id")
data_movies = convert_list_to_dict(items_movies, key_field="id")


