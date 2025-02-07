import boto3

# Initialize DynamoDB client
client = boto3.client('dynamodb')

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

# Convert all items to a JSON-friendly format
data_tv = [dynamodb_to_json(item) for item in items_tv]
data_movies = [dynamodb_to_json(item) for item in items_movies]

