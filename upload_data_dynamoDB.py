import boto3
import json
client = boto3.client('dynamodb')
# Sample data (with multiple movies in old format)
data = {
    "insert your json data"
}

# Function to convert the dictionary to the new format
def transform_data(movie_data):
    return {
        "adult": {'BOOL': movie_data["adult"]},
        "backdrop_path": {'S': movie_data["backdrop_path"]} if movie_data["backdrop_path"] else {'NULL': True},
        "genre_ids": {'NS': [str(genre) for genre in movie_data["genre_ids"]]},
        "id": {'N': str(movie_data["id"])},  # Keep original ID
        "original_language": {'S': movie_data["original_language"]},
        "original_title": {'S': movie_data["original_title"]},
        "overview": {'S': movie_data["overview"]},
        "popularity": {'N': str(movie_data["popularity"])},
        "poster_path": {'S': movie_data["poster_path"]},
        "release_date": {'S': movie_data["release_date"]},
        "title": {'S': movie_data["title"]},
        "video": {'BOOL': movie_data["video"]},
        "vote_average": {'N': str(movie_data["vote_average"])},
        "vote_count": {'N': str(movie_data["vote_count"])}
    }

# Convert all movies in the dataset
transformed_data = {key: transform_data(value) for key, value in data.items()}
json.dumps(transformed_data, indent=4)

for item in transformed_data.values():
    response = client.put_item(
        TableName='<your-table>',  # Change <your-table> accordingly
        Item=item
    )
    print(response)