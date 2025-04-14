from flask import Flask, request, jsonify
import random
import boto3
import signal
import threading

app = Flask(__name__)

# Global readiness flag
is_ready = True

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


@app.route("/", methods=['GET'])
def home():
    return "Hi! This app is an API, there is no UI ;)"


@app.route('/discover')
def get_discover():
    """
    Find movies using over filters and sort options.
    """
    type_ = request.args.get('type')
    data = data_tv if type_ == 'tv' else data_movies
    genre_id = request.args.get('genre')

    if not genre_id:
        results = random.sample(list(data.values()), 20)
    else:
        results = []
        for item in data.values():
            if int(genre_id) in item['genre_ids']:
                results.append(item)
                if len(results) >= 20:
                    break  # stop searching after the first 20 items

    return jsonify(results)


@app.route('/updatePopularity', methods=['POST'])
def update_popularity():
    movie_id = request.json.get('movieId')
    new_popularity = request.json.get('popularity')

    if movie_id not in data_movies:
        return jsonify({'error': 'Movie Id value not provided or not found'}), 400

    if new_popularity is None:
        return jsonify({'error': 'Popularity value not provided'}), 400

    try:
        new_popularity = float(new_popularity)
    except ValueError:
        return jsonify({'error': 'Popularity value must be a float'}), 400

    data_movies[movie_id]['popularity'] = new_popularity

    return jsonify({'message': 'Popularity updated successfully', 'new_popularity': new_popularity}), 200


@app.route('/status')
def status():
    return 'OK'

@app.route("/ready")
def readiness_probe():
    if is_ready:
        return jsonify({"status": "ready"}), 200
    else:
        return jsonify({"status": "shutting down"}), 503

@app.route("/live")
def liveness_probe():
    return jsonify({"status": "alive"}), 200

def handle_sigterm(*args):
    global is_ready
    print("SIGTERM received, setting readiness to False")
    is_ready = False


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, handle_sigterm)
    app.run(port=8080, host='0.0.0.0')
